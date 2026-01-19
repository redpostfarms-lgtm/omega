# Omega Voice Integration Guide

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
