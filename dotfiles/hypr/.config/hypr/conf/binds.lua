local mod = "SUPER"
local scripts = (os.getenv("HOME") or "") .. "/.config/hypr/scripts"
local walker_scripts = (os.getenv("HOME") or "") .. "/.config/walker/scripts"

local terminal = "kitty"
local browser = "firefox"
local filemanager = "nautilus --new-window"

local walker_wrapper = scripts .. "/walker.sh"

hl.bind(mod .. " + RETURN", hl.dsp.exec_cmd(terminal), { description = "Open terminal" })
hl.bind(mod .. " + E", hl.dsp.exec_cmd(filemanager), { description = "Open file manager" })
hl.bind(mod .. " + B", hl.dsp.exec_cmd(browser), { description = "Open browser" })
hl.bind("CTRL + SHIFT + escape", hl.dsp.exec_cmd(terminal .. " btop"), { description = "System monitor" })

hl.bind(mod .. " + R", hl.dsp.exec_cmd(walker_wrapper .. " toggle"), { description = "Open launcher" })
hl.bind(mod .. " + X", hl.dsp.exec_cmd("walker --provider menus:wallpapers"), { description = "Wallpaper picker" })
hl.bind(mod .. " + V", hl.dsp.exec_cmd("walker --provider clipboard"), { description = "Clipboard history" })
hl.bind(mod .. " + PERIOD", hl.dsp.exec_cmd("walker --provider symbols"), { description = "Symbols and emoji" })
hl.bind(mod .. " + Tab", hl.dsp.exec_cmd("walker --provider windows"), { description = "Window switcher" })
hl.bind("F1", hl.dsp.exec_cmd("walker --provider menus:keybinds"), { description = "Keybind reference" })
hl.bind(mod .. " + SHIFT + W", hl.dsp.exec_cmd(walker_scripts .. "/utility.sh provider.translate"), { description = "Translate text" })
hl.bind(mod .. " + SHIFT + T", hl.dsp.exec_cmd(walker_scripts .. "/utility.sh ocr.eng-rus"), { description = "OCR to clipboard" })
hl.bind(mod .. " + SHIFT + C", hl.dsp.exec_cmd(walker_scripts .. "/utility.sh color.pick"), { description = "Color picker" })
hl.bind("CTRL + ALT + DELETE", hl.dsp.exec_cmd("hyprlock"), { description = "Lock screen" })

hl.bind(mod .. " + SHIFT + S", hl.dsp.exec_cmd(scripts .. "/screenshot.sh area"), { description = "Screenshot area" })
hl.bind("Print", hl.dsp.exec_cmd(scripts .. "/screenshot.sh fullscreen"), { description = "Screenshot screen" })
hl.bind("CTRL + Print", hl.dsp.exec_cmd(scripts .. "/screenshot.sh area"), { description = "Screenshot area" })
hl.bind("ALT + Print", hl.dsp.exec_cmd(scripts .. "/screenshot.sh active"), { description = "Screenshot window" })
hl.bind("SHIFT + Print", hl.dsp.exec_cmd(scripts .. "/record.sh"), { description = "Toggle recording" })

hl.bind(mod .. " + SHIFT + R", hl.dsp.exec_cmd("systemctl --user restart waybar.service"), { description = "Restart waybar" })

hl.bind(mod .. " + Q", hl.dsp.window.close(), { description = "Close window" })
hl.bind(mod .. " + SHIFT + Q", hl.dsp.exec_cmd([[pid=$(hyprctl -j activewindow | jq -er '.pid | numbers | select(. > 1 and . == floor)') && kill -- "$pid"]]), { description = "Force-kill window" })
hl.bind(mod .. " + T", hl.dsp.window.float({ action = "toggle" }), { description = "Toggle floating" })
hl.bind(mod .. " + I", hl.dsp.window.pin(), { description = "Pin window" })
hl.bind(mod .. " + F", hl.dsp.window.fullscreen(), { description = "Fullscreen" })
hl.bind(mod .. " + SHIFT + F", hl.dsp.window.fullscreen({ mode = "maximized" }), { description = "Maximize" })
hl.bind(mod .. " + P", hl.dsp.window.pseudo(), { description = "Toggle pseudotiling" })
hl.bind(mod .. " + O", hl.dsp.layout("togglesplit"), { description = "Toggle split direction" })

