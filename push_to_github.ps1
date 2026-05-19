# ============================================================
# Painel Jurídico v2 - GitHub Push Script
# ============================================================
# This script configures Git remote and pushes to GitHub
# Usage: .\push_to_github.ps1

param(
    [Parameter(Mandatory=$false)]
    [string]$GitHubURL = ""
)

Write-Host "============================================================" -ForegroundColor Green
Write-Host "PAINEL JURÍDICO v2 - GITHUB PUSH SCRIPT" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

# Get GitHub URL if not provided
if ([string]::IsNullOrEmpty($GitHubURL)) {
    Write-Host "`nEnter your GitHub repository HTTPS URL" -ForegroundColor Cyan
    Write-Host "Example: https://github.com/your-username/painel-juridico-v2.git" -ForegroundColor Gray
    $GitHubURL = Read-Host "GitHub URL"
}

if ([string]::IsNullOrEmpty($GitHubURL)) {
    Write-Host "❌ No GitHub URL provided. Exiting." -ForegroundColor Red
    exit 1
}

# Navigate to project
Write-Host "`n1. Navigating to project directory..." -ForegroundColor Cyan
cd "C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2"

# Verify local state
Write-Host "`n2. Verifying local repository..." -ForegroundColor Cyan
Write-Host "Current branch:" -ForegroundColor Gray
git branch -a
Write-Host "`nLatest commits:" -ForegroundColor Gray
git log --oneline -3
Write-Host "`nRelease tags:" -ForegroundColor Gray
git tag -l

# Check if remote already exists
Write-Host "`n3. Configuring GitHub remote..." -ForegroundColor Cyan
$remoteExists = git remote -v | Select-String "origin"

if ($remoteExists) {
    Write-Host "⚠️  Remote 'origin' already exists" -ForegroundColor Yellow
    Write-Host "Removing existing remote..." -ForegroundColor Yellow
    git remote remove origin
}

Write-Host "Adding remote: $GitHubURL" -ForegroundColor Gray
git remote add origin $GitHubURL

# Verify remote
Write-Host "`n4. Verifying remote configuration..." -ForegroundColor Cyan
git remote -v

# Push commits
Write-Host "`n5. Pushing commits to GitHub..." -ForegroundColor Cyan
Write-Host "You may be prompted for GitHub credentials:" -ForegroundColor Yellow
Write-Host "  - Username: Your GitHub username" -ForegroundColor Gray
Write-Host "  - Password: Your personal access token (NOT your password)" -ForegroundColor Gray
Write-Host "  - Token scopes needed: repo, read:org" -ForegroundColor Gray
Write-Host "`nGenerating token: https://github.com/settings/tokens" -ForegroundColor Cyan

git push -u origin master

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Commits pushed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Push failed with error code: $LASTEXITCODE" -ForegroundColor Red
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Verify GitHub repository exists at: $GitHubURL" -ForegroundColor Gray
    Write-Host "  2. Verify personal access token is correct (repo + read:org scopes)" -ForegroundColor Gray
    Write-Host "  3. Check GitHub status: https://www.githubstatus.com" -ForegroundColor Gray
    exit 1
}

# Push tag
Write-Host "`n6. Pushing release tag v2.0.0..." -ForegroundColor Cyan
git push origin v2.0.0

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Tag pushed successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Tag push failed with error code: $LASTEXITCODE" -ForegroundColor Red
    exit 1
}

# Verify push
Write-Host "`n7. Verifying GitHub push..." -ForegroundColor Cyan
Write-Host "`nRecent commits on GitHub:" -ForegroundColor Cyan
git log origin/master --oneline -5

Write-Host "`nRelease tags on GitHub:" -ForegroundColor Cyan
git ls-remote --tags origin

Write-Host "`n============================================================" -ForegroundColor Green
Write-Host "✅ PUSH COMPLETE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

Write-Host "`nRepository URL: $GitHubURL" -ForegroundColor Green
Write-Host "Browse repository:" -ForegroundColor Cyan

# Extract GitHub web URL from git URL
$webURL = $GitHubURL -replace '\.git$', '' -replace 'https://', 'https://'
Write-Host $webURL -ForegroundColor Green

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "  1. Visit: $webURL" -ForegroundColor Gray
Write-Host "  2. Verify all files are present" -ForegroundColor Gray
Write-Host "  3. Check v2.0.0 release tag" -ForegroundColor Gray
Write-Host "  4. Create GitHub release (optional)" -ForegroundColor Gray
Write-Host "  5. Share repository link with team" -ForegroundColor Gray

Write-Host "`n" -ForegroundColor Green
