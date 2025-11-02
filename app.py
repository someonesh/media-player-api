from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app) 

# Use absolute path for database file
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "midias.db")
# Use absolute path for upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac', 'mp4', 'mov', 'mkv', 'avi', 'webm'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================================
# FUNÇÕES DO BANCO DE DADOS
# ============================================================

def init_db():
    """Inicializa o banco de dados SQLite"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create table only if it doesn't exist
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
            "numeroDias": row[9],
        })
    
    conn.close()
    return midias

def add_midia(data):
    """Adiciona uma nova mídia"""
    print("Adding media with data:", data)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Print the exact SQL query we're executing
        sql_query = '''
            INSERT INTO midias (name, uri, mimeType, cover, isFavorite, duration, fileSize, dateAdded, numeroDias)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        '''
        print("SQL Query:", sql_query)
        params = (
            data.get('name'),
            data.get('uri'),
            data.get('mimeType'),
            data.get('cover'),
            1 if data.get('isFavorite') else 0,
            data.get('duration', 0),
            data.get('fileSize', 0)
        )
        print("Parameters:", params)
        
        cursor.execute(sql_query, params)
        
        midia_id = cursor.lastrowid
        print("Media ID generated:", midia_id)
        conn.commit()
        conn.close()
        
        print("Media added successfully with ID:", midia_id)
        return midia_id
    except Exception as e:
        conn.close()
        print("Error adding media:", str(e))
        import traceback
        traceback.print_exc()
        raise

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
    
    # First get the media to check if it's a server file
    cursor.execute('SELECT uri FROM midias WHERE id = ?', (midia_id,))
    row = cursor.fetchone()
    
    if row:
        uri = row[0]
        # If it's a server file, delete the actual file
        if uri.startswith('/api/files/'):
            filename = uri.split('/')[-1]
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
    
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

@app.route('/test-debug', methods=['POST'])
def test_debug():
    """Test route for debugging"""
    print("Test debug route called")
    print("Request data:", request.data)
    print("Request form:", request.form)
    print("Request JSON:", request.json)
    return jsonify({"message": "Debug route working"}), 200

# New route to serve uploaded files
@app.route('/api/files/<filename>')
def serve_file(filename):
    """Serve uploaded files"""
    try:
        print(f"Attempting to serve file: {filename}")
        print(f"Upload folder path: {app.config['UPLOAD_FOLDER']}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"Full file path: {filepath}")
        
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"File not found at path: {filepath}")
            return jsonify({"error": "File not found"}), 404
            
        print(f"File found, serving: {filepath}")
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError as e:
        print(f"FileNotFoundError when serving {filename}: {str(e)}")
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        print(f"Error serving file {filename}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Error serving file: {str(e)}"}), 500

# New route to upload files
@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a new media file"""
    try:
        print("Received upload request")
        print("Files in request:", list(request.files.keys()) if request.files else "No files")
        print("Form data:", dict(request.form) if request.form else "No form data")
        print(f"Upload folder path: {app.config['UPLOAD_FOLDER']}")
        
        # Handle both web and React Native file uploads
        if 'file' not in request.files:
            # For React Native, the file might be in request.data or as form data
            if not request.files:
                return jsonify({"error": "No file provided"}), 400
            
        # Try to get file from request.files first (web)
        file = None
        if 'file' in request.files:
            file = request.files['file']
            print("Got file from 'file' key")
        else:
            # For React Native, we might need to handle it differently
            # Check if there's any file-like data in the request
            for key in request.files:
                file = request.files[key]
                print(f"Got file from '{key}' key")
                break
            
        if not file:
            return jsonify({"error": "No file provided"}), 400
            
        if file.filename == '':
            # Generate a filename if none provided
            file.filename = f"uploaded_file_{int(datetime.now().timestamp())}.mp3"
            print("Generated filename:", file.filename)

        print("File filename:", file.filename)
        print("File content type:", file.content_type if hasattr(file, 'content_type') else 'Unknown')

        if file and (allowed_file(file.filename or '') or file.filename):
            # Generate unique filename
            if file.filename and '.' in file.filename:
                extension = file.filename.rsplit('.', 1)[1].lower()
            else:
                # Try to guess extension from MIME type
                mimetype = file.content_type if hasattr(file, 'content_type') else ''
                print("MIME type:", mimetype)
                if 'mpeg' in mimetype or 'mp3' in mimetype:
                    extension = 'mp3'
                elif 'mp4' in mimetype:
                    extension = 'mp4'
                elif 'm4a' in mimetype or 'm4v' in mimetype:
                    extension = 'm4a' if 'audio' in mimetype else 'mp4'
                elif 'wav' in mimetype:
                    extension = 'wav'
                elif 'ogg' in mimetype or 'ogv' in mimetype:
                    extension = 'ogg' if 'audio' in mimetype else 'ogv'
                elif 'mov' in mimetype:
                    extension = 'mov'
                elif 'avi' in mimetype:
                    extension = 'avi'
                elif 'webm' in mimetype:
                    extension = 'webm'
                else:
                    # Default to mp4 for video or mp3 for audio
                    extension = 'mp4' if 'video' in mimetype else 'mp3'
            
            filename = f"{uuid.uuid4()}.{extension}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print("Saving file to:", filepath)
            
            # Ensure upload directory exists
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
                print("Created upload directory")
            
            try:
                file.save(filepath)
                print("File saved successfully")
            except Exception as save_error:
                print("Error saving file:", str(save_error))
                import traceback
                traceback.print_exc()
                return jsonify({"error": f"Failed to save file: {str(save_error)}"}), 500
            
            # Get file info
            try:
                file_size = os.path.getsize(filepath)
                print("File size:", file_size)
            except Exception as size_error:
                print("Error getting file size:", str(size_error))
                file_size = 0
            
            # Determine MIME type based on extension
            mime_type = 'video/mp4'  # default for video
            if extension in ['mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac']:
                mime_type = f'audio/{extension}' if extension != 'm4a' else 'audio/mp4'
            elif extension in ['mp4', 'mov', 'mkv', 'avi', 'webm']:
                mime_type = f'video/{extension}' if extension != 'mp4' else 'video/mp4'
            
            return jsonify({
                "filename": filename,
                "filepath": f"/api/files/{filename}",
                "filesize": file_size,
                "mimetype": mime_type
            }), 201
            
        return jsonify({"error": "File type not allowed"}), 400
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Upload error: {str(e)}")
        print(f"Error details: {error_details}")
        return jsonify({"error": f"Upload failed: {str(e)}", "details": error_details}), 500

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
        print("=== NEW REQUEST ===")
        print("Received request data:", request.data)
        print("Received form data:", request.form)
        print("Received JSON:", request.json)
        print("Content-Type:", request.headers.get('Content-Type'))
        
        # Handle both JSON and form data
        data = request.json
        if not data:
            # Try to get data from form
            if request.form:
                data = {}
                for key in request.form:
                    data[key] = request.form[key]
                print("Using form data:", data)
            else:
                print("No JSON or form data received")
                return jsonify({"error": "Dados inválidos - nenhum dado recebido"}), 400
        
        if 'name' not in data or 'uri' not in data:
            print("Missing required fields")
            print("Available fields:", list(data.keys()) if data else "No data")
            return jsonify({"error": "Dados inválidos - campos obrigatórios: name, uri"}), 400
        
        print("Creating media with data:", data)
        
        # Check if data contains unexpected fields
        expected_fields = {'name', 'uri', 'mimeType', 'cover', 'isFavorite', 'duration', 'fileSize'}
        unexpected_fields = set(data.keys()) - expected_fields
        if unexpected_fields:
            print(f"Unexpected fields in data: {unexpected_fields}")
            # Remove unexpected fields
            for field in unexpected_fields:
                data.pop(field, None)
        
        # Add debugging for each field
        print("Data fields:")
        for key, value in data.items():
            print(f"  {key}: {value} (type: {type(value)})")
        
        # Ensure mimeType is set properly
        if 'mimeType' not in data or not data['mimeType']:
            # Try to determine MIME type from file extension
            uri = data.get('uri', '')
            if uri:
                if any(ext in uri.lower() for ext in ['.mp4', '.mov', '.mkv', '.avi', '.webm']):
                    data['mimeType'] = 'video/mp4'  # default video MIME type
                elif any(ext in uri.lower() for ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac']):
                    data['mimeType'] = 'audio/mpeg'  # default audio MIME type
                else:
                    data['mimeType'] = 'audio/mpeg'  # default to audio
        
        # Use the add_midia function to insert data
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
        
        print("Created media:", new_midia)
        response_data = jsonify(new_midia)
        print("Sending response:", response_data)
        return response_data, 201
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error creating media: {str(e)}")
        print(f"Error details: {error_details}")
        return jsonify({"error": str(e), "details": error_details}), 500

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
        print(f"Error deleting media: {str(e)}")
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

# Let's add a global exception handler to catch any errors
import sys
import traceback

def custom_exception_handler(exc_type, exc_value, exc_traceback):
    print("=== GLOBAL EXCEPTION HANDLER ===")
    print(f"Exception type: {exc_type}")
    print(f"Exception value: {exc_value}")
    print("Traceback:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = custom_exception_handler

# Let's also add a middleware to log all requests
@app.before_request
def log_request_info():
    print("=== INCOMING REQUEST ===")
    print(f"Request URL: {request.url}")
    print(f"Request method: {request.method}")
    print(f"Request headers: {dict(request.headers)}")
    print(f"Request data: {request.data}")
    print(f"Request form: {request.form}")
    # Only try to parse JSON if the content type is JSON
    if request.headers.get('Content-Type') == 'application/json':
        print(f"Request JSON: {request.json}")
    else:
        print("Request JSON: Not a JSON request")

# Let's also add a middleware to log all responses
@app.after_request
def log_response_info(response):
    print("=== OUTGOING RESPONSE ===")
    print(f"Response status: {response.status}")
    print(f"Response headers: {dict(response.headers)}")
    # Don't try to get response data for file responses as it can cause errors
    if not response.headers.get('Content-Type', '').startswith('audio/'):
        try:
            print(f"Response data: {response.get_data()}")
        except Exception as e:
            print(f"Could not log response data: {e}")
    else:
        print("Response data: [File data - not logged]")
    return response

# Let's add a test function to see if we can insert data directly
def test_database_insertion():
    print("Testing direct database insertion...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO midias (name, uri, mimeType, cover, isFavorite, duration, fileSize, dateAdded, numeroDias)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        ''', ('Test Song', 'file:///test/song.mp3', 'audio/mpeg', None, 0, 0, 0))
        midia_id = cursor.lastrowid
        conn.commit()
        print("Direct insertion successful, ID:", midia_id)
        return midia_id
    except Exception as e:
        print("Direct insertion failed:", str(e))
        import traceback
        traceback.print_exc()
        raise
    finally:
        conn.close()

# Let's also add a test route to see if we can insert data through the API
@app.route('/test-db-insert', methods=['POST'])
def test_db_insert():
    print("Test DB insert route called")
    try:
        midia_id = test_database_insertion()
        return jsonify({"message": "DB insert test working", "id": midia_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Let's call this test function when the app starts
if __name__ == '__main__':
    init_db()
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")
    print("Starting Flask app...")
    
    # Test database insertion
    try:
        test_database_insertion()
    except Exception as e:
        print("Database test failed:", str(e))
    
    # Check if there are existing records
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM midias')
        count = cursor.fetchone()[0]
        print(f"Database contains {count} records")
        if count > 0:
            cursor.execute('SELECT id, name FROM midias LIMIT 5')
            records = cursor.fetchall()
            print("Sample records:")
            for record in records:
                print(f"  ID: {record[0]}, Name: {record[1]}")
        conn.close()
    except Exception as e:
        print("Error checking database records:", str(e))
    
    # Use Render's PORT environment variable or default to 5003
    port = int(os.environ.get('PORT', 5003))
    app.run(host='0.0.0.0', port=port, debug=False)
