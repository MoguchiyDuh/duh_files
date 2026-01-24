-- nvim/lua/plugins/codecompanion.lua
local status_ok, codecompanion = pcall(require, "codecompanion")
if not status_ok then
	return
end

local utils = require("core.utils")

codecompanion.setup({
	adapters = {
		http = {
			ollama = function()
				return require("codecompanion.adapters").extend("ollama", {
					env = {
						url = "http://" .. utils.get_ollama_host() .. ":11434",
					},
					schema = {
						model = {
							default = "qwen3:latest",
						},
					},
				})
			end,
		},
	},
	strategies = {
		chat = {
			adapter = "ollama",
		},
		inline = {
			adapter = "ollama",
		},
	},
	prompt_library = {
		markdown = {
			dirs = {
				vim.fn.stdpath("config") .. "/codecompanion/actions",
			},
		},
	},
	display = {
		chat = {
			window = {
				layout = "vertical",
				position = "right",
			},
		},
	},
})
