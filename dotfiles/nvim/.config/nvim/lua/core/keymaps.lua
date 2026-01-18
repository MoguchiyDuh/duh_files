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
-- AI - Gen.nvim (Manual prompt-based generation)
-- ============================================================================
local function gen_cmd(cmd)
	return function()
		if vim.fn.exists(":Gen") == 2 then
			vim.cmd("Gen " .. (cmd or ""))
		else
			vim.notify("Gen.nvim not loaded", vim.log.levels.ERROR)
		end
	end
end

keymap({ "n", "v" }, "<leader>]", gen_cmd(), { desc = "Gen: Open menu" })
keymap({ "n", "v" }, "<leader>gc", gen_cmd("Complete_Code"), { desc = "Gen: Complete code" })
keymap({ "n", "v" }, "<leader>ge", gen_cmd("Explain_Code"), { desc = "Gen: Explain code" })
keymap({ "n", "v" }, "<leader>gf", gen_cmd("Fix_Code"), { desc = "Gen: Fix code" })
keymap({ "n", "v" }, "<leader>go", gen_cmd("Optimize_Code"), { desc = "Gen: Optimize code" })

-- ============================================================================
-- AI - LLM.nvim (Inline completion)
-- ============================================================================
-- Manual trigger
keymap({ "n", "i" }, "<A-l>", "<Cmd>LLMSuggestion<CR>", { desc = "LLM: Trigger completion" })

-- Toggle auto-suggestions on/off
keymap("n", "<leader>la", "<Cmd>LLMToggleAutoSuggest<CR>", { desc = "LLM: Toggle auto-suggest" })
