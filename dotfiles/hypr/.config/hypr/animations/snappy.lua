return {
  curves = {
    { name = "snap", cfg = { type = "bezier", points = { { 0.25, 0.9 }, { 0.5, 1 } } } },
    { name = "snapOut", cfg = { type = "bezier", points = { { 0.4, 0 }, { 1, 1 } } } },
    { name = "liner", cfg = { type = "bezier", points = { { 1, 1 }, { 1, 1 } } } },
  },
  animations = {
    { leaf = "windowsIn",        enabled = true, speed = 1.0, bezier = "snap",   style = "popin 85%" },
    { leaf = "windowsOut",       enabled = true, speed = 0.7, bezier = "snapOut", style = "popin 90%" },
    { leaf = "windowsMove",      enabled = true, speed = 1.0, bezier = "snap",   style = "slide" },
    { leaf = "fade",             enabled = true, speed = 0.8, bezier = "snap" },
    { leaf = "layersIn",         enabled = true, speed = 0.8, bezier = "snap",   style = "fade" },
    { leaf = "layersOut",        enabled = true, speed = 0.6, bezier = "snapOut", style = "fade" },
    { leaf = "fadeLayersIn",     enabled = true, speed = 0.8, bezier = "snap" },
    { leaf = "fadeLayersOut",    enabled = true, speed = 0.6, bezier = "snapOut" },
    { leaf = "workspaces",       enabled = true, speed = 1.5, bezier = "snap",   style = "slidefade 20%" },
    { leaf = "specialWorkspace", enabled = true, speed = 1.0, bezier = "snap",   style = "slidevert" },
  },
}
