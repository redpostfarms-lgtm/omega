# Beam Search Variants - Comprehensive Guide 2026
**Date:** January 2026  
**Source:** Current LLM Best Practices  
**Status:** Reference Material for Omega Knowledge Base

---

## Overview

Beam search variants are extensions and modifications of the classic beam search algorithm, each designed to address specific limitations of standard beam search (such as repetition, lack of diversity, length bias, or suboptimal global optima). These variants are widely used in modern LLMs (translation, summarization, code generation, reasoning) in 2026.

---

## Beam Search Variants

### 1. Standard (Vanilla) Beam Search

**How it works:**
- At each step, expand all current beams and keep only the top b highest-scoring sequences
- Usually scored by sum of log-probabilities + length penalty

**Strengths:**
- Simple, deterministic
- Often finds very high-quality sequences

**Weaknesses:**
- Severe lack of diversity (beams quickly become almost identical)
- Strong bias toward shorter sequences unless length penalty is tuned

**Typical use:**
- Code completion
- Math/reasoning
- Translation when you want the single best output

**Parameters:**
- `num_beams=4–20`
- `length_penalty=0.6–1.0`

---

### 2. Diverse Beam Search

**How it works:**
- Split total beams into multiple groups (e.g., 4 groups of 5 beams each)
- Run standard beam search within each group
- Add a diversity penalty (usually Hamming distance) across groups to penalize beams that are too similar

**Strengths:**
- Produces multiple meaningfully different high-quality outputs instead of near-identical ones

**Weaknesses:**
- Slightly lower quality on individual beams (due to penalty)
- A bit slower

**Typical use:**
- Creative writing
- Brainstorming
- Paraphrasing
- Generating multiple story endings or dialogue options

**Parameters:**
- `num_beams=12–20`
- `num_beam_groups=4–5`
- `diversity_penalty=0.8–2.0`

**Availability:**
- Built into Hugging Face Transformers (`num_beam_groups` + `diversity_penalty`)

---

### 3. Beam Search with Length Normalization / Penalty

**How it works:**
- Adjust sequence score: `score = logprob_sum / (length ^ α)`
- `α > 1` → strongly favors longer sequences
- `α ≈ 0.6–1.0` → common balance (prevents very short outputs)
- `α < 1` → favors shorter (rarely used)

**Strengths:**
- Fixes the strong bias toward short sequences in vanilla beam search

**Weaknesses:**
- Tuning α is important — wrong value can produce too short or too verbose output

**Typical use:**
- Almost every real-world beam search implementation
- Translation, summarization, reasoning

**Parameters:**
- `length_penalty=0.6–1.0` (Hugging Face default 1.0)

---

### 4. Group Beam Search (Blockwise Beam Search)

**How it works:**
- Similar to diverse beam search but without explicit diversity penalty
- Simply divides beams into groups and keeps top candidates per group
- Often combined with diversity penalty

**Strengths:**
- Guarantees some minimum diversity (each group explores separately)

**Weaknesses:**
- Less controlled diversity than full diverse beam search

**Typical use:**
- When you want simple guaranteed diversity without tuning a penalty parameter

**Parameters:**
- `num_beam_groups=4–8`

---

### 5. Diverse Beam Search with Hamming Diversity (Classic 2016 Version)

**How it works:**
- The original diverse beam search paper uses Hamming distance between sequences as the diversity metric
- Modern implementations (Hugging Face) use similar but sometimes normalized or softened versions

**Strengths:**
- Mathematically principled diversity

**Weaknesses:**
- Can be computationally expensive for very large beam sizes

**Typical use:**
- Research papers
- High-quality creative generation

---

### 6. Beam Search with Lexical Constraints / Constrained Decoding

**How it works:**
- Force beams to follow certain rules (e.g., must include specific words, follow JSON schema, match regex)
- Done via guided search or logit masking

**Strengths:**
- Guarantees structured output (valid JSON, code syntax, API format)

**Weaknesses:**
- Can reduce quality if constraints are too strict

**Typical use:**
- Agent tools
- Structured output generation
- Code completion with syntax rules

**Tools:**
- Outlines
- Guidance
- jsonformer
- Hugging Face constrained beam search

---

### 7. Beam Search + Speculative Decoding

**How it works:**
- Use a small draft model to speculate several tokens ahead
- Beam search verifies/corrects the drafts → massive speedup

