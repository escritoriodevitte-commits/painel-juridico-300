# 🚀 DEPLOY EM NUVEM - PAINEL JURÍDICO

## OPÇÃO 1: RAILWAY (MAIS FÁCIL - RECOMENDADO)

### Passo 1: Acesse Railway
```
https://railway.app
```

### Passo 2: Conecte com GitHub
- Clique em "Deploy Now"
- Selecione "GitHub"
- Autorize Railway
- Selecione este repositório

### Passo 3: Pronto!
- Railway detecta Dockerfile automaticamente
- Faz deploy em 2 minutos
- URL pública gerada automaticamente

**URL fica assim:** `https://seu-projeto.railway.app`

---

## OPÇÃO 2: RENDER

### Passo 1: Acesse Render
```
https://render.com
```

### Passo 2: Novo Web Service
- Clique "New +"
- Selecione "Web Service"
- Conecte GitHub
- Selecione repositório

### Passo 3: Configure
- Build Command: `pip install -r requirements.txt`
- Start Command: `python main.py`
- Clique Deploy

---

## OPÇÃO 3: HEROKU

### Passo 1: Instale Heroku CLI
```
https://devcenter.heroku.com/articles/heroku-cli
```

### Passo 2: Login
```bash
heroku login
```

### Passo 3: Deploy
```bash
heroku create seu-app-name
git push heroku master
```

**URL fica assim:** `https://seu-app-name.herokuapp.com`

---

## OPÇÃO 4: GOOGLE CLOUD (COM CRÉDITO GRÁTIS)

### Passo 1: Acesse Google Cloud
```
https://cloud.google.com
```

### Passo 2: Cloud Run
- Ative Cloud Run API
- Deploy de container
- Conecte GitHub

### Passo 3: Configure
- Imagem: Dockerfile
- Porta: 5000
- Deploy

---

## COMANDOS GIT RÁPIDOS

```bash
# Primeiro commit
git add .
git commit -m "Deploy para nuvem"
git push origin master

# Heroku push
git push heroku master
```

---

## MONITORAMENTO

### Railway Dashboard
- Logs em tempo real
- Métricas de CPU/memória
- Restart automático

### Render Dashboard
- Logs completos
- Status de saúde
- Alertas

---

## VARIÁVEIS DE AMBIENTE

Se precisar adicionar variáveis (banco de dados, API keys):

### Railway
Settings → Environment → Adicionar variáveis

### Render
Environment → Adicionar variáveis

### Heroku
```bash
heroku config:set VARIAVEL=valor
```

---

## DOMÍNIO CUSTOMIZADO

### Railway
- Settings → Domains
- Adicionar domínio customizado

### Render
- Custom Domain
- Apontar DNS

---

## BANCO DE DADOS

Se precisar de banco de dados:

### PostgreSQL Gratuito
- Railway: Adicionar PostgreSQL (free tier)
- Render: Adicionar PostgreSQL
- Heroku: Heroku Postgres

### Conectar ao app
Variáveis de ambiente são criadas automaticamente

---

## CUSTO

- **Railway**: $5/mês (generoso)
- **Render**: Grátis (com limite)
- **Heroku**: Pago (eco dynos)
- **Google Cloud**: $300 crédito grátis

---

## ✅ APP ONLINE AGORA

Uma vez deployado, seu app está disponível 24/7:
- Acesse via URL pública
- Compartilhe com clientes
- Integre com sistema jurídico
- Monitore em tempo real

---

Escolha uma opção acima e siga os passos. Seu app estará online em minutos!
