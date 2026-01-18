local status_ok, gen = pcall(require, "gen")
if not status_ok then
	return
end

local utils = require("core.utils")
local host = utils.get_ollama_host()

gen.setup({
	model = "mistral:7b",
	host = host,
	port = "11434",
	display_mode = "float",
	show_model = true,
	show_prompt = true,
	no_auto_close = false,
	command = function(options)
		local body = vim.deepcopy(options)

		for k, v in pairs(body) do
			if type(v) == "function" then
				body[k] = nil
			end
		end

		return string.format(
			"curl --silent --no-buffer -X POST http://%s:%s/api/generate -d %s",
			options.host,
			options.port,
			vim.fn.shellescape(vim.fn.json_encode(body))
		)
	end,
	debug = false,
})

local custom_prompts = {
	Complete_Code = {
		prompt = "Complete this code. Only output the code without markdown formatting or explanation:\n\n$text",
		replace = true,
	},
	Explain_Code = {
		prompt = "Explain the following code:\n\n$text",
		replace = false,
	},
	Fix_Code = {
		prompt = "Fix any bugs in the following code. Only output the corrected code without markdown formatting or explanation:\n\n$text",
		replace = true,
	},
	Optimize_Code = {
		prompt = "Optimize the following code for better performance. Only output the optimized code without markdown formatting or explanation:\n\n$text",
		replace = true,
	},
	Add_Comments = {
		prompt = "Add brief, clear comments to this code. Only output the code with comments, without markdown formatting or explanation:\n\n$text",
		replace = true,
	},
}

for name, config in pairs(custom_prompts) do
	gen.prompts[name] = config
end
