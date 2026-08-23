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
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Literal

Json = dict[str, Any]
Provider = Literal["claude", "gpt", "gemini", "opencode-go", "zai"]
Source = Literal["auto", "opencode", "native"]
ProviderArg = Literal[
    "claude",
    "gpt",
    "codex",
    "gemini",
    "agy",
    "opencode-go",
    "go",
    "zai",
    "glm",
]
DEFAULT_PROVIDER_ARGS: list[ProviderArg] = [
    "claude",
    "gpt",
    "gemini",
    "opencode-go",
    "zai",
]

ACCESS_KEYS = {"access", "access_token", "accessToken"}
REFRESH_KEYS = {"refresh", "refresh_token", "refreshToken"}

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
CLAUDE_PROFILE_URL = "https://api.anthropic.com/api/oauth/profile"
CLAUDE_KEYCHAIN_SERVICE = "Claude Code-credentials"

OPENAI_CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"
OPENAI_TOKEN_URL = "https://auth.openai.com/oauth/token"
OPENAI_USAGE_URL = "https://chatgpt.com/backend-api/codex/usage"

ANTIGRAVITY_CLIENT_ID = (
    "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
)
ANTIGRAVITY_CLIENT_SECRET = "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"
ANTIGRAVITY_TOKEN_URL = "https://oauth2.googleapis.com/token"
ANTIGRAVITY_MODELS_URL = (
    "https://daily-cloudcode-pa.googleapis.com/v1internal:fetchAvailableModels"
)
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
ANTIGRAVITY_FILE_RE = re.compile(r"antigravity.*\.json$")

OPENCODE_GO_DASHBOARD_URL = "https://opencode.ai/workspace/{workspace_id}/go"
OPENCODE_GO_CREDENTIALS = (
    Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    / "opencode/opencode-go.json"
)
OPENCODE_GO_LIMITS = {
    "rolling": {"label": "session 5h", "dollars": 12},
    "weekly": {"label": "week 7d", "dollars": 30},
    "monthly": {"label": "month", "dollars": 60},
}

ZAI_USAGE_URL = "https://api.z.ai/api/monitor/usage/quota/limit"


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
    skip: bool = False


def read_json(path: Path) -> Json | None:
    try:
        data = json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def compact(data: Json) -> Json:
    return {key: value for key, value in data.items() if value not in (None, [], {})}


def as_dict(value: Any) -> Json:
    return value if isinstance(value, dict) else {}


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


def unix_ms_to_iso(value: Any) -> str | None:
    if not isinstance(value, int | float):
        return None
    return unix_to_iso(value / 1000)


def reset_suffix(value: str | None, stale_ok: bool = False) -> str:
    if not value:
        return ""
    try:
        reset = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return ""
    seconds = int((reset - datetime.now(UTC)).total_seconds())
    if seconds <= 0:
        return " (stale reset)" if stale_ok else ""
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    return f" resets in {' '.join(parts)}" if parts else ""


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


def http_request(
    url: str,
    *,
    method: str = "GET",
    token: str | None = None,
    headers: dict[str, str] | None = None,
    data: Json | bytes | None = None,
    timeout: int = 20,
) -> bytes:
    body = None
    request_headers = dict(headers or {})
    if token:
        request_headers["Authorization"] = f"Bearer {token}"
    if isinstance(data, dict):
        body = json.dumps(data).encode()
        request_headers.setdefault("Content-Type", "application/json")
    elif isinstance(data, bytes):
        body = data

    request = urllib.request.Request(
        url, data=body, headers=request_headers, method=method
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:500]
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def request_json(
    url: str,
    *,
    method: str = "GET",
    token: str | None = None,
    headers: dict[str, str] | None = None,
    data: Json | bytes | None = None,
    timeout: int = 20,
) -> Json:
    request_headers = dict(headers or {})
    request_headers.setdefault("Accept", "application/json")
    parsed = json.loads(
        http_request(
            url,
            method=method,
            token=token,
            headers=request_headers,
            data=data,
            timeout=timeout,
        )
    )
    if not isinstance(parsed, dict):
        raise RuntimeError("response was not a JSON object")
    return parsed


