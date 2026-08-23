local opt = vim.opt

-- disable netrw (using oil.nvim)
vim.g.loaded_netrw = 1
vim.g.loaded_netrwPlugin = 1

-- line numbers
opt.number = true
opt.relativenumber = true

-- indentation
opt.tabstop = 4
opt.shiftwidth = 4
opt.expandtab = true
opt.smartindent = true

-- ui
opt.termguicolors = true
opt.scrolloff = 8
opt.sidescrolloff = 8
opt.signcolumn = "yes"
opt.cursorline = true
opt.splitright = true
opt.splitbelow = true
opt.showmode = false -- lualine shows it
opt.winborder = "rounded" -- nvim 0.12 native float borders
opt.laststatus = 3

-- search
opt.ignorecase = true
opt.smartcase = true
opt.hlsearch = true

-- clipboard
opt.clipboard = "unnamedplus"

-- files
opt.undofile = true
opt.swapfile = false
opt.backup = false
opt.autoread = true

-- performance
opt.updatetime = 200
opt.timeoutlen = 300

-- misc
opt.mouse = "a"
opt.wrap = false
opt.splitkeep = "cursor"

vim.api.nvim_create_autocmd({ "FocusGained", "BufEnter" }, { command = "checktime" })
vim.lsp.log.set_level("ERROR")

-- ── external tool checks (not mason-managed) ──────────────────────────────
vim.api.nvim_create_autocmd("VimEnter", {
	once = true,
	callback = function()
		local missing = {}

		if vim.fn.executable("ty") == 0 then
			missing[#missing + 1] = "ty (Python LSP): uv tool install ty@latest"
		end

		if vim.fn.executable("rust-analyzer") == 0 then
			missing[#missing + 1] = "rust-analyzer: rustup component add rust-analyzer"
		end

		if #missing > 0 then
			vim.schedule(function()
				vim.notify(
					"Install required (not mason-managed):\n  • " .. table.concat(missing, "\n  • "),
					vim.log.levels.WARN,
					{ title = "Missing tools" }
				)
			end)
		end
	end,
})
