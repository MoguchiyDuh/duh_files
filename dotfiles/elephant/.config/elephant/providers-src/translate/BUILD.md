# Building the `translate` provider

This is a Go `plugin`-mode provider for elephant. The compiled `.so` goes to
`~/.config/elephant/providers/translate.so`. Go plugins require
**byte-identical toolchain + build flags** between the host binary and the
plugin, or loading fails with `plugin was built with a different version of
package internal/goarch` (or similar `internal/*` ABI errors).

The provider must also match the elephant plugin interface of the installed
version — `Query` gained a `[]rune` parameter in newer builds
(`func Query(conn net.Conn, query string, runes []rune, single bool, exact bool, format uint8) []*pb.QueryResponse_Item`).
A stale signature crashes elephant at startup with an `interface conversion`
panic.

## Requirements

- Exact same Go toolchain the installed `elephant` was built with. Verify via
  `go version -m /usr/bin/elephant` vs `go version`.
- Elephant source tree at the exact commit the installed package was built
  from (`go version -m /usr/bin/elephant` shows `(devel)` for git builds; get
  the commit from the package version, e.g. `r648.c9cc79b` -> `c9cc79b`).
- **Exact same build flags** as the AUR `PKGBUILD` uses for provider plugins:

  ```
  go build -ldflags="-s -w" -buildvcs=false -buildmode=plugin -trimpath
  ```

## Steps

1. Restore the source tree at the matching commit. The yay cache keeps the
   git repo even after cleaning the worktree:

   ```bash
   git -C ~/.cache/yay/elephant-all-git/elephant-all worktree add --detach /tmp/elephant-src <commit>
   ```

2. Copy `setup.go` + `README.md` from this directory into
   `<elephant-src>/internal/providers/translate/` (README.md is required —
   `go:embed`).
3. Build from the elephant source root:

   ```bash
   cd /tmp/elephant-src
   go build -ldflags="-s -w" -buildvcs=false -buildmode=plugin -trimpath \
     -o translate.so ./internal/providers/translate/
   ```

4. Install: `mkdir -p ~/.config/elephant/providers && cp translate.so ~/.config/elephant/providers/`
5. `systemctl --user restart elephant.service` and confirm with
   `elephant listproviders | grep translate`.

If elephant crash-loops after installing the plugin, remove
`~/.config/elephant/providers/translate.so`, `systemctl --user reset-failed
elephant.service`, restart, and fix the ABI/signature mismatch first.

## Config

Runtime config lives at `~/.config/elephant/translate.toml` (tracked in
this dotfiles repo). Key field: `target_lang` — ISO 639-1 code
(`en`, `ru`, `de`, ...), passed to `trans -brief -no-ansi :%LANG%`.

Queries support an inline target-lang bang: `de: hello` /
`ru: hello` (parsed by `parseQuery` in `setup.go`); plain queries use
`target_lang` with translate-shell source autodetection.
