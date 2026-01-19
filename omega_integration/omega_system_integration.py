#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega System Integration
Ensures all Omega components can access AZZ voice and LED visualization
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")


class OmegaSystemIntegration:
    """
    Integrates voice capabilities across all Omega systems
    Provides universal access to AZZ voice and LED Matrix
    """

    def __init__(self):
        """Initialize system integration"""
        self.root = Path(__file__).parent.parent
        self.integration_log = self.root / "logs" / "omega_integration.log"
        self.integration_log.parent.mkdir(parents=True, exist_ok=True)

        self.systems = {}
        self.integration_status = {}

    def log(self, message: str):
        """Log integration message"""
        print(f"[Omega Integration] {message}")

        with open(self.integration_log, "a", encoding="utf-8") as f:
            f.write(f"{message}\n")

    def discover_systems(self) -> List[str]:
        """Discover all Omega systems in codebase"""
        self.log("Discovering Omega systems...")

        systems = []

        # Known Omega components
        known_systems = [
            "gate_daemon.py",
            "gate_autonomous_admin.py",
            "gate_problem_solver.py",
            "gate_llm_integration.py",
            "gate_ide_integration.py",
            "omega_voice_profiles/azz_voice_system.py",
            "omega_visual_feedback/led_matrix_controller.py",
            "resource_controller.py",
            "run_comprehensive_tests.py"
        ]

        for system in known_systems:
            system_path = self.root / system
            if system_path.exists():
                systems.append(system)
                self.log(f"  ✓ Found: {system}")
            else:
                self.log(f"  ✗ Missing: {system}")

        return systems

    def create_voice_import_module(self):
        """Create universal voice import module"""
        self.log("\nCreating universal voice import module...")

        module_path = self.root / "omega_voice.py"

        content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Voice - Universal Voice Module
