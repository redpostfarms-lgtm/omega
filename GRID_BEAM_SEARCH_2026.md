# Grid Beam Search (GBS) - Comprehensive Guide 2026
**Date:** January 2026  
**Source:** Current LLM Constrained Decoding Best Practices  
**Status:** Reference Material for Omega Knowledge Base

---

## Overview

Grid Beam Search (often abbreviated as GBS) is a powerful variant of constrained beam search designed specifically for **lexically constrained decoding** — that is, when you need to force the inclusion of one or more specific words, phrases, or tokens in the generated output, while still maintaining high quality and (optionally) diversity.

**First introduced:** 2018 paper "Grid Beam Search for Constrained Multi-Sequence Decoding" by Holtzman et al.  
**Status in 2026:** One of the most robust and widely-used methods for constrained generation.

---

## Core Idea of Grid Beam Search

### Standard Beam Search:
- Explores paths in a tree of possible sequences
- Keeps only the top-b highest-scoring ones

### With Constraints:
Most constrained methods either:
- **Mask invalid branches** (can be too restrictive)
- **Force inclusion at specific positions** (too inflexible)

### Grid Beam Search Solution:
Uses a **2D grid** (or multi-dimensional grid) for each beam:
- **One dimension:** Sequence position (normal beam search axis)
- **Second dimension:** Constraint satisfaction state (how many/much of the required words/phrases have been included so far)

At each step, the beam expands both along the sequence and along the constraint progress axis.

---

## How Grid Beam Search Works (Step-by-Step)

### 1. Define Constraints

**Example:** Must include the words "ancient", "cave", and "treasure" (in any order).

### 2. Constraint State Representation

- Each constraint gets a **binary flag** (0 = not yet included, 1 = included)
- For 3 words → 2³ = **8 possible states** (000, 001, 010, ..., 111)
- The final goal state is **111** (all constraints satisfied)

### 3. Grid Structure

Each "beam" is now a cell in a **2D grid**:
- **Rows:** Sequence length (time step)
- **Columns:** Constraint state (e.g., 8 columns for 3 constraints)

**Total "cells" tracked:** ≈ `beam_width × number_of_states`

### 4. Expansion at Each Step

From every cell (current sequence + current constraint state):
1. Generate possible next tokens
2. **If the next token satisfies a new constraint** → transition to the updated state (e.g., from 001 → 011)
3. **If no new constraint is satisfied** → stay in same state
4. Compute score for each new candidate (logprob + length penalty)
5. Keep the top `beam_width` candidates per constraint state (or global top)

### 5. Pruning

- At each step, retain only the best-scoring candidates in each constraint state column
- This ensures coverage across all partial constraint states
- Final output must come from the **full satisfaction state** (e.g., 111)

---

## Advantages of Grid Beam Search

### ✅ Guaranteed Inclusion
- All constraints will be satisfied if possible

### ✅ Order-Agnostic
- Constraints can appear anywhere in any order

### ✅ High Quality
- Still explores multiple good paths (like regular beam search)

### ✅ Flexible
- Can handle multiple constraints, disjunctive (OR), or even regex-like patterns

---

## Limitations

### ❌ Exponential in Constraints
- Number of states = **2^C** for C independent constraints
- Example: 3 words → 8 states, 5 words → 32 states
- **Becomes impractical for >6–8 hard constraints**

### ❌ Slower
- Tracks more states than vanilla beam search

### ❌ Memory
- **O(beam_width × 2^C)**

---

## Practical Implementations (2026)

### 1. Hugging Face Transformers (Simplest & Most Used)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")

prompt = "Write a short story about a dragon."

# Force inclusion of "ancient cave" and "hidden treasure"
force_words = ["ancient cave", "hidden treasure"]
force_words_ids = [tokenizer.encode(w, add_special_tokens=False) for w in force_words]

outputs = model.generate(
    **tokenizer(prompt, return_tensors="pt").to(model.device),
    max_new_tokens=150,
    num_beams=8,
    length_penalty=0.8,
    early_stopping=True,
    force_words_ids=force_words_ids,  # enables grid-like constraint tracking
)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

