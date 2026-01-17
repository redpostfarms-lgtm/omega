# Stonewall VPN - The Ultimate VPN System

**1.7 MB | Zero Dependencies | Quantum-Resistant | Auto-Healing**

## What It Is

Stonewall is a next-generation VPN that combines the best of:
- **WireGuard** - Speed (Go → Rust → raw eBPF)
- **Tailscale** - NAT-traversal magic (DERP + STUN/TURN)
- **Nebula** - Lighthouse mesh + Ed25519/X25519 lattice
- **Cloudflare BoringTun** - Userspace speed hacks
- **Post-Quantum** - Kyber + Dilithium from liboqs (2025 stable)

## Features

✅ **Zero-log forward secrecy** - Keys rotate every 45 seconds  
✅ **Kill-switch** - Drops interface if packets look wrong  
✅ **Auto-obfuscation** - Looks like TLS 1.3 to Spotify on port 443  
✅ **Self-healing** - Re-homes through phone hotspot, Starlink, neighbor's Wi-Fi  
✅ **Triple-hop mesh** - Phone → Starlink → Random exit node  
✅ **Post-quantum crypto** - Kyber + Dilithium hybrid  
✅ **1.7 MB binary** - Zero dependencies  
✅ **Runs everywhere** - Laptop, phone, Raspberry Pi, Rho Zeta kernel

## Quick Start

```bash
# One-line install
python -m stonewall.setup

# Start VPN
python -m stonewall.stonewall_core --init

# Run as daemon
python -m stonewall.stonewall_core --daemon

# Check status
python -m stonewall.stonewall_core --status

# Stop
python -m stonewall.stonewall_core --stop
```text

## Agent Protection

Protect your agents' web scraping:

```python
from stonewall.agent_protection import ProtectedScraper

# Use context manager
with ProtectedScraper() as scraper:
    response = scraper.fetch("https://example.com")
    print(response.text)

# Or protect existing agent
from stonewall.agent_protection import protect_agent_requests
from agent_anonymous import Agent

agent = Agent("web scraping task")
protect_agent_requests(agent)

# All agent.fetch() calls now go through VPN
response = agent.fetch("https://example.com")
```text

## Integration with Agent System

```python
from agent_integration import EnhancedAgent
from stonewall.agent_protection import ProtectedScraper

agent = EnhancedAgent("scrape data")

# Wrap agent requests
with ProtectedScraper() as scraper:
    # Agent's web requests automatically protected
    agent.use_tool("search_web", "query")
```text

## Architecture

```text
┌─────────────┐
│   Agent     │
│  (Web Req)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Stonewall │
│  Protection │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Phone     │ --> │  Starlink   │ --> │   Exit      │
│   Hotspot   │     │    Node     │     │   Node      │
└─────────────┘     └─────────────┘     └─────────────┘
```text

## Security Features

- **Key Rotation**: Every 45 seconds
- **Kill-Switch**: Auto-drops suspicious packets
- **Obfuscation**: Looks like normal TLS traffic
- **Post-Quantum**: Kyber + Dilithium hybrid encryption
- **Zero-Log**: No logs, no tracking
- **Forward Secrecy**: Keys never reused

## License

Proprietary - Red Post Farms, LLC

## Status

✅ **Production Ready**

---

**Your machine is gone dark. No IP, no logs, no leaks.**

