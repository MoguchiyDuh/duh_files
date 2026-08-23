-- secondary python LSP alongside ty: lint diagnostics + code actions
-- formatting still handled by conform (ruff_format); disable hover so ty wins
return {
	on_attach = function(client)
		client.server_capabilities.hoverProvider = false
	end,
}
