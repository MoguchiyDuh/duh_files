#!/usr/bin/env python3
# /// script
# requires-python = ">=3.13"
# dependencies = []
# ///
"""
Claude Code multi-account manager.

Layout:
    ~/.claude/profiles/<name>.json   canonical, full credential store per account
    ~/.claude/.credentials.json      symlink -> whichever profile is "active"

Design note (read before touching set_active / write_json_atomic):
    This tool NEVER writes data through .credentials.json itself. All reads
    and writes target the canonical profile file in ~/.claude/profiles/
    directly; the only operation performed on .credentials.json is
    unlink+symlink to repoint it. That's what makes the symlink scheme safe:

    - Our own writes are atomic tmp+rename onto the *profile* file, which is
      never a symlink itself, so crash-safety is normal.
    - The real Claude Code client persists refreshed tokens with an in-place
      writeFileSync (no rename) to whatever .credentials.json resolves to
      (confirmed from source: utils/secureStorage/plainTextStorage.ts). That
      passes straight through the symlink and lands in the active profile
      file without disturbing the link. So a token refresh performed by
      Claude Code itself, while profile X is active, is never lost even
      though the OAuth server may rotate the refresh token on use.
    - Do NOT change profile writes to go through .credentials.json, and do
      NOT unlink() .credentials.json except in set_active()/logout() where
      it's intentional.

Commands: login, logout, status, refresh, list, use, add
"""
import argparse
import base64
import hashlib
import http.server
import json
import os
import pathlib
import queue
import secrets
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime, timezone

CLIENT_ID = "9d1c250a-e61b-44d9-88ed-5944d1962f5e"
SCOPES = "user:profile user:inference user:sessions:claude_code user:mcp_servers user:file_upload"
AUTH_SCOPES = f"org:create_api_key {SCOPES}"
AUTH_URL = "https://claude.com/cai/oauth/authorize"
MANUAL_REDIRECT_URL = "https://platform.claude.com/oauth/code/callback"
REDIRECT_PORT = int(os.environ.get("CLAW_AUTH_REDIRECT_PORT", "54321"))
TOKEN_URL = os.environ.get("CLAW_AUTH_TOKEN_URL", "https://platform.claude.com/v1/oauth/token")
BASE_API_URL = "https://api.anthropic.com"
PROFILE_URL = f"{BASE_API_URL}/api/oauth/profile"
USAGE_URL = f"{BASE_API_URL}/api/oauth/usage"
OAUTH_BETA_HEADER = "oauth-2025-04-20"

CLAUDE_DIR = pathlib.Path(os.environ.get("CLAUDE_CONFIG_DIR", pathlib.Path.home() / ".claude"))
CREDENTIALS_PATH = CLAUDE_DIR / ".credentials.json"
PROFILES_DIR = CLAUDE_DIR / "profiles"
DOC_KEY = "claudeAiOauth"
PROFILE_NAME_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-"
)

ORG_TYPE_TO_SUBSCRIPTION = {
    "claude_max": "max",
    "claude_pro": "pro",
    "claude_enterprise": "enterprise",
    "claude_team": "team",
}


class OAuthError(Exception):
    pass


# ---------- low-level helpers ----------


def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def generate_pkce() -> tuple[str, str]:
    verifier = base64url_encode(secrets.token_bytes(32))
    challenge = base64url_encode(hashlib.sha256(verifier.encode()).digest())
    return verifier, challenge


