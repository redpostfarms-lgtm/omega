#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run complete AZZ voice profile setup
Automated execution of all voice system initialization steps
"""

import asyncio
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

# Add omega_voice_profiles to path
sys.path.insert(0, str(Path(__file__).parent / "omega_voice_profiles"))

from azz_voice_system import AZZVoiceSystem, AZZ_VOICE_SAMPLE


async def main():
    """Run complete AZZ voice setup"""
    print("\n" + "=" * 70)
    print("  AZZ VOICE PROFILE - AUTOMATED SETUP")
    print("=" * 70 + "\n")

    azz = AZZVoiceSystem()

    # Step 1: Analyze all audio samples
    print("\n[Step 1/4] Analyzing audio samples...")
    print("-" * 70)

    samples_dir = azz.voice_path / "samples"
    audio_files = list(samples_dir.glob("*.wav"))

    if not audio_files:
        print(f"✗ No WAV files found in {samples_dir}")
        return

    print(f"Found {len(audio_files)} audio files")

    analyses = []
    for audio_file in audio_files:
        print(f"\nAnalyzing: {audio_file.name}")
        try:
            analysis = azz.analyze_audio_file(audio_file)
            analyses.append({
                "file": audio_file,
                "analysis": analysis
            })

            print(f"  ✓ Duration: {analysis['duration']:.2f}s")
            print(f"  ✓ Pitch: {analysis['pitch']['mean']:.2f} Hz")
            if 'spectral_features' in analysis:
                print(f"  ✓ Spectral centroid: {analysis['spectral_features']['centroid_mean']:.2f} Hz")

        except Exception as e:
            print(f"  ✗ Error analyzing {audio_file.name}: {e}")

    print(f"\n✓ Analyzed {len(analyses)} files successfully")

    # Step 2: Select best sample for reference
    print("\n[Step 2/4] Selecting best reference sample...")
    print("-" * 70)

    # Find sample with good duration and clear pitch
    best_sample = None
    best_score = 0

    for item in analyses:
        analysis = item["analysis"]

        # Score based on duration (prefer 10-30 seconds) and pitch clarity
        duration_score = 1.0 if 10 <= analysis["duration"] <= 30 else 0.5
        pitch_score = 1.0 if analysis["pitch"]["std"] < 50 else 0.5

        score = duration_score * pitch_score

        if score > best_score:
            best_score = score
            best_sample = item

    if best_sample:
        print(f"\n✓ Selected: {best_sample['file'].name}")
        print(f"  Duration: {best_sample['analysis']['duration']:.2f}s")
        print(f"  Mean pitch: {best_sample['analysis']['pitch']['mean']:.2f} Hz")

        # Copy to azz.wav
        import shutil
        shutil.copy2(best_sample['file'], AZZ_VOICE_SAMPLE)
        print(f"  ✓ Copied to {AZZ_VOICE_SAMPLE}")

    # Step 3: Create voice profile
    print("\n[Step 3/4] Creating voice profile...")
    print("-" * 70)

    try:
        profile = azz.create_voice_profile_from_samples([item["file"] for item in analyses])

        print(f"\n✓ Voice Profile Created:")
        print(f"  Samples: {profile.get('num_samples', 0)}")
        print(f"  Total duration: {profile.get('total_duration', 0):.2f}s")
        if 'pitch' in profile:
            print(f"  Average pitch: {profile['pitch']['mean']:.2f} Hz")
            print(f"  Pitch range: {profile['pitch']['min']:.2f} - {profile['pitch']['max']:.2f} Hz")

        # Save profile
        profile_file = azz.voice_path / "azz_profile.json"
        import json
        with open(profile_file, "w") as f:
            json.dump(profile, f, indent=2)
        print(f"  ✓ Profile saved to {profile_file}")

    except Exception as e:
        print(f"✗ Error creating profile: {e}")

    # Step 4: Test synthesis (if Azure key available)
    print("\n[Step 4/4] Testing voice synthesis...")
    print("-" * 70)

    import os
    if os.getenv("AZURE_SPEECH_KEY"):
        try:
            test_text = "Hello, this is the AZZ voice profile test."
            test_output = azz.voice_path / "test_synthesis.wav"

            print(f"Testing: '{test_text}'")
            azz.synthesize_with_azure(test_text, test_output)

            if test_output.exists():
                print(f"✓ Synthesis successful: {test_output}")
            else:
                print("✗ Synthesis file not created")

        except Exception as e:
            print(f"✗ Azure synthesis error: {e}")
            print("  Note: Requires AZURE_SPEECH_KEY environment variable")
    else:
        print("⚠ Azure Speech SDK key not configured")
        print("  Set AZURE_SPEECH_KEY environment variable to test synthesis")

    # Summary
    print("\n" + "=" * 70)
    print("  AZZ VOICE PROFILE SETUP COMPLETE")
    print("=" * 70)

    print("\n✓ Setup Summary:")
    print(f"  • Audio samples analyzed: {len(analyses)}")
    print(f"  • Reference sample: {AZZ_VOICE_SAMPLE.name}")
    print(f"  • Voice profile: {azz.voice_path / 'azz_profile.json'}")
    print(f"  • Registry: H:\\The Gatekeeper\\voices\\voice_registry.json")

    print("\nNext Steps:")
    print("  1. Set AZURE_SPEECH_KEY for Azure TTS")
    print("  2. Update Omega codebase to use AZZ profile")
    print("  3. Test voice synthesis in your application")

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
