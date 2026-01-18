# Git - Complete Guide

Git is a distributed version control system designed to track changes in source code during software development. It enables collaboration, maintains project history, and provides powerful branching and merging capabilities.

---

## Core Concepts

### Repository (Repo)
A **repository** is a directory tracked by Git containing your project files and the complete history of all changes.

**Types:**
- **Local repository**: On your machine
- **Remote repository**: On a server (GitHub, GitLab, Bitbucket)

---

### Commit
A **commit** is a snapshot of your project at a specific point in time. Each commit has:
- Unique SHA-1 hash (e.g., `a3f2b8c`)
- Author information
- Timestamp
- Commit message
- Parent commit(s)

---

### Branch
A **branch** is an independent line of development. The default branch is typically `main` or `master`.

**Benefits:**
- Isolate features/fixes
- Work on multiple tasks simultaneously
- Safe experimentation

---

### Working Directory, Staging Area, Repository

```
Working Directory  →  Staging Area  →  Local Repository  →  Remote Repository
   (modified)         (staged/indexed)     (committed)          (pushed)
      |                     |                   |                   |
   git add            git commit          git push
```

---

### HEAD
**HEAD** is a pointer to the current branch reference (latest commit on current branch).

---

### Remote
A **remote** is a version of your repository hosted on a server.

**Common remotes:**
- `origin`: Default name for primary remote
- `upstream`: Original repository (for forks)

---

## Installation and Configuration

### Initial Setup

```bash
# Set global username
git config --global user.name "Your Name"

# Set global email
git config --global user.email "your.email@example.com"

# Set default branch name
git config --global init.defaultBranch main

# Set default editor
git config --global core.editor "vim"
git config --global core.editor "code --wait"  # VS Code

# Enable colored output
git config --global color.ui auto

# Set line ending preferences
git config --global core.autocrlf true    # Windows
git config --global core.autocrlf input   # macOS/Linux
```

---

### Configuration Levels

```bash
# System-wide (all users)
git config --system

# User-specific (global)
git config --global

# Repository-specific (local)
git config --local

# View all configurations
git config --list

# View specific config
git config user.name

# Edit config file directly
git config --global --edit
```

---

## Creating Repositories

### Initialize New Repository

```bash
# Create new repo in current directory
git init

# Create new repo in specific directory
git init project-name

# Create bare repository (for remote)
git init --bare project.git
```

---

### Clone Existing Repository

```bash
# Clone via HTTPS
git clone https://github.com/user/repo.git

# Clone via SSH
git clone git@github.com:user/repo.git

# Clone to specific directory
git clone https://github.com/user/repo.git my-folder

# Clone specific branch
git clone -b develop https://github.com/user/repo.git

# Shallow clone (limited history)
git clone --depth 1 https://github.com/user/repo.git
```

---

## Basic Workflow

### Checking Status

```bash
# Full status
git status

# Short format
git status -s
git status --short

# Show branch info
git status -sb
```

**Status indicators:**
- `??` - Untracked
- `A` - Added (staged)
- `M` - Modified
- `D` - Deleted
- `R` - Renamed
- `C` - Copied
- `U` - Unmerged

---

### Adding Changes (Staging)

```bash
# Stage specific file
git add filename.txt

# Stage multiple files
git add file1.txt file2.txt

# Stage all changes
git add .

# Stage all changes (including deletions)
git add -A
git add --all

# Stage only modified/deleted (not new files)
git add -u
git add --update

# Interactive staging
git add -i
git add --interactive

# Patch mode (choose specific changes)
git add -p
git add --patch

# Stage by file pattern
git add *.js
git add src/**/*.py
```

---

### Committing Changes

```bash
# Commit with inline message
git commit -m "Add user authentication feature"

# Commit with detailed message
git commit -m "Add user authentication" -m "- Implement JWT tokens
- Add login/logout endpoints
- Create user session management"

# Stage all tracked files and commit
git commit -a -m "Fix typo in README"
git commit -am "Fix typo in README"

# Amend last commit (change message)
git commit --amend -m "New commit message"

# Amend last commit (add more changes)
git add forgotten-file.txt
git commit --amend --no-edit

# Commit with specific author
git commit --author="John Doe <john@example.com>" -m "Message"

# Create empty commit
git commit --allow-empty -m "Trigger CI pipeline"
```

