vim.cmd("hi clear")
if vim.fn.exists("syntax_on") == 1 then vim.cmd("syntax reset") end
vim.g.colors_name = "dynamic"
vim.o.background = "dark"
vim.o.termguicolors = true

local c = {
  bg     = "{{ colors.surface.default.hex }}",
  fg     = "{{ colors.on_surface.default.hex }}",
  cursor = "{{ colors.primary.default.hex }}",
  c0     = "{{ colors.surface_container_highest.default.hex }}",
  c1     = "{{ colors.error.default.hex }}",
  c2     = "{{ colors.tertiary.default.hex }}",
  c3     = "{{ colors.secondary.default.hex }}",
  c4     = "{{ colors.primary.default.hex }}",
  c5     = "{{ colors.primary_fixed.default.hex }}",
  c6     = "{{ colors.tertiary_fixed.default.hex }}",
  c7     = "{{ colors.on_surface.default.hex }}",
  c8     = "{{ colors.surface_variant.default.hex }}",
  c9     = "{{ colors.primary_container.default.hex }}",
  c10    = "{{ colors.tertiary_container.default.hex }}",
  c11    = "{{ colors.secondary_container.default.hex }}",
  c12    = "{{ colors.primary.default.hex }}",
  c13    = "{{ colors.tertiary.default.hex }}",
  c14    = "{{ colors.secondary.default.hex }}",
  c15    = "{{ colors.on_surface_variant.default.hex }}",
}

local function hi(group, opts)
  vim.api.nvim_set_hl(0, group, opts)
end

hi("Normal",          { fg = c.fg,  bg = c.bg })
hi("NormalNC",        { fg = c.fg,  bg = c.bg })
hi("NormalFloat",     { fg = c.fg,  bg = c.c0 })
hi("FloatBorder",     { fg = c.c8,  bg = c.c0 })
hi("FloatTitle",      { fg = c.c7,  bg = c.c0, bold = true })

hi("StatusLine",      { fg = c.c15, bg = c.c0 })
hi("StatusLineNC",    { fg = c.c8,  bg = c.c0 })
hi("WinSeparator",    { fg = c.c8 })
hi("VertSplit",       { fg = c.c8 })

hi("LineNr",          { fg = c.c8 })
hi("LineNrAbove",     { fg = c.c8 })
hi("LineNrBelow",     { fg = c.c8 })
hi("CursorLine",      { bg = c.c0 })
hi("CursorLineNr",    { fg = c.c15, bold = true })
hi("SignColumn",      { fg = c.c8,  bg = c.bg })
hi("ColorColumn",     { bg = c.c0 })
hi("EndOfBuffer",     { fg = c.c8 })

hi("Pmenu",           { fg = c.fg,  bg = c.c0 })
hi("PmenuSel",        { fg = c.bg,  bg = c.c4,  bold = true })
hi("PmenuSbar",       { bg = c.c0 })
hi("PmenuThumb",      { bg = c.c8 })

hi("TabLine",         { fg = c.c8,  bg = c.c0 })
hi("TabLineSel",      { fg = c.bg,  bg = c.c4,  bold = true })
hi("TabLineFill",     { bg = c.c0 })

hi("Search",          { fg = c.bg,  bg = c.c14 })
hi("IncSearch",       { fg = c.bg,  bg = c.c4,  bold = true })
hi("CurSearch",       { fg = c.bg,  bg = c.c4,  bold = true })
hi("Substitute",      { fg = c.bg,  bg = c.c1 })

hi("Visual",          { bg = c.c11 })
hi("VisualNOS",       { bg = c.c11 })

hi("MatchParen",      { fg = c.c6,  bold = true, underline = true })
hi("Folded",          { fg = c.c8,  bg = c.c0,  italic = true })
hi("FoldColumn",      { fg = c.c8,  bg = c.bg })
hi("Conceal",         { fg = c.c8 })