**Strengths:**
- 2–4× faster inference with almost same quality

**Weaknesses:**
- Needs good draft model

**Typical use:**
- Production inference (vLLM, TensorRT-LLM, DeepSeek-V3.2 inference)

**Status in 2026:**
- Very common in high-throughput serving

---

## Quick Summary Table (2026 Perspective)

| Variant | Diversity | Quality | Speed | Best For | Real-World Popularity |
| --------- | ----------- | --------- | ------- | ---------- | ---------------------- |
| **Standard Beam** | Very low | Highest | Medium | Code, math, translation | Very high |
| **Diverse Beam** | High | Very high | Medium-slow | Creative writing, brainstorming | High (creative tools) |
| **Length-Normalized Beam** | Low | High | Medium | Any beam search task | Almost universal |
| **Group / Constrained Beam** | Medium | High | Medium | Structured output, agents | Growing fast |
| **Beam + Speculative** | Low | Very high | Fast | Production inference | Very high (serving) |

---

## Bottom Line (January 2026)

### Standard Beam Search:
→ **Gold standard** for precision & single best output

### Diverse Beam Search:
→ **Go-to** when you need multiple distinct high-quality alternatives (creative, planning, paraphrasing)

### Key Points:
- ✅ All serious variants use **length penalty** and **early stopping**
- ✅ Most production chat systems **avoid beam search entirely** (use top-p/top-k) because users prefer natural variation
- ✅ **Diverse beam search is gaining traction** in agents, creative tools, and reasoning systems

---

## Decision Framework

### Choose Standard Beam Search when:
✅ You need the single best, highest-quality output
✅ Deterministic results are required
✅ Use cases: Code completion, math, translation, reasoning

### Choose Diverse Beam Search when:
✅ You need multiple distinct, high-quality alternatives
✅ Use cases: Creative writing, brainstorming, paraphrasing, story generation, dialogue options

### Choose Length-Normalized Beam when:
✅ You need to avoid short sequence bias
✅ Use cases: Translation, summarization, any beam search task

### Choose Constrained Beam Search when:
✅ You need structured output (JSON, code syntax, specific formats)
✅ Use cases: Agent tools, structured output generation, code completion

### Choose Beam + Speculative Decoding when:
✅ You need fast inference in production
✅ Use cases: High-throughput serving, production systems

---

## Implementation Notes

### Standard Beam Search:
```python
{
    "num_beams": 4-20,
    "length_penalty": 0.6-1.0
}
```text

### Diverse Beam Search:
```python
{
    "num_beams": 12-20,
    "num_beam_groups": 4-5,
    "diversity_penalty": 0.8-2.0,
    "length_penalty": 0.6-1.0
}
```text

### Length-Normalized Beam:
```python
{
    "num_beams": 4-20,
    "length_penalty": 0.6-1.0  # Default: 1.0
}
```text

### Constrained Beam Search:
```python
{
    "num_beams": 4-20,
    "constraints": [...],  # Word/phrase constraints
    "force_words_ids": [...],  # Token ID constraints
    "guidance_scale": 1.0-2.0  # Constraint strength
}
```text

### Beam + Speculative Decoding:
```python
{
    "num_beams": 4-20,
    "speculative_decoding": True,
    "draft_model": "...",
    "speculation_length": 4-8
}
```text

---

## 2026 Status

### Production Chat Systems:
- ❌ **Avoid beam search entirely** (use top-p/top-k)
- ✅ Users prefer natural variation
- ✅ Top-k/top-p sampling dominates

### Where Beam Search Thrives:
- ✅ **Code generation** (standard beam)
- ✅ **Creative tools** (diverse beam)
- ✅ **Agent planning** (diverse beam)
- ✅ **Reasoning systems** (standard/diverse beam)
- ✅ **Translation/summarization** (length-normalized beam)
- ✅ **Structured output** (constrained beam)
- ✅ **Production inference** (beam + speculative)

---

## References

- **Date:** January 2026
- **Source:** Current LLM decoding best practices
- **Status:** Active recommendations for 2026
- **Tools:** Hugging Face Transformers, Outlines, Guidance, jsonformer, vLLM, TensorRT-LLM

---

**Document Created:** January 2026  
**Status:** Reference Material  
**Use:** Educational system knowledge base  
**Related:** LLM_DECODING_STRATEGIES_2026.md
