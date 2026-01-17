# Knowledge Base Update V30: MAUVE vs JS Divergence Curve Visualizations and Code

**Date:** 2026-01-10  
**Update Type:** Content Addition  
**Document Updated:** `DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md`

## Summary

Added comprehensive visual illustrations and Python code examples for comparing MAUVE and JS divergence curves, including simulated curve generation and real MAUVE computation with curve plotting.

### Content Added

1. **Visual Comparison: MAUVE vs JS Divergence Curves Section**
   - Introduction to visual comparison concept
   - Explanation of axes (λ vs divergence value)
   - Three quality level examples with ASCII art diagrams:
     - **Excellent Model (MAUVE ≈ 0.95, JS ≈ 0.06)**: Very low, flat MAUVE curve; low symmetric JS peak
     - **Good but Repetitive (MAUVE ≈ 0.70, JS ≈ 0.20)**: Higher MAUVE peak in middle; moderate JS peak
     - **Poor Model (MAUVE ≈ 0.30, JS ≈ 0.45)**: Very high MAUVE curve; high JS peak
   - Key takeaways from the curves:
     - MAUVE curve characteristics (worst-case divergence, sensitive to degeneration, asymmetric)
     - JS divergence characteristics (symmetric, averages KL, less sensitive)
   - Bottom line (2026 perspective) with usage recommendations

2. **Code Example 1: Simulated Curve Comparison**
   - Complete Python code for generating and visualizing comparison curves
   - Helper functions:
     - `simulate_mauve_curve()`: Simulates MAUVE max-divergence curve with peak height, width, and asymmetry parameters
     - `simulate_js_curve()`: Simulates symmetric JS divergence curve (parabolic shape)
   - Three quality level scenarios with realistic parameters
   - Matplotlib visualization with three subplots
   - Approximate MAUVE score annotations
   - Expected output description
   - Key takeaways from visualization

3. **Code Example 2: Real MAUVE Computation with Curve Plotting**
   - Complete, ready-to-run Python code using official `mauve-text` library
   - Configuration section (featurizer, batch size, sample size)
   - GPT-2-large featurizer loading (standard from original paper)
   - Human reference text loading (WikiText-103 test set)
   - Model text generation (Llama-3.1-8B-Instruct example)
   - Real MAUVE computation with `compute_mauve()` function
   - Results printing (MAUVE score, frontier divergence, info divergence, cluster counts, sample sizes)
   - MAUVE divergence curve plotting with matplotlib
   - Area annotation on plot
   - Expected runtime and output description
   - Tips for optimization (sample size, featurizer choice, saving results)

## Integration with Existing Knowledge

This code complements:

- **MAUVE vs JS comparison table**: Provides visual and code-based understanding of the differences
- **MAUVE computation details**: Shows practical implementation of the theoretical concepts
- **MAUVE divergence curve illustration**: Adds comparison perspective with JS divergence curves

## Knowledge Base Structure

```text
LLM Decoding Strategies Knowledge:
├── LLM_DECODING_STRATEGIES_2026.md (Comparisons & Decision Guides)
├── BEAM_SEARCH_VARIANTS_2026.md (Beam Search Variants Overview)
├── GRID_BEAM_SEARCH_2026.md (Grid Beam Search Guide)
├── GRID_BEAM_SEARCH_FROM_SCRATCH.py (Grid Beam Search Implementation)
├── CONTRASTIVE_SEARCH_MATH_2026.md (Mathematical Details)
└── DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md (Code Examples - NOW WITH MAUVE/JS Curve Code) ⭐
```text

## Status

✅ **Complete** - Comprehensive visual illustrations and Python code examples for MAUVE vs JS divergence curve comparison fully integrated, providing both simulated visualization and real computation capabilities.
