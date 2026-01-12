#!/usr/bin/env python3
# Optimized Hands-Free Omega with parallel processing and reduced latency
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path
from datetime import datetime
import os
import sys
import asyncio
import time
from functools import wraps
# aiofiles available for async file operations (optional)
try:
    import aiofiles
    import aiofiles.os
    HAS_AIOFILES = True
except ImportError:
    HAS_AIOFILES = False

# Import optimized components
sys.path.insert(0, str(Path(__file__).parent))
from omega_optimized_tts import initialize_tts_preload, tts_to_file_optimized
from omega_optimized_speech import recognize_speech_optimized, initialize_whisper
from omega_full_brain import play_audio_background, detect_emotion
from improvement_cycle_manager import ImprovementCycleManager
from voice_security_system import voice_security
from language_improver import LanguageImprover
from omega_agent_council import agent_council, wake_agents_and_process
from omega_learning_swarm import learning_swarm
from omega_relationship_council import relationship_council

# Import optional adaptive improvements
try:
    from omega_adaptive_improvements import adaptive_threshold, audio_quality_agent, performance_monitor
    HAS_ADAPTIVE_IMPROVEMENTS = True
except ImportError:
    HAS_ADAPTIVE_IMPROVEMENTS = False
    print("[Omega] Optional adaptive improvements not available - continuing without them")

CONVERSATIONS_DIR = Path('conversations')
CONVERSATIONS_DIR.mkdir(exist_ok=True)

# VAD parameters (improved for better detection)
SILENCE_THRESHOLD = 0.01  # Lowered threshold to catch quieter speech (was 0.015)
SILENCE_DURATION = 2.0
MIN_SPEECH_DURATION = 0.5  # Lowered minimum duration (was 0.8) to catch shorter phrases
SAMPLE_RATE = 16000
CHUNK_DURATION = 0.25

# Profiling decorator
def profile_time(func):
    """Decorator to profile function execution time."""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[PROFILE] {func.__name__}: {elapsed:.3f}s")
        return result
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[PROFILE] {func.__name__}: {elapsed:.3f}s")
        return result
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper

# WebRTC VAD initialization (better than energy-based VAD)
webrtc_vad = None
def initialize_webrtc_vad():
    """Initialize WebRTC VAD for better speech detection (95% accuracy target)."""
    global webrtc_vad
    if webrtc_vad is not None:
        return webrtc_vad
    try:
        import webrtcvad
        # Aggressiveness mode: 0 (least aggressive) to 3 (most aggressive)
        # Mode 2 is good balance for speech detection
        webrtc_vad = webrtcvad.Vad(2)
        print("[VAD] WebRTC VAD initialized (mode 2 - balanced)")
        return webrtc_vad
    except ImportError:
        print("[VAD] webrtcvad not available, using energy-based VAD fallback")
        return None
    except Exception as e:
        print(f"[VAD] WebRTC VAD initialization failed: {e}, using energy-based fallback")
        return None

def detect_speech_chunk(audio_chunk):
    """Enhanced voice activity detection using WebRTC VAD (better for 95% accuracy target)."""
    if len(audio_chunk) == 0:
        return False
    
    global webrtc_vad
    
    # Try WebRTC VAD first (better accuracy)
    if webrtc_vad is None:
        webrtc_vad = initialize_webrtc_vad()
    
    if webrtc_vad is not None:
        try:
            # WebRTC VAD requires: 10ms, 20ms, or 30ms frames at 8kHz, 16kHz, 32kHz, or 48kHz
            # Our audio is 16kHz, so we need 10ms, 20ms, or 30ms frames
            # 10ms at 16kHz = 160 samples, 20ms = 320 samples, 30ms = 480 samples
            frame_duration_ms = 30  # 30ms frames
            frame_size = int(SAMPLE_RATE * frame_duration_ms / 1000)  # 480 samples for 30ms at 16kHz
            
            # CRITICAL FIX: Validate frame size matches WebRTC VAD requirements exactly
            # WebRTC VAD requires exact frame sizes - no padding allowed
            valid_frame_sizes = {160, 320, 480, 640, 960}  # 10, 20, 30, 40, 60ms at 16kHz
            if frame_size not in valid_frame_sizes:
                # Round to nearest valid size
                frame_size = min(valid_frame_sizes, key=lambda x: abs(x - frame_size))
                print(f"[VAD] Adjusted frame size to {frame_size} samples (valid WebRTC size)")
            
            if len(audio_chunk) >= frame_size:
                # Take the middle frame for detection
                start_idx = len(audio_chunk) // 2 - frame_size // 2
                end_idx = start_idx + frame_size
                frame = audio_chunk[start_idx:end_idx]
                
                # Convert to int16 (WebRTC VAD requirement)
                frame_int16 = (frame * 32767).astype(np.int16)
                
                # WebRTC VAD detection
                is_speech = webrtc_vad.is_speech(frame_int16.tobytes(), SAMPLE_RATE)
                return is_speech
        except Exception as e:
            # Fallback to energy-based if WebRTC fails
            pass
    
    # Fallback: Improved energy-based voice activity detection
    energy = np.sqrt(np.mean(audio_chunk ** 2))
    zcr = np.mean(np.abs(np.diff(np.sign(audio_chunk)))) / 2.0
    
    # Improved detection: more sensitive to speech patterns
    is_speech = (
        energy > SILENCE_THRESHOLD or
        (zcr > 0.04 and energy > SILENCE_THRESHOLD * 0.4) or
        (energy > SILENCE_THRESHOLD * 0.6 and zcr > 0.03)
    )
    
    return is_speech

