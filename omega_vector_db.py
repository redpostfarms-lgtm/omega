"""
Omega Vector Database Integration
==================================
Vector database optimization for RAG system.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime
import numpy as np

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("[Vector DB] ChromaDB not available. Install with: pip install chromadb")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("[Vector DB] FAISS not available. Install with: pip install faiss-cpu")

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("[Vector DB] sentence-transformers not available. Install with: pip install sentence-transformers")

class VectorDatabase:
    """Vector database for RAG system"""
    
    def __init__(self, db_type: str = "chromadb", db_path: Optional[Path] = None):
        self.base_dir = Path(__file__).parent.absolute()
        self.db_type = db_type
        self.db_path = db_path or (self.base_dir / "vector_db")
        self.db_path.mkdir(exist_ok=True)
        
        self.embeddings_model = None
        self.chroma_client = None
        self.chroma_collection = None
        self.faiss_index = None
        self.faiss_metadata = []
        
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("[Vector DB] Embeddings model initialized")
            except Exception as e:
                print(f"[Vector DB] Embeddings initialization failed: {e}")
        
        if db_type == "chromadb" and CHROMADB_AVAILABLE:
            self._initialize_chromadb()
        elif db_type == "faiss" and FAISS_AVAILABLE:
            self._initialize_faiss()
        else:
            print(f"[Vector DB] Using fallback (no vector DB)")
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB"""
        try:
            self.chroma_client = chromadb.PersistentClient(
                path=str(self.db_path / "chromadb"),
                settings=Settings(anonymized_telemetry=False)
            )
            self.chroma_collection = self.chroma_client.get_or_create_collection(
                name="omega_knowledge_base",
                metadata={"description": "Omega knowledge base embeddings"}
            )
            print("[Vector DB] ChromaDB initialized")
        except Exception as e:
            print(f"[Vector DB] ChromaDB initialization failed: {e}")
            self.chroma_client = None
    
    def _initialize_faiss(self):
        """Initialize FAISS"""
        try:
            self.faiss_index = None
            self.faiss_metadata = []
            print("[Vector DB] FAISS initialized (will create index on first add)")
        except Exception as e:
            print(f"[Vector DB] FAISS initialization failed: {e}")
    
    def add_document(self, text: str, metadata: Optional[Dict[str, Any]] = None, doc_id: Optional[str] = None):
        """
        Add document to vector database.
        
        Args:
            text: Document text
            metadata: Optional metadata
            doc_id: Optional document ID
        """
        if not self.embeddings_model:
            print("[Vector DB] Embeddings model not available")
            return
        
        try:
            embedding = self.embeddings_model.encode(text).tolist()
            
            if not doc_id:
                import hashlib
                doc_id = hashlib.md5(text.encode()).hexdigest()[:16]
            
            if self.chroma_collection:
                self.chroma_collection.add(
                    embeddings=[embedding],
                    documents=[text],
                    ids=[doc_id],
                    metadatas=[metadata or {}]
                )
            elif self.faiss_index is not None:
                embedding_array = np.array([embedding], dtype='float32')
                self.faiss_index.add(embedding_array)
                self.faiss_metadata.append({
                    "id": doc_id,
                    "text": text,
                    "metadata": metadata or {}
                })
            else:
                if FAISS_AVAILABLE:
                    dimension = len(embedding)
                    self.faiss_index = faiss.IndexFlatL2(dimension)
                    embedding_array = np.array([embedding], dtype='float32')
                    self.faiss_index.add(embedding_array)
                    self.faiss_metadata.append({
                        "id": doc_id,
                        "text": text,
                        "metadata": metadata or {}
                    })
            
            print(f"[Vector DB] Document added: {doc_id}")
        except Exception as e:
            print(f"[Vector DB] Error adding document: {e}")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search vector database.
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of search results with text, metadata, and score
        """
        if not self.embeddings_model:
            return []
        
        try:
            query_embedding = self.embeddings_model.encode(query).tolist()
            
            results = []
            
            if self.chroma_collection:
                search_results = self.chroma_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
                
                for i in range(len(search_results['ids'][0])):
                    results.append({
                        "id": search_results['ids'][0][i],
                        "text": search_results['documents'][0][i],
                        "metadata": search_results['metadatas'][0][i] if search_results['metadatas'] else {},
                        "score": 1.0 - search_results['distances'][0][i] if search_results['distances'] else 0.0
                    })
            elif self.faiss_index is not None and len(self.faiss_metadata) > 0:
                query_array = np.array([query_embedding], dtype='float32')
                distances, indices = self.faiss_index.search(query_array, top_k)
                
                for i, idx in enumerate(indices[0]):
                    if idx < len(self.faiss_metadata):
                        metadata = self.faiss_metadata[idx]
                        results.append({
                            "id": metadata["id"],
                            "text": metadata["text"],
                            "metadata": metadata["metadata"],
                            "score": 1.0 / (1.0 + distances[0][i])  # Convert distance to similarity
                        })
            
            return results
        except Exception as e:
            print(f"[Vector DB] Error searching: {e}")
            return []
    
    def save_faiss_index(self):
        """Save FAISS index to disk"""
        if self.faiss_index is not None:
            try:
                faiss.write_index(self.faiss_index, str(self.db_path / "faiss.index"))
                with open(self.db_path / "faiss_metadata.json", 'w', encoding='utf-8') as f:
                    json.dump(self.faiss_metadata, f, indent=2)
                print("[Vector DB] FAISS index saved")
            except Exception as e:
                print(f"[Vector DB] Error saving FAISS index: {e}")
    
    def load_faiss_index(self):
        """Load FAISS index from disk"""
        if FAISS_AVAILABLE:
            try:
                index_path = self.db_path / "faiss.index"
                if index_path.exists():
                    self.faiss_index = faiss.read_index(str(index_path))
                    metadata_path = self.db_path / "faiss_metadata.json"
                    if metadata_path.exists():
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            self.faiss_metadata = json.load(f)
                    print("[Vector DB] FAISS index loaded")
            except Exception as e:
                print(f"[Vector DB] Error loading FAISS index: {e}")

_vector_db = None

def get_vector_db(db_type: str = "chromadb") -> VectorDatabase:
    """Get global vector database instance"""
    global _vector_db
    if _vector_db is None:
        _vector_db = VectorDatabase(db_type=db_type)
    return _vector_db

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" " * 20 + "OMEGA VECTOR DATABASE")
    print("=" * 80)
    print()
    
    if CHROMADB_AVAILABLE:
        db = VectorDatabase(db_type="chromadb")
        print("[OK] Vector database initialized (ChromaDB)")
    elif FAISS_AVAILABLE:
        db = VectorDatabase(db_type="faiss")
        print("[OK] Vector database initialized (FAISS)")
    else:
        print("[INFO] No vector database available")
        print("  Install with: pip install chromadb OR pip install faiss-cpu")
    
    print()
    print("Usage:")
    print("  from omega_vector_db import get_vector_db")
    print("  db = get_vector_db()")
    print("  db.add_document('Your text here')")
    print("  results = db.search('query', top_k=3)")
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