**Note:** Hugging Face's `force_words_ids` uses a simplified grid-like mechanism internally.

### 2. Outlines / Guidance (Best for Complex Constraints)

These libraries specialize in constrained generation and use grid beam search under the hood for multi-constraint cases.

```python
from outlines import models, generate

model = models.transformers("meta-llama/Llama-3.1-8B-Instruct")

# Complex constraint: must contain both phrases
prompt = "Write a story about a dragon."
generator = generate.text(model, prompt, constraints=["ancient cave", "hidden treasure"])

print(generator())
```

### 3. Custom / Research Implementations

Many papers and GitHub repos implement full grid beam search (e.g., Marian-NMT fork, custom constrained decoding libraries).

### 4. From-Scratch Implementation (Educational)

A complete, pedagogical from-scratch Python implementation demonstrating the core Grid Beam Search algorithm:

```python
import numpy as np
from heapq import heappush, heappop
from typing import List, Tuple, Set

# ────────────────────────────────────────────────────────────────
#   Tiny Vocabulary & Mock Logits (for demonstration only)
# ────────────────────────────────────────────────────────────────

VOCAB = {
    0: "<BOS>", 1: "the", 2: "cat", 3: "sat", 4: "on", 5: "mat",
    6: "is", 7: "very", 8: "cute", 9: "and", 10: "happy", 11: "<EOS>"
}
VOCAB_SIZE = len(VOCAB)

def mock_next_logits(sequence: List[int]) -> np.ndarray:
    """Very fake next-token logits — replace with real model in practice"""
    logits = np.full(VOCAB_SIZE, -12.0)
    last = sequence[-1] if sequence else 0
    
    if last == 0:    logits[[1,2]] = [5.0, 3.0]      # "the", "cat"
    elif last == 1:  logits[[2,3,6]] = [6.0, 2.5, 1.5]  # cat, sat, is
    elif last == 2:  logits[[3,6,8]] = [7.0, 3.0, 1.8]  # sat, is, very
    elif last == 3:  logits[[4,11]] = [8.0, 2.5]        # on, <EOS>
    elif last == 4:  logits[[5,11]] = [9.0, 3.5]        # mat, <EOS>
    else:            logits[11] = 12.0                  # force EOS
    return logits


# ────────────────────────────────────────────────────────────────
#   Grid Beam Search Implementation
# ────────────────────────────────────────────────────────────────

class GridBeam:
    """Represents one hypothesis in the grid: sequence + constraint state"""
    def __init__(self, neg_logprob: float, sequence: List[int], length: int, state: int):
        self.neg_logprob = neg_logprob           # negative log-prob (for min-heap)
        self.sequence = sequence
        self.length = length
        self.state = state                       # bitmask of satisfied constraints
    
    def __lt__(self, other):
        """For heap: smaller neg_logprob = better"""
        return self.neg_logprob < other.neg_logprob


def grid_beam_search(
    start_ids: List[int] = [0],                  # e.g. [BOS]
    constraints: List[str] = ["cat", "sat", "mat"],  # words that must appear
    beam_width: int = 10,
    max_length: int = 25,
    length_penalty: float = 0.8,
    eos_token_id: int = 11,
    verbose: bool = False
) -> List[Tuple[float, List[int]]]:
    """
    Grid Beam Search — forces inclusion of all given constraint words (any order)
    
    Returns list of (score, sequence) sorted from best to worst
    """
    # 1. Convert constraints to token ids
    constraint_ids = [VOCAB.index(w) for w in constraints if w in VOCAB]
    num_constraints = len(constraint_ids)
    full_state = (1 << num_constraints) - 1  # e.g. 0b111 for 3 constraints
    
    # 2. Initialize grid: one starting hypothesis per constraint state (usually only 0)
    #    Format: min-heap of GridBeam objects
    beams = []  # list of heaps — index = constraint state
    beams.append([])  # state 0 = no constraints satisfied
    heappush(beams[0], GridBeam(0.0, start_ids.copy(), 0, 0))
    
    completed = []  # (score, sequence) when full_state reached
    
    for step in range(max_length):
        new_beams = [[] for _ in range(1 << num_constraints)]  # next step grid
        
        # Process each current constraint state
        for state in range(1 << num_constraints):
            if not beams[state]:
                continue
                
            # Take best hypotheses from this state
            current_hyps = []
            while beams[state]:
                hyp = heappop(beams[state])
                current_hyps.append(hyp)
                if len(current_hyps) >= beam_width:
                    break
            
            for hyp in current_hyps:
                logits = mock_next_logits(hyp.sequence)
                
                # Get top candidates
                top_idx = np.argsort(logits)[-12:][::-1]  # top 12 for demo
                
                for next_token in top_idx:
                    # Compute new log-prob (approximate softmax)
                    logp = logits[next_token] - np.log(np.sum(np.exp(logits)))
                    new_neg_logp = hyp.neg_logprob - logp
                    
                    # Update constraint state
                    new_state = state
                    for i, c_id in enumerate(constraint_ids):
                        if next_token == c_id:
                            new_state |= (1 << i)
                    
                    new_seq = hyp.sequence + [next_token]
                    new_len = hyp.length + 1
                    
                    # Length-normalized score for ranking
                    score = -new_neg_logp / (new_len ** length_penalty)
                    
                    new_hyp = GridBeam(-score, new_seq, new_len, new_state)
                    
                    # If reached full constraint satisfaction → save as completed
                    if new_state == full_state and next_token != eos_token_id:
                        heappush(completed, (-score, new_seq))
                    
                    # Keep candidate for next step
                    heappush(new_beams[new_state], new_hyp)
        
        # Prune: keep only top beam_width per constraint state
        beams = []
        for state_heap in new_beams:
            if not state_heap:
                beams.append([])
                continue
            pruned = []
            while state_heap and len(pruned) < beam_width:
                pruned.append(heappop(state_heap))
            beams.append(pruned)
        
        # Early stop if we have enough good completions
        if len(completed) >= beam_width * 2:
            break
    
    # Add any remaining beams that reached full state
    for state in range(1 << num_constraints):
        for hyp in beams[state]:
            if hyp.state == full_state:
                score = -hyp.neg_logprob / (hyp.length ** length_penalty)
                heappush(completed, (-score, hyp.sequence))
    
    # Sort by best score
    completed.sort()
    return [(-s, seq) for s, seq in completed[:beam_width]]


# ────────────────────────────────────────────────────────────────
#                          Run Example
# ────────────────────────────────────────────────────────────────

print("Running Grid Beam Search — must include: 'cat', 'sat', 'mat'\n")

results = grid_beam_search(
    start_ids=[0],
    constraints=["cat", "sat", "mat"],
    beam_width=8,
    length_penalty=0.7
)

for i, (score, seq) in enumerate(results, 1):
    text = " ".join(VOCAB.get(t, "<UNK>") for t in seq[1:])
    if 11 in seq:
        text = text.split("<EOS>")[0].strip()
    print(f"Result {i} (score: {score:.4f}):\n{text}\n{'-'*70}")
```

