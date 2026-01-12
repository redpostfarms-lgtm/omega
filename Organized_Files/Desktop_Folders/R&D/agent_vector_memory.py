# -*- coding: utf-8 -*-
# VECTOR MEMORY SYSTEM - Semantic similarity search
# Industry-standard vector embeddings for agent memory

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None
    print("Warning: NumPy not available. Install with: pip install numpy")

try:
    from sentence_transformers import SentenceTransformer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("Warning: sentence-transformers not available. Install with: pip install sentence-transformers")


@dataclass
class Memory:
    """Single memory with vector embedding."""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None
    timestamp: float = 0.0
    importance: float = 1.0
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class VectorMemory:
    """
    Vector-based memory system with semantic similarity search.
    
    Uses embeddings to find similar memories, enabling:
    - Semantic search
    - Context retrieval
    - Pattern recognition
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize vector memory system."""
        self.memories: Dict[str, Memory] = {}
        self.embeddings: List[List[float]] = []
        self.memory_ids: List[str] = []
        self.model = None
        self.embedding_dim = 384  # Default for MiniLM
        
        # Load embedding model
        if HAS_TRANSFORMERS:
            try:
                self.model = SentenceTransformer(model_name)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                print(f"[Vector Memory] Loaded model: {model_name} ({self.embedding_dim}D embeddings)")
            except Exception as e:
                print(f"[Vector Memory] Model load failed: {e}. Using fallback.")
        else:
            print("[Vector Memory] Using fallback embeddings (install sentence-transformers for full features)")
    
    def add_memory(self, content: str, metadata: Dict[str, Any] = None, 
                   importance: float = 1.0) -> str:
        """
        Add memory with automatic embedding.
        
        Args:
            content: Memory content
            metadata: Optional metadata
            importance: Importance score (0.0-1.0)
            
        Returns:
            Memory ID
        """
        # Generate ID
        memory_id = hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:16]
        
        # Generate embedding
        embedding = self._embed(content)
        
        # Create memory
        memory = Memory(
            id=memory_id,
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            importance=importance
        )
        
        # Store
        self.memories[memory_id] = memory
        self.embeddings.append(embedding)
        self.memory_ids.append(memory_id)
        
        return memory_id
    
    def _embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        if self.model:
            try:
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            except:
                pass
        
        # Fallback: simple hash-based embedding
        return self._fallback_embed(text)
    
    def _fallback_embed(self, text: str) -> List[float]:
        """Fallback embedding (hash-based)."""
        # Simple hash-based embedding (not semantic, but works)
        hash_value = hashlib.sha256(text.encode()).hexdigest()
        
        # Convert to vector
        embedding = []
        for i in range(0, len(hash_value), 2):
            val = int(hash_value[i:i+2], 16) / 255.0
            embedding.append(val)
        
        # Pad or truncate to embedding_dim
        while len(embedding) < self.embedding_dim:
            embedding.extend(embedding[:self.embedding_dim - len(embedding)])
        
        return embedding[:self.embedding_dim]
    
    def search(self, query: str, top_k: int = 5, 
               min_similarity: float = 0.5) -> List[Tuple[str, float, Memory]]:
        """
        Semantic search for similar memories.
        
        Args:
            query: Search query
            top_k: Number of results
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of (memory_id, similarity, memory) tuples
        """
        if not self.memories:
            return []
        
        # Embed query
        query_embedding = self._embed(query)
        
        # Compute similarities
        similarities = []
        for i, memory_id in enumerate(self.memory_ids):
            memory = self.memories[memory_id]
            if memory.embedding:
                similarity = self._cosine_similarity(query_embedding, memory.embedding)
                # Weight by importance
                weighted_similarity = similarity * memory.importance
                
                if weighted_similarity >= min_similarity:
                    similarities.append((memory_id, weighted_similarity, memory))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not HAS_NUMPY:
            # Fallback implementation
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2) ** 0.5
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            return dot_product / (magnitude1 * magnitude2)
        
        # NumPy version (faster)
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        magnitude1 = np.linalg.norm(v1)
        magnitude2 = np.linalg.norm(v2)
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return float(dot_product / (magnitude1 * magnitude2))
    
    def get_context(self, query: str, max_memories: int = 10) -> str:
        """
        Get relevant context from memories.
        
        Args:
            query: Context query
            max_memories: Maximum memories to retrieve
            
        Returns:
            Context string
        """
        results = self.search(query, top_k=max_memories)
        
        context_parts = []
        for memory_id, similarity, memory in results:
            context_parts.append(f"[Similarity: {similarity:.2f}] {memory.content}")
        
        return "\n".join(context_parts)
    
    def save(self, filepath: str):
        """Save memories to file."""
        data = {
            'memories': {mid: asdict(mem) for mid, mem in self.memories.items()},
            'embedding_dim': self.embedding_dim,
            'saved_at': time.time()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str):
        """Load memories from file."""
        if not os.path.exists(filepath):
            return
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.memories = {}
        self.embeddings = []
        self.memory_ids = []
        
        for mid, mem_data in data.get('memories', {}).items():
            memory = Memory(**mem_data)
            self.memories[mid] = memory
            if memory.embedding:
                self.embeddings.append(memory.embedding)
                self.memory_ids.append(mid)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        return {
            'total_memories': len(self.memories),
            'embedding_dim': self.embedding_dim,
            'has_model': self.model is not None,
            'has_numpy': HAS_NUMPY
        }


if __name__ == '__main__':
    print("=" * 60)
    print("VECTOR MEMORY SYSTEM - Test")
    print("=" * 60)
    
    memory = VectorMemory()
    
    # Add some memories
    memory.add_memory("User likes Python programming", {'topic': 'programming'}, importance=0.9)
    memory.add_memory("User prefers fast code execution", {'topic': 'performance'}, importance=0.8)
    memory.add_memory("Agent system needs vector embeddings", {'topic': 'improvements'}, importance=1.0)
    
    # Search
    results = memory.search("coding languages", top_k=3)
    print(f"\nSearch results for 'coding languages':")
    for mid, similarity, mem in results:
        print(f"  [{similarity:.3f}] {mem.content}")
    
    # Get context
    context = memory.get_context("improvements needed", max_memories=2)
    print(f"\nContext: {context[:100]}...")
    
    stats = memory.get_stats()
    print(f"\nStats: {stats}")
    
    print("\n[OK] Vector memory ready")

