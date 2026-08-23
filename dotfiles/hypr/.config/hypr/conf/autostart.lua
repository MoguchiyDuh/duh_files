local autostart = {
    "awww-daemon",
    "hypridle",
    "waybar",
    "wl-paste --type text --watch ~/.config/waybar/scripts/clipboard.sh store",
    "wl-paste --type image --watch ~/.config/waybar/scripts/clipboard.sh store",
    "clash-verge",
    "flatpak run org.telegram.desktop -startintray",
    "flatpak run com.discordapp.Discord --start-minimized",
}

hl.on("hyprland.start", function()
    for _, cmd in ipairs(autostart) do
        hl.exec_cmd(cmd)
    end
end)
