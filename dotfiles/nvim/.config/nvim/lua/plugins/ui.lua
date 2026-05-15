return {
	-- ── colorschemes (all installed, one active) ──────────────────────────────
	{ "rebelot/kanagawa.nvim", lazy = true },
	{ "folke/tokyonight.nvim", lazy = true },
	{ "catppuccin/nvim", lazy = true, name = "catppuccin" },
	{ "navarasu/onedark.nvim", lazy = true },
	{ "rose-pine/neovim", lazy = true, name = "rose-pine" },

	-- ── theme loader (active theme + hot-switch) ──────────────────────────────
	{
		"rebelot/kanagawa.nvim", -- drives the initial load; change to swap default
		lazy = false,
		priority = 1000,
		config = function()
			-- ── persist state ─────────────────────────────────────────────────
			local state_file = vim.fn.stdpath("data") .. "/theme_state.json"

			local function save_state(theme, transp)
				local f = io.open(state_file, "w")
				if f then
					f:write(vim.json.encode({ theme = theme, transparent = transp }))
					f:close()
				end
			end

			local function load_state()
				local f = io.open(state_file, "r")
				if not f then
					return nil
				end
				local ok, data = pcall(vim.json.decode, f:read("*a"))
				f:close()
				return ok and data or nil
			end

			-- ── transparency ──────────────────────────────────────────────────
			local transparent = false

			local transparent_groups = {
				"Normal",
				"NormalNC",
				"NormalFloat",
				"SignColumn",
				"StatusLine",
				"StatusLineNC",
				"EndOfBuffer",
				"CursorLine",
				"CursorLineNr",
				"LineNr",
				"LineNrAbove",
				"LineNrBelow",
				"WinSeparator",
				"VertSplit",
			}

			local function apply_transparent()
				for _, g in ipairs(transparent_groups) do
					vim.api.nvim_set_hl(0, g, { bg = "none" })
				end
			end

			-- toggle: <leader>cb
			vim.keymap.set("n", "<leader>cb", function()
				transparent = not transparent
				if transparent then
					apply_transparent()
					vim.notify("Transparency on")
				else
					vim.cmd("colorscheme " .. vim.g.colors_name)
					vim.notify("Transparency off")
				end
				save_state(vim.g.colors_name, transparent)
			end, { desc = "Toggle background transparency" })

			-- per-theme setup (no transparency baked in — toggle controls it)
			local themes = {
				kanagawa = function()
					require("kanagawa").setup({ compile = false, terminalColors = true })
					vim.cmd("colorscheme kanagawa")
				end,
				tokyonight = function()
					require("tokyonight").setup({ style = "night" })
					vim.cmd("colorscheme tokyonight")
				end,
				catppuccin = function()
					require("catppuccin").setup({ flavour = "mocha" })
					vim.cmd("colorscheme catppuccin")
				end,
				onedark = function()
					require("onedark").setup({})
					require("onedark").load()
				end,
				["rose-pine"] = function()
					require("rose-pine").setup({})
					vim.cmd("colorscheme rose-pine")
				end,
			}

			-- re-apply transparency after theme switch if it was enabled
			vim.api.nvim_create_autocmd("ColorScheme", {
				callback = function()
					if transparent then
						apply_transparent()
					end
				end,
			})

			-- hot-switch via snacks picker: <leader>ct
			vim.keymap.set("n", "<leader>ct", function()
				local names = {}
				for name in pairs(themes) do
					table.insert(names, name)
				end
				table.sort(names)
				Snacks.picker.select(names, {
					prompt = "Theme",
					snacks = {
						layout = {
							config = function(layout)
								for _, box in ipairs(layout.layout) do
									if box.win == "list" and not box.height then
										box.height = math.floor(math.max(math.min(#names, vim.o.lines * 0.8 - 10), 2))
									end
								end
							end,
						},
					},
				}, function(choice)
					if choice and themes[choice] then
						themes[choice]()
						save_state(choice, transparent)
					end
				end)
			end, { desc = "Switch colorscheme" })

			-- load saved state or default
			local state = load_state()
			local default_theme = (state and state.theme) or "kanagawa"
			if themes[default_theme] then
				themes[default_theme]()
			else
				themes["kanagawa"]()
			end
			if state and state.transparent then
				transparent = true
				apply_transparent()
			end
		end,
	},

	-- ── snacks (dashboard, notifs, indent, words, picker, etc.) ──────────────
	{
		"folke/snacks.nvim",
		priority = 900,
		lazy = false,
		opts = {
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
			picker = { enabled = true },
			scope = { enabled = true },
			scroll = { enabled = true },
			statuscolumn = { enabled = true },
			words = { enabled = true },
		},
		keys = {
			{
				"<leader>ff",
				function()
					Snacks.picker.files()
				end,
				desc = "Find files",
			},
			{
				"<leader>fg",
				function()
					Snacks.picker.grep()
				end,
				desc = "Live grep",
			},
			{
				"<leader>fr",
				function()
					Snacks.picker.recent()
				end,
				desc = "Recent files",
			},
			{
				"<leader>fb",
				function()
					Snacks.picker.buffers()
				end,
				desc = "Buffers",
			},
			{
				"<leader>fk",
				function()
					Snacks.picker.keymaps()
				end,
				desc = "Keymaps",
			},
			{
				"<leader>fp",
				function()
					Snacks.picker.commands()
				end,
				desc = "Commands",
			},
			{
				"<leader>fd",
				function()
					Snacks.picker.diagnostics()
				end,
				desc = "Diagnostics",
			},
			{
				"gr",
				function()
					Snacks.picker.lsp_references()
				end,
				desc = "LSP references",
			},
			{
				"<leader>gd",
				function()
					Snacks.picker.lsp_definitions()
				end,
				desc = "LSP definitions",
			},
			{
				"<leader>gb",
				function()
					Snacks.gitbrowse()
				end,
				desc = "Git browse",
			},
			{
				"<leader>N",
				function()
					Snacks.notifier.show_history()
				end,
				desc = "Notification history",
			},
			{
				"<leader>.",
				function()
					Snacks.scratch()
				end,
				desc = "Scratch buffer",
			},
		},
	},

	-- ── statusline ────────────────────────────────────────────────────────────
	{
		"nvim-lualine/lualine.nvim",
		dependencies = { "nvim-tree/nvim-web-devicons" },
		event = "VeryLazy",
		opts = {
			options = {
				theme = "auto",
				globalstatus = true,
				component_separators = "",
				section_separators = "",
			},
			sections = {
				lualine_a = { "mode" },
				lualine_b = { "branch", "diff", "diagnostics" },
				lualine_c = { { "filename", path = 1 } },
				lualine_x = { "encoding", "filetype" },
				lualine_y = { "progress" },
				lualine_z = { "location" },
			},
		},
	},

	-- ── buffer tabs ───────────────────────────────────────────────────────────
	{
		"akinsho/bufferline.nvim",
		dependencies = { "nvim-tree/nvim-web-devicons" },
		event = "VeryLazy",
		opts = {
			options = {
				numbers = "ordinal",
				diagnostics = "nvim_lsp",
				diagnostics_indicator = function(count, level)
					local icon = level:match("error") and " " or " "
					return " " .. icon .. count
				end,
				separator_style = "thin",
				always_show_bufferline = true,
				offsets = {
					{ filetype = "OilNvim", text = "File Explorer", text_align = "center", separator = true },
				},
			},
		},
	},

	-- ── which-key ─────────────────────────────────────────────────────────────
	{
		"folke/which-key.nvim",
		event = "VeryLazy",
		opts = {},
	},
}
