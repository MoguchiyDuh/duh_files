# Should stay on top
typeset -g POWERLEVEL9K_INSTANT_PROMPT=off

if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

export TERMINAL=$terminal
export XDG_TERMINAL_EMULATOR=$terminal

export ZSH="$HOME/.oh-my-zsh"

ZSH_THEME="powerlevel10k/powerlevel10k"

plugins=(git zsh-autosuggestions zsh-syntax-highlighting zsh-completions fzf)

source $ZSH/oh-my-zsh.sh

# nnn config
export NNN_TRASH=1
export NNN_OPTS="deH"  # d=detail, e=scroll editor, H=show hidden
export NNN_FIFO="/tmp/nnn.fifo"
export EDITOR="nvim"
export VISUAL="nvim"
export NNN_OPENER=xdg-open

# REMAP
alias ls='eza --icons --git --header --group-directories-first'
alias la='eza -la --icons --git --header --group-directories-first'
alias cat='bat'
alias grep='rg'
alias find='fd'

# PACMAN ALIASES
alias pac='sudo pacman'                  # base alias
alias pac-update='sudo pacman -Sy'       # update package lists (like `apt update`)
alias pac-upgrade='sudo pacman -Syu'     # full system upgrade (like `apt upgrade`)
alias pac-install='sudo pacman -S --needed'       # install package(s)
alias pac-remove='sudo pacman -Rns'       # remove with configs and deps
alias pac-search='pacman -Ss'            # search in repositories
alias pac-show='pacman -Si'              # show package details
alias pac-list='pacman -Q'               # list installed packages
alias pac-listfiles='pacman -Ql'         # list files from package
alias pac-clean='sudo pacman -Sc'        # remove unused packages and cache
alias pac-autoclean='sudo pacman -Scc'   # delete all cached packages
alias pac-depends='pactree -d1'          # show package dependencies (basic)
alias pac-why='pactree -r'               # reverse dependencies (why pkg is installed)

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

# OTHER ALIASES
alias h='history'
alias hc='history -c'
alias c='clear'
alias venv='source .venv/bin/activate'

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# Autocompletion
fpath=(~/.zsh/completions $fpath)
autoload -U compinit && compinit -u
compdef _uv uv.exe
compdef _cargo cargo.exe
compdef _go go.exe
compdef _pip pip.exe
compdef _python python.exe
eval "$(register-python-argcomplete duh-ytdl)"
eval "$(register-python-argcomplete duh-ytdl-new)"

export PATH="$HOME/.local/bin:$PATH"

# Zoxide
eval "$(zoxide init zsh)"

# Pretty info on startup
fastfetch
