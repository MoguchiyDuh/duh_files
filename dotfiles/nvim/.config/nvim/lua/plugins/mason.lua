local status_ok, mason = pcall(require, "mason")
if not status_ok then
	return
end

mason.setup({
	ui = {
		icons = {
			package_installed = "✓",
			package_pending = "➜",
			package_uninstalled = "✗",
		},
	},
})

SERVERS = {
	"lua_ls", -- Lua
	"pyright", -- Python
	"gopls", -- Go
	"rust_analyzer", -- Rust
	"clangd", -- C/C++
	"html", -- HTML
	"cssls", -- CSS
	"ts_ls", -- TypeScripts / JavaScript
}

require("mason-lspconfig").setup({
	ensure_installed = SERVERS,
	automatic_installation = true,
})

require("mason-tool-installer").setup({
	ensure_installed = {
		"llm-ls",
		-- Formatters
		"stylua",
		"black",
		"isort",
		"clang-format",

		-- Linters
		"flake8",
		"eslint",
	},
	auto_update = true,
	run_on_start = true,
})