def request_text(
    url: str, *, headers: dict[str, str] | None = None, timeout: int = 20
) -> str:
    return http_request(url, headers=headers, timeout=timeout).decode(errors="replace")


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
    return Path(
        os.environ.get(
            "CLAUDE_CREDENTIALS_FILE", Path.home() / ".claude/.credentials.json"
        )
    )


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


def claude_account_email(token: str) -> str | None:
    try:
        raw = request_json(
            CLAUDE_PROFILE_URL, token=token, headers={"User-Agent": USER_AGENT}
        )
    except Exception:
        return None
    account = raw.get("account")
    return account.get("email") if isinstance(account, dict) else None


def lookup_claude(src: Source) -> Result:
    auth = claude_auth(src)
    token = find_string(auth.data, ACCESS_KEYS | {"oauth_token", "token"}) if auth else None
    if not auth or not token:
        return Result(
            "claude", False, error=f"no Claude OAuth token found for --src {src}", skip=True
        )

    errors: list[str] = []
    for url in CLAUDE_USAGE_URLS:
        try:
            raw = request_json(
                url,
                token=token,
                headers={
                    "anthropic-beta": "oauth-2025-04-20",
                    "User-Agent": USER_AGENT,
                },
            )
            account = account_name(auth.data, raw) or claude_account_email(token)
            return Result(
                "claude",
                True,
                compact(
                    {
                        "source": url,
                        "auth_source": auth.src,
                        "auth_path": path_str(auth.path),
                        "account": account,
                        "updated_at": now_iso(),
                        "raw": raw,
                    }
                ),
            )
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    return Result("claude", False, error="; ".join(errors))


def gpt_auth(native_first: bool) -> Auth | None:
    sources = [
        ("opencode", opencode_auth_path()),
        ("codex", Path.home() / ".codex/auth.json"),
    ]
    if native_first:
        sources.reverse()
    for source, path in sources:
        auth = read_json(path)
        if not auth:
            continue
        if source == "opencode":
            if isinstance(auth.get("openai"), dict):
                return Auth(source, path, auth["openai"])
            continue
        return Auth(source, path, auth)
    return None


def refresh_openai_token(auth: Auth) -> str:
    refresh = find_string(auth.data, REFRESH_KEYS)
    if not refresh:
        raise RuntimeError(f"{auth.path} has no OpenAI refresh token")
    data = post_form(
        OPENAI_TOKEN_URL,
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh,
            "client_id": OPENAI_CLIENT_ID,
        },
    )
    token = data.get("access_token")
    if not isinstance(token, str) or not token:
        raise RuntimeError("OpenAI refresh response had no access_token")
    return token


def lookup_gpt(src: Source) -> Result:
    auth = gpt_auth(src == "native")
    if not auth:
        return Result("gpt", False, error="no OpenAI OAuth credentials found", skip=True)
    token = find_string(auth.data, ACCESS_KEYS)
    account_id = (
        find_string(auth.data, {"accountId", "account_id", "chatgpt_account_id"}) or ""
    )
    if not token:
        return Result("gpt", False, error=f"{auth.path} has no OpenAI access token", skip=True)

    headers = {
        "chatgpt-account-id": account_id,
        "User-Agent": f"Mozilla/5.0 {USER_AGENT}",
    }
    try:
        try:
            raw = request_json(OPENAI_USAGE_URL, token=token, headers=headers)
        except RuntimeError as exc:
            if "HTTP 401" not in str(exc) and "HTTP 403" not in str(exc):
                raise
            raw = request_json(
                OPENAI_USAGE_URL, token=refresh_openai_token(auth), headers=headers
            )
    except Exception as exc:
        return Result("gpt", False, error=str(exc))

    rate = as_dict(raw.get("rate_limit"))
    primary = as_dict(rate.get("primary_window"))
    secondary = as_dict(rate.get("secondary_window"))
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
                    {
                        "used_percent": primary.get("used_percent"),
                        "resets_at": unix_to_iso(primary.get("reset_at")),
                    }
                ),
                "week_7d": compact(
                    {
                        "used_percent": secondary.get("used_percent"),
                        "resets_at": unix_to_iso(secondary.get("reset_at")),
                    }
                ),
                "additional_rate_limits": raw.get("additional_rate_limits"),
                "code_review_rate_limit": raw.get("code_review_rate_limit"),
                "raw": raw,
            }
        ),
    )


