vim.api.nvim_create_autocmd("TextYankPost", {
	callback = function()
		vim.hl.on_yank()
	end,
})

vim.api.nvim_create_autocmd("Signal", {
	pattern = "SIGUSR1",
	callback = function()
		if vim.g.colors_name == "wallust" then
			dofile(vim.fn.expand("~/.local/share/nvim/site/colors/wallust.lua"))
		end
	end,
})
