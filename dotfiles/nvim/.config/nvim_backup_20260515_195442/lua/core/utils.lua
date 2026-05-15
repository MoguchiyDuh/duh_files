-- ~/.config/nvim/lua/core/utils.lua
local M = {}

--- Check if running in WSL
---@return boolean
function M.is_wsl()
	return vim.fn.filereadable("/proc/sys/fs/binfmt_misc/WSLInterop") == 1
end

--- Get WSL host IP address (Windows host from WSL2)
---@return string IP address or fallback
function M.get_wsl_host()
	local handle = io.popen("ip route show default 2>/dev/null | awk '{print $3}'")
	if handle then
		local ip = handle:read("*all"):gsub("%s+", "")
		handle:close()
		if ip ~= "" then
			return ip
		end
	end
	return "127.0.0.1"
end

--- Get appropriate host for Ollama (handles WSL/native Linux)
---@return string Host address
function M.get_ollama_host()
	return M.is_wsl() and M.get_wsl_host() or "localhost"
end

return M
