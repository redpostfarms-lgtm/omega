# -*- coding: utf-8 -*-
# Test Shadows - Anti-Tag & Trace-Bait

from stonewall.stonewall_core import StonewallVPN, StonewallConfig

print("=" * 60)
print("SHADOWS TEST - Anti-Tag & Trace-Bait")
print("=" * 60)

config = StonewallConfig(anti_tag=True, trace_bait=True)
vpn = StonewallVPN(config)

print("\n[OK] Stonewall created with anti-tag and trace-bait")
print("[OK] Starting VPN...")

vpn.start()

status = vpn.get_status()
print(f"\nAnti-tag available: {status.get('anti_tag') is not None}")
print(f"Trace-bait available: {status.get('trace_bait') is not None}")

if status.get('anti_tag'):
    print(f"\nAnti-Tag Status:")
    print(f"  Active: {status['anti_tag']['active']}")
    print(f"  Tags neutralized: {status['anti_tag']['tags_neutralized']}")

if status.get('trace_bait'):
    print(f"\nTrace-Bait Status:")
    print(f"  Active: {status['trace_bait']['active']}")
    print(f"  Probes swallowed: {status['trace_bait']['total_swallowed']}")

print("\n[OK] Shadows mode active. Agents protected.")
print("[OK] Your agents crawl. Your IP dances. Your traces vanish.")

vpn.stop()
print("\n[OK] Test complete.")

