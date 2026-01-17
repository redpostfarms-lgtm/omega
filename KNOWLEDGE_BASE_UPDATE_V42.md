# Knowledge Base Update V42: Sigmoid vs Linear Alpha Ramp Comparison

**Date:** 2026-01-10  
**Update Type:** Code Examples Enhancement  
**Document Updated:** `DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md`

## Summary

Added comprehensive comparison section between sigmoid-shaped and linear alpha ramps with visualizations, detailed explanations, and practical tuning guidance.

### Content Added to DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md

1. **Comparison: Sigmoid vs Linear Alpha Ramps Section**
   - **Introduction**: Explanation of comparison purpose and parameter settings
     - All curves use base_alpha = 0.3, max_alpha = 1.0
     - Sigmoid curves use steepness = 5.0 and midpoint = 0.5
   
   - **Side-by-Side Comparison ASCII Visualization**:
     - Combined curve showing both linear and sigmoid (steepness=5.0) on same graph
     - Legend explaining which curve is which
     - Visual comparison showing smooth S-curve vs straight line
   
   - **Sigmoid with Steepness = 8.0 Comparison**:
     - Second comparison showing sigmoid (steepness=8.0) vs linear
     - Visual demonstration of sharper S-curve behavior
     - Shows how steeper sigmoid differs from linear
   
   - **How the Curves Compare Table**:
     - **Linear ramp**: Characteristics, pros (simple, predictable, easy tuning), cons (sudden change, less natural)
     - **Sigmoid ramp, steepness=5.0**: Characteristics, pros (natural, smooth, popular in 2026), cons (slightly harder to tune)
     - **Sigmoid ramp, steepness=8.0**: Characteristics, pros (long creative phase, sudden control), cons (can feel abrupt)
   
   - **Visual Comparison Breakdown**:
     - **Linear Ramp**: Formula, constant rate explanation, no adaptation
     - **Sigmoid Ramp, steepness=5.0**: Formula, gradual start, rapid middle, smooth finish, balanced option
     - **Sigmoid Ramp, steepness=8.0**: Formula, very long creative phase, sharp transition, quick stabilization
   
   - **Tuning Guidance**:
     - Prefer sigmoid (steepness 4–8) for most creative/long-form tasks
     - Use linear for predictable behavior or simpler tuning
     - Higher steepness (8–12) → longer creative phase followed by quick tightening
     - Lower steepness (3–5) → very gradual control increase
   
   - **When to Use Each Table**:
     - Use case recommendations for each ramp type
     - Creative/long-form generation → Sigmoid (steepness 5–8)
     - Epic stories (>300 tokens) → Sigmoid (steepness 8–12)
     - Predictable/technical text → Linear
     - Very long narratives (>500 tokens) → Sigmoid (steepness 3–5)
   
   - **Mathematical Comparison**:
     - Linear formula: $\alpha_t = \alpha_{\text{base}} + (\alpha_{\text{max}} - \alpha_{\text{base}}) \times \frac{t}{T}$
     - Sigmoid formula: $\alpha_t = \alpha_{\text{base}} + \frac{(\alpha_{\text{max}} - \alpha_{\text{base}})}{1 + \exp(-\text{steepness} \times (t/T - \text{midpoint}))}$
     - Variable definitions and explanations
     - Clear comparison of formulas

## Key Improvements

### Visual Comparison
- **Side-by-side curves**: Clear visual comparison of different ramp types
- **Multiple examples**: Both moderate and sharp sigmoid comparisons
- **Legend**: Easy identification of different curve types

### Detailed Analysis
- **Comprehensive table**: Pros and cons of each ramp type
- **Mathematical formulas**: Exact formulas for both approaches
- **Use case recommendations**: When to use each type

### Practical Guidance
- **Tuning guidance**: Clear recommendations for different scenarios
- **Use case table**: Specific recommendations based on generation type
- **Steepness guidance**: How to choose appropriate steepness values

## Integration with Existing Knowledge

These additions complement:
- **Existing sigmoid implementation**: Comparison explains why sigmoid is preferred
- **Existing linear implementation**: Shows when linear might be appropriate
- **Existing visualization sections**: Adds comparative context to individual visualizations
- **Mathematical documentation**: Formulas match those in `CONTRASTIVE_SEARCH_MATH_2026.md`

## Knowledge Base Structure

```text
LLM Decoding Strategies Knowledge:
├── LLM_DECODING_STRATEGIES_2026.md (Comparisons & Decision Guides)
├── BEAM_SEARCH_VARIANTS_2026.md (Beam Search Variants Overview)
├── GRID_BEAM_SEARCH_2026.md (Grid Beam Search Guide)
├── GRID_BEAM_SEARCH_FROM_SCRATCH.py (Grid Beam Search Implementation)
├── CONTRASTIVE_SEARCH_MATH_2026.md (Mathematical Details)
└── DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md (Code Examples - NOW WITH Ramp Comparison) ⭐
    └── Pattern 5: Contrastive Search
        └── Section 6: Sigmoid-Shaped Alpha Ramp
            ├── Implementation Code
            ├── Visualization Sections
            └── Comparison: Sigmoid vs Linear (NEW)
                ├── Side-by-Side Visualizations
                ├── Comparison Table
                ├── When to Use Each
                └── Mathematical Comparison
```text

## Status

✅ **Complete** - Comprehensive comparison section between sigmoid and linear alpha ramps with side-by-side visualizations, detailed comparison table, use case recommendations, and mathematical formulas fully integrated into the code examples document, providing clear guidance for choosing between ramp types.
