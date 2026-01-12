# Knowledge Base Update V23: SimCTG Training Objective Details

**Date:** 2026-01-10  
**Update Type:** Content Expansion  
**Document Updated:** `CONTRASTIVE_SEARCH_MATH_2026.md`

## Summary

Expanded the SimCTG section with comprehensive details about the contrastive training objective, including mathematical formulation, implementation details, and practical status.

### Content Added

1. **Problem Definition**
   - Explanation of anisotropy in standard LMs
   - How anisotropy causes degeneration and poor diversity
   - SimCTG's goal: push representations toward isotropy

2. **Mathematical Formulation**
   - InfoNCE-style contrastive loss equation
   - Definition of positive and negative pairs
   - Cosine similarity function
   - Temperature parameter explanation
   - Full training objective (weighted combination with NLL loss)

3. **Positive Pair Augmentation**
   - Dropout-based augmentation method
   - How to create positive pairs using different dropout masks
   - Natural positive pair generation without explicit data augmentation

4. **Implementation Details**
   - Positive pair creation (dropout-based)
   - Negative pair selection (in-batch negatives)
   - Temperature value (τ = 0.05)
   - Embedding layer selection
   - Training application (fine-tuning vs. pretraining)

5. **Empirical Results**
   - Isotropy improvement metrics (cosine similarity increase from ~0.1 to ~0.4–0.6)
   - Degeneration reduction (rep-n scores)
   - MAUVE improvements
   - Human evaluation results

6. **Practical Status in 2026**
   - Why SimCTG training is not commonly applied
   - Why contrastive search decoding alone is sufficient
   - Modern model alternatives (better data, architecture, regularization)
   - Continued popularity of contrastive search decoding

7. **Key Insight Reinforcement**
   - Emphasis on contrastive search working without SimCTG training
   - Why this made it immediately applicable to existing models

## Integration with Existing Knowledge

This expansion provides the complete theoretical foundation for understanding:

- Why contrastive search works (addresses anisotropy)
- How SimCTG training could enhance it (though not necessary)
- The mathematical relationship between training and decoding methods

## Knowledge Base Structure

```
LLM Decoding Strategies Knowledge:
├── LLM_DECODING_STRATEGIES_2026.md (Comparisons & Decision Guides)
├── BEAM_SEARCH_VARIANTS_2026.md (Beam Search Variants Overview)
├── GRID_BEAM_SEARCH_2026.md (Grid Beam Search Guide)
├── GRID_BEAM_SEARCH_FROM_SCRATCH.py (Grid Beam Search Implementation)
├── DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md (Code Examples)
└── CONTRASTIVE_SEARCH_MATH_2026.md (Mathematical Details - NOW WITH FULL SimCTG SECTION) ⭐
```

## Status

✅ **Complete** - SimCTG training objective fully documented with mathematical formulation, implementation details, and practical context.
