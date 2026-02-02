-- ~/.config/nvim/lua/core/keymaps.lua
local keymap = vim.keymap.set

-- Leader key
vim.g.mapleader = " "

-- ============================================================================
-- Standard keymaps
-- ============================================================================
keymap("n", "<C-s>", ":w!<CR>", { noremap = true, silent = true, desc = "Save file" })
keymap("n", "<C-q>", ":q<CR>", { noremap = true, silent = true, desc = "Quit file" })
keymap("n", "<Esc>", ":noh<CR>", { noremap = true, silent = true, desc = "Clear search highlights" })

-- Window navigation
keymap("n", "<C-h>", "<C-w>h", { desc = "Move to left split" })
keymap("n", "<C-j>", "<C-w>j", { desc = "Move to bottom split" })
keymap("n", "<C-k>", "<C-w>k", { desc = "Move to top split" })
keymap("n", "<C-l>", "<C-w>l", { desc = "Move to right split" })

-- Buffer navigation
keymap("n", "<Tab>", ":bnext<CR>", { desc = "Next buffer" })
keymap("n", "<S-Tab>", ":bprev<CR>", { desc = "Previous buffer" })
keymap("n", "<leader>bd", ":bdelete<CR>", { desc = "Delete buffer" })

-- File tree (Nvim-tree)
keymap("n", "<C-n>", function()
	if vim.fn.exists(":NvimTreeToggle") == 2 then
		vim.cmd("NvimTreeToggle")
	end
end, { desc = "Toggle file tree" })

-- LSP keymaps
keymap("n", "K", vim.lsp.buf.hover, { silent = true, desc = "Show hover documentation" })
keymap("n", "gd", vim.lsp.buf.definition, { silent = true, desc = "Go to definition" })
keymap("n", "gr", vim.lsp.buf.references, { silent = true, desc = "Show references" })
keymap("n", "<leader>e", vim.diagnostic.open_float, { silent = true, desc = "Show diagnostics" })
keymap("n", "<leader>rn", vim.lsp.buf.rename, { silent = true, desc = "Rename symbol" })

-- Formatting
keymap("n", "<leader>F", function()
	local ok, conform = pcall(require, "conform")
	if ok then
		conform.format({ async = true, lsp_fallback = true })
	end
end, { desc = "Format buffer" })
