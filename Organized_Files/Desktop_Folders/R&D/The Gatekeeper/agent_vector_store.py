# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
Agent Vector Store
Vector database for storing and searching agent embeddings
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import math

BRAIN = Path(r'D:\RPF_BRAIN')
ARCHIVED = BRAIN / 'Archived'
VECTOR_DIR = ARCHIVED / 'vector_store'
VECTOR_DIR.mkdir(parents=True, exist_ok=True)

class AgentVectorStore:
    """Vector database for storing and searching embeddings."""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.vectors = {}
        self.metadata = {}
        self.index_file = VECTOR_DIR / 'vector_index.json'
        self._load_index()
    
    def _load_index(self):
        """Load vector index from disk."""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.vectors = data.get('vectors', {})
                    self.metadata = data.get('metadata', {})
            except:
                self.vectors = {}
                self.metadata = {}
        else:
            self.vectors = {}
            self.metadata = {}
    
    def _save_index(self):
        """Save vector index to disk."""
        data = {
            'vectors': self.vectors,
            'metadata': self.metadata,
            'dimension': self.dimension,
            'updated_at': time.time()
        }
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _simple_embedding(self, text: str) -> List[float]:
        """
        Simple text embedding (hash-based).
        For production, use a real embedding model (sentence-transformers, OpenAI, etc.)
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector
        """
        # Simple hash-based embedding (placeholder)
        # In production, replace with actual embedding model
        hash_obj = hashlib.sha256(text.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        
        # Convert hash to vector
        vector = []
        for i in range(self.dimension):
            if i < len(hash_bytes):
                vector.append(float(hash_bytes[i] % 256) / 255.0)
            else:
                # Pad with hash-derived values
                pad_hash = hashlib.sha256(f"{text}_{i}".encode('utf-8')).digest()[0]
                vector.append(float(pad_hash % 256) / 255.0)
        
        return vector
    
    def add_embedding(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a text embedding to the vector store.
        
        Args:
            text: Text to embed
            metadata: Optional metadata
        
        Returns:
            Vector ID
        """
        vector_id = hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]
        embedding = self._simple_embedding(text)
        
        self.vectors[vector_id] = {
            'vector': embedding,
            'text': text,
            'created_at': time.time()
        }
        
        self.metadata[vector_id] = metadata or {}
        
        # Save index
        self._save_index()
        
        return vector_id
    
    def search_similar(self, query: str, top_k: int = 10) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar vectors.
        
        Args:
            query: Query text
            top_k: Number of results to return
        
        Returns:
            List of (vector_id, similarity_score, metadata) tuples
        """
        query_vector = self._simple_embedding(query)
        similarities = []
        
        for vector_id, vector_data in self.vectors.items():
            vector = vector_data['vector']
            similarity = self._cosine_similarity(query_vector, vector)
            metadata = self.metadata.get(vector_id, {})
            
            similarities.append((vector_id, similarity, {
                'text': vector_data.get('text', ''),
                'metadata': metadata
            }))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top_k results
        return similarities[:top_k]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def build_index(self, texts: List[str], metadata: Optional[List[Dict[str, Any]]] = None):
        """
        Build index from multiple texts.
        
        Args:
            texts: List of texts to index
            metadata: Optional list of metadata dictionaries
        """
        metadata = metadata or [{}] * len(texts)
        
        for i, text in enumerate(texts):
            meta = metadata[i] if i < len(metadata) else {}
            self.add_embedding(text, meta)
    
    def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """Get a vector by ID."""
        if vector_id in self.vectors:
            return {
                'id': vector_id,
                'vector': self.vectors[vector_id]['vector'],
                'text': self.vectors[vector_id].get('text', ''),
                'metadata': self.metadata.get(vector_id, {})
            }
        return None
    
    def delete_vector(self, vector_id: str) -> bool:
        """Delete a vector by ID."""
        if vector_id in self.vectors:
            del self.vectors[vector_id]
            if vector_id in self.metadata:
                del self.metadata[vector_id]
            self._save_index()
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        return {
            'total_vectors': len(self.vectors),
            'dimension': self.dimension,
            'index_file': str(self.index_file)
        }

