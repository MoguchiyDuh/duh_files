local home = os.getenv("HOME") or ""
local cache = os.getenv("XDG_CACHE_HOME") or (home .. "/.cache")
local dir = home .. "/.config/hypr/animations"
local selected = "snappy"

local handle = io.open(cache .. "/current-animation", "r")
if handle then
  local content = handle:read("*l")
  handle:close()
  if content and content ~= "" then
    selected = content
  end
end

hl.config({ animations = { enabled = true } })

local ok, preset = pcall(dofile, dir .. "/" .. selected .. ".lua")

if not ok or type(preset) ~= "table" then
  preset = {
    curves = {
      { name = "liner", cfg = { type = "bezier", points = { { 1, 1 }, { 1, 1 } } } },
    },
    animations = {
      { leaf = "fade", enabled = true, speed = 0.5, bezier = "liner" },
    },
  }
end

for _, curve in ipairs(preset.curves or {}) do
  hl.curve(curve.name, curve.cfg)
end

for _, animation in ipairs(preset.animations or {}) do
  hl.animation(animation)
end
