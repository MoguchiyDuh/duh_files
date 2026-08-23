# Claude OAuth Account Manager (`claude-oauth.py`) Guide

`duh-claude-oauth` manages multiple Claude Code OAuth accounts side by side on one machine. It handles the PKCE login flow itself (no `claude` CLI required) and keeps each account's tokens in its own file under `~/.claude/profiles/`, with `~/.claude/.credentials.json` kept as a symlink to whichever one is "active."

---

## Storage Layout

```
~/.claude/profiles/<name>.json   canonical credentials + metadata for one account
~/.claude/.credentials.json      symlink -> whichever profile is active
```

Each profile file uses the same `claudeAiOauth` schema the real Claude Code client reads/writes, plus a sibling `_meta` key (`name`, `email`, `displayName`, `addedAt`, `lastRefreshedAt`) used for display purposes only.

**Why a symlink instead of copying credentials around:** the OAuth server can rotate the refresh token on every refresh. If credentials were copied into `.credentials.json` and copied back out, a refresh performed while an account was active would only land in the copy — switching back later would replay a stale, possibly-invalidated refresh token. Because the real Claude Code client writes credentials in place (no atomic rename), a refresh always lands directly in the active profile file through the symlink, so nothing goes stale.

This tool never writes through `.credentials.json` itself — all reads/writes target the canonical profile file directly. The only operation ever performed on `.credentials.json` is unlink + re-symlink, done deliberately by `login`, `use`, `add`, and `logout`.

**Known gotcha:** if the *real* Claude Code client (or any other tool) ever runs its own `/logout`, it will `unlink()` `.credentials.json` directly, destroying the symlink (the profile file itself is untouched). `status`/`list` will report the credentials path as missing — just run `duh-claude-oauth use <name>` to relink.

---

## Commands

### 1. `login`

Authenticates a new account via the browser (or a manually pasted code for headless sessions) and adds it as a profile.

**Usage:** `duh-claude-oauth login [OPTIONS]`

**Options:**

- `--name NAME`: Profile name. Defaults to the local part of the account's email (collision-safe, auto-suffixed).
- `--no-browser`: Don't auto-open the browser; print the URL instead.
- `--force`: Overwrite an existing profile with the same name.

On success, the new profile becomes active.

---

### 2. `logout [name]`

Removes a stored profile entirely (not just the active link).

**Usage:** `duh-claude-oauth logout [name]`

- `name` defaults to the currently active profile.
- If the removed profile was active, switches to the most-recently-used remaining profile automatically.
- If no profiles remain, removes the `.credentials.json` symlink and leaves the machine unauthenticated.

---

### 3. `status [--all]`

Shows account info and **live quota** pulled from `/api/oauth/usage` (5h / 7d / 7d-opus / 7d-sonnet / 7d-oauth-apps / extra usage, with reset times). Refreshes the access token first if it's within 5 minutes of expiry.

**Usage:** `duh-claude-oauth status [--all]`

- No args: active profile only.
- `--all`: every stored profile, each hit individually for quota (network call per profile).

---

### 4. `refresh [name]`

Force-refreshes a profile's access token regardless of expiry, and persists the result.

**Usage:** `duh-claude-oauth refresh [name]`

- `name` defaults to the active profile.

---

### 5. `list`

Lists every stored profile: active marker, name, email, subscription tier, and whether the token is currently valid or expired. Also warns if `.credentials.json` is unmanaged (a plain file, not a symlink into `profiles/`) or a broken symlink.

**Usage:** `duh-claude-oauth list`

---

### 6. `use <name>`

Switches the active account by relinking `.credentials.json`. Opportunistically refreshes the target profile first (best-effort — a failed refresh only prints a warning, it doesn't block the switch).

**Usage:** `duh-claude-oauth use <name>`

---

### 7. `add <name>`

Adopts an existing, unmanaged `~/.claude/.credentials.json` (e.g. one just created by a native `claude login`, or copied in from another machine) as a new named profile, then makes it active.

**Usage:** `duh-claude-oauth add <name> [--force]`

- Fails if `.credentials.json` is already a managed symlink (use `use` instead) or has no usable credentials.
- `--force` overwrites an existing profile with the same name.

---

## Multi-Machine Notes

Profile files (`~/.claude/profiles/*.json`) can be copied between machines freely (e.g. via `scp`) — each is self-contained. Prefer `add` on the *remote* machine to adopt a session that already exists there over pushing a token from elsewhere: OAuth tokens are typically issued per device/login, and two machines sharing one token pair means whichever refreshes last invalidates the other's copy.
