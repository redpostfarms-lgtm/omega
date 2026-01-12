# Knowledge Base Update V29: MAUVE vs. Jensen-Shannon Divergence Comparison

**Date:** 2026-01-10  
**Update Type:** Content Addition  
**Document Updated:** `DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md`

## Summary

Added comprehensive comparison between MAUVE and Jensen-Shannon (JS) divergence metrics, including detailed comparison table, visual intuition explanation, and practical recommendations for 2026.

### Content Added

1. **Example 4: MAUVE vs. Jensen-Shannon Divergence Comparison Section**
   - Introduction to both metrics
   - Context: Both used to compare model-generated vs human-written text distributions
   - Purpose: Understanding differences in design, sensitivity, and practical use

2. **Comparison Table**
   - **13 comparison aspects:**
     1. Definition (mathematical formulation)
     2. Range / Interpretability (0-1 scale explanation)
     3. Symmetry (asymmetric vs symmetric)
     4. Sensitivity to Degeneration (repetition detection)
     5. Sensitivity to Diversity (distribution coverage)
     6. Quantization (clustering requirements)
     7. Compute Cost (performance comparison)
     8. Need for Reference Set (sample size requirements)
     9. Robustness to Featurizer (model choice sensitivity)
     10. Typical Values (2026 benchmarks)
     11. Real-World Usage (application contexts)
     12. Main Strength (key advantages)
   
   - Winners identified for each aspect
   - MAUVE wins on: sensitivity to degeneration, sensitivity to diversity, real-world usage, main strength
   - JS divergence wins on: symmetry, compute cost, need for reference set, robustness to featurizer

3. **Visual Intuition: Why MAUVE Catches Degeneration Better**
   - **Standard JS divergence limitations:**
     - Repetitive models can have low JS divergence if human set has similar phrases
     - JS averages forward + reverse KL → doesn't strongly penalize when model is "stuck"
   
   - **MAUVE advantages:**
     - Uses maximum divergence along mixture frontier → forces full distribution coverage
     - Repetitive models create high peak in divergence curve → large area → low MAUVE
     - Much more sensitive to degeneration than plain JS

4. **Summary (2026 Perspective)**
   - **Use MAUVE when:**
     - Evaluating open-ended generation (stories, dialogue, creative text)
     - Caring about both quality and diversity
     - Standard in LLM papers and leaderboards
   
   - **Use JS divergence when:**
     - Need fast, simple, symmetric baseline
     - Quick sanity check
     - Embedding comparison
     - MAUVE compute is too expensive
   
   - **In practice:**
     - Most 2025–2026 papers report both
     - JS as cheap sanity check
     - MAUVE as main diversity+quality metric
     - Frontier models score very high on MAUVE (0.90+)

## Integration with Existing Knowledge

This comparison complements:

- **MAUVE computation details**: Provides context for when MAUVE is preferred over alternatives
- **MAUVE divergence curve illustration**: Helps understand why MAUVE is more sensitive to degeneration
- **Evaluation metrics context**: Shows trade-offs between different evaluation approaches

## Knowledge Base Structure

```
LLM Decoding Strategies Knowledge:
├── LLM_DECODING_STRATEGIES_2026.md (Comparisons & Decision Guides)
├── BEAM_SEARCH_VARIANTS_2026.md (Beam Search Variants Overview)
├── GRID_BEAM_SEARCH_2026.md (Grid Beam Search Guide)
├── GRID_BEAM_SEARCH_FROM_SCRATCH.py (Grid Beam Search Implementation)
├── CONTRASTIVE_SEARCH_MATH_2026.md (Mathematical Details)
└── DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md (Code Examples - NOW WITH MAUVE vs JS Comparison) ⭐
```

## Status

✅ **Complete** - Comprehensive comparison between MAUVE and Jensen-Shannon divergence fully integrated, providing clear guidance on when to use each metric for text generation evaluation.