hi("Directory",       { fg = c.c4 })
hi("Title",           { fg = c.c5,  bold = true })
hi("Question",        { fg = c.c2 })
hi("MoreMsg",         { fg = c.c4 })
hi("ModeMsg",         { fg = c.fg,  bold = true })
hi("ErrorMsg",        { fg = c.c1,  bold = true })
hi("WarningMsg",      { fg = c.c3 })
hi("SpellBad",        { undercurl = true, sp = c.c1 })
hi("SpellCap",        { undercurl = true, sp = c.c4 })
hi("SpellRare",       { undercurl = true, sp = c.c2 })
hi("SpellLocal",      { undercurl = true, sp = c.c6 })
hi("NonText",         { fg = c.c8 })
hi("SpecialKey",      { fg = c.c8 })
hi("Whitespace",      { fg = c.c8 })

hi("DiffAdd",         { fg = c.c6,  bg = c.c0 })
hi("DiffChange",      { fg = c.c3,  bg = c.c0 })
hi("DiffDelete",      { fg = c.c1,  bg = c.c0 })
hi("DiffText",        { fg = c.c5,  bg = c.c0,  bold = true })

hi("Comment",         { fg = c.c8,  italic = true })
hi("Constant",        { fg = c.c9 })
hi("String",          { fg = c.c2 })
hi("Character",       { fg = c.c2 })
hi("Number",          { fg = c.c6 })
hi("Boolean",         { fg = c.c5 })
hi("Float",           { fg = c.c6 })
hi("Identifier",      { fg = c.fg })
hi("Function",        { fg = c.c4 })
hi("Statement",       { fg = c.c5 })
hi("Conditional",     { fg = c.c5 })
hi("Repeat",          { fg = c.c5 })
hi("Label",           { fg = c.c5 })
hi("Operator",        { fg = c.c6 })
hi("Keyword",         { fg = c.c5,  bold = true })
hi("Exception",       { fg = c.c1 })
hi("PreProc",         { fg = c.c13 })
hi("Include",         { fg = c.c13 })
hi("Define",          { fg = c.c13 })
hi("Macro",           { fg = c.c13 })
hi("PreCondit",       { fg = c.c13 })
hi("Type",            { fg = c.c3 })
hi("StorageClass",    { fg = c.c3 })
hi("Structure",       { fg = c.c3 })
hi("Typedef",         { fg = c.c14 })
hi("Special",         { fg = c.c6 })
hi("SpecialChar",     { fg = c.c6 })
hi("Tag",             { fg = c.c4 })
hi("Delimiter",       { fg = c.c15 })
hi("SpecialComment",  { fg = c.c8,  italic = true })
hi("Debug",           { fg = c.c1 })
hi("Underlined",      { underline = true })
hi("Error",           { fg = c.c1,  bold = true })
hi("Todo",            { fg = c.c3,  bold = true })

hi("DiagnosticError",            { fg = c.c1 })
hi("DiagnosticWarn",             { fg = c.c3 })
hi("DiagnosticInfo",             { fg = c.c4 })
hi("DiagnosticHint",             { fg = c.c2 })
hi("DiagnosticOk",               { fg = c.c6 })
hi("DiagnosticUnderlineError",   { undercurl = true, sp = c.c1 })
hi("DiagnosticUnderlineWarn",    { undercurl = true, sp = c.c3 })
hi("DiagnosticUnderlineInfo",    { undercurl = true, sp = c.c4 })
hi("DiagnosticUnderlineHint",    { undercurl = true, sp = c.c2 })
hi("DiagnosticVirtualTextError", { fg = c.c1,  italic = true })
hi("DiagnosticVirtualTextWarn",  { fg = c.c3,  italic = true })
hi("DiagnosticVirtualTextInfo",  { fg = c.c4,  italic = true })
hi("DiagnosticVirtualTextHint",  { fg = c.c2,  italic = true })

hi("LspReferenceText",  { bg = c.c0 })
hi("LspReferenceRead",  { bg = c.c0 })
hi("LspReferenceWrite", { bg = c.c0,  bold = true })
hi("LspSignatureActiveParameter", { fg = c.c5, bold = true })
