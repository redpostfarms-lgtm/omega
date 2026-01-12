#!/usr/bin/env python3
# Grid Beam Search - From-Scratch Implementation (Educational)
"""
From-scratch Python implementation of Grid Beam Search (GBS) for educational purposes.
Demonstrates the core algorithm with a clean, understandable, and reasonably efficient version.

This is a pedagogical implementation — real libraries (Outlines, Guidance) are more optimized.
"""
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


def hamming_distance(seq1: List[int], seq2: List[int]) -> float:
    """Normalized Hamming distance between two sequences"""
    min_len = min(len(seq1), len(seq2))
    if min_len == 0:
        return 0.0
    diff = sum(a != b for a, b in zip(seq1[:min_len], seq2[:min_len]))
    return diff / min_len


def grid_beam_search(
    start_ids: List[int] = [0],                  # e.g. [BOS]
    constraints: List[str] = ["cat", "sat", "mat"],  # words that must appear
    beam_width: int = 10,
    max_length: int = 25,
    length_penalty: float = 0.8,
    diversity_penalty: float = 0.0,             # NEW: diversity penalty (0.0 = no diversity)
    eos_token_id: int = 11,
    verbose: bool = False
) -> List[Tuple[float, List[int]]]:
    """
    Grid Beam Search — forces inclusion of all given constraint words (any order)
    
    With diversity_penalty > 0, this becomes Constrained Diverse Grid Beam Search,
    encouraging different paths across the grid while maintaining constraints.
    
    Args:
        start_ids: Starting token IDs (usually [BOS])
        constraints: List of words/phrases that must appear in output
        beam_width: Number of beams to maintain per constraint state
        max_length: Maximum sequence length
        length_penalty: Length normalization exponent (0.8 typical)
        diversity_penalty: Strength of diversity penalty (0.0 = none, 1.2 = moderate, 2.0 = strong)
        eos_token_id: End-of-sequence token ID
        verbose: Print debug information
    
    Returns:
        List of (score, sequence) sorted from best to worst
        All sequences guaranteed to contain all constraints (if possible)
    """
    # 1. Convert constraints to token ids
    constraint_ids = [VOCAB.index(w) for w in constraints if w in VOCAB]
    num_constraints = len(constraint_ids)
    full_state = (1 << num_constraints) - 1  # e.g. 0b111 for 3 constraints
    
    if verbose:
        print(f"Constraints: {constraints}")
        print(f"Constraint IDs: {constraint_ids}")
        print(f"Number of constraint states: {1 << num_constraints}")
        print(f"Full state (goal): {full_state} (binary: {bin(full_state)})\n")
    
    # 2. Initialize grid: one starting hypothesis per constraint state (usually only 0)
    #    Format: list of heaps — index = constraint state
    beams = []  # list of heaps — index = constraint state
    for _ in range(1 << num_constraints):
        beams.append([])
    heappush(beams[0], GridBeam(0.0, start_ids.copy(), 0, 0))  # Start at state 0
    
    completed = []  # (score, sequence) when full_state reached
    
    for step in range(max_length):
        new_beams = [[] for _ in range(1 << num_constraints)]  # next step grid
        
        # Process each current constraint state
        for state in range(1 << num_constraints):
            if not beams[state]:
                continue
                
            # Take best hypotheses from this state
            current_hyps = []
            while beams[state] and len(current_hyps) < beam_width:
                hyp = heappop(beams[state])
                current_hyps.append(hyp)
            
            for hyp in current_hyps:
                logits = mock_next_logits(hyp.sequence)
                
                # Get top candidates
                top_k = min(12, VOCAB_SIZE)  # top 12 for demo
                top_idx = np.argsort(logits)[-top_k:][::-1]
                
                for next_token in top_idx:
                    # Compute new log-prob (approximate softmax)
                    logp = logits[next_token] - np.log(np.sum(np.exp(logits - np.max(logits))) + 1e-10)
                    new_neg_logp = hyp.neg_logprob - logp
                    
                    # Update constraint state (bitmask)
                    new_state = state
                    for i, c_id in enumerate(constraint_ids):
                        if next_token == c_id:
                            new_state |= (1 << i)  # Set bit i
                    
                    new_seq = hyp.sequence + [next_token]
                    new_len = hyp.length + 1
                    
                    # Base score with length penalty
                    base_score = -new_neg_logp / (new_len ** length_penalty)
                    
                    # Add diversity penalty against best beams in OTHER states (if enabled)
                    diversity_penalty_sum = 0.0
                    if diversity_penalty > 0.0:
                        for other_state in range(1 << num_constraints):
                            if other_state == new_state or not beams[other_state]:
                                continue
                            # Compare with best (top) beam in other state
                            best_other = beams[other_state][0]
                            hamming = hamming_distance(new_seq, best_other.sequence)
                            diversity_penalty_sum += (1.0 - hamming) * diversity_penalty
                    
                    final_score = base_score - diversity_penalty_sum
                    
                    new_hyp = GridBeam(-final_score, new_seq, new_len, new_state)
                    
                    # If reached full constraint satisfaction → save as completed
                    if new_state == full_state and next_token != eos_token_id:
                        heappush(completed, (-final_score, new_seq))
                        if verbose:
                            print(f"Step {step}: Found completion in state {new_state} (score: {final_score:.4f})")
                    
                    # Keep candidate for next step (add to appropriate state heap)
                    heappush(new_beams[new_state], new_hyp)
        
        # Prune: keep only top beam_width candidates per constraint state
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
            if verbose:
                print(f"Early stopping at step {step} (found {len(completed)} completions)")
            break
    
    # Add any remaining beams that reached full state
    for state in range(1 << num_constraints):
        for hyp in beams[state]:
            if hyp.state == full_state:
                score = -hyp.neg_logprob / (hyp.length ** length_penalty)
                heappush(completed, (-score, hyp.sequence))
    
    # Sort by best score (min-heap gives worst first, so we reverse)
    completed.sort()
    return [(-s, seq) for s, seq in completed[:beam_width]]


