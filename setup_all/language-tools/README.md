# Language Tool Inventories

These lists track global tools installed outside pacman/AUR.

Review before restoring. Do not install entries that are obsolete or intentionally removed.

## npm

```bash
sudo npm install -g $(cat setup_all/language-tools/npm-global.txt)
```

`opencode-ai` is intentionally tracked.

## Cargo

```bash
while read -r crate; do cargo install "$crate"; done < setup_all/language-tools/cargo-install.txt
```

## uv Tools

```bash
while read -r tool; do uv tool install "$tool"; done < setup_all/language-tools/uv-tools.txt
```

## pipx

```bash
while read -r app; do pipx install "$app"; done < setup_all/language-tools/pipx-tools.txt
```

## Rustup

```bash
while read -r toolchain; do rustup toolchain install "$toolchain"; done < setup_all/language-tools/rustup-toolchains.txt
while read -r component; do rustup component add "$component"; done < setup_all/language-tools/rustup-components.txt
while read -r target; do rustup target add "$target"; done < setup_all/language-tools/rustup-targets.txt
```

## Go

`go-bin.txt` tracks manually installed binaries found in `$GOPATH/bin`. It does not know their module paths, so restore these manually with `go install module@version` when needed.