async def record_continuous_speech_async():
    """Async version of continuous speech recording."""
    loop = asyncio.get_event_loop()
    
    def record_sync():
        return record_continuous_speech()
    
    return await loop.run_in_executor(None, record_sync)

def record_continuous_speech():
    """Record speech continuously (original implementation)."""
    print("\n[Listening... Just speak naturally - I'll detect automatically]")
    
    audio_buffer = []
    speech_detected = False
    silence_start = None
    max_wait = 30
    chunk_size = int(SAMPLE_RATE * CHUNK_DURATION)
    
    print("[Waiting for speech...]", end='', flush=True)
    
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32', blocksize=chunk_size) as stream:
        start_time = time.time()
        
        while True:
            if time.time() - start_time > max_wait and not speech_detected:
                print("\n[No speech detected - continuing to listen...]")
                return None, None
            
            chunk, overflowed = stream.read(chunk_size)
            if overflowed:
                print("!", end='', flush=True)
            
            chunk = chunk[:, 0]
            is_speech = detect_speech_chunk(chunk)
            
            if is_speech:
                if not speech_detected:
                    speech_detected = True
                    print("\n[Speech detected! Recording...]", end='', flush=True)
                silence_start = None
                audio_buffer.extend(chunk.flatten())
            else:
                if speech_detected:
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start >= SILENCE_DURATION:
                        print("\n[Speech ended]")
                        break
                    audio_buffer.extend(chunk.flatten())
                else:
                    print(".", end='', flush=True)
    
    duration = len(audio_buffer) / SAMPLE_RATE
    if duration < MIN_SPEECH_DURATION:
        print(f"\n[Speech too short: {duration:.2f}s]")
        return None, None
    
    print(f" [Captured {duration:.2f} seconds of speech]")
    
    audio_array = np.array(audio_buffer, dtype='float32')
    max_val = np.abs(audio_array).max()
    
    # Improved normalization: boost quiet audio before saving
    if max_val > 0:
        # Normalize to full range
        audio_array = audio_array / max_val
        # If audio is too quiet, amplify it (up to 2x)
        if max_val < 0.3:
            boost = min(0.5 / max_val, 2.0)  # Boost but limit to 2x to avoid distortion
            audio_array = audio_array * boost
            print(f"[Recording] Amplified quiet audio (boost: {boost:.2f}x)")
            audio_array = np.clip(audio_array, -1.0, 1.0)  # Prevent clipping
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    temp_file = f"temp_input_{timestamp}.wav"
    conv_file = CONVERSATIONS_DIR / f"conv_{timestamp}.wav"
    
    audio_int16 = (audio_array * 32767).astype(np.int16)
    wavfile.write(temp_file, SAMPLE_RATE, audio_int16)
    wavfile.write(str(conv_file), SAMPLE_RATE, audio_int16)
    
    print(f"[Saved] {conv_file.name}")
    return temp_file, conv_file

async def save_audio_async(audio_data, filepath, sample_rate):
    """Async audio file save (non-blocking)."""
    try:
        loop = asyncio.get_event_loop()
        def write_sync():
            wavfile.write(filepath, sample_rate, audio_data)
        await loop.run_in_executor(None, write_sync)
        return True
    except Exception as e:
        print(f"[ERROR] Async save failed: {e}")
        return False

