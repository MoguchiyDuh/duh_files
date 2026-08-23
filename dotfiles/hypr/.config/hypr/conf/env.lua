local tokens = require("conf.tokens")
local t = tokens.t

local cursor_size = tostring(t.toolkit and t.toolkit.cursor_size or 24)
local cursor_theme = t.toolkit and t.toolkit.cursor or "Adwaita"

hl.env("XCURSOR_SIZE", cursor_size)
hl.env("HYPRCURSOR_SIZE", cursor_size)
hl.env("XCURSOR_THEME", cursor_theme)
hl.env("HYPRCURSOR_THEME", cursor_theme)

hl.env("QT_QPA_PLATFORMTHEME", "qt6ct")
hl.env("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
hl.env("QT_WAYLAND_DISABLE_WINDOWDECORATION", "1")
hl.env("QT_QPA_PLATFORM", "wayland;xcb")

hl.env("ADW_DEBUG_COLOR_SCHEME", "prefer-dark")
hl.env("GDK_BACKEND", "wayland,x11")
hl.env("SDL_VIDEODRIVER", "wayland")
hl.env("CLUTTER_BACKEND", "wayland")

hl.env("XDG_CURRENT_DESKTOP", "Hyprland")
hl.env("XDG_SESSION_TYPE", "wayland")
hl.env("XDG_SESSION_DESKTOP", "Hyprland")

hl.env("MOZ_ENABLE_WAYLAND", "1")
hl.env("MOZ_WEBRENDER", "1")
hl.env("MOZ_ACCELERATED", "1")
hl.env("BROWSER", "firefox")

hl.env("LIBVA_DRIVER_NAME", "nvidia")
hl.env("GBM_BACKEND", "nvidia-drm")
hl.env("__GLX_VENDOR_LIBRARY_NAME", "nvidia")
hl.env("__GL_YIELD", "USLEEP")
hl.env("__GL_SHADER_DISK_CACHE", "1")
hl.env("__GL_SHADER_DISK_CACHE_PATH", "/tmp")
hl.env("PROTON_ENABLE_NVAPI", "1")
hl.env("DXVK_ENABLE_NVAPI", "1")
