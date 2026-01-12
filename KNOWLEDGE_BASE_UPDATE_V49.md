# Knowledge Base Update V49: Full Hybrid Generation, Contrastive Search Details, and Adaptive Alpha

**Date:** 2026-01-10  
**Update Type:** Code Examples Enhancement  
**Document Updated:** `DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md`

## Summary

Added comprehensive hybrid generation code, detailed contrastive search mathematical explanation, complete implementation, and adaptive alpha variant with exponential ramp.

### Content Added to DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md

1. **New Section: Full Hybrid Generation: Contrastive → Diverse Beam → Nucleus Polish**
   
   - **Complete three-phase hybrid implementation**:
     - Phase 1: Contrastive search (coherent main body)
     - Phase 2: Diverse beam search (multiple draft endings)
     - Phase 3: Nucleus polish (natural final touch)
   
   - **Complete functions**:
     - `contrastive_step()`: Single contrastive search step
     - `nucleus_polish_step()`: Single nucleus sampling step for polish
     - `hybrid_contrastive_beam_nucleus()`: Full three-phase generation function
   
   - **Example usage**:
     - Real model (Llama-3.1-8B-Instruct)
     - Production parameter values
     - Complete runnable example
   
   - **Documentation**: Clear explanation of each phase and its purpose

2. **New Section: Contrastive Search: Mathematical Details and Original Derivation**
   
   - **Complete paper citation**:
     - "A Contrastive Framework for Neural Text Generation" (Su et al. 2022)
     - NeurIPS 2022 (Spotlight)
     - arXiv link and GitHub implementation link
   
   - **Core mathematical formulation**:
     - Complete score formula: $s_t(y) = \log p(y | x_{<t}) - \alpha \times \max_{i=1}^{t-1} \text{sim}(h_t(y), h_i)$
     - Detailed explanation of each component
     - Greedy and sampling versions
   
   - **Why it works**:
     - Likelihood term explanation (coherence)
     - Contrastive penalty explanation (diversity)
     - Intuition and derivation
   
   - **Practical approximations**:
     - Top-k approximation (most common)
     - Embedding proxy (fastest)
     - Current hidden proxy (simplest)
   
   - **Typical parameters & behavior table**:
     - 4 parameters (alpha, top_k, temperature, repetition_penalty)
     - Typical ranges and effects
     - Most popular combination
   
   - **Summary of original derivation**: Why the formula works

3. **New Section: Complete Contrastive Search Implementation**
   
   - **Full `contrastive_search()` function**:
     - Complete implementation following original paper
     - Top-k approximation for efficiency
     - Embedding proxy for hidden states
     - Both greedy and sampling modes
     - Optional repetition penalty
     - Comprehensive docstring
   
   - **Key implementation details**:
     - Likelihood term preservation
     - Contrastive penalty calculation
     - Top-k approximation
     - Hidden state proxy
     - Safety features
     - Flexibility (sampling vs greedy)
   
   - **Example usage**:
     - Real model (Llama-3.1-8B-Instruct)
     - Production parameter values
     - Complete runnable example
   
   - **Typical parameter recommendations (2026)**: Specific values and ranges

4. **New Section: Adaptive Alpha Variant (Exponential Ramp)**
   
   - **Complete `adaptive_alpha_contrastive_search()` function**:
     - Exponential adaptive alpha formula
     - Starts low for creativity
     - Grows exponentially for anti-repetition
     - Optional cap to prevent extremes
     - Comprehensive docstring
   
   - **Key features**:
     - Formula: $\alpha_t = \text{base\_alpha} \times \text{growth\_rate}^{t / \text{max\_new\_tokens}}$
     - Behavior explanation (early vs late)
     - Typical values (2026 practice)
   
   - **Example usage**:
     - Real model (Llama-3.1-8B-Instruct)
     - Production parameter values
     - Complete runnable example
   
   - **When to use**: Long-form creative and reasoning generation

## Key Improvements

### Hybrid Generation
- **Three-phase system**: Combines best methods for different phases
- **Complete implementation**: All three phases fully implemented
- **Production-ready**: Real model examples with recommended parameters
- **Clear documentation**: Purpose of each phase explained

### Mathematical Foundation
- **Complete citation**: Original paper details and links
- **Full formula**: Mathematical notation with explanations
- **Derivation explanation**: Why the formula works
- **Practical approximations**: Real-world implementations
- **Parameter table**: Comprehensive parameter guide

### Complete Implementation
- **Production-ready code**: Full contrastive search implementation
- **Follows original paper**: Closely matches mathematical derivation
- **Efficient approximations**: Top-k and embedding proxy
- **Flexible modes**: Greedy and sampling
- **Safety features**: Repetition penalty included

### Adaptive Alpha
- **Exponential ramp**: Smooth transition from creativity to control
- **Formula explanation**: Mathematical definition
- **Behavior description**: Early vs late generation
- **Typical values**: Production recommendations
- **Use cases**: When to use this variant

## Integration with Existing Knowledge

These additions complement:
- **Existing contrastive search sections**: Provides deeper mathematical foundation
- **Existing hybrid examples**: More complete hybrid implementation
- **Existing adaptive alpha sections**: Exponential variant addition
- **Mathematical documentation**: Practical implementations of theory

## Knowledge Base Structure

```
LLM Decoding Strategies Knowledge:
├── LLM_DECODING_STRATEGIES_2026.md (Comparisons & Decision Guides)
├── BEAM_SEARCH_VARIANTS_2026.md (Beam Search Variants Overview)
├── GRID_BEAM_SEARCH_2026.md (Grid Beam Search Guide)
├── GRID_BEAM_SEARCH_FROM_SCRATCH.py (Grid Beam Search Implementation)
├── CONTRASTIVE_SEARCH_MATH_2026.md (Mathematical Details)
└── DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md (Code Examples - NOW WITH Hybrid & Adaptive Alpha) ⭐
    └── Pattern 5: Contrastive Search
        └── Section 6: Sigmoid-Shaped Alpha Ramp
            ├── Implementation Code
            ├── Mathematical Formula
            ├── Matplotlib Plotting Code
            ├── Interactive Plotly Versions
            ├── Interactive Overlay Versions
            ├── Understanding top_k and top_p Parameters
            ├── Code Examples: Top-p, Top-k, and Hybrid Implementation
            ├── Full Hybrid Generation: Contrastive → Diverse Beam → Nucleus Polish (NEW)
            ├── Contrastive Search: Mathematical Details and Original Derivation (NEW)
            ├── Complete Contrastive Search Implementation (NEW)
            └── Adaptive Alpha Variant (Exponential Ramp) (NEW)
```

## Status

✅ **Complete** - Comprehensive hybrid generation code (Contrastive → Diverse Beam → Nucleus Polish), complete contrastive search mathematical explanation with original paper citation and derivation, full production-ready contrastive search implementation following the original 2022 paper, adaptive alpha variant with exponential ramp, all with real model examples, production parameter values, comprehensive docstrings, and detailed explanations fully integrated into the code examples document, providing both theoretical understanding and practical implementation tools for advanced contrastive search techniques.
