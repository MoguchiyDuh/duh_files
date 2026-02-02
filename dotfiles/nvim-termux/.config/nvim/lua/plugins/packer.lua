-- ~/.config/nvim/lua/plugins/packer.lua (Termux lightweight version)
local ensure_packer = function()
	local fn = vim.fn
	local install_path = fn.stdpath("data") .. "/site/pack/packer/start/packer.nvim"
	if fn.empty(fn.glob(install_path)) > 0 then
		fn.system({ "git", "clone", "--depth", "1", "https://github.com/wbthomason/packer.nvim", install_path })
		vim.cmd([[packadd packer.nvim]])
		return true
	end
	return false
end

local packer_bootstrap = ensure_packer()

vim.cmd([[packadd packer.nvim]])

return require("packer").startup(function(use)
	use("wbthomason/packer.nvim")

	-- UI
	use("navarasu/onedark.nvim")
	use({ "nvim-lualine/lualine.nvim", requires = "nvim-tree/nvim-web-devicons" })
	use({ "nvim-tree/nvim-tree.lua", requires = "nvim-tree/nvim-web-devicons" })
	use({
		"goolord/alpha-nvim",
		requires = { "nvim-tree/nvim-web-devicons" },
	})

	-- LSP (no Mason - use system-installed servers)
	use("neovim/nvim-lspconfig")

	-- Completion
	use("hrsh7th/nvim-cmp")
	use("hrsh7th/cmp-nvim-lsp")
	use("hrsh7th/cmp-buffer")
	use("hrsh7th/cmp-path")
	use("hrsh7th/cmp-nvim-lua")
	use("saadparwaiz1/cmp_luasnip")

	-- Snippets
	use("L3MON4D3/LuaSnip")
	use("rafamadriz/friendly-snippets")

	-- Formatting
	use("stevearc/conform.nvim")

	-- Utilities (lightweight)
	use({
		"numToStr/Comment.nvim",
		config = function()
			require("Comment").setup()
		end,
	})
	use({
		"windwp/nvim-autopairs",
		event = "InsertEnter",
		config = function()
			require("nvim-autopairs").setup({})
		end,
	})
	use({ "lewis6991/gitsigns.nvim", requires = "nvim-lua/plenary.nvim" })
	use({
		"folke/which-key.nvim",
		config = function()
			require("which-key").setup()
		end,
	})

	if packer_bootstrap then
		require("packer").sync()
	end
end)
