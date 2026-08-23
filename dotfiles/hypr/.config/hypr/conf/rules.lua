local floating_utilities = {
    { name = "wifi-manager", class = "^(nm-connection-editor)$" },
    { name = "bluetooth-manager", class = "^(blueman-manager)$" },
    { name = "sound-manager", class = "^(org.pulseaudio.pavucontrol)$" },
    { name = "polkit-agent", class = "^(polkit-gnome-authentication-agent-1)$" },
}

for _, rule in ipairs(floating_utilities) do
    hl.window_rule({
        name = rule.name,
        match = { class = rule.class },
        float = true,
        center = true,
        pin = true,
        opaque = true,
    })
end

hl.window_rule({
    name = "pip-window",
    match = { title = "^(Picture-in-Picture)$" },
    float = true,
    pin = true,
    size = "25% 25%",
    center = true,
    opaque = true,
})

hl.window_rule({
    name = "discord-popout",
    match = { class = "^(discord)$", title = "^(.*Popout.*|.*Stream.*)$" },
    float = true,
    pin = true,
    size = "25% 25%",
    center = true,
    opaque = true,
})

hl.window_rule({
    name = "file-dialogs",
    match = {
        title = "^(Open File|Select a File|Choose wallpaper|Open Folder|Save As|Library|File Upload)(.*)$",
    },
    float = true,
    center = true,
    opaque = true,
})

hl.window_rule({
    name = "file-dialogs-wants",
    match = { title = "^(.*)(wants to save|wants to open)$" },
    float = true,
    center = true,
    opaque = true,
})

hl.window_rule({
    name = "suppress-maximize",
    match = { class = ".*" },
    suppress_event = "maximize",
})

hl.window_rule({
    name = "fix-xwayland-drags",
    match = {
        class = "^$",
        title = "^$",
        xwayland = true,
        float = true,
        fullscreen = false,
        pin = false,
    },
    no_focus = true,
})

hl.layer_rule({
    name = "shell-blur",
    match = { namespace = "^duhshell(-.*)?$" },
    blur = true,
    ignore_alpha = 0.3,
})

hl.layer_rule({
    name = "notifications-blur",
    match = { namespace = "^swaync(-.*)?$" },
    blur = true,
    ignore_alpha = 0.3,
})
