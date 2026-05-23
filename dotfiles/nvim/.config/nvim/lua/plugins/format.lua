return {
	-- ── formatter ─────────────────────────────────────────────────────────────
	{
		"stevearc/conform.nvim",
		event = "BufWritePre",
		opts = {
			formatters_by_ft = {
				lua = { "stylua" },
				python = { "ruff_format", "ruff_organize_imports" },
				rust = { "rustfmt" },
				c = { "clang-format" },
				cpp = { "clang-format" },
				javascript = { "prettier" },
				typescript = { "prettier" },
				json = { "dprint" },
				jsonc = { "dprint" },
				markdown = { "dprint" },
				toml = { "taplo" },
				yaml = { "dprint" },
				sh = { "shfmt" },
			},
			formatters = {
				dprint = {
					-- always use global config so dprint works outside project roots
					args = { "fmt", "--config", vim.fn.expand("~/.config/dprint/dprint.jsonc"), "--stdin", "$FILENAME" },
				},
			},
			format_on_save = {
				timeout_ms = 1500,
				lsp_fallback = true,
			},
		},
	},

	-- ── linter ────────────────────────────────────────────────────────────────
	{
		"mfussenegger/nvim-lint",
		event = { "BufWritePost", "BufReadPost", "InsertLeave" },
		config = function()
			local lint = require("lint")
			lint.linters_by_ft = {
				python = { "ruff" },
				javascript = { "eslint" },
				typescript = { "eslint" },
				yaml = { "yamllint" },
			}
			vim.api.nvim_create_autocmd({ "BufWritePost", "BufReadPost", "InsertLeave" }, {
				callback = function()
					lint.try_lint()
				end,
			})
		end,
	},
}
