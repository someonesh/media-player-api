from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import base64
import uuid

app = Flask(__name__)
CORS(app) 

DB_FILE = "midias.db"
MEDIA_FOLDER = "media"

# Create media folder if it doesn't exist
if not os.path.exists(MEDIA_FOLDER):
    os.makedirs(MEDIA_FOLDER)

# ============================================================
# FUNÇÕES DO BANCO DE DADOS
# ============================================================

def init_db():
    """Inicializa o banco de dados SQLite"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS midias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        uri TEXT NOT NULL,
        mimeType TEXT NOT NULL,
        cover TEXT,
        isFavorite INTEGER DEFAULT 0,
        duration INTEGER DEFAULT 0,
        fileSize INTEGER DEFAULT 0,
        dateAdded TEXT DEFAULT (datetime('now')),
        lastAccessed TEXT DEFAULT (datetime('now')),
        deviceId TEXT,
        deviceName TEXT
    )
''')
    
    conn.commit()
    conn.close()

def get_all_midias():
    """Busca todas as mídias"""
    try:
        # Garantir que o banco existe
        init_db()
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM midias ORDER BY dateAdded DESC')
        rows = cursor.fetchall()
        
        midias = []
        for row in rows:
            # Tratar casos onde a linha pode ter menos colunas
            midia = {
                "id": row[0] if len(row) > 0 else None,
                "name": row[1] if len(row) > 1 else "",
                "uri": row[2] if len(row) > 2 else "",
                "mimeType": row[3] if len(row) > 3 else "",
                "cover": row[4] if len(row) > 4 else None,
                "isFavorite": bool(row[5]) if len(row) > 5 else False,
                "duration": row[6] if len(row) > 6 else 0,
                "fileSize": row[7] if len(row) > 7 else 0,
                "dateAdded": row[8] if len(row) > 8 else None,
                "lastAccessed": row[9] if len(row) > 9 else None,
                "deviceId": row[10] if len(row) > 10 else None,
                "deviceName": row[11] if len(row) > 11 else None
            }
            midias.append(midia)
        
        conn.close()
        return midias
    except Exception as e:
        # Se houver erro, inicializar o banco e retornar lista vazia
        try:
            init_db()
            return []
        except:
            raise e

def add_midia(data):
    """Adiciona uma nova mídia"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO midias (name, uri, mimeType, cover, isFavorite, duration, fileSize, dateAdded, lastAccessed)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    ''', (
        data.get('name'),
        data.get('uri'),
        data.get('mimeType'),
        data.get('cover'),
        1 if data.get('isFavorite') else 0,
        data.get('duration', 0),
        data.get('fileSize', 0)
    ))
    
    midia_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return midia_id

def update_midia(midia_id, data):
    """Atualiza uma mídia"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE midias 
        SET name = ?, isFavorite = ?, lastAccessed = datetime('now')
        WHERE id = ?
    ''', (
        data.get('name'),
        1 if data.get('isFavorite') else 0,
        midia_id
    ))
    
    conn.commit()
    conn.close()

def delete_midia(midia_id):
    """Deleta uma mídia"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM midias WHERE id = ?', (midia_id,))
    
    conn.commit()
    conn.close()

# ============================================================
# ROTAS DA API
# ============================================================

@app.route('/')
def index():
    """Rota raiz - redireciona para página de teste"""
    return jsonify({
        "message": "API Mídia Player - Funcionando!",
        "endpoints": {
            "test": "/test",
            "test_page": "/test-page",
            "api_midias": "/api/midias",
            "stats": "/api/stats",
            "db_info": "/api/db/info",
            "favorites": "/api/midias/favorites"
        },
        "documentation": "Acesse /test-page para interface de teste"
    }), 200

@app.route('/test')
def test():
    """Rota de teste"""
    return jsonify({"status": "OK", "message": "API funcionando!"})

@app.route('/api/midias', methods=['GET'])
def get_midias():
    """Lista todas as mídias"""
    try:
        # Garantir que o banco está inicializado
        init_db()
        midias = get_all_midias()
        return jsonify(midias), 200
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return jsonify({
            "error": str(e),
            "details": error_details,
            "message": "Erro ao buscar mídias. Verifique se o banco de dados está configurado corretamente."
        }), 500

