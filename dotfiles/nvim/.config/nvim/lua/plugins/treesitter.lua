local status_ok, treesitter = pcall(require, "nvim-treesitter.configs")
if not status_ok then
	return
end

treesitter.setup({
	-- Exclude parsers bundled with nvim 0.12: lua, c, vim, vimdoc, query
	ensure_installed = {
		"cpp",
		"markdown",
		"markdown_inline",
		"python",
		"rust",
		"yaml",
		"bash",
		"json",
		"toml",
		"regex",
		"diff",
		"git_config",
		"gitcommit",
		"gitignore",
	},
	highlight = { enable = true },
	indent = { enable = true },
})
