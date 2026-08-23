return {
	-- ── snacks (dashboard, picker, notifier, indent, scratch, words) ──────────
	{
		"folke/snacks.nvim",
		priority = 900,
		lazy = false,
		opts = {
			bigfile = { enabled = true },
			quickfile = { enabled = true },
			dashboard = {
				preset = {
					keys = {
						{ icon = " ", key = "f", desc = "Find File", action = ":lua Snacks.picker.files()" },
						{ icon = " ", key = "g", desc = "Live Grep", action = ":lua Snacks.picker.grep()" },
						{ icon = " ", key = "r", desc = "Recent Files", action = ":lua Snacks.picker.recent()" },
						{
							icon = " ",
							key = "c",
							desc = "Config",
							action = ":lua Snacks.picker.files({ cwd = vim.fn.stdpath('config') })",
						},
						{ icon = " ", key = "q", desc = "Quit", action = ":qa" },
					},
				},
			},
			indent = { enabled = true },
			input = { enabled = true },
			notifier = { enabled = true, timeout = 3000 },
			picker = {
				enabled = true,
				sources = {
					buffers = {
						win = {
							input = {
								keys = {
									["<C-d>"] = { "bufdelete", mode = { "n", "i" } },
								},
							},
							list = {
								keys = {
									["<C-d>"] = "bufdelete",
								},
							},
						},
					},
				},
			},
			scope = { enabled = true },
			scroll = { enabled = true },
			statuscolumn = { enabled = true },
			words = { enabled = true },
		},
		keys = {
			{ "<leader>ff", function() Snacks.picker.files() end, desc = "Find files" },
			{ "<leader>fg", function() Snacks.picker.grep() end, desc = "Live grep" },
			{ "<leader>fr", function() Snacks.picker.recent() end, desc = "Recent files" },
			{ "<leader>fb", function() Snacks.picker.buffers() end, desc = "Buffers" },
			{ "<leader>fk", function() Snacks.picker.keymaps() end, desc = "Keymaps" },
			{ "<leader>fp", function() Snacks.picker.commands() end, desc = "Commands" },
			{ "<leader>fd", function() Snacks.picker.diagnostics() end, desc = "Diagnostics" },
			{ "gr", function() Snacks.picker.lsp_references() end, desc = "LSP references" },
			{ "<leader>gd", function() Snacks.picker.lsp_definitions() end, desc = "LSP definitions" },
			{ "<leader>gb", function() Snacks.gitbrowse() end, desc = "Git browse" },
			{ "<leader>N", function() Snacks.notifier.show_history() end, desc = "Notification history" },
			{ "<leader>.", function() Snacks.scratch() end, desc = "Scratch buffer" },
		},
	},

	-- ── trouble ───────────────────────────────────────────────────────────────
	{
		"folke/trouble.nvim",
		cmd = "Trouble",
		opts = {},
		keys = {
			{ "<leader>xx", "<cmd>Trouble diagnostics toggle<cr>", desc = "Diagnostics (Trouble)" },
			{ "<leader>xX", "<cmd>Trouble diagnostics toggle filter.buf=0<cr>", desc = "Buffer diagnostics" },
			{
				"[q",
				function()
					if require("trouble").is_open() then
						require("trouble").prev({ skip_groups = true, jump = true })
					else
						local ok, err = pcall(vim.cmd.cprevious)
						if not ok then vim.notify(err, vim.log.levels.ERROR) end
					end
				end,
				desc = "Previous item",
			},
			{
				"]q",
				function()
					if require("trouble").is_open() then
						require("trouble").next({ skip_groups = true, jump = true })
					else
						local ok, err = pcall(vim.cmd.cnext)
						if not ok then vim.notify(err, vim.log.levels.ERROR) end
					end
				end,
				desc = "Next item",
			},
		},
	},

	-- ── which-key ─────────────────────────────────────────────────────────────
	{ "folke/which-key.nvim", event = "VeryLazy", opts = {} },
}
