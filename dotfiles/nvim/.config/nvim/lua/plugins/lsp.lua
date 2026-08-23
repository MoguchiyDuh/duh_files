return {
	-- ── completion (blink.cmp) ────────────────────────────────────────────────
	{
		"Saghen/blink.cmp",
		version = "*",
		event = "InsertEnter",
		dependencies = { "rafamadriz/friendly-snippets" },
		opts_extend = { "sources.default" },
		opts = {
			snippets = { preset = "default" },
			keymap = {
				preset = "default",
				["<Tab>"] = { "select_next", "snippet_forward", "fallback" },
				["<S-Tab>"] = { "select_prev", "snippet_backward", "fallback" },
				["<CR>"] = { "accept", "fallback" },
				["<C-e>"] = { "cancel" },
				["<C-b>"] = { "scroll_documentation_up", "fallback" },
				["<C-f>"] = { "scroll_documentation_down", "fallback" },
			},
			appearance = { nerd_font_variant = "mono" },
			sources = {
				default = { "lsp", "path", "snippets", "buffer" },
			},
			completion = {
				documentation = { auto_show = true, auto_show_delay_ms = 200 },
			},
			signature = { enabled = true },
		},
	},

	-- ── mason ─────────────────────────────────────────────────────────────────
	{
		"williamboman/mason.nvim",
		cmd = "Mason",
		build = ":MasonUpdate",
		opts = {
			ui = {
				border = "rounded",
				icons = { package_installed = "✓", package_pending = "➜", package_uninstalled = "✗" },
			},
		},
	},

	-- ── mason-lspconfig: install servers only; wiring is native vim.lsp.enable
	{
		"williamboman/mason-lspconfig.nvim",
		dependencies = { "williamboman/mason.nvim" },
		opts = {
			ensure_installed = {
				"lua_ls",
				"clangd",
				"taplo",
				"yamlls",
				"marksman",
				"bashls",
				"gopls",
			},
			-- rust_analyzer (rustup) and ty (uv) are not mason-managed
			-- ruff is enabled manually with custom config below
		},
	},

	-- ── mason-tool-installer (formatters + linters) ───────────────────────────
	{
		"WhoIsSethDaniel/mason-tool-installer.nvim",
		dependencies = { "williamboman/mason.nvim" },
		opts = {
			ensure_installed = {
				"shfmt",        -- sh formatter
				"stylua",       -- lua formatter
				"ruff",         -- python formatter + linter
				"clang-format", -- c/cpp formatter
				"prettier",     -- js/ts/json/jsonc/md/yaml formatter
				"taplo",        -- toml formatter
				"eslint",       -- js/ts linter
				"yamllint",     -- yaml linter
			},
			auto_update = true,
			run_on_start = true,
		},
	},

	-- ── lazydev: proper lua_ls workspace + vim.uv types for nvim config ────────
	{
		"folke/lazydev.nvim",
		ft = "lua",
		opts = {
			library = {
				{ path = "${3rd}/luv/library", words = { "vim%.uv" } },
			},
		},
	},

	-- ── lsp wiring (native 0.12 API) ──────────────────────────────────────────
	-- per-server overrides live in after/lsp/*.lua (higher priority than the
	-- nvim-lspconfig lsp/*.lua defaults on runtimepath).
	{
		"neovim/nvim-lspconfig",
		lazy = false,
		dependencies = {
			"williamboman/mason-lspconfig.nvim",
			"b0o/SchemaStore.nvim",
			"Saghen/blink.cmp",
		},
		config = function()
			vim.lsp.config("*", {
				capabilities = require("blink.cmp").get_lsp_capabilities(),
			})

			vim.lsp.enable({
				"lua_ls",
				"clangd",
				"taplo",
				"yamlls",
				"marksman",
				"bashls",
				"gopls",
				"rust_analyzer",
				"ty",
				"ruff",
			})
		end,
	},
}
