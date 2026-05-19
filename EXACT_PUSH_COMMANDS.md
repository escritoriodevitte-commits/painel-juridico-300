# Exact Terminal Commands - Link Remote & Push

**Copy-paste ready commands for your platform**

---

## 📌 Prerequisites

Before running these commands:
1. Create empty repository on your platform (GitHub.com/new, GitLab.com, etc.)
2. **DO NOT** initialize with README
3. Copy the repository HTTPS URL from the platform
4. Replace `YOUR-USERNAME` with your actual username

---

## GitHub (Recommended)

### Create Repository
Visit: https://github.com/new
- Name: `painel-juridico-v2`
- Description: `Production-ready legal case management desktop application`
- Choose: Public or Private
- DO NOT initialize

### Copy-Paste These Commands

```powershell
# Set your GitHub username (replace YOUR-USERNAME)
$username = "YOUR-USERNAME"

# Add remote
git remote add origin https://github.com/$username/painel-juridico-v2.git

# Verify remote
git remote -v

# Create release tag
git tag -a v2.0.0 -m "Release v2.0.0 - Deployment Automation Complete"

# Verify tag
git tag -l

# Push commits (you'll be prompted for credentials)
git push -u origin master

# Push tags
git push origin v2.0.0

# Verify push
git log origin/master --oneline -5
git ls-remote --tags origin
```

### All-In-One (Single Command)

```powershell
git remote add origin https://github.com/YOUR-USERNAME/painel-juridico-v2.git; git remote -v; git tag -a v2.0.0 -m "Release v2.0.0 - Deployment Automation Complete"; git tag -l; git push -u origin master; git push origin v2.0.0; git log origin/master --oneline -5; git ls-remote --tags origin
```

---

## GitLab

### Create Repository
Visit: https://gitlab.com/projects/new
- Project name: `painel-juridico-v2`
- Description: `Production-ready legal case management desktop application`
- Choose: Public or Private
- DO NOT initialize

### Copy-Paste These Commands

```powershell
# Set your GitLab username (replace YOUR-USERNAME)
$username = "YOUR-USERNAME"

# Add remote
git remote add origin https://gitlab.com/$username/painel-juridico-v2.git

# Verify remote
git remote -v

# Create release tag
git tag -a v2.0.0 -m "Release v2.0.0 - Deployment Automation Complete"

# Verify tag
git tag -l

# Push commits (you'll be prompted for credentials)
git push -u origin master

# Push tags
git push origin v2.0.0

# Verify push
git log origin/master --oneline -5
git ls-remote --tags origin
```

### All-In-One (Single Command)

```powershell
git remote add origin https://gitlab.com/YOUR-USERNAME/painel-juridico-v2.git; git remote -v; git tag -a v2.0.0 -m "Release v2.0.0 - Deployment Automation Complete"; git tag -l; git push -u origin master; git push origin v2.0.0; git log origin/master --oneline -5; git ls-remote --tags origin
```

---

## Bitbucket

### Create Repository
Visit: https://bitbucket.org/repo/create
- Repository name: `painel-juridico-v2`
- Description: `Production-ready legal case management desktop application`
- Choose: Public or Private
- DO NOT initialize

### Copy-Paste These Commands

```powershell
# Set your Bitbucket username (replace YOUR-USERNAME)
$username = "YOUR-USERNAME"

# Add remote
git remote add origin https://bitbucket.org/$username/painel-juridico-v2.git

# Verify remote
git remote -v

# Create release tag
git tag -a v2.0.0 -m "Release v2.0.0 - Deployment Automation Complete"

# Verify tag
git tag -l

# Push commits (you'll be prompted for credentials)
git push -u origin master

# Push tags
git push origin v2.0.0

# Verify push
git log origin/master --oneline -5
git ls-remote --tags origin
```

### All-In-One (Single Command)

```powershell
git remote add origin https://bitbucket.org/YOUR-USERNAME/painel-juridico-v2.git; git remote -v; git tag -a v2.0.0 -m "Release v2.0.0 - Deployment Automation Complete"; git tag -l; git push -u origin master; git push origin v2.0.0; git log origin/master --oneline -5; git ls-remote --tags origin
```

