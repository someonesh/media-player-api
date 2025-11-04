# 🚀 Endpoints Rápidos - Sua API

## 🌐 **Sua API está em:**
**`https://media-player-api.onrender.com`**

---

## ⚡ Teste Rápido no Navegador

### 📄 **Página de Teste Interativa** (Recomendado!)
👉 **`https://media-player-api.onrender.com/test-page`**

### 🔍 **Endpoints Diretos:**

| Endpoint | Descrição |
|----------|-----------|
| `https://media-player-api.onrender.com/test` | Testa se API está funcionando |
| `https://media-player-api.onrender.com/api/midias` | Lista todas as mídias |
| `https://media-player-api.onrender.com/api/stats` | Estatísticas da BD |
| `https://media-player-api.onrender.com/api/db/info` | Informações da estrutura da BD |
| `https://media-player-api.onrender.com/api/midias/favorites` | Lista favoritos |
| `https://media-player-api.onrender.com/debug` | Debug - todas as mídias |

---

## 🧪 Teste com cURL

```bash
# Configurar URL
API_URL="https://media-player-api.onrender.com"

# Testar API
curl $API_URL/test

# Listar mídias
curl $API_URL/api/midias

# Estatísticas
curl $API_URL/api/stats

# Info da BD
curl $API_URL/api/db/info

# Favoritos
curl $API_URL/api/midias/favorites
```

---

## 📋 Todos os Endpoints

### GET (Consulta)
- ✅ `/test` - Testa API
- ✅ `/api/midias` - Lista todas
- ✅ `/api/midias/{id}` - Busca por ID
- ✅ `/api/midias/favorites` - Favoritos
- ✅ `/api/stats` - Estatísticas
- ✅ `/api/db/info` - Info da BD
- ✅ `/debug` - Debug
- ✅ `/test-page` - Página de teste

### POST (Criar)
- ➕ `/api/midias` - Adicionar mídia (JSON)
- ➕ `/api/midias/upload` - Upload arquivo
- ➕ `/api/midias/{id}/favorite` - Alternar favorito

### PUT (Atualizar)
- ✏️ `/api/midias/{id}` - Atualizar mídia

### DELETE (Remover)
- 🗑️ `/api/midias/{id}` - Deletar mídia

---

## 💡 Dica

**Use a página `/test-page`** - É a forma mais fácil de testar todos os endpoints!

Acesse: **`https://media-player-api.onrender.com/test-page`**

