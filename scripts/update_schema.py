import sqlite3

def update_schema():
    conn = sqlite3.connect("data/parsed_chat.sqlite")
    cursor = conn.cursor()

    # Add conversation_id to messages if it doesn't exist
    try:
        cursor.execute("ALTER TABLE messages ADD COLUMN conversation_id TEXT")
    except sqlite3.OperationalError:
        pass # Column already exists

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        start_time TEXT,
        end_time TEXT,
        participants TEXT,
        topic TEXT,
        message_count INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        description TEXT,
        source_conversation_id TEXT,
        FOREIGN KEY(source_conversation_id) REFERENCES conversations(id)
    )
    """)

    conn.commit()
    conn.close()
    print("Schema updated successfully.")

if __name__ == "__main__":
    update_schema()
