# --- Powerlevel10k Instant Prompt ---
# Should stay on top
typeset -g POWERLEVEL9K_INSTANT_PROMPT=off

if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# --- Exports & Environment ---
export ZSH="$HOME/.oh-my-zsh"
export PATH="$HOME/.local/bin:$PATH"
export TERMINAL=$terminal
export XDG_TERMINAL_EMULATOR=$terminal
export EDITOR="nvim"
export VISUAL="nvim"
export MANPAGER="sh -c 'col -bx | bat -l man -p'"

# --- Oh My Zsh Configuration ---
ZSH_THEME="powerlevel10k/powerlevel10k"
plugins=(git zsh-autosuggestions zsh-syntax-highlighting zsh-completions fzf)

source $ZSH/oh-my-zsh.sh

# --- nnn Configuration ---
export NNN_TRASH=1
export NNN_OPTS="deH"
export NNN_FIFO="/tmp/nnn.fifo"
export NNN_OPENER=xdg-open

# --- Completion Settings ---
fpath=(~/.zsh/completions $fpath)
autoload -U compinit && compinit -u

compdef _uv uv.exe
compdef _cargo cargo.exe
compdef _go go.exe
compdef _pip pip.exe
compdef _python python.exe
eval "$(register-python-argcomplete duh-yt_manager)"

# --- Aliases: Core Remaps ---
alias ls='eza --icons --git --header --group-directories-first'
alias la='eza -la --icons --git --header --group-directories-first'
alias tree='eza --tree --icons'

# --- Aliases: Pacman ---
alias pac='sudo pacman'
alias pac-update='sudo pacman -Sy'
alias pac-upgrade='sudo pacman -Syu'
alias pac-install='sudo pacman -S --needed'
alias pac-remove='sudo pacman -Rns'
alias pac-search='pacman -Ss'
alias pac-show='pacman -Si'
alias pac-list='pacman -Q'
alias pac-listfiles='pacman -Ql'
alias pac-clean='sudo pacman -Sc'
alias pac-autoclean='sudo pacman -Scc'
alias pac-depends='pactree -d1'
alias pac-why='pactree -r'

# --- Aliases: Yay ---
alias y='yay'
alias y-update='yay -Sy'
alias y-upgrade='yay -Syu'
alias y-install='yay -S --needed'
alias y-remove='yay -Rns'
alias y-search='yay -Ss'
alias y-show='yay -Si'
alias y-list='yay -Q'
alias y-listfiles='yay -Ql'
alias y-clean='yay -Sc'
alias y-autoclean='yay -Scc'

# --- Aliases: Utilities ---
alias h='history'
alias hc='history -c'
alias c='clear'
alias venv='source .venv/bin/activate'
alias lgit='lazygit'
alias lsql='lazysql'
alias ldoc='lazydocker'

# --- Initializations ---
eval "$(zoxide init zsh)"

# Load Powerlevel10k elements
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# Startup info
fastfetch

export PATH="$HOME/.cargo/bin:$PATH"
