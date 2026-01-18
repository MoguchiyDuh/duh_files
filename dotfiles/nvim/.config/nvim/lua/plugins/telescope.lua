local status_ok, telescope = pcall(require, "telescope")
if not status_ok then
	return
end

telescope.setup({
	defaults = {
		layout_config = {
			horizontal = { width = 0.9 },
		},
		file_ignore_patterns = { "node_modules", ".git" },
	},
	extensions = {
		fzf = {
			fuzzy = true,
			override_generic_sorter = true,
			override_file_sorter = true,
		},
	},
})

require("telescope").load_extension("fzf")
