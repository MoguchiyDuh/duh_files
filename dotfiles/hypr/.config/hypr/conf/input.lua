hl.config({
    input = {
        kb_layout = "us,ru",
        kb_options = "grp:win_space_toggle",
        numlock_by_default = true,
        follow_mouse = 1,
        sensitivity = -0.5,
        accel_profile = "flat",
        repeat_rate = 50,
        repeat_delay = 250,
        touchpad = {
            natural_scroll = true,
            disable_while_typing = true,
            tap_to_click = true,
        },
    },

    gestures = {
        workspace_swipe_distance = 300,
        workspace_swipe_cancel_ratio = 0.5,
        workspace_swipe_create_new = false,
    },
})
