# Knowledge Base Update V39: Hybrid Contrastive-Beam Implementations & Nucleus Sampling

**Date:** 2026-01-10  
**Update Type:** Code Examples Enhancement  
**Document Updated:** `DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md`

## Summary

Added hybrid contrastive-beam search implementations (2-phase and 3-phase), comprehensive nucleus sampling explanation, and complete nucleus sampling code implementation.

### Content Added to DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md

1. **New Example 5: Hybrid Contrastive-Beam Search (Contrastive Body → Diverse Beam Endings)**

   - **Complete 2-phase hybrid implementation**:
     - Phase 1: Contrastive search for fluent, semantically diverse main body
     - Phase 2: Diverse beam search for multiple distinct endings
   - **Key Features:**
     - Contrastive phase (first 100 tokens): Ensures fluent, non-repetitive main body/story development
     - Diverse beam phase (last 60 tokens): Generates multiple distinct, high-quality endings
     - Smooth transition: Beam starts exactly from the contrastive body
     - Complete function: `hybrid_contrastive_beam()` with all parameters
   - **Parameters:**
     - Contrastive: alpha=0.7, top_k=40 (balanced fluency + diversity)
     - Beam: 12 beams, 3 groups, diversity_penalty=1.3 (good variety)
   - **Typical Output Pattern:**
     - Main body: A coherent, flowing story introduction (contrastive prevents early loops)
     - Endings: 3 different high-quality conclusions (e.g., happy, tragic, mysterious)
   - **Usage example**: Complete code with model loading and generation
   - **Use case**: Mirrors how many 2026 reasoning/creative models structure output

2. **New Example 6: Full Hybrid (Contrastive → Diverse Beam → Nucleus Polish)**

   - **Complete 3-phase hybrid implementation**:
     - Phase 1: Contrastive search for coherent main body
     - Phase 2: Diverse beam search for multiple draft endings
     - Phase 3: Nucleus polish for natural final touch
   - **Key Features:**
     - Complete function: `hybrid_contrastive_beam_nucleus()` with all parameters
     - All three phases fully implemented
     - Smooth transitions between phases
   - **How This Hybrid Works:**
     1. Contrastive phase (100 tokens) → Builds a fluent, non-repetitive story core
     2. Diverse beam phase (60 tokens) → Generates multiple distinct, high-quality draft endings
     3. Nucleus polish phase (30 tokens) → Takes the best beam ending and adds natural polish
   - **Result**: A coherent, non-repetitive main story + a beautifully varied, natural-sounding ending
   - **Tuning Tips:**
     - Contrastive phase: Longer = more coherent body (80–150 tokens)
     - Beam phase: More groups = more stylistic variety
     - Polish phase: Short (20–40 tokens) → keeps it natural without losing structure
   - **Usage example**: Complete code with model loading and generation
   - **Use case**: Strong 2026 pattern for high-quality creative/story generation

3. **New Pattern 9: Nucleus Sampling (Top-p Sampling) - Detailed Explanation and Implementation**

   - **Comprehensive Explanation Section:**
     - **Core Idea**: Dynamic selection of tokens based on cumulative probability
     - **Mathematical Formulation**: Complete step-by-step mathematical description
       - Probability computation
       - Sorting and cumulative probability
       - Nucleus cutoff calculation
       - Renormalization and sampling
     - **Key Properties**: Behavior at different p values (0.0, 0.9–0.95, 1.0)
     - **Comparison with Top-k Sampling**: Detailed comparison table (6 aspects)
     - **Typical Parameters in 2026**: Recommended values for p, temperature, penalties
     - **Visual Intuition**: Example with probability distribution
     - **Bottom Line**: Why nucleus sampling is preferred in production systems

   - **Complete Implementation Section:**
     - **Function: `nucleus_sampling_step()`**:
       - Single step of nucleus sampling
       - All major penalties: repetition, frequency, presence, length (on EOS)
       - Temperature scaling
       - Dynamic nucleus cutoff
       - Renormalization and sampling
     - **Function: `generate_with_nucleus()`**:
       - Full autoregressive generation loop
       - Complete penalty tracking
       - EOS handling
       - Works with any causal LM
     - **Key Features:**
       - All major penalties included
       - Dynamic nucleus (adaptive size)
       - Numerical stability
       - Efficient (only sorts once per step)
       - Flexible parameter tuning
     - **Typical Parameter Recommendations (2026):**
       - p = 0.90–0.95
       - temperature = 0.75–0.90
       - repetition_penalty = 1.05–1.15
       - frequency_penalty = 0.1–0.3
       - presence_penalty = 0.1–0.3
       - length_penalty_alpha = 0.6–1.0
     - **Usage example**: Complete code with model loading and generation

## Key Improvements

### Hybrid Implementations
- **Production-ready**: Complete standalone functions with all features
- **Multi-phase support**: 2-phase and 3-phase hybrids
- **Better documentation**: Detailed explanations and tuning recommendations
- **Smooth transitions**: Proper handoff between phases

### Nucleus Sampling
- **Comprehensive explanation**: Mathematical formulation, intuition, and comparison
- **Production-ready implementation**: Complete with all penalties
- **Detailed documentation**: Parameter recommendations and tuning tips
- **Educational value**: Clear explanation of why nucleus sampling is preferred

## Integration with Existing Knowledge

These additions complement:
- **Existing hybrid decoding examples**: Enhanced with contrastive-beam hybrids
- **Existing nucleus sampling usage**: Now with full explanation and standalone implementation
- **Mathematical documentation**: Nucleus sampling matches formulations in related papers
- **Decision guides**: Hybrid examples support recommendations in `LLM_DECODING_STRATEGIES_2026.md`

## Knowledge Base Structure

```text
LLM Decoding Strategies Knowledge:
├── LLM_DECODING_STRATEGIES_2026.md (Comparisons & Decision Guides)
├── BEAM_SEARCH_VARIANTS_2026.md (Beam Search Variants Overview)
├── GRID_BEAM_SEARCH_2026.md (Grid Beam Search Guide)
├── GRID_BEAM_SEARCH_FROM_SCRATCH.py (Grid Beam Search Implementation)
├── CONTRASTIVE_SEARCH_MATH_2026.md (Mathematical Details)
└── DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md (Code Examples - NOW WITH Hybrid Contrastive-Beam & Nucleus) ⭐
    ├── Pattern 8: Hybrid Decoding Approaches
    │   ├── Example 5: Hybrid Contrastive-Beam (2-phase)
    │   └── Example 6: Full Hybrid (Contrastive → Beam → Nucleus) (3-phase)
    └── Pattern 9: Nucleus Sampling (Detailed Explanation + Implementation)
```text

## Status

✅ **Complete** - Hybrid contrastive-beam search implementations (2-phase and 3-phase), comprehensive nucleus sampling explanation with mathematical formulation, and complete nucleus sampling code implementation with all penalties fully integrated into the code examples document, providing production-ready implementations with detailed documentation and practical examples.
