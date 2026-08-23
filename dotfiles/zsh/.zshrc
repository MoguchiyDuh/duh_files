export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
export EDITOR="nvim"
export VISUAL="nvim"
export MANPAGER="sh -c 'col -bx | bat -l man -p'"
export OPENCODE_ENABLE_EXA=1

plugin_dir="${XDG_DATA_HOME:-$HOME/.local/share}/zsh/plugins"
mkdir -p "$plugin_dir"

typeset -A _plugin_repos=(
  zsh-autosuggestions "zsh-users/zsh-autosuggestions"
  fast-syntax-highlighting "zdharma-continuum/fast-syntax-highlighting"
  zsh-completions "zsh-users/zsh-completions"
)
for _name _slug in ${(kv)_plugin_repos}; do
  if [[ ! -d "$plugin_dir/$_name" ]]; then
    git clone --quiet --depth 1 "https://github.com/$_slug" "$plugin_dir/$_name" &
  fi
done
wait

export HISTFILE="${XDG_STATE_HOME:-$HOME/.local/state}/zsh/history"
mkdir -p "$HISTFILE:h"
HISTSIZE=50000
SAVEHIST=50000
setopt inc_append_history share_history hist_ignore_dups hist_ignore_space hist_reduce_blanks
setopt autocd interactive_comments no_beep

fpath=("$plugin_dir/zsh-completions/src" $fpath)
autoload -Uz compinit
compinit -d "${XDG_CACHE_HOME:-$HOME/.cache}/zsh/zcompdump-$ZSH_VERSION"

zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Za-z}'
[[ -n ${LS_COLORS:-} ]] && zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}

bindkey -e
bindkey '^[[H' beginning-of-line
bindkey '^[[F' end-of-line
bindkey '^[[3~' delete-char
bindkey '^[[1;5C' forward-word
bindkey '^[[1;5D' backward-word

ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=8'
ZSH_AUTOSUGGEST_STRATEGY=(history completion)
source "$plugin_dir/zsh-autosuggestions/zsh-autosuggestions.zsh"

alias ls='eza --icons --git --header --group-directories-first'
alias la='eza -la --icons --git --header --group-directories-first'

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

alias h='history'
alias hc='rm -f ~/.local/share/atuin/history.db'
alias c='clear'
alias venv='source .venv/bin/activate'
alias lgit='lazygit'
alias lsql='lazysql'
alias ldoc='lazydocker'

yy() {
  local tmp="$(mktemp -t "yazi-cwd.XXXXXX")" cwd
  yazi "$@" --cwd-file="$tmp"
  if cwd="$(command cat -- "$tmp")" && [ -n "$cwd" ] && [ "$cwd" != "$PWD" ]; then
    builtin cd -- "$cwd"
  fi
  rm -f -- "$tmp"
}

eval "$(zoxide init zsh)"
eval "$(fzf --zsh)"
eval "$(atuin init zsh)"
[[ -o interactive ]] && fastfetch
eval "$(starship init zsh)"
source "$plugin_dir/fast-syntax-highlighting/fast-syntax-highlighting.plugin.zsh"