@app.route('/api/midias', methods=['POST'])
def create_midia():
    """Adiciona uma nova mídia"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Dados inválidos"}), 400
        
        if 'name' not in data or 'uri' not in data:
            return jsonify({"error": "Dados inválidos"}), 400
        
        midia_id = add_midia(data)
        
        new_midia = {
            "id": midia_id,
            "name": data.get('name'),
            "uri": data.get('uri'),
            "mimeType": data.get('mimeType'),
            "cover": data.get('cover'),
            "isFavorite": data.get('isFavorite', False),
            "duration": data.get('duration', 0),
            "fileSize": data.get('fileSize', 0),
            "dateAdded": datetime.now().isoformat()
        }
        
        return jsonify(new_midia), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/midias/<int:midia_id>', methods=['PUT'])
def update_midia_route(midia_id):
    """Atualiza uma mídia"""
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Dados inválidos"}), 400
        
        update_midia(midia_id, data)
        
        # Busca a mídia atualizada
        midias = get_all_midias()
        updated = next((m for m in midias if m['id'] == midia_id), None)
        
        if not updated:
            return jsonify({"error": "Mídia não encontrada"}), 404
        
        return jsonify(updated), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/midias/<int:midia_id>', methods=['DELETE'])
def delete_midia_route(midia_id):
    """Deleta uma mídia"""
    try:
        delete_midia(midia_id)
        return jsonify({"message": "Mídia removida"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/midias/<int:midia_id>/favorite', methods=['POST'])
def toggle_favorite(midia_id):
    """Marca/desmarca favorito"""
    try:
        # Busca a mídia atual
        midias = get_all_midias()
        midia = next((m for m in midias if m['id'] == midia_id), None)
        
        if not midia:
            return jsonify({"error": "Mídia não encontrada"}), 404
        
        # Inverte o status de favorito
        new_status = not midia['isFavorite']
        update_midia(midia_id, {'name': midia['name'], 'isFavorite': new_status})
        
        return jsonify({"isFavorite": new_status}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/midias/upload', methods=['POST'])
def upload_midia():
    """Upload de uma nova mídia"""
    try:
        # Get form data
        name = request.form.get('name')
        mimeType = request.form.get('mimeType')
        deviceId = request.form.get('deviceId')
        deviceName = request.form.get('deviceName')
        isFavorite = request.form.get('isFavorite', False)
        
        if not name or not mimeType:
            return jsonify({"error": "Dados inválidos"}), 400
        
        # Handle file upload
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "Nome de arquivo inválido"}), 400
            
        # Save file
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ''
        filename = str(uuid.uuid4()) + file_extension
        file_path = os.path.join(MEDIA_FOLDER, filename)
        file.save(file_path)
        
        # Save to database
        data = {
            'name': name,
            'uri': f"/api/midias/media/{filename}",
            'mimeType': mimeType,
            'deviceId': deviceId,
            'deviceName': deviceName,
            'isFavorite': isFavorite
        }
        
        midia_id = add_midia(data)
        
        new_midia = {
            "id": midia_id,
            "name": name,
            "uri": f"http://localhost:5003/api/midias/media/{filename}",
            "mimeType": mimeType,
            "deviceId": deviceId,
            "deviceName": deviceName,
            "isFavorite": isFavorite,
            "dateAdded": datetime.now().isoformat()
        }
        
        return jsonify(new_midia), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/midias/media/<filename>')
@app.route('/api/files/<filename>')
def serve_media(filename):
    """Servir arquivo de mídia"""
    try:
        return send_from_directory(MEDIA_FOLDER, filename)
    except Exception as e:
        return jsonify({"error": "Arquivo não encontrado"}), 404

@app.route('/debug')
def debug():
    """Debug route to check data"""
    midias = get_all_midias()
    return jsonify({
        "midias": midias,
        "count": len(midias)
    })

@app.route('/api/midias/<int:midia_id>', methods=['GET'])
def get_midia_by_id(midia_id):
    """Busca uma mídia específica por ID"""
    try:
        midias = get_all_midias()
        midia = next((m for m in midias if m['id'] == midia_id), None)
        
        if not midia:
            return jsonify({"error": "Mídia não encontrada"}), 404
        
        return jsonify(midia), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/midias/favorites', methods=['GET'])
def get_favorites():
    """Lista todas as mídias favoritas"""
    try:
        midias = get_all_midias()
        favorites = [m for m in midias if m['isFavorite']]
        return jsonify({
            "favorites": favorites,
            "count": len(favorites)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Retorna estatísticas da base de dados"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Total de mídias
        cursor.execute('SELECT COUNT(*) FROM midias')
        total = cursor.fetchone()[0]
        
        # Total de favoritos
        cursor.execute('SELECT COUNT(*) FROM midias WHERE isFavorite = 1')
        favorites = cursor.fetchone()[0]
        
        # Total por tipo de mídia
        cursor.execute('SELECT mimeType, COUNT(*) FROM midias GROUP BY mimeType')
        by_type = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Tamanho total dos arquivos
        cursor.execute('SELECT SUM(fileSize) FROM midias')
        total_size = cursor.fetchone()[0] or 0
        
        # Duração total
        cursor.execute('SELECT SUM(duration) FROM midias')
        total_duration = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return jsonify({
            "total_midias": total,
            "total_favorites": favorites,
            "by_mime_type": by_type,
            "total_file_size": total_size,
            "total_duration": total_duration,
            "total_duration_formatted": f"{total_duration // 60} minutos" if total_duration > 0 else "0 minutos"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/db/info', methods=['GET'])
def get_db_info():
    """Retorna informações sobre a estrutura da base de dados"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Informações da tabela
        cursor.execute("PRAGMA table_info(midias)")
        columns = cursor.fetchall()
        
        column_info = []
        for col in columns:
            column_info.append({
                "id": col[0],
                "name": col[1],
                "type": col[2],
                "not_null": bool(col[3]),
                "default_value": col[4],
                "primary_key": bool(col[5])
            })
        
        # Tamanho do arquivo da base de dados
        db_size = os.path.getsize(DB_FILE) if os.path.exists(DB_FILE) else 0
        
        conn.close()
        
        return jsonify({
            "table_name": "midias",
            "columns": column_info,
            "database_file": DB_FILE,
            "database_size_bytes": db_size,
            "database_size_formatted": f"{db_size / 1024:.2f} KB" if db_size > 0 else "0 KB"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test-page')
def test_page():
    """Página HTML para testar a API"""
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Teste da API - Mídia Player</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                text-align: center;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 30px;
            }
            .endpoints {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .endpoint-card {
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 20px;
                transition: all 0.3s;
            }
            .endpoint-card:hover {
                border-color: #667eea;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
            }
            .method {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                margin-right: 10px;
            }
            .method.get { background: #28a745; color: white; }
            .method.post { background: #007bff; color: white; }
            .method.put { background: #ffc107; color: black; }
            .method.delete { background: #dc3545; color: white; }
            .endpoint-path {
                font-family: 'Courier New', monospace;
                color: #495057;
                margin: 10px 0;
                word-break: break-all;
            }
            .description {
                color: #6c757d;
                font-size: 14px;
                margin-bottom: 15px;
            }
            button {
                background: #667eea;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
                transition: background 0.3s;
                width: 100%;
            }
            button:hover {
                background: #5568d3;
            }
            .response {
                margin-top: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 5px;
                border-left: 4px solid #667eea;
                max-height: 400px;
                overflow-y: auto;
            }
            .response pre {
                white-space: pre-wrap;
                word-wrap: break-word;
                font-size: 12px;
                color: #333;
            }
            .loading {
                color: #667eea;
                font-style: italic;
            }
            .error {
                color: #dc3545;
            }
            .success {
                color: #28a745;
            }
            .endpoint-list {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-top: 30px;
            }
            .endpoint-list h2 {
                color: #333;
                margin-bottom: 15px;
            }
            .endpoint-item {
                padding: 10px;
                margin: 5px 0;
                background: white;
                border-radius: 5px;
                border-left: 3px solid #667eea;
            }
            .api-config {
                background: #e7f3ff;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
                border: 2px solid #667eea;
            }
            .api-config h3 {
                color: #333;
                margin-bottom: 15px;
            }
            .api-input-group {
                display: flex;
                gap: 10px;
                margin-bottom: 10px;
            }
            .api-input-group input {
                flex: 1;
                padding: 10px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                font-family: 'Courier New', monospace;
            }
            .api-input-group input:focus {
                outline: none;
                border-color: #667eea;
            }
            .api-input-group button {
                padding: 10px 20px;
                width: auto;
            }
            .current-url {
                margin-top: 10px;
                padding: 10px;
                background: white;
                border-radius: 5px;
                font-size: 12px;
                color: #666;
            }
            .current-url strong {
                color: #333;
            }
            .url-examples {
                margin-top: 15px;
                padding: 10px;
                background: white;
                border-radius: 5px;
                font-size: 12px;
            }
            .url-examples code {
                display: block;
                margin: 5px 0;
                padding: 5px;
                background: #f8f9fa;
                border-radius: 3px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 Teste da API - Mídia Player</h1>
            <p class="subtitle">Teste todos os endpoints da sua API diretamente no navegador</p>
            
            <div class="api-config">
                <h3>⚙️ Configuração da API</h3>
                <div class="api-input-group">
                    <input type="text" id="api-url" placeholder="https://sua-api.onrender.com" />
                    <button onclick="setApiUrl()">Definir URL</button>
                </div>
                <div class="current-url">
                    <strong>URL Atual:</strong> <span id="current-url">Detectando automaticamente...</span>
                </div>
                <div class="url-examples">
                    <strong>Exemplos de URLs:</strong>
                    <code>https://sua-api.onrender.com</code>
                    <code>https://midia-player-api.onrender.com</code>
                    <code>http://localhost:5003</code>
                </div>
            </div>
            
            <div class="endpoints">
                <div class="endpoint-card">
                    <span class="method get">GET</span>
                    <div class="endpoint-path">/test</div>
                    <div class="description">Testa se a API está funcionando</div>
                    <button onclick="testEndpoint('/test', 'GET')">Testar</button>
                </div>
                
                <div class="endpoint-card">
                    <span class="method get">GET</span>
                    <div class="endpoint-path">/api/midias</div>
                    <div class="description">Lista todas as mídias</div>
                    <button onclick="testEndpoint('/api/midias', 'GET')">Testar</button>
                </div>
                
                <div class="endpoint-card">
                    <span class="method get">GET</span>
                    <div class="endpoint-path">/api/stats</div>
                    <div class="description">Estatísticas da base de dados</div>
                    <button onclick="testEndpoint('/api/stats', 'GET')">Testar</button>
                </div>
                
                <div class="endpoint-card">
                    <span class="method get">GET</span>
                    <div class="endpoint-path">/api/db/info</div>
                    <div class="description">Informações da estrutura da BD</div>
                    <button onclick="testEndpoint('/api/db/info', 'GET')">Testar</button>
                </div>
                
                <div class="endpoint-card">
                    <span class="method get">GET</span>
                    <div class="endpoint-path">/api/midias/favorites</div>
                    <div class="description">Lista mídias favoritas</div>
                    <button onclick="testEndpoint('/api/midias/favorites', 'GET')">Testar</button>
                </div>
                
                <div class="endpoint-card">
                    <span class="method get">GET</span>
                    <div class="endpoint-path">/debug</div>
                    <div class="description">Debug - ver todas as mídias</div>
                    <button onclick="testEndpoint('/debug', 'GET')">Testar</button>
                </div>
            </div>
            
            <div id="response" class="response" style="display: none;">
                <strong>Resposta:</strong>
                <pre id="response-content"></pre>
            </div>
            
            <div class="endpoint-list">
                <h2>📋 Lista Completa de Endpoints</h2>
                <div class="endpoint-item">
                    <strong>GET</strong> <code>/test</code> - Testa se a API está funcionando
                </div>
                <div class="endpoint-item">
                    <strong>GET</strong> <code>/api/midias</code> - Lista todas as mídias
                </div>
                <div class="endpoint-item">
                    <strong>GET</strong> <code>/api/midias/{id}</code> - Busca uma mídia por ID
                </div>
                <div class="endpoint-item">
                    <strong>GET</strong> <code>/api/midias/favorites</code> - Lista mídias favoritas
                </div>
                <div class="endpoint-item">
                    <strong>GET</strong> <code>/api/stats</code> - Estatísticas da base de dados
                </div>
                <div class="endpoint-item">
                    <strong>GET</strong> <code>/api/db/info</code> - Informações da estrutura da BD
                </div>
                <div class="endpoint-item">
                    <strong>GET</strong> <code>/debug</code> - Debug - ver todas as mídias
                </div>
                <div class="endpoint-item">
                    <strong>POST</strong> <code>/api/midias</code> - Adiciona uma nova mídia (JSON)
                </div>
                <div class="endpoint-item">
                    <strong>POST</strong> <code>/api/midias/upload</code> - Upload de arquivo de mídia
                </div>
                <div class="endpoint-item">
                    <strong>PUT</strong> <code>/api/midias/{id}</code> - Atualiza uma mídia
                </div>
                <div class="endpoint-item">
                    <strong>DELETE</strong> <code>/api/midias/{id}</code> - Remove uma mídia
                </div>
                <div class="endpoint-item">
                    <strong>POST</strong> <code>/api/midias/{id}/favorite</code> - Alterna favorito
                </div>
                <div class="endpoint-item">
                    <strong>GET</strong> <code>/api/midias/media/{filename}</code> - Serve arquivo de mídia
                </div>
            </div>
        </div>
        
        <script>
            let API_BASE = window.location.origin;
            
            // Carregar URL salva no localStorage ou usar a atual
            window.addEventListener('load', () => {
                const savedUrl = localStorage.getItem('api_url');
                if (savedUrl) {
                    API_BASE = savedUrl;
                    document.getElementById('api-url').value = savedUrl;
                }
                updateCurrentUrl();
                testEndpoint('/test', 'GET');
            });
            
            function setApiUrl() {
                const input = document.getElementById('api-url');
                let url = input.value.trim();
                
                // Remover barra final se existir
                if (url.endsWith('/')) {
                    url = url.slice(0, -1);
                }
                
                // Validar URL
                if (url && (url.startsWith('http://') || url.startsWith('https://'))) {
                    API_BASE = url;
                    localStorage.setItem('api_url', url);
                    updateCurrentUrl();
                    alert('URL da API atualizada com sucesso!');
                    // Testar a nova URL
                    testEndpoint('/test', 'GET');
                } else if (url) {
                    alert('Por favor, insira uma URL válida (deve começar com http:// ou https://)');
                } else {
                    // Se vazio, usar a URL atual
                    API_BASE = window.location.origin;
                    localStorage.removeItem('api_url');
                    updateCurrentUrl();
                    alert('Usando URL atual da página');
                    testEndpoint('/test', 'GET');
                }
            }
            
            function updateCurrentUrl() {
                document.getElementById('current-url').textContent = API_BASE;
            }
            
            // Permitir Enter no input
            document.addEventListener('DOMContentLoaded', () => {
                const input = document.getElementById('api-url');
                if (input) {
                    input.addEventListener('keypress', (e) => {
                        if (e.key === 'Enter') {
                            setApiUrl();
                        }
                    });
                }
            });
            
            async function testEndpoint(endpoint, method = 'GET') {
                const responseDiv = document.getElementById('response');
                const responseContent = document.getElementById('response-content');
                
                responseDiv.style.display = 'block';
                responseContent.innerHTML = '<span class="loading">Carregando...</span>';
                
                try {
                    const response = await fetch(API_BASE + endpoint, {
                        method: method,
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    
                    const data = await response.json();
                    
                    const statusClass = response.ok ? 'success' : 'error';
                    responseContent.innerHTML = `
                        <span class="${statusClass}"><strong>Status:</strong> ${response.status} ${response.statusText}</span>
                        <pre>${JSON.stringify(data, null, 2)}</pre>
                    `;
                } catch (error) {
                    responseContent.innerHTML = `
                        <span class="error"><strong>Erro:</strong> ${error.message}</span>
                    `;
                }
            }
            
        </script>
    </body>
    </html>
    """
    return html

def update_existing_media_uris():
    """Atualiza URIs de mídias existentes para o novo formato"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Update URIs that point to /api/files/ to use /api/midias/media/
    cursor.execute("""
        UPDATE midias 
        SET uri = REPLACE(uri, '/api/files/', '/api/midias/media/')
        WHERE uri LIKE '%/api/files/%'
    """)
    
    conn.commit()
    conn.close()

# ============================================================
# INICIALIZAÇÃO
# ============================================================

# Inicializar banco de dados quando o módulo carregar
# Isso funciona tanto para desenvolvimento quanto para produção (Gunicorn)
try:
    init_db()
    update_existing_media_uris()
    print("Banco de dados inicializado com sucesso!")
except Exception as e:
    print(f"Erro ao inicializar banco de dados: {e}")

if __name__ == '__main__':
    # Usa PORT do Render ou 5003 para localhost
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=False)
