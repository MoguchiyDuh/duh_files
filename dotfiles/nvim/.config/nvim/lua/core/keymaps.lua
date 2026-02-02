-- ~/.config/nvim/lua/core/keymaps.lua
local keymap = vim.keymap.set
local opts = { noremap = true, silent = true }

-- Leader key
vim.g.mapleader = " "

-- ============================================================================
-- Standard keymaps
-- ============================================================================
-- Save/Quit
keymap("n", "<leader>w", ":w<CR>", { noremap = true, silent = true, desc = "Save file" })
keymap("n", "<leader>W", ":w!<CR>", { noremap = true, silent = true, desc = "Force save file" })
keymap("n", "<leader>q", ":q<CR>", { noremap = true, silent = true, desc = "Quit file" })
keymap("n", "<leader>Q", ":q!<CR>", { noremap = true, silent = true, desc = "Force quit file" })

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
keymap("n", "<leader>sh", ":split<CR>", { noremap = true, silent = true, desc = "Horizontal split" })
keymap("n", "<leader>sx", ":close<CR>", { noremap = true, silent = true, desc = "Close split" })
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
keymap("t", "<Esc>", "<C-\\><C-n>", { noremap = true, silent = true, desc = "Exit terminal mode" })

-- ============================================================================
-- Buffer navigation
-- ============================================================================
-- Smart buffer close (avoid jumping to nvim-tree)
local function smart_close_buffer(force)
	local current = vim.api.nvim_get_current_buf()
	local buffers = vim.fn.getbufinfo({ buflisted = 1 })

	-- Filter out current buffer and special buffers
	local valid_buffers = {}
	for _, buf in ipairs(buffers) do
		if buf.bufnr ~= current and buf.name ~= "" and not buf.name:match("NvimTree") then
			table.insert(valid_buffers, buf.bufnr)
		end
	end

	-- Switch to next valid buffer before closing, or create new empty buffer
	if #valid_buffers > 0 then
		vim.cmd("buffer " .. valid_buffers[1])
	else
		vim.cmd("enew")
	end

	-- Close the original buffer
	local cmd = force and "bdelete!" or "bdelete"
	vim.cmd(cmd .. " " .. current)
end

keymap("n", "<leader>bn", ":bnext<CR>", { noremap = true, silent = true, desc = "Next buffer" })
keymap("n", "<leader>bp", ":bprevious<CR>", { noremap = true, silent = true, desc = "Previous buffer" })
keymap("n", "<leader>bd", function() smart_close_buffer(false) end, { noremap = true, silent = true, desc = "Close buffer" })
keymap("n", "<leader>bD", function() smart_close_buffer(true) end, { noremap = true, silent = true, desc = "Force close buffer" })
keymap("n", "<Tab>", ":bnext<CR>", { noremap = true, silent = true, desc = "Next buffer" })
keymap("n", "<S-Tab>", ":bprevious<CR>", { noremap = true, silent = true, desc = "Previous buffer" })

-- Jump to buffer by number
for i = 1, 9 do
	keymap("n", "<leader>" .. i, ":BufferLineGoToBuffer " .. i .. "<CR>", {
		noremap = true,
		silent = true,
		desc = "Go to buffer " .. i,
	})
end

-- ============================================================================
-- LSP keymaps
-- ============================================================================
keymap("n", "K", vim.lsp.buf.hover, { silent = true, desc = "Show hover documentation" })
keymap("n", "gd", vim.lsp.buf.definition, { silent = true, desc = "Go to definition" })
keymap("n", "gD", vim.lsp.buf.declaration, { silent = true, desc = "Go to declaration" })
keymap("n", "gi", vim.lsp.buf.implementation, { silent = true, desc = "Go to implementation" })
keymap("n", "gt", vim.lsp.buf.type_definition, { silent = true, desc = "Go to type definition" })
keymap("n", "<leader>ca", vim.lsp.buf.code_action, { silent = true, desc = "Code actions" })
keymap("n", "<leader>rn", vim.lsp.buf.rename, { silent = true, desc = "Rename symbol" })
keymap("n", "<leader>e", vim.diagnostic.open_float, { silent = true, desc = "Show diagnostics" })
keymap("n", "[d", vim.diagnostic.goto_prev, { silent = true, desc = "Previous diagnostic" })
keymap("n", "]d", vim.diagnostic.goto_next, { silent = true, desc = "Next diagnostic" })
keymap("i", "<C-k>", vim.lsp.buf.signature_help, { silent = true, desc = "Signature help" })

-- ============================================================================
-- Telescope
-- ============================================================================
local ts_ok, ts = pcall(require, "telescope.builtin")
if ts_ok then
	keymap("n", "<leader>ff", ts.find_files, { desc = "Find files" })
	keymap("n", "<leader>fg", ts.git_files, { desc = "Find git files" })
	keymap("n", "<leader>fs", function()
		ts.grep_string({ search = vim.fn.input("Grep > ") })
	end, { desc = "Live grep search" })
	keymap("n", "<leader>fb", ts.buffers, { desc = "Find buffers" })
	keymap("n", "gr", ts.lsp_references, { desc = "Show references" })
end

-- ============================================================================
-- Flash (navigation)
-- ============================================================================
local flash_ok, flash = pcall(require, "flash")
if flash_ok then
	-- Don't map in operator-pending mode to avoid conflicts with nvim-surround
	keymap({ "n", "x" }, "s", function()
		flash.jump()
	end, { desc = "Flash jump" })
	keymap({ "n", "x" }, "S", function()
		flash.treesitter()
	end, { desc = "Flash treesitter" })
	-- Alternative binding for operator-pending
	keymap("o", "z", function()
		flash.jump()
	end, { desc = "Flash jump (operator mode)" })
end

-- ============================================================================
-- Git - Lazygit
-- ============================================================================
keymap("n", "<leader>gg", ":LazyGit<CR>", { noremap = true, silent = true, desc = "Open LazyGit" })

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

-- ============================================================================
-- File tree (Nvim-tree)
-- ============================================================================
keymap("n", "<C-n>", function()
	if vim.fn.exists(":NvimTreeToggle") == 2 then
		vim.cmd("NvimTreeToggle")
	end
end, { desc = "Toggle file tree" })

-- ============================================================================
-- AI - CodeCompanion
-- ============================================================================
local function codecompanion_cmd(cmd)
	return function()
		if vim.fn.exists(":CodeCompanionChat") == 2 or vim.fn.exists(":CodeCompanionActions") == 2 then
			vim.cmd(cmd)
		else
			vim.notify("CodeCompanion not loaded", vim.log.levels.WARN)
		end
	end
end

-- Chat
keymap(
	{ "n", "v" },
	"<leader>cc",
	codecompanion_cmd("CodeCompanionChat Toggle"),
	{ desc = "CodeCompanion: Toggle chat" }
)
keymap({ "n", "v" }, "<leader>ca", codecompanion_cmd("CodeCompanionActions"), { desc = "CodeCompanion: Actions" })
keymap("v", "ga", codecompanion_cmd("CodeCompanionChat Add"), { desc = "CodeCompanion: Add to chat" })

-- Inline (gen.nvim style)
keymap("v", "<leader>cf", codecompanion_cmd("CodeCompanion /fix_inline"), { desc = "CodeCompanion: Fix code" })
keymap(
	"v",
	"<leader>co",
	codecompanion_cmd("CodeCompanion /optimize_inline"),
	{ desc = "CodeCompanion: Optimize code" }
)
keymap(
	"v",
	"<leader>cp",
	codecompanion_cmd("CodeCompanion /complete_inline"),
	{ desc = "CodeCompanion: Complete code" }
)