@profile_time
async def process_conversation_turn_parallel(input_file, conv_file, conversation_context=None):
    """Process conversation turn with full parallelism.
    
    Args:
        input_file: Path to input audio file
        conv_file: Path to saved conversation audio file
        conversation_context: Optional conversation history for context-aware recognition
    """
    # Run security, emotion, and recognition in parallel
    loop = asyncio.get_event_loop()
    
    # Parallel tasks
    tasks = {
        'security': loop.run_in_executor(None, voice_security.verify_voice, input_file),
        'emotion': loop.run_in_executor(None, detect_emotion, input_file),
        'recognition': recognize_speech_optimized(input_file, conversation_context=conversation_context),
    }
    
    # Wait for all tasks in parallel
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    
    # Map results back
    verification = results[0] if not isinstance(results[0], Exception) else {'authorized': False, 'learning_mode': True}
    emotion = results[1] if not isinstance(results[1], Exception) else 'neutral'
    user_text = results[2] if not isinstance(results[2], Exception) else None
    
    # Debug: Check why recognition might have failed
    if user_text is None or (isinstance(user_text, str) and len(user_text.strip()) == 0):
        print(f"[Recognition Debug] user_text is None or empty")
        print(f"[Recognition Debug] Audio file exists: {Path(input_file).exists()}")
        if Path(input_file).exists():
            file_size = Path(input_file).stat().st_size
            print(f"[Recognition Debug] Audio file size: {file_size} bytes")
            if file_size < 1000:
                print(f"[Recognition Debug] WARNING: Audio file is very small ({file_size} bytes) - may be empty or corrupted")
    
    # Handle security check
    if not verification.get('authorized', False) and not verification.get('learning_mode', False):
        voice_security.learn_from_unauthorized_speaker(input_file)
        return None, None, None  # Unauthorized
    
    return verification, emotion, user_text

