return {
	settings = {
		Lua = {
			diagnostics = { globals = { "vim" } },
			workspace = {
				checkThirdParty = false,
				-- workaround for lua_ls 3.17 first-buffer library bug (folke/lazydev#136)
				library = { vim.env.VIMRUNTIME },
			},
			telemetry = { enable = false },
		},
	},
}