def opencode_go_config() -> tuple[str, str, str, Path | None]:
    workspace_id = os.environ.get("OPENCODE_GO_WORKSPACE_ID", "").strip()
    auth_cookie = os.environ.get("OPENCODE_GO_AUTH_COOKIE", "").strip()
    if workspace_id or auth_cookie:
        if not workspace_id or not auth_cookie:
            missing = (
                "OPENCODE_GO_AUTH_COOKIE"
                if workspace_id
                else "OPENCODE_GO_WORKSPACE_ID"
            )
            raise RuntimeError(f"{missing} is not set")
        return workspace_id, auth_cookie, "env", None

    path = Path(
        os.environ.get("OPENCODE_GO_CREDENTIALS_FILE", OPENCODE_GO_CREDENTIALS)
    ).expanduser()
    config = read_json(path)
    if config:
        if path.stat().st_mode & 0o077:
            raise RuntimeError(f"{path} must have mode 0600")
        workspace_id = str(config.get("workspaceId", "")).strip()
        auth_cookie = str(config.get("authCookie", "")).strip()
        if not workspace_id or not auth_cookie:
            missing = "workspaceId" if not workspace_id else "authCookie"
            raise RuntimeError(f"{path} has no {missing}")
        return workspace_id, auth_cookie, "dashboard-cookie", path

    raise RuntimeError(
        "set OPENCODE_GO_WORKSPACE_ID and OPENCODE_GO_AUTH_COOKIE, or create "
        f"{path} with workspaceId and authCookie"
    )


def parse_duration_seconds(value: str) -> float | None:
    units = {"day": 86400, "hour": 3600, "minute": 60, "second": 1}
    matches = re.findall(
        r"(\d+(?:\.\d+)?)\s*(days?|hours?|minutes?|seconds?)", value.lower()
    )
    if not matches:
        return 0 if re.search(r"\b(?:reset\s+)?now\b", value, re.I) else None
    return sum(float(amount) * units[unit.rstrip("s")] for amount, unit in matches)


def opencode_go_window(html: str, field: str, label: str) -> Json | None:
    number = r"(-?\d+(?:\.\d+)?)"
    for pattern, reverse in (
        (
            rf"{field}:\$R\[\d+\]=\{{[^}}]*usagePercent:{number}[^}}]*resetInSec:{number}[^}}]*\}}",
            False,
        ),
        (
            rf"{field}:\$R\[\d+\]=\{{[^}}]*resetInSec:{number}[^}}]*usagePercent:{number}[^}}]*\}}",
            True,
        ),
    ):
        match = re.search(pattern, html)
        if match:
            first, second = map(float, match.groups())
            used, reset_seconds = (second, first) if reverse else (first, second)
            return {
                "used_percent": max(0.0, used),
                "resets_at": (
                    datetime.now(UTC) + timedelta(seconds=max(0.0, reset_seconds))
                ).isoformat(),
            }

    for item in html.split('data-slot="usage-item"')[1:]:
        label_match = re.search(r'data-slot="usage-label">([^<]+)<', item)
        if not label_match or label not in label_match.group(1).lower():
            continue
        usage_match = re.search(r'data-slot="usage-value">[^0-9]*(\d+(?:\.\d+)?)', item)
        reset_match = re.search(
            r'data-slot="(?:reset-time|reset-now)">([\s\S]*?)</span>', item
        )
        if not usage_match or not reset_match:
            continue
        reset_text = re.sub(r"<!--/?\$-->", "", reset_match.group(1))
        reset_seconds = parse_duration_seconds(reset_text)
        if reset_seconds is None:
            continue
        return {
            "used_percent": float(usage_match.group(1)),
            "resets_at": (
                datetime.now(UTC) + timedelta(seconds=reset_seconds)
            ).isoformat(),
        }
    return None


