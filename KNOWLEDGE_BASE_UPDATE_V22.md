# Knowledge Base Update V22: Contrastive Search Mathematical Details

**Date:** 2026-01-10  
**Update Type:** New Document Addition  
**Document Added:** `CONTRASTIVE_SEARCH_MATH_2026.md`

## Summary

Added comprehensive mathematical documentation for Contrastive Search, including:

### Content Added

1. **Core Mathematical Formulation**
   - Formal probability adjustment equation
   - Definition of key variables (hidden states, vocabulary, similarity function)
   - Alpha parameter explanation

2. **Practical Implementation Details**
   - Approximation methods (current hidden state, word embeddings, top-k candidates)
   - Step-by-step algorithmic formulation
   - Adjusted score calculation with similarity penalty

3. **Parameter Guidance**
   - Typical ranges for `top_k` (10-50) and `alpha` (0.5-1.0)
   - Effect of each parameter
   - Similarity function choices (cosine, dot product, L2)
   - Embedding layer selection trade-offs

4. **Mathematical Advantages**
   - Semantic loop avoidance (vs. lexical-only prevention in top-k/top-p)
   - Fluency maintenance
   - Long-form coherence improvements

5. **Real-World Performance Metrics**
   - 40-70% repetition reduction compared to top-k=50
   - Coherence score improvements
   - Optimal parameter combination (top_k=40, alpha=0.7, temperature=0.8)

6. **Limitations**
   - Hidden state access requirements
   - Performance overhead
   - Model-dependent alpha tuning
   - Why it's popular in open-source but rare in closed APIs

7. **Original Paper Information**
   - Correct citation: Su et al. (2022) - "A Contrastive Framework for Neural Text Generation" (NeurIPS 2022)
   - arXiv: 2202.06417
   - Official implementation link (SimCTG GitHub)
   - Follow-up paper (Su & Collier, 2022) - 16 languages validation

8. **Historical Context & Impact**
   - SimCTG training method explanation
   - Breakthrough insights (works without retraining)
   - Historical impact on later methods
   - Performance results from original paper

9. **References**
   - Primary papers (Su et al., 2022; Su & Collier, 2022)
   - Related work (Li et al., 2022 - Contrastive Decoding)
   - Implementation links

## Integration with Existing Knowledge

This document complements:

- **`LLM_DECODING_STRATEGIES_2026.md`**: Provides the mathematical foundation for the comparison table entries
- **`DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md`**: Provides theoretical background for the practical implementation examples

## Knowledge Base Structure

```text
LLM Decoding Strategies Knowledge:
├── LLM_DECODING_STRATEGIES_2026.md (Comparisons & Decision Guides)
├── BEAM_SEARCH_VARIANTS_2026.md (Beam Search Variants Overview)
├── GRID_BEAM_SEARCH_2026.md (Grid Beam Search Guide)
├── GRID_BEAM_SEARCH_FROM_SCRATCH.py (Grid Beam Search Implementation)
├── DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md (Code Examples - Diverse Beam, Outlines, Contrastive)
└── CONTRASTIVE_SEARCH_MATH_2026.md (NEW - Mathematical Details) ⭐
```text

## Status

✅ **Complete** - Mathematical documentation fully integrated into Omega's knowledge base.

## Update Note (2026-01-10)

✅ **Citations Corrected** - Updated document with correct original paper citations:
- Primary paper: Su et al. (2022) - "A Contrastive Framework for Neural Text Generation" (arXiv:2202.06417)
- Added follow-up paper: Su & Collier (2022) - "Contrastive Search Is What You Need For Neural Text Generation" (arXiv:2210.14140)
- Added SimCTG training method explanation
- Added historical impact and context section
- Updated core mathematical formulation to match original paper (maximization of contrastive score)