# ────────────────────────────────────────────────────────────────
#                          Run Example
# ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("  GRID BEAM SEARCH - FROM-SCRATCH IMPLEMENTATION")
    print("  With Diversity Penalty Support")
    print("=" * 70)
    
    # Example 1: Standard Grid Beam Search (no diversity)
    print("\n[Example 1] Standard Grid Beam Search (diversity_penalty=0.0)")
    print("Must include: 'cat', 'sat', 'mat'\n")
    
    results1 = grid_beam_search(
        start_ids=[0],
        constraints=["cat", "sat", "mat"],
        beam_width=8,
        length_penalty=0.7,
        diversity_penalty=0.0,  # No diversity
        verbose=False
    )
    
    print(f"Found {len(results1)} results:\n")
    for i, (score, seq) in enumerate(results1[:3], 1):  # Show top 3
        text = " ".join(VOCAB.get(t, "<UNK>") for t in seq[1:])
        if 11 in seq:
            text = text.split("<EOS>")[0].strip()
        print(f"Result {i} (score: {score:.4f}):")
        print(f"  {text}\n{'-'*70}\n")
    
    # Example 2: Constrained Diverse Grid Beam Search (with diversity)
    print("\n[Example 2] Constrained Diverse Grid Beam Search (diversity_penalty=1.2)")
    print("Must include: 'cat', 'sat', 'mat'\n")
    
    results2 = grid_beam_search(
        start_ids=[0],
        constraints=["cat", "sat", "mat"],
        beam_width=8,
        length_penalty=0.7,
        diversity_penalty=1.2,  # Moderate diversity
        verbose=False
    )
    
    print(f"Found {len(results2)} results:\n")
    for i, (score, seq) in enumerate(results2[:3], 1):  # Show top 3
        text = " ".join(VOCAB.get(t, "<UNK>") for t in seq[1:])
        if 11 in seq:
            text = text.split("<EOS>")[0].strip()
        print(f"Result {i} (score: {score:.4f}):")
        print(f"  {text}\n{'-'*70}\n")
