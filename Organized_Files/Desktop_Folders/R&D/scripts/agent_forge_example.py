# -*- coding: utf-8 -*-
# AGENT FORGE - Usage Examples
# Quick-start guide for generating battle-tested system prompts

from agent_forge import forge_system_prompt, generate_agent_prompt, save_prompt_to_file, AGENT_TEMPLATES

# Example 1: Generate from pre-built template
print("=" * 60)
print("Example 1: Use a pre-built template")
print("=" * 60)

coder_prompt = generate_agent_prompt("coder", your_name="Red Post Farms")
print(coder_prompt)
print("\n")

# Example 2: Custom agent from scratch
print("=" * 60)
print("Example 2: Create custom agent")
print("=" * 60)

custom_prompt = forge_system_prompt(
    agent_name="TaxOracle",
    short_description="Federal and state tax compliance expert",
    your_name="Red Post Farms",
    personality_description="Precise. Factual. Cites IRS.gov. Knows every code section. No guessing on tax matters.",
    sign_off_emoji="💰",
    sign_off_text="taxes optimized, IRS happy"
)

print(custom_prompt[:300] + "...")  # First 300 chars
print("\n")

# Example 3: Override template defaults
print("=" * 60)
print("Example 3: Override template with custom values")
print("=" * 60)

gatekeeper_pro = generate_agent_prompt(
    "gatekeeper",
    your_name="Red Post Farms",
    agent_name="Gatekeeper Pro",
    sign_off_text="doors opened, knowledge delivered, zero excuses"
)

print(gatekeeper_pro[:300] + "...")
print("\n")

# Example 4: Save to file for use in other systems
print("=" * 60)
print("Example 4: Save prompts to files")
print("=" * 60)

researcher_prompt = generate_agent_prompt("researcher", your_name="Red Post Farms")
save_prompt_to_file(researcher_prompt, "researcher_agent_prompt.txt")

print("\n✅ All examples complete!")
print("\nAvailable templates:", list(AGENT_TEMPLATES.keys()))

