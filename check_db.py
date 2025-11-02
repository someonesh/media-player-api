import sqlite3
import os

def check_database(db_name):
    if not os.path.exists(db_name):
        print(f"Database {db_name} does not exist")
        return
        
    print(f"\n=== Checking {db_name} ===")
    try:
        # Connect to the database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Check if midias table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='midias'")
        if not cursor.fetchone():
            print("Table 'midias' does not exist")
            conn.close()
            return

        # Get table info
        cursor.execute('PRAGMA table_info(midias)')
        columns = cursor.fetchall()

        print("Table 'midias' schema:")
        for column in columns:
            print(f"  {column[1]} ({column[2]}) - Not Null: {bool(column[3])} - Default: {column[4]} - PK: {bool(column[5])}")

        # Check if there's any data
        cursor.execute('SELECT COUNT(*) FROM midias')
        count = cursor.fetchone()[0]
        print(f"\nTotal records in 'midias' table: {count}")

        # Show first few records if any
        if count > 0:
            cursor.execute('SELECT * FROM midias LIMIT 3')
            records = cursor.fetchall()
            print("\nFirst few records:")
            for record in records:
                print(f"  {record}")

        conn.close()
    except Exception as e:
        print(f"Error checking {db_name}: {e}")

# Check both databases
check_database('midias.db')
check_database('midias_new.db')