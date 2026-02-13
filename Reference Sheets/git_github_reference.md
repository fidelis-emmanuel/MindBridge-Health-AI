# GIT & GITHUB REFERENCE SHEET
**MindBridge Health - Healthcare AI Engineer Training**
**Day 4 - February 12, 2026**

---

## 🎯 WHAT IS GIT & GITHUB?

**GIT:**
- Version control system (runs on YOUR computer)
- Tracks changes to your code
- Like a "time machine" for your files
- Creates snapshots (commits) of your work

**GITHUB:**
- Cloud hosting for Git repositories
- Your code backed up online
- Visible to employers/recruiters
- Collaboration platform

**ANALOGY:**
- Git = Track Changes in Word (local)
- GitHub = Google Drive for code (cloud)

---

## ⚙️ INITIAL SETUP (ONE TIME ONLY)

### Check if Git is installed:
````bash
git --version
````

**Should show:** `git version 2.x.x`

### Configure your identity:
````bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
````

### Verify configuration:
````bash
git config --global user.name
git config --global user.email
````

---

## 🌟 GITHUB ACCOUNT SETUP (ONE TIME)

### 1. Create account:
- Go to https://github.com
- Sign up with professional username
- Use same email as Git config
- Verify email address

### 2. Enable 2FA (Security):
- Settings → Password and authentication
- Enable two-factor authentication
- Use Authenticator app

### 3. Create Personal Access Token:
- Settings → Developer settings → Personal access tokens → Tokens (classic)
- Generate new token (classic)
- Note: "Project name - Local Development"
- Expiration: 90 days
- Scope: Check "repo" only
- Generate token
- **COPY AND SAVE IMMEDIATELY!**

