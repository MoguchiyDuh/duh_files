return {
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

	-- ── mason-lspconfig ───────────────────────────────────────────────────────
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
			-- dprint excluded: used as formatter via conform, not as LSP
			-- rust_analyzer and ty are not mason-managed; enabled manually below
			-- dprint: formatter only via conform, not an LSP
			-- ruff: configured manually below (custom on_attach to disable hoverProvider)
			automatic_enable = { exclude = { "dprint", "ruff" } },
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

	-- ── lspconfig ─────────────────────────────────────────────────────────────
	{
		"neovim/nvim-lspconfig",
		dependencies = {
			"williamboman/mason-lspconfig.nvim",
			"b0o/SchemaStore.nvim",
			"Saghen/blink.cmp",
		},
		config = function()
			local capabilities = require("blink.cmp").get_lsp_capabilities()

			-- lua
			vim.lsp.config.lua_ls = {
				capabilities = capabilities,
				settings = { Lua = { diagnostics = { globals = { "vim" } } } },
			}

			-- yaml + SchemaStore
			vim.lsp.config.yamlls = {
				capabilities = capabilities,
				settings = {
					yaml = {
						schemaStore = { enable = false, url = "" },
						schemas = require("schemastore").yaml.schemas(),
					},
				},
			}

			-- rust-analyzer: use clippy instead of cargo check
			vim.lsp.config.rust_analyzer = {
				capabilities = capabilities,
				settings = {
					["rust-analyzer"] = {
						check = { command = "clippy" },
					},
				},
			}
			vim.lsp.enable("rust_analyzer")

			-- ── ty (python type-checker LSP) ─────────────────────────────────
			-- NOTE: PEP 723 script env resolution not supported yet (astral-sh/ty#691).
			-- ty does not implement workspace/didChangeConfiguration or per-file isolation.
			-- ty handles: types, completions, nav, inlay hints.
			-- ruff server (below) handles: lint diagnostics + code actions.
			vim.lsp.config.ty = {
				capabilities = capabilities,
				settings = {
					ty = { diagnosticMode = "openFilesOnly" },
				},
			}
			vim.lsp.enable("ty")

			-- ── ruff server (python lint + code actions) ──────────────────────
			-- Secondary Python LSP alongside ty. Provides: real-time lint diagnostics,
			-- quick-fix code actions, organize-imports, fix-all, noqa hover.
			-- Formatting is still handled by conform.nvim (ruff_format).
			-- Disable hover so ty's hover takes precedence.
			vim.lsp.config.ruff = {
				capabilities = capabilities,
				on_attach = function(client)
					client.server_capabilities.hoverProvider = true
				end,
			}
			vim.lsp.enable("ruff")

			-- gopls: gofumpt formatting + full staticcheck suite
			vim.lsp.config.gopls = {
				capabilities = capabilities,
				settings = {
					gopls = {
						gofumpt = true,
						staticcheck = true,
						analyses = {
							unusedparams = true,
							shadow = true,
						},
					},
				},
			}

			-- bashls: shellcheck invoked automatically when on PATH
			vim.lsp.config.bashls = {
				capabilities = capabilities,
				filetypes = { "sh", "bash", "zsh" },
			}

			-- clangd
			vim.lsp.config.clangd = {
				capabilities = capabilities,
				cmd = { "clangd", "--background-index", "--offset-encoding=utf-16" },
				root_markers = { ".clangd", ".git", "compile_commands.json", "CMakeLists.txt", "Makefile" },
			}
		end,
	},

	-- ── completion ────────────────────────────────────────────────────────────
	{
		"Saghen/blink.cmp",
		version = "*",
		event = "InsertEnter",
		opts = {
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
}
