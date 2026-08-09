import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "parsed_chat.sqlite")

def get_db_connection():
    # Make sure we are looking at the right path relative to project root
    # or handle absolute path based on execution location.
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_messages(limit: int = 50, offset: int = 0, sender: str = None, search: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM messages WHERE 1=1"
    params = []
    
    if sender:
        query += " AND sender = ?"
        params.append(sender)
        
    if search:
        query += " AND text LIKE ?"
        params.append(f"%{search}%")
        
    query += " ORDER BY id ASC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Get total count for pagination info (simplified, count without limit/offset)
    count_query = "SELECT COUNT(*) FROM messages WHERE 1=1"
    count_params = []
    if sender:
        count_query += " AND sender = ?"
        count_params.append(sender)
    if search:
        count_query += " AND text LIKE ?"
        count_params.append(f"%{search}%")
        
    cursor.execute(count_query, count_params)
    total_count = cursor.fetchone()[0]
    
    conn.close()
    
    messages = [dict(row) for row in rows]
    return {
        "messages": messages,
        "total": total_count,
        "limit": limit,
        "offset": offset
    }

def get_message_by_date(date_str: str, limit: int = 50):
    """date_str format expected: YYYY-MM-DD"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Find the first message on or after this date
    query = "SELECT * FROM messages WHERE datetime_iso >= ? ORDER BY id ASC LIMIT ?"
    cursor.execute(query, [date_str, limit])
    rows = cursor.fetchall()
    
    conn.close()
    return [dict(row) for row in rows]
