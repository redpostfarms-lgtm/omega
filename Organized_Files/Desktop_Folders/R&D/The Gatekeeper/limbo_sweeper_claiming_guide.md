# LIMBO SWEEPER - WHERE THE MONEY GOES

**Red Post Farms, LLC | Copyright (c) 2025-2026 | All Rights Reserved**

---

## Important: The Sweeper is a FINDER, Not Always a CLAIMER

The Limbo Sweeper **finds** opportunities. Actually **claiming** them requires additional steps depending on the type.

---

## Component Breakdown

### 1. Bitcoin Puzzles (#50 & #66)

**What the sweeper does:**
- Probes the puzzle ranges
- Logs attempts
- **Does NOT solve** (that requires brute force with GPU)

**If you actually solved a puzzle:**
- The Bitcoin would go to **whatever wallet address you control**
- You'd need to:
  1. Generate a private key in the puzzle range
  2. Derive the Bitcoin address from that key
  3. The puzzle reward goes to that address
  4. You'd control it because you have the private key

**Reality check:**
- Puzzle #50: ~1,099,511,627,776 possible keys (needs GPU brute force)
- Puzzle #66: ~18,446,744,073,709,551,616 possible keys (extremely difficult)
- The sweeper just logs probe attempts - doesn't actually solve

**Where money goes:** Your wallet (if you solve it)

---

### 2. Dust Reclamation

**What the sweeper does:**
- Checks public Bitcoin addresses for small amounts (dust)
- Uses Blockstream API to read blockchain data
- **Only checks - does NOT claim**

**To actually claim dust:**
- You'd need the **private key** for that Bitcoin address
- The sweeper doesn't have private keys
- It's just checking if addresses have funds

**Reality check:**
- Most addresses checked will have no dust
- If they do have dust, you can't claim it without the private key
- The sweeper is just showing you "hey, this address has some BTC"

**Where money goes:** Nowhere - you can't claim it without private keys

**Exception:** If you own the addresses being checked, you'd claim to your own wallet

---

### 3. Testnet Airdrops

**What the sweeper does:**
- Attempts to claim testnet tokens from L2 chains
- Uses the testnet address from your config

**If successful:**
- Tokens go to: **Your testnet address** (from config: `testnet_address`)
- Format: `0x...` (Ethereum address format)

**Reality check:**
- Testnet tokens have **NO REAL VALUE**
- They're for testing only
- Can't be converted to real money

**Where money goes:** Your testnet address (but it's fake money)

---

### 4. Unclaimed Funds Search

**What the sweeper does:**
- Searches state databases for unclaimed funds
- Checks unclaimed.org, missingmoney.com
- **Only finds - does NOT claim**

**To actually claim:**
- You'd need to file a claim with the state
- Usually requires:
  1. Proof of identity
  2. Proof you're the person named
  3. Filing paperwork with state treasury
  4. Waiting for processing

**If you successfully claim:**
- Money goes to: **You** (via check, direct deposit, etc.)
- Processed by state treasury
- Can take weeks/months

**Reality check:**
- Most people find nothing
- If you find something, it's YOUR money (you just didn't know about it)
- Legal to claim your own unclaimed funds

**Where money goes:** You (after filing state claim)

---

### 5. Bug Bounty Fuzzing

**What the sweeper does:**
- Scrapes HackerOne for bug bounty programs
- Would run fuzzers (if implemented)
- **Only finds vulnerabilities - does NOT get paid automatically**

**To actually get paid:**
- You'd need to:
  1. Find a real vulnerability
  2. Report it through HackerOne/Bugcrowd
  3. Wait for triage/verification
  4. Get paid by the platform

**If you find and report a bug:**
- Payment goes to: **Your HackerOne/Bugcrowd account**
- Usually PayPal, bank transfer, or cryptocurrency
- Amount depends on severity ($500 - $50,000+)

**Reality check:**
- Most fuzzing finds nothing
- Finding real bugs is hard
- Payment only if bug is accepted

**Where money goes:** Your HackerOne/Bugcrowd account → Your bank/PayPal

---

## Summary Table

| Component | What Sweeper Does | Can It Claim? | Where Money Goes |
|-----------|------------------|---------------|------------------|
| Bitcoin Puzzles | Probes ranges | No (needs solving) | Your wallet (if solved) |
| Dust Reclamation | Checks addresses | No (needs private keys) | Nowhere (can't claim) |
| Testnet Airdrops | Claims testnet tokens | Yes | Your testnet address (fake money) |
| Unclaimed Funds | Searches databases | No (needs state claim) | You (after state processing) |
| Bug Bounties | Finds vulnerabilities | No (needs reporting) | Your HackerOne account |

---

## What You Actually Get

The sweeper creates a **report** (`tx_dump.json`) with:
- What it found
- Where it found it
- How much (if known)
- Source

**You then decide:**
- Is it claimable?
- Do you want to pursue it?
- What's the process?

---

## Realistic Expectations

**Most likely outcomes:**
1. **Bitcoin Puzzles:** Nothing (just probe logs)
2. **Dust:** Nothing (or addresses you can't claim)
3. **Airdrops:** Testnet tokens (no real value)
4. **Unclaimed Funds:** Maybe something, maybe nothing
5. **Bug Bounties:** Nothing (unless you find real bugs)

**The sweeper is a SCANNER, not a MAGIC MONEY MACHINE.**

It finds opportunities. You still need to:
- Have the right keys/access
- File proper claims
- Do the work to actually get paid

---

## If You Want to Actually Claim Funds

### For Unclaimed Funds:
1. Check `tx_dump.json` for hits
2. Go to state treasury website
3. File claim with proof of identity
4. Wait for processing
5. Get paid

### For Bug Bounties:
1. Check `tx_dump.json` for targets
2. Manually test/fuzz those targets
3. Report valid bugs to HackerOne
4. Get paid if accepted

### For Bitcoin:
1. If you solve a puzzle → Bitcoin goes to your wallet
2. If you find dust you own → Claim to your wallet
3. Otherwise → Can't claim without private keys

---

**Bottom line:** The sweeper finds opportunities. You still need to do the work to claim them (if they're claimable at all).
