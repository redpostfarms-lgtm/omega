# Contrastive Search: Mathematical Details (2026)

Contrastive search is a decoding strategy introduced in the 2022 NeurIPS paper "A Contrastive Framework for Neural Text Generation" by Su et al. (arXiv:2202.06417). It has become increasingly popular in 2025–2026 because it produces significantly more fluent and less repetitive long-form text than top-k/top-p sampling while maintaining high quality.

## Original Paper

**Title:** A Contrastive Framework for Neural Text Generation  
**Authors:** Yixuan Su, Tian Lan, Yan Wang, Dani Yogatama, Lingpeng Kong, Nigel Collier  
**Conference:** NeurIPS 2022 (Spotlight)  
**arXiv:** 2202.06417  
**Publication Date:** February 13, 2022 (v1), with updates through 2022  
**Official Implementation:** GitHub - yxuansu/SimCTG  
**arXiv Link:** https://arxiv.org/abs/2202.06417

### Key Contribution

The authors identify that **anisotropic (non-uniform) token representations** in autoregressive LMs cause degeneration (repetitive, bland text). They propose two parts:

1. **SimCTG** — A contrastive training objective to calibrate the model's representation space toward isotropy (uniform distribution)
2. **Contrastive Search** — A new decoding algorithm that encourages diversity while preserving coherence

The breakthrough insight: Contrastive search works well even **without additional SimCTG training** on off-the-shelf models, making it immediately applicable to existing models.

## Core Mathematical Idea (Original Formulation)

At each generation step, contrastive search selects the token that maximizes a **contrastive score** that balances likelihood and penalizes similarity to past tokens.

Let:

- $x_{<t} = x_1, x_2, \dots, x_{t-1}$ be the sequence generated so far
- $h_t$ be the hidden state at time $t$ (the representation of the current context)
- $V$ be the vocabulary
- $p(\cdot | x_{<t})$ be the original softmax probability distribution over next token $x_t$

For candidate token $y \in V$, the **contrastive score** is:

$$\text{Score}(y) = \log p(y | x_{<t}) - \alpha \cdot \max_{i<t} \text{sim}(h_t(y), h_i)$$

Where:

- $\log p(y | x_{<t})$ is the log-probability from the model (likelihood term)
- $\text{sim}(\cdot, \cdot)$ = cosine similarity between hidden states or embeddings
- $h_t(y)$ = hidden state that would be produced if token $y$ were chosen next
- $h_i$ = hidden state of previously generated token $x_i$
- $\alpha \in [0.5, 1.0]$ = degeneration penalty strength (hyperparameter)

The algorithm **selects the token $y$ that maximizes this score**, balancing high likelihood with low similarity to past tokens.

## Mathematical Derivation (Step-by-Step)

Here is the mathematical derivation of the contrastive search objective, step by step, as presented in the paper.

### 1. Standard Autoregressive Decoding (Baseline)

At each time step $t$, given context $x_{<t} = x_1 \dots x_{t-1}$, the model outputs logits $z_t(y)$ for each possible next token $y \in V$ (vocabulary).

The probability is:

$$p(y | x_{<t}) = \text{softmax}(z_t(y)) = \frac{\exp(z_t(y))}{\sum_{y' \in V} \exp(z_t(y'))}$$

Standard sampling methods (greedy, beam, top-k, top-p) select $y$ based only on these probabilities, which often leads to degeneration (repetitive, bland text) because of anisotropic token representations.

### 2. Observation: Anisotropy Causes Degeneration

The paper shows that token representations (hidden states $h_t$) in pretrained LMs are highly anisotropic — they cluster in a narrow cone in the vector space, causing many unrelated tokens to have high cosine similarity.

This leads to:

- High-probability tokens being similar to previous ones
- Model keeps selecting similar continuations → repetition

### 3. Contrastive Search Objective

The key idea is to modify the selection criterion so that we favor tokens $y$ that are both likely (high $p(y)$) and dissimilar to previous tokens.