**Commit message best practices:**
- Use imperative mood: "Add feature" not "Added feature"
- Keep first line under 50 characters
- Add detailed description after blank line
- Reference issue numbers: "Fix #123"

---

### Viewing History

```bash
# View commit history
git log

# Compact one-line format
git log --oneline

# Show graph of branches
git log --oneline --graph --all

# Show last N commits
git log -5

# Show commits with diffs
git log -p
git log --patch

# Show commits with file statistics
git log --stat

# Show commits by author
git log --author="John Doe"

# Show commits in date range
git log --since="2024-01-01"
git log --until="2024-12-31"
git log --after="2 weeks ago"

# Show commits affecting specific file
git log -- filename.txt

# Search commit messages
git log --grep="bug fix"

# Pretty format
git log --pretty=format:"%h - %an, %ar : %s"

# Show commits with specific change
git log -S "function_name"
git log -G "regex_pattern"
```

---

## Branch Management

### Creating Branches

```bash
# List all local branches
git branch

# List all branches (local + remote)
git branch -a
git branch --all

# List remote branches
git branch -r

# Create new branch
git branch feature-login

# Create branch from specific commit
git branch bugfix-123 a3f2b8c

# Create and switch to new branch
git checkout -b feature-signup
git switch -c feature-signup  # Modern syntax
```

---

### Switching Branches

```bash
# Switch to existing branch
git checkout main
git switch main  # Modern syntax

# Switch to previous branch
git checkout -
git switch -

# Create and switch (if doesn't exist)
git checkout -b feature-new
git switch -c feature-new
```

---

### Renaming Branches

```bash
# Rename current branch
git branch -m new-name

# Rename specific branch
git branch -m old-name new-name

# Rename and push to remote
git branch -m old-name new-name
git push origin -u new-name
git push origin --delete old-name
```

---

### Deleting Branches

```bash
# Delete local branch (safe)
git branch -d feature-completed

# Force delete local branch
git branch -D feature-abandoned

# Delete remote branch
git push origin --delete feature-old
git push origin :feature-old  # Alternative syntax

# Prune deleted remote branches
git fetch --prune
git remote prune origin
```

---

### Merging Branches

```bash
# Merge branch into current branch
git merge feature-login

# Merge with commit message
git merge feature-login -m "Merge login feature"

# Fast-forward merge only
git merge --ff-only feature-login

# Always create merge commit
git merge --no-ff feature-login

# Squash merge (combine all commits)
git merge --squash feature-login

# Abort merge
git merge --abort
```

**Merge strategies:**
- **Fast-forward**: Linear history (no merge commit)
- **No-fast-forward**: Always creates merge commit
- **Squash**: Combines all commits into one

---

## Remote Operations

### Managing Remotes

```bash
# Add remote
git remote add origin https://github.com/user/repo.git

# List remotes
git remote
git remote -v  # Show URLs

# Show remote details
git remote show origin

# Rename remote
git remote rename origin upstream

# Change remote URL
git remote set-url origin https://github.com/user/new-repo.git

# Remove remote
git remote remove origin
git remote rm origin
```

---

### Fetching

```bash
# Fetch from default remote (origin)
git fetch

# Fetch from specific remote
git fetch upstream

# Fetch all remotes
git fetch --all

# Fetch and prune deleted branches
git fetch --prune

# Fetch specific branch
git fetch origin main

# Fetch tags
git fetch --tags
```

---

### Pulling

```bash
# Fetch and merge
git pull

# Pull from specific remote and branch
git pull origin main

# Pull with rebase instead of merge
git pull --rebase

# Pull all branches
git pull --all

# Force pull (overwrite local changes)
git fetch origin
git reset --hard origin/main
```

---

### Pushing

```bash
# Push to default remote
git push

# Set upstream and push
git push -u origin main
git push --set-upstream origin main

# Push specific branch
git push origin feature-login

# Push all branches
git push --all

# Push tags
git push --tags

# Push specific tag
git push origin v1.0.0

# Force push (dangerous!)
git push --force
git push -f

# Force push with lease (safer)
git push --force-with-lease

# Delete remote branch
git push origin --delete feature-old

# Push without triggering hooks
git push --no-verify
```

