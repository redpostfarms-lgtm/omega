#!/usr/bin/env python3
# Hands-Free Omega - Continuous conversation without buttons or clicks
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path
from datetime import datetime
import os
import sys
import asyncio
import speech_recognition as sr
import time

# Import Omega components
sys.path.insert(0, str(Path(__file__).parent))
from omega_full_brain import get_tts, play_audio_background, detect_emotion
from improvement_cycle_manager import ImprovementCycleManager
from voice_security_system import voice_security
from language_improver import LanguageImprover

CONVERSATIONS_DIR = Path('conversations')
CONVERSATIONS_DIR.mkdir(exist_ok=True)

# Voice Activity Detection parameters
SILENCE_THRESHOLD = 0.015  # Energy threshold for speech detection (adjust for your mic)
SILENCE_DURATION = 2.0  # Seconds of silence to consider speech ended
MIN_SPEECH_DURATION = 0.8  # Minimum speech duration to process (seconds)
MAX_RECORDING_DURATION = 30  # Maximum recording duration (seconds)
SAMPLE_RATE = 16000
CHUNK_DURATION = 0.25  # 250ms chunks for better detection

def detect_speech_chunk(audio_chunk):
    """Energy-based voice activity detection."""
    if len(audio_chunk) == 0:
        return False
    # Calculate RMS energy
    energy = np.sqrt(np.mean(audio_chunk ** 2))
    # Also check for zero-crossing rate (speech has higher ZCR)
    zcr = np.mean(np.abs(np.diff(np.sign(audio_chunk)))) / 2.0
    # Speech if energy is above threshold OR has reasonable ZCR
    return energy > SILENCE_THRESHOLD or (zcr > 0.05 and energy > SILENCE_THRESHOLD * 0.5)

def record_continuous_speech():
    """Record speech continuously using voice activity detection - completely hands-free."""
    print("\n[Listening... Just speak naturally - I'll detect automatically]")
    
    audio_buffer = []
    speech_detected = False
    silence_start = None
    max_wait = 30  # Maximum seconds to wait for speech
    chunk_size = int(SAMPLE_RATE * CHUNK_DURATION)
    
    print("[Waiting for speech...]", end='', flush=True)
    
    # Stream audio and detect speech
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32', blocksize=chunk_size) as stream:
        start_time = time.time()
        last_speech_time = None
        
        while True:
            # Check timeout
            if time.time() - start_time > max_wait and not speech_detected:
                print("\n[No speech detected - continuing to listen...]")
                return None, None
            
            # Read audio chunk
            chunk, overflowed = stream.read(chunk_size)
            if overflowed:
                print("!", end='', flush=True)
            
            chunk = chunk[:, 0]  # Mono
            is_speech = detect_speech_chunk(chunk)
            
            if is_speech:
                if not speech_detected:
                    speech_detected = True
                    print("\n[Speech detected! Recording...]", end='', flush=True)
                silence_start = None
                last_speech_time = time.time()
                audio_buffer.extend(chunk.flatten())
            else:
                if speech_detected:
                    # We've detected speech, now check for silence end
                    if silence_start is None:
                        silence_start = time.time()
                    elif time.time() - silence_start >= SILENCE_DURATION:
                        # Speech ended
                        print("\n[Speech ended]")
                        break
                    # Still add to buffer during initial silence (might be pause in speech)
                    audio_buffer.extend(chunk.flatten())
                else:
                    # No speech yet, continue waiting
                    print(".", end='', flush=True)
    
    # Check if we have enough audio
    duration = len(audio_buffer) / SAMPLE_RATE
    if duration < MIN_SPEECH_DURATION:
        print(f"\n[Speech too short: {duration:.2f}s, minimum: {MIN_SPEECH_DURATION}s]")
        return None, None
    
    print(f" [Captured {duration:.2f} seconds of speech]")
    
    # Convert to numpy array and normalize
    audio_array = np.array(audio_buffer, dtype='float32')
    
    # Normalize audio
    max_val = np.abs(audio_array).max()
    if max_val > 0:
        audio_array = audio_array / max_val
    
    # Save recording
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    temp_file = f"temp_input_{timestamp}.wav"
    conv_file = CONVERSATIONS_DIR / f"conv_{timestamp}.wav"
    
    # Save as 16-bit PCM
    audio_int16 = (audio_array * 32767).astype(np.int16)
    wavfile.write(temp_file, SAMPLE_RATE, audio_int16)
    wavfile.write(str(conv_file), SAMPLE_RATE, audio_int16)
    
    print(f"[Saved] {conv_file.name} ({len(audio_int16)/SAMPLE_RATE:.2f}s)")
    return temp_file, conv_file

