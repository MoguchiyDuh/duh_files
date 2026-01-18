local status_ok, cmp_nvim_lsp = pcall(require, "cmp_nvim_lsp")
if not status_ok then
	return
end

local capabilities = cmp_nvim_lsp.default_capabilities()

for _, lsp in ipairs(SERVERS) do -- SERVERS from mason.lua
	vim.lsp.config(lsp, {
		capabilities = capabilities,
	})
end

-- Lua LSP specific settings
vim.lsp.config.lua_ls = {
	capabilities = capabilities,
	settings = {
		Lua = {
			diagnostics = {
				globals = { "vim" },
			},
		},
	},
}

-- Pyright settings to auto-detect uv's .venv
local function get_python_path(workspace)
	-- 1. Check for .venv in the current project root
	local venv_path = workspace .. "/.venv/bin/python"
	if vim.fn.filereadable(venv_path) == 1 then
		return venv_path
	end

	-- 2. Check if this is a UV project (pyproject.toml or uv.lock exists)
	local has_pyproject = vim.fn.filereadable(workspace .. "/pyproject.toml") == 1
	local has_uv_lock = vim.fn.filereadable(workspace .. "/uv.lock") == 1

	if has_pyproject or has_uv_lock then
		-- Try to get UV's python for this project
		local cmd = { "uv", "run", "--directory", workspace, "python", "-c", "import sys; print(sys.executable)" }
		local obj = vim.system(cmd, { text = true }):wait()
		if obj.code == 0 and obj.stdout then
			return vim.trim(obj.stdout)
		end
	end

	-- 3. Handle PEP 723 inline script metadata
	local bufname = vim.api.nvim_buf_get_name(0)
	local first_line = vim.api.nvim_buf_get_lines(0, 0, 1, false)[1] or ""
	if first_line:match("^# /// script") or first_line:match("^#!.*uv run") then
		local cmd = { "uv", "run", "--script", bufname, "python", "-c", "import sys; print(sys.executable)" }
		local obj = vim.system(cmd, { text = true }):wait()
		if obj.code == 0 and obj.stdout then
			return vim.trim(obj.stdout)
		end
	end

	-- 4. Fallback to system python (or whatever is in PATH)
	return vim.fn.exepath("python3") or vim.fn.exepath("python") or "python"
end

vim.lsp.config.pyright = {
	capabilities = capabilities,
	before_init = function(_, config)
		-- This dynamically sets the python path per-project based on the project root
		config.settings.python.pythonPath = get_python_path(config.root_dir or vim.fn.getcwd())
	end,
	settings = {
		python = {
			analysis = {
				autoSearchPaths = true,
				useLibraryCodeForTypes = true,
				diagnosticMode = "openFilesOnly", -- "workspace" can be heavy on big uv projects
				typeCheckingMode = "basic", -- Change to "strict" if you want aggressive typing
			},
		},
	},
}

-- Clangd
vim.lsp.config.clangd = {
	capabilities = capabilities,
	cmd = { "clangd", "--background-index" },
	root_markers = {
		".clangd",
		".clang-tidy",
		".git",
		"compile_commands.json",
		"compile_flags.txt",
		"CMakeLists.txt", -- Add this if using CMake
		"Makefile", -- Add this if using Make
	},
}

-- Enable configured LSP servers
for _, lsp in ipairs(SERVERS) do
	vim.lsp.enable(lsp)
end
