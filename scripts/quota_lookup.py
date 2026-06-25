#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

Json = dict[str, Any]
Provider = Literal["claude", "gpt", "gemini", "copilot"]
Source = Literal["auto", "opencode", "native"]
ProviderArg = Literal["claude", "gpt", "codex", "gemini", "agy", "copilot", "gh"]
DEFAULT_PROVIDER_ARGS: list[ProviderArg] = ["claude", "gpt", "gemini", "copilot"]

USER_AGENT = "quota-lookup/0.1"
OPENCODE_AUTH = Path.home() / ".local/share/opencode/auth.json"
ACCOUNT_KEY_PRIORITY = (
    {"email", "emailAddress", "user_email"},
    {"login", "preferred_username", "username", "userName"},
    {"account", "accountId", "account_id", "chatgpt_account_id", "user_id", "userId"},
)

CLAUDE_USAGE_URLS = [
    "https://api.anthropic.com/api/oauth/usage",
    "https://claude.ai/api/oauth/usage",
]
CLAUDE_KEYCHAIN_SERVICE = "Claude Code-credentials"

OPENAI_CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"
OPENAI_TOKEN_URL = "https://auth.openai.com/oauth/token"
OPENAI_USAGE_URL = "https://chatgpt.com/backend-api/codex/usage"

ANTIGRAVITY_CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
ANTIGRAVITY_CLIENT_SECRET = "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"
ANTIGRAVITY_TOKEN_URL = "https://oauth2.googleapis.com/token"
ANTIGRAVITY_MODELS_URL = "https://daily-cloudcode-pa.googleapis.com/v1internal:fetchAvailableModels"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
ANTIGRAVITY_FILE_RE = re.compile(r"antigravity.*\.json$")

COPILOT_USER_URL = "https://api.github.com/copilot_internal/user"


@dataclass(frozen=True)
class Auth:
    src: str
    path: Path | None
    data: Json | str


@dataclass(frozen=True)
class Result:
    provider: Provider
    ok: bool
    data: Json | None = None
    error: str | None = None


def read_json(path: Path) -> Json | None:
    try:
        data = json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def compact(data: Json) -> Json:
    return {key: value for key, value in data.items() if value not in (None, [], {})}


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def as_percent(value: Any) -> str:
    if value is None:
        return "?"
    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return str(value)


def unix_to_iso(value: Any) -> str | None:
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(float(value), tz=UTC).isoformat()
    except (OSError, TypeError, ValueError):
        return None


def reset_suffix(value: str | None) -> str:
    if not value:
        return ""
    try:
        reset = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return ""
    seconds = int((reset - datetime.now(UTC)).total_seconds())
    if seconds <= 0:
        return ""
    minutes = seconds // 60
    if minutes >= 60:
        return f" resets {minutes // 60}h{minutes % 60}m"
    return f" resets {minutes}m"


def find_string(value: Any, names: set[str]) -> str | None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in names and isinstance(item, str) and item:
                return item
        for item in value.values():
            found = find_string(item, names)
            if found:
                return found
    if isinstance(value, list):
        for item in value:
            found = find_string(item, names)
            if found:
                return found
    return None


def account_name(*values: Any) -> str | None:
    for keys in ACCOUNT_KEY_PRIORITY:
        for value in values:
            found = find_string(value, keys)
            if found:
                return found
    return None


def request_json(
    url: str,
    *,
    method: str = "GET",
    token: str | None = None,
    headers: dict[str, str] | None = None,
    data: Json | bytes | None = None,
    timeout: int = 20,
) -> Json:
    body = None
    request_headers = dict(headers or {})
    if token:
        request_headers["Authorization"] = f"Bearer {token}"
    if isinstance(data, dict):
        body = json.dumps(data).encode()
        request_headers.setdefault("Content-Type", "application/json")
    elif isinstance(data, bytes):
        body = data
    request_headers.setdefault("Accept", "application/json")

    request = urllib.request.Request(url, data=body, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            parsed = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:500]
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError("response was not a JSON object")
    return parsed


