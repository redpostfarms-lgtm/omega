# Knowledge Base Update V25: SimCTG Code Examples

**Date:** 2026-01-10  
**Update Type:** Content Addition  
**Document Updated:** `DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md`

## Summary

Added comprehensive SimCTG (Simulated Contrastive Training for Generation) code examples to the code examples document, including both a basic loss function implementation and a complete training loop example.

### Content Added

1. **Pattern 6: SimCTG Training Objective Section**
   - Introduction to SimCTG as contrastive training for isotropy
   - Note about optional nature (contrastive search alone often sufficient)
   - Context: When SimCTG training is beneficial

2. **Example 1: Basic SimCTG Loss Function**
   - Clean, self-contained `simctg_loss()` function implementation
   - InfoNCE-style contrastive loss with cosine similarity
   - L2 normalization for embeddings
   - Positive/negative pair handling
   - Temperature parameter support
   - Usage example in training step (pseudo-code)
   - Helper function for two-forward-pass positive pairs

3. **Example 2: Full Training Loop with SimCTG**
   - Complete production-ready training loop
   - Integration with Hugging Face Transformers
   - Accelerate library for mixed precision and multi-GPU
   - Dataset loading and preparation
   - Optimizer and scheduler setup
   - Full training loop with:
     - Standard next-token prediction loss (NLL)
     - SimCTG contrastive loss
     - Weighted combination of losses
     - Gradient accumulation
     - Logging and checkpointing

4. **Key Notes and Best Practices**
   - Positive pair creation via dropout augmentation
   - Negative pair selection (in-batch negatives)
   - Temperature and weight hyperparameters
   - Embedding layer selection
   - Improvements for 2026:
     - Two-forward-pass implementation
     - Memory efficiency (gradient checkpointing)
     - Modern alternatives (Mixup, L2 norm + contrastive search)

5. **Practical Context (2026 Perspective)**
   - Why SimCTG isn't used everywhere
   - When SimCTG training is beneficial
   - Relationship to contrastive search decoding
   - Modern model improvements

## Integration with Existing Knowledge

This code complements:

- **`CONTRASTIVE_SEARCH_MATH_2026.md`**: Provides practical implementation of the theoretical SimCTG formulation
- **`LLM_DECODING_STRATEGIES_2026.md`**: Shows how SimCTG training relates to contrastive search decoding
- **Contrastive Search code examples**: Demonstrates the training-time component that enhances decoding-time contrastive search

## Knowledge Base Structure

```
LLM Decoding Strategies Knowledge:
├── LLM_DECODING_STRATEGIES_2026.md (Comparisons & Decision Guides)
├── BEAM_SEARCH_VARIANTS_2026.md (Beam Search Variants Overview)
├── GRID_BEAM_SEARCH_2026.md (Grid Beam Search Guide)
├── GRID_BEAM_SEARCH_FROM_SCRATCH.py (Grid Beam Search Implementation)
├── CONTRASTIVE_SEARCH_MATH_2026.md (Mathematical Details - SimCTG Theory)
└── DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md (Code Examples - NOW WITH SimCTG Implementation) ⭐
```

## Status

✅ **Complete** - SimCTG code examples fully integrated, providing both basic implementation and complete training loop for practical use.