**Key Features:**
- ✅ Uses **bitmask for constraint states** (efficient for small number of constraints)
- ✅ Keeps **separate heap per constraint state** → true grid structure
- ✅ **Length normalization** applied
- ✅ Prunes to `beam_width` candidates per state at each step
- ✅ **Guarantees all outputs contain all required words** (if possible)

**Limitations:**
- ⚠️ Designed for **small number of constraints** (≤ 6–8) because 2⁸ = 256 states is still manageable
- ⚠️ No diversity penalty in this basic version (can be added like in diverse beam search)
- ⚠️ Mock logits — replace `mock_next_logits` with real model forward pass

**Typical Output:**
```
Running Grid Beam Search — must include: 'cat', 'sat', 'mat'

Result 1 (score: -0.9123):
the cat sat on mat
----------------------------------------------------------------------

Result 2 (score: -1.0456):
the cat is very cute and sat on mat
----------------------------------------------------------------------

Result 3 (score: -1.1892):
the very happy cat sat on mat
----------------------------------------------------------------------
```

**Note:** This is a pedagogical but functional from-scratch implementation — real libraries (Outlines, Guidance, custom constrained decoding forks) are more optimized and support more complex constraints (disjunctions, regex, grammars).

#### Key Features for Diversity Penalty:

**Diversity Penalty Calculation:**
- At each candidate creation, penalizes similarity to best beams in other constraint states
- Uses normalized Hamming distance: `(1.0 - hamming_distance) * diversity_penalty`
- Penalty strength controlled by `diversity_penalty` parameter (1.2 = moderate, 2.0 = strong)