def now_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _http_json(method, url, *, headers=None, body=None, timeout=15):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "claude-account-manager/2.0",
            **(headers or {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")
        raise OAuthError(f"{method} {url} -> {e.code}: {body_text}") from None
    except urllib.error.URLError as e:
        raise OAuthError(f"{method} {url} -> {e.reason}") from None


def validate_profile_name(name: str) -> str:
    if not name or any(ch not in PROFILE_NAME_CHARS for ch in name):
        raise OAuthError(
            "profile name must contain only letters, numbers, dots, underscores, hyphens"
        )
    return name


# ---------- OAuth wire protocol ----------


def build_auth_url(redirect_uri: str, state: str, challenge: str) -> str:
    params = {
        "code": "true",
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": AUTH_SCOPES,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"


def exchange_code(code: str, verifier: str, redirect_uri: str, state: str) -> dict:
    data = _http_json(
        "POST",
        TOKEN_URL,
        headers={"anthropic-beta": OAUTH_BETA_HEADER},
        body={
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "code": code,
            "redirect_uri": redirect_uri,
            "code_verifier": verifier,
            "state": state,
        },
    )
    if "refresh_token" not in data:
        raise OAuthError("token response missing refresh_token")
    return data


def call_refresh_token(refresh_token_str: str, scopes: str = SCOPES) -> dict:
    return _http_json(
        "POST",
        TOKEN_URL,
        headers={"anthropic-beta": OAUTH_BETA_HEADER},
        body={
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": refresh_token_str,
            "scope": scopes,
        },
    )


def fetch_profile(access_token: str) -> dict | None:
    try:
        return _http_json(
            "GET", PROFILE_URL, headers={"Authorization": f"Bearer {access_token}"}
        )
    except OAuthError:
        return None


def fetch_usage(access_token: str) -> dict:
    return _http_json(
        "GET",
        USAGE_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "anthropic-beta": OAUTH_BETA_HEADER,
        },
        timeout=10,
    )


def build_credentials(token_data: dict, old: dict | None = None) -> dict:
    old = old or {}
    creds = {
        "accessToken": token_data["access_token"],
        "refreshToken": token_data.get("refresh_token") or old.get("refreshToken"),
        "expiresAt": now_ms() + token_data["expires_in"] * 1000,
    }
    scope_str = token_data.get("scope")
    if scope_str:
        creds["scopes"] = scope_str.split()
    elif old.get("scopes"):
        creds["scopes"] = old["scopes"]
    if old.get("subscriptionType"):
        creds["subscriptionType"] = old["subscriptionType"]
    if old.get("rateLimitTier"):
        creds["rateLimitTier"] = old["rateLimitTier"]
    return creds


def subscription_type_from_org(organization: dict) -> str | None:
    return ORG_TYPE_TO_SUBSCRIPTION.get(organization.get("organization_type"))


# ---------- local callback listener (automatic flow) ----------


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]
        if state != self.server.expected_state:
            self.server.auth_error = OAuthError("state mismatch")
        elif not code:
            self.server.auth_error = OAuthError("missing authorization code")
        else:
            self.server.auth_code = code
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(
            b"<html><body><h2>Authentication successful - "
            b"you can close this tab.</h2></body></html>"
        )

    def log_message(self, fmt, *args):
        pass


def _wait_for_callback(port: int, expected_state: str, result_queue: queue.Queue):
    server = http.server.HTTPServer(("127.0.0.1", port), _CallbackHandler)
    server.allow_reuse_address = True
    server.expected_state = expected_state
    server.auth_code = None
    server.auth_error = None
    while server.auth_code is None and server.auth_error is None:
        server.handle_request()
    server.server_close()
    if server.auth_error:
        result_queue.put(("error", server.auth_error))
    else:
        result_queue.put(("auto", server.auth_code))


def _parse_manual_code(value: str, expected_state: str) -> str:
    value = value.strip()
    if not value:
        raise OAuthError("empty manual code")
    if "://" in value:
        parsed = urllib.parse.urlparse(value)
        params = urllib.parse.parse_qs(parsed.query)
        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]
    elif "#" in value:
        code, state = value.split("#", 1)
    else:
        code, state = value, expected_state
    if state != expected_state:
        raise OAuthError("state mismatch")
    if not code:
        raise OAuthError("missing authorization code")
    return code


def _read_manual_code(result_queue: queue.Queue):
    value = input(
        "Paste manual code/callback URL, or press Enter to wait for browser: "
    ).strip()
    if value:
        result_queue.put(("manual", value))


