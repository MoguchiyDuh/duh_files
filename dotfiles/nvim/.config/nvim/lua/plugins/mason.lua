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
	"jsonls", -- JSON
	"yamlls", -- YAML
	"taplo", -- TOML
}

require("mason-lspconfig").setup({
	ensure_installed = SERVERS,
	automatic_installation = true,
})

require("mason-tool-installer").setup({
	ensure_installed = {
		-- "llm-ls", -- Unused
		-- Formatters
		"stylua",
		"ruff", -- Python formatter + linter (replaces black, isort, flake8)
		"clang-format",
		"prettier",
		"taplo", -- TOML formatter

		-- Linters
		"eslint",
		"jsonlint",
		"yamllint",
	},
	auto_update = true,
	run_on_start = true,
})
