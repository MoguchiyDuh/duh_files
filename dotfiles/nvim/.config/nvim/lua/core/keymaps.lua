local map = vim.keymap.set

-- ── save / quit ───────────────────────────────────────────────────────────────
map("n", "<C-s>", "<cmd>w<cr>", { desc = "Save" })
map("n", "<C-q>", "<cmd>q<cr>", { desc = "Quit" })
map("n", "<leader>w", "<cmd>w<cr>", { desc = "Save" })
map("n", "<leader>q", "<cmd>q<cr>", { desc = "Quit" })
map("n", "<leader>Q", "<cmd>qa!<cr>", { desc = "Force quit all" })

-- ── clear search highlight ────────────────────────────────────────────────────
map("n", "<Esc>", "<cmd>noh<cr>", { desc = "Clear highlights" })

-- ── splits ───────────────────────────────────────────────────────────────────
map("n", "<C-h>", "<C-w>h", { desc = "Move to left split" })
map("n", "<C-j>", "<C-w>j", { desc = "Move to split below" })
map("n", "<C-k>", "<C-w>k", { desc = "Move to split above" })
map("n", "<C-l>", "<C-w>l", { desc = "Move to right split" })
map("n", "<leader>sv", "<cmd>vsplit<cr>", { desc = "Vertical split" })
map("n", "<leader>ss", "<cmd>split<cr>", { desc = "Horizontal split" })
map("n", "<leader>se", "<C-w>=", { desc = "Equal splits" })

-- ── move lines ───────────────────────────────────────────────────────────────
map("n", "<A-j>", "<cmd>m .+1<cr>==", { desc = "Move line down" })
map("n", "<A-k>", "<cmd>m .-2<cr>==", { desc = "Move line up" })
map("v", "<A-j>", ":m '>+1<cr>gv=gv", { desc = "Move selection down" })
map("v", "<A-k>", ":m '<-2<cr>gv=gv", { desc = "Move selection up" })

-- ── indent keep selection ─────────────────────────────────────────────────────
map("v", "<", "<gv", { desc = "Indent left" })
map("v", ">", ">gv", { desc = "Indent right" })

-- ── buffers ───────────────────────────────────────────────────────────────────
map("n", "<S-h>", "<cmd>bprevious<cr>", { desc = "Prev buffer" })
map("n", "<S-l>", "<cmd>bnext<cr>", { desc = "Next buffer" })
map("n", "<leader>bd", function()
	local cur = vim.api.nvim_get_current_buf()
	local listed = vim.fn.getbufinfo({ buflisted = 1 })
	local others = vim.tbl_filter(function(b)
		return b.bufnr ~= cur and b.name ~= "" and not b.name:match("NvimTree")
	end, listed)
	if #others > 0 then
		vim.cmd("buffer " .. others[1].bufnr)
	else
		vim.cmd("enew")
	end
	vim.cmd("bdelete " .. cur)
end, { desc = "Close buffer" })

-- jump to buffer by ordinal (bufferline)
for i = 1, 9 do
	map("n", "<leader>" .. i, "<cmd>BufferLineGoToBuffer " .. i .. "<cr>", { desc = "Buffer " .. i })
end

-- ── lsp ───────────────────────────────────────────────────────────────────────
map("n", "K", vim.lsp.buf.hover, { desc = "Hover docs" })
map("n", "gd", vim.lsp.buf.definition, { desc = "Go to definition" })
map("n", "gD", vim.lsp.buf.declaration, { desc = "Go to declaration" })
map("n", "gi", vim.lsp.buf.implementation, { desc = "Go to implementation" })
map("n", "gy", vim.lsp.buf.type_definition, { desc = "Go to type definition" })
map("n", "<leader>ca", vim.lsp.buf.code_action, { desc = "Code action" })
map("n", "<leader>rn", vim.lsp.buf.rename, { desc = "Rename" })
map("n", "<leader>e", vim.diagnostic.open_float, { desc = "Show diagnostic" })
map("n", "[d", function() vim.diagnostic.jump({ count = -1 }) end, { desc = "Prev diagnostic" })
map("n", "]d", function() vim.diagnostic.jump({ count = 1 }) end, { desc = "Next diagnostic" })
map("i", "<C-k>", vim.lsp.buf.signature_help, { desc = "Signature help" })

-- ── git ───────────────────────────────────────────────────────────────────────
map("n", "<leader>gg", "<cmd>LazyGit<cr>", { desc = "LazyGit" })

-- ── format ───────────────────────────────────────────────────────────────────
map("n", "<leader>F", function()
	require("conform").format({ async = true, lsp_format = "fallback" })
end, { desc = "Format buffer" })

-- ── terminal ─────────────────────────────────────────────────────────────────
map("n", "<leader>t", "<cmd>terminal<cr>", { desc = "Terminal" })