def post_form(url: str, payload: dict[str, str]) -> Json:
    return request_json(
        url,
        method="POST",
        data=urllib.parse.urlencode(payload).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


def opencode_auth_path() -> Path:
    return Path(os.environ.get("OPENCODE_AUTH_FILE", OPENCODE_AUTH))


def opencode_provider(name: str) -> Auth | None:
    auth = read_json(opencode_auth_path())
    if not auth or not isinstance(auth.get(name), dict):
        return None
    return Auth("opencode", opencode_auth_path(), auth[name])


def path_str(path: Path | None) -> str | None:
    return str(path) if path else None


def read_macos_keychain_json(service: str) -> Json | None:
    if sys.platform != "darwin":
        return None
    try:
        proc = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-w"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def claude_credentials_path() -> Path:
    return Path(os.environ.get("CLAUDE_CREDENTIALS_FILE", Path.home() / ".claude/.credentials.json"))


def claude_auth(src: Source) -> Auth | None:
    if src in ("auto", "native"):
        keychain = read_macos_keychain_json(CLAUDE_KEYCHAIN_SERVICE)
        if keychain:
            return Auth("mac-keychain", None, keychain)
        creds = read_json(claude_credentials_path())
        if creds:
            return Auth(".credentials.json", claude_credentials_path(), creds)
    if src in ("auto", "opencode"):
        return opencode_provider("anthropic")
    return None


def lookup_claude(src: Source) -> Result:
    auth = claude_auth(src)
    token = find_string(auth.data, {"access", "access_token", "accessToken", "oauth_token", "token"}) if auth else None
    if not auth or not token:
        return Result("claude", False, error=f"no Claude OAuth token found for --src {src}")

    errors: list[str] = []
    for url in CLAUDE_USAGE_URLS:
        try:
            raw = request_json(
                url,
                token=token,
                headers={"anthropic-beta": "oauth-2025-04-20", "User-Agent": USER_AGENT},
            )
            return Result(
                "claude",
                True,
                compact(
                    {
                        "source": url,
                        "auth_source": auth.src,
                        "auth_path": path_str(auth.path),
                        "account": account_name(auth.data, raw),
                        "updated_at": now_iso(),
                        "raw": raw,
                    }
                ),
            )
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    return Result("claude", False, error="; ".join(errors))


def gpt_auth(native_first: bool) -> Auth | None:
    sources = [("opencode", opencode_auth_path()), ("codex", Path.home() / ".codex/auth.json")]
    if native_first:
        sources.reverse()
    for source, path in sources:
        auth = read_json(path)
        if not auth:
            continue
        if source == "opencode" and isinstance(auth.get("openai"), dict):
            return Auth(source, path, auth["openai"])
        return Auth(source, path, auth)
    return None


def refresh_openai_token(auth: Auth) -> str:
    refresh = find_string(auth.data, {"refresh", "refresh_token", "refreshToken"})
    if not refresh:
        raise RuntimeError(f"{auth.path} has no OpenAI refresh token")
    data = post_form(
        OPENAI_TOKEN_URL,
        {"grant_type": "refresh_token", "refresh_token": refresh, "client_id": OPENAI_CLIENT_ID},
    )
    token = data.get("access_token")
    if not isinstance(token, str) or not token:
        raise RuntimeError("OpenAI refresh response had no access_token")
    return token


def lookup_gpt(src: Source, *, native_first: bool = False) -> Result:
    auth = gpt_auth(native_first or src == "native")
    if not auth:
        return Result("gpt", False, error="no OpenAI OAuth credentials found")
    token = find_string(auth.data, {"access", "access_token", "accessToken"})
    account_id = find_string(auth.data, {"accountId", "account_id", "chatgpt_account_id"}) or ""
    if not token:
        return Result("gpt", False, error=f"{auth.path} has no OpenAI access token")

    headers = {"chatgpt-account-id": account_id, "User-Agent": f"Mozilla/5.0 {USER_AGENT}"}
    try:
        try:
            raw = request_json(OPENAI_USAGE_URL, token=token, headers=headers)
        except RuntimeError as exc:
            if "HTTP 401" not in str(exc) and "HTTP 403" not in str(exc):
                raise
            raw = request_json(OPENAI_USAGE_URL, token=refresh_openai_token(auth), headers=headers)
    except Exception as exc:
        return Result("gpt", False, error=str(exc))

    rate = raw.get("rate_limit") if isinstance(raw.get("rate_limit"), dict) else {}
    primary = rate.get("primary_window") if isinstance(rate.get("primary_window"), dict) else {}
    secondary = rate.get("secondary_window") if isinstance(rate.get("secondary_window"), dict) else {}
    return Result(
        "gpt",
        True,
        compact(
            {
                "source": OPENAI_USAGE_URL,
                "auth_source": auth.src,
                "auth_path": path_str(auth.path),
                "account": account_name(raw, auth.data) or account_id,
                "updated_at": now_iso(),
                "plan": raw.get("plan_type"),
                "session_5h": compact(
                    {"used_percent": primary.get("used_percent"), "resets_at": unix_to_iso(primary.get("reset_at"))}
                ),
                "week_7d": compact(
                    {"used_percent": secondary.get("used_percent"), "resets_at": unix_to_iso(secondary.get("reset_at"))}
                ),
                "additional_rate_limits": raw.get("additional_rate_limits"),
                "code_review_rate_limit": raw.get("code_review_rate_limit"),
                "raw": raw,
            }
        ),
    )


def copilot_auth(native_first: bool) -> Auth | None:
    sources = [("opencode", opencode_auth_path()), ("gh", Path.home() / ".config/gh/hosts.yml")]
    if native_first:
        sources.reverse()
    for source, path in sources:
        if source == "opencode":
            auth = read_json(path)
            if not auth:
                continue
            provider = auth.get("github") if isinstance(auth.get("github"), dict) else auth.get("copilot")
            if isinstance(provider, dict):
                token = find_string(provider, {"access", "access_token", "accessToken", "token", "key"})
                if token:
                    return Auth(source, path, token)
            continue
        try:
            text = path.read_text()
        except OSError:
            continue
        match = re.search(r"oauth_token:\s*(\S+)", text)
        if match:
            return Auth(source, path, match.group(1))
    return None


def lookup_copilot(src: Source) -> Result:
    auth = copilot_auth(src == "native")
    if not auth or not isinstance(auth.data, str):
        return Result("copilot", False, error="no Copilot/GitHub OAuth credentials found")
    try:
        raw = request_json(
            COPILOT_USER_URL,
            token=auth.data,
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        )
    except Exception as exc:
        return Result("copilot", False, error=str(exc))
    return Result(
        "copilot",
        True,
        compact(
            {
                "source": COPILOT_USER_URL,
                "auth_source": auth.src,
                "auth_path": path_str(auth.path),
                "account": account_name(raw),
                "updated_at": now_iso(),
                "plan": raw.get("copilot_plan") or raw.get("access_type_sku") or raw.get("sku"),
                "quota_used": raw.get("quota_used") or raw.get("quotaUsed"),
                "quota_limit": raw.get("quota_limit") or raw.get("quotaLimit"),
                "quota_reset": raw.get("quota_reset_date") or raw.get("quotaResetDate"),
                "raw": raw,
            }
        ),
    )


def antigravity_file() -> Path:
    override = os.environ.get("ANTIGRAVITY_AUTH_FILE")
    if override:
        return Path(override).expanduser()
    config_dir = Path.home() / ".config/opencode"
    matches = sorted(path for path in config_dir.glob("antigravity*.json") if ANTIGRAVITY_FILE_RE.search(path.name))
    return matches[0] if matches else config_dir / "antigravity-accounts.json"


def antigravity_auth(src: Source) -> Auth | None:
    sources = [("antigravity", antigravity_file()), ("opencode", opencode_auth_path())]
    if src == "opencode":
        sources.reverse()
    for source, path in sources:
        auth = read_json(path)
        if not auth:
            continue
        if source == "opencode" and isinstance(auth.get("antigravity"), dict):
            return Auth(source, path, auth["antigravity"])
        if source == "antigravity":
            return Auth("opencode", path, auth)
    return None


def active_antigravity_account(auth: Json) -> Json:
    accounts = auth.get("accounts")
    if not isinstance(accounts, list) or not accounts:
        return auth
    index = auth.get("activeIndex")
    family = auth.get("activeIndexByFamily")
    if not isinstance(index, int) and isinstance(family, dict) and isinstance(family.get("gemini"), int):
        index = family["gemini"]
    if not isinstance(index, int) or index < 0 or index >= len(accounts):
        index = 0
    account = accounts[index]
    return account if isinstance(account, dict) else auth


def antigravity_access_token(account: Json) -> str:
    token = find_string(account, {"access", "access_token", "accessToken"})
    if token:
        return token
    return refresh_antigravity_token(account)


def refresh_antigravity_token(account: Json) -> str:
    refresh = find_string(account, {"refresh", "refresh_token", "refreshToken"})
    if not refresh:
        raise RuntimeError("Antigravity auth has no refresh token")
    refresh = refresh.split("|", 1)[0]
    data = post_form(
        ANTIGRAVITY_TOKEN_URL,
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh,
            "client_id": ANTIGRAVITY_CLIENT_ID,
            "client_secret": ANTIGRAVITY_CLIENT_SECRET,
        },
    )
    token = data.get("access_token")
    if not isinstance(token, str) or not token:
        raise RuntimeError("Antigravity refresh response had no access_token")
    return token


