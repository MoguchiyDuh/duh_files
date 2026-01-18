#!/bin/bash
# Zsh auto-installer with Oh-My-Zsh, Powerlevel10k, and plugins
# Supports: Arch (pacman/yay), Debian/Ubuntu (apt), Fedora (dnf), macOS (brew)

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Zsh Auto-Installer ===${NC}"
echo

# Detect OS and package manager
detect_system() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [ -f /etc/arch-release ]; then
        echo "arch"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    elif [ -f /etc/fedora-release ]; then
        echo "fedora"
    else
        echo "unknown"
    fi
}

SYSTEM=$(detect_system)
echo -e "${BLUE}Detected system: ${YELLOW}$SYSTEM${NC}"
echo

if [ "$SYSTEM" = "unknown" ]; then
    echo -e "${RED}Error: Unsupported system${NC}"
    exit 1
fi

# Install packages based on system
install_packages() {
    echo -e "${GREEN}[1/7] Installing packages...${NC}"

    case $SYSTEM in
        arch)
            sudo pacman -S --needed --noconfirm zsh zsh-completions git curl

            # Check if yay is installed
            if command -v yay &> /dev/null; then
                echo "Installing autojump via yay..."
                yay -S --needed --noconfirm autojump
            else
                echo -e "${YELLOW}Warning: yay not found, skipping autojump${NC}"
                echo "Install yay first or install autojump manually"
            fi
            ;;

        debian)
            sudo apt update
            sudo apt install -y zsh git curl autojump
            ;;

        fedora)
            sudo dnf install -y zsh git curl autojump-zsh
            ;;

        macos)
            if ! command -v brew &> /dev/null; then
                echo -e "${RED}Error: Homebrew not installed${NC}"
                echo "Install from: https://brew.sh"
                exit 1
            fi
            brew install zsh git curl autojump
            ;;
    esac
}

install_packages

# Install Oh-My-Zsh
echo -e "${GREEN}[2/7] Installing Oh-My-Zsh...${NC}"
if [ -d "$HOME/.oh-my-zsh" ]; then
    echo "Oh-My-Zsh already installed"
else
    RUNZSH=no sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
fi

# Install Powerlevel10k
echo -e "${GREEN}[3/7] Installing Powerlevel10k...${NC}"
if [ -d "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k" ]; then
    echo "Powerlevel10k already installed"
else
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
fi

# Install zsh-autosuggestions
echo -e "${GREEN}[4/7] Installing zsh-autosuggestions...${NC}"
if [ -d "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions" ]; then
    echo "zsh-autosuggestions already installed"
else
    git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
fi

# Install zsh-syntax-highlighting
echo -e "${GREEN}[5/7] Installing zsh-syntax-highlighting...${NC}"
if [ -d "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting" ]; then
    echo "zsh-syntax-highlighting already installed"
else
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
fi

# Install zsh-completions plugin
echo -e "${GREEN}[5.5/7] Installing zsh-completions plugin...${NC}"
if [ -d "${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-completions" ]; then
    echo "zsh-completions plugin already installed"
else
    git clone https://github.com/zsh-users/zsh-completions ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-completions
fi

# Configure .zshrc
echo -e "${GREEN}[6/7] Configuring .zshrc...${NC}"

# Backup existing .zshrc
if [ -f "$HOME/.zshrc" ]; then
    cp "$HOME/.zshrc" "$HOME/.zshrc.backup.$(date +%Y%m%d_%H%M%S)"
    echo "Backed up existing .zshrc"
fi

# Determine autojump source path based on system
AUTOJUMP_SOURCE=""
case $SYSTEM in
    arch)
        AUTOJUMP_SOURCE="/etc/profile.d/autojump.zsh"
        ;;
    debian)
        AUTOJUMP_SOURCE="/usr/share/autojump/autojump.sh"
        ;;
    fedora)
        AUTOJUMP_SOURCE="/usr/share/autojump/autojump.zsh"
        ;;
    macos)
        AUTOJUMP_SOURCE="\$(brew --prefix)/etc/profile.d/autojump.sh"
        ;;
