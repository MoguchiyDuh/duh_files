# Neovim - Complete Keybinding Guide

Neovim is a hyperextensible Vim-based text editor. This guide covers all default keybindings, modes, and common operations.

---

## Modes

Neovim operates in different modes, each with its own set of keybindings:

| Mode | Description | Enter | Exit |
|------|-------------|-------|------|
| **Normal** | Default mode for navigation and commands | `Esc` | - |
| **Insert** | Text insertion | `i`, `a`, `o`, etc. | `Esc` |
| **Visual** | Text selection | `v`, `V`, `Ctrl-v` | `Esc` |
| **Command-line** | Execute commands | `:` | `Enter` or `Esc` |
| **Replace** | Overwrite text | `R` | `Esc` |
| **Terminal** | Terminal emulator | `:terminal` | `Ctrl-\ Ctrl-n` |

---

## Normal Mode - Motion Commands

### Basic Movement

```
h                 # Move left
j                 # Move down
k                 # Move up
l                 # Move right

Ctrl-h            # Move left (alternative)
Ctrl-j            # Move down (alternative)
Ctrl-k            # Move up (alternative)
Ctrl-l            # Move right (alternative)
```

---

### Word Movement

```
w                 # Next word (start)
W                 # Next WORD (whitespace-separated)
e                 # Next word (end)
E                 # Next WORD (end)
b                 # Previous word (start)
B                 # Previous WORD (start)
ge                # Previous word (end)
gE                # Previous WORD (end)
```

**Note:** `word` respects punctuation, `WORD` only whitespace.

---

### Line Movement

```
0                 # Start of line (column 0)
^                 # First non-blank character
$                 # End of line
g_                # Last non-blank character
g0                # First character on screen line (when wrap enabled)
g^                # First non-blank on screen line
g$                # Last character on screen line
gm                # Middle of screen line
```

---

### Screen Movement

```
H                 # Top of screen (High)
M                 # Middle of screen
L                 # Bottom of screen (Low)
zt                # Scroll current line to top
zz                # Scroll current line to center
zb                # Scroll current line to bottom
```

---

### Paragraph/Block Movement

```
{                 # Previous paragraph/block
}                 # Next paragraph/block
(                 # Previous sentence
)                 # Next sentence
[[                # Previous section/function
]]                # Next section/function
[]                # End of previous section
][                # End of next section
```

---

### Document Movement

```
gg                # First line of document
G                 # Last line of document
:n or nG          # Go to line n
n%                # Go to n% through file
```

---

### Character Search

```
f{char}           # Find next {char} on line (forward)
F{char}           # Find previous {char} on line (backward)
t{char}           # Till next {char} (cursor before char)
T{char}           # Till previous {char}
;                 # Repeat last f/F/t/T
,                 # Repeat last f/F/t/T in opposite direction
```

---

### Matching Pairs

```
%                 # Jump to matching bracket/paren/brace
[{                # Previous unmatched {
]}                # Next unmatched }
[(                # Previous unmatched (
])                # Next unmatched )
```

---

### Scrolling

```
Ctrl-f            # Page down (forward)
Ctrl-b            # Page up (backward)
Ctrl-d            # Half page down
Ctrl-u            # Half page up
Ctrl-e            # Scroll down one line
Ctrl-y            # Scroll up one line
```

---

### Jump List

```
Ctrl-o            # Jump to older position
Ctrl-i            # Jump to newer position (Tab)
:jumps            # Show jump list
```

---

### Change List

