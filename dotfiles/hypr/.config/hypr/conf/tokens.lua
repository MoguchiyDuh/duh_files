local M = {}

local defaults = {
    profile = "fallback",
    animation = "snappy",
    color = {
        background = "#101014",
        foreground = "#E6E6E6",
        accent = "#7AA2F7",
        accent_alt = "#89DDFF",
        error = "#E5484D",
        color0 = "#1A1B26",
        surface = { "#101014", "#17181D", "#212228", "#2C2D33", "#3A3B41" },
    },
    shape = { radius = 16, radius_sm = 10, radius_lg = 24, border = 2 },
    spacing = { gap_in = 6, gap_out = 6, pad = 8 },
    effect = {
        blur = true,
        blur_size = 8,
        blur_passes = 3,
        shadow = true,
        shadow_range = 20,
        shadow_offset = { 0, 8 },
        opacity_active = 1.0,
        opacity_inactive = 0.9,
        surface_alpha = 0.85,
    },
    shell = { bar_height = 40, bar_margin = 8 },
    animations = { enabled = true, curves = {}, leaves = {} },
}

local function merge(base, override)
    if type(override) ~= "table" then
        return base
    end
    local out = {}
    for k, v in pairs(base) do
        out[k] = v
    end
    for k, v in pairs(override) do
        if type(v) == "table" and type(out[k]) == "table" then
            out[k] = merge(out[k], v)
        else
            out[k] = v
        end
    end
    return out
end

local function load()
    local home = os.getenv("HOME") or ""
    local path = home .. "/.cache/duhshell/tokens.lua"
    local chunk = loadfile(path)
    if not chunk then
        return defaults
    end
    local ok, data = pcall(chunk)
    if not ok or type(data) ~= "table" then
        return defaults
    end
    return merge(defaults, data)
end

M.t = load()

function M.rgba(hex, alpha)
    local raw = tostring(hex or "#000000"):gsub("#", "")
    if #raw ~= 6 then
        raw = "000000"
    end
    local a = math.floor(math.max(0, math.min(1, alpha or 1)) * 255 + 0.5)
    return string.format("rgba(%s%02x)", raw, a)
end

function M.rgb(hex)
    local raw = tostring(hex or "#000000"):gsub("#", "")
    if #raw ~= 6 then
        raw = "000000"
    end
    return string.format("rgb(%s)", raw)
end

function M.surface(level)
    local ramp = M.t.color.surface or {}
    if #ramp == 0 then
        return M.t.color.background
    end
    local i = math.max(1, math.min(#ramp, (level or 0) + 1))
    return ramp[i]
end

return M
