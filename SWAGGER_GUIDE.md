# 📚 Guia do Swagger/OpenAPI

## 🎯 Como Acessar

### 🌐 **No Render:**
Acesse: **`https://media-player-api.onrender.com/docs`**

### 💻 **Localmente:**
Acesse: **`http://localhost:5003/docs`**

---

## 📖 O que é Swagger?

Swagger é uma interface interativa para testar e documentar sua API. Você pode:

- ✅ Ver todos os endpoints disponíveis
- ✅ Testar GET, POST, PUT, DELETE diretamente no navegador
- ✅ Ver exemplos de requisições e respostas
- ✅ Testar endpoints com dados reais

---

## 🚀 Como Usar

### 1. **Acessar a Documentação**
1. Abra o navegador
2. Acesse `https://media-player-api.onrender.com/docs`
3. Você verá a interface Swagger UI

### 2. **Testar um Endpoint GET**
1. Encontre o endpoint desejado (ex: `GET /api/midias`)
2. Clique em **"Try it out"**
3. Clique em **"Execute"**
4. Veja a resposta abaixo

### 3. **Testar um Endpoint POST**
1. Encontre o endpoint (ex: `POST /api/midias`)
2. Clique em **"Try it out"**
3. Preencha o body com JSON (exemplo já está preenchido)
4. Clique em **"Execute"**
5. Veja a resposta

---

## 📋 Endpoints Documentados

### ✅ GET Endpoints
- `/test` - Testa se API está funcionando
- `/api/midias` - Lista todas as mídias
- `/api/stats` - Estatísticas da BD

### ✅ POST Endpoints
- `/api/midias` - Adiciona nova mídia

---

## 💡 Exemplo de Uso

### Testar GET /api/midias
1. Acesse `/docs`
2. Expanda `GET /api/midias`
3. Clique em **"Try it out"**
4. Clique em **"Execute"**
5. Veja a lista de mídias na resposta

### Testar POST /api/midias
1. Acesse `/docs`
2. Expanda `POST /api/midias`
3. Clique em **"Try it out"**
4. Modifique o JSON no body:
```json
{
  "name": "Minha Música",
  "uri": "/api/midias/media/teste.mp3",
  "mimeType": "audio/mpeg",
  "isFavorite": false,
  "duration": 180,
  "fileSize": 5242880
}
```
5. Clique em **"Execute"**
6. Veja a mídia criada na resposta

---

## 🔧 Troubleshooting

### Swagger não carrega?
- Verifique se o servidor está rodando
- Verifique se o endpoint `/docs` está acessível
- Verifique os logs do servidor

### Erro ao testar POST?
- Verifique se todos os campos obrigatórios estão preenchidos
- Verifique o formato JSON
- Verifique se a API está funcionando (`/test`)

---

## 📝 Notas

- O Swagger gera automaticamente a documentação baseada nos docstrings dos endpoints
- Você pode testar todos os métodos HTTP (GET, POST, PUT, DELETE)
- As respostas mostram exemplos reais de dados

---

## 🎯 Links Úteis

- **Swagger UI:** `/docs`
- **Página de Teste:** `/test-page`
- **Teste Simples:** `/test`
- **API Base:** `/api/midias`

