return {
	cmd = { "clangd", "--background-index", "--offset-encoding=utf-16" },
	root_markers = { ".clangd", ".git", "compile_commands.json", "CMakeLists.txt", "Makefile" },
}
