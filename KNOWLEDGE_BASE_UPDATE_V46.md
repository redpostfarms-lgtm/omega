# Knowledge Base Update V46: Mathematical Formula & Plotting Code for Sigmoid Alpha Ramp

**Date:** 2026-01-10  
**Update Type:** Code Examples Enhancement  
**Document Updated:** `DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md`

## Summary

Added comprehensive mathematical formula section for sigmoid alpha ramp and complete Python code for generating and plotting sigmoid curves with various parameter combinations.

### Content Added to DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md

1. **New Section: Mathematical Formula for Sigmoid Alpha Ramp**
   - **Complete formula**: 
     $$\alpha(t) = \alpha_{\text{base}} + (\alpha_{\text{max}} - \alpha_{\text{base}}) \cdot \frac{1}{1 + e^{-k(t - t_0)}}$$
   
   - **Detailed parameter explanations**:
     - $\alpha(t)$ → alpha value at generation step $t$
     - $\alpha_{\text{base}}$ → starting (minimum) alpha value
     - $\alpha_{\text{max}}$ → maximum (asymptotic) alpha value
     - $k$ → steepness parameter (higher = sharper S-curve)
     - $t_0$ → midpoint (inflection point, usually 0.5 = middle)
     - $t$ → normalized progress (0 to 1)
     - $e$ → base of natural logarithm (≈ 2.71828)
   
   - **Equivalent Forms**:
     - Standard logistic form
     - Form with growth rate using $\sigma(x)$ notation
   
   - **Typical Parameter Values (2026 Practice)**:
     - $\alpha_{\text{base}}$: 0.2 – 0.6
     - $\alpha_{\text{max}}$: 0.9 – 1.2
     - $k$ (steepness): 4.0 – 12.0
     - $t_0$ (midpoint): 0.4 – 0.7
   
   - **Visual Summary of Parameter Effects**:
     - Higher $k$ → sharper S-curve
     - Lower $k$ → very gradual ramp
     - Lower $t_0$ → earlier strong penalty
     - Higher $t_0$ → longer creative phase
   
   - **Why sigmoid is preferred**: Explanation of smooth behavior change benefits

2. **New Section: Code to Generate and Plot Sigmoid Curves**
   - **Complete Python script**:
     - `sigmoid_ramp()` function with full docstring
     - Mathematical formula in docstring
     - Parameter explanations
   
   - **Plotting code**:
     - Five different parameter combinations plotted
     - Curve 1: Default (base=0.3, max=1.0, steep=5.0, mid=0.5)
     - Curve 2: Higher steepness (steep=10.0, sharp)
     - Curve 3: Lower base_alpha (base=0.2, more creative start)
     - Curve 4: Higher max_alpha (max=1.2, strong late control)
     - Curve 5: Shifted midpoint (mid=0.4, earlier ramp)
   
   - **Visualization features**:
     - Professional matplotlib styling
     - Clear labels and legend
     - Grid for easy reading
     - Custom colors for each curve
     - Dashed line style for shifted midpoint
   
   - **Documentation**:
     - "What You'll See When You Run It" section
     - "How to Customize" section
     - "Example Parameter Effects" section
     - Note about extending the script

## Key Improvements

### Mathematical Foundation
- **Complete formula**: Full mathematical definition with all components
- **Parameter explanations**: Clear descriptions of each variable
- **Equivalent forms**: Alternative mathematical representations
- **Typical values**: Parameter ranges for 2026 practice
- **Visual summary**: Quick reference for parameter effects

### Plotting Code
- **Self-contained script**: Ready-to-run Python code
- **Multiple examples**: Five different parameter combinations
- **Professional visualization**: Clean matplotlib plots
- **Documentation**: Clear instructions for customization
- **Practical examples**: Real-world parameter combinations

### Educational Value
- **Visual learning**: Generate actual plots to understand parameter effects
- **Hands-on tuning**: Users can modify and test different parameters
- **Complete examples**: All major parameter variations demonstrated

## Integration with Existing Knowledge

These additions complement:
- **Existing sigmoid implementation**: Mathematical foundation explains the code
- **Existing visualizations**: Plotting code can generate the same curves
- **Existing parameter documentation**: Formula provides mathematical basis
- **Mathematical documentation**: Forms match those in `CONTRASTIVE_SEARCH_MATH_2026.md`

## Knowledge Base Structure

```text
LLM Decoding Strategies Knowledge:
├── LLM_DECODING_STRATEGIES_2026.md (Comparisons & Decision Guides)
├── BEAM_SEARCH_VARIANTS_2026.md (Beam Search Variants Overview)
├── GRID_BEAM_SEARCH_2026.md (Grid Beam Search Guide)
├── GRID_BEAM_SEARCH_FROM_SCRATCH.py (Grid Beam Search Implementation)
├── CONTRASTIVE_SEARCH_MATH_2026.md (Mathematical Details)
└── DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md (Code Examples - NOW WITH Formula & Plotting) ⭐
    └── Pattern 5: Contrastive Search
        └── Section 6: Sigmoid-Shaped Alpha Ramp
            ├── Implementation Code
            ├── Mathematical Formula for Sigmoid Alpha Ramp (NEW)
            ├── Code to Generate and Plot Sigmoid Curves (NEW)
            └── Visualization Sections
```text

## Status

✅ **Complete** - Comprehensive mathematical formula for sigmoid alpha ramp with detailed parameter explanations, equivalent forms, typical parameter values, and complete Python code for generating and plotting sigmoid curves with multiple parameter combinations fully integrated into the code examples document, providing both theoretical understanding and practical visualization tools.
