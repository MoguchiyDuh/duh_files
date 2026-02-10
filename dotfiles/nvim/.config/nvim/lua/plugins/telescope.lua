local status_ok, telescope = pcall(require, "telescope")
if not status_ok then
	return
end

local actions = require("telescope.actions")

telescope.setup({
	defaults = {
		layout_config = {
			horizontal = { width = 0.9 },
		},
		file_ignore_patterns = { "node_modules", ".git" },
		mappings = {
			i = {
				["<C-d>"] = actions.delete_buffer,
			},
			n = {
				["dd"] = actions.delete_buffer,
			},
		},
	},
	pickers = {
		buffers = {
			sort_mru = true,
			sort_lastused = true,
			previewer = true,
			mappings = {
				i = {
					["<C-d>"] = actions.delete_buffer,
				},
				n = {
					["dd"] = actions.delete_buffer,
				},
			},
		},
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
