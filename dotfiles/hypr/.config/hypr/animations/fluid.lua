return {
  curves = {
    { name = "fluidSpring", cfg = { type = "spring",  mass = 1, stiffness = 75, dampening = 12 } },
    { name = "fluidExit",   cfg = { type = "bezier",  points = { { 0.4, 0 }, { 1, 1 } } } },
    { name = "fluidFade",   cfg = { type = "bezier",  points = { { 0.5, 0.5 }, { 0.75, 1 } } } },
    { name = "liner",       cfg = { type = "bezier",  points = { { 0, 0 }, { 1, 1 } } } },
  },
  animations = {
    { leaf = "windowsIn",        enabled = true, speed = 5.0, spring = "fluidSpring", style = "popin 85%" },
    { leaf = "windowsOut",       enabled = true, speed = 3.0, bezier = "fluidExit",   style = "popin 85%" },
    { leaf = "windowsMove",      enabled = true, speed = 5.0, spring = "fluidSpring" },
    { leaf = "fade",             enabled = true, speed = 4.0, bezier = "fluidFade" },
    { leaf = "layersIn",         enabled = true, speed = 4.0, spring = "fluidSpring", style = "fade" },
    { leaf = "layersOut",        enabled = true, speed = 3.0, bezier = "fluidExit",   style = "fade" },
    { leaf = "fadeLayersIn",     enabled = true, speed = 3.5, bezier = "fluidFade" },
    { leaf = "fadeLayersOut",    enabled = true, speed = 3.0, bezier = "fluidExit" },
    { leaf = "workspaces",       enabled = true, speed = 5.0, spring = "fluidSpring", style = "slidefade 20%" },
    { leaf = "specialWorkspace", enabled = true, speed = 4.0, spring = "fluidSpring", style = "slidevert" },
    { leaf = "border",           enabled = true, speed = 6.0, bezier = "fluidFade" },
    { leaf = "borderangle",      enabled = true, speed = 100.0, bezier = "liner", style = "loop" },
  },
}
