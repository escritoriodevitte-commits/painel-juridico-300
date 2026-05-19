# ============================================
# CRIAR REPOSITÓRIO GITHUB E FAZER DEPLOY
# ============================================
# Cole seu token GitHub abaixo (gerado em https://github.com/settings/tokens)
# Depois execute este script

$GITHUB_TOKEN = "PASTE_YOUR_TOKEN_HERE"
$GITHUB_USER = "SEU_USUARIO_AQUI"

if ($GITHUB_TOKEN -eq "PASTE_YOUR_TOKEN_HERE") {
    Write-Host "❌ Configure GITHUB_TOKEN primeiro!" -ForegroundColor Red
    Write-Host ""
    Write-Host "1. Acesse: https://github.com/settings/tokens/new" -ForegroundColor Yellow
    Write-Host "2. Selecione 'repo' (acesso completo)" -ForegroundColor Yellow
    Write-Host "3. Clique 'Generate token'" -ForegroundColor Yellow
    Write-Host "4. Copie o token" -ForegroundColor Yellow
    Write-Host "5. Cole no script acima onde diz PASTE_YOUR_TOKEN_HERE" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Seu usuário GitHub está em: https://github.com/SEU_USUARIO" -ForegroundColor Cyan
    exit 1
}

Write-Host "🚀 CRIANDO REPOSITÓRIO E FAZENDO DEPLOY" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# 1. Criar repositório
Write-Host "1️⃣ Criando repositório no GitHub..." -ForegroundColor Yellow
$body = @{
    name = "painel-juridico"
    description = "Painel Estratégico Jurídico - Web App com IA"
    private = $false
    auto_init = $false
} | ConvertTo-Json

$response = Invoke-WebRequest -Uri "https://api.github.com/user/repos" `
    -Headers @{Authorization = "token $GITHUB_TOKEN"} `
    -ContentType "application/json" `
    -Method POST `
    -Body $body 2>&1

if ($response.StatusCode -eq 201) {
    Write-Host "✅ Repositório criado!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Repositório pode já existir, continuando..." -ForegroundColor Yellow
}
Write-Host ""

# 2. Configurar Git
Write-Host "2️⃣ Configurando Git..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin "https://github.com/$GITHUB_USER/painel-juridico.git"
git branch -M main
Write-Host "✅ Git configurado!" -ForegroundColor Green
Write-Host ""

# 3. Fazer push
Write-Host "3️⃣ Enviando código para GitHub..." -ForegroundColor Yellow
git push -u origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao fazer push" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Código enviado!" -ForegroundColor Green
Write-Host ""

# 4. Deploy no Railway
Write-Host "4️⃣ PRÓXIMO PASSO - RAILWAY DEPLOY" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Acesse: https://railway.app" -ForegroundColor White
Write-Host "2. Clique em 'New Project'" -ForegroundColor White
Write-Host "3. Selecione 'Deploy from GitHub'" -ForegroundColor White
Write-Host "4. Autorize Railway com GitHub" -ForegroundColor White
Write-Host "5. Selecione: $GITHUB_USER/painel-juridico" -ForegroundColor White
Write-Host "6. Railway detecta Dockerfile automaticamente" -ForegroundColor White
Write-Host "7. Clique Deploy" -ForegroundColor White
Write-Host ""
Write-Host "✅ APP ESTARÁ ONLINE EM 2-3 MINUTOS!" -ForegroundColor Green
Write-Host ""
Write-Host "URL será: https://seu-projeto.up.railway.app" -ForegroundColor Cyan
Write-Host ""