def lookup_opencode_go() -> Result:
    try:
        workspace_id, auth_cookie, auth_source, auth_path = opencode_go_config()
        url = OPENCODE_GO_DASHBOARD_URL.format(
            workspace_id=urllib.parse.quote(workspace_id, safe="")
        )
        html = request_text(
            url,
            headers={
                "Accept": "text/html",
                "Cookie": f"auth={auth_cookie}",
                "User-Agent": "Mozilla/5.0 quota-lookup/0.1",
            },
        )
    except Exception as exc:
        return Result("opencode-go", False, error=str(exc))

    windows = {
        key: opencode_go_window(html, field, key)
        for key, field in (
            ("rolling", "rollingUsage"),
            ("weekly", "weeklyUsage"),
            ("monthly", "monthlyUsage"),
        )
    }
    if not any(windows.values()):
        return Result(
            "opencode-go",
            False,
            error="could not parse usage from the OpenCode Go dashboard",
        )

    return Result(
        "opencode-go",
        True,
        compact(
            {
                "source": url,
                "auth_source": auth_source,
                "auth_path": path_str(auth_path),
                "account": workspace_id,
                "updated_at": now_iso(),
                "plan": "go",
                "limits": OPENCODE_GO_LIMITS,
                **windows,
            }
        ),
    )


def zai_auth() -> Auth | None:
    key = os.environ.get("ZAI_API_KEY", "").strip()
    if key:
        return Auth("env", None, key)
    return opencode_provider("zai-coding-plan") or opencode_provider("zai")


ZAI_UNIT_HOURS: dict[int, int] = {3: 1, 6: 168}


def zai_label(lim: Json) -> str:
    unit = lim.get("unit")
    number = lim.get("number")
    if isinstance(unit, int) and isinstance(number, int | float) and unit in ZAI_UNIT_HOURS:
        hours = ZAI_UNIT_HOURS[unit] * int(number)
        if hours < 24:
            return f"session {hours}h"
        days = hours // 24
        return f"week {days}d" if days <= 7 else f"month {days}d"
    period = lim.get("period") or lim.get("periodType") or lim.get("periodUnit")
    if period:
        return str(period).lower().replace("_", " ")
    if isinstance(number, int | float):
        n = int(number)
        return f"session {n}h" if n < 24 else f"week {n // 24}d"
    return "session"


def zai_windows(data: Json) -> list[Json]:
    windows: list[Json] = []
    for lim in data.get("limits", []):
        if not isinstance(lim, dict):
            continue
        limit_type = str(lim.get("type", "")).lower()
        if limit_type == "credit_limit":
            label = zai_label(lim)
        else:
            label = limit_type.replace("_", " ") or "quota"
        percentage = lim.get("percentage")
        windows.append(
            compact(
                {
                    "label": label,
                    "used_percent": float(percentage)
                    if isinstance(percentage, int | float)
                    else None,
                    "resets_at": unix_ms_to_iso(lim.get("nextResetTime")),
                    "remaining": lim.get("remaining"),
                }
            )
        )
    return windows


def lookup_zai() -> Result:
    auth = zai_auth()
    token = find_string(auth.data, {"key", "api_key", "apiKey", "access_token"}) if auth else None
    if not auth or not token:
        return Result("zai", False, error="no z.ai API key found (ZAI_API_KEY or opencode auth)", skip=True)

    try:
        raw = request_json(
            ZAI_USAGE_URL, token=token, headers={"User-Agent": USER_AGENT}
        )
    except Exception as exc:
        return Result("zai", False, error=str(exc))

    payload = as_dict(raw.get("data"))
    windows = zai_windows(payload)
    if not windows:
        return Result("zai", False, error=f"unexpected response: {raw.get('msg', raw)}")

    level = payload.get("level")
    return Result(
        "zai",
        True,
        compact(
            {
                "source": ZAI_USAGE_URL,
                "auth_source": auth.src,
                "auth_path": path_str(auth.path),
                "updated_at": now_iso(),
                "plan": level.title() if isinstance(level, str) and level else None,
                "windows": windows,
                "raw": payload,
            }
        ),
    )


def antigravity_file() -> Path:
    override = os.environ.get("ANTIGRAVITY_AUTH_FILE")
    if override:
        return Path(override).expanduser()
    config_dir = Path.home() / ".config/opencode"
    matches = sorted(
        path
        for path in config_dir.glob("antigravity*.json")
        if ANTIGRAVITY_FILE_RE.search(path.name)
    )
    return matches[0] if matches else config_dir / "antigravity-accounts.json"


