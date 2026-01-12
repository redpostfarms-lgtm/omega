# Knowledge Base Update V28: MAUVE Divergence Curve Illustration

**Date:** 2026-01-10  
**Update Type:** Content Addition  
**Document Updated:** `DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md`

## Summary

Added comprehensive visual illustration of the MAUVE divergence curve, including ASCII art diagrams, interpretation guide, and code example for plotting the curve.

### Content Added

1. **Visual Illustration of MAUVE Divergence Curve Section**
   - Introduction to the divergence curve concept
   - Explanation of how λ parameter affects the curve:
     - λ = 0 → purely human distribution
     - λ = 1 → purely model distribution
     - Middle λ → mixture closest to both
   - MAUVE score formula: 1 minus normalized area under curve

2. **Three Representative Curve Examples (ASCII Art)**
   - **Example 1: Excellent model (MAUVE ≈ 0.95)**
     - Low, flat curve across all λ
     - Small area under curve
     - Near-human distribution
   
   - **Example 2: Good but repetitive model (MAUVE ≈ 0.70)**
     - Higher peak in the middle
     - Larger area under curve
     - Moderate degeneration
   
   - **Example 3: Poor model (MAUVE ≈ 0.30)**
     - Very high curve across all λ
     - Huge area under curve
     - Highly repetitive/bland

3. **Interpretation Guide**
   - Low, flat curve → distributions very similar → high MAUVE
   - High peak in middle → distributions quite different → low MAUVE
   - Normalization explanation: area normalized against maximum possible divergence

4. **Real-World Examples (2026 Benchmarks)**
   - Frontier closed models: very low curve, MAUVE 0.92–0.96
   - Top open models: close to frontier, MAUVE 0.86–0.91
   - Older dense models: higher peak, MAUVE 0.82–0.87

5. **Plotting the Curve in Code**
   - Code example using `mauve-text` package
   - Matplotlib plotting example
   - Accessing `divergences_quantiles` from MAUVE results
   - Visualization best practices

6. **Key Insight**
   - The lower and flatter the curve, the better the model matches human text distribution
   - This visualization is the heart of MAUVE

## Integration with Existing Knowledge

This visual explanation complements:

- **MAUVE computation details**: Provides visual understanding of the mathematical formulation
- **MAUVE evaluation code**: Shows how to visualize the results
- **MAUVE comparison table**: Helps interpret the scores in context

## Knowledge Base Structure

```
LLM Decoding Strategies Knowledge:
├── LLM_DECODING_STRATEGIES_2026.md (Comparisons & Decision Guides)
├── BEAM_SEARCH_VARIANTS_2026.md (Beam Search Variants Overview)
├── GRID_BEAM_SEARCH_2026.md (Grid Beam Search Guide)
├── GRID_BEAM_SEARCH_FROM_SCRATCH.py (Grid Beam Search Implementation)
├── CONTRASTIVE_SEARCH_MATH_2026.md (Mathematical Details)
└── DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md (Code Examples - NOW WITH MAUVE Curve Visualization) ⭐
```

## Status

✅ **Complete** - Comprehensive visual illustration of MAUVE divergence curve fully integrated, providing intuitive understanding of how MAUVE scores are computed and what they mean visually.
