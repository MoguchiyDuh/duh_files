return {
	-- ── file manager (edit fs like a buffer) ──────────────────────────────────
	{
		"stevearc/oil.nvim",
		dependencies = { "nvim-tree/nvim-web-devicons" },
		lazy = false,
		opts = {
			default_file_explorer = true,
			view_options = { show_hidden = true },
			float = { padding = 2 },
			keymaps = {
				["<C-s>"] = { "actions.select", opts = { horizontal = true } },
				["<C-v>"] = { "actions.select", opts = { vertical = true } },
				["<C-h>"] = false, -- free for window nav
			},
		},
		keys = {
			{ "<C-n>", "<cmd>Oil<cr>", desc = "Open file explorer" },
		},
	},

	-- ── treesitter ────────────────────────────────────────────────────────────
	-- nvim 0.12+: highlight/indent are built-in, plugin only manages parsers
	{
		"nvim-treesitter/nvim-treesitter",
		build = ":TSUpdate",
		event = { "BufReadPost", "BufNewFile" },
		config = function()
			require("nvim-treesitter").setup()

			-- install parsers
			local parsers = {
				"lua",
				"vim",
				"vimdoc",
				"python",
				"go",
				"rust",
				"c",
				"cpp",
				"javascript",
				"typescript",
				"html",
				"css",
				"json",
				"yaml",
				"toml",
				"markdown",
				"markdown_inline",
				"bash",
				"regex",
				"diff",
				"git_config",
				"gitcommit",
				"gitignore",
			}
			local install = require("nvim-treesitter.install")
			for _, lang in ipairs(parsers) do
				pcall(install.install, lang)
			end

			-- enable highlight + indent via built-in vim.treesitter
			vim.api.nvim_create_autocmd("FileType", {
				callback = function(ev)
					local ok = pcall(vim.treesitter.start, ev.buf)
					if ok then
						vim.bo[ev.buf].indentexpr = "v:lua.require'nvim-treesitter'.indentexpr()"
					end
				end,
			})
		end,
	},

	-- ── git signs ─────────────────────────────────────────────────────────────
	{
		"lewis6991/gitsigns.nvim",
		event = { "BufReadPost", "BufNewFile" },
		opts = {
			signs = {
				add = { text = "+" },
				change = { text = "~" },
				delete = { text = "_" },
				topdelete = { text = "‾" },
				changedelete = { text = "~" },
			},
		},
		keys = {
			{
				"]h",
				function()
					require("gitsigns").next_hunk()
				end,
				desc = "Next hunk",
			},
			{
				"[h",
				function()
					require("gitsigns").prev_hunk()
				end,
				desc = "Prev hunk",
			},
			{
				"<leader>gs",
				function()
					require("gitsigns").stage_hunk()
				end,
				desc = "Stage hunk",
			},
			{
				"<leader>gr",
				function()
					require("gitsigns").reset_hunk()
				end,
				desc = "Reset hunk",
			},
			{
				"<leader>gu",
				function()
					require("gitsigns").undo_stage_hunk()
				end,
				desc = "Undo stage hunk",
			},
			{
				"<leader>gp",
				function()
					require("gitsigns").preview_hunk()
				end,
				desc = "Preview hunk",
			},
			{
				"<leader>gl",
				function()
					require("gitsigns").blame_line()
				end,
				desc = "Blame line",
			},
			{
				"<leader>gD",
				function()
					require("gitsigns").diffthis()
				end,
				desc = "Diff this",
			},
		},
	},

	-- ── lazygit ───────────────────────────────────────────────────────────────
	{
		"kdheepak/lazygit.nvim",
		dependencies = { "nvim-lua/plenary.nvim" },
		cmd = "LazyGit",
	},

	-- ── jump navigation ───────────────────────────────────────────────────────
	{
		"folke/flash.nvim",
		event = "VeryLazy",
		opts = {},
		keys = {
			{
				"<leader>j",
				function()
					require("flash").jump()
				end,
				mode = { "n", "x", "o" },
				desc = "Flash jump",
			},
			{
				"<leader>J",
				function()
					require("flash").treesitter()
				end,
				mode = { "n", "x", "o" },
				desc = "Flash treesitter",
			},
		},
	},

	-- ── surround ──────────────────────────────────────────────────────────────
	{
		"kylechui/nvim-surround",
		event = "VeryLazy",
		opts = {},
	},

	-- ── autopairs ─────────────────────────────────────────────────────────────
	{
		"windwp/nvim-autopairs",
		event = "InsertEnter",
		opts = {},
	},

	-- ── markdown rendering ────────────────────────────────────────────────────
	{
		"MeanderingProgrammer/render-markdown.nvim",
		dependencies = { "nvim-treesitter/nvim-treesitter", "nvim-tree/nvim-web-devicons" },
		ft = { "markdown" },
		opts = {},
	},

	-- ── sudo save ─────────────────────────────────────────────────────────────
	{
		"lambdalisue/suda.vim",
		cmd = { "SudaRead", "SudaWrite" },
		init = function()
			vim.g.suda_smart_edit = 1
		end,
	},
}
