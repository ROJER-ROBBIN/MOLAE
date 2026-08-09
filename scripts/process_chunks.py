import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.whatsapp.chunker import chunk_conversations

if __name__ == "__main__":
    print("Starting chunking process...")
    chunk_conversations()
    print("Chunking complete.")
