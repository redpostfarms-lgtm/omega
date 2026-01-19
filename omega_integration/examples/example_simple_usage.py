#!/usr/bin/env python3
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