---

## Undoing Changes

### Discard Unstaged Changes

```bash
# Discard changes in specific file
git restore filename.txt
git checkout -- filename.txt  # Old syntax

# Discard all unstaged changes
git restore .
git checkout -- .

# Discard changes in directory
git restore src/
```

---

### Unstage Files

```bash
# Unstage specific file
git restore --staged filename.txt
git reset HEAD filename.txt  # Old syntax

# Unstage all files
git restore --staged .
git reset HEAD .
```

---

### Reset Commits

```bash
# Soft reset (keep changes staged)
git reset --soft HEAD~1

# Mixed reset (keep changes unstaged) [default]
git reset HEAD~1
git reset --mixed HEAD~1

# Hard reset (discard all changes)
git reset --hard HEAD~1

# Reset to specific commit
git reset --hard a3f2b8c

# Reset specific file to HEAD
git reset HEAD filename.txt
```

**Reset levels:**
- `--soft`: Move HEAD, keep staging and working directory
- `--mixed`: Move HEAD, reset staging, keep working directory
- `--hard`: Move HEAD, reset staging and working directory

---

### Revert Commits

```bash
# Revert last commit (creates new commit)
git revert HEAD

# Revert specific commit
git revert a3f2b8c

# Revert multiple commits
git revert a3f2b8c b4e1d9f

# Revert without committing
git revert --no-commit HEAD~3..HEAD
```

**Reset vs Revert:**
- **Reset**: Rewrites history (dangerous for public branches)
- **Revert**: Creates new commit (safe for public branches)

---

## Stashing

### Save Changes Temporarily

```bash
# Stash current changes
git stash
git stash save

# Stash with message
git stash save "Work in progress on login"
git stash push -m "WIP: authentication"

# Stash including untracked files
git stash -u
git stash --include-untracked

# Stash including ignored files
git stash -a
git stash --all

# Stash specific files
git stash push -m "Partial work" file1.txt file2.txt
```

---

### Apply Stashed Changes

```bash
# List stashes
git stash list

# Apply most recent stash
git stash apply

# Apply specific stash
git stash apply stash@{2}

# Apply and remove from stash
git stash pop

# Apply specific stash and remove
git stash pop stash@{1}
```

---

### Manage Stashes

```bash
# Show stash contents
git stash show
git stash show -p  # Show diff

# Show specific stash
git stash show stash@{1}

# Create branch from stash
git stash branch feature-from-stash

# Delete specific stash
git stash drop stash@{1}

# Delete all stashes
git stash clear
```

---

## Tagging

### Creating Tags

```bash
# Create lightweight tag
git tag v1.0.0

# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Tag specific commit
git tag -a v0.9.0 a3f2b8c -m "Beta release"

# Tag with GPG signature
git tag -s v1.0.0 -m "Signed release"
```

---

### Viewing Tags

```bash
# List all tags
git tag

# List tags matching pattern
git tag -l "v1.*"

# Show tag details
git show v1.0.0

# List tags with messages
git tag -n
```

---

### Sharing Tags

```bash
# Push specific tag
git push origin v1.0.0

# Push all tags
git push origin --tags
git push --tags

# Delete local tag
git tag -d v0.9.0

# Delete remote tag
git push origin --delete v0.9.0
git push origin :refs/tags/v0.9.0

# Checkout tag
git checkout v1.0.0
git checkout tags/v1.0.0
```

---

## Viewing Differences

```bash
# Show unstaged changes
git diff

# Show staged changes
git diff --staged
git diff --cached

# Compare working directory with specific commit
git diff HEAD
git diff a3f2b8c

# Compare two commits
git diff a3f2b8c..b4e1d9f

# Compare two branches
git diff main..feature-branch

# Show changes in specific file
git diff filename.txt

# Show word-level diff
git diff --word-diff

# Show statistics only
git diff --stat

# Show file names only
git diff --name-only

# Show diff with context lines
git diff -U10  # 10 lines of context
```

---

## Rebasing

### Basic Rebase

```bash
# Rebase current branch onto main
git rebase main

# Continue rebase after resolving conflicts
git rebase --continue

# Skip current commit
git rebase --skip

# Abort rebase
git rebase --abort

# Rebase onto specific commit
git rebase a3f2b8c
```

