vim.g.mapleader = " "
vim.g.maplocalleader = "\\"

-- disable netrw (using oil.nvim)
vim.g.loaded_netrw = 1
vim.g.loaded_netrwPlugin = 1

local opt = vim.opt

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
opt.signcolumn = "yes"
opt.cursorline = true
opt.splitright = true
opt.splitbelow = true
opt.showmode = false -- lualine shows it

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

vim.api.nvim_create_autocmd({ "FocusGained", "BufEnter" }, { command = "checktime" })
vim.lsp.log.set_level("ERROR")