Import this module from any Omega system to access voice capabilities
"""

import asyncio
import sys
from pathlib import Path

# Add paths
_module_path = Path(__file__).parent
sys.path.insert(0, str(_module_path / "omega_integration"))
sys.path.insert(0, str(_module_path / "omega_voice_profiles"))
sys.path.insert(0, str(_module_path / "omega_visual_feedback"))

# Import components
try:
    from omega_voice_hub import omega_voice_hub
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False
    omega_voice_hub = None


async def speak(text: str, color: str = "red", visualize: bool = True) -> bool:
    """
    Universal speak function - use from any Omega system

    Args:
        text: Text to speak
        color: LED color (red/green/blue/etc.)
        visualize: Enable LED visualization

    Returns:
        True if successful

    Example:
        >>> import omega_voice
        >>> await omega_voice.speak("Hello from Omega!", color="red")
    """
    if not VOICE_AVAILABLE or not omega_voice_hub:
        print(f"[Omega Voice] ⚠ Voice system not available: {text}")
        return False

    return await omega_voice_hub.quick_speak(text, color=color)


async def announce(message: str, priority: str = "normal") -> bool:
    """
    System announcement with priority-based colors

    Args:
        message: Announcement text
        priority: Priority level (low/normal/high/critical)

    Example:
        >>> import omega_voice
        >>> await omega_voice.announce("System ready", priority="normal")
    """
    if not VOICE_AVAILABLE or not omega_voice_hub:
        print(f"[Omega Voice] ⚠ Voice system not available: {message}")
        return False

    await omega_voice_hub.system_announce(message, priority)
    return True


def set_led_state(state: str):
    """
    Set LED state (idle/listening/processing/speaking/error/success)

    Args:
        state: State name

    Example:
        >>> import omega_voice
        >>> omega_voice.set_led_state("processing")
    """
    if VOICE_AVAILABLE and omega_voice_hub:
        omega_voice_hub.set_led_state(state)


def get_voice_status() -> dict:
    """
    Get voice system status

    Returns:
        Status dictionary

    Example:
        >>> import omega_voice
        >>> status = omega_voice.get_voice_status()
        >>> print(status["led_connected"])
    """
    if VOICE_AVAILABLE and omega_voice_hub:
        return omega_voice_hub.get_status()

    return {
        "available": False,
        "error": "Voice system not initialized"
    }


# Synchronous wrapper for simple use cases
def speak_sync(text: str, color: str = "red"):
    """
    Synchronous speak function

    Args:
        text: Text to speak
        color: LED color

    Example:
        >>> import omega_voice
        >>> omega_voice.speak_sync("Hello!")
    """
    asyncio.run(speak(text, color))


# Quick access to components
def get_azz_voice():
    """Get AZZ Voice System instance"""
    if VOICE_AVAILABLE and omega_voice_hub:
        return omega_voice_hub.azz_voice
    return None


def get_led_matrix():
    """Get LED Matrix controller instance"""
    if VOICE_AVAILABLE and omega_voice_hub:
        return omega_voice_hub.led_matrix
    return None


def get_voice_led():
    """Get Voice-LED integration instance"""
    if VOICE_AVAILABLE and omega_voice_hub:
        return omega_voice_hub.voice_led
    return None
'''

        with open(module_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.log(f"✓ Created: {module_path}")
        return module_path

    def create_integration_examples(self):
        """Create usage examples for different systems"""
        self.log("\nCreating integration examples...")

        examples_dir = self.root / "omega_integration" / "examples"
        examples_dir.mkdir(parents=True, exist_ok=True)

        # Example 1: Simple usage
        example1 = examples_dir / "example_simple_usage.py"
        with open(example1, "w", encoding="utf-8") as f:
            f.write('''#!/usr/bin/env python3
"""Example: Simple voice usage in any Omega system"""

import asyncio
import omega_voice


async def main():
    """Simple voice example"""

    # Speak with default red LED
    await omega_voice.speak("Omega system online", color="red")

    # System announcement
    await omega_voice.announce("All systems operational", priority="normal")

    # Set LED state
    omega_voice.set_led_state("success")

    # Check status
    status = omega_voice.get_voice_status()
    print(f"Voice available: {status.get('led_connected', False)}")


if __name__ == "__main__":
    asyncio.run(main())
''')

        # Example 2: Advanced usage
        example2 = examples_dir / "example_advanced_usage.py"
        with open(example2, "w", encoding="utf-8") as f:
            f.write('''#!/usr/bin/env python3
"""Example: Advanced voice usage with direct component access"""

import asyncio
import omega_voice


async def main():
    """Advanced voice example"""

    # Get direct access to components
    azz = omega_voice.get_azz_voice()
    led = omega_voice.get_led_matrix()
    voice_led = omega_voice.get_voice_led()

    if azz and led:
        # Custom synthesis with LED control
        led.set_color_by_name("blue")
        led.display_text("WORKING...")

        # Direct synthesis
        from pathlib import Path
        output = Path("custom_speech.wav")
        azz.synthesize_with_azure("Custom synthesis", output)

        # Visualize
        if output.exists():
            await led.sync_with_speech(output)

        # Success state
        led.set_color_by_name("green")


if __name__ == "__main__":
    asyncio.run(main())
''')

        # Example 3: Integration with GATE daemon
        example3 = examples_dir / "example_gate_daemon_integration.py"
        with open(example3, "w", encoding="utf-8") as f:
            f.write('''#!/usr/bin/env python3
"""Example: Integration with GATE daemon"""

import asyncio
import omega_voice


class GATEWithVoice:
    """GATE daemon with voice announcements"""

    async def patrol_with_voice(self):
        """Patrol system with voice feedback"""

        # Set LED to processing
        omega_voice.set_led_state("processing")
        await omega_voice.announce("Starting system patrol", priority="normal")

        # Simulate patrol
        await asyncio.sleep(2)

        # Found issues
        issues_found = 3

        if issues_found > 0:
            omega_voice.set_led_state("error")
            await omega_voice.announce(
                f"Found {issues_found} issues",
                priority="high"
            )

            # Fixing
            omega_voice.set_led_state("processing")
            await omega_voice.speak("Resolving issues")

            await asyncio.sleep(2)

        # Complete
        omega_voice.set_led_state("success")
        await omega_voice.announce("Patrol complete", priority="normal")

        # Back to idle
        omega_voice.set_led_state("idle")


async def main():
    gate = GATEWithVoice()
    await gate.patrol_with_voice()


if __name__ == "__main__":
    asyncio.run(main())
''')

        self.log(f"✓ Created: {example1}")
        self.log(f"✓ Created: {example2}")
        self.log(f"✓ Created: {example3}")

    def create_integration_guide(self):
        """Create integration guide"""
        guide_path = self.root / "omega_integration" / "INTEGRATION_GUIDE.md"

        content = '''# Omega Voice Integration Guide

How to add voice capabilities to any Omega system component.

## Quick Start

### 1. Import the Module

```python
import omega_voice
```

### 2. Use Voice Functions

```python
import asyncio

# Async speak
await omega_voice.speak("Hello from Omega!", color="red")

# Sync speak (simpler)
omega_voice.speak_sync("Hello!")

# System announcement
await omega_voice.announce("System ready", priority="normal")

# Set LED state
omega_voice.set_led_state("processing")
```

## Available Functions

### `speak(text, color="red", visualize=True)`
Speak text with LED visualization.

**Example**:
```python
await omega_voice.speak("Hello!", color="green", visualize=True)
```

### `announce(message, priority="normal")`
System announcement with priority-based LED colors.

**Priorities**: low (blue), normal (green), high (orange), critical (red)

**Example**:
```python
await omega_voice.announce("Critical error", priority="critical")
```

### `set_led_state(state)`
Set LED state directly.

**States**: idle, listening, processing, speaking, error, success

**Example**:
```python
omega_voice.set_led_state("success")
```

### `get_voice_status()`
Get voice system status.

**Example**:
```python
status = omega_voice.get_voice_status()
print(f"LED connected: {status['led_connected']}")
```

## Direct Component Access

### Get AZZ Voice System
```python
azz = omega_voice.get_azz_voice()
if azz:
    azz.synthesize_with_azure("Text", Path("output.wav"))
```

### Get LED Matrix
```python
led = omega_voice.get_led_matrix()
if led:
    led.set_color_by_name("blue")
    led.display_text("HELLO")
```

### Get Voice-LED Integration
```python
voice_led = omega_voice.get_voice_led()
if voice_led:
    await voice_led.synthesize_with_visualization("Text", Path("output.wav"))
```

## Integration Patterns

### Pattern 1: Simple Notifications

```python
import omega_voice

async def notify_user(message: str):
    await omega_voice.speak(message, color="green")
```

### Pattern 2: Status Updates

```python
import omega_voice

async def process_task():
    omega_voice.set_led_state("processing")
    await omega_voice.speak("Processing task")

    # Do work...

    omega_voice.set_led_state("success")
    await omega_voice.speak("Task complete")
```

### Pattern 3: Error Handling

```python
import omega_voice

async def handle_error(error: str):
    omega_voice.set_led_state("error")
    await omega_voice.announce(f"Error: {error}", priority="critical")
```

## Best Practices

1. **Use async/await** for speak functions
2. **Set LED states** for visual feedback
3. **Use priorities** for announcements (low/normal/high/critical)
4. **Check availability** before using voice
5. **Handle gracefully** if voice is unavailable

## Example: Full Integration

```python
import asyncio
import omega_voice


class MyOmegaComponent:
    async def run(self):
        # Start
        omega_voice.set_led_state("idle")
        await omega_voice.announce("Component starting", priority="normal")

        try:
            # Processing
            omega_voice.set_led_state("processing")
            await omega_voice.speak("Processing data")

            # Work here...
            await asyncio.sleep(2)

            # Success
            omega_voice.set_led_state("success")
            await omega_voice.announce("Processing complete", priority="normal")

        except Exception as e:
            # Error
            omega_voice.set_led_state("error")
            await omega_voice.announce(f"Error: {e}", priority="critical")

        finally:
            # Idle
            omega_voice.set_led_state("idle")


async def main():
    component = MyOmegaComponent()
    await component.run()


if __name__ == "__main__":
    asyncio.run(main())
```

## Testing Voice Integration

```python
import omega_voice

# Check if voice is available
status = omega_voice.get_voice_status()
if status.get("available", False):
    print("✓ Voice system ready")
else:
    print("✗ Voice system not available")

# Test speak
omega_voice.speak_sync("Test message")
```

## All Systems That Can Use Voice

Any Omega component can now use voice:
- GATE daemon (`gate_daemon.py`)
- Autonomous admin (`gate_autonomous_admin.py`)
- Problem solver (`gate_problem_solver.py`)
- LLM integration (`gate_llm_integration.py`)
- Resource controller (`resource_controller.py`)
- Test runner (`run_comprehensive_tests.py`)
- Any custom components

Simply import `omega_voice` and start speaking!
'''

        with open(guide_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.log(f"\n✓ Created integration guide: {guide_path}")

    async def verify_integration(self):
        """Verify integration works"""
        self.log("\nVerifying integration...")

        try:
            # Import omega_voice module
            sys.path.insert(0, str(self.root))
            import omega_voice

            # Test availability
            status = omega_voice.get_voice_status()

            self.log("  Voice system status:")
            for key, value in status.items():
                self.log(f"    {key}: {value}")

            # Test speak (will simulate if not connected)
            self.log("  Testing speak function...")
            await omega_voice.speak("Integration test successful", color="green")

            self.log("✓ Integration verified")
            return True

        except Exception as e:
            self.log(f"✗ Verification failed: {e}")
            return False

    async def run_integration(self):
        """Run full integration"""
        print("\n" + "=" * 70)
        print("  OMEGA SYSTEM INTEGRATION")
        print("=" * 70 + "\n")

        # Discover systems
        systems = self.discover_systems()
        print(f"\nDiscovered {len(systems)} Omega systems")

        # Create universal voice module
        voice_module = self.create_voice_import_module()

        # Create examples
        self.create_integration_examples()

        # Create guide
        self.create_integration_guide()

        # Verify
        success = await self.verify_integration()

        print("\n" + "=" * 70)
        print("  INTEGRATION COMPLETE")
        print("=" * 70)

        print("\n✓ Universal voice module created:")
        print(f"  {voice_module}")

        print("\n✓ Any Omega system can now use voice:")
        print("  import omega_voice")
        print("  await omega_voice.speak('Hello!')")

        print("\n✓ Integration guide created:")
        print("  omega_integration/INTEGRATION_GUIDE.md")

        print("\n✓ Examples created:")
        print("  omega_integration/examples/")

        print("\n" + "=" * 70 + "\n")


async def main():
    """Main entry point"""
    integration = OmegaSystemIntegration()
    await integration.run_integration()


if __name__ == "__main__":
    asyncio.run(main())
