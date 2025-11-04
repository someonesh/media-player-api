# 📋 Endpoints da API - Mídia Player

## 🚀 Como Testar

### 🌐 **Testando no Render (Recomendado)**

**Sua API:** `https://media-player-api.onrender.com`

#### Opção 1: Página de Teste Interativa
1. Acesse: **`https://media-player-api.onrender.com/test-page`**
2. A página detecta automaticamente a URL do Render
3. Clique nos botões para testar cada endpoint

#### Opção 2: Testar Endpoints Diretamente no Navegador
Acesse qualquer endpoint GET diretamente:
- **`https://media-player-api.onrender.com/test`**
- **`https://media-player-api.onrender.com/api/midias`**
- **`https://media-player-api.onrender.com/api/stats`**
- **`https://media-player-api.onrender.com/api/db/info`**
- **`https://media-player-api.onrender.com/api/midias/favorites`**
- **`https://media-player-api.onrender.com/debug`**

### 💻 **Testando Localmente (Localhost)**

Se estiver testando localmente:
- Página de teste: `http://localhost:5003/test-page`
- Endpoints: `http://localhost:5003/test`, `http://localhost:5003/api/midias`, etc.

---

## 📍 Endpoints Disponíveis

### 🔍 **GET - Consultar Dados**

#### 1. Testar API
```
GET /test
```
**Descrição:** Testa se a API está funcionando  
**Resposta:**
```json
{
  "status": "OK",
  "message": "API funcionando!"
}
```

#### 2. Listar Todas as Mídias
```
GET /api/midias
```
**Descrição:** Retorna todas as mídias cadastradas  
**Resposta:**
```json
[
  {
    "id": 1,
    "name": "Música Exemplo",
    "uri": "/api/midias/media/arquivo.mp3",
    "mimeType": "audio/mpeg",
    "cover": null,
    "isFavorite": false,
    "duration": 180,
    "fileSize": 5242880,
    "dateAdded": "2024-01-01 12:00:00",
    "lastAccessed": "2024-01-01 12:00:00",
    "deviceId": null,
    "deviceName": null
  }
]
```

#### 3. Buscar Mídia por ID
```
GET /api/midias/{id}
```
**Descrição:** Retorna uma mídia específica pelo ID  
**Exemplo:** `GET /api/midias/1`

#### 4. Listar Favoritos
```
GET /api/midias/favorites
```
**Descrição:** Retorna todas as mídias marcadas como favoritas  
**Resposta:**
```json
{
  "favorites": [...],
  "count": 5
}
```

#### 5. Estatísticas da Base de Dados
```
GET /api/stats
```
**Descrição:** Retorna estatísticas gerais da base de dados  
**Resposta:**
```json
{
  "total_midias": 50,
  "total_favorites": 10,
  "by_mime_type": {
    "audio/mpeg": 30,
    "audio/m4a": 15,
    "video/mp4": 5
  },
  "total_file_size": 524288000,
  "total_duration": 3600,
  "total_duration_formatted": "60 minutos"
}
```

#### 6. Informações da Estrutura da BD
```
GET /api/db/info
```
**Descrição:** Retorna informações sobre a estrutura da tabela  
**Resposta:**
```json
{
  "table_name": "midias",
  "columns": [
    {
      "id": 0,
      "name": "id",
      "type": "INTEGER",
      "not_null": false,
      "default_value": null,
      "primary_key": true
    },
    ...
  ],
  "database_file": "midias.db",
  "database_size_bytes": 1048576,
  "database_size_formatted": "1024.00 KB"
}
```

#### 7. Debug - Ver Todas as Mídias
```
GET /debug
```
**Descrição:** Endpoint de debug para ver todas as mídias com contador  
**Resposta:**
```json
{
  "midias": [...],
  "count": 50
}
```

#### 8. Servir Arquivo de Mídia
```
GET /api/midias/media/{filename}
GET /api/files/{filename}
```
**Descrição:** Serve arquivos de mídia armazenados  
**Exemplo:** `GET /api/midias/media/07c29c24-af1b-4c3e-86b9-1c29118b4c0e.mp3`

