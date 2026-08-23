-- not mason-managed: uv tool install ty@latest
-- PEP 723 script env resolution not supported yet (astral-sh/ty#691)
return {
	settings = {
		ty = { diagnosticMode = "openFilesOnly" },
	},
}