def antigravity_headers(account: Json) -> dict[str, str]:
    fingerprint = account.get("fingerprint") if isinstance(account.get("fingerprint"), dict) else {}
    metadata = fingerprint.get("clientMetadata") if isinstance(fingerprint.get("clientMetadata"), dict) else None
    headers = {
        "User-Agent": fingerprint.get("userAgent") or "antigravity/hub/2.0.10 darwin/arm64",
        "X-Goog-Api-Client": fingerprint.get("apiClient") or "google-cloud-sdk vscode_cloudshelleditor/0.1",
    }
    if metadata:
        headers["Client-Metadata"] = json.dumps(metadata, separators=(",", ":"))
    return headers


def fetch_antigravity_models(token: str, project_id: str, account: Json) -> Json:
    return request_json(
        ANTIGRAVITY_MODELS_URL,
        method="POST",
        token=token,
        data={"project": project_id} if project_id else {},
        headers={"Content-Type": "application/json", **antigravity_headers(account)},
    )


def google_account(token: str) -> str | None:
    try:
        raw = request_json(GOOGLE_USERINFO_URL, token=token, headers={"User-Agent": USER_AGENT})
    except Exception:
        return None
    return account_name(raw)


def antigravity_group(model_name: str, entry: Json) -> str | None:
    text = f"{model_name} {entry.get('displayName', '')} {entry.get('modelName', '')}".lower()
    if "claude" in text:
        return "claude"
    if "gemini-3" not in text and "gemini 3" not in text:
        return None
    return "gemini-flash" if "flash" in text else "gemini-pro"


