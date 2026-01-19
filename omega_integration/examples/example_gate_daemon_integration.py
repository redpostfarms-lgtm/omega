#!/usr/bin/env python3
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
