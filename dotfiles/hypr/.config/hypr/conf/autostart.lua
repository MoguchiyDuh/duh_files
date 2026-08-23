local autostart = {
  "gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'",
  "gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita-dark'",
  "gsettings set org.gnome.desktop.interface font-name 'JetBrainsMono Nerd Font Mono 11'",
  "gsettings set org.gnome.desktop.interface cursor-theme 'Adwaita'",
}

hl.on("hyprland.start", function()
  for _, cmd in ipairs(autostart) do
    hl.exec_cmd(cmd)
  end
end)
