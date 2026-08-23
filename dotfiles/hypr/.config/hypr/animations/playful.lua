return {
  curves = {
    { name = "rubber", cfg = { type = "spring", mass = 1, stiffness = 90, dampening = 8 } },
    { name = "settle", cfg = { type = "spring", mass = 1, stiffness = 140, dampening = 14 } },
    { name = "liner", cfg = { type = "bezier", points = { { 1, 1 }, { 1, 1 } } } },
  },
  animations = {
    { leaf = "windowsIn",        enabled = true, speed = 1.6, spring = "rubber", style = "popin 80%" },
    { leaf = "windowsOut",       enabled = true, speed = 1.0, spring = "settle", style = "popin 85%" },
    { leaf = "windowsMove",      enabled = true, speed = 1.6, spring = "rubber", style = "slide" },
    { leaf = "fade",             enabled = true, speed = 1.0, spring = "settle" },
    { leaf = "layersIn",         enabled = true, speed = 1.2, spring = "settle", style = "fade" },
    { leaf = "layersOut",        enabled = true, speed = 0.9, spring = "settle", style = "fade" },
    { leaf = "fadeLayersIn",     enabled = true, speed = 1.0, spring = "settle" },
    { leaf = "fadeLayersOut",    enabled = true, speed = 0.9, spring = "settle" },
    { leaf = "workspaces",       enabled = true, speed = 2.4, spring = "rubber", style = "slide" },
    { leaf = "specialWorkspace", enabled = true, speed = 1.6, spring = "settle", style = "slidevert" },
  },
}
