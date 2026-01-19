"""
Omega RAG System
================
Implements Retrieval Augmented Generation (RAG) for knowledge base integration.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    VECTOR_DB_AVAILABLE = True
except ImportError:
    VECTOR_DB_AVAILABLE = False
    print("[RAG] Vector DB libraries not available. Install with: pip install scikit-learn")

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("[RAG] Sentence transformers not available. Install with: pip install sentence-transformers")

class SimpleRAGSystem:
    """Simple RAG system using TF-IDF or embeddings"""
    
    def __init__(self, knowledge_base_path: Optional[Path] = None):
        self.base_dir = Path(__file__).parent.absolute()
        self.knowledge_base_path = knowledge_base_path or (self.base_dir / "knowledge_base.json")
        self.documents = []
        self.vectorizer = None
        self.embeddings_model = None
        self.document_embeddings = []
        self.use_embeddings = EMBEDDINGS_AVAILABLE
        
        if self.use_embeddings:
            self._initialize_embeddings()
        else:
            self._initialize_tfidf()
        
        self.load_knowledge_base()
    
    def _initialize_embeddings(self):
        """Initialize sentence transformer embeddings"""
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("[RAG] Embeddings model initialized")
            except Exception as e:
                print(f"[RAG] Embeddings initialization failed: {e}")
                self.use_embeddings = False
                self._initialize_tfidf()
    
    def _initialize_tfidf(self):
        """Initialize TF-IDF vectorizer"""
        if VECTOR_DB_AVAILABLE:
            self.vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
            print("[RAG] TF-IDF vectorizer initialized")
    
    def load_knowledge_base(self):
        """Load knowledge base from file"""
        if not self.knowledge_base_path.exists():
            self.documents = []
            self._save_knowledge_base()
            return
        
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.documents = data.get('documents', [])
            
            if self.documents:
                self._index_documents()
                print(f"[RAG] Loaded {len(self.documents)} documents from knowledge base")
        except Exception as e:
            print(f"[RAG] Error loading knowledge base: {e}")
            self.documents = []
    
    def _save_knowledge_base(self):
        """Save knowledge base to file"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "documents": self.documents
            }
            with open(self.knowledge_base_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[RAG] Error saving knowledge base: {e}")
    
    def add_document(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """Add document to knowledge base"""
        doc = {
            "id": len(self.documents),
            "text": text,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        self.documents.append(doc)
        self._index_documents()
        self._save_knowledge_base()
    
    def _index_documents(self):
        """Index documents for retrieval"""
        if not self.documents:
            return
        
        texts = [doc['text'] for doc in self.documents]
        
        if self.use_embeddings and self.embeddings_model:
            try:
                self.document_embeddings = self.embeddings_model.encode(texts)
                print(f"[RAG] Indexed {len(texts)} documents with embeddings")
            except Exception as e:
                print(f"[RAG] Embedding error: {e}")
                self.use_embeddings = False
                self._initialize_tfidf()
                self._index_documents()
        elif self.vectorizer and VECTOR_DB_AVAILABLE:
            try:
                self.vectorizer.fit(texts)
                print(f"[RAG] Indexed {len(texts)} documents with TF-IDF")
            except Exception as e:
                print(f"[RAG] TF-IDF indexing error: {e}")
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for query"""
        if not self.documents:
            return []
        
        try:
            if self.use_embeddings and self.embeddings_model and len(self.document_embeddings) > 0:
                query_embedding = self.embeddings_model.encode([query])
                similarities = cosine_similarity(query_embedding, self.document_embeddings)[0]
                top_indices = np.argsort(similarities)[-top_k:][::-1]
                
                results = []
                for idx in top_indices:
                    results.append({
                        "document": self.documents[idx],
                        "score": float(similarities[idx])
                    })
                return results
            elif self.vectorizer and VECTOR_DB_AVAILABLE:
                texts = [doc['text'] for doc in self.documents]
                query_vector = self.vectorizer.transform([query])
                doc_vectors = self.vectorizer.transform(texts)
                similarities = cosine_similarity(query_vector, doc_vectors)[0]
                top_indices = np.argsort(similarities)[-top_k:][::-1]
                
                results = []
                for idx in top_indices:
                    results.append({
                        "document": self.documents[idx],
                        "score": float(similarities[idx])
                    })
                return results
        except Exception as e:
            print(f"[RAG] Retrieval error: {e}")
        
        return []
    
    def augment_prompt(self, query: str, top_k: int = 3) -> str:
        """Augment prompt with retrieved context"""
        retrieved = self.retrieve(query, top_k)
        if not retrieved:
            return query
        
        context_parts = []
        for result in retrieved:
            context_parts.append(result['document']['text'])
        
        context = '\n\n'.join(context_parts)
        augmented = f"Context:\n{context}\n\nQuery: {query}"
        return augmented

def get_rag_system(knowledge_base_path: Optional[Path] = None) -> SimpleRAGSystem:
    """Get global RAG system instance"""
    if not hasattr(get_rag_system, '_instance'):
        get_rag_system._instance = SimpleRAGSystem(knowledge_base_path)
    return get_rag_system._instance

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" " * 25 + "OMEGA RAG SYSTEM")
    print("=" * 80)
    print()
    
    rag = SimpleRAGSystem()
    print("[OK] RAG system initialized")
    print(f"  - Knowledge base: {rag.knowledge_base_path.name}")
    print(f"  - Documents: {len(rag.documents)}")
    print(f"  - Method: {'Embeddings' if rag.use_embeddings else 'TF-IDF'}")
    print()
    print("Features:")
    print("  - Document indexing")
    print("  - Semantic search")
    print("  - Context retrieval")
    print("  - Prompt augmentation")
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
