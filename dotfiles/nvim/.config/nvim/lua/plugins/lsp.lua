local servers = {
	"lua_ls",
	"rust_analyzer",
	"clangd",
	"taplo",
	"yamlls",
	"marksman",
	"bashls",
	"gopls",
}

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
			-- rust_analyzer excluded: managed by rustup
			-- basedpyright excluded: replaced by ty (installed via uv tool)
			ensure_installed = {
				"lua_ls", "clangd", "taplo", "yamlls", "marksman", "bashls", "gopls",
			},
			automatic_installation = { exclude = { "basedpyright", "rust_analyzer" } },
		},
	},

	-- ── mason-tool-installer (formatters + linters) ───────────────────────────
	{
		"WhoIsSethDaniel/mason-tool-installer.nvim",
		dependencies = { "williamboman/mason.nvim" },
		config = function()
			require("mason-tool-installer").setup({
				ensure_installed = {
					"shfmt",        -- sh/bash/zsh formatter
					"shellcheck",   -- sh/bash/zsh lint (used by bashls internally)
					"stylua",       -- lua formatter
					"ruff",         -- python formatter + linter
					"clang-format", -- c/cpp formatter
					"dprint",       -- md/json/jsonc/yaml formatter
					"goimports",    -- go import formatter
					"gofumpt",      -- go strict formatter
					"yamllint",     -- yaml linter
				},
				auto_update = true,
				run_on_start = true,
			})

			-- after dprint is installed/updated, refresh global plugin versions once
			vim.api.nvim_create_autocmd("User", {
				pattern = "MasonToolsUpdateCompleted",
				once = true,
				callback = function(e)
					local installed = e.data or {}
					for _, pkg in ipairs(installed) do
						if pkg == "dprint" then
							vim.system(
								{ "dprint", "config", "update", "--global" },
								{ text = true },
								function(obj)
									if obj.code ~= 0 then
										vim.schedule(function()
											vim.notify("dprint config update failed:\n" .. (obj.stderr or ""), vim.log.levels.WARN)
										end)
									end
								end
							)
							break
						end
					end
				end,
			})
		end,
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

			-- default capabilities for all servers
			for _, server in ipairs(servers) do
				vim.lsp.config(server, { capabilities = capabilities })
			end

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

			-- ── ty (python LSP) ───────────────────────────────────────────────
			-- NOTE: PEP 723 script env resolution is not supported by ty LSP yet
			-- (astral-sh/ty#691, milestone ty-1.1). ty does not implement
			-- workspace/didChangeConfiguration or per-file server isolation.
			vim.lsp.config("ty", {
				capabilities = capabilities,
				settings = {
					ty = {
						diagnosticMode = "openFilesOnly",
					},
				},
			})
			vim.lsp.enable("ty")

			-- rust-analyzer: use clippy instead of cargo check
			vim.lsp.config.rust_analyzer = {
				capabilities = capabilities,
				settings = {
					["rust-analyzer"] = {
						check = { command = "clippy" },
					},
				},
			}

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

			for _, server in ipairs(servers) do
				vim.lsp.enable(server)
			end
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