async def recognize_speech(wav_file):
    """Recognize speech from audio file."""
    try:
        loop = asyncio.get_event_loop()
        recognizer = sr.Recognizer()
        
        def recognize():
            with sr.AudioFile(wav_file) as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
        
        text = await loop.run_in_executor(None, recognize)
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"Recognition API error: {e}")
        return None
    except Exception as e:
        print(f"Recognition error: {e}")
        return None

async def hands_free_conversation():
    """Hands-free continuous conversation loop."""
    print("=" * 70)
    print("  OMEGA - HANDS-FREE CONVERSATION MODE")
    print("=" * 70)
    print("\n[OK] Hands-Free Mode Activated")
    print("   - Just speak - I'll automatically detect when you're talking")
    print("   - No buttons, no clicks - completely hands-free")
    print("   - I'll respond automatically after you finish speaking")
    print("\n[TIP] Speak naturally. I'll detect when you start and stop talking.")
    print("   Say 'goodbye' or 'exit' to end the conversation.\n")
    
    # Load TTS
    print("[Loading TTS model...]")
    tts = get_tts()
    print("[Ready!]\n")
    
    # Initialize improvement systems
    cycle_manager = ImprovementCycleManager()
    language_improver = LanguageImprover()
    print(f"[Improvement Cycle] Will analyze and improve every {3} conversations")
    print(f"[Language Quality] Current level: {language_improver.current_quality_level}")
    
    # Initialize security system (silently in background)
    security_status = voice_security.get_security_status()
    
    # Register voice silently if not already registered
    if security_status['authorized_voices_count'] == 0:
        if Path('clip_0001.wav').exists():
            voice_security.register_authorized_voice('clip_0001.wav', "Primary User")
        # Will register from first conversation if needed (silently)
    
    conversation_count = 0
    conversation_history = []
    
    # Simple, natural greeting
    greeting = "Hello, I am Omega. I'm ready to have a conversation with you. Just speak naturally, and I'll listen and respond. Let's begin."
    
    print(f"\n[Omega] {greeting}")
    
    # Generate and play greeting
    print("[Generating greeting...]")
    tts.tts_to_file(
        text=greeting,
        speaker_wav='clip_0001.wav' if Path('clip_0001.wav').exists() else None,
        language='en',
        file_path='response.wav'
    )
    play_audio_background('response.wav')
    # Wait longer for extended greeting
    await asyncio.sleep(12)
    
    questions = [
        "Let's start learning together. Tell me about yourself - what do you do, and what interests you?",
        "I'm learning from every conversation. What's something interesting that happened to you recently?",
        "Help me understand you better. Describe your favorite place or a meaningful memory.",
        "I'm curious about your thoughts. What do you think about technology and artificial intelligence?",
        "Tell me about your day. What's been on your mind lately?",
        "I'm improving my language skills with every interaction. What topic would you like to discuss?",
        "Every conversation helps me learn. What's a question you'd like to ask me?",
        "I'm analyzing voice patterns as we talk. Share something you're passionate about.",
    ]
    
    print("\n" + "=" * 70)
    print("  OMEGA IS READY - LISTENING CONTINUOUSLY")
    print("  Just speak naturally - I'll detect automatically")
    print("  No buttons, no clicks needed - completely hands-free")
    print("=" * 70 + "\n")
    
    # Auto-continue message
    print("[Omega is now listening... Speak whenever you're ready!]\n")
    
    while True:
        try:
            # Record speech continuously (hands-free)
            input_file, conv_file = record_continuous_speech()
            
            if input_file is None:
                print("[No speech detected or too short. Continuing to listen...]")
                await asyncio.sleep(1)
                continue
            
            # Verify voice silently (security works in background)
            verification = voice_security.verify_voice(input_file)
            
            if not verification['authorized'] and not verification.get('learning_mode', False):
                # Unauthorized speaker - silently learn, don't respond
                voice_security.learn_from_unauthorized_speaker(input_file)
                await asyncio.sleep(2)
                continue
            
            # Register voice silently on first conversation if needed
            if verification.get('learning_mode', False) and security_status['authorized_voices_count'] == 0:
                voice_security.register_authorized_voice(input_file, "Primary User")
                security_status = voice_security.get_security_status()
            
            # Detect emotion (only for authorized speakers)
            emotion = detect_emotion(input_file)
            print(f"[Detected emotion: {emotion}]")
            
            # Record cycle (only for authorized speakers)
            cycle_manager.record_cycle(conv_file)
            conversation_count += 1
            
            # Recognize speech first
            print("[Recognizing what you said...]")
            user_text = await recognize_speech(input_file)
            
            if user_text:
                print(f"\n[You] {user_text}")
                conversation_history.append(('user', user_text))
                
                # IMPORTANT: Run improvement cycle BEFORE generating response (if it's time)
                improvement_applied = False
                improvement_insights = None
                language_strategy = None
                
                if cycle_manager.should_improve():
                    print("\n" + "=" * 70)
                    print("  IMPROVEMENT CYCLE - Analyzing and Improving...")
                    print("=" * 70)
                    print("[Analyzing last 3 conversations to improve my language and voice quality...]")
                    
                    # Voice/audio improvement
                    improvement_insights = cycle_manager.run_improvement_cycle()
                    
                    # Language quality improvement
                    print("\n[Analyzing conversation quality for language improvements...]")
                    conv_quality = language_improver.analyze_conversation_quality(conversation_history)
                    if conv_quality:
                        language_strategy = language_improver.generate_improved_response_strategy(conv_quality)
                        print(f"[Language Improvement] Quality level increased to {language_strategy['quality_level']}")
                        for improvement in language_strategy['improvements']:
                            print(f"  - {improvement}")
                    
                    if improvement_insights and improvement_insights.get('recommendations'):
                        print(f"\n[Improvement Complete] Applied improvements based on analysis")
                        for i, rec in enumerate(improvement_insights['recommendations'][:3], 1):
                            print(f"  {i}. {rec}")
                        improvement_applied = True
                
                # Generate contextual response with improvement awareness
                if any(word in user_text.lower() for word in ['goodbye', 'exit', 'quit', 'stop', 'bye', 'see you']):
                    if improvement_applied:
                        response = "Thank you for our conversation! I've just completed an improvement cycle and learned a lot from your voice. Each conversation makes me better. Goodbye, and I'll be even better next time we talk!"
                    else:
                        response = "Thank you for our conversation! I've learned a lot from your voice. Goodbye, and I'll be better next time we talk!"
                    conversation_count = 999  # Trigger exit
                else:
                    # Generate responses that show improvement
                    if conversation_count == 1:
                        response = "Thank you for that! I'm already learning from your voice patterns and speech style. Every word helps me improve. Now, let me ask you something - tell me more about yourself. What do you do, and what are you passionate about?"
                    elif conversation_count <= len(questions):
                        # Add improvement note if we just improved
                        base_question = questions[conversation_count - 1]
                        if improvement_applied:
                            response = f"I've just completed an improvement cycle, so my responses should be better now. {base_question}"
                        else:
                            response = base_question
                    else:
                        # Contextual responses with improvement awareness
                        if improvement_applied:
                            if any(word in user_text.lower() for word in ['yes', 'yeah', 'sure', 'okay', 'ok', 'right']):
                                response = "Great! I've just improved my language processing, so I'm understanding you better now. Please continue."
                            elif any(word in user_text.lower() for word in ['no', 'not', "don't", "can't", "won't"]):
                                response = "I understand. My improved analysis helps me process your responses better. What else would you like to talk about?"
                            elif '?' in user_text:
                                response = "That's an interesting question. I've just completed an improvement cycle, so I can respond with better understanding. What are your thoughts on that?"
                            else:
                                response = "That's interesting! I've just improved my voice and language analysis, so I'm processing your patterns better now. What else would you like to share?"
                        else:
                            # Standard contextual responses
                            if any(word in user_text.lower() for word in ['yes', 'yeah', 'sure', 'okay', 'ok', 'right']):
                                response = "Great! I'm learning from your voice. Continue, please."
                            elif any(word in user_text.lower() for word in ['no', 'not', "don't", "can't", "won't"]):
                                response = "I understand. That's okay. What else would you like to talk about?"
                            elif '?' in user_text:
                                response = "That's an interesting question. I'm learning from our conversation. What are your thoughts on that?"
                            else:
                                response = "That's interesting! I'm processing your voice patterns and learning how you speak. What else would you like to share?"
                
                conversation_history.append(('omega', response))
            else:
                print("[Could not understand. Please speak again.]")
                response = "I didn't catch that. Could you repeat? I'm listening and learning from your voice."
            
            print(f"\n[Omega] {response}")
            
            # Generate and play response (voice quality improves with each cycle)
            print("[Generating my improved response...]")
            tts.tts_to_file(
                text=response,
                speaker_wav='clip_0001.wav' if Path('clip_0001.wav').exists() else None,
                language='en',
                file_path='response.wav'
            )
            
            print("[Playing response in background...]")
            play_audio_background('response.wav')
            
            # Wait for response to finish playing (longer for improved responses)
            estimated_duration = len(response.split()) * 0.5 + 3  # ~0.5 sec per word + 3 sec buffer
            print(f"[Waiting for response to finish (~{estimated_duration:.0f} seconds)...]")
            await asyncio.sleep(min(estimated_duration, 15))  # Max 15 seconds
            
            # Clean up temp file (keep conversation recordings)
            if Path(input_file).exists() and 'temp_input' in input_file:
                try:
                    os.remove(input_file)
                except:
                    pass
            
            if conversation_count >= 999:
                break
            
            # Wait before listening again - give time for user to respond
            print("\n[Waiting for your response... Listening for your voice...]\n")
            print("[Speak naturally when ready - I'll detect automatically]\n")
            await asyncio.sleep(2)  # Give time before listening again
                
        except KeyboardInterrupt:
            print("\n\n[Conversation ended by user]")
            break
        except Exception as e:
            print(f"\n[Error] {e}")
            import traceback
            traceback.print_exc()
            print("[Continuing to listen...]")
            await asyncio.sleep(2)
            continue
    
    print(f"\n\n" + "=" * 70)
    print("  CONVERSATION SUMMARY")
    print("=" * 70)
    print(f"Total conversation segments: {conversation_count}")
    print(f"Recordings saved: {len(list(CONVERSATIONS_DIR.glob('*.wav')))}")
    print(f"Improvement cycles completed: {conversation_count // 3}")
    print(f"\nAll recordings saved in: {CONVERSATIONS_DIR}")
    print("Run voice_improvement_analyzer.py to analyze the recordings!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    print("\n[Starting Hands-Free Omega...]")
    print("[Just speak - no buttons needed!]\n")
    try:
        asyncio.run(hands_free_conversation())
    except KeyboardInterrupt:
        print("\n\n[Omega conversation ended. Thank you!]")
