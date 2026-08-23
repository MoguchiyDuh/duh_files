Name = "animations"
NamePretty = "Animations"
Description = "Hyprland animation presets (drop-in files in ~/.config/hypr/animations)"
Icon = "preferences-desktop-multitasking-symbolic"
Action = 'bash "$HOME/.config/walker/scripts/utility.sh" "animation.%VALUE%"'
SearchName = true
FixedOrder = false
Cache = false

function GetEntries()
  local entries = {}
  local dir = os.getenv("HOME") .. "/.config/hypr/animations"
  local handle = io.popen("ls -1 " .. dir .. " 2>/dev/null")
  if not handle then
    return entries
  end

  for line in handle:lines() do
    local name = line:match("^(.*)%.lua$")
    if name and name ~= "" then
      entries[#entries + 1] = {
        Text = name:sub(1, 1):upper() .. name:sub(2),
        Subtext = "Apply " .. name .. " animations",
        Value = name,
        Icon = "preferences-desktop-multitasking-symbolic",
        Keywords = { "animation", "motion", "hyprland", name },
      }
    end
  end

  handle:close()
  table.sort(entries, function(a, b)
    return a.Text:lower() < b.Text:lower()
  end)

  return entries
end
