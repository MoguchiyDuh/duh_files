Name = "themes"
NamePretty = "Change theme"
Description = "Apply a wallust theme across the desktop"
Icon = "preferences-desktop-theme"
Action = 'bash "$HOME/.config/walker/scripts/utility.sh" "theme.%VALUE%"'
Terminal = true
SearchName = true
FixedOrder = true
Cache = false

local function shell_quote(value)
  return "'" .. value:gsub("'", "'\"'\"'") .. "'"
end

function GetEntries()
  local entries = {}
  local handle = io.popen("wallust theme list 2>/dev/null | sed -n 's/^- //p'")
  if not handle then
    return entries
  end
  for line in handle:lines() do
    local name = line:match("^%s*(.-)%s*$")
    if name ~= "" then
      entries[#entries + 1] = {
        Text = name,
        Subtext = "Apply " .. name .. " via wallust",
        Value = name,
        Icon = "preferences-desktop-theme",
        Keywords = { "theme", "appearance", "design", name },
      }
    end
  end
  handle:close()
  table.sort(entries, function(a, b)
    return a.Text:lower() < b.Text:lower()
  end)
  return entries
end