---

### Interactive Rebase

```bash
# Interactive rebase last 3 commits
git rebase -i HEAD~3

# Interactive rebase from specific commit
git rebase -i a3f2b8c

# Interactive rebase entire branch
git rebase -i --root
```

**Interactive rebase commands:**
- `pick` (p): Use commit
- `reword` (r): Edit commit message
- `edit` (e): Stop to amend commit
- `squash` (s): Merge with previous commit
- `fixup` (f): Like squash but discard message
- `drop` (d): Remove commit
- `exec` (x): Run shell command

**Example:**
```
pick a3f2b8c Add login feature
reword b4e1d9f Add signup feature
squash c5f3a7d Fix typo in signup
drop d6g4b8e Debugging code
```

---

### Rebase vs Merge

| Feature | Rebase | Merge |
|---------|--------|-------|
| History | Linear | Branched |
| Conflicts | Per commit | Once |
| Public branches | Avoid | Safe |
| Use case | Clean history | Preserve history |

---

## Cherry-Picking

```bash
# Pick single commit
git cherry-pick a3f2b8c

# Pick multiple commits
git cherry-pick a3f2b8c b4e1d9f

# Pick range of commits
git cherry-pick a3f2b8c..d6g4b8e
git cherry-pick a3f2b8c^..d6g4b8e  # Include first commit

# Cherry-pick without committing
git cherry-pick -n a3f2b8c
git cherry-pick --no-commit a3f2b8c

# Cherry-pick and edit message
git cherry-pick -e a3f2b8c
git cherry-pick --edit a3f2b8c

# Continue cherry-pick
git cherry-pick --continue

# Abort cherry-pick
git cherry-pick --abort
```

---

## Resolving Conflicts

### Merge Conflicts

When conflicts occur during merge/rebase:

```bash
# Check conflicted files
git status

# View conflict markers in files
# <<<<<<< HEAD
# Your changes
# =======
# Incoming changes
# >>>>>>> branch-name

# After resolving conflicts:
git add resolved-file.txt
git commit  # For merge
git rebase --continue  # For rebase

# Use theirs/ours strategy
git checkout --theirs file.txt  # Use incoming version
git checkout --ours file.txt    # Use current version

# Abort merge
git merge --abort

# Abort rebase
git rebase --abort
```

---

### Merge Tools

```bash
# Configure merge tool
git config --global merge.tool vimdiff
git config --global merge.tool meld

# Launch merge tool
git mergetool

# Common merge tools:
# - vimdiff
# - meld
# - kdiff3
# - p4merge
# - Beyond Compare
```

---

## Advanced Git

### Bisect (Binary Search for Bugs)

```bash
# Start bisect
git bisect start

# Mark current commit as bad
git bisect bad

# Mark known good commit
git bisect good a3f2b8c

# Git will checkout middle commit, test and mark:
git bisect good  # If working
git bisect bad   # If broken

# Automate bisect
git bisect start HEAD a3f2b8c
git bisect run ./test-script.sh

# Finish bisect
git bisect reset
```

---

### Blame (Find Who Changed What)

```bash
# Show who last modified each line
git blame filename.txt

# Show specific line range
git blame -L 10,20 filename.txt

# Show from specific commit
git blame a3f2b8c filename.txt

# Ignore whitespace changes
git blame -w filename.txt

# Show email instead of name
git blame -e filename.txt
```

---

### Reflog (Reference Logs)

```bash
# Show reflog (all reference updates)
git reflog

# Show reflog for specific branch
git reflog show main

# Recover lost commit
git reflog
git checkout a3f2b8c  # Use hash from reflog

# Recover deleted branch
git reflog
git checkout -b recovered-branch a3f2b8c
```

---

### Submodules

```bash
# Add submodule
git submodule add https://github.com/user/repo.git path/to/submodule

# Clone repo with submodules
git clone --recursive https://github.com/user/repo.git

# Initialize submodules after clone
git submodule init
git submodule update

# Update all submodules
git submodule update --remote

# Remove submodule
git submodule deinit path/to/submodule
git rm path/to/submodule
rm -rf .git/modules/path/to/submodule
```

---

### Worktrees

