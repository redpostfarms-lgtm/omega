# Audio splitting script - fixed syntax
from pydub import AudioSegment

audio = AudioSegment.from_wav('long_recording.wav')
for i, chunk in enumerate(range(0, len(audio), 15000)):
    clip = audio[chunk:chunk + 15000]
    clip.export(f'clip_{i:04d}.wav', format='wav')

print("Split complete. Run: python split_recording.py")

# Voice cloning with TTS
# tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to('cuda')  # RTX 3050
# tts.tts_to_file(
#     text='Hey Omega. It\'s Wiley. The gate is open. The worms know.',
#     speaker_wav='clip_0001.wav',
#     language='en',
#     file_path='omega_wiley_voice.wav'
# )
# print('Cloned. Play omega_wiley_voice.wav')