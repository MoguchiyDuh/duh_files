local servers = {
	"lua_ls",
	"basedpyright",
	"rust_analyzer",
	"clangd",
	"ts_ls",
	"html",
	"cssls",
	"taplo",
	"yamlls",
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
			ensure_installed = { "lua_ls", "basedpyright", "clangd", "ts_ls", "html", "cssls", "taplo", "yamlls" },
			automatic_installation = true,
		},
	},

	-- ── mason-tool-installer (formatters + linters) ───────────────────────────
	{
		"WhoIsSethDaniel/mason-tool-installer.nvim",
		dependencies = { "williamboman/mason.nvim" },
		opts = {
			ensure_installed = {
				"stylua", -- lua
				"ruff", -- python format + lint
				"clang-format", -- c/cpp
				"prettier", -- js/ts/json/md
				"taplo", -- toml
				"eslint", -- js/ts lint
				"yamllint", -- yaml lint
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

			-- python: auto-detect uv .venv
			local function get_python_path(workspace)
				local venv = workspace .. "/.venv/bin/python"
				if vim.fn.filereadable(venv) == 1 then
					return venv
				end
				if
					vim.fn.filereadable(workspace .. "/pyproject.toml") == 1
					or vim.fn.filereadable(workspace .. "/uv.lock") == 1
				then
					local obj = vim.system(
						{ "uv", "run", "--directory", workspace, "python", "-c", "import sys; print(sys.executable)" },
						{ text = true }
					):wait()
					if obj.code == 0 and obj.stdout then
						return vim.trim(obj.stdout)
					end
				end
				return vim.fn.exepath("python3") or vim.fn.exepath("python") or "python"
			end

			vim.lsp.config.basedpyright = {
				capabilities = capabilities,
				before_init = function(_, config)
					config.settings = config.settings or {}
					config.settings.python = config.settings.python or {}
					config.settings.python.pythonPath = get_python_path(config.root_dir or vim.fn.getcwd())
				end,
				settings = {
					basedpyright = {
						analysis = {
							autoSearchPaths = true,
							useLibraryCodeForTypes = true,
							diagnosticMode = "openFilesOnly",
							typeCheckingMode = "basic",
						},
					},
				},
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
