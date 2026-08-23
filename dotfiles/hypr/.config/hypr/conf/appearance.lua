local tokens = require("conf.tokens")
local t = tokens.t

local shape, space, fx = t.shape, t.spacing, t.effect

hl.config({
    general = {
        gaps_in = space.gap_in,
        gaps_out = space.gap_out,
        border_size = shape.border,
        col = {
            active_border = {
                colors = { tokens.rgba(t.color.accent, 1), tokens.rgba(t.color.accent_alt, 1) },
                angle = 45,
            },
            inactive_border = tokens.rgba(t.color.color0, 1),
        },
        resize_on_border = false,
        allow_tearing = false,
        layout = "dwindle",
    },

    decoration = {
        rounding = shape.radius,
        rounding_power = 2,
        active_opacity = fx.opacity_active,
        inactive_opacity = fx.opacity_inactive,
        shadow = {
            enabled = fx.shadow,
            range = fx.shadow_range,
            render_power = 3,
            color = tokens.rgba("#000000", 0.55),
            offset = { fx.shadow_offset[1] or 0, fx.shadow_offset[2] or 0 },
        },
        blur = {
            enabled = fx.blur,
            size = fx.blur_size,
            passes = fx.blur_passes,
            new_optimizations = true,
            ignore_opacity = true,
            xray = false,
            vibrancy = 0.1696,
        },
    },

    dwindle = {
        preserve_split = true,
    },

    binds = {
        workspace_back_and_forth = true,
        allow_workspace_cycles = true,
        pass_mouse_when_bound = false,
    },

    misc = {
        disable_hyprland_logo = true,
        disable_splash_rendering = true,
        force_default_wallpaper = 0,
        vrr = 0,
        focus_on_activate = true,
        enable_anr_dialog = true,
        mouse_move_enables_dpms = true,
        key_press_enables_dpms = true,
    },

    xwayland = {
        force_zero_scaling = true,
    },

    ecosystem = {
        no_update_news = true,
        no_donation_nag = true,
    },

    cursor = {
        no_hardware_cursors = false,
        enable_hyprcursor = true,
    },

    opengl = {
        nvidia_anti_flicker = true,
    },
})
