# Knowledge Base Update V48: Complete Code Examples for Top-p, Top-k, and Hybrid Sampling

**Date:** 2026-01-10  
**Update Type:** Code Examples Enhancement  
**Document Updated:** `DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md`

## Summary

Added comprehensive, ready-to-run Python code examples for top-p (nucleus) sampling, top-k sampling, and their hybrid combination, including full autoregressive generation loops with all penalties and production-ready implementations.

### Content Added to DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md

1. **New Section: Code Examples: Top-p, Top-k, and Hybrid Implementation**
   
   **1.1. Top-p (Nucleus) Sampling Implementation**
   - **Complete `top_p_step()` function**:
     - Full parameter support (p, temperature, penalties)
     - Repetition, frequency, and presence penalties
     - Length penalty on EOS
     - Nucleus cutoff calculation
     - Renormalization and sampling
     - Comprehensive docstring
   
   - **Complete `generate_top_p()` function**:
     - Full autoregressive generation loop
     - Token tracking and EOS handling
     - Clean interface with **sampling_kwargs
     - Docstring with usage instructions
   
   - **Example usage**:
     - Real model (Llama-3.1-8B-Instruct)
     - Production parameter values (p=0.92, temperature=0.85, etc.)
     - Complete runnable example
   
   **1.2. Top-k Sampling Implementation (for Comparison)**
   - **Complete `top_k_step()` function**:
     - Same penalty support as top-p
     - Fixed pool size (k tokens)
     - Top-k selection logic
     - Comprehensive docstring
   
   - **Complete `generate_top_k()` function**:
     - Full autoregressive generation loop
     - Same interface as top-p for easy comparison
     - Docstring with usage instructions
   
   - **Example usage**:
     - Same prompt as top-p for direct comparison
     - Production parameter values (k=50, temperature=0.85, etc.)
     - Comparison notes
   
   - **Key Differences section**:
     - Nucleus vs top-k behavior comparison
     - Pool size differences
     - Adaptive vs fixed behavior
     - Production recommendations
   
   **1.3. Hybrid Top-p + Top-k Implementation (Recommended for Production)**
   - **Complete explanation**:
     - Why hybrid is dominant in 2026
     - Comparison with pure methods
     - Real-world adoption (Grok, Claude, GPT, Gemini, etc.)
   
   - **Mathematical/Algorithmic Details**:
     - Step-by-step algorithm explanation
     - 7-step process breakdown
   
   - **Complete `hybrid_top_p_top_k_step()` function**:
     - Top-k pre-filtering (safety net)
     - Top-p nucleus selection (adaptive intelligence)
     - All penalty support
     - Proper cutoff calculation
     - Comprehensive docstring
   
   - **Complete `generate_hybrid_top_p_top_k()` function**:
     - Full autoregressive generation loop
     - Production-ready implementation
     - Docstring emphasizing production use
   
   - **Example usage**:
     - Recommended production settings
     - top_k=50, top_p=0.92, temperature=0.8
     - Complete parameter set
   
   - **Typical Parameter Values (2026 Production Default)**:
     - Complete parameter ranges
     - Most common values
     - Production combination
   
   - **Visual Intuition**:
     - Same probability distribution example
     - Comparison of all three methods
     - When hybrid wins explanation

## Key Improvements

### Complete Implementations
- **Full generation loops**: All three methods include complete autoregressive generation
- **All penalties**: Repetition, frequency, presence, and length penalties
- **Production-ready**: Real model examples with recommended parameters
- **Comprehensive docstrings**: Clear parameter explanations and usage

### Educational Value
- **Side-by-side comparison**: Same prompt, same parameters for easy comparison
- **Key differences section**: Clear explanation of when to use each
- **Visual intuition**: Probability distribution examples
- **Production guidance**: Real-world parameter recommendations

### Hybrid Implementation
- **Correct algorithm**: Proper top-k pre-filtering + top-p nucleus selection
- **Safety + intelligence**: Explains why hybrid combines best of both
- **Production standard**: Emphasized as 2026 gold standard
- **Complete documentation**: Algorithm steps, parameters, examples

### Code Quality
- **Clean structure**: Consistent interfaces across all three methods
- **Error handling**: Proper bounds checking and edge cases
- **Performance**: Efficient tensor operations
- **Readability**: Well-commented and organized code

## Integration with Existing Knowledge

These additions complement:
- **Existing parameter explanations**: Code implements the concepts explained
- **Existing comparison tables**: Code demonstrates the differences
- **Production recommendations**: Code uses recommended parameter values
- **Mathematical documentation**: Code implements the algorithms described

## Knowledge Base Structure

```text
LLM Decoding Strategies Knowledge:
├── LLM_DECODING_STRATEGIES_2026.md (Comparisons & Decision Guides)
├── BEAM_SEARCH_VARIANTS_2026.md (Beam Search Variants Overview)
├── GRID_BEAM_SEARCH_2026.md (Grid Beam Search Guide)
├── GRID_BEAM_SEARCH_FROM_SCRATCH.py (Grid Beam Search Implementation)
├── CONTRASTIVE_SEARCH_MATH_2026.md (Mathematical Details)
└── DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md (Code Examples - NOW WITH Top-p/Top-k/Hybrid Code) ⭐
    └── Pattern 5: Contrastive Search
        └── Section 6: Sigmoid-Shaped Alpha Ramp
            ├── Implementation Code
            ├── Mathematical Formula
            ├── Matplotlib Plotting Code
            ├── Interactive Plotly Versions
            ├── Interactive Overlay Versions
            ├── Understanding top_k and top_p Parameters
            │   ├── The top_k Parameter
            │   ├── The top_p Parameter (Nucleus Sampling)
            │   └── Comparison: top_p vs top_k
            └── Code Examples: Top-p, Top-k, and Hybrid Implementation (NEW)
                ├── Top-p (Nucleus) Sampling Implementation
                ├── Top-k Sampling Implementation
                └── Hybrid Top-p + Top-k Implementation (Recommended)
```text

## Status

✅ **Complete** - Comprehensive, ready-to-run Python code examples for top-p (nucleus) sampling, top-k sampling, and their hybrid combination, including full autoregressive generation loops with all penalties (repetition, frequency, presence, length), production-ready implementations with recommended 2026 parameter values, complete docstrings, example usage with real models, key differences explanations, and visual intuition, fully integrated into the code examples document, providing both theoretical understanding and practical implementation tools for the most widely used decoding strategies in 2026.
