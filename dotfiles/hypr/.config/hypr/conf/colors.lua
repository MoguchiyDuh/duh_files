local M = {}

local fallback = {
  background = "#1A1B26",
  foreground = "#C0CAF5",
  cursor = "#C0CAF5",
  color0 = "#15161E",
  color1 = "#F7768E",
  color2 = "#9ECE6A",
  color3 = "#E0AF68",
  color4 = "#7AA2F7",
  color5 = "#BB9AF7",
  color6 = "#7DCFFF",
  color7 = "#A9B1D6",
  color8 = "#414868",
  color9 = "#F7768E",
  color10 = "#9ECE6A",
  color11 = "#E0AF68",
  color12 = "#7AA2F7",
  color13 = "#BB9AF7",
  color14 = "#7DCFFF",
  color15 = "#C0CAF5",
}

local function palette()
  local path = (os.getenv("HOME") or "") .. "/.cache/wallust/colors.lua"
  local chunk = loadfile(path)
  if not chunk then
    return fallback
  end
  local ok, data = pcall(chunk)
  if not ok or type(data) ~= "table" then
    return fallback
  end
  local merged = {}
  for key, value in pairs(fallback) do
    merged[key] = value
  end
  for key, value in pairs(data) do
    if type(key) == "string" and type(value) == "string" then
      merged[key] = value
    end
  end
  return merged
end

M.c = palette()

function M.rgb(hex)
  local raw = tostring(hex or ""):gsub("#", "")
  if #raw ~= 6 then
    raw = fallback.background:sub(2)
  end
  return string.format("rgb(%s)", raw)
end

function M.rgba(hex, alpha)
  local raw = tostring(hex or ""):gsub("#", "")
  if #raw ~= 6 then
    raw = fallback.background:sub(2)
  end
  local a = math.floor(math.max(0, math.min(1, alpha or 1)) * 255 + 0.5)
  return string.format("rgba(%s%02x)", raw, a)
end

return M
