-- nvim/lua/plugins/llm.lua
-- Refactored for qwen2.5-coder:1.5b with dynamic host detection

local status_ok, llm = pcall(require, "llm")
if not status_ok then
	return
end

local utils = require("core.utils")

llm.setup({
	backend = "ollama",
	model = "qwen2.5-coder:1.5b",
	url = "http://" .. utils.get_ollama_host() .. ":11434/api/generate",
	request_body = {
		raw = true,
		options = {
			num_predict = 64,
			temperature = 0,
			stop = { "<|endoftext|>", "<|file_separator|>", "<|endof_word|>", "<|end|>" },
		},
	},
	fim = {
		enabled = true,
		prefix = "<|fim_prefix|>",
		middle = "<|fim_middle|>",
		suffix = "<|fim_suffix|>",
	},
	enable_suggestions_on_startup = true,
	lsp = {
		bin_path = vim.fn.stdpath("data") .. "/mason/bin/llm-ls",
	},
})
