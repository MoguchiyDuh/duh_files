-- nvim/lua/plugins/gen.lua
-- Refactored for qwen3:latest with dynamic host detection

local status_ok, gen = pcall(require, "gen")
if not status_ok then
	return
end

local utils = require("core.utils")

gen.setup({
	model = "qwen3:latest",
	host = utils.get_ollama_host(),
	port = "11434",
	display_mode = "float",
	show_model = true,
	show_prompt = true,
	no_auto_close = false,
	command = function(options)
		local body = vim.deepcopy(options)

		-- Remove Lua functions from body
		for k, v in pairs(body) do
			if type(v) == "function" then
				body[k] = nil
			end
		end

		return string.format(
			"curl --silent --no-buffer -X POST http://%s:%s/api/chat -d %s",
			options.host,
			options.port,
			vim.fn.shellescape(vim.fn.json_encode(body))
		)
	end,
	debug = false,
})

-- Common AI prompts
gen.prompts["Complete_Code"] = {
	prompt = "Complete this code. Only output the code without markdown formatting or explanation:\n\n$text",
	replace = true,
}
gen.prompts["Explain_Code"] = {
	prompt = "Explain the following code:\n\n$text",
	replace = false,
}
gen.prompts["Fix_Code"] = {
	prompt = "Fix any bugs in the following code. Only output the corrected code without markdown formatting or explanation:\n\n$text",
	replace = true,
}
gen.prompts["Optimize_Code"] = {
	prompt = "Optimize the following code for better performance. Only output the optimized code without markdown formatting or explanation:\n\n$text",
	replace = true,
}
