import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Constants
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "vector_db")
COLLECTION_NAME = "chitraguptar_memory"
MODEL_NAME = "all-MiniLM-L6-v2"

class MemoryRetrievalEngine:
    def __init__(self):
        os.makedirs(DB_DIR, exist_ok=True)
        # Initialize local ChromaDB
        self.chroma_client = chromadb.PersistentClient(path=DB_DIR)
        
        # Load local embedding model (downloads first time if not present)
        self.model = SentenceTransformer(MODEL_NAME)
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def semantic_search(self, query: str, top_k: int = 5):
        """
        Search for the most relevant conversation chunks based on semantic meaning.
        """
        # Generate embedding for the query
        query_embedding = self.model.encode(query).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "chunk_id": results['ids'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "document": results['documents'][0][i],
                    "distance": results['distances'][0][i]
                })
                
        return formatted_results

# Singleton instance
retrieval_engine = MemoryRetrievalEngine()