The contrastive score for candidate token $y$ at time $t$ is defined as:

$$s_t(y) = \log p(y | x_{<t}) - \alpha \cdot \max_{i=1}^{t-1} \text{sim}(h_t(y), h_i)$$

Where:

- $\log p(y | x_{<t})$ = log-probability from the model (likelihood term)
- $\text{sim}(\cdot, \cdot)$ = cosine similarity:
  $$\text{sim}(u, v) = \frac{u^\top v}{\|u\|_2 \|v\|_2}$$
- $h_t(y)$ = the hidden state that would be produced if $y$ were chosen as $x_t$ (computed by feeding $x_{<t} + y$ into the model and taking the last hidden state)
- $h_i$ = hidden state of previously generated token $x_i$ (cached from earlier steps)
- $\alpha \in [0,1]$ = degeneration penalty strength (hyperparameter)

The final next token is selected as:

$$x_t = \arg\max_{y \in V} s_t(y)$$

Or, in practice, sample from softmax-normalized $s_t(y)$ (soft version).

### 4. Why This Works (Derivation Insight)

The term $-\alpha \cdot \max \text{sim}(h_t(y), h_i)$ acts as a contrastive penalty:

- If $y$ leads to a hidden state very similar to previous ones → large penalty → lower score
- If $y$ leads to a dissimilar (new) hidden state → small penalty → score dominated by $\log p(y)$

This encourages semantic diversity (new ideas) while preserving likelihood (coherence).

The $\max$ operator makes it conservative — it penalizes based on the most similar previous token, ensuring no part of history is overly repeated.

### 5. Practical Approximation (Used in Most Implementations)

Computing $h_t(y)$ for every $y \in V$ (vocabulary ~50k–200k) is too expensive ($O(V)$ forward passes per step).

Real implementations approximate by:

- Only considering top-k candidates ($k=10$–$50$) from $p(y | x_{<t})$
- Using the current hidden state $h_t$ (before choosing $y$) as proxy for $h_t(y)$
- Or using word embeddings $e(y)$ instead of full hidden states

**Common approximation (most used in 2026):**

$$s_t(y) \approx \log p(y | x_{<t}) - \alpha \cdot \max_{i<t} \text{cos\_sim}(e(y), e(x_i))$$

Where $e(\cdot)$ is the word embedding layer (much cheaper to compute).

Then:

$$x_t = \arg\max_y s_t(y) \quad \text{or} \quad \text{sample } y \sim \text{softmax}(s_t(y))$$

### 6. Typical Parameter Values (from Paper & 2026 Practice)

- $\alpha = 0.5$–$1.0$ (paper sweet spot: 0.7–0.8)
- $\text{top\_k} = 10$–$50$ (for approximation)
- Often combined with temperature 0.7–0.9 for sampling

### Summary of the Derivation

The contrastive search score is a simple but elegant combination:

- **Likelihood term** ($\log p$) → ensures coherence
- **Contrastive penalty** ($-\alpha \times \max \text{similarity}$) → ensures diversity

By subtracting the maximum similarity to any previous hidden state (or embedding), the method actively avoids both lexical and semantic repetition, leading to more fluent and varied long-form text than top-k/top-p.

This is why contrastive search became (and remains in 2026) one of the strongest decoding methods for open-ended generation.

### Alternative Probability-Adjusted Formulation

Many implementations convert this to a probability distribution by applying softmax over adjusted scores:

$$\hat{p}(y | x_{<t}) = \frac{\exp(\text{Score}(y))}{\sum_{y' \in V} \exp(\text{Score}(y'))}$$

Or equivalently:

