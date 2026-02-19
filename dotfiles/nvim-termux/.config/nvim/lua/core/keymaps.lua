-- ~/.config/nvim/lua/core/keymaps.lua
local keymap = vim.keymap.set

-- Leader key
vim.g.mapleader = " "

-- ============================================================================
-- Standard keymaps
-- ============================================================================
-- Save/Quit
keymap("n", "<C-s>", ":w<CR>", { noremap = true, silent = true, desc = "Save file" })
keymap("n", "<C-q>", ":q<CR>", { noremap = true, silent = true, desc = "Quit file" })
keymap("n", "<leader>w", ":w<CR>", { noremap = true, silent = true, desc = "Save file" })
keymap("n", "<leader>W", ":w!<CR>", { noremap = true, silent = true, desc = "Force save file" })
keymap("n", "<leader>q", ":q<CR>", { noremap = true, silent = true, desc = "Quit file" })
keymap("n", "<leader>Q", ":qa!<CR>", { noremap = true, silent = true, desc = "Force quit all" })

-- Clear search highlights
keymap("n", "<Esc>", ":noh<CR>", { noremap = true, silent = true, desc = "Clear search highlights" })

-- ============================================================================
-- Window/Split management
-- ============================================================================
-- Navigate between splits
keymap("n", "<C-h>", "<C-w>h", { noremap = true, silent = true, desc = "Move to left split" })
keymap("n", "<C-j>", "<C-w>j", { noremap = true, silent = true, desc = "Move to split below" })
keymap("n", "<C-k>", "<C-w>k", { noremap = true, silent = true, desc = "Move to split above" })
keymap("n", "<C-l>", "<C-w>l", { noremap = true, silent = true, desc = "Move to right split" })

-- Split management
keymap("n", "<leader>sv", ":vsplit<CR>", { noremap = true, silent = true, desc = "Vertical split" })
keymap("n", "<leader>sx", ":split<CR>", { noremap = true, silent = true, desc = "Horizontal split" })
keymap("n", "<leader>se", "<C-w>=", { noremap = true, silent = true, desc = "Make splits equal size" })

-- ============================================================================
-- Better editing
-- ============================================================================
-- Move lines up/down
keymap("n", "<A-j>", ":m .+1<CR>==", { noremap = true, silent = true, desc = "Move line down" })
keymap("n", "<A-k>", ":m .-2<CR>==", { noremap = true, silent = true, desc = "Move line up" })
keymap("v", "<A-j>", ":m '>+1<CR>gv=gv", { noremap = true, silent = true, desc = "Move selection down" })
keymap("v", "<A-k>", ":m '<-2<CR>gv=gv", { noremap = true, silent = true, desc = "Move selection up" })

-- Stay in visual mode when indenting
keymap("v", "<", "<gv", { noremap = true, silent = true, desc = "Indent left" })
keymap("v", ">", ">gv", { noremap = true, silent = true, desc = "Indent right" })

-- ============================================================================
-- Terminal
-- ============================================================================
keymap("n", "<C-t>", ":terminal<CR>", { noremap = true, silent = true, desc = "Open terminal" })

-- ============================================================================
-- Buffer navigation
-- ============================================================================
-- Smart buffer close (avoid jumping to nvim-tree)
local function smart_close_buffer(force)
	local current = vim.api.nvim_get_current_buf()
	local buffers = vim.fn.getbufinfo({ buflisted = 1 })

	local valid_buffers = {}
	for _, buf in ipairs(buffers) do
		if buf.bufnr ~= current and buf.name ~= "" and not buf.name:match("NvimTree") then
			table.insert(valid_buffers, buf.bufnr)
		end
	end

	if #valid_buffers > 0 then
		vim.cmd("buffer " .. valid_buffers[1])
	else
		vim.cmd("enew")
	end

	local cmd = force and "bdelete!" or "bdelete"
	vim.cmd(cmd .. " " .. current)
end

keymap("n", "<leader>bn", ":bnext<CR>", { noremap = true, silent = true, desc = "Next buffer" })
keymap("n", "<leader>bp", ":bprevious<CR>", { noremap = true, silent = true, desc = "Previous buffer" })
keymap("n", "<leader>bd", function()
	smart_close_buffer(false)
end, { noremap = true, silent = true, desc = "Close buffer" })
keymap("n", "<leader>bD", function()
	smart_close_buffer(true)
end, { noremap = true, silent = true, desc = "Force close buffer" })
keymap("n", "<Tab>", ":bnext<CR>", { noremap = true, silent = true, desc = "Next buffer" })
keymap("n", "<S-Tab>", ":bprevious<CR>", { noremap = true, silent = true, desc = "Previous buffer" })

-- ============================================================================
-- File tree (Nvim-tree)
-- ============================================================================
keymap("n", "<C-n>", function()
	if vim.fn.exists(":NvimTreeToggle") == 2 then
		vim.cmd("NvimTreeToggle")
	end
end, { desc = "Toggle file tree" })

-- ============================================================================
-- LSP keymaps
-- ============================================================================
keymap("n", "K", vim.lsp.buf.hover, { silent = true, desc = "Show hover documentation" })
keymap("n", "gd", vim.lsp.buf.definition, { silent = true, desc = "Go to definition" })
keymap("n", "gD", vim.lsp.buf.declaration, { silent = true, desc = "Go to declaration" })
keymap("n", "gi", vim.lsp.buf.implementation, { silent = true, desc = "Go to implementation" })
keymap("n", "gt", vim.lsp.buf.type_definition, { silent = true, desc = "Go to type definition" })
keymap("n", "gr", vim.lsp.buf.references, { silent = true, desc = "Show references" })
keymap("n", "<leader>ca", vim.lsp.buf.code_action, { silent = true, desc = "Code actions" })
keymap("n", "<leader>rn", vim.lsp.buf.rename, { silent = true, desc = "Rename symbol" })
keymap("n", "<leader>e", vim.diagnostic.open_float, { silent = true, desc = "Show diagnostics" })
keymap("n", "[d", vim.diagnostic.goto_prev, { silent = true, desc = "Previous diagnostic" })
keymap("n", "]d", vim.diagnostic.goto_next, { silent = true, desc = "Next diagnostic" })
keymap("i", "<C-k>", vim.lsp.buf.signature_help, { silent = true, desc = "Signature help" })

-- ============================================================================
-- Git - Gitsigns
-- ============================================================================
local gs_ok, gs = pcall(require, "gitsigns")
if gs_ok then
	keymap("n", "<leader>gd", gs.preview_hunk, { desc = "Preview hunk diff" })
	keymap("n", "<leader>gD", gs.diffthis, { desc = "Diff split" })
	keymap("n", "<leader>gb", gs.blame_line, { desc = "Blame line" })
	keymap("n", "]h", gs.next_hunk, { desc = "Next hunk" })
	keymap("n", "[h", gs.prev_hunk, { desc = "Previous hunk" })
	keymap("n", "<leader>gs", gs.stage_hunk, { desc = "Stage hunk" })
	keymap("n", "<leader>gu", gs.undo_stage_hunk, { desc = "Undo stage hunk" })
	keymap("n", "<leader>gr", gs.reset_hunk, { desc = "Reset hunk" })
end

-- ============================================================================
-- Formatting (Conform)
-- ============================================================================
keymap("n", "<leader>F", function()
	local ok, conform = pcall(require, "conform")
	if ok then
		conform.format({ async = true, lsp_fallback = true })
	else
		vim.notify("Conform not found", vim.log.levels.WARN)
	end
end, { desc = "Format buffer" })
