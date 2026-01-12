# Knowledge Base Update V24: SimCTG vs. L2 Normalization Comparison

**Date:** 2026-01-10  
**Update Type:** Content Addition  
**Document Updated:** `CONTRASTIVE_SEARCH_MATH_2026.md`

## Summary

Added a comprehensive comparison section between SimCTG (contrastive training) and L2 normalization (unit norm) as two different approaches to addressing anisotropy in language model representations.

### Content Added

1. **Comparison Table**
   - Stage of application (training vs. inference)
   - Goals and mechanisms
   - Effect on anisotropy and generation quality
   - Compute cost comparison
   - Need for retraining
   - Typical use cases
   - Empirical results
   - Limitations

2. **Detailed Explanation Sections**
   - **SimCTG (Contrastive Training)**:
     - Training objective formulation (InfoNCE-style)
     - Why it works (isotropy improvement)
     - Results (MAUVE, rep-n, diversity scores)
   
   - **L2 Normalization (Unit Norm)**:
     - Mathematical operation ($v_{\text{norm}} = v / \|v\|_2$)
     - Why it helps (magnitude normalization)
     - Limitations (post-hoc projection, doesn't fix root cause)
     - Results (modest improvements)

3. **Summary & Recommendation (2026 Perspective)**
   - SimCTG as powerful, proactive solution
   - L2 normalization as cheap, reactive fix
   - Practical recommendations:
     - Fine-tuning scenarios → use SimCTG
     - Off-the-shelf models → L2 normalization + contrastive search
   - Current status (2024–2025): contrastive search alone often sufficient

## Integration with Existing Knowledge

This comparison provides context for:

- Understanding different approaches to isotropy improvement
- When to use training-time vs. inference-time methods
- Practical decision-making for addressing anisotropy
- Relationship between SimCTG training and simpler inference-time fixes

## Knowledge Base Structure

```
LLM Decoding Strategies Knowledge:
├── LLM_DECODING_STRATEGIES_2026.md (Comparisons & Decision Guides)
├── BEAM_SEARCH_VARIANTS_2026.md (Beam Search Variants Overview)
├── GRID_BEAM_SEARCH_2026.md (Grid Beam Search Guide)
├── GRID_BEAM_SEARCH_FROM_SCRATCH.py (Grid Beam Search Implementation)
├── DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md (Code Examples)
└── CONTRASTIVE_SEARCH_MATH_2026.md (Mathematical Details - NOW WITH SimCTG vs. L2 Comparison) ⭐
```

## Status

✅ **Complete** - Comprehensive comparison between SimCTG and L2 normalization added to the knowledge base, providing practical guidance on when to use each approach.
