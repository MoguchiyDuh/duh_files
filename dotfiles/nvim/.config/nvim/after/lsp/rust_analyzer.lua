-- not mason-managed: rustup component add rust-analyzer
return {
	settings = {
		["rust-analyzer"] = {
			check = { command = "clippy" },
		},
	},
}
