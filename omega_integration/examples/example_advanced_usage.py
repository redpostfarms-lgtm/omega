#!/usr/bin/env python3
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
