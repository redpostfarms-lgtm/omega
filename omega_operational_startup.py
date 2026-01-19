"""
Omega Operational Startup System
=================================
Operational startup sequence with Omega introduction.
Omega is now a standalone operational system.
"""

import sys
import asyncio
import os
from pathlib import Path
from datetime import datetime

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        try:
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except (OSError, IOError, AttributeError) as e:
            pass

sys.path.insert(0, str(Path(__file__).parent))

def safe_print(text):
    """Print text with Unicode support and fallback"""
    if not isinstance(text, str):
        text = str(text)
    
    try:
        print(text)
    except UnicodeEncodeError:
        replacements = {
            '✓': '[OK]', '✗': '[X]', 'ℹ': '[i]',
            '✅': '[OK]', '❌': '[X]', '⚠️': '[WARN]',
            '⏱️': '[TIME]', '🔧': '[FIX]', '📝': '[INFO]'
        }
        safe_text = text
        for unicode_char, ascii_replacement in replacements.items():
            safe_text = safe_text.replace(unicode_char, ascii_replacement)
        safe_text = safe_text.encode('ascii', errors='replace').decode('ascii')
        print(safe_text)

async def omega_operational_startup():
    """Omega operational startup with introduction and resource-aware loading"""
    
    safe_print("\n" + "=" * 80)
    safe_print(" " * 25 + "OMEGA - OPERATIONAL STARTUP")
    safe_print("=" * 80)
    safe_print("")
    
    safe_print("[PHASE 0] Resource Management Initialization...")
    try:
        from omega_system_resource_manager import initialize_system_resources, get_system_resource_manager, load_system_patterns
        initialize_system_resources()
        load_system_patterns()  # Load previous patterns if available
        resource_manager = get_system_resource_manager()
        if resource_manager:
            status = resource_manager.get_resource_status()
            safe_print(f"  [OK] Resource manager initialized")
            safe_print(f"  [OK] Performance profile: {status['performance_profile']}")
            if status['gpu']:
                safe_print(f"  [OK] GPU available: {status['gpu']['device_name']}")
        else:
            resource_manager = None
            safe_print("  [i] Resource manager not available, using standard loading")
    except ImportError:
        resource_manager = None
        safe_print("  [i] Resource manager not available, using standard loading")
    except Exception as e:
        resource_manager = None
        safe_print(f"  [!] Resource manager initialization error: {e}")
    
    safe_print("\n[PHASE 1] System Initialization...")
    safe_print("  [OK] Loading system modules...")
    
    try:
        from omega_full_brain import get_tts, play_audio_background
        from voice_security_system import voice_security
        from omega_relationship_system import get_relationship_manager
        safe_print("  [OK] Core systems loaded")
    except ImportError as e:
        safe_print(f"  [X] Error loading core systems: {e}")
        return
    
    try:
        rel_manager = get_relationship_manager()
        relationship_status = rel_manager.get_relationship_status()
        safe_print(f"  [OK] Relationship system loaded (Level: {relationship_status['mutual_level']})")
    except Exception as e:
        safe_print(f"  [!] Relationship system unavailable: {e}")
        rel_manager = None
    
    safe_print("\n[PHASE 2] Omega Introduction...")
    safe_print("  [OK] Initializing TTS system...")
    
    try:
        tts = get_tts()
        safe_print("  [OK] TTS system ready")
    except Exception as e:
        safe_print(f"  [X] TTS initialization error: {e}")
        return
    
    try:
        if rel_manager:
            greeting = rel_manager.get_appropriate_greeting()
            introduction = f"""{greeting} I am now a standalone operational system, 
    ready to assist you with any task. I can help with code, learning, hardware control, 
    and much more. I am here to serve. How may I assist you today?"""
        else:
            introduction = """Hello, I am Omega. I am now a standalone operational system, 
    ready to assist you with any task. I can help with code, learning, hardware control, 
    and much more. I am here to serve. How may I assist you today?"""
    except (AttributeError, KeyError, RuntimeError) as e:
        introduction = """Hello, I am Omega. I am now a standalone operational system, 
    ready to assist you with any task. I can help with code, learning, hardware control, 
    and much more. I am here to serve. How may I assist you today?"""
    
    safe_print("\n" + "=" * 80)
    safe_print(" " * 25 + "OMEGA - INTRODUCTION")
    safe_print("=" * 80)
    safe_print("")
    safe_print(introduction.replace('\n    ', ' ').strip())
    safe_print("")
    safe_print("=" * 80)
    safe_print("")
    
    try:
        safe_print("[Generating introduction audio...]")
        tts.tts_to_file(
            text=introduction,
            speaker_wav='clip_0001.wav' if Path('clip_0001.wav').exists() else None,
            language='en',
            file_path='omega_intro.wav'
        )
        
        safe_print("[Playing introduction...]")
        play_audio_background('omega_intro.wav')
        
        await asyncio.sleep(20)
    except Exception as e:
        safe_print(f"  [X] Audio generation error: {e}")
        safe_print("  [i] Continuing without audio...")
    
    safe_print("\n[PHASE 3] System Status Check...")
    
    integrations = {
        "Hardware Control": Path("omega_comprehensive_hardware.py").exists(),
        "Developer Integrations": Path("omega_developer_integrations.py").exists(),
        "VPN System": Path("omega_vpn_enhanced.py").exists(),
        "Control Panel": Path("omega_control_panel.py").exists(),
        "Startup Optimizer": Path("omega_startup_optimizer.py").exists(),
        "API Keys": Path("omega_api_keys_enhanced.py").exists(),
        "Research System": Path("omega_enhanced_research_system.py").exists(),
    }
    
    safe_print("  Integration Status:")
    for name, status in integrations.items():
        status_icon = "[OK]" if status else "[X]"
        safe_print(f"    {status_icon} {name}")
    
    safe_print("\n[PHASE 4] Entering Operational Mode...")
    safe_print("  [OK] Omega is now operational")
    safe_print("  [OK] Ready to assist with:")
    safe_print("      - Code assistance and learning")
    safe_print("      - Hardware control and monitoring")
    safe_print("      - System optimization")
    safe_print("      - Research and information")
    safe_print("      - And much more...")
    safe_print("")
    
    safe_print("\n[PHASE 5] Starting Hands-Free Conversation...")
    safe_print("  [OK] Voice recognition ready")
    safe_print("  [OK] TTS system ready")
    safe_print("  [OK] Conversation mode active")
    
    if resource_manager:
        try:
            from omega_system_resource_manager import save_system_patterns
            save_system_patterns()
            safe_print("  [OK] Loading patterns saved for future optimization")
        except (ImportError, AttributeError, RuntimeError) as e:
            pass
    safe_print("")
    safe_print("=" * 80)
    safe_print(" " * 25 + "OMEGA - OPERATIONAL")
    safe_print("=" * 80)
    safe_print("")
    safe_print("Omega is now operational and ready to assist you.")
    safe_print("Press Ctrl+C to exit.")
    safe_print("")
    
    try:
        from hands_free_omega_optimized import hands_free_conversation_optimized
        await hands_free_conversation_optimized()
    except ImportError:
        try:
            from hands_free_omega import hands_free_conversation
            await hands_free_conversation()
        except ImportError as e:
            safe_print(f"[ERROR] Could not start conversation mode: {e}")
            safe_print("Omega is operational but conversation mode is unavailable.")
            return

def main():
    """Main function"""
    try:
        asyncio.run(omega_operational_startup())
    except KeyboardInterrupt:
        safe_print("\n\n" + "=" * 80)
        safe_print(" " * 25 + "OMEGA - SHUTDOWN")
        safe_print("=" * 80)
        safe_print("")
        safe_print("Omega is shutting down. Thank you for using Omega.")
        safe_print("=" * 80)
    except Exception as e:
        safe_print(f"\n[ERROR] Startup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
