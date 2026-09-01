return {
  curves = {
    { name = "exprIn",    cfg = { type = "bezier", points = { { 0.38, 1.21 }, { 0.22, 1.0  } } } },
    { name = "exprDecel", cfg = { type = "bezier", points = { { 0.05, 0.7  }, { 0.1,  1.0  } } } },
    { name = "exprAccel", cfg = { type = "bezier", points = { { 0.3,  0.0  }, { 0.8,  0.15 } } } },
    { name = "exprStall", cfg = { type = "bezier", points = { { 1.0, -0.1  }, { 0.7,  0.85 } } } },
    { name = "liner",     cfg = { type = "bezier", points = { { 0,   0     }, { 1,    1.0  } } } },
  },
  animations = {
    { leaf = "windowsIn",        enabled = true, speed = 4.0, bezier = "exprIn",    style = "popin 80%" },
    { leaf = "windowsOut",       enabled = true, speed = 2.5, bezier = "exprDecel", style = "popin 90%" },
    { leaf = "windowsMove",      enabled = true, speed = 4.0, bezier = "exprDecel" },
    { leaf = "fadeIn",           enabled = true, speed = 3.0, bezier = "exprDecel" },
    { leaf = "fadeOut",          enabled = true, speed = 2.5, bezier = "exprDecel" },
    { leaf = "layersIn",         enabled = true, speed = 2.7, bezier = "exprDecel", style = "popin 93%" },
    { leaf = "layersOut",        enabled = true, speed = 2.4, bezier = "exprAccel", style = "popin 94%" },
    { leaf = "fadeLayersIn",     enabled = true, speed = 0.5, bezier = "exprDecel" },
    { leaf = "fadeLayersOut",    enabled = true, speed = 2.7, bezier = "exprStall" },
    { leaf = "workspaces",       enabled = true, speed = 7.0, bezier = "exprDecel", style = "slide" },
    { leaf = "specialWorkspace", enabled = true, speed = 3.5, bezier = "exprDecel", style = "slidevert" },
    { leaf = "border",           enabled = true, speed = 10,  bezier = "exprDecel" },
    { leaf = "borderangle",      enabled = true, speed = 100.0, bezier = "liner", style = "loop" },
  },
}
