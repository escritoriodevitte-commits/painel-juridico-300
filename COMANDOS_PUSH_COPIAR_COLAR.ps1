# ============================================================
# PAINEL JURÍDICO v2 - COMANDOS DE PUSH PRONTOS
# ============================================================
# INSTRUÇÕES:
# 1. Copie os comandos abaixo
# 2. Substitua "SEU-USUARIO" pelo seu usuário GitHub
# 3. Cole cada comando no PowerShell e aperte Enter
# ============================================================

# PASSO 1: Navegar até o projeto
cd "C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2"

# PASSO 2: Configurar remote (SUBSTITUA SEU-USUARIO)
git remote add origin https://github.com/SEU-USUARIO/painel-juridico-v2.git

# PASSO 3: Verificar se remote foi configurado
git remote -v

# PASSO 4: Fazer push dos commits
# Quando pedir credenciais: Cole seu token pessoal (gerado em https://github.com/settings/tokens)
git push -u origin master

# PASSO 5: Fazer push da tag de release
git push origin v2.0.0

# PASSO 6: Verificar se o push foi bem-sucedido
git log origin/master --oneline -5
git ls-remote --tags origin

# ============================================================
# SE RECEBER ERRO "remote origin already exists":
# git remote remove origin
# git remote add origin https://github.com/SEU-USUARIO/painel-juridico-v2.git
# ============================================================

# ============================================================
# APÓS COMPLETAR O PUSH:
# 1. Visite: https://github.com/SEU-USUARIO/painel-juridico-v2
# 2. Verifique se 10 commits aparecem
# 3. Verifique se tag v2.0.0 existe
# 4. Verifique se todos os arquivos estão presentes
# ============================================================
