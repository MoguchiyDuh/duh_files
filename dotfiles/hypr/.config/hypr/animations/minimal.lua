return {
  curves = {
    { name = "minFade", cfg = { type = "bezier", points = { { 0.25, 1 }, { 0.5, 1 } } } },
    { name = "liner",   cfg = { type = "bezier", points = { { 0, 0 },   { 1, 1 } } } },
  },
  animations = {
    { leaf = "windowsIn",        enabled = true, speed = 2.0, bezier = "minFade", style = "popin 95%" },
    { leaf = "windowsOut",       enabled = true, speed = 1.5, bezier = "minFade", style = "popin 95%" },
    { leaf = "windowsMove",      enabled = false },
    { leaf = "fade",             enabled = true, speed = 4.0, bezier = "minFade" },
    { leaf = "layersIn",         enabled = true, speed = 2.0, bezier = "minFade", style = "fade" },
    { leaf = "layersOut",        enabled = true, speed = 1.5, bezier = "minFade", style = "fade" },
    { leaf = "fadeLayersIn",     enabled = true, speed = 1.8, bezier = "minFade" },
    { leaf = "fadeLayersOut",    enabled = true, speed = 1.5, bezier = "minFade" },
    { leaf = "workspaces",       enabled = true, speed = 0.5, bezier = "liner",   style = "fade" },
    { leaf = "specialWorkspace", enabled = true, speed = 0.5, bezier = "liner",   style = "fade" },
    { leaf = "border",           enabled = false },
    { leaf = "borderangle",      enabled = true, speed = 100.0, bezier = "liner", style = "loop" },
  },
}
