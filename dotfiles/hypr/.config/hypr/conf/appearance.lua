local colors = require("conf.colors")
local c = colors.c

hl.config({
  general = {
    gaps_in = 6,
    gaps_out = 6,
    border_size = 2,
      col = {
        active_border = {
          colors = { colors.rgb(c.color12), colors.rgb(c.color13) },
          angle = 0,
        },
        inactive_border = colors.rgb(c.color0),
      },
    resize_on_border = false,
    allow_tearing = false,
    layout = "dwindle",
  },

  decoration = {
    rounding = 16,
    rounding_power = 2,
    active_opacity = 1.0,
    inactive_opacity = 0.80,
    shadow = {
      enabled = true,
      range = 20,
      render_power = 3,
      color = colors.rgba("#000000", 0.55),
      offset = { 0, 8 },
    },
    blur = {
      enabled = true,
      size = 8,
      passes = 3,
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
    vrr = false,
    focus_on_activate = true,
    enable_anr_dialog = true,
    allow_session_lock_restore = true,
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
