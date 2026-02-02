local status_ok, conform = pcall(require, "conform")
if not status_ok then
	return
end

conform.setup({
	formatters_by_ft = {
		-- lua: stylua doesn't compile on Termux, use LSP formatting
		python = { "black", "isort" },
		rust = { "rustfmt" },
		json = { "prettier" },
		jsonc = { "prettier" },
		-- toml: taplo doesn't compile on Termux, use LSP formatting
	},
	format_on_save = {
		timeout_ms = 500,
		lsp_fallback = true,
	},
})
