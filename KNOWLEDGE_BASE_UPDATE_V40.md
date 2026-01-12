# Knowledge Base Update V40: Enhanced Contrastive Search Details & Adaptive Alpha Implementations

**Date:** 2026-01-10  
**Update Type:** Code Examples Enhancement  
**Document Updated:** `DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md`

## Summary

Added comprehensive contrastive search mathematical details, enhanced code implementation, and sigmoid-shaped alpha ramp variant to the code examples document.

### Content Added to DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md

1. **Enhanced Pattern 5: Contrastive Search Section**
   - **Mathematical Formulation Section**:
     - Complete explanation of the original 2022 NeurIPS paper
     - Paper citation with authors, arXiv, and GitHub repo
     - Core mathematical formulation: $s_t(y) = \log p(y | x_{<t}) - \alpha \times \max_{i=1}^{t-1} \text{sim}(h_t(y), h_i)$
     - Detailed explanation of each component
     - Greedy and sampling versions of selection
   
   - **Why This Formula Works (Intuition & Derivation)**:
     - Likelihood term explanation (coherence and grammatical correctness)
     - Contrastive penalty explanation (diversity and anti-repetition)
     - Max operator rationale (conservative worst-case similarity)
     - Alpha trade-off explanation
   
   - **Practical Approximation Section**:
     - Top-k approximation (most common)
     - Embedding proxy (fastest)
     - Current hidden proxy (simplest)
     - Computational complexity discussion
   
   - **Typical Parameters & Behavior (2026) Table**:
     - Alpha parameter range and effects
     - Top-k parameter range and effects
     - Temperature parameter range and effects
     - Repetition penalty parameter range and effects
     - Most popular combination in 2026
   
   - **Summary of the Original Derivation**:
     - Contrastive score explanation
     - Likelihood term → coherence
     - Contrastive penalty → diversity (lexical + semantic)
     - Why it avoids both exact word repetition and semantic loops

2. **New Section 6: Sigmoid-Shaped Alpha Ramp Variant**
   - **Complete implementation**: `sigmoid_alpha_contrastive_search()` function
   - **Sigmoid formula**:
     $$\alpha_t = \text{base\_alpha} + \frac{(\text{max\_alpha} - \text{base\_alpha})}{1 + \exp(-\text{steepness} \times (\text{progress} - \text{midpoint}))}$$
   - **Key Features**:
     - Smooth, non-linear transition
     - Starts very low (creative/exploratory early)
     - Gradually increases in the middle
     - Approaches maximum value asymptotically toward the end
   - **Parameters**:
     - `base_alpha`: minimum value (early generation) - 0.2–0.5
     - `max_alpha`: maximum value (late generation) - 0.9–1.2
     - `steepness`: controls sharpness of transition - 4.0–8.0
     - `midpoint`: where curve is centered - 0.4–0.6
   - **Behavior explanation**:
     - Very slow increase at beginning → high creativity
     - Rapid transition in middle
     - Asymptotic approach to max_alpha → very strong penalty late
   - **Typical tuning values (2026 practice)**: Complete recommendations
   - **Why Sigmoid Ramp**: Advantages over linear/exponential
   - **Use case**: Excellent for very long generations (>200 tokens)
   - **Usage example**: Complete code with model loading and generation

3. **Section Renumbering**
   - Updated "Faster Version using vLLM" from section 6 to section 7

## Key Improvements

### Mathematical Details
- **Complete formulation**: All equations and notation explained
- **Intuition**: Clear explanation of why it works
- **Practical approximations**: Real-world implementation strategies
- **Parameter guidance**: Comprehensive recommendations for 2026

### Adaptive Alpha Variants
- **Three ramp types**: Linear (already existed), Exponential (already existed), Sigmoid (new)
- **Sigmoid advantages**: Smoother transition, natural behavior, fine control
- **Complete implementations**: Production-ready code for all variants

## Integration with Existing Knowledge

These additions complement:
- **Existing contrastive search examples**: Enhanced with detailed mathematical foundation
- **Existing adaptive alpha variants**: Added sigmoid ramp for complete coverage
- **Mathematical documentation**: Matches formulations in `CONTRASTIVE_SEARCH_MATH_2026.md`
- **Decision guides**: Detailed explanation supports recommendations in `LLM_DECODING_STRATEGIES_2026.md`

## Knowledge Base Structure

```
LLM Decoding Strategies Knowledge:
├── LLM_DECODING_STRATEGIES_2026.md (Comparisons & Decision Guides)
├── BEAM_SEARCH_VARIANTS_2026.md (Beam Search Variants Overview)
├── GRID_BEAM_SEARCH_2026.md (Grid Beam Search Guide)
├── GRID_BEAM_SEARCH_FROM_SCRATCH.py (Grid Beam Search Implementation)
├── CONTRASTIVE_SEARCH_MATH_2026.md (Mathematical Details)
└── DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md (Code Examples - NOW WITH Enhanced Details & Sigmoid) ⭐
    └── Pattern 5: Contrastive Search
        ├── Mathematical Formulation (Complete)
        ├── Practical Approximation
        ├── Typical Parameters & Behavior
        ├── Section 4: Adaptive Alpha (Linear)
        ├── Section 5: Exponential Alpha Ramp
        └── Section 6: Sigmoid-Shaped Alpha Ramp (NEW)
```

## Status

✅ **Complete** - Comprehensive contrastive search mathematical details with complete formulation, intuition, and practical approximations, plus sigmoid-shaped alpha ramp variant implementation fully integrated into the code examples document, providing complete coverage of all major adaptive alpha ramp types with detailed mathematical foundation.
