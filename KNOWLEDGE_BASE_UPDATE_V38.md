# Knowledge Base Update V38: Enhanced Adaptive Alpha Variants & Side-by-Side Comparison

**Date:** 2026-01-10  
**Update Type:** Code Examples Enhancement  
**Document Updated:** `DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md`

## Summary

Added improved adaptive alpha implementations (linear and exponential ramps) and a comprehensive side-by-side code comparison between contrastive search and diverse beam search.

### Content Added to DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md

1. **Enhanced Section 4: Adaptive Alpha Variant (Linear Ramp)**

   - **Complete standalone function**: `adaptive_contrastive_search()` with full implementation
   - **Improved features:**
     - Linear alpha ramp: base_alpha → max_alpha over generation
     - Repetition penalty support
     - Better hidden state tracking
     - Sampling and greedy modes
     - Complete error handling
   - **Key Features documentation:**
     - Linear alpha ramp explanation
     - Dynamic penalty behavior
     - Approximation method
     - Safety features
     - Flexibility options
   - **Tuning Recommendations (2026):**
     - Long-form (>150 tokens): base_alpha=0.5, max_alpha=0.9–1.0
     - Medium-length (50–150): base_alpha=0.6, max_alpha=0.8
     - Short/precise: base_alpha=0.7, max_alpha=0.7 (fixed)
     - Top-k recommendations: 40–60
   - **Usage example**: Complete code with model loading and generation

2. **New Section 5: Exponential Alpha Ramp Variant**

   - **Complete implementation**: `exponential_contrastive_search()` function
   - **Exponential formula**: alpha_t = base_alpha × growth_rate^(t / max_new_tokens)
   - **Key Features:**
     - Starts low (e.g. 0.4) for early creativity
     - Grows exponentially → becomes very strong (e.g. 1.0–1.5) toward the end
     - Prevents late-stage repetition and semantic drift
   - **Typical values:**
     - `base_alpha`: 0.3–0.6
     - `growth_rate`: 1.6–2.2 (higher = faster ramp-up)
     - `top_k`: 40–60
   - **Alternative: Exponential with saturation**
     - Code snippet for saturating exponential curve
     - Uses: alpha = max_alpha - (max_alpha - base_alpha) * exp(-growth_rate * progress)
     - Smoother, saturating curve option
   - **Usage example**: Complete code with model loading and generation

3. **New Section 5.5: Contrastive Search vs Diverse Beam Search - Side-by-Side Comparison**

   - **Complete comparison implementation**: Both strategies in consistent style
   - **Common setup code**: Shared model loading and prompt setup
   - **1. Contrastive Search Implementation:**
     - Complete function with all features
     - Hidden state tracking
     - Repetition penalty
     - Contrastive penalty computation
     - Usage example
   - **2. Diverse Beam Search Implementation:**
     - Hugging Face built-in usage
     - Parameter configuration
     - Multiple output generation
     - Usage example
   - **Key Differences in Practice Table:**
     - 8 comparison aspects:
       - Output Style
       - Randomness
       - Repetition Prevention
       - Speed
       - Use Case
       - Parameter Tuning
       - Typical 2026 Preference
   - **How to Choose Between Them:**
     - Clear decision guidance
     - Use case recommendations
     - Hybrid approach suggestion

4. **Section Renumbering**
   - Updated "Faster Version using vLLM" from section 5 to section 6

## Key Improvements

### Adaptive Alpha Variants
- **Production-ready**: Complete standalone functions with all features
- **Better documentation**: Detailed explanations and tuning recommendations
- **Multiple ramp options**: Linear and exponential variants
- **Alternative options**: Exponential with saturation variant

### Side-by-Side Comparison
- **Practical comparison**: Real code implementations for both strategies
- **Consistent style**: Same setup and prompt for fair comparison
- **Comprehensive table**: 8 key differences documented
- **Decision guidance**: Clear recommendations for choosing between strategies

## Integration with Existing Knowledge

These additions complement:
- **Existing contrastive search examples**: Enhanced with improved adaptive variants
- **Existing diverse beam search examples**: Provides direct comparison
- **Mathematical documentation**: Adaptive alpha variants match mathematical formulations in `CONTRASTIVE_SEARCH_MATH_2026.md`
- **Decision guides**: Comparison table supports recommendations in `LLM_DECODING_STRATEGIES_2026.md`

## Knowledge Base Structure

```
LLM Decoding Strategies Knowledge:
├── LLM_DECODING_STRATEGIES_2026.md (Comparisons & Decision Guides)
├── BEAM_SEARCH_VARIANTS_2026.md (Beam Search Variants Overview)
├── GRID_BEAM_SEARCH_2026.md (Grid Beam Search Guide)
├── GRID_BEAM_SEARCH_FROM_SCRATCH.py (Grid Beam Search Implementation)
├── CONTRASTIVE_SEARCH_MATH_2026.md (Mathematical Details)
└── DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md (Code Examples - NOW WITH Enhanced Adaptive Variants & Comparison) ⭐
    ├── Section 4: Enhanced Adaptive Alpha (Linear Ramp)
    ├── Section 5: Exponential Alpha Ramp
    └── Section 5.5: Contrastive vs Diverse Beam Search Side-by-Side Comparison
```

## Status

✅ **Complete** - Enhanced adaptive alpha variants (linear and exponential ramps) and comprehensive side-by-side comparison between contrastive search and diverse beam search fully integrated into the code examples document, providing production-ready implementations with detailed documentation and practical comparison guidance.
