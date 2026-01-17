# Knowledge Base Update V34: Contrastive Search Mathematical Derivation

**Date:** 2026-01-10  
**Update Type:** Content Addition  
**Document Updated:** `CONTRASTIVE_SEARCH_MATH_2026.md`

## Summary

Added comprehensive step-by-step mathematical derivation of the contrastive search objective, explaining how the algorithm is derived from standard autoregressive decoding and why it works to prevent degeneration.

### Content Added

1. **Mathematical Derivation (Step-by-Step) Section**
   - Complete derivation from standard autoregressive decoding to contrastive search
   - Six subsections covering the full derivation process

2. **Step 1: Standard Autoregressive Decoding (Baseline)**
   - Standard probability formulation: $p(y | x_{<t}) = \text{softmax}(z_t(y))$
   - Explanation of standard sampling methods
   - Problem statement: why standard methods lead to degeneration

3. **Step 2: Observation: Anisotropy Causes Degeneration**
   - Explanation of anisotropic token representations
   - How clustering in vector space causes high cosine similarity
   - Consequences: high-probability tokens being similar, leading to repetition

4. **Step 3: Contrastive Search Objective**
   - Formal definition of contrastive score:
     $$s_t(y) = \log p(y | x_{<t}) - \alpha \cdot \max_{i=1}^{t-1} \text{sim}(h_t(y), h_i)$$
   - Detailed explanation of each component:
     - Log-probability term (likelihood)
     - Cosine similarity function
     - Hidden state computation
     - Alpha parameter (degeneration penalty strength)
   - Token selection: $\arg\max$ or softmax sampling

5. **Step 4: Why This Works (Derivation Insight)**
   - How contrastive penalty works
   - Effect when hidden state is similar vs. dissimilar
   - Semantic diversity encouragement
   - Likelihood preservation
   - Conservative nature of max operator

6. **Step 5: Practical Approximation (Used in Most Implementations)**
   - Computational complexity problem ($O(V)$ forward passes)
   - Approximation strategies:
     - Top-k candidate consideration
     - Current hidden state as proxy
     - Word embeddings instead of full hidden states
   - Common 2026 approximation:
     $$s_t(y) \approx \log p(y | x_{<t}) - \alpha \cdot \max_{i<t} \text{cos\_sim}(e(y), e(x_i))$$
   - Word embedding approach (cheaper computation)

7. **Step 6: Typical Parameter Values (from Paper & 2026 Practice)**
   - Alpha range: 0.5–1.0 (sweet spot: 0.7–0.8)
   - Top-k range: 10–50
   - Temperature combination: 0.7–0.9

8. **Summary of the Derivation**
   - Key insight: combination of likelihood + contrastive penalty
   - Why it avoids repetition (lexical and semantic)
   - Comparison to top-k/top-p
   - Status in 2026 (strongest decoding method for open-ended generation)

## Integration with Existing Knowledge

This derivation complements:

- **Core Mathematical Idea section**: Provides detailed background for how the formula is derived
- **Practical Formulation section**: Explains the connection between theory and practice
- **SimCTG training section**: Shows how contrastive search addresses the anisotropy problem identified in training
- **Code examples**: Provides theoretical foundation for practical implementations

## Knowledge Base Structure

```text
LLM Decoding Strategies Knowledge:
├── LLM_DECODING_STRATEGIES_2026.md (Comparisons & Decision Guides)
├── BEAM_SEARCH_VARIANTS_2026.md (Beam Search Variants Overview)
├── GRID_BEAM_SEARCH_2026.md (Grid Beam Search Guide)
├── GRID_BEAM_SEARCH_FROM_SCRATCH.py (Grid Beam Search Implementation)
├── DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md (Code Examples)
└── CONTRASTIVE_SEARCH_MATH_2026.md (Mathematical Details - NOW WITH Full Derivation) ⭐
```text

## Status

✅ **Complete** - Comprehensive mathematical derivation of contrastive search fully integrated, providing step-by-step explanation of how the algorithm is derived from standard autoregressive decoding and why it effectively prevents degeneration through contrastive penalty.