---

### ➕ **POST - Criar/Adicionar Dados**

#### 9. Adicionar Nova Mídia (JSON)
```
POST /api/midias
Content-Type: application/json
```
**Body:**
```json
{
  "name": "Nova Música",
  "uri": "/api/midias/media/arquivo.mp3",
  "mimeType": "audio/mpeg",
  "cover": null,
  "isFavorite": false,
  "duration": 180,
  "fileSize": 5242880
}
```
**Resposta:** Retorna a mídia criada com ID

#### 10. Upload de Arquivo de Mídia
```
POST /api/midias/upload
Content-Type: multipart/form-data
```
**Form Data:**
- `file`: Arquivo de mídia
- `name`: Nome da mídia
- `mimeType`: Tipo MIME (ex: "audio/mpeg")
- `deviceId`: (opcional) ID do dispositivo
- `deviceName`: (opcional) Nome do dispositivo
- `isFavorite`: (opcional) true/false

**Resposta:** Retorna a mídia criada com URI

#### 11. Alternar Favorito
```
POST /api/midias/{id}/favorite
```
**Descrição:** Alterna o status de favorito de uma mídia  
**Exemplo:** `POST /api/midias/1/favorite`  
**Resposta:**
```json
{
  "isFavorite": true
}
```

---

### ✏️ **PUT - Atualizar Dados**

#### 12. Atualizar Mídia
```
PUT /api/midias/{id}
Content-Type: application/json
```
**Body:**
```json
{
  "name": "Nome Atualizado",
  "isFavorite": true
}
```
**Exemplo:** `PUT /api/midias/1`  
**Resposta:** Retorna a mídia atualizada

---

### 🗑️ **DELETE - Remover Dados**

#### 13. Deletar Mídia
```
DELETE /api/midias/{id}
```
**Descrição:** Remove uma mídia da base de dados  
**Exemplo:** `DELETE /api/midias/1`  
**Resposta:**
```json
{
  "message": "Mídia removida"
}
```

---

## 🧪 Exemplos de Teste

### 🌐 **Testando no Render:**

#### No Navegador:
1. Acesse: `https://media-player-api.onrender.com/test`
2. Você verá a resposta JSON diretamente

#### Com cURL (Terminal):

```bash
# URL da sua API
API_URL="https://media-player-api.onrender.com"

# Testar API
curl $API_URL/test

# Listar mídias
curl $API_URL/api/midias

# Estatísticas
curl $API_URL/api/stats

# Informações da BD
curl $API_URL/api/db/info

# Buscar mídia por ID
curl $API_URL/api/midias/1

# Listar favoritos
curl $API_URL/api/midias/favorites
```

#### Testar com POST (cURL):

```bash
API_URL="https://media-player-api.onrender.com"

# Adicionar mídia
curl -X POST $API_URL/api/midias \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Teste",
    "uri": "/api/midias/media/teste.mp3",
    "mimeType": "audio/mpeg"
  }'

# Alternar favorito
curl -X POST $API_URL/api/midias/1/favorite
```

### 💻 **Testando Localmente:**

```bash
# Testar API
curl http://localhost:5003/test

# Listar mídias
curl http://localhost:5003/api/midias

# Estatísticas
curl http://localhost:5003/api/stats

# Informações da BD
curl http://localhost:5003/api/db/info
```

---

## 📝 Notas

- **Base URL (Render):** `https://media-player-api.onrender.com`
- **Base URL (Local):** `http://localhost:5003`
- **CORS:** Habilitado para todas as origens
- **Formato de Resposta:** JSON
- **Base de Dados:** SQLite (`midias.db`)
- **Pasta de Mídias:** `media/`

---

## 🎯 Página de Teste Interativa

### 🌐 **No Render:**
Acesse **`https://media-player-api.onrender.com/test-page`** para uma interface gráfica que permite:
- Configurar a URL da API manualmente
- Testar todos os endpoints com botões
- Ver respostas formatadas em JSON
- Funciona automaticamente detectando a URL atual

### 💻 **Localmente:**
Acesse `http://localhost:5003/test-page` para a mesma interface de teste local.

