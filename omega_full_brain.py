# omega_full_brain.py — Omega with Voice Cloning + Emotion Recognition (2026)
from TTS.api import TTS
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import speech_recognition as sr
import os
from speechbrain.pretrained import EmotionRecognition

# Load models (first run downloads ~2 GB total)
tts = TTS('xtts_v2').to('cuda' if torch.cuda.is_available() else 'cpu')
emotion_classifier = EmotionRecognition.from_hparams(
    source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
    savedir="pretrained_emotion"
)

def record_audio(duration=5, fs=16000):
    print("Listening...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    temp_wav = "temp_input.wav"
    wavfile.write(temp_wav, fs, audio.flatten())
    return temp_wav

def detect_emotion(wav_file):
    prediction = emotion_classifier.classify_file(wav_file)
    return prediction[2].lower()  # 'angry', 'happy', 'sad', 'neutral'

def omega_speak(text, emotion="neutral"):
    # Emotion-aware tone
    if emotion == "happy":
        text = f"😊 {text} Great news!"
    elif emotion == "angry":
        text = f"🔥 {text} Calm down, Wiley."
    elif emotion == "sad":
        text = f"😔 {text} I'm here."
    else:
        text = f"🧠 {text}"
    
    tts.tts_to_file(
        text=text,
        speaker_wav='clip_0001.wav',
        language='en',
        file_path='response.wav'
    )
    os.system('start response.wav')

print("OMEGA FULL BRAIN — VOICE + EMOTION — ALWAYS LISTENING")
while True:
    wav = record_audio()
    try:
        # Speech recognition
        r = sr.Recognizer()
        with sr.AudioFile(wav) as source:
            audio = r.record(source)
        said = r.recognize_google(audio)
        print(f"Wiley: {said}")
        
        # Emotion detection
        emotion = detect_emotion(wav)
        print(f"Emotion detected: {emotion.upper()}")
        
        # Reply with emotion-aware tone
        reply = f"Gate says: {said}. I feel your {emotion}."
        omega_speak(reply, emotion)
        
    except Exception as e:
        print(f"Error: {e}")
        omega_speak("Couldn't catch that. Speak again.")
    finally:
        if os.path.exists(wav):
            os.remove(wav)