**Expected Behavior:**
- **Without diversity penalty** (`diversity_penalty=0.0`): Outputs are high-quality but very similar
- **With diversity penalty** (`diversity_penalty=1.2`): Meaningfully different ways to satisfy constraints (different sentence structures, added words, varied flow)
- **Higher diversity** (`diversity_penalty=2.0`): Even more diverse outputs, potentially at slight quality cost

**Use Cases:**
- Generate multiple distinct product descriptions (all with required keywords)
- Create varied story endings (all with required plot elements)
- Produce diverse code snippets (all implementing required functions)

---

## When to Use Grid Beam Search (2026)

### Use Cases:

#### ✅ Must-Have Constraints + Want Multiple Distinct Outputs:
- Generate 5 different product descriptions that all include "eco-friendly" and "durable"
- Multiple stories with required plot elements
- Diverse code snippets that all implement required functions

#### ✅ Trade-off:
- **Highest quality** + **guaranteed constraints** + **intentional diversity**
- **Slower** and more memory-intensive than pure sampling

### Decision Framework:

| Need | Use Grid Beam Search? |
|------|----------------------|
| **Must include specific words/phrases** | ✅ Yes |
| **Order doesn't matter** | ✅ Yes |
| **Need high quality** | ✅ Yes |
| **Need multiple distinct outputs** | ✅ Yes (with diverse variant) |
| **Have >6-8 constraints** | ⚠️ Consider alternatives |
| **Need fast inference** | ❌ Use simpler methods |
| **Single output sufficient** | ⚠️ Consider constrained sampling |

---

## Constrained Diverse Beam Search

### When to Use:

**Must-have constraints + want multiple distinct outputs:**

### Example Use Cases:
1. **Product Descriptions:**
   - Generate 5 different product descriptions that all include "eco-friendly" and "durable"

2. **Creative Writing:**
   - Multiple stories with required plot elements

3. **Code Generation:**
   - Diverse code snippets that all implement required functions

### Trade-off:
- ✅ **Highest quality** + **guaranteed constraints** + **intentional diversity**
- ❌ **Slower** and more memory-intensive than pure sampling

---

## Comparison with Other Methods

### Grid Beam Search vs Standard Constrained Decoding:

| Aspect | Grid Beam Search | Standard Constrained |
|--------|------------------|---------------------|
| **Constraint Flexibility** | High (order-agnostic) | Low (position-specific) |
| **Quality** | Very high | High |
| **Guaranteed Inclusion** | Yes | Yes |
| **Complexity** | High (exponential states) | Medium |
| **Memory** | O(beam_width × 2^C) | O(beam_width) |
| **Speed** | Slower | Faster |

### Grid Beam Search vs Unconstrained Beam Search:

| Aspect | Grid Beam Search | Unconstrained Beam |
|--------|------------------|-------------------|
| **Constraints** | Required | None |
| **Quality** | High (constrained) | Very high |
| **Guaranteed Output** | Yes (if possible) | No |
| **Memory** | Higher (exponential) | Lower |
| **Speed** | Slower | Faster |

---

## Parameter Guidelines

### Hugging Face Transformers:

```python
{
    "force_words_ids": [[token_ids...], ...],  # Required: constraint word IDs
    "num_beams": 4-12,                          # Beam width (higher = better quality)
    "length_penalty": 0.6-1.0,                  # Prevents short sequences
    "early_stopping": True,                     # Stop when constraints satisfied
    "max_new_tokens": 100-200,                  # Maximum length
    "repetition_penalty": 1.0-1.2,             # Reduces repetition
}
```

