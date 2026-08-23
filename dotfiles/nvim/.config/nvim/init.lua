-- leader keys must exist before plugins load
vim.g.mapleader = " "
vim.g.maplocalleader = "\\"

-- unused providers
vim.g.loaded_perl_provider = 0
vim.g.loaded_ruby_provider = 0

require("config.options")
require("config.lazy")
