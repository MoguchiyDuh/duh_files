local tokens = require("conf.tokens")
local anim = tokens.t.animations or {}

if not anim.enabled then
    hl.config({ animations = { enabled = false } })
    return
end

hl.config({ animations = { enabled = true } })

for name, spec in pairs(anim.curves or {}) do
    if type(spec) == "table" and type(spec.bezier) == "table" and #spec.bezier == 4 then
        hl.curve(name, {
            type = "bezier",
            points = { { spec.bezier[1], spec.bezier[2] }, { spec.bezier[3], spec.bezier[4] } },
        })
    elseif type(spec) == "table" and type(spec.spring) == "table" then
        hl.curve(name, {
            type = "spring",
            mass = spec.spring.mass or 1,
            stiffness = spec.spring.stiffness or 70,
            dampening = spec.spring.dampening or 15,
        })
    end
end

for leaf, spec in pairs(anim.leaves or {}) do
    if type(spec) == "table" then
        local entry = {
            leaf = leaf,
            enabled = true,
            speed = spec.speed or 1.0,
            bezier = spec.curve or "default",
        }
        if spec.style then
            entry.style = spec.style
        end
        hl.animation(entry)
    end
end
