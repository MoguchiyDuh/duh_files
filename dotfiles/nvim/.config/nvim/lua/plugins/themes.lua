-- theme/variant/transparency selector
--   <leader>ct  pick theme -> variant
--   <leader>cv  pick variant for current theme
--   <leader>cb  toggle transparency

return {
	{ "folke/tokyonight.nvim", lazy = true },
	{ "catppuccin/nvim", lazy = true, name = "catppuccin" },
	{ "navarasu/onedark.nvim", lazy = true },
	{ "rose-pine/neovim", lazy = true, name = "rose-pine" },
	{ "sainnhe/gruvbox-material", lazy = true },
	{ "EdenEast/nightfox.nvim", lazy = true },
	{ "sainnhe/everforest", lazy = true },

	{
		"rebelot/kanagawa.nvim",
		lazy = false,
		priority = 1000,
		config = function()
			local light_variants = {
				["tokyonight-day"] = true,
				["catppuccin-latte"] = true,
				["onedark-light"] = true,
				["rose-pine-dawn"] = true,
				["dayfox"] = true,
				["dawnfox"] = true,
				["kanagawa-lotus"] = true,
				["everforest-light"] = true,
			}
			local is_light = function(v) return v and light_variants[v] == true end
			local strip = function(s) return (s or ""):gsub("%s+%[.+%]", "") end

			local function warn_if_light(v)
				if is_light(v) then
					vim.notify(
						"LIGHT THEME - use <leader>ct or <leader>cv to switch back",
						vim.log.levels.WARN,
						{ title = "LIGHT THEME ACTIVE", timeout = 8000 }
					)
				end
			end

			local function snacks_layout(n)
				return {
					layout = {
						config = function(layout)
							for _, box in ipairs(layout.layout) do
								if box.win == "list" and not box.height then
									box.height = math.floor(math.max(math.min(n, vim.o.lines * 0.8 - 10), 2))
								end
							end
						end,
					},
				}
			end

			local themes = {
			dynamic = {
				variants = { "dynamic" },
				load = function(_)
					vim.o.background = "dark"
					vim.cmd("colorscheme dynamic")
				end,
			},
				kanagawa = {
					variants = { "kanagawa-wave", "kanagawa-dragon", "kanagawa-lotus [LIGHT]" },
					load = function(variant)
						local v = strip(variant) ~= "" and strip(variant) or "kanagawa-wave"
						require("kanagawa").setup({ compile = false, terminalColors = true })
						vim.o.background = is_light(v) and "light" or "dark"
						vim.cmd("colorscheme " .. v)
						warn_if_light(v)
					end,
				},
				tokyonight = {
					variants = { "tokyonight-night", "tokyonight-storm", "tokyonight-moon", "tokyonight-day [LIGHT]" },
					load = function(variant)
						local v = strip(variant) ~= "" and strip(variant) or "tokyonight-night"
						require("tokyonight").setup({ style = v:gsub("tokyonight%-", "") })
						vim.o.background = is_light(v) and "light" or "dark"
						vim.cmd("colorscheme " .. v)
						warn_if_light(v)
					end,
				},
				catppuccin = {
					variants = { "catppuccin-mocha", "catppuccin-macchiato", "catppuccin-frappe", "catppuccin-latte [LIGHT]" },
					load = function(variant)
						local v = strip(variant) ~= "" and strip(variant) or "catppuccin-mocha"
						require("catppuccin").setup({ flavour = v:gsub("catppuccin%-", "") })
						vim.o.background = is_light(v) and "light" or "dark"
						vim.cmd("colorscheme " .. v)
						warn_if_light(v)
					end,
				},
				onedark = {
					variants = { "dark", "darker", "cool", "deep", "warm", "warmer", "light [LIGHT]" },
					load = function(variant)
						local v = strip(variant) ~= "" and strip(variant) or "dark"
						require("onedark").setup({ style = v })
						vim.o.background = is_light("onedark-" .. v) and "light" or "dark"
						require("onedark").load()
					end,
				},
				["rose-pine"] = {
					variants = { "rose-pine", "rose-pine-moon", "rose-pine-dawn [LIGHT]" },
					load = function(variant)
						local v = strip(variant) ~= "" and strip(variant) or "rose-pine"
						require("rose-pine").setup({})
						vim.o.background = is_light(v) and "light" or "dark"
						vim.cmd("colorscheme " .. v)
						warn_if_light(v)
					end,
				},
				["gruvbox-material"] = {
					variants = { "soft", "medium", "hard" },
					load = function(variant)
						local v = strip(variant) ~= "" and strip(variant) or "medium"
						vim.g.gruvbox_material_background = v
						vim.g.gruvbox_material_better_performance = 1
						vim.o.background = "dark"
						vim.cmd("colorscheme gruvbox-material")
					end,
				},
				nightfox = {
					variants = { "nightfox", "carbonfox", "nordfox", "terafox", "duskfox", "dayfox [LIGHT]", "dawnfox [LIGHT]" },
					load = function(variant)
						local v = strip(variant) ~= "" and strip(variant) or "nightfox"
						require("nightfox").setup({})
						vim.o.background = is_light(v) and "light" or "dark"
						vim.cmd("colorscheme " .. v)
						warn_if_light(v)
					end,
				},
				everforest = {
					variants = { "soft", "medium", "hard" },
					load = function(variant)
						local v = strip(variant) ~= "" and strip(variant) or "medium"
						vim.g.everforest_background = v
						vim.g.everforest_better_performance = 1
						vim.o.background = "dark"
						vim.cmd("colorscheme everforest")
					end,
				},
			}

			local state_file = vim.fn.stdpath("data") .. "/theme_state.json"
			local transparent = false

			local function save_state(theme, transp, variant)
				local f = io.open(state_file, "w")
				if f then
					f:write(vim.json.encode({ theme = theme, transparent = transp, variant = variant }))
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

			local transparent_groups = {
				"Normal", "NormalNC", "NormalFloat", "SignColumn", "StatusLine", "StatusLineNC",
				"EndOfBuffer", "CursorLine", "CursorLineNr", "LineNr", "LineNrAbove", "LineNrBelow",
				"WinSeparator", "VertSplit", "SnacksNormal", "SnacksNormalNC", "SnacksWinBar",
				"SnacksWinBarNC", "SnacksPickerPickWin", "SnacksPickerPickWinCurrent",
			}

			local function apply_transparent()
				for _, g in ipairs(transparent_groups) do
					vim.api.nvim_set_hl(0, g, { bg = "none" })
				end
			end

			vim.api.nvim_create_autocmd("ColorScheme", {
				callback = function()
					if transparent then
						apply_transparent()
					end
				end,
			})

			local function apply_theme(name, variant)
				local t = themes[name]
				if not t then
					return
				end
				vim.o.background = "dark"
				t.load(variant)
				save_state(name, transparent, variant)
			end

			local function confirm_light(variant, on_confirm)
				local v = strip(variant)
				if not is_light(v) then
					on_confirm()
					return
				end
				Snacks.picker.select(
					{ "Yes, I know what I'm doing", "No, go back" },
					{ prompt = "LIGHT THEME - are you sure?", snacks = snacks_layout(2) },
					function(choice)
						if choice and choice:sub(1, 3) == "Yes" then
							on_confirm()
						end
					end
				)
			end

			local function pick_variant(name, on_done)
				local t = themes[name]
				if not t or #t.variants <= 1 then
					on_done(nil)
					return
				end
				Snacks.picker.select(
					t.variants,
					{ prompt = "Variant", snacks = snacks_layout(#t.variants) },
					function(v)
						if not v then
							return
						end
						confirm_light(v, function()
							on_done(v)
						end)
					end
				)
			end

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
			end, { desc = "Toggle transparency" })

			vim.keymap.set("n", "<leader>ct", function()
				local names = vim.tbl_keys(themes)
				table.sort(names)
				Snacks.picker.select(names, { prompt = "Theme", snacks = snacks_layout(#names) }, function(choice)
					if not choice then
						return
					end
					pick_variant(choice, function(variant)
						apply_theme(choice, variant)
					end)
				end)
			end, { desc = "Switch theme" })

			vim.keymap.set("n", "<leader>cv", function()
				local current = vim.g.colors_name or ""
				local name = current
				for key in pairs(themes) do
					if current:find(key, 1, true) then
						name = key
						break
					end
				end
				pick_variant(name, function(variant)
					if variant then
						apply_theme(name, variant)
					end
				end)
			end, { desc = "Switch variant" })

			local state = load_state()
			local boot_theme = (state and state.theme) or "kanagawa"
			local boot_variant = state and state.variant
			apply_theme(themes[boot_theme] and boot_theme or "kanagawa", boot_variant)
			if state and state.transparent then
				transparent = true
				apply_transparent()
			end
		end,
	},
}
