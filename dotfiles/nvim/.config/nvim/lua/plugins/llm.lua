local status_ok, llm = pcall(require, "llm")
if not status_ok then
	return
end

local utils = require("core.utils")
local home = os.getenv("HOME")
local llm_ls_path = home .. "/.local/share/nvim/mason/bin/llm-ls"

llm.setup({
	backend = "ollama",
	model = "qwen2.5-coder:1.5b",
	url = "http://" .. utils.get_ollama_host() .. ":11434/api/generate",
	request_body = {
		-- Ensure raw mode is enabled if using llm-ls to prevent Ollama from wrapping in chat templates
		raw = true,
		options = {
			num_predict = 64, -- Increased for better code blocks
			temperature = 0, -- Set to 0 for deterministic code generation
			stop = { "<|endoftext|>", "<|file_separator|>", "<|endof_word|>", "<|end|>" },
		},
	},
	fim = {
		enabled = true,
		prefix = "<|fim_prefix|>",
		middle = "<|fim_middle|>",
		suffix = "<|fim_suffix|>",
	},
	-- Ensure the LSP is actually triggered
	enable_suggestions_on_startup = true,
	lsp = {
		bin_path = llm_ls_path,
	},
})