def summarize_antigravity(raw: Json) -> list[Json]:
    models = raw.get("models")
    if not isinstance(models, dict):
        return []
    groups: dict[str, Json] = {}
    for model_name, entry in models.items():
        if not isinstance(model_name, str) or not isinstance(entry, dict):
            continue
        group = antigravity_group(model_name, entry)
        if not group:
            continue
        quota = entry.get("quotaInfo") if isinstance(entry.get("quotaInfo"), dict) else {}
        current = groups.setdefault(group, {"model": group, "model_count": 0})
        current["model_count"] += 1

        remaining = quota.get("remainingFraction")
        if isinstance(remaining, int | float):
            remaining = min(max(float(remaining), 0.0), 1.0)
            current["remaining_fraction"] = min(float(current.get("remaining_fraction", 1.0)), remaining)
            current["used_percent"] = max(float(current.get("used_percent", 0.0)), (1.0 - remaining) * 100.0)
        reset_time = quota.get("resetTime")
        if isinstance(reset_time, str) and (not current.get("resets_at") or reset_time < current["resets_at"]):
            current["resets_at"] = reset_time
    return [groups[key] for key in ("gemini-flash", "gemini-pro", "claude") if key in groups]


def lookup_gemini(src: Source) -> Result:
    auth = antigravity_auth(src)
    if not auth or not isinstance(auth.data, dict):
        return Result("gemini", False, error=f"no Antigravity OAuth credentials found for --src {src}")
    account = active_antigravity_account(auth.data)
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT_ID")
    project_id = project_id or account.get("managedProjectId") or account.get("projectId") or ""

    try:
        token = antigravity_access_token(account)
        try:
            raw = fetch_antigravity_models(token, str(project_id), account)
        except RuntimeError as exc:
            if "HTTP 401" not in str(exc) and "HTTP 403" not in str(exc):
                raise
            token = refresh_antigravity_token(account)
            raw = fetch_antigravity_models(token, str(project_id), account)
    except Exception as exc:
        return Result("gemini", False, error=str(exc))

    return Result(
        "gemini",
        True,
        compact(
            {
                "source": ANTIGRAVITY_MODELS_URL,
                "auth_source": auth.src,
                "auth_path": path_str(auth.path),
                "account": account_name(account, auth.data, raw) or google_account(token),
                "updated_at": now_iso(),
                "project_id": project_id,
                "buckets": summarize_antigravity(raw),
                "raw": raw,
            }
        ),
    )


