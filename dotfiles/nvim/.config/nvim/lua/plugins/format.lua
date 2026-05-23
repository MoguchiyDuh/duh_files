return {
	-- ── formatter ─────────────────────────────────────────────────────────────
	{
		"stevearc/conform.nvim",
		event = "BufWritePre",
		opts = {
			formatters_by_ft = {
				lua        = { "stylua" },
				python     = { "ruff_format", "ruff_organize_imports" },
				rust       = { "rustfmt" },
				c          = { "clang-format" },
				cpp        = { "clang-format" },
				javascript = { "prettier" },
				typescript = { "prettier" },
				json       = { "prettier" },
				jsonc      = { "prettier" },
				markdown   = { "prettier" },
				toml       = { "taplo" },
				yaml       = { "prettier" },
				sh         = { "shfmt" },
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
