# Deploy Automático para Railway
# Copie e execute este script no PowerShell

Write-Host "🚀 DEPLOY AUTOMÁTICO - PAINEL JURÍDICO" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Git
Write-Host "1️⃣ Verificando Git..." -ForegroundColor Yellow
git --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git não encontrado! Instale em: https://git-scm.com/" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Git OK`n" -ForegroundColor Green

# 2. Adicionar arquivos
Write-Host "2️⃣ Adicionando arquivos..." -ForegroundColor Yellow
git add .
git status
Write-Host "✅ Arquivos adicionados`n" -ForegroundColor Green

# 3. Commit
Write-Host "3️⃣ Fazendo commit..." -ForegroundColor Yellow
git commit -m "Deploy automático para nuvem - Dockerfile, Railway, Render, Heroku"
Write-Host "✅ Commit feito`n" -ForegroundColor Green

# 4. Push
Write-Host "4️⃣ Enviando para GitHub..." -ForegroundColor Yellow
git push origin master
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao fazer push. Verifique suas credenciais." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Push concluído`n" -ForegroundColor Green

# 5. Instruções Railway
Write-Host "5️⃣ PRÓXIMO PASSO - RAILWAY:" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Acesse: https://railway.app" -ForegroundColor White
Write-Host "2. Faça login com GitHub" -ForegroundColor White
Write-Host "3. Clique em 'New Project'" -ForegroundColor White
Write-Host "4. Selecione 'Deploy from GitHub'" -ForegroundColor White
Write-Host "5. Selecione este repositório" -ForegroundColor White
Write-Host "6. Railway fará deploy automático" -ForegroundColor White
Write-Host ""
Write-Host "Seu app ficará online em: https://seu-projeto.up.railway.app" -ForegroundColor Green
Write-Host ""

Write-Host "✅ TUDO PRONTO!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
