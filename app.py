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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM midias ORDER BY dateAdded DESC')
    rows = cursor.fetchall()
    
    midias = []
    for row in rows:
        midias.append({
            "id": row[0],
            "name": row[1],
            "uri": row[2],
            "mimeType": row[3],
            "cover": row[4],
            "isFavorite": bool(row[5]),
            "duration": row[6],
            "fileSize": row[7],
            "dateAdded": row[8],
            "lastAccessed": row[9],  # This should be lastAccessed
            "deviceId": row[10],
            "deviceName": row[11]
        })
    
    conn.close()
    return midias

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

@app.route('/test')
def test():
    """Rota de teste"""
    return jsonify({"status": "OK", "message": "API funcionando!"})

@app.route('/api/midias', methods=['GET'])
def get_midias():
    """Lista todas as mídias"""
    try:
        midias = get_all_midias()
        return jsonify(midias), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

if __name__ == '__main__':
    init_db()
    update_existing_media_uris()
    app.run(host='0.0.0.0', port=5003, debug=False)
