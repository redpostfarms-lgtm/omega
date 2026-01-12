# Knowledge Base Update V47: Interactive Plotly Versions & Parameter Explanations (top_k, top_p)

**Date:** 2026-01-10  
**Update Type:** Code Examples Enhancement  
**Document Updated:** `DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md`

## Summary

Added interactive Plotly versions of sigmoid alpha ramp visualizations with sliders, plus comprehensive explanations of top_k and top_p parameters with detailed comparison tables and tuning guidance.

### Content Added to DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md

1. **New Section: Interactive Plotly Versions (Advanced)**
   
   **1.1. Basic Interactive Version with Steepness Slider**
   - **Complete Plotly code** with interactive dropdown menu
   - **Multiple steepness values** (3.0, 5.0, 8.0, 12.0) with color coding
   - **Interactive features**: Show all curves or focus on specific steepness
   - **Unified hover info**: Shows values for all visible curves
   - **Zoom/pan enabled**
   - **Usage instructions**: How to run in Jupyter/Colab environments
   
   **1.2. Interactive Version with All Parameter Sliders**
   - **Complete Plotly code** with four sliders:
     - base_alpha (0.1 to 0.8)
     - max_alpha (0.8 to 1.3)
     - steepness (2.0 to 15.0)
     - midpoint (0.2 to 0.8)
   - **Real-time curve updates**
   - **Detailed usage instructions**
   - **Observations guide**: What to expect when adjusting each parameter

2. **New Section: Interactive Overlay Versions (Temperature and top_k)**
   
   **2.1. Interactive Version with Temperature Overlay**
   - **Plotly code** with dual y-axes (alpha and temperature)
   - **Temperature overlay slider** (0.5 to 1.5)
   - **Visualizes interaction** between alpha ramp and temperature
   - **Dashed line styling** for temperature overlay
   - **Usage and observation guides**
   
   **2.2. Interactive Version with top_k Overlay**
   - **Plotly code** with top_k overlay
   - **top_k overlay slider** (10 to 100)
   - **Visualizes candidate pool size** relative to alpha
   - **Observation guide** for understanding interactions
   - **Note about full interactivity** (Dash/callbacks for production)

3. **New Section: Understanding top_k and top_p Parameters**
   
   **3.1. The top_k Parameter in Contrastive Search**
   - **Complete explanation** of how top_k works
   - **Step-by-step process**: From probability computation to token selection
   - **Comprehensive effects table**:
     - 6 top_k ranges (5–10, 10–20, 30–50, 60–100, >100)
     - 7 aspects per range (pool size, coherence, diversity, speed, risk, feeling, use case)
   - **Visual intuition**: Example probability distribution with different top_k values
   - **Tuning guidance (2026 practice)**:
     - Starting values (40–50 sweet spot)
     - Short vs long-form recommendations
     - Troubleshooting (too repetitive vs too random)
     - Pairing with alpha
   - **Most popular combination**: alpha=0.7, top_k=40–50, temperature=0.8–0.9, repetition_penalty=1.1
   
   **3.2. The top_p Parameter (Nucleus Sampling)**
   - **Complete explanation**: What top_p does and why it's important
   - **Historical context**: 2019 paper by Holtzman et al.
   - **Real-world adoption**: Used by Grok, Claude, GPT, Gemini, Llama, Qwen, etc.
   - **Step-by-step example**: Probability distribution with cumulative probabilities
   - **Key behavior table**: How nucleus size adapts to model confidence
   - **Advantages over top-k**: Dynamic adaptation, prevents low-prob tokens, more natural text
   - **Typical values (2026)**: p=0.90–0.95, temperature=0.7–0.9, penalties
   - **Most popular production combo**: top_p=0.92–0.95, temperature=0.8, repetition_penalty=1.1
   - **Visual intuition**: High vs low confidence scenarios
   - **Bottom line**: Why top_p is the gold standard for conversational text
   
   **3.3. Comparison: top_p vs top_k**
   - **Comprehensive comparison table**: 11 aspects comparing top-k and top-p
   - **Visual intuition**: Same probability distribution example showing both methods
   - **When to choose which**: Best practices for 2026
   - **Most popular production setting**: Complete parameter combination
   - **Real-world usage**: Which method dominates and why

## Key Improvements

### Interactive Visualizations
- **Plotly integration**: Professional interactive plots with sliders
- **Multiple parameter controls**: All four sigmoid parameters adjustable
- **Overlay support**: Temperature and top_k overlays for hybrid systems
- **User-friendly**: Clear instructions and observation guides
- **Production-ready structure**: Notes about full interactivity with Dash/callbacks

### Parameter Explanations
- **Comprehensive coverage**: Complete explanations of top_k and top_p
- **Practical tables**: Effects, comparisons, and tuning guidance
- **Visual examples**: Probability distributions and cumulative calculations
- **Real-world context**: 2026 best practices and popular combinations
- **Troubleshooting guides**: How to adjust for common issues

### Educational Value
- **Step-by-step processes**: Clear explanations of how parameters work
- **Comparison tables**: Side-by-side analysis of top_k vs top_p
- **Tuning guidance**: Specific recommendations for different use cases
- **Historical context**: Origins and evolution of nucleus sampling
- **Visual intuition**: Examples that make concepts concrete

## Integration with Existing Knowledge

These additions complement:
- **Existing sigmoid implementations**: Interactive visualizations for the code
- **Existing contrastive search code**: Parameter explanations for the implementations
- **Existing comparison sections**: More detailed parameter analysis
- **Mathematical documentation**: Practical application of theoretical concepts

## Knowledge Base Structure

```
LLM Decoding Strategies Knowledge:
├── LLM_DECODING_STRATEGIES_2026.md (Comparisons & Decision Guides)
├── BEAM_SEARCH_VARIANTS_2026.md (Beam Search Variants Overview)
├── GRID_BEAM_SEARCH_2026.md (Grid Beam Search Guide)
├── GRID_BEAM_SEARCH_FROM_SCRATCH.py (Grid Beam Search Implementation)
├── CONTRASTIVE_SEARCH_MATH_2026.md (Mathematical Details)
└── DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md (Code Examples - NOW WITH Interactive Plots & Parameter Guides) ⭐
    └── Pattern 5: Contrastive Search
        └── Section 6: Sigmoid-Shaped Alpha Ramp
            ├── Implementation Code
            ├── Mathematical Formula
            ├── Matplotlib Plotting Code
            ├── Interactive Plotly Versions (NEW)
            │   ├── Basic Interactive (Steepness Slider)
            │   └── All Parameter Sliders
            ├── Interactive Overlay Versions (NEW)
            │   ├── Temperature Overlay
            │   └── top_k Overlay
            ├── Understanding top_k and top_p Parameters (NEW)
            │   ├── The top_k Parameter
            │   ├── The top_p Parameter (Nucleus Sampling)
            │   └── Comparison: top_p vs top_k
            └── Visualization Sections (ASCII art)
```

## Status

✅ **Complete** - Interactive Plotly versions with sliders for all sigmoid parameters, temperature and top_k overlays, comprehensive explanations of top_k and top_p parameters with detailed comparison tables, tuning guidance, visual examples, and real-world 2026 best practices fully integrated into the code examples document, providing both interactive visualization tools and deep understanding of key contrastive search parameters.