$$\hat{p}(y | x_{<t}) = \frac{p(y | x_{<t}) \cdot \exp(-\alpha \cdot \max_{i<t} \text{sim}(h_t(y), h_i))}{\sum_{y' \in V} p(y' | x_{<t}) \cdot \exp(-\alpha \cdot \max_{i<t} \text{sim}(h_t(y'), h_i))}$$

### Practical Approximation

In practice, most implementations approximate this:

Instead of computing $h_t(y)$ for every $y$ (which would be very expensive), they use:

- The current hidden state $h_t$ (before choosing $y$)
- Or the word embeddings of previous tokens
- Or a top-k candidate approximation (only penalize among top-k candidates)

## Most Common Practical Formulation (2025–2026)

This is the version used in most open-source implementations:

1. Compute original probabilities $p(y | x_{<t}) = \text{softmax}(z_t(y))$, where $z_t$ are logits.
2. Get the top-k candidates: $y_1, \dots, y_k$ with highest $p(y_i)$.
3. For each candidate $y_i$:
   - Compute similarity penalty:
     $$s_i = \max_{j=1}^{t-1} \text{cos\_sim}(e(y_i), e(x_j))$$
     where $e(\cdot)$ is the word embedding (or final hidden state projection)
   - Adjusted score:
     $$\hat{z}_i = z_t(y_i) - \alpha \cdot s_i \cdot \|z_t(y_i)\|$$
     (some variants skip the norm or use different scaling)

4. Re-softmax over the adjusted top-k scores to get final probabilities
5. Sample from this distribution

## Typical Values & Behavior

| Parameter | Typical Range | Effect |
|-----------|---------------|--------|
| `top_k` | 10 – 50 | Larger → more candidates considered before contrastive penalty |
| `alpha` | 0.5 – 1.0 | 0.0 → standard top-k<br>0.6–0.8 → sweet spot (most papers)<br>1.0 → very strong anti-similarity |
| Similarity | Cosine (default) | Some use dot product or negative L2 distance |
| Embedding layer | Word embedding or final hidden | Word embedding is faster; final hidden is more semantic |

## Mathematical Advantages Over Top-k/Top-p

1. **Avoids semantic loops** — top-k/top-p only prevent lexical repetition; contrastive penalizes similar meaning (e.g., avoids repeating "AI will change the world" in different words)
2. **Maintains fluency** — Unlike nucleus sampling with very high temperature, contrastive keeps high-probability tokens dominant
3. **Better long-form coherence** — Empirical results show longer generations stay on-topic longer than top-k/top-p

## Real-World Performance (2025–2026)

Papers and community benchmarks show contrastive search often:

- Reduces repetition by 40–70% compared to top-k=50
- Improves coherence scores (human eval, perplexity on long text) over top-p
- Performs best when combined with moderate top-k (30–50) + alpha ≈ 0.7

**Most popular combination today:**
```
contrastive search + top_k=40 + alpha=0.7 + temperature=0.8
```

## SimCTG: Contrastive Training (Optional Enhancement)

The original paper also introduced **SimCTG** (Similarity Contrastive Training for Generation), a contrastive pre-training/fine-tuning objective designed to fix the anisotropic (non-uniform) distribution of token representations in autoregressive language models — a major cause of degeneration (repetitive, bland text) during decoding.

### The Problem SimCTG Solves

In standard LMs (GPT-style), the final hidden states (or word embeddings after projection) tend to cluster in a narrow cone in the vector space — this is called **anisotropy**.

This causes:

- **High similarity between unrelated tokens** — Representations are too close together
- **Degeneration** — Model keeps repeating high-probability tokens/phrases
- **Poor diversity** — Even with high temperature or nucleus sampling, outputs remain repetitive

SimCTG adds a contrastive loss during training to push representations toward **isotropy** (more uniform distribution across the sphere).

### Mathematical Formulation of SimCTG Objective

SimCTG is an additional auxiliary loss added to the standard negative log-likelihood (NLL) language modeling loss.

Let:

- $h_i$: the final hidden state (or embedding) of token $x_i$ in a sequence
- $\mathcal{B}$: a batch of sequences (positive pairs are tokens within the same sequence)
- **Positive pairs**: $(h_i, h_j)$ where $i$ and $j$ are tokens in the same sequence (usually nearby)
- **Negative pairs**: all other pairs in the batch

The contrastive loss is **InfoNCE-style** (like SimCLR):

$$\mathcal{L}_{\text{SimCTG}} = -\sum_{i} \log \frac{\exp(\text{sim}(h_i, h_i^+)/\tau)}{\exp(\text{sim}(h_i, h_i^+)/\tau) + \sum_{k} \exp(\text{sim}(h_i, h_k^-)/\tau)}$$

Where:

- $h_i^+$: positive example (e.g., the next token, or a nearby token in the same sequence)
- $h_k^-$: negative examples (all other tokens in the batch)
- $\text{sim}(\cdot, \cdot)$: cosine similarity:
  $$\text{sim}(u,v) = \frac{u^\top v}{\|u\| \|v\|}$$
- $\tau$: temperature parameter (typically 0.05–0.2)

### Positive Pair Augmentation (Dropout-Based)

In practice, they often use **dropout as a form of positive augmentation**:

For each token $i$, create a positive pair by passing the same sequence twice with different dropout masks → get two slightly different hidden states $h_i$ and $h_i^+$.

This creates natural positive pairs without needing explicit data augmentation.

### Full Training Objective

The total loss is a weighted combination:

$$\mathcal{L} = \mathcal{L}_{\text{NLL}} + \lambda \mathcal{L}_{\text{SimCTG}}$$

Where:

- $\mathcal{L}_{\text{NLL}}$: standard language modeling loss
- $\lambda$: weighting factor (typically 0.1–1.0, paper uses $\lambda=1.0$ in most experiments)

### Key Implementation Details from the Paper

- **Positive pairs**: Use dropout-based augmentation — run the same sequence twice with different dropout masks to get $h_i$ and $h_i^+$
- **Negative pairs**: All other tokens in the same batch (in-batch negatives, like SimCLR)
- **Temperature $\tau$**: 0.05 (most experiments)
- **Embedding layer**: Usually the last hidden state before LM head, or the word embedding after projection
- **Training**: Applied during fine-tuning (e.g., on story/dialog datasets), not necessarily full pretraining

### Empirical Results (from Paper & Follow-ups)

After SimCTG training:

- **Isotropy improvement**: Cosine similarity between random tokens increases significantly (from ~0.1 to ~0.4–0.6)
- **Degeneration reduction**: Rep-n (repetition-n) scores drop dramatically
- **MAUVE** (diversity + quality metric): Big gains over baseline LM
- **Human evaluation**: Generated text rated more coherent and diverse

### Practical Status in 2026

**SimCTG training is not very commonly applied today** because:

1. **Contrastive search (decoding-time) alone already gives most of the benefit** — The decoding algorithm works well without retraining
2. **Fine-tuning with SimCTG is expensive and model-specific** — Requires retraining for each model
3. **Many modern models** (Llama-3.1/3.3, Qwen3, DeepSeek-V3) achieve similar anti-degeneration effects through:
   - Better pretraining data
   - Improved architecture
   - Other regularization techniques

**However, contrastive search (decoding) remains very popular** — especially for long-form creative generation, where it provides significant improvements without any model retraining.

### Key Insight

While SimCTG training can improve results, **contrastive search decoding works effectively even without SimCTG training** on standard off-the-shelf models. This made it immediately applicable to existing models without retraining, which is why contrastive search became so popular in the open-source community.

## SimCTG vs. L2 Normalization: Comparison of Isotropy Methods

SimCTG (from the 2022 NeurIPS paper) and L2 normalization (also called unit normalization or L2 unit norm) are two different approaches to addressing the anisotropy problem in language model representations — where token embeddings cluster in a narrow cone in vector space, leading to degeneration (repetitive, bland text) during generation.

While both aim to improve the isotropy (more uniform distribution) of representations, they operate at different stages, have different mechanisms, and achieve different results.

### Core Comparison Table

| Aspect | SimCTG (Contrastive Training Objective) | L2 Normalization (Unit Norm) | Key Difference / Winner |
|--------|----------------------------------------|------------------------------|-------------------------|
| **Stage of Application** | Training / fine-tuning (modifies model weights) | Inference / post-processing (normalizes embeddings after generation) | SimCTG changes the model; L2 is a cheap fix |
| **Goal** | Calibrate representation space to be more isotropic via contrastive loss | Force all vectors to have unit length | — |
| **Mechanism** | InfoNCE-style contrastive loss with positive/negative pairs (dropout augmentation + in-batch negatives) | Simply divide each vector by its L2 norm: $v \leftarrow v / \|v\|_2$ | SimCTG actively learns; L2 just projects |
| **Effect on Anisotropy** | Actively pushes embeddings toward uniform distribution (reduces cone effect) | Removes magnitude differences → reduces some anisotropy but doesn't fix underlying clustering | SimCTG is stronger |
| **Effect on Generation Quality** | Significantly reduces repetition and improves diversity (MAUVE scores, human eval) | Helps a bit with degeneration but often insufficient alone (still repetitive) | SimCTG |
| **Compute Cost** | High — extra loss term during training (2× forward passes for positives) | Extremely low — just a division at inference | L2 normalization |
| **Need for Retraining** | Yes — requires fine-tuning the model | No — can be applied post-hoc to any model | L2 is easier |
| **Typical Use** | Fine-tuning for better long-form generation (stories, dialogue) | Quick fix during inference (often combined with contrastive search) | L2 for quick wins; SimCTG for serious improvement |
| **Empirical Results (from papers)** | Big gains in MAUVE, rep-n, human eval over baselines | Modest gains; helps but doesn't match contrastive training | SimCTG |
| **Limitations** | Expensive to train; gains may be model-specific | Doesn't fix the root cause (clustering); can distort magnitudes | — |

### Detailed Explanation

#### SimCTG (Contrastive Training)

**Training objective (InfoNCE-style):**

- For each token $i$, create a positive pair $(h_i, h_i^+)$ via dropout augmentation (run the same sequence twice with different dropout masks)
- Negatives are in-batch tokens (other tokens in the mini-batch)
- Loss:
  $$\mathcal{L}_{\text{SimCTG}} = -\log \frac{\exp(\text{sim}(h_i, h_i^+)/\tau)}{\exp(\text{sim}(h_i, h_i^+)/\tau) + \sum_{k} \exp(\text{sim}(h_i, h_k^-)/\tau)}$$
- Total loss: $\mathcal{L} = \mathcal{L}_{\text{NLL}} + \lambda \mathcal{L}_{\text{SimCTG}}$ ($\lambda \approx 1.0$ in the paper)

**Why it works** — Forces representations to be more uniformly distributed on the hypersphere (isotropy), reducing the cone effect that causes high similarity between unrelated tokens.

**Results** — Much better long-form generation; less repetition; higher diversity scores (MAUVE, rep-n).

#### L2 Normalization (Unit Norm)

**Operation** — At inference, for any representation vector $v$ (hidden state or embedding):

$$v_{\text{norm}} = \frac{v}{\|v\|_2}$$

where $\|v\|_2 = \sqrt{\sum_{i} v_i^2}$ is the Euclidean (L2) norm.

**Why it helps** — Removes magnitude differences → forces all vectors to lie on the unit hypersphere → reduces some anisotropy by making cosine similarity more meaningful.

**Limitations** — It's a post-hoc projection — it doesn't change the underlying model or training dynamics. Anisotropy (clustering) can still exist; it just gets "projected" onto the sphere. Doesn't fix the root cause like contrastive training does.

**Results** — Improves degeneration somewhat (better than nothing), but far less effective than contrastive objectives in papers.

### Summary & Recommendation (2026 Perspective)

- **SimCTG is the more powerful, proactive solution** — it learns a better representation space during training/fine-tuning.
- **L2 normalization is the cheap, reactive fix** — apply it at inference to any model for a quick boost.

**In practice today:**

1. **If you're fine-tuning a model** for long-form or creative generation → use SimCTG (or similar contrastive objectives) during training.
2. **If you're using an off-the-shelf model** (Llama, Qwen, DeepSeek) → apply L2 normalization at inference + contrastive search decoding — this combination gives most of the benefit without retraining.

Many recent papers (2024–2025) show that contrastive search alone often works well on pre-trained models, making SimCTG training less necessary — but when you can afford to fine-tune, SimCTG still gives the best isotropy and diversity.

## Follow-Up Paper

**"Contrastive Search Is What You Need For Neural Text Generation"**  
**Authors:** Yixuan Su, Nigel Collier  
**arXiv:** 2210.14140  
**Date:** October 2022  
**arXiv Link:** https://arxiv.org/abs/2210.14140

This follow-up work demonstrates that contrastive search works well across **16 languages** on off-the-shelf models without additional training, further validating its practical applicability.

## Historical Impact (2026 Perspective)

Contrastive search was a breakthrough because it:

1. **Fixes degeneration without extra training** — Works at decoding time only
2. **Inspired many later methods** — Contrastive Decoding (Li et al., 2023), Adaptive Contrastive Search (2024), etc.
3. **Still widely used in 2026** — Particularly for long-form generation tasks where coherence + diversity matter (stories, roleplay, reasoning chains, creative writing)

### Performance Results (Original Paper)

Outperformed beam search, nucleus sampling, top-k, etc., on benchmarks:

- **MAUVE** (diversity-coherence metric)
- **rep-n** (repetition metrics)
- **Human evaluation** (quality assessments)

Across multiple languages and tasks: story generation, dialogue, summarization, etc.

## Contrastive Search Variants and Extensions (2023–2026)

Here are the main variants and extensions of contrastive search that have emerged since the original 2022 paper. These variants are actively used and discussed in the 2025–2026 literature and open-source community.

### 1. Original Contrastive Search (Su et al., 2022)

**Core Formula:**

$$s_t(y) = \log p(y | x_{<t}) - \alpha \times \max_{i<t} \text{cos\_sim}(h_t(y), h_i)$$

$$x_t = \arg\max_y s_t(y) \quad \text{(or sample from softmax}(s_t(y)))$$

- $\alpha = 0.5$–$1.0$ (usually 0.7)
- $h_t(y)$ = hidden state if $y$ is chosen (full forward pass per candidate → approximated with top-k)
- **Most used approximation (2026 default)**: Use word embeddings $e(y)$ instead of $h_t(y)$, or current $h_t$ as proxy

**Strengths:** Excellent anti-repetition (lexical + semantic), strong coherence  
**Weaknesses:** Slow (top-k forward passes), needs careful alpha tuning

### 2. Adaptive Contrastive Search (2023–2024 extension)

**Key improvement:** Make $\alpha$ dynamic instead of fixed.

**Variants:**

- $\alpha(t) = \alpha_0 \times (t / \text{max\_length})$ (increases penalty as sequence grows → stronger anti-repetition later)
- $\alpha$ based on entropy — $\alpha = \alpha_0 \times (1 - \text{entropy}(p(y)))$ → stronger penalty when model is overconfident (low entropy)
- Perplexity-triggered — increase $\alpha$ when recent perplexity is low (model too certain → risk of repetition)

**Popular config:**

```python
alpha_base = 0.6
alpha = alpha_base * (1 + 0.5 * current_step / max_length)
```

**Strengths:** Better balance in long sequences  
**Used in:** Many Llama-3.x and Qwen forks

### 3. Contrastive Search with Kernel Density Penalty (2024)

**Improvement:** Replace max similarity with a kernel density estimate (KDE) over previous hidden states.

$$\text{penalty}(y) = \alpha \times \int K(h_t(y) - h_i) \, dh_i$$

(approximated with Gaussian kernel over previous $h_i$)

**Strengths:** Smoother, more robust penalty (doesn't over-penalize a single outlier previous token)  
**Weaknesses:** Slightly more compute (kernel sum over history)  
**Typical kernel:** Gaussian with bandwidth $\sigma \approx 0.1$–$0.3$  
**Used in:** Research papers on long-context generation, some DeepSeek-inspired forks

### 4. Contrastive + Top-p Hybrid (Most Common 2026 Production Variant)

**How it works:**

1. First apply contrastive penalty on top-k candidates
2. Then apply top-p filtering on the adjusted distribution
3. Sample from the result

**Strengths:** Combines contrastive's anti-repetition with nucleus's adaptivity  
**Most used combo:** $\alpha=0.6$–$0.8$ + $\text{top\_k}=40$–$60$ + $\text{top\_p}=0.92$–$0.95$

### 5. Contrastive Search with Length-Adaptive Penalty (2025+)

**Key idea:** Make penalty stronger as sequence grows (to prevent long-term drift/repetition).

$$\alpha_t = \alpha_{\text{base}} \times (1 + \beta \times t / \text{max\_length})$$

- $\beta \approx 0.3$–$0.8$
- Very effective for generations >200 tokens

**Used in:** Long-form story/roleplay models, some agent systems

### Summary Table – Contrastive Search Variants (2026)

| Variant | Main Change | Alpha Range | top_k Range | Best For | Popularity |
|---------|-------------|-------------|-------------|----------|------------|
| **Original Contrastive Search** | Fixed $\alpha$ + max similarity | 0.6–1.0 | 10–50 | General long-form | Very high |
| **Adaptive $\alpha$** | Dynamic $\alpha$ (length/entropy-based) | 0.5–1.0 | 20–60 | Long sequences | High |
| **Kernel Density Penalty** | KDE instead of max sim | 0.5–0.9 | 30–70 | Research/long-context | Medium |
| **Contrastive + Top-p Hybrid** | Contrastive penalty → top-p filter | 0.6–0.8 | 40–60 | Production chat/story (most used) | **Highest** |
| **Length-Adaptive Penalty** | $\alpha$ increases with sequence length | 0.6–1.2 | 30–50 | Very long generations (>300 tokens) | Growing |

**Most popular in 2026:**

```
contrastive + top-p hybrid
alpha = 0.7
top_k = 40–50
top_p = 0.93
temperature = 0.8
```

This gives the best balance of fluency, diversity, and low repetition on most open models.

## Limitations

1. **Needs access to hidden states or word embeddings** → not possible with black-box APIs (OpenAI, etc.)
2. **Slightly slower than plain top-k** (embedding lookup + similarity computation)
3. **Alpha tuning is model-dependent** — too high → bland text; too low → repetition

This is why contrastive search is very popular in open-source (Llama, Qwen, DeepSeek forks) but rare in closed APIs.

## References

### Primary Papers

- **Su, Y.**, Lan, T., Wang, Y., Yogatama, D., Kong, L., & Collier, N. (2022). A Contrastive Framework for Neural Text Generation. *Advances in Neural Information Processing Systems (NeurIPS 2022, Spotlight)*. arXiv:2202.06417. https://arxiv.org/abs/2202.06417

- **Su, Y.**, & Collier, N. (2022). Contrastive Search Is What You Need For Neural Text Generation. arXiv:2210.14140. https://arxiv.org/abs/2210.14140

### Related Work

- **Li, X.**, Zhang, T., Dubois, Y., Taori, R., Gulrajani, I., Guestrin, C., ... & Hashimoto, T. (2022). Contrastive Decoding: Open-ended Text Generation as Optimization. arXiv:2210.15097. https://arxiv.org/abs/2210.15097

### Implementation

- **Official Implementation:** GitHub - yxuansu/SimCTG (https://github.com/yxuansu/SimCTG)

## See Also

- `LLM_DECODING_STRATEGIES_2026.md` - Comparison table between Diverse Beam Search and Contrastive Search
- `DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md` - Practical code implementation examples for Contrastive Search
