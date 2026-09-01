Name = "themes"
NamePretty = "Change theme"
Description = "Apply a matugen color from hex"
Icon = "preferences-desktop-theme"
Action = 'matugen color hex --prefer saturation "%VALUE%"'
SearchName = true
FixedOrder = true
Cache = false

function GetEntries()
  return {}
end