```bash
# Create worktree
git worktree add ../hotfix-branch hotfix

# List worktrees
git worktree list

# Remove worktree
git worktree remove ../hotfix-branch

# Prune deleted worktrees
git worktree prune
```

---

## Git Hooks

Hooks are scripts that run automatically at specific Git events.

### Common Hooks

**Client-side:**
- `pre-commit`: Before commit is created
- `prepare-commit-msg`: Before commit message editor
- `commit-msg`: Validate commit message
- `post-commit`: After commit is created
- `pre-push`: Before push to remote

**Server-side:**
- `pre-receive`: Before accepting push
- `update`: Similar to pre-receive, per-branch
- `post-receive`: After accepting push

### Example Hook

```bash
# .git/hooks/pre-commit
#!/bin/sh
npm test
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

---

## .gitignore

### Patterns

```gitignore
# Ignore specific file
secret.txt

# Ignore all files with extension
*.log

# Ignore directory
node_modules/
build/

# Ignore files in any directory
**/*.tmp

# Ignore except specific file
!important.log

# Ignore files matching pattern
temp-*
*-backup

# Comments
# This is a comment
```

### Global gitignore

```bash
# Create global gitignore
git config --global core.excludesfile ~/.gitignore_global

# Common global ignores
# macOS
.DS_Store

# Windows
Thumbs.db

# IDEs
.vscode/
.idea/
*.swp
```

---

## Best Practices

### Commit Best Practices

1. **Atomic commits**: One logical change per commit
2. **Meaningful messages**: Describe what and why
3. **Test before commit**: Ensure code works
4. **Frequent commits**: Commit often, push daily
5. **Review before push**: Check `git diff` and `git log`

---

### Branch Workflow

**Common workflows:**

1. **Git Flow**:
   - `main`: Production-ready
   - `develop`: Integration branch
   - `feature/*`: New features
   - `release/*`: Release preparation
   - `hotfix/*`: Emergency fixes

2. **GitHub Flow**:
   - `main`: Always deployable
   - `feature/*`: Short-lived feature branches
   - Pull requests for review
   - Deploy after merge

3. **Trunk-Based Development**:
   - Single `main` branch
   - Very short-lived feature branches
   - Feature flags for incomplete features

---

### Security Best Practices

1. **Never commit secrets**: Use environment variables
2. **Use SSH keys**: More secure than HTTPS
3. **Sign commits**: Use GPG signatures
4. **Review history**: Check for exposed secrets
5. **Use .gitignore**: Prevent accidental commits

---

## Troubleshooting

### Common Issues

**Accidentally committed to wrong branch:**
```bash
git reset --soft HEAD~1
git stash
git checkout correct-branch
git stash pop
git commit -m "Message"
```

**Remove file from Git but keep locally:**
```bash
git rm --cached filename.txt
echo "filename.txt" >> .gitignore
git commit -m "Remove tracked file"
```

**Undo pushed commit:**
```bash
# Create revert commit
git revert HEAD
git push

# Force push (dangerous if others pulled)
git reset --hard HEAD~1
git push --force
```

**Recover deleted branch:**
```bash
git reflog
git checkout -b recovered-branch <commit-hash>
```

**Clean untracked files:**
```bash
# Dry run
git clean -n

# Remove untracked files
git clean -f

# Remove untracked files and directories
git clean -fd

# Remove ignored files too
git clean -fdx
```

---

## Aliases

### Useful Aliases

```bash
# Configure aliases
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual 'log --oneline --graph --all --decorate'
git config --global alias.amend 'commit --amend --no-edit'
git config --global alias.undo 'reset HEAD~1 --mixed'
```

---

## Quick Reference

### Essential Commands

| Command | Description |
|---------|-------------|
| `git init` | Initialize repository |
| `git clone <url>` | Clone repository |
| `git status` | Check status |
| `git add <file>` | Stage changes |
| `git commit -m "msg"` | Commit changes |
| `git push` | Push to remote |
| `git pull` | Fetch and merge |
| `git branch` | List branches |
| `git checkout <branch>` | Switch branch |
| `git merge <branch>` | Merge branch |
| `git log` | View history |
| `git diff` | Show changes |

---

## See Also
- [[00 - Programming MOC]] - Programming overview
