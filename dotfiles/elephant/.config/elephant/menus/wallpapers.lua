Name = "wallpapers"
NamePretty = "Wallpapers"
Description = "Images and videos from ~/Pictures/Wallpapers"
Icon = "preferences-desktop-wallpaper"
Action = 'bash "$HOME/.config/walker/scripts/utility.sh" wallpaper'
SearchName = true
FixedOrder = true
Cache = false

local home = os.getenv("HOME")
local wallpaper_dir = home .. "/Pictures/Wallpapers"
local helper = home .. "/.config/walker/scripts/utility.sh"
RefreshOnChange = { wallpaper_dir }

local function shell_quote(value)
    return "'" .. value:gsub("'", "'\"'\"'") .. "'"
end

local function nul_lines(data)
    local values = {}
    local start = 1
    while true do
        local stop = data:find("\0", start, true)
        if not stop then
            break
        end
        table.insert(values, data:sub(start, stop - 1))
        start = stop + 1
    end
    return values
end

local function thumbnail(path)
    local command = "bash " .. shell_quote(helper) .. " thumbnail " .. shell_quote(path) .. " 2>/dev/null"
    local handle = io.popen(command)
    if not handle then
        return ""
    end
    local result = handle:read("*l") or ""
    handle:close()
    return result
end

function GetEntries()
    local entries = {}
    local command = "find -- " .. shell_quote(wallpaper_dir) ..
        " -type f \\( -name '*.jpg' -o -name '*.jpeg' -o -name '*.png'" ..
        " -o -name '*.webp' -o -name '*.gif' -o -name '*.mp4'" ..
        " -o -name '*.avi' -o -name '*.mov' -o -name '*.mkv'" ..
        " -o -name '*.webm' \\) -print0 2>/dev/null"
    local handle = io.popen(command)
    if not handle then
        return entries
    end

    local paths = nul_lines(handle:read("*a") or "")
    handle:close()
    table.sort(paths, function(left, right)
        return left:lower() < right:lower()
    end)

    for _, path in ipairs(paths) do
        local name = path:match("([^/]+)$") or path
        table.insert(entries, {
            Text = name,
            Value = path,
            Icon = thumbnail(path),
            Keywords = { "wallpaper", "background", name },
        })
    end
    return entries
end
