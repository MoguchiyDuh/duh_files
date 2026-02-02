local status_ok, conform = pcall(require, "conform")
if not status_ok then
	return
end

-- Define formatters for specific file types
conform.setup({
	formatters_by_ft = {
		javascript = { "prettier" },
		typescript = { "prettier" },
		lua = { "stylua" },
		python = { "ruff_format", "ruff_organize_imports" },
		rust = { "rustfmt" },
		cpp = { "clang-format" },
		c = { "clang-format" },
		html = { "prettier" },
		css = { "prettier" },
		markdown = { "prettier" },
		json = { "prettier" },
		jsonc = { "prettier" },
		yaml = { "prettier" },
		toml = { "taplo" },
	},
	format_on_save = {
		timeout_ms = 1500,
		lsp_fallback = true,
	},
})
