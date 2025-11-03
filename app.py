from flask import Flask, jsonify, request
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
CORS(app) 

DB_FILE = "midias.db"

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
        numeroDias TEXT DEFAULT (datetime('now'))          
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
        # Calculate days since added
        date_added = row[8]
        if date_added:
            try:
                # Parse the date and calculate days
                from datetime import datetime
                date_obj = datetime.fromisoformat(date_added.replace('Z', '+00:00'))
                days_diff = (datetime.now() - date_obj).days
                numero_dias = str(days_diff)
            except:
                # Fallback if date parsing fails
                numero_dias = "0"
        else:
            numero_dias = "0"
            
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
            "numeroDias": numero_dias,
        })
    
    conn.close()
    return midias

def add_midia(data):
    """Adiciona uma nova mídia"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO midias (name, uri, mimeType, cover, isFavorite, duration, fileSize)
        VALUES (?, ?, ?, ?, ?, ?, ?)
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
        SET name = ?, isFavorite = ?
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

# ============================================================
# INICIALIZAÇÃO
# ============================================================

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5003, debug=False)
