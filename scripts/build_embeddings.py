import sqlite3
import sys
import os
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.ai.retrieval import retrieval_engine

DB_PATH = "data/parsed_chat.sqlite"

def build_embeddings():
    print("Loading conversations from SQLite...")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all conversation chunks
    cursor.execute("SELECT * FROM conversations")
    conversations = cursor.fetchall()
    
    if not conversations:
        print("No conversations found. Run chunker first.")
        return

    print(f"Found {len(conversations)} conversation chunks. Preparing to embed...")
    
    # We will process in batches
    BATCH_SIZE = 32
    
    ids = []
    documents = []
    metadatas = []
    
    for conv in tqdm(conversations, desc="Preparing text data"):
        conv_id = conv['id']
        start_time = conv['start_time'] or ""
        
        # Get messages for this conversation
        cursor.execute("SELECT sender, text FROM messages WHERE conversation_id = ? ORDER BY id ASC", (conv_id,))
        messages = cursor.fetchall()
        
        # Build the document string
        doc_parts = []
        for msg in messages:
            sender = msg['sender'] if msg['sender'] else "System"
            text = msg['text'] if msg['text'] else ""
            if text:
                doc_parts.append(f"{sender}: {text}")
                
        doc_text = "\n".join(doc_parts)
        if not doc_text.strip():
            continue
            
        ids.append(conv_id)
        documents.append(doc_text)
        metadatas.append({
            "start_time": start_time,
            "participants": conv['participants'] or ""
        })

    conn.close()

    total_docs = len(documents)
    print(f"Ready to embed {total_docs} documents using {retrieval_engine.model.model_card_data.model_id}...")

    # Embed and store in ChromaDB in batches to manage memory
    for i in tqdm(range(0, total_docs, BATCH_SIZE), desc="Embedding and storing"):
        batch_ids = ids[i:i+BATCH_SIZE]
        batch_docs = documents[i:i+BATCH_SIZE]
        batch_metas = metadatas[i:i+BATCH_SIZE]
        
        # Generate embeddings
        batch_embeddings = retrieval_engine.model.encode(batch_docs).tolist()
        
        # Add to ChromaDB
        retrieval_engine.collection.upsert(
            ids=batch_ids,
            embeddings=batch_embeddings,
            documents=batch_docs,
            metadatas=batch_metas
        )

    print("Embedding build complete! Stored in local vector database.")

if __name__ == "__main__":
    build_embeddings()