local directions = {
    { key = "H", arrow = "left",  dir = "left",  dx = -128, dy = 0 },
    { key = "L", arrow = "right", dir = "right", dx = 128,  dy = 0 },
    { key = "K", arrow = "up",    dir = "up",    dx = 0,    dy = -128 },
    { key = "J", arrow = "down",  dir = "down",  dx = 0,    dy = 128 },
}

for _, d in ipairs(directions) do
    for _, key in ipairs({ d.key, d.arrow }) do
        hl.bind(mod .. " + " .. key, hl.dsp.focus({ direction = d.dir }), { description = "Focus " .. d.dir })
        hl.bind(mod .. " + SHIFT + " .. key, hl.dsp.window.swap({ direction = d.dir }), { description = "Swap " .. d.dir })
        hl.bind(mod .. " + CTRL + " .. key, hl.dsp.window.resize({ x = d.dx, y = d.dy, relative = true }), { repeating = true, description = "Resize " .. d.dir })
    end
end

hl.bind(mod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true, description = "Move window" })
hl.bind(mod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true, description = "Resize window" })

hl.bind("ALT + Tab", hl.dsp.window.cycle_next(), { repeating = true, description = "Next window" })
hl.bind("SHIFT + ALT + Tab", hl.dsp.window.cycle_next({ prev = true }), { repeating = true, description = "Previous window" })

for i = 1, 10 do
    local key = i % 10
    hl.bind(mod .. " + " .. key, hl.dsp.focus({ workspace = i }), { description = "Workspace " .. i })
    hl.bind(mod .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = i }), { description = "Move to workspace " .. i })
end

local relative = {
    { keys = { "H", "left" },  target = "e-1", label = "previous" },
    { keys = { "L", "right" }, target = "e+1", label = "next" },
}

for _, r in ipairs(relative) do
    for _, key in ipairs(r.keys) do
        hl.bind(mod .. " + ALT + " .. key, hl.dsp.focus({ workspace = r.target }), { description = "Go to " .. r.label .. " workspace" })
        hl.bind(mod .. " + SHIFT + ALT + " .. key, hl.dsp.window.move({ workspace = r.target }), { description = "Move to " .. r.label .. " workspace" })
    end
end

hl.bind(mod .. " + M", hl.dsp.workspace.toggle_special("magic"), { description = "Toggle scratchpad" })
hl.bind(mod .. " + SHIFT + M", hl.dsp.window.move({ workspace = "special:magic" }), { description = "Move to scratchpad" })

local media = {
    { "XF86AudioRaiseVolume",  "wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+",   "Volume up" },
    { "XF86AudioLowerVolume",  "wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-",         "Volume down" },
    { "XF86AudioMute",         "wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle",        "Mute output" },
    { "XF86AudioMicMute",      "wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle",     "Mute microphone" },
    { "XF86MonBrightnessUp",   "brightnessctl -e4 -n2 set 5%+",                     "Brightness up" },
    { "XF86MonBrightnessDown", "brightnessctl -e4 -n2 set 5%-",                     "Brightness down" },
}

for _, m in ipairs(media) do
    hl.bind(m[1], hl.dsp.exec_cmd(m[2]), { locked = true, repeating = true, description = m[3] })
end

local players = {
    { "XF86AudioNext",  "playerctl next",       "Next track" },
    { "XF86AudioPause", "playerctl play-pause", "Play/pause" },
    { "XF86AudioPlay",  "playerctl play-pause", "Play/pause" },
    { "XF86AudioPrev",  "playerctl previous",   "Previous track" },
}

for _, p in ipairs(players) do
    hl.bind(p[1], hl.dsp.exec_cmd(p[2]), { locked = true, description = p[3] })
end
