local status_ok, onedark = pcall(require, "onedark")
if not status_ok then
	return
end

onedark.setup({
	transparent = true,
	colors = {},
	highlights = {},
	code_style = {
		comments = "italic",
		keywords = "none",
		functions = "none",
		strings = "none",
		variables = "none",
	},
	lualine = {
		transparent = true,
	},
})
require("onedark").load()
