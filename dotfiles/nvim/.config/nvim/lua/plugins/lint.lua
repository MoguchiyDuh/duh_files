local status_ok, lint = pcall(require, "lint")
if not status_ok then
	return
end

lint.linters_by_ft = {
	javascript = { "eslint" },
	typescript = { "eslint" },
	python = { "flake8" },
}

vim.api.nvim_create_autocmd({ "BufWritePost", "BufReadPost", "InsertLeave" }, {
	callback = function()
		require("lint").try_lint()
	end,
})
