-- ~/.config/nvim/lua/core/keymaps.lua
local keymap = vim.keymap.set
local opts = { noremap = true, silent = true }

-- Leader key
vim.g.mapleader = " "

-- ============================================================================
-- Standard keymaps
-- ============================================================================
keymap("n", "<C-s>", ":w!<CR>", { noremap = true, silent = true, desc = "Save file" })
keymap("n", "<C-q>", ":q<CR>", { noremap = true, silent = true, desc = "Quit file" })
keymap("n", "<Esc>", ":noh<CR>", { noremap = true, silent = true, desc = "Clear search highlights" })

-- ============================================================================
-- LSP keymaps
-- ============================================================================
keymap("n", "K", vim.lsp.buf.hover, { silent = true, desc = "Show hover documentation" })
keymap("n", "gd", vim.lsp.buf.definition, { silent = true, desc = "Go to definition" })
keymap("n", "<leader>e", vim.diagnostic.open_float, { silent = true, desc = "Show diagnostics" })

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
