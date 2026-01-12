#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# OMEGA PHASE 1 INTEGRATION
# Integrates Vector RAG + Multi-Modal with Omega Core
# Phase 1: Critical Foundation

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Import Phase 1 modules
try:
    from omega_vector_rag_system import OmegaVectorRAG
    VECTOR_RAG_AVAILABLE = True
except ImportError:
    VECTOR_RAG_AVAILABLE = False
    OmegaVectorRAG = None

try:
    from omega_multimodal_processor import OmegaMultiModalProcessor
    MULTIMODAL_AVAILABLE = True
except ImportError:
    MULTIMODAL_AVAILABLE = False
    OmegaMultiModalProcessor = None

# Import Omega core
try:
    from deep_system_test import OmegaSystemTester
    OMEGA_CORE_AVAILABLE = True
except ImportError:
    OMEGA_CORE_AVAILABLE = False
    OmegaSystemTester = None

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'

logger = logging.getLogger('Omega.Phase1')

class OmegaPhase1Integration:
    """Omega Phase 1 Integration - Vector RAG + Multi-Modal."""
    
    def __init__(self):
        """Initialize Phase 1 integration."""
        self.vector_rag = None
        self.multimodal = None
        self.omega_core = None
        
        # Initialize Vector RAG
        if VECTOR_RAG_AVAILABLE:
            try:
                self.vector_rag = OmegaVectorRAG()
                logger.info("✅ Vector RAG system initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Vector RAG: {e}")
        
        # Initialize Multi-Modal
        if MULTIMODAL_AVAILABLE:
            try:
                self.multimodal = OmegaMultiModalProcessor()
                logger.info("✅ Multi-Modal processor initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Multi-Modal: {e}")
        
        # Initialize Omega Core
        if OMEGA_CORE_AVAILABLE:
            try:
                self.omega_core = OmegaSystemTester(autonomous=True)
                logger.info("✅ Omega core initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Omega core: {e}")
        
        logger.info("Omega Phase 1 Integration initialized")
    
    def index_document(self, content: str, metadata: Optional[Dict] = None) -> Optional[str]:
        """Index document in RAG system."""
        if not self.vector_rag:
            logger.warning("Vector RAG not available")
            return None
        return self.vector_rag.index_document(content, metadata)
    
    def search_knowledge(self, query: str, top_k: int = 5) -> Optional[Dict]:
        """Search knowledge base."""
        if not self.vector_rag:
            logger.warning("Vector RAG not available")
            return None
        return self.vector_rag.search(query, top_k=top_k)
    
    def process_image(self, image_path: str, use_llm: bool = True) -> Optional[Any]:
        """Process image."""
        if not self.multimodal:
            logger.warning("Multi-Modal processor not available")
            return None
        return self.multimodal.process_image(image_path, use_llm=use_llm)
    
    def process_audio(self, audio_path: str) -> Optional[Any]:
        """Process audio."""
        if not self.multimodal:
            logger.warning("Multi-Modal processor not available")
            return None
        return self.multimodal.process_audio(audio_path)
    
    def process_video(self, video_path: str) -> Optional[Any]:
        """Process video."""
        if not self.multimodal:
            logger.warning("Multi-Modal processor not available")
            return None
        return self.multimodal.process_video(video_path)
    
    def augmented_query(self, query: str, use_rag: bool = True, use_multimodal: bool = False) -> str:
        """Create augmented query with RAG context."""
        augmented = query
        
        if use_rag and self.vector_rag:
            try:
                augmented = self.vector_rag.augment_for_llm(query, top_k=5)
            except Exception as e:
                logger.warning(f"RAG augmentation failed: {e}")
        
        return augmented
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status."""
        status = {
            "vector_rag": {
                "available": self.vector_rag is not None,
                "stats": self.vector_rag.get_stats() if self.vector_rag else None
            },
            "multimodal": {
                "available": self.multimodal is not None,
                "capabilities": self.multimodal.get_capabilities() if self.multimodal else None
            },
            "omega_core": {
                "available": self.omega_core is not None
            }
        }
        return status

def main():
    """Test Phase 1 integration."""
    print("=" * 60)
    print("OMEGA PHASE 1 INTEGRATION - TEST")
    print("=" * 60)
    
    integration = OmegaPhase1Integration()
    
    # Status
    print("\n[1] Integration Status:")
    status = integration.get_status()
    print(json.dumps(status, indent=2))
    
    # Test RAG
    if integration.vector_rag:
        print("\n[2] Testing RAG system...")
        doc_id = integration.index_document(
            "Omega Phase 1 includes Vector RAG and Multi-Modal processing capabilities.",
            {"source": "phase1", "type": "system"}
        )
        print(f"Indexed document: {doc_id}")
        
        results = integration.search_knowledge("What is Phase 1?", top_k=3)
        if results:
            print(f"Found {results['count']} documents")
            for doc in results['documents']:
                print(f"  [{doc['rank']}] {doc['similarity']:.3f}: {doc['content'][:60]}...")
    
    # Test Multi-Modal
    if integration.multimodal:
        print("\n[3] Testing Multi-Modal capabilities...")
        capabilities = integration.multimodal.get_capabilities()
        for cap, avail in capabilities.items():
            status = "✅" if avail else "❌"
            print(f"  {status} {cap}")
    
    print("\n" + "=" * 60)
    print("PHASE 1 INTEGRATION TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

# RPF-GK-2026-7A3F9B2C-4D8E1F6A-9C2B5D7E-3F8A1C4E (ownership signature)
