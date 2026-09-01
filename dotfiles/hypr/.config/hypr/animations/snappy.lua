return {
  curves = {
    { name = "snappyOut",  cfg = { type = "bezier", points = { { 0.13, 1 }, { 0.1, 1 } } } },
    { name = "snappyExit", cfg = { type = "bezier", points = { { 0, 0 },    { 1, 1 } } } },
    { name = "liner",      cfg = { type = "bezier", points = { { 0, 0 },    { 1, 1 } } } },
  },
  animations = {
    { leaf = "windowsIn",        enabled = true, speed = 5.0, bezier = "snappyOut",  style = "popin 87%" },
    { leaf = "windowsOut",       enabled = true, speed = 4.0, bezier = "snappyExit", style = "popin 87%" },
    { leaf = "windowsMove",      enabled = true, speed = 8.0, bezier = "snappyOut" },
    { leaf = "fade",             enabled = true, speed = 5.0, bezier = "snappyOut" },
    { leaf = "layersIn",         enabled = true, speed = 4.0, bezier = "snappyOut",  style = "slide" },
    { leaf = "layersOut",        enabled = true, speed = 3.5, bezier = "snappyExit", style = "slide" },
    { leaf = "fadeLayersIn",     enabled = true, speed = 4.0, bezier = "snappyOut" },
    { leaf = "fadeLayersOut",    enabled = true, speed = 3.5, bezier = "snappyExit" },
    { leaf = "workspaces",       enabled = true, speed = 4.0, bezier = "snappyOut",  style = "slide" },
    { leaf = "specialWorkspace", enabled = true, speed = 4.0, bezier = "snappyOut",  style = "slidevert" },
    { leaf = "border",           enabled = true, speed = 8.0, bezier = "snappyOut" },
    { leaf = "borderangle",      enabled = true, speed = 100.0, bezier = "liner", style = "loop" },
  },
}