---

## Azure DevOps

### Create Repository
Visit: https://dev.azure.com
- Create new project: `painel-juridico-v2`
- Create repository in project
- DO NOT initialize

### Copy-Paste These Commands

```powershell
# Set your Azure DevOps organization and project
$org = "YOUR-ORG"
$project = "painel-juridico-v2"

# Add remote
git remote add origin "https://dev.azure.com/$org/$project/_git/painel-juridico-v2"

# Verify remote
git remote -v

# Create release tag
git tag -a v2.0.0 -m "Release v2.0.0 - Deployment Automation Complete"

# Verify tag
git tag -l

# Push commits (you'll be prompted for credentials)
git push -u origin master

# Push tags
git push origin v2.0.0

# Verify push
git log origin/master --oneline -5
git ls-remote --tags origin
```

### All-In-One (Single Command)

```powershell
$org = "YOUR-ORG"; $project = "painel-juridico-v2"; git remote add origin "https://dev.azure.com/$org/$project/_git/painel-juridico-v2"; git remote -v; git tag -a v2.0.0 -m "Release v2.0.0 - Deployment Automation Complete"; git tag -l; git push -u origin master; git push origin v2.0.0; git log origin/master --oneline -5; git ls-remote --tags origin
```

---

## Private Git Server

### Copy-Paste These Commands

```powershell
# Set your server URL
$serverUrl = "https://your-server.com/git/painel-juridico-v2.git"

# Add remote
git remote add origin $serverUrl

# Verify remote
git remote -v

# Create release tag
git tag -a v2.0.0 -m "Release v2.0.0 - Deployment Automation Complete"

# Verify tag
git tag -l

# Push commits (you'll be prompted for credentials)
git push -u origin master

# Push tags
git push origin v2.0.0

# Verify push
git log origin/master --oneline -5
git ls-remote --tags origin
```

---

## 🔑 Authentication When Prompted

### GitHub/GitLab/Bitbucket
When prompted for password, enter your **Personal Access Token** (NOT your password)

**Generate Token:**
- **GitHub**: https://github.com/settings/tokens
- **GitLab**: https://gitlab.com/-/profile/personal_access_tokens
- **Bitbucket**: https://bitbucket.org/account/settings/personal-scripts/

---

## ✅ Verification Commands (After Push)

```powershell
# View commits on remote
git log origin/master --oneline -10

# View tags on remote
git ls-remote --tags origin

# View remote configuration
git remote -v

# Check status
git status
```

---

## 📋 Step-by-Step Process

1. **Create repository** on your chosen platform (do NOT initialize)
2. **Copy the HTTPS URL** from the platform
3. **Replace YOUR-USERNAME** in the commands above
4. **Open PowerShell** in your project directory
5. **Run the commands** in order:
   - `git remote add origin ...`
   - `git remote -v` (verify)
   - `git tag -a v2.0.0 ...`
   - `git push -u origin master` (enter token when prompted)
   - `git push origin v2.0.0`
6. **Verify success** with `git log origin/master` and `git ls-remote --tags origin`

---

## 🔍 Troubleshooting

### Error: "remote repository not found"
**Check:**
- Repository created on platform
- Username is correct in URL
- URL copied exactly

**Fix:**
```powershell
git remote remove origin
git remote add origin https://github.com/CORRECT-USERNAME/painel-juridico-v2.git
```

### Error: "Authentication failed"
**Clear credentials and retry:**
```powershell
cmdkey /delete:github.com
git push -u origin master
# Enter your personal access token when prompted
```

### Error: "permission denied"
**Check:**
- Token has `repo` scope
- Repository is Public (or you have write access)
- Using correct GitHub/GitLab account

---

## 💾 Save These Commands

Recommended: Save to a text file for future reference:
```powershell
# Create a file with your chosen commands
"git remote add origin https://github.com/YOUR-USERNAME/painel-juridico-v2.git" | Out-File -FilePath "git_commands.txt"
```

---

## ✨ You're Ready!

Choose your platform above, replace placeholders, and run the commands.

All 10 files (140.1 KB) with complete deployment automation documentation will be pushed to your remote repository.

Good luck! 🚀