def wait_for_authorization_code(
    port: int, expected_state: str, manual_redirect_uri: str
) -> tuple[str, str]:
    result_queue: queue.Queue = queue.Queue()
    callback_thread = threading.Thread(
        target=_wait_for_callback, args=(port, expected_state, result_queue), daemon=True
    )
    callback_thread.start()
    if sys.stdin.isatty():
        manual_thread = threading.Thread(
            target=_read_manual_code, args=(result_queue,), daemon=True
        )
        manual_thread.start()
    try:
        while True:
            source, result = result_queue.get()
            if source == "error":
                raise result
            if source == "manual":
                return _parse_manual_code(result, expected_state), manual_redirect_uri
            return result, f"http://localhost:{port}/callback"
    except KeyboardInterrupt:
        raise OAuthError("authentication cancelled") from None


# ---------- profile store ----------


def read_json_object(path: pathlib.Path) -> dict:
    try:
        doc = json.loads(path.read_text())
    except FileNotFoundError:
        raise OAuthError(f"file not found: {path}") from None
    except json.JSONDecodeError as e:
        raise OAuthError(f"invalid JSON in {path}: {e}") from None
    if not isinstance(doc, dict):
        raise OAuthError(f"expected JSON object in {path}")
    return doc


def write_json_atomic(path: pathlib.Path, doc: dict) -> None:
    """Atomic tmp+rename write. Only ever called on canonical profile files
    (never on CREDENTIALS_PATH) -- see module docstring."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        tmp.write_text(json.dumps(doc, indent=2))
        os.chmod(tmp, 0o600)
        tmp.replace(path)
    finally:
        if tmp.exists():
            tmp.unlink()


def profile_path(name: str) -> pathlib.Path:
    return PROFILES_DIR / f"{validate_profile_name(name)}.json"


def list_profile_names() -> list[str]:
    if not PROFILES_DIR.exists():
        return []
    return sorted(p.stem for p in PROFILES_DIR.glob("*.json"))


def load_profile(name: str) -> dict:
    path = profile_path(name)
    if not path.exists():
        raise OAuthError(f"no such profile: {name}")
    return read_json_object(path)


def profile_creds(doc: dict) -> dict:
    creds = doc.get(DOC_KEY)
    if not isinstance(creds, dict) or "accessToken" not in creds:
        raise OAuthError(f"profile missing {DOC_KEY}.accessToken")
    return creds


def save_profile(name: str, creds: dict, meta_updates: dict | None = None) -> None:
    path = profile_path(name)
    doc = read_json_object(path) if path.exists() else {}
    doc[DOC_KEY] = creds
    meta = doc.get("_meta", {})
    meta["name"] = name
    if meta_updates:
        meta.update({k: v for k, v in meta_updates.items() if v is not None})
    doc["_meta"] = meta
    write_json_atomic(path, doc)


def active_profile_name() -> str | None:
    """Name of the profile .credentials.json currently points at, or None
    if unmanaged/missing/broken. Assumes the symlink's target exists;
    callers that need broken-link detection should use credentials_state()."""
    if not CREDENTIALS_PATH.is_symlink():
        return None
    target = CREDENTIALS_PATH.resolve()
    try:
        target.relative_to(PROFILES_DIR.resolve())
    except ValueError:
        return None
    return target.stem


def credentials_state() -> str:
    """One of: 'linked', 'unmanaged', 'broken', 'missing'."""
    if CREDENTIALS_PATH.is_symlink():
        target = CREDENTIALS_PATH.resolve()
        if not target.exists():
            return "broken"
        return "linked" if active_profile_name() else "unmanaged"
    if CREDENTIALS_PATH.exists():
        return "unmanaged"
    return "missing"


def set_active(name: str, *, allow_unmanaged_replace: bool = False) -> None:
    """Repoint .credentials.json at profiles/<name>.json. Refuses to clobber
    an unmanaged (non-symlink) file unless allow_unmanaged_replace is set
    (only cmd_add should pass True, after it has already read+saved that
    file's contents into the target profile)."""
    target = profile_path(name)
    if not target.exists():
        raise OAuthError(f"no such profile: {name}")
    state = credentials_state()
    if state == "unmanaged" and not allow_unmanaged_replace:
        raise OAuthError(
            f"{CREDENTIALS_PATH} exists and isn't managed by this tool (not a "
            f"symlink into {PROFILES_DIR}). Run 'add <name>' to adopt it first."
        )
    if CREDENTIALS_PATH.exists() or CREDENTIALS_PATH.is_symlink():
        CREDENTIALS_PATH.unlink()
    CLAUDE_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_PATH.symlink_to(target)


def ensure_fresh(name: str, *, force: bool = False) -> str:
    """Return a valid access token for `name`, refreshing (and persisting)
    if it's within 5 minutes of expiry or `force` is set."""
    doc = load_profile(name)
    creds = profile_creds(doc)
    if force or creds["expiresAt"] - now_ms() < 5 * 60 * 1000:
        data = call_refresh_token(creds["refreshToken"])
        new_creds = build_credentials(data, creds)
        save_profile(name, new_creds, {"lastRefreshedAt": utc_now_iso()})
        return new_creds["accessToken"]
    return creds["accessToken"]


def default_profile_name(email: str | None) -> str:
    base = "default"
    if email:
        local = email.split("@", 1)[0]
        base = "".join(ch if ch in PROFILE_NAME_CHARS else "-" for ch in local) or "default"
    name = base
    n = 2
    while profile_path(name).exists():
        name = f"{base}-{n}"
        n += 1
    return name


# ---------- commands ----------


def cmd_login(args):
    state_val = os.environ.get("CLAW_AUTH_FIXED_STATE") or base64url_encode(
        secrets.token_bytes(32)
    )
    verifier, challenge = generate_pkce()
    redirect_uri = f"http://localhost:{REDIRECT_PORT}/callback"
    auth_url = build_auth_url(redirect_uri, state_val, challenge)
    print("Opening browser for Claude authentication...")
    print(f"Automatic URL: {auth_url}")
    if not args.no_browser:
        webbrowser.open(auth_url)
    code, token_redirect_uri = wait_for_authorization_code(
        REDIRECT_PORT, state_val, MANUAL_REDIRECT_URL
    )
    print("Got auth code, exchanging for tokens...")
    data = exchange_code(code, verifier, token_redirect_uri, state_val)
    creds = build_credentials(data)

    profile = fetch_profile(creds["accessToken"]) or {}
    account = profile.get("account") or {}
    organization = profile.get("organization") or {}
    email = account.get("email")
    display_name = account.get("display_name")
    sub_type = subscription_type_from_org(organization)
    if sub_type:
        creds["subscriptionType"] = sub_type
    if organization.get("rate_limit_tier"):
        creds["rateLimitTier"] = organization["rate_limit_tier"]

    name = args.name or default_profile_name(email)
    validate_profile_name(name)
    if profile_path(name).exists() and not args.force:
        raise OAuthError(
            f"profile '{name}' already exists; pass --name to choose another "
            "or --force to overwrite"
        )

    save_profile(
        name,
        creds,
        {"email": email, "displayName": display_name, "addedAt": utc_now_iso()},
    )
    set_active(name)
    print(f"Logged in as '{name}'" + (f" ({email})" if email else ""))
    print(f"{CREDENTIALS_PATH} -> {profile_path(name)}")


def cmd_logout(args):
    name = args.name or active_profile_name()
    if not name:
        raise OAuthError("no active profile and no name given; nothing to log out of")
    path = profile_path(name)
    if not path.exists():
        raise OAuthError(f"no such profile: {name}")
    was_active = active_profile_name() == name
    path.unlink()
    print(f"Removed profile '{name}'")
    if not was_active:
        return

    remaining = list_profile_names()
    if not remaining:
        if CREDENTIALS_PATH.exists() or CREDENTIALS_PATH.is_symlink():
            CREDENTIALS_PATH.unlink()
        print("No other accounts remain. Not authenticated.")
        return

    def sort_key(n: str) -> str:
        try:
            meta = load_profile(n).get("_meta", {})
        except OAuthError:
            return ""
        return meta.get("lastRefreshedAt") or meta.get("addedAt") or ""

    next_name = max(remaining, key=sort_key)
    set_active(next_name)
    print(f"Switched active account to '{next_name}'")


def format_relative(iso_str: str | None) -> str:
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        delta = dt - datetime.now(timezone.utc)
        total_s = int(delta.total_seconds())
    except (ValueError, TypeError):
        return f", resets {iso_str}"
    if total_s < 0:
        return ""
    days, rem = divmod(total_s, 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    return f", resets in {' '.join(parts)}" if parts else ""


def print_quota(usage: dict) -> None:
    def fmt(bucket_key: str, label: str):
        bucket = usage.get(bucket_key)
        if not bucket:
            return
        util = bucket.get("utilization")
        util_s = f"{util}%" if util is not None else "?"
        resets_s = format_relative(bucket.get("resets_at"))
        print(f"    {label}: {util_s}{resets_s}")

    fmt("five_hour", "5h")
    fmt("seven_day", "7d")
    fmt("seven_day_opus", "7d opus")
    fmt("seven_day_sonnet", "7d sonnet")
    fmt("seven_day_oauth_apps", "7d oauth apps")
    extra = usage.get("extra_usage")
    if extra and extra.get("is_enabled"):
        util = extra.get("utilization")
        print(f"    extra usage: {util}%" if util is not None else "    extra usage: enabled")


def print_profile_status(name: str, active: bool) -> None:
    doc = load_profile(name)
    creds = profile_creds(doc)
    meta = doc.get("_meta", {})
    expires_at = datetime.fromtimestamp(creds["expiresAt"] / 1000, tz=timezone.utc)
    marker = "*" if active else " "
    label = meta.get("email") or name
    print(f"[{marker}] {name}  ({label})")
    print(
        f"    subscription: {creds.get('subscriptionType', '?')}   "
        f"expires: {expires_at.isoformat()}"
    )
    try:
        token = ensure_fresh(name)
        print_quota(fetch_usage(token))
    except OAuthError as e:
        print(f"    quota check failed: {e}")


def cmd_status(args):
    active = active_profile_name()
    if args.all:
        names = list_profile_names()
        if not names:
            print("No profiles stored.")
            return
        for n in names:
            print_profile_status(n, n == active)
        return

    if args.name:
        print_profile_status(args.name, args.name == active)
        return

    if not active:
        state = credentials_state()
        if state == "unmanaged":
            print(
                f"{CREDENTIALS_PATH} exists but isn't managed by this tool. "
                "Run 'add <name>' to adopt it."
            )
        elif state == "broken":
            print(f"{CREDENTIALS_PATH} is a broken symlink.")
        else:
            print("Not authenticated.")
        return
    print_profile_status(active, True)


def cmd_refresh(args):
    name = args.name or active_profile_name()
    if not name:
        raise OAuthError("no active profile and no name given")
    token = ensure_fresh(name, force=True)
    print(f"Refreshed '{name}': {token[:20]}...{token[-8:]}")


def cmd_list(args):
    state = credentials_state()
    if state == "unmanaged":
        print(f"warning: {CREDENTIALS_PATH} is unmanaged (not a symlink into {PROFILES_DIR})")
    elif state == "broken":
        print(f"warning: {CREDENTIALS_PATH} is a broken symlink")

    names = list_profile_names()
    if not names:
        print("No profiles stored. Run 'login' or 'add <name>'.")
        return

    active = active_profile_name()
    for n in names:
        try:
            doc = load_profile(n)
            creds = profile_creds(doc)
            meta = doc.get("_meta", {})
            expires_at = datetime.fromtimestamp(creds["expiresAt"] / 1000, tz=timezone.utc)
            status_s = "EXPIRED" if expires_at < datetime.now(timezone.utc) else "valid"
            marker = "*" if n == active else " "
            email = meta.get("email") or "?"
            sub = creds.get("subscriptionType") or "?"
            print(f"[{marker}] {n:<20} {email:<30} {sub:<10} {status_s}")
        except OAuthError as e:
            print(f"[?] {n:<20} error: {e}")


def cmd_use(args):
    name = args.name
    if not profile_path(name).exists():
        available = ", ".join(list_profile_names()) or "(none)"
        raise OAuthError(f"no such profile: {name}. available: {available}")
    try:
        ensure_fresh(name)
    except OAuthError as e:
        print(f"warning: could not refresh '{name}' before switching: {e}")
    set_active(name)
    print(f"Active account: {name}")


def cmd_add(args):
    name = validate_profile_name(args.name)
    state = credentials_state()
    if state == "linked":
        raise OAuthError(
            f"{CREDENTIALS_PATH} is already managed (active profile: "
            f"{active_profile_name()}). Use 'use' to switch."
        )
    if state in ("missing", "broken"):
        raise OAuthError(f"{CREDENTIALS_PATH} has no usable credentials to adopt.")
    if profile_path(name).exists() and not args.force:
        raise OAuthError(f"profile '{name}' already exists; pass --force to overwrite")

    doc = read_json_object(CREDENTIALS_PATH)
    creds = profile_creds(doc)
    profile = fetch_profile(creds["accessToken"]) or {}
    account = profile.get("account") or {}
    organization = profile.get("organization") or {}
    email = account.get("email")
    display_name = account.get("display_name")
    sub_type = subscription_type_from_org(organization)
    if sub_type:
        creds["subscriptionType"] = sub_type
    if organization.get("rate_limit_tier"):
        creds["rateLimitTier"] = organization["rate_limit_tier"]

    save_profile(
        name,
        creds,
        {"email": email, "displayName": display_name, "addedAt": utc_now_iso()},
    )
    set_active(name, allow_unmanaged_replace=True)
    print(f"Adopted existing credentials as '{name}'" + (f" ({email})" if email else ""))


def main():
    parser = argparse.ArgumentParser(description="Manage multiple Claude Code OAuth accounts")
    sub = parser.add_subparsers(dest="command", required=True)

    p_login = sub.add_parser("login", help="Authenticate a new account")
    p_login.add_argument("--name", help="Profile name (default: derived from email)")
    p_login.add_argument("--no-browser", action="store_true")
    p_login.add_argument("--force", action="store_true", help="Overwrite existing profile")
    p_login.set_defaults(func=cmd_login)

    p_logout = sub.add_parser("logout", help="Remove an account, switch to another")
    p_logout.add_argument("name", nargs="?", help="Profile to log out of (default: active)")
    p_logout.set_defaults(func=cmd_logout)

    p_status = sub.add_parser("status", help="Show active account and live quota")
    p_status.add_argument("name", nargs="?", help="Profile to show (default: active)")
    p_status.add_argument("--all", action="store_true", help="Show every stored profile")
    p_status.set_defaults(func=cmd_status)

    p_refresh = sub.add_parser("refresh", help="Force-refresh a profile's access token")
    p_refresh.add_argument("name", nargs="?", help="Profile to refresh (default: active)")
    p_refresh.set_defaults(func=cmd_refresh)

    p_list = sub.add_parser("list", help="List all stored profiles")
    p_list.set_defaults(func=cmd_list)

    p_use = sub.add_parser("use", help="Switch the active account")
    p_use.add_argument("name")
    p_use.set_defaults(func=cmd_use)

    p_add = sub.add_parser(
        "add", help="Adopt the current unmanaged .credentials.json as a named profile"
    )
    p_add.add_argument("name")
    p_add.add_argument("--force", action="store_true")
    p_add.set_defaults(func=cmd_add)

    args = parser.parse_args()
    try:
        args.func(args)
    except OAuthError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\ncancelled", file=sys.stderr)
        sys.exit(130)