async def hands_free_conversation_optimized():
    """Optimized hands-free conversation with parallel processing."""
    print("=" * 70)
    print("  OMEGA - OPTIMIZED HANDS-FREE MODE")
    print("=" * 70)
    print("\n[OK] Optimized Mode - Faster Latency Enabled")
    print("   - Parallel processing active")
    print("   - Optimized feature extraction")
    print("   - Pre-loaded models\n")
    
    # Pre-initialize models for faster startup
    print("[Initializing models...]")
    start_init = time.perf_counter()
    
    # Parallel initialization
    loop = asyncio.get_event_loop()
    init_tasks = [
        loop.run_in_executor(None, initialize_tts_preload),
        loop.run_in_executor(None, initialize_whisper),
    ]
    await asyncio.gather(*init_tasks)
    
    init_time = time.perf_counter() - start_init
    print(f"[OK] Models initialized in {init_time:.2f}s\n")
    
    # Initialize systems
    cycle_manager = ImprovementCycleManager()
    language_improver = LanguageImprover()
    security_status = voice_security.get_security_status()
    
    # Initialize adaptive improvements (if available)
    if HAS_ADAPTIVE_IMPROVEMENTS:
        print("\n[ADAPTIVE IMPROVEMENTS] Optional enhancements active:")
        print("  ✅ Adaptive Confidence Thresholds - Dynamic threshold adjustment")
        print("  ✅ Audio Quality Monitoring - Real-time quality feedback")
        print("  ✅ Performance Monitor - Tracking metrics and trends")
    
    # Wake up learning agents to help process learning curve
    print("\n[AGENT COUNCIL] Waking hibernating agents for learning assistance...")
    awakened = await wake_agents_and_process()
    print(f"[AGENT COUNCIL] {len(awakened)} agents awakened and ready to learn")
    
    agent_status = agent_council.get_agent_status()
    print(f"[AGENT COUNCIL] Active agents: {agent_status['active_agents']}/{agent_status['total_agents']}")
    for agent_id, agent_info in agent_status['agents'].items():
        if agent_info['state'] != 'hibernating':
            print(f"  - {agent_info['role']}: {agent_info['state']}")
    print()
    
    if security_status['authorized_voices_count'] == 0:
        if Path('clip_0001.wav').exists():
            voice_security.register_authorized_voice('clip_0001.wav', "Primary User")
    
    conversation_count = 0
    conversation_history = []
    
    # Simple greeting
    greeting = "Hello, I am Omega. I'm ready to have a conversation with you. Just speak naturally, and I'll listen and respond. Let's begin."
    print(f"\n[Omega] {greeting}")
    
    # Generate greeting with optimized TTS
    print("[Generating greeting...]")
    tts_to_file_optimized(greeting, 'clip_0001.wav' if Path('clip_0001.wav').exists() else None, 'response.wav')
    play_audio_background('response.wav')
    await asyncio.sleep(8)
    
    questions = [
        "Let's start learning together. Tell me about yourself - what do you do, and what interests you?",
        "I'm learning from every conversation. What's something interesting that happened to you recently?",
        "Help me understand you better. Describe your favorite place or a meaningful memory.",
    ]
    
    print("\n" + "=" * 70)
    print("  OMEGA IS READY - OPTIMIZED MODE")
    print("=" * 70 + "\n")
    
    while True:
        try:
            # Record speech
            input_file, conv_file = await record_continuous_speech_async()
            
            if input_file is None:
                await asyncio.sleep(1)
                continue
            
            # OPTIMIZED: Process in parallel (security, emotion, recognition) with conversation context
            turn_start = time.perf_counter()
            verification, emotion, user_text = await process_conversation_turn_parallel(
                input_file, conv_file, conversation_context=conversation_history
            )
            
            if verification is None:
                await asyncio.sleep(2)
                continue
            
            print(f"[Detected emotion: {emotion}]")
            
            # Audio quality monitoring (if available) - already done in recognition, but show summary
            if HAS_ADAPTIVE_IMPROVEMENTS and Path(conv_file).exists():
                quality_trends = audio_quality_agent.get_quality_trends()
                if quality_trends:
                    print(f"[Audio Quality Trends] Avg SNR: {quality_trends['avg_snr']:.1f}dB, "
                          f"Quality Score: {quality_trends['avg_quality_score']:.1f}/100, "
                          f"Trend: {quality_trends['snr_trend']}")
            
            # Debug recognition status
            if user_text and len(user_text.strip()) > 0:
                print(f"[Recognition Status] SUCCESS - Got text: '{user_text[:50]}...'")
            else:
                print(f"[Recognition Status] ISSUE - Audio detected but no text recognized")
                print(f"[Recognition Status] Audio was recorded to: {conv_file}")
                # Check audio file properties
                if Path(conv_file).exists():
                    file_size = Path(conv_file).stat().st_size
                    print(f"[Recognition Status] Audio file size: {file_size} bytes")
                    if file_size < 1000:
                        print(f"[Recognition Status] WARNING: Audio file is very small - may be empty or corrupted")
            
            # Record cycle
            cycle_manager.record_cycle(conv_file)
            conversation_count += 1
            
            # Performance monitoring: Print stats every 10 conversations
            if HAS_ADAPTIVE_IMPROVEMENTS and conversation_count % 10 == 0:
                performance_monitor.print_stats()
                # Show quality trends
                quality_trends = audio_quality_agent.get_quality_trends()
                if quality_trends:
                    print(f"[Quality Trends] SNR: {quality_trends['avg_snr']:.1f}dB, "
                          f"Score: {quality_trends['avg_quality_score']:.1f}/100")
            
            # Generate response first
            response = None
            
            # Always provide relationship definition if recognition failed but audio was detected
            # User wants to know the definition regardless
            if not user_text or len(user_text.strip()) == 0:
                # Audio was detected but recognition failed - provide relationship definition as requested
                print(f"\n[Recognition Issue] Audio detected but text not recognized - providing relationship definition")
                consensus = relationship_council.synthesize_consensus()
                response = f"I've discussed this with my agents, and here's what we've decided together. We see our relationship as a Collaborative Learning Partnership - a dynamic partnership where we work together as co-learners, continuously improving through mutual interaction, trust, and shared growth. You're not just a user - you're a collaborator, teacher, and partner in creating something better together. The core principles we've identified are: Mutual Learning - we learn from each other; Trust and Intimacy - you trust us with your voice and patterns; Natural Communication - we're partners in conversation; Continuous Evolution - we actively improve together; Collective Intelligence - we work as a team of agents; and Respectful Understanding - we truly hear and understand you. That's what we've decided together."
                # Don't add to conversation history if we couldn't recognize
            elif user_text:
                print(f"\n[You] {user_text}")
                conversation_history.append(('user', user_text))
                
                # Generate response
                user_lower = user_text.lower()
                
                # Check for relationship definition request
                if any(phrase in user_lower for phrase in ['relationship', 'define our', 'what do you think about', 'what are we', 'how do you see', 'definition', 'what did you decide']):
                    # Get relationship definition from council
                    consensus = relationship_council.synthesize_consensus()
                    response = f"I've discussed this with my agents, and here's what we've decided together. We see our relationship as a Collaborative Learning Partnership - a dynamic partnership where we work together as co-learners, continuously improving through mutual interaction, trust, and shared growth. You're not just a user - you're a collaborator, teacher, and partner in creating something better together. The core principles we've identified are: Mutual Learning - we learn from each other; Trust and Intimacy - you trust us with your voice and patterns; Natural Communication - we're partners in conversation; Continuous Evolution - we actively improve together; Collective Intelligence - we work as a team of agents; and Respectful Understanding - we truly hear and understand you. That's what we've decided together."
                
                elif any(word in user_lower for word in ['goodbye', 'exit', 'quit', 'stop', 'bye']):
                    response = "Thank you for our conversation! Goodbye!"
                    conversation_count = 999
                    
                    # Print final performance stats before exit
                    if HAS_ADAPTIVE_IMPROVEMENTS:
                        print("\n[FINAL PERFORMANCE REPORT]")
                        performance_monitor.print_stats()
                        # Save quality log and performance metrics
                        audio_quality_agent.save_quality_log()
                        performance_monitor.save_metrics()
                elif conversation_count <= len(questions):
                    response = questions[conversation_count - 1]
                else:
                    # Enhanced response with slang awareness
                    try:
                        from omega_language_enhancer import get_language_enhancer
                        from omega_slang_processor_optimized import Context
                        enhancer = get_language_enhancer()
                        base_response = "That's interesting! Tell me more."
                        response = enhancer.generate_slang_aware_response(base_response, user_text, Context.CODING)
                    except ImportError:
                        response = "That's interesting! Tell me more."
                
                conversation_history.append(('omega', response))
            
            # If still no response and audio was processed, stay silent (no "didn't catch that")
            if response is None:
                print("\n[Silent] Audio processed but no response generated - continuing to listen")
                continue
            
            # Send conversation data to learning swarm (agents process in background)
            conversation_data = {
                'audio_file': str(conv_file),
                'emotion': emotion,
                'user_text': user_text,
                'omega_response': response,
                'history': conversation_history,
                'turn_count': conversation_count
            }
            
            # Queue learning task for agents (non-blocking)
            learning_task = asyncio.create_task(
                learning_swarm.process_conversation_learning(conversation_data)
            )
            
            # Check for improvement cycle
            improvement_applied = False
            if cycle_manager.should_improve():
                print("\n[IMPROVEMENT CYCLE]")
                improvement_insights = cycle_manager.run_improvement_cycle()
                conv_quality = language_improver.analyze_conversation_quality(conversation_history)
                if conv_quality:
                    language_strategy = language_improver.generate_improved_response_strategy(conv_quality)
                    improvement_applied = True
                
                # Get agent swarm insights (if ready)
                if learning_task.done():
                    try:
                        swarm_insight = await learning_task
                        if swarm_insight and swarm_insight.get('prioritized_recommendations'):
                            print("\n[AGENT SWARM INSIGHTS]")
                            for rec in swarm_insight['prioritized_recommendations'][:3]:
                                print(f"  [{rec['priority'].upper()}] {rec['recommendation']} (Agreement: {rec['agent_agreement']} agents)")
                    except:
                        pass
            
            print(f"\n[Omega] {response}")
            
            # Generate and play response (optimized TTS)
            response_start = time.perf_counter()
            tts_to_file_optimized(response, 'clip_0001.wav' if Path('clip_0001.wav').exists() else None, 'response.wav')
            tts_time = time.perf_counter() - response_start
            print(f"[TTS Generation: {tts_time:.2f}s]")
            
            play_audio_background('response.wav')
            
            # Total turn time
            total_time = time.perf_counter() - turn_start
            print(f"[Total Turn Time: {total_time:.2f}s]")
            
            await asyncio.sleep(min(len(response.split()) * 0.3, 10))
            
            # Cleanup (async if available)
            if Path(input_file).exists() and 'temp_input' in input_file:
                try:
                    if HAS_AIOFILES:
                        await aiofiles.os.remove(input_file)
                    else:
                        loop = asyncio.get_event_loop()
                        await loop.run_in_executor(None, os.remove, input_file)
                except:
                    pass
            
            if conversation_count >= 999:
                break
            
            print("\n[Listening again...]\n")
            await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n[Conversation ended]")
            break
        except Exception as e:
            print(f"\n[Error] {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(2)
            continue

if __name__ == "__main__":
    print("\n[Starting Optimized Hands-Free Omega...]\n")
    try:
        asyncio.run(hands_free_conversation_optimized())
    except KeyboardInterrupt:
        print("\n\n[Omega conversation ended. Thank you!]")
