# LIMBO SWEEPER - COMPLETE WALKTHROUGH

**Red Post Farms, LLC | Copyright (c) 2025-2026 | All Rights Reserved**

**Status:** ✅ **READY FOR TESTING**

---

## What Is Limbo Sweeper?

Limbo Sweeper searches for "floating cash" - unclaimed funds, dust, airdrops, and opportunities that are publicly available. It's a vacuum for money that's sitting in limbo.

**Key Points:**
- ✅ **100% Legal** - Only checks public data
- ✅ **Zero Harm** - Doesn't steal, hack, or break anything
- ✅ **One File** - Clean, simple, run it and done
- ✅ **Air-Gapped Ready** - Can work offline (with cached data)

---

## Components Explained

### 1. Bitcoin Puzzles (#50 & #66)
**What it does:**
- Probes Bitcoin puzzle challenges (public competitions)
- Puzzle #50: Range `0x8000000000` to `0xFFFFFFFFFFF`
- Puzzle #66: Range `0x20000000000000000` to `0x3FFFFFFFFFFFFFFFF`
- **Note:** Actual solving requires brute force (GPU-intensive)
- This just logs probe attempts

**Why it's safe:**
- Public challenges, anyone can try
- No private keys needed
- Just checking ranges

### 2. Dust Reclamation
**What it does:**
- Checks public Bitcoin addresses for small amounts (dust)
- Uses Blockstream API (public, no auth)
- Only **checks** - doesn't claim (you'd need private keys)

**Why it's safe:**
- Public addresses are public
- Just reading blockchain data
- Can't claim without private keys

**Example addresses checked:**
- `1FeexV6bAHb8ybZjqQMjJrcCrHGW9sb6uF`
- `1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2`
- `1CUNEBjYrZVX9nW9cp5vwV7NCPQVf2uL6P`

### 3. Testnet Airdrops
**What it does:**
- Attempts to claim testnet tokens from L2 chains
- Chains: Jito, Blast, zkSync, Linea
- **Testnet tokens have NO real value** (safe)

**Why it's safe:**
- Testnet = fake money
- Public faucets
- No real value

**Requires:**
- Testnet address (Ethereum format: `0x...`)

### 4. Unclaimed Funds Search
**What it does:**
- Searches state databases for unclaimed funds
- Checks: unclaimed.org, missingmoney.com
- Uses your name and state

**Why it's safe:**
- Public databases
- You're searching for YOURSELF
- Legal to claim your own unclaimed funds

**Requires:**
- Name to search (e.g., "Ruth Berry")
- State code (e.g., "TX")

### 5. Bug Bounty Fuzzing
**What it does:**
- Scrapes HackerOne for bug bounty programs
- Would run fuzzers via agent swarm
- **Requires Selenium** (webdriver)

**Why it's safe:**
- Bug bounties are legal security research
- Public programs
- You get paid for finding bugs

**Requires:**
- Selenium installed
- ChromeDriver
- Advanced setup

---

## Setup Walkthrough

### Step 1: Run Setup
```bash
python limbo_sweeper_test_setup.py
```text

This will:
1. Ask about wallet addresses (or use defaults)
2. Ask for testnet address (optional)
3. Ask for name/state for unclaimed funds search
4. Let you enable/disable features
5. Save configuration

### Step 2: Test Components
```bash
python limbo_sweeper_test_run.py --all
```text

This tests each component individually and shows what it does.

### Step 3: Run Full Sweep
```bash
python limbo_sweeper.py
```text

This runs all enabled components and saves results.

### Step 4: Check Results
```bash
python limbo_sweeper_test_run.py --results
```text

Or check the file directly:
```text
D:\RPF_BRAIN\Omega\tx_dump.json
```text

---

## Configuration

Configuration is saved to:
```text
D:\RPF_BRAIN\Omega\limbo_config.json
```text

**Example config:**
```json
{
  "wallet_addresses": [
    "1FeexV6bAHb8ybZjqQMjJrcCrHGW9sb6uF"
  ],
  "testnet_address": "0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
  "search_name": "Ruth Berry",
  "search_state": "TX",
  "enable_btc_puzzles": true,
  "enable_dust_reclaim": true,
  "enable_airdrops": true,
  "enable_refunds": true,
  "enable_bounties": false,
  "test_mode": true,
  "rate_limit_delay": 0.1
}
```text

---

## Output Files

All files are saved to: `D:\RPF_BRAIN\Omega\`

1. **`limbo.db`** - SQLite database with all hits
2. **`tx_dump.json`** - JSON export of unclaimed hits
3. **`sweep.log`** - Log file (if logging enabled)
4. **`limbo_config.json`** - Configuration file

---

## Questions You Might Have

### Q: Is this legal?
**A:** Yes. Everything checks public data only. No hacking, no stealing.

### Q: Can I actually claim the funds?
**A:** 
- **Dust:** Only if you have the private keys (you don't)
- **Airdrops:** Yes, if you claim testnet tokens
- **Unclaimed funds:** Yes, if they're yours (legal claim process)
- **Bounties:** Yes, if you find bugs (legal security research)

### Q: Will this hurt anyone?
**A:** No. It only reads public data. Doesn't break anything.

### Q: What if I find something?
**A:** Check `tx_dump.json`. Each hit has:
- Type (dust, airdrop, refund, etc.)
- Source
- Amount
- Wallet/address

### Q: Can I run this offline?
**A:** Partially. Some components need internet (APIs). But database and results work offline.

### Q: Is this safe for my computer?
**A:** Yes. It's just Python scripts making API calls. No malware, no viruses.

---

## Test Run Checklist

Before running a full sweep:

- [ ] Run setup: `python limbo_sweeper_test_setup.py`
- [ ] Review config: `python limbo_sweeper_test_setup.py --show`
- [ ] Test components: `python limbo_sweeper_test_run.py --all`
- [ ] Check internet connection (for API calls)
- [ ] Review what each component does (this document)
- [ ] Run full sweep: `python limbo_sweeper.py`
- [ ] Check results: `python limbo_sweeper_test_run.py --results`

---

## Troubleshooting

### "No wallet addresses configured"
- Run setup and add addresses, or use defaults

### "Selenium not available"
- Install: `pip install selenium`
- Download ChromeDriver
- Or disable bounties feature

### "API errors"
- Check internet connection
- Some APIs may be rate-limited
- Try again later

### "No results found"
- This is normal - most addresses have no dust
- Most people have no unclaimed funds
- Check `tx_dump.json` anyway

---

## Next Steps

1. **Run setup** - Configure what you want to check
2. **Test components** - See what each does
3. **Run sweep** - Let it search
4. **Check results** - See what it found
5. **Repeat** - Run periodically to catch new opportunities

---

**Ready to test? Start with:**
```bash
python limbo_sweeper_test_setup.py
```text
