swayimg.text.size = 16
swayimg.text.color = 0xffdddddd
swayimg.text.background = 0x80000000
swayimg.text.padding = 8
swayimg.imagelist.order = "numeric"

local function toggle_info()
    swayimg.text.visible = not swayimg.text.visible
end

local function noop()
end

local function quote(path)
    return "'" .. path:gsub("'", "'\\''") .. "'"
end

local function trash(mode)
    local img = mode.get_image()
    if img then
        os.execute("trash-put -- " .. quote(img.path))
        swayimg.imagelist.remove(img.path)
        swayimg.text.status = "Trashed: " .. img.path
    end
end

local function pan(mode, dx, dy)
    local pos = mode.get_position()
    local wnd = swayimg.get_window_size()
    mode.set_abs_position(pos.x + math.floor(wnd.width * dx / 10),
                          pos.y + math.floor(wnd.height * dy / 10))
end

local function viewer_binds(mode)
    mode.on_key({ "q", "Escape" }, function() swayimg.exit() end)
    mode.on_key("j", function() mode.open("next") end)
    mode.on_key("k", function() mode.open("prev") end)
    mode.on_key("right", function() mode.open("next") end)
    mode.on_key("left", function() mode.open("prev") end)
    mode.on_key("g", function() mode.open("first") end)
    mode.on_key("Shift+g", function() mode.open("last") end)
    mode.on_key("h", function() pan(mode, 1, 0) end)
    mode.on_key("l", function() pan(mode, -1, 0) end)
    mode.on_key("equal", function() mode.scale = mode.scale * 1.1 end)
    mode.on_key("minus", function() mode.scale = mode.scale / 1.1 end)
    mode.on_key("0", function() mode.reset() end)
    mode.on_key("r", function() mode.reload() end)
    mode.on_key("space", function() mode.mark_image() end)
    mode.on_key("x", function() trash(mode) end)
    mode.on_key("f", function() swayimg.fullscreen = not swayimg.fullscreen end)
    mode.on_key("i", toggle_info)
    mode.on_key("t", noop)
end

local function gallery_binds(mode)
    mode.on_key({ "q", "Escape" }, function() swayimg.exit() end)
    mode.on_key("h", function() mode.select("left") end)
    mode.on_key("l", function() mode.select("right") end)
    mode.on_key("k", function() mode.select("up") end)
    mode.on_key("j", function() mode.select("down") end)
    mode.on_key("g", function() mode.select("first") end)
    mode.on_key("Shift+g", function() mode.select("last") end)
    mode.on_key("Return", function() swayimg.mode = "viewer" end)
    mode.on_key("e", function() swayimg.mode = "viewer" end)
    mode.on_key("equal", function() mode.thumb_size = mode.thumb_size + 10 end)
    mode.on_key("minus", function() mode.thumb_size = mode.thumb_size - 10 end)
    mode.on_key("space", function() mode.mark_image() end)
    mode.on_key("x", function() trash(mode) end)
    mode.on_key("f", function() swayimg.fullscreen = not swayimg.fullscreen end)
    mode.on_key("i", toggle_info)
    mode.on_key("t", noop)
end

viewer_binds(swayimg.viewer)
viewer_binds(swayimg.slideshow)
gallery_binds(swayimg.gallery)

swayimg.viewer.on_key("e", function() swayimg.mode = "gallery" end)
swayimg.slideshow.on_key("e", function() swayimg.mode = "gallery" end)
