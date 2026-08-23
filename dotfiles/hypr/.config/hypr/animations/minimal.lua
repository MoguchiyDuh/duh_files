return {
  curves = {
    { name = "liner", cfg = { type = "bezier", points = { { 1, 1 }, { 1, 1 } } } },
  },
  animations = {
    { leaf = "windowsIn",        enabled = true, speed = 0.5, bezier = "liner", style = "popin 95%" },
    { leaf = "windowsOut",       enabled = true, speed = 0.4, bezier = "liner", style = "popin 95%" },
    { leaf = "windowsMove",      enabled = true, speed = 0.5, bezier = "liner", style = "slide" },
    { leaf = "fade",             enabled = true, speed = 0.5, bezier = "liner" },
    { leaf = "layersIn",         enabled = true, speed = 0.4, bezier = "liner", style = "fade" },
    { leaf = "layersOut",        enabled = true, speed = 0.4, bezier = "liner", style = "fade" },
    { leaf = "fadeLayersIn",     enabled = true, speed = 0.4, bezier = "liner" },
    { leaf = "fadeLayersOut",    enabled = true, speed = 0.4, bezier = "liner" },
    { leaf = "workspaces",       enabled = true, speed = 1.0, bezier = "liner", style = "fade" },
    { leaf = "specialWorkspace", enabled = true, speed = 0.5, bezier = "liner", style = "slidevert" },
  },
}
