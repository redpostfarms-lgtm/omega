#!/usr/bin/env python3
# Interactive Omega - Conversational interface with recording
import asyncio
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path
from datetime import datetime
import os
import sys

# Import Omega components
sys.path.insert(0, str(Path(__file__).parent))
from omega_full_brain import get_tts, play_audio_background, detect_emotion, recognize_speech_async
from improvement_cycle_manager import ImprovementCycleManager
import speech_recognition as sr

CONVERSATIONS_DIR = Path('conversations')
CONVERSATIONS_DIR.mkdir(exist_ok=True)

def record_user_input(duration=5, sample_rate=16000):
    """Record user speech input."""
    print("\n[Listening... Speak now]")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()
    temp_file = f"temp_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    wavfile.write(temp_file, sample_rate, audio.flatten())
    
    # Save conversation segment
    conv_file = CONVERSATIONS_DIR / f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    wavfile.write(str(conv_file), sample_rate, audio.flatten())
    print(f"[Saved conversation segment: {conv_file.name}]")
    
    return temp_file, conv_file

async def recognize_speech(wav_file):
    """Recognize speech from audio file."""
    try:
        loop = asyncio.get_event_loop()
        recognizer = sr.Recognizer()
        
        def recognize():
            with sr.AudioFile(wav_file) as source:
                audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
        
        text = await loop.run_in_executor(None, recognize)
        return text
    except sr.UnknownValueError:
        return None
    except Exception as e:
        print(f"Recognition error: {e}")
        return None

async def interactive_conversation():
    """Interactive conversation with Omega."""
    print("=" * 60)
    print("  INTERACTIVE OMEGA - CONVERSATION MODE")
    print("=" * 60)
    print("\nOmega is ready to chat!")
    print("I'll record our conversations to improve my voice quality.")
    print("\nI'll listen, understand, and respond to what you say.")
    print("Press Ctrl+C to end the conversation.\n")
    
    # Load TTS
    print("[Loading TTS model...]")
    tts = get_tts()
    print("[Ready!]\n")
    
    # Initialize improvement cycle manager
    cycle_manager = ImprovementCycleManager()
    print(f"[Improvement Cycle] Will improve every {3} conversations")
    print(f"[Current Cycle] {cycle_manager.current_cycle}")
    print()
    
    conversation_count = 0
    conversation_history = []
    questions = [
        "Hello! I'm Omega. I'm learning from your voice to improve my speech. How are you today?",
        "Tell me about yourself. What do you do? I'm analyzing your voice patterns as you speak.",
        "What's something interesting that happened to you recently? I'm learning from every word you say.",
        "Describe your favorite place. I'm studying how you form sounds and express yourself.",
        "Tell me a story or share a memory. The more we talk, the better I understand your voice.",
        "What are your thoughts on technology? I'm processing your speech patterns in real-time.",
    ]
    
    # Start conversation
    response = questions[0] if questions else "Hello! Let's have a conversation so I can learn from your voice."
    print(f"\n[Omega] {response}")
    
    # Generate and play initial greeting
    tts.tts_to_file(
        text=response,
        speaker_wav='clip_0001.wav' if Path('clip_0001.wav').exists() else None,
        language='en',
        file_path='response.wav'
    )
    play_audio_background('response.wav')
    await asyncio.sleep(8)
    
    while True:
        try:
            # Record user input (5 seconds)
            input_file, conv_file = record_user_input(duration=5)
            
            # Detect emotion
            emotion = detect_emotion(input_file)
            print(f"[Detected emotion: {emotion}]")
            
            # Record cycle
            cycle_manager.record_cycle(conv_file)
            conversation_count += 1
            
            # Check if improvement cycle needed
            if cycle_manager.should_improve():
                print("\n[IMPROVEMENT CYCLE TRIGGERED]")
                improvement = cycle_manager.run_improvement_cycle()
                if improvement:
                    response = f"Based on analyzing our last 3 conversations, I've learned about your voice patterns. Your average pitch is {improvement['avg_pitch']:.1f} Hz. {improvement['recommendations'][0] if improvement['recommendations'] else 'Continuing to improve!'}"
                else:
                    response = "I've completed an improvement cycle analysis. Continuing to learn from our conversation."
                
                print(f"\n[Omega] {response}")
                
                # Generate and play improvement announcement
                tts.tts_to_file(
                    text=response,
                    speaker_wav='clip_0001.wav' if Path('clip_0001.wav').exists() else None,
                    language='en',
                    file_path='response.wav'
                )
                play_audio_background('response.wav')
                await asyncio.sleep(8)
            
            # Recognize speech
            print("[Recognizing speech...]")
            user_text = await recognize_speech(input_file)
            
            if user_text:
                print(f"\n[You] {user_text}")
                conversation_history.append(('user', user_text))
                
                # Generate contextual response
                if any(word in user_text.lower() for word in ['quit', 'exit', 'stop', 'bye', 'goodbye']):
                    response = "Thank you for the conversation! I've learned a lot from your voice. Goodbye!"
                    conversation_count = 999  # Trigger exit
                elif any(word in user_text.lower() for word in ['how are you', "how's it going", "how do you feel"]):
                    response = "I'm doing great! I'm learning from your voice patterns right now. Every conversation helps me improve my speech quality."
                elif conversation_count < len(questions):
                    response = questions[conversation_count]
                else:
                    # Contextual responses based on keywords
                    if any(word in user_text.lower() for word in ['yes', 'yeah', 'sure', 'okay', 'ok']):
                        response = "Great! Tell me more. I'm analyzing your voice characteristics as you speak."
                    elif any(word in user_text.lower() for word in ['no', 'not', "don't", "can't"]):
                        response = "I understand. That's okay. What else would you like to talk about?"
                    else:
                        response = "That's interesting! I'm learning from your voice patterns. What else would you like to share?"
                
                conversation_history.append(('omega', response))
            else:
                print("[Could not understand. Please speak again.]")
                response = "I didn't catch that. Could you repeat? I'm listening and learning from your voice."
            
            print(f"\n[Omega] {response}")
            
            # Generate and play response
            print("[Generating response...]")
            tts.tts_to_file(
                text=response,
                speaker_wav='clip_0001.wav' if Path('clip_0001.wav').exists() else None,
                language='en',
                file_path='response.wav'
            )
            
            print("[Playing response in background...]")
            play_audio_background('response.wav')
            
            # Wait for response to play
            await asyncio.sleep(8)
            
            # Clean up temp file (keep conversation recordings)
            if Path(input_file).exists() and 'temp_input' in input_file:
                os.remove(input_file)
            
            if conversation_count >= 999:
                break
                
        except KeyboardInterrupt:
            print("\n\n[Conversation ended]")
            break
        except Exception as e:
            print(f"\n[Error] {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\nTotal conversation segments recorded: {conversation_count}")
    print(f"All recordings saved in: {CONVERSATIONS_DIR}")
    print("\n[Summary]")
    print(f"  Conversations: {len(conversation_history)//2}")
    print(f"  Recordings saved: {len(list(CONVERSATIONS_DIR.glob('*.wav')))}")
    print("\nRun voice_improvement_analyzer.py to analyze the recordings!")

if __name__ == "__main__":
    print("\nStarting Interactive Omega...")
    print("This will help improve voice quality through conversation!\n")
    asyncio.run(interactive_conversation())