```
g;                # Go to previous change
g,                # Go to next change
:changes          # Show change list
`.                # Jump to last change position
```

---

## Normal Mode - Editing Commands

### Insert Mode Entry

```
i                 # Insert before cursor
I                 # Insert at start of line
a                 # Append after cursor
A                 # Append at end of line
o                 # Open new line below
O                 # Open new line above
s                 # Substitute character (delete char and insert)
S                 # Substitute line (delete line and insert)
cc                # Change line (same as S)
C                 # Change to end of line
```

---

### Delete Commands

```
x                 # Delete character under cursor
X                 # Delete character before cursor
dw                # Delete word
dW                # Delete WORD
dd                # Delete line
D                 # Delete to end of line (same as d$)
d0                # Delete to start of line
d^                # Delete to first non-blank
d$                # Delete to end of line
d{motion}         # Delete with any motion
```

**Examples:**
```
d2w               # Delete 2 words
d5j               # Delete 5 lines down
dt)               # Delete till )
df,               # Delete including ,
```

---

### Change Commands

```
cw                # Change word
cW                # Change WORD
cc                # Change line
C                 # Change to end of line
c0                # Change to start of line
c$                # Change to end of line
c{motion}         # Change with any motion
r{char}           # Replace single character
R                 # Enter Replace mode
```

**Examples:**
```
c3w               # Change 3 words
ct"               # Change till "
ciw               # Change inner word
ci"               # Change inside quotes
```

---

### Yank (Copy) Commands

```
yw                # Yank word
yW                # Yank WORD
yy                # Yank line
Y                 # Yank line (same as yy)
y$                # Yank to end of line
y0                # Yank to start of line
y{motion}         # Yank with any motion
```

**Examples:**
```
y3j               # Yank 3 lines down
yap               # Yank a paragraph
yi"               # Yank inside quotes
```

---

### Paste Commands

```
p                 # Paste after cursor/below line
P                 # Paste before cursor/above line
gp                # Paste and move cursor after
gP                # Paste before and move cursor after
]p                # Paste and adjust indent
[p                # Paste before and adjust indent
```

---

### Undo/Redo

```
u                 # Undo
Ctrl-r            # Redo
U                 # Undo all changes on line
:earlier 10m      # Go to state 10 minutes ago
:later 5m         # Go to state 5 minutes later
```

---

### Repeat Commands

```
.                 # Repeat last change
@:                # Repeat last command-line command
@@                # Repeat last macro
&                 # Repeat last :substitute
```

---

### Text Manipulation

```
~                 # Toggle case of character
g~{motion}        # Toggle case
gu{motion}        # Lowercase
gU{motion}        # Uppercase
guu               # Lowercase line
gUU               # Uppercase line
g~w               # Toggle case of word
guaw              # Lowercase word
gUaw              # Uppercase word
```

---

### Joining Lines

```
J                 # Join line below with space
gJ                # Join line below without space
```

---

### Increment/Decrement

```
Ctrl-a            # Increment number under cursor
Ctrl-x            # Decrement number under cursor
g Ctrl-a          # Increment sequence (visual mode)
g Ctrl-x          # Decrement sequence (visual mode)
```

---

### Indentation

```
>>                # Indent line right
<<                # Indent line left
>{motion}         # Indent motion right
<{motion}         # Indent motion left
={motion}         # Auto-indent motion
==                # Auto-indent line
gg=G              # Auto-indent entire file
```

---

### Formatting

```
gq{motion}        # Format text
gqq               # Format line
gw{motion}        # Format text (keep cursor position)
gww               # Format line (keep cursor)
```

---

## Text Objects

Text objects define regions of text for operations.

### Inner vs Around

```
i{object}         # Inner object (exclude delimiters)
a{object}         # Around object (include delimiters)
```

---

### Word Objects

```
iw                # Inner word
aw                # Around word (includes trailing space)
iW                # Inner WORD
aW                # Around WORD
```

**Examples:**
```
diw               # Delete inner word
daw               # Delete word including space
ciw               # Change inner word
yaw               # Yank word with space
```

---

### Sentence/Paragraph Objects

```
is                # Inner sentence
as                # Around sentence
ip                # Inner paragraph
ap                # Around paragraph
```

---

### Paired Delimiters

```
i"                # Inside double quotes
a"                # Around double quotes
i'                # Inside single quotes
a'                # Around single quotes
i`                # Inside backticks
a`                # Around backticks
i(  or  ib        # Inside parentheses
a(  or  ab        # Around parentheses
i[                # Inside brackets
a[                # Around brackets
i{  or  iB        # Inside braces
a{  or  aB        # Around braces
i<                # Inside angle brackets
a<                # Around angle brackets
it                # Inside HTML/XML tag
at                # Around HTML/XML tag
```

**Examples:**
```
di"               # Delete inside quotes
ca(               # Change around parentheses
yi{               # Yank inside braces
dat               # Delete around HTML tag
cit               # Change inside HTML tag
```

---

## Visual Mode

### Enter Visual Mode

```
v                 # Character-wise visual
V                 # Line-wise visual
Ctrl-v            # Block-wise visual (column)
gv                # Reselect last visual selection
```

---

### Visual Mode Operations

Once in visual mode, use motion keys to select, then:

```
d                 # Delete selection
c                 # Change selection
y                 # Yank selection
~                 # Toggle case
u                 # Lowercase
U                 # Uppercase
>                 # Indent right
<                 # Indent left
=                 # Auto-indent
J                 # Join lines
o                 # Toggle cursor to other end
O                 # Toggle cursor to other corner (block mode)
```

---

### Visual Block Mode

Special operations in block mode (`Ctrl-v`):

```
I                 # Insert before block
A                 # Append after block
c                 # Change block
r                 # Replace all characters
$                 # Select to end of lines
```

---

### Visual Mode Motions

```
aw                # Select word
ap                # Select paragraph
a"                # Select quoted string (including quotes)
i"                # Select inside quotes
at                # Select HTML tag
it                # Select inside HTML tag
```

---

## Searching and Replacing

### Search

```
/pattern          # Search forward
?pattern          # Search backward
n                 # Next match
N                 # Previous match
*                 # Search word under cursor (forward)
#                 # Search word under cursor (backward)
g*                # Search partial word forward
g#                # Search partial word backward
```

---

### Search Options

```
/pattern\c        # Case-insensitive search
/pattern\C        # Case-sensitive search
/\<pattern\>      # Whole word search
/pattern/e        # Cursor at end of match
/pattern/+2       # Cursor 2 lines after match
```

---

### Search History

```
/<Up>             # Previous search pattern
/<Down>           # Next search pattern
q/                # Open search history window
q?                # Open backward search history
```

---

### Substitute (Replace)

```
:s/old/new/       # Replace first occurrence in line
:s/old/new/g      # Replace all in line
:%s/old/new/g     # Replace all in file
:%s/old/new/gc    # Replace all with confirmation
:5,10s/old/new/g  # Replace in lines 5-10
:'<,'>s/old/new/g # Replace in visual selection
```

**Flags:**
```
g                 # Global (all occurrences in line)
c                 # Confirm each substitution
i                 # Ignore case
I                 # Don't ignore case
```

---

### Search Highlighting

```
:set hlsearch     # Enable highlight
:set nohlsearch   # Disable highlight
:noh              # Clear current highlights
```

---

## Marks and Jumps

### Setting Marks

```
m{a-z}            # Set local mark (lowercase = buffer-local)
m{A-Z}            # Set global mark (uppercase = across files)
```

---

### Jumping to Marks

```
'{mark}           # Jump to mark line (first non-blank)
`{mark}           # Jump to exact mark position
''                # Jump to previous position (line)
``                # Jump to previous position (exact)
'.                # Jump to last change (line)
`.                # Jump to last change (exact)
'"                # Jump to last exit position
'[                # Jump to start of last change/yank
']                # Jump to end of last change/yank
'<                # Jump to start of last visual selection
'>                # Jump to end of last visual selection
```

---

### Special Marks

```
'.                # Last change
'"                # Last exit position in current buffer
'[                # Start of last change/yank
']                # End of last change/yank
'<                # Start of last visual selection
'>                # End of last visual selection
```

---

### List Marks

```
:marks            # Show all marks
:marks aB         # Show specific marks
:delmarks a       # Delete mark a
:delmarks a-z     # Delete marks a through z
:delmarks!        # Delete all lowercase marks
```

---

## Registers

### Using Registers

```
"{register}       # Use specific register
"ayy              # Yank line to register a
"ap               # Paste from register a
"Ayy              # Append line to register a (uppercase)
```

---

### Special Registers

```
""                # Unnamed register (default)
"0                # Last yank
"1-"9             # Delete history (1=most recent)
"-                # Small delete (less than one line)
"*                # System clipboard (X11 primary)
"+                # System clipboard (X11 clipboard)
"_                # Black hole (discard)
"/                # Last search pattern
":                # Last command
".                # Last inserted text
"%                # Current filename
"#                # Alternate filename
"=                # Expression register
```

---

### Register Operations

```
:reg              # Show all registers
:reg abc          # Show specific registers
"ayiw             # Yank inner word to register a
"Ayw              # Append word to register a
"_dd              # Delete line to black hole (no save)
"+yy              # Yank line to system clipboard
"+p               # Paste from system clipboard
```

---

## Macros

### Recording Macros

```
q{register}       # Start recording to register
q                 # Stop recording
@{register}       # Execute macro
@@                # Repeat last macro
{count}@{register} # Execute macro count times
```

**Example workflow:**
```
qa                # Start recording to register a
<commands>        # Perform operations
q                 # Stop recording
@a                # Execute macro
10@a              # Execute macro 10 times
```

---

### Editing Macros

```
:let @a='...'     # Set macro content directly
:put a            # Paste macro content
"ap               # Paste macro to edit
"ayy              # Yank edited macro back
```

---

### Recursive Macros

```
qaq               # Clear register a
qa                # Start recording
<commands>
@a                # Call macro recursively
q                 # Stop recording
```

---

## Windows

### Creating Windows

```
:split            # Horizontal split (same file)
:vsplit           # Vertical split (same file)
:new              # Horizontal split (new file)
:vnew             # Vertical split (new file)
Ctrl-w s          # Horizontal split
Ctrl-w v          # Vertical split
Ctrl-w n          # Horizontal split (new file)
```

---

### Navigating Windows

```
Ctrl-w h          # Move to left window
Ctrl-w j          # Move to window below
Ctrl-w k          # Move to window above
Ctrl-w l          # Move to right window
Ctrl-w w          # Cycle to next window
Ctrl-w W          # Cycle to previous window
Ctrl-w p          # Go to previous window
Ctrl-w t          # Go to top-left window
Ctrl-w b          # Go to bottom-right window
```

---

### Resizing Windows

```
Ctrl-w =          # Make all windows equal size
Ctrl-w +          # Increase height
Ctrl-w -          # Decrease height
Ctrl-w >          # Increase width
Ctrl-w <          # Decrease width
Ctrl-w |          # Maximize width
Ctrl-w _          # Maximize height
:resize 20        # Set height to 20 lines
:vertical resize 80  # Set width to 80 columns
```

---

### Moving Windows

```
Ctrl-w H          # Move window to far left
Ctrl-w J          # Move window to bottom
Ctrl-w K          # Move window to top
Ctrl-w L          # Move window to far right
Ctrl-w r          # Rotate windows
Ctrl-w R          # Rotate windows backward
Ctrl-w x          # Exchange with next window
```

---

### Closing Windows

```
:q                # Quit window
:close            # Close current window
Ctrl-w c          # Close current window
Ctrl-w q          # Quit current window
Ctrl-w o          # Close all other windows (:only)
:only             # Close all windows except current
```

---

## Buffers

### Buffer Operations

```
:e file           # Edit file (new buffer)
:enew             # Create new unnamed buffer
:badd file        # Add file to buffer list
:bdelete          # Delete current buffer
:bdelete N        # Delete buffer N
:bwipeout         # Wipe out buffer (remove all traces)
```

---

### Navigating Buffers

```
:bnext            # Next buffer
:bprevious        # Previous buffer
:bfirst           # First buffer
:blast            # Last buffer
:buffer N         # Go to buffer N
:buffer filename  # Go to buffer by name
:b partial<Tab>   # Go to buffer by partial name
Ctrl-^            # Toggle to alternate buffer
Ctrl-6            # Same as Ctrl-^ (alternate buffer)
```

---

### Buffer List

```
:ls               # List all buffers
:buffers          # List all buffers (same as :ls)
:files            # List all buffers (same as :ls)
:ls!              # List all buffers including unlisted
```

**Buffer indicators:**
```
%     Current buffer
#     Alternate buffer
a     Active (loaded and displayed)
h     Hidden
-     Not modifiable
=     Readonly
+     Modified
```

---

## Tabs

### Creating Tabs

```
:tabnew           # New tab with empty buffer
:tabnew file      # New tab with file
:tabe file        # New tab with file (same as :tabnew)
Ctrl-w T          # Move window to new tab
```

---

### Navigating Tabs

```
gt                # Next tab
gT                # Previous tab
{count}gt         # Go to tab {count}
:tabn             # Next tab
:tabp             # Previous tab
:tabfirst         # First tab
:tablast          # Last tab
```

---

### Managing Tabs

```
:tabclose         # Close current tab
:tabonly          # Close all other tabs
:tabm N           # Move tab to position N
:tabm +1          # Move tab one position right
:tabm -1          # Move tab one position left
```

---

### Tab List

```
:tabs             # List all tabs
```

---

## Folding

### Manual Folding

```
zf{motion}        # Create fold
zd                # Delete fold under cursor
zD                # Delete folds recursively
zE                # Eliminate all folds in window
```

---

### Fold Navigation

```
zo                # Open fold
zO                # Open folds recursively
zc                # Close fold
zC                # Close folds recursively
za                # Toggle fold
zA                # Toggle folds recursively
zv                # Open folds to reveal cursor
zx                # Undo manually opened/closed folds
zX                # Undo manually opened/closed folds (recursive)
zm                # Fold more (increase foldlevel)
zM                # Close all folds
zr                # Fold less (reduce foldlevel)
zR                # Open all folds
```

---

### Fold Movement

```
[z                # Move to start of open fold
]z                # Move to end of open fold
zj                # Move to next fold
zk                # Move to previous fold
```

---

### Fold Methods

```
:set foldmethod=manual     # Manual folding
:set foldmethod=indent     # Fold by indentation
:set foldmethod=expr       # Fold by expression
:set foldmethod=marker     # Fold by markers
:set foldmethod=syntax     # Fold by syntax
```

---

## Command-Line Mode

### Entering Command Mode

```
:                 # Enter command-line mode
/                 # Search forward
?                 # Search backward
!                 # Filter through external command
```

---

### Command-Line Editing

```
Ctrl-w            # Delete word before cursor
Ctrl-u            # Delete to start of line
Ctrl-h            # Delete character before cursor (backspace)
Ctrl-r {reg}      # Insert register content
Ctrl-r Ctrl-w     # Insert word under cursor
Ctrl-r Ctrl-a     # Insert WORD under cursor
```

---

### Command-Line Navigation

```
<Left>            # Move cursor left
<Right>           # Move cursor right
Ctrl-b            # Move to start of line
Ctrl-e            # Move to end of line
<Up>              # Previous command in history
<Down>            # Next command in history
```

---

### Command-Line Window

```
q:                # Open command-line window (commands)
q/                # Open command-line window (search forward)
q?                # Open command-line window (search backward)
Ctrl-f            # Open command-line window from command mode
```

---

### Range Syntax

```
:5,10             # Lines 5-10
:'<,'>            # Visual selection
:%                # Entire file
:.                # Current line
:$                # Last line
:.,$              # Current to last line
:.,+5             # Current line plus 5
:-5,.             # 5 lines before to current
```

---

## File Operations

### Opening Files

```
:e file           # Edit file
:e!               # Reload file (discard changes)
:e#               # Edit alternate file
:e .              # Open file explorer in current directory
:E                # Open explorer
:Sex              # Split window and explore
:Vex              # Vertical split and explore
```

---

### Saving Files

```
:w                # Write (save) file
:w file           # Write to file
:w!               # Force write
:w >> file        # Append to file
:wa               # Write all changed buffers
:wq               # Write and quit
:x                # Write (if changed) and quit
ZZ                # Same as :x
:saveas file      # Save as file and edit
```

---

### Quitting

```
:q                # Quit
:q!               # Quit without saving
:qa               # Quit all windows
:qa!              # Quit all without saving
:wqa              # Write all and quit
ZQ                # Quit without checking changes
```

---

### File Info

```
Ctrl-g            # Show file info
g Ctrl-g          # Show detailed file info (word count, etc.)
:file             # Show current filename
:f                # Same as :file
```

---

## Insert Mode

### Insert Mode Entry

Already covered in Normal Mode, but here again:

```
i                 # Insert before cursor
I                 # Insert at start of line
a                 # Append after cursor
A                 # Append at end of line
o                 # Open line below
O                 # Open line above
```

---

### Insert Mode Commands

```
Ctrl-h            # Delete character before cursor (backspace)
Ctrl-w            # Delete word before cursor
Ctrl-u            # Delete to start of line
Ctrl-t            # Indent line
Ctrl-d            # De-indent line
Ctrl-n            # Next completion match
Ctrl-p            # Previous completion match
Ctrl-x Ctrl-n     # Word completion (keywords)
Ctrl-x Ctrl-f     # File path completion
Ctrl-x Ctrl-l     # Line completion
Ctrl-x Ctrl-o     # Omni completion (LSP)
Ctrl-r {reg}      # Insert register content
Ctrl-r =          # Insert expression result
Ctrl-a            # Insert previously inserted text
Ctrl-@            # Insert previously inserted text and exit insert
Ctrl-v {code}     # Insert character by decimal code
Ctrl-v u{code}    # Insert Unicode character
```

---

### Insert Mode Movement

```
<Left>            # Move left
<Right>           # Move right
<Up>              # Move up
<Down>            # Move down
<Home>            # Start of line
<End>             # End of line
```

---

### Completion

```
Ctrl-n            # Next match (generic completion)
Ctrl-p            # Previous match
Ctrl-x Ctrl-n     # Keyword completion (current file)
Ctrl-x Ctrl-i     # Keyword completion (current + included)
Ctrl-x Ctrl-]     # Tag completion
Ctrl-x Ctrl-f     # Filename completion
Ctrl-x Ctrl-l     # Whole line completion
Ctrl-x Ctrl-o     # Omni completion
Ctrl-x Ctrl-u     # User-defined completion
Ctrl-x Ctrl-v     # Vim command completion
Ctrl-x Ctrl-s     # Spelling suggestions
```

---

## Replace Mode

```
R                 # Enter Replace mode
r{char}           # Replace single character
gr{char}          # Virtual replace single character
gR                # Enter Virtual Replace mode
```

In Replace mode, typing overwrites existing characters.

---

## Terminal Mode

### Terminal Operations

```
:terminal         # Open terminal in current window
:term             # Same as :terminal
:split | term     # Open terminal in split
:vsplit | term    # Open terminal in vertical split
:tabnew | term    # Open terminal in new tab
```

---

### Terminal Navigation

```
Ctrl-\ Ctrl-n     # Exit terminal mode to normal mode
i                 # Enter terminal mode (from normal)
a                 # Enter terminal mode (from normal)
```

---

### Terminal Window Management

Once in normal mode (after `Ctrl-\ Ctrl-n`):
```
Ctrl-w h/j/k/l    # Navigate to other windows
Ctrl-w c          # Close terminal window
```

---

## Spell Checking

### Enable Spell Checking

```
:set spell        # Enable spell checking
:set nospell      # Disable spell checking
:set spell spelllang=en_us  # Set language
```

---

### Spell Navigation

```
]s                # Next misspelled word
[s                # Previous misspelled word
]S                # Next bad word (ignore rare words)
[S                # Previous bad word
```

---

### Spell Correction

```
z=                # Suggest corrections
1z=               # Use first suggestion
zg                # Add word to dictionary (good word)
zG                # Add word to internal word list
zw                # Mark word as bad
zW                # Mark word as bad (internal)
zug               # Undo zg (remove from dictionary)
zuw               # Undo zw
```

---

## Quickfix and Location Lists

### Quickfix List

```
:copen            # Open quickfix window
:cclose           # Close quickfix window
:cnext            # Next quickfix item
:cprevious        # Previous quickfix item
:cfirst           # First quickfix item
:clast            # Last quickfix item
:cc N             # Go to quickfix item N
:cnfile           # First item in next file
:cpfile           # First item in previous file
```

---

### Location List

```
:lopen            # Open location list
:lclose           # Close location list
:lnext            # Next location list item
:lprevious        # Previous location list item
:lfirst           # First location list item
:llast            # Last location list item
```

---

## Diff Mode

### Starting Diff

```
:diffsplit file   # Diff with file in split
:diffthis         # Make current window part of diff
:diffoff          # Turn off diff mode
:diffupdate       # Update diff highlighting
```

---

### Diff Navigation

```
]c                # Next change
[c                # Previous change
```

---

### Diff Operations

```
do                # Diff obtain (get changes from other)
dp                # Diff put (put changes to other)
:diffget          # Get changes from specific buffer
:diffput          # Put changes to specific buffer
```

---

## Tags

### Tag Navigation

```
Ctrl-]            # Jump to tag under cursor
Ctrl-t            # Jump back from tag
g Ctrl-]          # List matching tags
:tag tagname      # Jump to tag
:tags             # Show tag stack
:tn               # Next matching tag
:tp               # Previous matching tag
:tfirst           # First matching tag
:tlast            # Last matching tag
```

---

### Tag Generation

```
:!ctags -R        # Generate tags for project (external)
```

---

## LSP (Language Server Protocol)

**Note:** Requires LSP client configured (built-in in Neovim 0.5+)

### LSP Commands

```
gd                # Go to definition
gD                # Go to declaration
gr                # Go to references
gi                # Go to implementation
K                 # Show hover documentation
<C-k>             # Show signature help
<leader>rn        # Rename symbol
<leader>ca        # Code action
[d                # Previous diagnostic
]d                # Next diagnostic
<leader>e         # Show diagnostic float
<leader>q         # Set location list with diagnostics
<leader>f         # Format code
```

**These keybindings may vary based on your LSP configuration.**

---

## File Explorer (Netrw)

```
:E                # Open file explorer
:Sex              # Split and explore
:Vex              # Vertical split and explore
:Tex              # Tab and explore

# Inside Netrw:
<Enter>           # Open file/directory
-                 # Go up directory
d                 # Create directory
%                 # Create file
R                 # Rename file
D                 # Delete file
i                 # Change view mode
s                 # Change sorting
r                 # Reverse sorting
gh                # Toggle hidden files
```

---

## Help System

```
:help             # Open help
:help topic       # Help on specific topic
:helpgrep pattern # Search help files
Ctrl-]            # Follow link in help
Ctrl-t            # Go back in help
:help index       # Index of all commands
:help quickref    # Quick reference
:help usr_toc     # User manual table of contents
```

**Examples:**
```
:help w           # Help on 'w' command
:help i_ctrl-w    # Help on Ctrl-w in insert mode
:help c_ctrl-r    # Help on Ctrl-r in command mode
:help 'number'    # Help on 'number' option
```

---

## Options and Settings

### Setting Options

```
:set option       # Enable boolean option
:set nooption     # Disable boolean option
:set option!      # Toggle boolean option
:set option?      # Query option value
:set option=value # Set value
:set option+=value # Append to value
:set option-=value # Remove from value
```

---

### Common Options

```
:set number       # Show line numbers
:set relativenumber # Show relative line numbers
:set nowrap       # Disable line wrapping
:set expandtab    # Use spaces instead of tabs
:set tabstop=4    # Tab width
:set shiftwidth=4 # Indent width
:set autoindent   # Auto-indent new lines
:set smartindent  # Smart auto-indenting
:set hlsearch     # Highlight search results
:set incsearch    # Incremental search
:set ignorecase   # Case-insensitive search
:set smartcase    # Smart case sensitivity
:set clipboard=unnamedplus # Use system clipboard
:set mouse=a      # Enable mouse
:set cursorline   # Highlight current line
:set colorcolumn=80 # Show column guide
```

---

## Advanced Commands

### Execute Normal Commands

```
:normal {cmd}     # Execute normal mode commands
:%normal A;       # Append ; to every line
:'<,'>normal @a   # Execute macro a on selection
```

---

### Global Commands

```
:g/pattern/cmd    # Execute cmd on lines matching pattern
:g!/pattern/cmd   # Execute cmd on lines NOT matching
:v/pattern/cmd    # Same as :g! (inverse)
```

**Examples:**
```
:g/TODO/d         # Delete all lines with TODO
:g/^$/d           # Delete all empty lines
:g/pattern/normal @a # Execute macro on matching lines
:v/^#/d           # Delete all lines NOT starting with #
```

---

### Sort

```
:sort             # Sort lines
:sort!            # Sort in reverse
:sort u           # Sort and remove duplicates
:sort i           # Case-insensitive sort
:sort n           # Numeric sort
```

---

### External Commands

```
:!command         # Execute external command
:r !command       # Read command output into buffer
:w !command       # Write buffer to command stdin
:%!command        # Filter buffer through command
:'<,'>!command    # Filter selection through command
```

**Examples:**
```
:!ls              # List directory
:r !date          # Insert current date
:%!sort           # Sort entire file
:'<,'>!sort -u    # Sort and deduplicate selection
```

---

## Session Management

```
:mksession file   # Save session to file
:mksession! file  # Overwrite session file
:source file      # Load session
:mksession! ~/Session.vim # Save session
nvim -S ~/Session.vim     # Start with session
```

---

## Miscellaneous Commands

### Recording Screen Updates

```
qa                # Start recording to register a
q                 # Stop recording
```

---

### Digraphs (Special Characters)

```
Ctrl-k {char1}{char2}  # Insert digraph in insert mode
:digraphs         # Show all digraphs
```

**Examples:**
```
Ctrl-k a*         # Greek alpha (α)
Ctrl-k (c         # Copyright (©)
Ctrl-k <<         # Left angle quote («)
```

---

### Calculator

```
# In insert mode:
Ctrl-r =          # Open expression register
2+2<Enter>        # Calculates and inserts 4
```

---

### Source Commands

```
:source %         # Source current file
:so %             # Same as :source %
```

---

### Execute Commands

```
:execute "cmd"    # Execute command from string
:execute "normal! gg" # Execute normal mode commands
```

---

## Common Workflows

### Refactoring

```
# Rename variable under cursor
*                 # Search for word
cgn               # Change next occurrence
.                 # Repeat for each occurrence
n.                # Next occurrence and repeat
```

---

### Multiple Cursors (Alternative)

```
# Using visual block mode:
Ctrl-v            # Enter visual block
j/k               # Select multiple lines
I                 # Insert at start
<text>            # Type text
Esc               # Apply to all lines
```

---

### Surround Text (Manual)

```
# Surround word with quotes:
ciw               # Change inner word
"<text>"          # Type quoted text

# Or visually:
viw               # Select inner word
c                 # Change
"<text>"          # Type quoted text
```

---

### Navigate Jumps

```
Ctrl-o            # Jump to previous location
Ctrl-i            # Jump to next location
:jumps            # View jump list
g;                # Go to previous change
g,                # Go to next change
```

---

### Multiple File Editing

```
:args *.js        # Add all .js files to arg list
:argdo %s/old/new/ge | update  # Substitute in all and save
:bufdo %s/old/new/ge | update  # Substitute in all buffers
```

---

## Custom Keybindings (Common)

These are commonly set in `init.vim` or `init.lua`:

```vim
" Map leader to space
let mapleader = " "

" Quick save
nnoremap <leader>w :w<CR>

" Quick quit
nnoremap <leader>q :q<CR>

" Clear search highlight
nnoremap <leader>h :noh<CR>

" Split navigation
nnoremap <C-h> <C-w>h
nnoremap <C-j> <C-w>j
nnoremap <C-k> <C-w>k
nnoremap <C-l> <C-w>l

" Buffer navigation
nnoremap <leader>bn :bnext<CR>
nnoremap <leader>bp :bprevious<CR>
nnoremap <leader>bd :bdelete<CR>

" Tab navigation
nnoremap <leader>tn :tabnext<CR>
nnoremap <leader>tp :tabprevious<CR>
```

---

## Popular Plugins and Their Bindings

### vim-plug (Plugin Manager)

```
:PlugInstall      # Install plugins
:PlugUpdate       # Update plugins
:PlugClean        # Remove unlisted plugins
:PlugUpgrade      # Upgrade vim-plug itself
```

---

### NERDTree (File Explorer)

```
<leader>n         # Toggle NERDTree (custom)
Ctrl-n            # Toggle NERDTree (custom)

# Inside NERDTree:
o                 # Open file/directory
s                 # Open in split
v                 # Open in vsplit
t                 # Open in tab
i                 # Open in split (alternative)
m                 # Open menu (create/delete/move)
R                 # Refresh
?                 # Toggle help
```

---

### fzf.vim (Fuzzy Finder)

```
:Files            # Search files
:GFiles           # Search git files
:Buffers          # Search buffers
:Lines            # Search lines in loaded buffers
:BLines           # Search lines in current buffer
:Tags             # Search tags
:Ag pattern       # Search pattern using ag
:Rg pattern       # Search pattern using ripgrep

# Custom mappings:
<leader>ff        # Find files
<leader>fg        # Find git files
<leader>fb        # Find buffers
<leader>fl        # Find lines
```

---

### telescope.nvim (Fuzzy Finder)

```
<leader>ff        # Find files
<leader>fg        # Live grep
<leader>fb        # Buffers
<leader>fh        # Help tags
<leader>fo        # Old files
<leader>fc        # Commands

# Inside telescope:
Ctrl-n            # Next item
Ctrl-p            # Previous item
Ctrl-c            # Close
Ctrl-x            # Open in split
Ctrl-v            # Open in vsplit
Ctrl-t            # Open in tab
```

---

### vim-surround

```
cs"'              # Change surrounding " to '
cs'<q>            # Change ' to <q></q>
cst"              # Change surrounding tag to "
ds"               # Delete surrounding "
dst               # Delete surrounding tag
ysiw]             # Surround inner word with []
ysiw[             # Surround inner word with [ ] (with spaces)
yss)              # Surround entire line with ()
ySS)              # Surround line and indent
```

---

### vim-commentary

```
gcc               # Comment/uncomment line
gc{motion}        # Comment motion
gcap              # Comment paragraph
gc                # Comment selection (visual mode)
```

---

### vim-fugitive (Git)

```
:Git              # Git status
:Git add %        # Stage current file
:Git commit       # Commit
:Git push         # Push
:Git pull         # Pull
:Git blame        # Blame current file
:Gdiffsplit       # Diff current file
:Glog             # Load commits into quickfix
```

---

### nvim-tree.lua

```
<leader>e         # Toggle file tree
<leader>r         # Refresh tree

# Inside tree:
o                 # Open file/folder
a                 # Create file/folder
d                 # Delete file/folder
r                 # Rename file/folder
x                 # Cut file/folder
c                 # Copy file/folder
p                 # Paste file/folder
y                 # Copy name
Y                 # Copy relative path
gy                # Copy absolute path
```

---

### nvim-cmp (Completion)

```
Ctrl-n            # Next suggestion
Ctrl-p            # Previous suggestion
Ctrl-y            # Confirm selection
Ctrl-e            # Close completion menu
Ctrl-d            # Scroll docs down
Ctrl-u            # Scroll docs up
Ctrl-Space        # Trigger completion
```

---

### hop.nvim (Easy Motion)

```
<leader>hw        # Hop to word
<leader>hl        # Hop to line
<leader>hc        # Hop to character
<leader>hp        # Hop to pattern
```

---

## Debugging

### Built-in Debugging (termdebug)

```
:Termdebug        # Start debugging session
:Break            # Set breakpoint
:Clear            # Clear breakpoint
:Step             # Step over
:Over             # Step over
:Finish           # Step out
:Continue         # Continue execution
:Evaluate         # Evaluate expression
```

---

## Performance

### Profiling

```
:profile start profile.log  # Start profiling
:profile func *             # Profile all functions
:profile file *             # Profile all files
:profile stop               # Stop profiling
```

---

## Tips and Tricks

### Repeat Last Command

```
@:                # Repeat last : command
@@                # Repeat last macro
.                 # Repeat last change
&                 # Repeat last :substitute
```

---

### Quick Calculations

```
# In insert mode:
Ctrl-r =5*8<CR>   # Inserts 40
```

---

### Rot13 Encoding

```
g?{motion}        # Rot13 encode
g?g?              # Rot13 entire line
```

---

### Increment/Decrement Multiple

```
# In visual block mode:
Ctrl-v            # Select column
g Ctrl-a          # Incrementing sequence
```

---

### Execute Command on Range

```
:5,10normal A;    # Append ; to lines 5-10
:%normal @a       # Execute macro a on all lines
```

---

## Quick Reference

### Mode Indicators

```
-- INSERT --      # Insert mode
-- VISUAL --      # Visual mode
-- VISUAL LINE -- # Visual line mode
-- VISUAL BLOCK -- # Visual block mode
-- REPLACE --     # Replace mode
```

---

### Essential Commands Summary

| Category | Command | Description |
|----------|---------|-------------|
| **Motion** | `hjkl` | Basic movement |
| | `w/b/e` | Word movement |
| | `0/$` | Line start/end |
| | `gg/G` | File start/end |
| **Edit** | `i/a/o` | Insert modes |
| | `d/c/y` | Delete/change/yank |
| | `p/P` | Paste |
| | `u/Ctrl-r` | Undo/redo |
| **Search** | `//?` | Search forward/backward |
| | `n/N` | Next/previous match |
| | `*//#` | Search word under cursor |
| **Visual** | `v/V/Ctrl-v` | Visual modes |
| **Files** | `:w/:q/:e` | Save/quit/edit |
| **Windows** | `Ctrl-w s/v` | Split horizontal/vertical |
| | `Ctrl-w hjkl` | Navigate windows |
| **Buffers** | `:bn/:bp` | Next/previous buffer |
| **Macros** | `q{a-z}` | Record macro |
| | `@{a-z}` | Execute macro |

---

## Configuration Files

### Config Locations

```
~/.config/nvim/init.vim      # Main Vimscript config
~/.config/nvim/init.lua      # Main Lua config
~/.config/nvim/lua/          # Lua modules directory
```

---

### Basic init.vim Example

```vim
" Leader key
let mapleader = " "

" Line numbers
set number
set relativenumber

" Indentation
set expandtab
set tabstop=4
set shiftwidth=4

" Search
set ignorecase
set smartcase
set hlsearch
set incsearch

" UI
set cursorline
set termguicolors
set mouse=a

" Clipboard
set clipboard=unnamedplus

" Custom keybindings
nnoremap <leader>w :w<CR>
nnoremap <leader>q :q<CR>
nnoremap <leader>h :noh<CR>
```

---

## See Also
- [[00 - Programming MOC]] - Programming overview
- [[Git]] - Version control
- [[Regex]] - Pattern matching in searches