**Token format:** `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**USE THIS AS PASSWORD when pushing to GitHub!**

---

## 📂 CREATING A NEW REPOSITORY

### On GitHub (Web):
1. Click "+" → New repository
2. Repository name: `Your-Project-Name`
3. Description: Brief project description
4. Visibility: **Public** (for portfolio)
5. **DO NOT** check any initialization boxes
6. Click "Create repository"

### On Your Computer (Local):
````bash
# Navigate to your project folder
cd "E:\Your Project Folder"

# Initialize Git
git init

# Create .gitignore FIRST (security!)
echo "*.env" > .gitignore
echo "API_KEY.txt" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Project description"

# Connect to GitHub
git remote add origin https://github.com/USERNAME/REPO-NAME.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
````

**When prompted:**
- Username: your-github-username
- Password: **PASTE YOUR TOKEN** (not your GitHub password!)

---

## 🔄 DAILY GIT WORKFLOW

### The Standard Process:

**1. Check status:**
````bash
git status
````
Shows what files changed

**2. Add files:**
````bash
git add .                    # Add ALL changed files
git add filename.py          # Add specific file
git add folder/              # Add entire folder
````

**3. Commit with message:**
````bash
git commit -m "Description of what you changed"
````

**Examples of good commit messages:**
- `"Add patient analyzer script"`
- `"Fix bug in Excel generator"`
- `"Update README with installation instructions"`
- `"Add error handling to batch processor"`

**4. Push to GitHub:**
````bash
git push
````

**First time pushing a new branch:**
````bash
git push -u origin main
````

---

## 📋 ESSENTIAL GIT COMMANDS

### Status & Information:
````bash
git status              # See what changed
git log                 # See commit history
git log --oneline       # Compact commit history
git diff                # See exact changes (not yet staged)
````

### Adding & Committing:
````bash
git add .               # Stage all changes
git add filename.py     # Stage specific file
git commit -m "message" # Create commit with message
````

### Pushing & Pulling:
````bash
git push                # Send commits to GitHub
git pull                # Get latest from GitHub
````

### Branching (Advanced):
````bash
git branch              # List branches
git branch name         # Create new branch
git checkout name       # Switch to branch
git checkout -b name    # Create and switch to branch
````

### Undoing Changes:
````bash
git restore filename    # Discard changes to file
git reset HEAD~1        # Undo last commit (keep changes)
git reset --hard HEAD~1 # Undo last commit (discard changes)
````

**⚠️ BE CAREFUL with `--hard` - it permanently deletes changes!**

---

## 🔒 SECURITY BEST PRACTICES

### .gitignore File:

**ALWAYS create .gitignore BEFORE first commit!**
````bash
# Create .gitignore
echo "*.env" > .gitignore
echo "*.txt" >> .gitignore
echo "API_KEY.txt" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "venv/" >> .gitignore
echo ".vscode/" >> .gitignore
````

### What to NEVER commit:
- ❌ API keys
- ❌ Passwords
- ❌ Database credentials
- ❌ .env files
- ❌ Personal data
- ❌ Large binary files

### What to ALWAYS commit:
- ✅ Source code (.py, .js, .html)
- ✅ Documentation (.md, .txt)
- ✅ Configuration templates
- ✅ README files
- ✅ .gitignore file

---

## 📝 CREATING A PROFESSIONAL README

### Basic README Structure:
````markdown
# Project Name

Brief description of what the project does

## Features
- Feature 1
- Feature 2
- Feature 3

## Technologies
- Python 3.x
- Library 1
- Library 2

## Installation
```bash
git clone https://github.com/username/repo.git
cd repo
pip install -r requirements.txt
```

## Usage
```bash
python main.py
```

## Author
Your Name
Your Title
Your Location
````

### README Best Practices:
- ✅ Clear project title
- ✅ Brief description (1-2 sentences)
- ✅ Features list
- ✅ Technologies used
- ✅ Installation instructions
- ✅ Usage examples
- ✅ Author information
- ✅ Use emojis (🎯 🚀 ✅) for visual appeal
- ✅ Include code blocks with syntax highlighting

---

## 🚨 COMMON ERRORS & SOLUTIONS

### Error: "repository not found"
**Solution:** Check your remote URL
````bash
git remote -v                # See current URL
git remote remove origin     # Remove old URL
git remote add origin https://github.com/USERNAME/REPO.git  # Add correct URL
````

### Error: "Please tell me who you are"
**Solution:** Configure Git identity
````bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
````

### Error: "Permission denied"
**Solution:** Use Personal Access Token, not password
- Generate new token on GitHub
- Use token when asked for password

### Error: "fatal: not a git repository"
**Solution:** Initialize Git in the folder
````bash
git init
````

### Error: "Your branch is ahead of origin/main"
**Solution:** Push your commits
````bash
git push
````

### Error: "refusing to merge unrelated histories"
**Solution:** (When pulling from existing repo)
````bash
git pull origin main --allow-unrelated-histories
````

### Accidentally committed sensitive file:
**Solution:**
````bash
# Remove from Git (but keep local file)
git rm --cached filename.txt

# Add to .gitignore
echo "filename.txt" >> .gitignore

# Commit the removal
git add .gitignore
git commit -m "Remove sensitive file and update .gitignore"
git push
````

---

## 📊 GIT WORKFLOW DIAGRAM
````
Your Computer                  GitHub
     |                           |
     |--- git init              |
     |--- git add .             |
     |--- git commit            |
     |                           |
     |--- git push -----------→ |
     |                           |
     |← ----------- git pull ---|
     |                           |
````

**Normal workflow:**
1. Make changes to files
2. `git add .` (stage changes)
3. `git commit -m "message"` (save snapshot)
4. `git push` (send to GitHub)

---

## 🎯 DAILY PRACTICE ROUTINE

### Morning:
````bash
git status              # See what you have
git pull                # Get latest from GitHub
````

### After making changes:
````bash
git status              # See what changed
git add .               # Stage changes
git commit -m "What you did"
git push                # Send to GitHub
````

### Before leaving:
````bash
git status              # Verify everything committed
git push                # Make sure GitHub is updated
````

---

## 💡 PRO TIPS

**Tip 1: Commit Often**
- Commit every 30-60 minutes
- Or after completing a feature
- Small commits = easier to track

**Tip 2: Write Good Commit Messages**
- ✅ "Add patient analyzer function"
- ✅ "Fix bug in Excel generator"
- ❌ "Update" (too vague)
- ❌ "asdf" (meaningless)

**Tip 3: Push Daily**
- Backs up your work
- Makes it visible to others
- Creates professional activity

**Tip 4: Review Before Committing**
````bash
git status       # What files changed?
git diff         # What exactly changed?
````

**Tip 5: Use .gitignore**
- Create it FIRST, before any commits
- Better to exclude too much than too little
- Review it periodically

---

## 📚 GITHUB PROFILE OPTIMIZATION

### Professional Profile Checklist:
- ✅ Professional username
- ✅ Real name
- ✅ Professional bio (1-2 sentences)
- ✅ Location (for local jobs)
- ✅ Email verified
- ✅ 2FA enabled
- ⏰ Profile picture (later)
- ⏰ Personal website (later)

### Repository Best Practices:
- ✅ Descriptive repository names
- ✅ Clear descriptions
- ✅ Professional READMEs
- ✅ Public visibility (for portfolio)
- ✅ Regular commits (shows activity)
- ✅ Organized folder structure

---

## 🔍 CHECKING YOUR WORK

### After pushing to GitHub:
1. Go to https://github.com/USERNAME/REPO
2. Verify all files are there
3. Check README displays correctly
4. Review code to ensure no secrets
5. Test clone link works

### Verification commands:
````bash
git status              # Should say "nothing to commit"
git log                 # Should show your commits
git remote -v           # Should show GitHub URL
````

---

## 📞 WHEN TO USE WHAT

**Use Git (Local):**
- Tracking your changes
- Creating commits
- Viewing history
- Undoing mistakes

**Use GitHub (Cloud):**
- Backing up code
- Sharing with others
- Showing employers
- Collaborating with team

**Use Both:**
- Normal development workflow
- Daily code changes
- Professional portfolio

---

## 🎓 PRACTICE EXERCISES

### Exercise 1: New Project
1. Create new folder
2. Initialize Git
3. Create .gitignore
4. Add some Python files
5. Commit and push to GitHub

### Exercise 2: Making Changes
1. Modify a file
2. Check status
3. Add and commit
4. Push to GitHub
5. Verify on GitHub

### Exercise 3: README
1. Create README.md
2. Add project description
3. Add features list
4. Commit and push
5. View on GitHub

---

## 🚀 QUICK REFERENCE

### First Time Setup:
````bash
git config --global user.name "Name"
git config --global user.email "email"
````

### New Project:
````bash
git init
git add .
git commit -m "Initial commit"
git remote add origin URL
git branch -M main
git push -u origin main
````

### Daily Workflow:
````bash
git status
git add .
git commit -m "Description"
git push
````

### View History:
````bash
git log
git log --oneline
````

---

## 📖 GLOSSARY

**Repository (Repo):** Folder tracked by Git

**Commit:** Snapshot of your code at a point in time

**Push:** Send commits from your computer to GitHub

**Pull:** Get commits from GitHub to your computer

**Branch:** Separate line of development

**Main:** Default branch name (used to be "master")

**Origin:** Nickname for your GitHub repository

**Clone:** Copy a repository from GitHub to your computer

**Fork:** Copy someone else's repository to your account

**Staging:** Preparing files for commit (git add)

**Remote:** GitHub repository URL

**Local:** Your computer's copy

---

## ✅ DAY 4 ACCOMPLISHMENTS CHECKLIST

**Setup:**
- [ ] Git installed and configured
- [ ] GitHub account created
- [ ] Professional username chosen
- [ ] Email verified
- [ ] 2FA enabled
- [ ] Personal Access Token created

**First Repository:**
- [ ] Repository created on GitHub
- [ ] .gitignore file created
- [ ] Files committed locally
- [ ] Code pushed to GitHub
- [ ] README.md created and pushed

**Skills Learned:**
- [ ] git init
- [ ] git add
- [ ] git commit
- [ ] git push
- [ ] git status
- [ ] git log
- [ ] Creating .gitignore
- [ ] Writing commit messages
- [ ] Using Personal Access Token

---

## 🎯 NEXT STEPS

**Continue practicing:**
1. Make daily commits to your projects
2. Update your README as you build features
3. Push to GitHub every day
4. Review your GitHub profile weekly

**Week 2 Preview:**
- Windows Task Scheduler (automated scripts!)
- More advanced Git workflows
- Collaborating with others

---

**END OF REFERENCE SHEET**
````

---

## 💾 SAVE THIS FILE!

**STEPS:**

**1. In Notepad (already open), paste ALL the content above**

**2. File → Save As**

**Filename:** `git_github_reference.md`

**Save as type:** All Files (*.*) 

**Location:** `E:\Mindbridge health care\Reference Sheets\`

**3. Close Notepad**

---

## 📂 NOW YOU HAVE 6 REFERENCE SHEETS!
````
E:\Mindbridge health care\Reference Sheets\
├── python_essentials_reference.md
├── cli_commands_reference.md
├── architecture_patterns_reference.md
├── staying_current_guide.md
├── document_generation_reference.md
└── git_github_reference.md  ← NEW!