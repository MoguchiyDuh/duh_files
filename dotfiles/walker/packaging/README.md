# walker (patched)

Patched build of `walker` 2.17.0 that fixes custom grid item templates for menu providers.

## Why

Upstream walker never loads a per-provider grid template for `menus:*` providers.
`create_item` (src/renderers/mod.rs) looks up `grid_items[provider]`, but the theme
loader only ever populates `grid_items` from the built-in default and from
`item_*_grid.xml` files that are never in its read list. Result: `menus:wallpapers`
always rendered the built-in `item.xml` (a 26px `GtkImage`), so custom wallpaper
grid layouts had no effect.

`grid-items.patch` makes the loader mirror each theme `item_<provider>.xml` into
`grid_items`, so `item_menus-wallpapers.xml` (a `GtkPicture` with `content-fit`)
drives the grid cells.

## Rebuild

    makepkg -f
    sudo pacman -U walker-2.17.0-1-x86_64.pkg.tar.zst

## Prevent overwrite

`walker` is in `IgnorePkg` in `/etc/pacman.conf`. Remove it there to allow upstream
upgrades, then re-apply this patch against the new version if the upstream bug persists.