def antigravity_identity(account: Json) -> str:
    refresh = find_string(account, REFRESH_KEYS)
    if refresh:
        return refresh.split("|", 1)[0]
    email = account.get("email")
    return str(email) if isinstance(email, str) and email else ""


def opencode_account_json_antigravity() -> Auth | None:
    path = Path.home() / ".local/share/opencode/account.json"
    data = read_json(path)
    if not data:
        return None
    accounts = data.get("accounts")
    if not isinstance(accounts, dict):
        return None
    for account in accounts.values():
        if not isinstance(account, dict) or account.get("serviceID") != "antigravity":
            continue
        credential = account.get("credential")
        if isinstance(credential, dict):
            return Auth("opencode", path, credential)
    return None


def antigravity_account_sources(src: Source) -> list[Auth]:
    candidates: list[Auth] = []
    native_path = antigravity_file()
    native = read_json(native_path)
    if isinstance(native, dict):
        accounts = native.get("accounts")
        if isinstance(accounts, list) and accounts:
            candidates.extend(
                Auth("native", native_path, account)
                for account in accounts
                if isinstance(account, dict)
            )
        elif accounts is None:
            candidates.append(Auth("native", native_path, native))

    if src != "native":
        plugin = opencode_provider("antigravity")
        if plugin and isinstance(plugin.data, dict):
            candidates.append(plugin)
        account_store = opencode_account_json_antigravity()
        if account_store:
            candidates.append(account_store)

    if src == "opencode":
        candidates = [c for c in candidates if c.src != "native"]
    elif src == "native":
        candidates = [c for c in candidates if c.src != "opencode"]

    seen: set[str] = set()
    result: list[Auth] = []
    for candidate in candidates:
        key = antigravity_identity(candidate.data)
        if key:
            if key in seen:
                continue
            seen.add(key)
        result.append(candidate)
    return result


def antigravity_active_indexes() -> set[int]:
    native = read_json(antigravity_file())
    if not isinstance(native, dict):
        return set()
    index = native.get("activeIndex")
    family = native.get("activeIndexByFamily")
    if isinstance(family, dict) and isinstance(family.get("gemini"), int):
        index = family["gemini"]
    return {index} if isinstance(index, int) else set()


def antigravity_access_token(account: Json) -> str:
    return find_string(account, ACCESS_KEYS) or refresh_antigravity_token(account)