esac

# Modify .zshrc
ZSHRC="$HOME/.zshrc"

# Change theme to powerlevel10k
if grep -q "^ZSH_THEME=" "$ZSHRC"; then
    sed -i 's|^ZSH_THEME=.*|ZSH_THEME="powerlevel10k/powerlevel10k"|' "$ZSHRC"
else
    # Add theme if not present
    sed -i '/^export ZSH=/a ZSH_THEME="powerlevel10k/powerlevel10k"' "$ZSHRC"
fi

# Update plugins
if grep -q "^plugins=(" "$ZSHRC"; then
    sed -i 's|^plugins=(.*|plugins=(git zsh-autosuggestions zsh-syntax-highlighting zsh-completions autojump)|' "$ZSHRC"
else
    # Add plugins if not present
    sed -i '/^source \$ZSH\/oh-my-zsh.sh/i plugins=(git zsh-autosuggestions zsh-syntax-highlighting zsh-completions autojump)' "$ZSHRC"
fi

# Add fpath for zsh-completions
if ! grep -q "fpath.*zsh-completions" "$ZSHRC"; then
    sed -i '/^source \$ZSH\/oh-my-zsh.sh/i fpath+=${ZSH_CUSTOM:-${ZSH:-~/.oh-my-zsh}/custom}/plugins/zsh-completions/src' "$ZSHRC"
fi

# Add Powerlevel10k instant prompt at the beginning (after shebang/comments)
if ! grep -q "p10k-instant-prompt" "$ZSHRC"; then
    P10K_PROMPT='# Enable Powerlevel10k instant prompt
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi
'
    # Find first non-comment line
    FIRST_LINE=$(grep -n "^[^#]" "$ZSHRC" | head -1 | cut -d: -f1)
    if [ -n "$FIRST_LINE" ]; then
        sed -i "${FIRST_LINE}i\\${P10K_PROMPT}" "$ZSHRC"
    else
        # If all lines are comments, append at beginning
        echo -e "${P10K_PROMPT}\n$(cat $ZSHRC)" > "$ZSHRC"
    fi
fi

# Add autojump source at the end if not present
if ! grep -q "autojump" "$ZSHRC" || ! grep -q "$AUTOJUMP_SOURCE" "$ZSHRC"; then
    echo "" >> "$ZSHRC"
    echo "# Autojump" >> "$ZSHRC"
    echo "[[ -s \"$AUTOJUMP_SOURCE\" ]] && source \"$AUTOJUMP_SOURCE\"" >> "$ZSHRC"
fi

# Add p10k config source at the end if not present
if ! grep -q "p10k.zsh" "$ZSHRC"; then
    echo "" >> "$ZSHRC"
    echo "# To customize prompt, run \`p10k configure\` or edit ~/.p10k.zsh" >> "$ZSHRC"
    echo "[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh" >> "$ZSHRC"
fi

echo ".zshrc configured"

# Change default shell
echo -e "${GREEN}[7/7] Setting Zsh as default shell...${NC}"
ZSH_PATH=$(which zsh)

if [ "$SHELL" != "$ZSH_PATH" ]; then
    if [ "$SYSTEM" = "macos" ]; then
        # macOS requires adding zsh to /etc/shells
        if ! grep -q "$ZSH_PATH" /etc/shells; then
            echo "$ZSH_PATH" | sudo tee -a /etc/shells
        fi
    fi
    chsh -s "$ZSH_PATH"
    echo "Default shell changed to Zsh"
else
    echo "Zsh is already the default shell"
fi

echo
echo -e "${BLUE}=== Installation Complete! ===${NC}"
echo
echo -e "${GREEN}Next steps:${NC}"
echo "1. Log out and log back in (or run: exec zsh)"
echo "2. Run 'p10k configure' to set up Powerlevel10k theme"
echo
echo -e "${BLUE}Installed components:${NC}"
echo "  • Oh-My-Zsh"
echo "  • Powerlevel10k"
echo "  • zsh-autosuggestions"
echo "  • zsh-syntax-highlighting"
echo "  • zsh-completions"
echo "  • autojump"
