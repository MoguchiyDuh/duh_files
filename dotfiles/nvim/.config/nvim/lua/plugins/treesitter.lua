local status_ok, treesitter = pcall(require, "nvim-treesitter.configs")
if not status_ok then
	return
end

treesitter.setup({
	ensure_installed = {
		"c",
		"cpp",
		"lua",
		"vim",
		"vimdoc",
		"query",
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
