import sqlite3
import os

# Delete existing database files
db_files = ['midias.db', 'midias_new.db']
for db_file in db_files:
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"Deleted {db_file}")
        except Exception as e:
            print(f"Could not delete {db_file}: {e}")

# Create new database with correct schema
DB_FILE = "midias.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Drop existing table if it exists
cursor.execute('DROP TABLE IF EXISTS midias')

cursor.execute('''
CREATE TABLE midias (
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

print(f"Created new database {DB_FILE} with correct schema")

# Test insertion
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Test insertion without filename column
try:
    cursor.execute('''
        INSERT INTO midias (name, uri, mimeType, cover, isFavorite, duration, fileSize, dateAdded, numeroDias)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    ''', ('Test Song', 'file:///test/song.mp3', 'audio/mpeg', None, 0, 0, 0))
    
    midia_id = cursor.lastrowid
    conn.commit()
    print(f"Test insertion successful, ID: {midia_id}")
    
    # Verify the data
    cursor.execute('SELECT * FROM midias WHERE id = ?', (midia_id,))
    row = cursor.fetchone()
    print(f"Inserted row: {row}")
    
except Exception as e:
    print(f"Test insertion failed: {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()