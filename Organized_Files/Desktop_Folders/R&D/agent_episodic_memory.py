# -*- coding: utf-8 -*-
# EPISODIC MEMORY COMPRESSION - Long-term memory with compression
# Groups related memories, compresses episodes, enables long-term context

import os
import sys
import json
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict

try:
    from agent_vector_memory import VectorMemory, Memory
    HAS_VECTOR_MEMORY = True
except ImportError:
    HAS_VECTOR_MEMORY = False
    Memory = None
    print("Warning: Vector memory not available. Install agent_vector_memory.py")


@dataclass
class Episode:
    """Episode - group of related memories."""
    id: str
    title: str
    memories: List[str]  # Memory IDs
    summary: str  # Compressed summary
    start_time: float
    end_time: float
    importance: float = 1.0
    compressed: bool = False


class EpisodicMemory:
    """
    Episodic memory system with compression.
    
    Groups memories into episodes and compresses them:
    - Temporal grouping (related memories together)
    - Episode summarization
    - Long-term retention without bloat
    """
    
    def __init__(self, vector_memory: Optional[VectorMemory] = None, 
                 compression_threshold: int = 50):
        """Initialize episodic memory."""
        self.vector_memory = vector_memory
        if not self.vector_memory and HAS_VECTOR_MEMORY:
            self.vector_memory = VectorMemory()
        
        self.episodes: Dict[str, Episode] = {}
        self.current_episode: Optional[Episode] = None
        self.compression_threshold = compression_threshold
        self.memory_to_episode: Dict[str, str] = {}  # memory_id -> episode_id
    
    def start_episode(self, title: str) -> str:
        """Start a new episode."""
        if self.current_episode and not self.current_episode.compressed:
            # Compress previous episode if it has many memories
            if len(self.current_episode.memories) >= self.compression_threshold:
                self._compress_episode(self.current_episode.id)
        
        # Create new episode
        episode_id = hashlib.md5(f"{title}{time.time()}".encode()).hexdigest()[:16]
        episode = Episode(
            id=episode_id,
            title=title,
            memories=[],
            summary="",
            start_time=time.time(),
            end_time=time.time()
        )
        
        self.episodes[episode_id] = episode
        self.current_episode = episode
        
        return episode_id
    
    def add_memory_to_episode(self, memory_id: str, episode_id: Optional[str] = None):
        """Add memory to episode."""
        if episode_id is None:
            if self.current_episode:
                episode_id = self.current_episode.id
            else:
                # Create default episode
                episode_id = self.start_episode("Default Episode")
        
        if episode_id in self.episodes:
            episode = self.episodes[episode_id]
            if memory_id not in episode.memories:
                episode.memories.append(memory_id)
                episode.end_time = time.time()
                self.memory_to_episode[memory_id] = episode_id
    
    def _compress_episode(self, episode_id: str):
        """Compress episode by summarizing."""
        if episode_id not in self.episodes:
            return
        
        episode = self.episodes[episode_id]
        
        if episode.compressed or len(episode.memories) < 5:
            return
        
        # Get memory contents
        memory_contents = []
        if self.vector_memory:
            for mem_id in episode.memories:
                if mem_id in self.vector_memory.memories:
                    mem = self.vector_memory.memories[mem_id]
                    memory_contents.append(mem.content)
        
        # Generate summary (simplified - would use LLM in production)
        if memory_contents:
            # Extract key themes
            summary = f"Episode: {episode.title}\n"
            summary += f"Duration: {episode.end_time - episode.start_time:.1f}s\n"
            summary += f"Memories: {len(episode.memories)}\n"
            summary += f"Key points: {', '.join(memory_contents[:3])}"
            
            episode.summary = summary
            episode.compressed = True
            
            # Keep only important memories (importance > 0.7)
            if self.vector_memory:
                important_memories = []
                for mem_id in episode.memories:
                    if mem_id in self.vector_memory.memories:
                        mem = self.vector_memory.memories[mem_id]
                        if mem.importance > 0.7:
                            important_memories.append(mem_id)
                
                # Replace memories with important ones only
                episode.memories = important_memories[:10]  # Keep top 10
            
            print(f"[Episodic Memory] Compressed episode {episode_id}: {len(episode.memories)} memories → summary")
    
    def get_episode_context(self, query: str, max_episodes: int = 5) -> str:
        """Get context from relevant episodes."""
        if not self.vector_memory:
            return ""
        
        # Search for relevant memories
        results = self.vector_memory.search(query, top_k=20)
        
        # Group by episode
        episode_relevance = defaultdict(float)
        episode_memories = defaultdict(list)
        
        for memory_id, similarity, memory in results:
            episode_id = self.memory_to_episode.get(memory_id)
            if episode_id:
                episode_relevance[episode_id] = max(episode_relevance[episode_id], similarity)
                episode_memories[episode_id].append((memory_id, similarity, memory))
        
        # Sort episodes by relevance
        sorted_episodes = sorted(episode_relevance.items(), key=lambda x: x[1], reverse=True)
        
        # Build context
        context_parts = []
        for episode_id, relevance in sorted_episodes[:max_episodes]:
            episode = self.episodes.get(episode_id)
            if episode:
                context_parts.append(f"--- Episode: {episode.title} (Relevance: {relevance:.2f}) ---")
                
                if episode.compressed:
                    context_parts.append(episode.summary)
                else:
                    # Include memory contents
                    for mem_id, sim, mem in episode_memories[episode_id][:5]:
                        context_parts.append(f"  [{sim:.2f}] {mem.content}")
        
        return "\n".join(context_parts)
    
    def compress_all_old_episodes(self, age_threshold: float = 86400):
        """Compress all episodes older than threshold."""
        current_time = time.time()
        compressed_count = 0
        
        for episode_id, episode in self.episodes.items():
            age = current_time - episode.end_time
            if age > age_threshold and not episode.compressed:
                self._compress_episode(episode_id)
                compressed_count += 1
        
        if compressed_count > 0:
            print(f"[Episodic Memory] Compressed {compressed_count} old episodes")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get episodic memory statistics."""
        total_memories = sum(len(ep.memories) for ep in self.episodes.values())
        compressed_count = sum(1 for ep in self.episodes.values() if ep.compressed)
        
        return {
            'total_episodes': len(self.episodes),
            'compressed_episodes': compressed_count,
            'total_memories': total_memories,
            'current_episode': self.current_episode.id if self.current_episode else None,
            'compression_ratio': f"{compressed_count}/{len(self.episodes)}" if self.episodes else "0/0"
        }


# Integration with VectorMemory
def enhance_vector_memory_with_episodes(vector_memory: VectorMemory) -> EpisodicMemory:
    """Enhance vector memory with episodic compression."""
    return EpisodicMemory(vector_memory=vector_memory)


if __name__ == '__main__':
    print("=" * 60)
    print("EPISODIC MEMORY - Test")
    print("=" * 60)
    
    # Create episodic memory
    if HAS_VECTOR_MEMORY:
        vector_mem = VectorMemory()
        episodic = EpisodicMemory(vector_mem)
        
        # Start episode
        episode_id = episodic.start_episode("Code Review Session")
        
        # Add memories
        mem1 = vector_mem.add_memory("Found bug in agent_anonymous.py", importance=0.9)
        mem2 = vector_mem.add_memory("Fixed encoding issue", importance=0.8)
        mem3 = vector_mem.add_memory("Improved error handling", importance=0.7)
        
        episodic.add_memory_to_episode(mem1, episode_id)
        episodic.add_memory_to_episode(mem2, episode_id)
        episodic.add_memory_to_episode(mem3, episode_id)
        
        # Get context
        context = episodic.get_episode_context("bug fixes")
        print(f"\nContext:\n{context[:200]}...")
        
        stats = episodic.get_stats()
        print(f"\nStats: {stats}")
    
    print("\n[OK] Episodic memory ready")