def refresh_antigravity_token(account: Json) -> str:
    refresh = find_string(account, REFRESH_KEYS)
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
    fingerprint = as_dict(account.get("fingerprint"))
    metadata = as_dict(fingerprint.get("clientMetadata"))
    headers = {
        "User-Agent": fingerprint.get("userAgent")
        or "antigravity/hub/2.0.10 darwin/arm64",
        "X-Goog-Api-Client": fingerprint.get("apiClient")
        or "google-cloud-sdk vscode_cloudshelleditor/0.1",
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
        raw = request_json(
            GOOGLE_USERINFO_URL, token=token, headers={"User-Agent": USER_AGENT}
        )
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
        quota = as_dict(entry.get("quotaInfo"))
        current = groups.setdefault(group, {"model": group, "model_count": 0})
        current["model_count"] += 1

        remaining = quota.get("remainingFraction")
        if isinstance(remaining, int | float):
            remaining = min(max(float(remaining), 0.0), 1.0)
            current["remaining_fraction"] = min(
                float(current.get("remaining_fraction", 1.0)), remaining
            )
            current["used_percent"] = max(
                float(current.get("used_percent", 0.0)), (1.0 - remaining) * 100.0
            )
        reset_time = quota.get("resetTime")
        if isinstance(reset_time, str) and (
            not current.get("resets_at") or reset_time < current["resets_at"]
        ):
            current["resets_at"] = reset_time
    return [
        groups[key] for key in ("gemini-flash", "gemini-pro", "claude") if key in groups
    ]


def cached_antigravity_buckets(quota: Json) -> list[Json]:
    buckets: list[Json] = []
    for key in ("gemini-flash", "gemini-pro", "claude"):
        info = as_dict(quota.get(key))
        if not info:
            continue
        remaining = info.get("remainingFraction")
        used_percent = None
        if isinstance(remaining, int | float):
            remaining = min(max(float(remaining), 0.0), 1.0)
            used_percent = (1.0 - remaining) * 100.0
        buckets.append(
            compact(
                {
                    "model": key,
                    "model_count": info.get("modelCount"),
                    "used_percent": used_percent,
                    "resets_at": info.get("resetTime"),
                }
            )
        )
    return buckets


def lookup_gemini(src: Source) -> Result:
    sources = antigravity_account_sources(src)
    if not sources:
        return Result(
            "gemini",
            False,
            error=f"no Antigravity OAuth credentials found for --src {src}",
            skip=True,
        )

    active_indexes = antigravity_active_indexes()
    accounts_out: list[Json] = []
    errors: list[str] = []

    for index, source in enumerate(sources):
        account = source.data
        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get(
            "GOOGLE_CLOUD_PROJECT_ID"
        )
        project_id = (
            project_id
            or account.get("managedProjectId")
            or account.get("projectId")
            or ""
        )
        entry: Json = {
            "auth_source": source.src,
            "auth_path": path_str(source.path),
            "email": account.get("email"),
            "enabled": account.get("enabled"),
            "active": index in active_indexes or None,
        }
        if project_id:
            entry["project_id"] = project_id

        try:
            token = antigravity_access_token(account)
            try:
                raw = fetch_antigravity_models(token, str(project_id), account)
            except RuntimeError as exc:
                if "HTTP 401" not in str(exc) and "HTTP 403" not in str(exc):
                    raise
                token = refresh_antigravity_token(account)
                raw = fetch_antigravity_models(token, str(project_id), account)
            buckets = summarize_antigravity(raw)
            email = account.get("email") or account_name(account, raw) or google_account(token)
            if email:
                entry["email"] = email
            if buckets:
                entry["buckets"] = buckets
        except Exception as exc:
            cached = cached_antigravity_buckets(as_dict(account.get("cachedQuota")))
            if cached:
                entry["cached"] = True
                entry["buckets"] = cached
            else:
                entry["error"] = str(exc)
                errors.append(str(exc))
        accounts_out.append(compact(entry))

    if not accounts_out:
        return Result("gemini", False, error="no Antigravity accounts found", skip=True)

    primary = next(
        (
            entry
            for entry in accounts_out
            if entry.get("active") and entry.get("buckets")
        ),
        next((entry for entry in accounts_out if entry.get("buckets")), None),
    )
    data = compact(
        {
            "source": ANTIGRAVITY_MODELS_URL,
            "auth_source": ", ".join(sorted({source.src for source in sources})),
            "auth_path": path_str(sources[0].path),
            "account": (primary or {}).get("email"),
            "updated_at": now_iso(),
            "accounts": accounts_out,
            "buckets": (primary or {}).get("buckets"),
        }
    )
    return Result("gemini", not errors, data)


def print_window(label: str, bucket: Any, percent_key: str, suffix: str = "", stale_ok: bool = False) -> None:
    bucket = as_dict(bucket)
    if bucket:
        percent = as_percent(bucket.get(percent_key))
        print(f"  {label}: {percent}{suffix}{reset_suffix(bucket.get('resets_at'), stale_ok=stale_ok)}")


def print_result(result: Result) -> None:
    print(result.provider)
    if not result.ok or not result.data:
        print(f"  error: {result.error}\n")
        return

    data = result.data
    print(f"  source: {data.get('source', '?')}")
    print(f"  src: {data.get('auth_source', '?')}")
    print(f"  account: {data.get('account') or 'unknown'}")
    if data.get("plan"):
        print(f"  plan: {data['plan']}")
    match result.provider:
        case "claude":
            raw = as_dict(data.get("raw"))
            print_window("session 5h", raw.get("five_hour"), "utilization")
            print_window("week 7d", raw.get("seven_day"), "utilization")
            print_window("week 7d opus", raw.get("seven_day_opus"), "utilization")
            print_window("week 7d sonnet", raw.get("seven_day_sonnet"), "utilization")
            print_window("week 7d oauth apps", raw.get("seven_day_oauth_apps"), "utilization")
            extra = as_dict(raw.get("extra_usage"))
            if extra.get("is_enabled"):
                util = extra.get("utilization")
                util_s = as_percent(util) if util is not None else "enabled"
                print(f"  extra usage: {util_s}")
        case "gpt":
            print_window("session 5h", data.get("session_5h"), "used_percent")
            print_window("week 7d", data.get("week_7d"), "used_percent")
        case "gemini":
            accounts = data.get("accounts")
            if isinstance(accounts, list) and accounts:
                for account in accounts:
                    email = account.get("email") or "unknown"
                    flags = []
                    if account.get("active"):
                        flags.append("active")
                    if account.get("enabled") is False:
                        flags.append("disabled")
                    if account.get("cached"):
                        flags.append("cached")
                    suffix = f" ({', '.join(flags)})" if flags else ""
                    print(f"  account: {email}{suffix}")
                    if account.get("project_id"):
                        print(f"  project: {account['project_id']}")
                    if account.get("error"):
                        print(f"  error: {account['error']}")
                    for bucket in account.get("buckets", []):
                        print_window(
                            as_dict(bucket).get("model", "quota"),
                            bucket,
                            "used_percent",
                            " used",
                        )
            else:
                if data.get("project_id"):
                    print(f"  project: {data['project_id']}")
                for bucket in data.get("buckets", []):
                    print_window(
                        as_dict(bucket).get("model", "quota"), bucket, "used_percent", " used"
                    )
        case "opencode-go":
            for key, info in as_dict(data.get("limits")).items():
                info = as_dict(info)
                print_window(
                    info.get("label", "?"),
                    data.get(key),
                    "used_percent",
                    f" used / ${info.get('dollars', '?')} cap",
                )
        case "zai":
            for window in data.get("windows", []):
                window = as_dict(window)
                remaining = window.get("remaining")
                suffix = f" used / {remaining} credits left" if remaining is not None else " used"
                print_window(window.get("label", "quota"), window, "used_percent", suffix, stale_ok=True)
    print()


def canonical_provider(name: ProviderArg) -> Provider:
    aliases: dict[ProviderArg, Provider] = {
        "claude": "claude",
        "gpt": "gpt",
        "codex": "gpt",
        "gemini": "gemini",
        "agy": "gemini",
        "opencode-go": "opencode-go",
        "go": "opencode-go",
        "zai": "zai",
        "glm": "zai",
    }
    return aliases[name]


def source_for(provider_arg: ProviderArg, provider: Provider, src: Source) -> Source:
    if src != "auto":
        return src
    if provider_arg == "codex":
        return "native"
    if provider == "gemini":
        return "auto"
    if provider == "gpt":
        return "opencode"
    return "auto"


def lookup(provider_arg: ProviderArg, src: Source) -> Result:
    provider = canonical_provider(provider_arg)
    selected = source_for(provider_arg, provider, src)
    match provider:
        case "claude":
            return lookup_claude(selected)
        case "gpt":
            return lookup_gpt(selected)
        case "gemini":
            return lookup_gemini(selected)
        case "opencode-go":
            return lookup_opencode_go()
        case "zai":
            return lookup_zai()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="OAuth quota lookup: claude, gpt/codex, gemini/agy, opencode-go/go, zai/glm"
    )
    parser.add_argument(
        "providers",
        nargs="*",
        choices=[
            "claude",
            "gpt",
            "codex",
            "gemini",
            "agy",
            "opencode-go",
            "go",
            "zai",
            "glm",
        ],
        default=DEFAULT_PROVIDER_ARGS,
        help="provider: claude, gpt/codex, gemini/agy, opencode-go/go, zai/glm",
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
        print(
            json.dumps(
                [r.__dict__ for r in results if not r.skip],
                indent=2,
                default=str,
            )
        )
    else:
        for result in results:
            if not result.skip:
                print_result(result)
    return 0 if all(r.ok for r in results if not r.skip) else 1


if __name__ == "__main__":
    raise SystemExit(main())