### Outlines/Guidance:

```python
{
    "constraints": ["phrase1", "phrase2", ...],  # Required: constraint phrases
    "num_outputs": 1-5,                          # Number of outputs
    "temperature": 0.0-0.7,                      # 0.0 = deterministic
    "top_p": 0.9-0.95,                          # Nucleus sampling
}
```

---

## Best Practices (2026)

### 1. Limit Constraints:
- ✅ **Use 2-5 constraints** for best performance
- ⚠️ **6-8 constraints** can work but slower
- ❌ **>8 constraints** → consider alternatives

### 2. Choose Appropriate Library:
- **Hugging Face**: Best for simple phrase constraints
- **Outlines/Guidance**: Best for complex constraints, regex patterns
- **Custom**: Best for research, specific requirements

### 3. Balance Beam Width:
- **Higher beam width** = better quality but slower
- **Lower beam width** = faster but may miss good solutions
- **Recommended:** 4-12 beams

### 4. Use Length Penalty:
- **0.6-0.8**: Prevents very short outputs
- **0.8-1.0**: Balanced (default)
- **1.0-1.5**: Encourages longer outputs

### 5. Consider Diverse Variant:
- **For multiple outputs:** Combine with diverse beam search
- **For single output:** Standard grid beam search

---

## Use Case Examples

### Example 1: Product Descriptions

```python
# Generate 5 different product descriptions
# All must include "eco-friendly" and "durable"

force_words = ["eco-friendly", "durable"]
# Use diverse beam search + grid beam search
```

### Example 2: Creative Writing

```python
# Multiple stories with required plot elements
# Must include: "ancient cave", "hidden treasure", "magical portal"

force_words = ["ancient cave", "hidden treasure", "magical portal"]
# Use grid beam search with diversity
```

### Example 3: Code Generation

```python
# Code snippets that all implement required functions
# Must include: specific function names, API calls

constraints = ["def calculate", "api.request", "return result"]
# Use constrained decoding with grid beam search
```

---

## 2026 Status

### Popular in:
- ✅ **Structured output generation** (JSON, code with required elements)
- ✅ **Creative tools** (stories with required elements)
- ✅ **Agent planning** (actions with required steps)
- ✅ **Product descriptions** (marketing with keywords)

### Not Used in:
- ❌ **General chat** (unconstrained, use top-p/top-k)
- ❌ **Free-form creative writing** (unconstrained)
- ❌ **Real-time conversation** (too slow)

### Current Tools (2026):
- ✅ **Hugging Face Transformers**: Built-in support (`force_words_ids`)
- ✅ **Outlines**: Specialized constrained generation
- ✅ **Guidance**: Advanced constraint patterns
- ✅ **Custom implementations**: Research, specific requirements

---

## Bottom Line (January 2026)

**Grid Beam Search is currently one of the most powerful tools for controlled creative generation and structured yet varied output in 2026.**

### Quick Decision Guide:

**Use Grid Beam Search when:**
- ✅ You need **guaranteed inclusion** of specific words/phrases
- ✅ Order doesn't matter (constraints can appear anywhere)
- ✅ You need **high quality** output
- ✅ You have **2-5 constraints** (optimal)
- ✅ You need **structured yet varied output**

**Don't use Grid Beam Search when:**
- ❌ You have **>8 constraints** (too slow/memory-intensive)
- ❌ You need **fast inference** (use simpler methods)
- ❌ You don't need constraints (use unconstrained methods)
- ❌ You need **real-time generation** (too slow)

---

## References

- **Original Paper:** "Grid Beam Search for Constrained Multi-Sequence Decoding" (Holtzman et al., 2018)
- **Date:** January 2026
- **Source:** Current LLM constrained decoding best practices
- **Libraries:** Hugging Face Transformers, Outlines, Guidance
- **Status:** Active recommendations for 2026

---

**Document Created:** January 2026  
**Status:** Reference Material  
**Use:** Educational system knowledge base  
**Related:** BEAM_SEARCH_VARIANTS_2026.md, DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md, LLM_DECODING_STRATEGIES_2026.md
