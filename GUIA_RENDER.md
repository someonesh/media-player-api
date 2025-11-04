# 🚀 Guia Rápido - Testar API no Render

## 🎯 **Sua API está em:**
**`https://media-player-api.onrender.com`**

---

## 📍 Passos para Testar

### 1️⃣ **URL da sua API**
Sua API está hospedada em: `https://media-player-api.onrender.com`

### 2️⃣ **Teste Diretamente no Navegador**

Acesse qualquer um destes endpoints no navegador:

```
https://media-player-api.onrender.com/test
https://media-player-api.onrender.com/api/midias
https://media-player-api.onrender.com/api/stats
https://media-player-api.onrender.com/api/db/info
https://media-player-api.onrender.com/api/midias/favorites
https://media-player-api.onrender.com/debug
```

### 3️⃣ **Use a Página de Teste Interativa** (Recomendado!)

1. Acesse: **`https://media-player-api.onrender.com/test-page`**
2. A página detecta automaticamente a URL do Render
3. Se necessário, você pode configurar manualmente no campo de configuração
4. Clique nos botões para testar cada endpoint
5. Veja as respostas JSON formatadas

### 4️⃣ **Teste com cURL (Terminal)**

```bash
# URL da sua API
API_URL="https://media-player-api.onrender.com"

# Testar se está funcionando
curl $API_URL/test

# Listar todas as mídias
curl $API_URL/api/midias

# Ver estatísticas
curl $API_URL/api/stats

# Ver informações da base de dados
curl $API_URL/api/db/info
```

---

## ✅ Endpoints Disponíveis para Teste

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/test` | Testa se API está funcionando |
| GET | `/api/midias` | Lista todas as mídias |
| GET | `/api/midias/{id}` | Busca mídia por ID |
| GET | `/api/midias/favorites` | Lista favoritos |
| GET | `/api/stats` | Estatísticas da BD |
| GET | `/api/db/info` | Informações da estrutura da BD |
| GET | `/debug` | Debug - ver todas as mídias |
| GET | `/test-page` | **Página de teste interativa** |

---

## 🎯 Exemplo Prático

Sua API: `https://media-player-api.onrender.com`

### Teste no Navegador:
1. Abra: **`https://media-player-api.onrender.com/test-page`**
2. Clique em "Testar" em qualquer endpoint
3. Veja a resposta JSON abaixo

### Teste Direto:
- **`https://media-player-api.onrender.com/test`**
- **`https://media-player-api.onrender.com/api/midias`**
- **`https://media-player-api.onrender.com/api/stats`**
- **`https://media-player-api.onrender.com/api/db/info`**
- **`https://media-player-api.onrender.com/api/midias/favorites`**

---

## 💡 Dicas

1. **Use a página `/test-page`** - É a forma mais fácil de testar todos os endpoints
2. **A URL é salva automaticamente** - A página lembra a URL que você configurou
3. **Teste no navegador primeiro** - É mais rápido e visual
4. **Use cURL para testes avançados** - Para POST, PUT, DELETE

---

## ❓ Problemas Comuns

### "Cannot GET /"
- Verifique se a URL está correta
- Certifique-se de que o serviço está rodando no Render

### "Connection refused"
- O serviço pode estar dormindo (plano gratuito)
- Aguarde alguns segundos ou faça upgrade

### CORS Error
- CORS já está habilitado na API
- Se ainda assim der erro, verifique se está usando HTTPS

---

## 📚 Documentação Completa

Veja `ENDPOINTS.md` para a documentação completa de todos os endpoints!

