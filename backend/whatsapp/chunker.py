import sqlite3
from datetime import datetime, timedelta
import uuid

DB_PATH = "data/parsed_chat.sqlite"
GAP_THRESHOLD_HOURS = 2

def chunk_conversations():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Clear existing chunks
    cursor.execute("DELETE FROM conversations")
    cursor.execute("UPDATE messages SET conversation_id = NULL")

    cursor.execute("SELECT id, datetime_iso, sender FROM messages WHERE is_system = 0 ORDER BY datetime_iso ASC, id ASC")
    messages = cursor.fetchall()

    if not messages:
        print("No messages to chunk.")
        return

    conversations = []
    message_updates = []

    current_chunk_id = f"conv_{uuid.uuid4().hex[:8]}"
    current_start = None
    current_end = None
    current_participants = set()
    current_message_ids = []

    def save_current_chunk():
        if current_message_ids:
            conversations.append((
                current_chunk_id,
                current_start.isoformat() if current_start else None,
                current_end.isoformat() if current_end else None,
                ",".join(filter(None, current_participants)),
                None, # topic
                len(current_message_ids)
            ))
            for mid in current_message_ids:
                message_updates.append((current_chunk_id, mid))

    for msg in messages:
        if not msg['datetime_iso']:
            continue
            
        msg_time = datetime.fromisoformat(msg['datetime_iso'])
        sender = msg['sender']

        if current_end is None:
            # First message
            current_start = msg_time
            current_end = msg_time
            if sender: current_participants.add(sender)
            current_message_ids.append(msg['id'])
        else:
            time_diff = msg_time - current_end
            if time_diff > timedelta(hours=GAP_THRESHOLD_HOURS):
                # Gap exceeded threshold, save old chunk and start new
                save_current_chunk()
                
                current_chunk_id = f"conv_{uuid.uuid4().hex[:8]}"
                current_start = msg_time
                current_end = msg_time
                current_participants = set()
                if sender: current_participants.add(sender)
                current_message_ids = [msg['id']]
            else:
                # Add to current chunk
                current_end = msg_time
                if sender: current_participants.add(sender)
                current_message_ids.append(msg['id'])

    # Save last chunk
    save_current_chunk()

    # Bulk insert conversations
    cursor.executemany(
        "INSERT INTO conversations (id, start_time, end_time, participants, topic, message_count) VALUES (?, ?, ?, ?, ?, ?)",
        conversations
    )

    # Bulk update messages
    cursor.executemany(
        "UPDATE messages SET conversation_id = ? WHERE id = ?",
        message_updates
    )

    conn.commit()
    conn.close()
    
    print(f"Created {len(conversations)} conversation chunks.")

if __name__ == "__main__":
    chunk_conversations()
