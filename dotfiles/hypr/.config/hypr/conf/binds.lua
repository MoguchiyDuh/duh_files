local mod = "SUPER"
local scripts = (os.getenv("HOME") or "") .. "/.config/hypr/scripts"
local rofi = (os.getenv("HOME") or "") .. "/.config/rofi/scripts"

local terminal = "kitty"
local browser = "firefox"
local filemanager = "nautilus --new-window"

local failed = {}

local function bind(keys, make, opts)
    local ok, err = pcall(function()
        hl.bind(keys, make(), opts)
    end)
    if not ok then
        failed[#failed + 1] = keys .. " (" .. tostring(err) .. ")"
    end
end

local function run(cmd)
    return function()
        return hl.dsp.exec_cmd(cmd)
    end
end

local function dsp(fn, arg)
    return function()
        if arg == nil then
            return fn()
        end
        return fn(arg)
    end
end

bind(mod .. " + RETURN", run(terminal), { description = "Open terminal" })
bind(mod .. " + E", run(filemanager), { description = "Open file manager" })
bind(mod .. " + B", run(browser), { description = "Open browser" })
bind("CTRL + SHIFT + escape", run(terminal .. " btop"), { description = "System monitor" })

bind(mod .. " + R", run(rofi .. "/spotlight.sh"), { description = "Open launcher" })
bind(mod .. " + V", run(rofi .. "/clipboard.sh"), { description = "Clipboard history" })
bind("CTRL + ALT + DELETE", run("wlogout"), { description = "Session menu" })

bind(mod .. " + SHIFT + S", run(scripts .. "/screenshot.sh area"), { description = "Screenshot area" })
bind("Print", run(scripts .. "/screenshot.sh fullscreen"), { description = "Screenshot screen" })
bind("CTRL + Print", run(scripts .. "/screenshot.sh area"), { description = "Screenshot area" })
bind("ALT + Print", run(scripts .. "/screenshot.sh active"), { description = "Screenshot window" })
bind("SHIFT + Print", run(scripts .. "/record.sh"), { description = "Toggle recording" })

bind(mod .. " + SHIFT + R", run("pkill -x waybar; waybar &"), { description = "Restart waybar" })

bind(mod .. " + Q", dsp(hl.dsp.window.close), { description = "Close window" })
bind(
    mod .. " + SHIFT + Q",
    run([[pid=$(hyprctl -j activewindow | jq -er '.pid | numbers | select(. > 1 and . == floor)') && kill -- "$pid"]]),
    { description = "Force-kill window" }
)
bind(mod .. " + T", dsp(hl.dsp.window.float, { action = "toggle" }), { description = "Toggle floating" })
bind(mod .. " + I", dsp(hl.dsp.window.pin), { description = "Pin window" })
bind(mod .. " + F", dsp(hl.dsp.window.fullscreen), { description = "Fullscreen" })
bind(mod .. " + SHIFT + F", dsp(hl.dsp.window.fullscreen, { mode = "maximized" }), { description = "Maximize" })
bind(mod .. " + P", dsp(hl.dsp.window.pseudo), { description = "Toggle pseudotiling" })
bind(mod .. " + O", dsp(hl.dsp.layout, "togglesplit"), { description = "Toggle split direction" })

local directions = {
    { key = "H", arrow = "left", dir = "left", dx = -128, dy = 0 },
    { key = "L", arrow = "right", dir = "right", dx = 128, dy = 0 },
    { key = "K", arrow = "up", dir = "up", dx = 0, dy = -128 },
    { key = "J", arrow = "down", dir = "down", dx = 0, dy = 128 },
}

for _, d in ipairs(directions) do
    for _, key in ipairs({ d.key, d.arrow }) do
        bind(mod .. " + " .. key, dsp(hl.dsp.focus, { direction = d.dir }), {
            description = "Focus " .. d.dir,
        })
        bind(mod .. " + SHIFT + " .. key, dsp(hl.dsp.window.swap, { direction = d.dir }), {
            description = "Swap " .. d.dir,
        })
        bind(mod .. " + CTRL + " .. key, dsp(hl.dsp.window.resize, { x = d.dx, y = d.dy, relative = true }), {
            repeating = true,
            description = "Resize " .. d.dir,
        })
    end
end

bind(mod .. " + mouse:272", dsp(hl.dsp.window.drag), { mouse = true, description = "Move window" })
bind(mod .. " + mouse:273", dsp(hl.dsp.window.resize), { mouse = true, description = "Resize window" })

bind("ALT + Tab", dsp(hl.dsp.window.cycle_next), { repeating = true, description = "Next window" })
bind("SHIFT + ALT + Tab", dsp(hl.dsp.window.cycle_next, { prev = true }), {
    repeating = true,
    description = "Previous window",
})

for i = 1, 10 do
    local key = i % 10
    bind(mod .. " + " .. key, dsp(hl.dsp.focus, { workspace = i }), {
        description = "Workspace " .. i,
    })
    bind(mod .. " + SHIFT + " .. key, dsp(hl.dsp.window.move, { workspace = i }), {
        description = "Move to workspace " .. i,
    })
end

local relative = {
    { keys = { "H", "left" }, target = "e-1", label = "previous" },
    { keys = { "L", "right" }, target = "e+1", label = "next" },
}

for _, r in ipairs(relative) do
    for _, key in ipairs(r.keys) do
        bind(mod .. " + ALT + " .. key, dsp(hl.dsp.focus, { workspace = r.target }), {
            description = "Go to " .. r.label .. " workspace",
        })
        bind(mod .. " + SHIFT + ALT + " .. key, dsp(hl.dsp.window.move, { workspace = r.target }), {
            description = "Move to " .. r.label .. " workspace",
        })
    end
end

bind(mod .. " + M", dsp(hl.dsp.workspace.toggle_special, "magic"), { description = "Toggle scratchpad" })
bind(mod .. " + SHIFT + M", dsp(hl.dsp.window.move, { workspace = "special:magic" }), {
    description = "Move to scratchpad",
})

local media = {
    { "XF86AudioRaiseVolume", "wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+", "Volume up" },
    { "XF86AudioLowerVolume", "wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-", "Volume down" },
    { "XF86AudioMute", "wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle", "Mute output" },
    { "XF86AudioMicMute", "wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle", "Mute microphone" },
    { "XF86MonBrightnessUp", "brightnessctl -e4 -n2 set 5%+", "Brightness up" },
    { "XF86MonBrightnessDown", "brightnessctl -e4 -n2 set 5%-", "Brightness down" },
}

for _, m in ipairs(media) do
    bind(m[1], run(m[2]), { locked = true, repeating = true, description = m[3] })
end

local players = {
    { "XF86AudioNext", "playerctl next", "Next track" },
    { "XF86AudioPause", "playerctl play-pause", "Play/pause" },
    { "XF86AudioPlay", "playerctl play-pause", "Play/pause" },
    { "XF86AudioPrev", "playerctl previous", "Previous track" },
}

for _, p in ipairs(players) do
    bind(p[1], run(p[2]), { locked = true, description = p[3] })
end

if #failed > 0 then
    local text = "duhshell: " .. #failed .. " keybind(s) failed to register"
    pcall(hl.notification.create, { text = text, timeout = 10000 })
    for _, entry in ipairs(failed) do
        print("[duhshell] bind failed: " .. entry)
    end
end