def print_header(data: Json) -> None:
    print(f"  source: {data.get('source', '?')}")
    print(f"  src: {data.get('auth_source', '?')}")
    print(f"  account: {data.get('account') or 'unknown'}")


def print_window(data: Json, label: str, key: str, percent_key: str = "used_percent") -> None:
    bucket = data.get(key)
    if isinstance(bucket, dict):
        print(f"  {label}: {as_percent(bucket.get(percent_key))}{reset_suffix(bucket.get('resets_at'))}")


def print_result(result: Result) -> None:
    print(result.provider)
    if not result.ok or not result.data:
        print(f"  error: {result.error}\n")
        return

    data = result.data
    print_header(data)
    match result.provider:
        case "claude":
            raw = data.get("raw")
            if isinstance(raw, dict):
                for label, key in (("session 5h", "five_hour"), ("week 7d", "seven_day")):
                    bucket = raw.get(key)
                    if isinstance(bucket, dict):
                        print(f"  {label}: {as_percent(bucket.get('utilization'))}{reset_suffix(bucket.get('resets_at'))}")
        case "gpt":
            print(f"  plan: {data.get('plan', '?')}")
            print_window(data, "session 5h", "session_5h")
            print_window(data, "week 7d", "week_7d")
        case "gemini":
            if data.get("project_id"):
                print(f"  project: {data['project_id']}")
            for bucket in data.get("buckets", []):
                if isinstance(bucket, dict):
                    print(f"  {bucket.get('model', 'quota')}: {as_percent(bucket.get('used_percent'))} used{reset_suffix(bucket.get('resets_at'))}")
        case "copilot":
            if data.get("plan"):
                print(f"  plan: {data['plan']}")
            used = data.get("quota_used")
            limit = data.get("quota_limit")
            if used is not None or limit is not None:
                print(f"  quota: {used if used is not None else '?'} / {limit if limit is not None else '?'}")
            if data.get("quota_reset"):
                print(f"  reset: {data['quota_reset']}")
    print()


def canonical_provider(name: ProviderArg) -> Provider:
    aliases: dict[ProviderArg, Provider] = {
        "claude": "claude",
        "gpt": "gpt",
        "codex": "gpt",
        "gemini": "gemini",
        "agy": "gemini",
        "copilot": "copilot",
        "gh": "copilot",
    }
    return aliases[name]


def source_for(provider_arg: ProviderArg, provider: Provider, src: Source) -> Source:
    if src != "auto":
        return src
    if provider_arg in ("codex", "gh"):
        return "native"
    if provider == "gemini":
        return "native"
    if provider in ("gpt", "copilot"):
        return "opencode"
    return "auto"


def lookup(provider_arg: ProviderArg, src: Source) -> Result:
    provider = canonical_provider(provider_arg)
    selected = source_for(provider_arg, provider, src)
    match provider:
        case "claude":
            return lookup_claude(selected)
        case "gpt":
            return lookup_gpt(selected, native_first=provider_arg == "codex")
        case "gemini":
            return lookup_gemini("opencode" if selected == "opencode" else "native")
        case "copilot":
            return lookup_copilot(selected)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OAuth quota lookup: claude, gpt/codex, gemini/agy, copilot/gh")
    parser.add_argument(
        "providers",
        nargs="*",
        choices=["claude", "gpt", "codex", "gemini", "agy", "copilot", "gh"],
        default=DEFAULT_PROVIDER_ARGS,
        help="provider: claude, gpt/codex, gemini/agy, copilot/gh",
    )
    parser.add_argument("--json", action="store_true", help="print raw JSON")
    parser.add_argument(
        "--src",
        choices=["auto", "opencode", "native"],
        default="auto",
        help="credential source for the selected provider",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = [lookup(name, args.src) for name in args.providers]
    if args.json:
        print(json.dumps([result.__dict__ for result in results], indent=2, default=str))
    else:
        for result in results:
            print_result(result)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
