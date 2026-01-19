#!/usr/bin/env python3
"""
OMEGA Voice Modifier
Adjusts and transforms voice samples with various effects
"""

import os
import sys
import numpy as np
import soundfile as sf

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'
BOLD = '\033[1m'

class OmegaVoiceModifier:
    """Modify and transform Omega voice samples"""
    
    def __init__(self):
        self.voice_files = {
            'warm': 'clip_0001.wav',
            'bright': 'omega_downloaded.wav'
        }
        self.modifications = []
    
    def print_header(self):
        print(f"\n{RED}{BOLD}{'='*70}{RESET}")
        print(f"{RED}{BOLD}{'🔴 OMEGA VOICE MODIFIER 🔴':^70}{RESET}")
        print(f"{RED}{BOLD}{'Advanced Voice Transformation System':^70}{RESET}")
        print(f"{RED}{BOLD}{'='*70}{RESET}\n")
    
    def load_audio(self, file_path):
        """Load audio file"""
        try:
            audio, sr = sf.read(file_path)
            print(f"{GREEN}✓ Loaded: {file_path}{RESET}")
            print(f"  Sample rate: {sr} Hz")
            print(f"  Duration: {len(audio)/sr:.2f}s")
            print(f"  Channels: {1 if audio.ndim == 1 else audio.shape[1]}\n")
            return audio, sr
        except Exception as e:
            print(f"{RED}✗ Failed to load {file_path}: {e}{RESET}\n")
            return None, None
    
    def save_audio(self, audio, sr, output_path):
        """Save audio file"""
        try:
            sf.write(output_path, audio, sr)
            size_kb = os.path.getsize(output_path) / 1024
            print(f"{GREEN}✓ Saved: {output_path} ({size_kb:.1f} KB){RESET}\n")
            return True
        except Exception as e:
            print(f"{RED}✗ Failed to save {output_path}: {e}{RESET}\n")
            return False
    
    def pitch_shift(self, audio, sr, semitones):
        """Shift pitch by semitones (positive = higher, negative = lower)"""
        try:
            import librosa
            shifted = librosa.effects.pitch_shift(audio, sr=sr, n_steps=semitones)
            return shifted
        except:
            # Fallback: simple resampling (less accurate but works)
            factor = 2 ** (semitones / 12.0)
            indices = np.round(np.arange(0, len(audio), factor))
            indices = indices[indices < len(audio)].astype(int)
            return audio[indices]
    
    def speed_change(self, audio, sr, factor):
        """Change speed (factor > 1 = faster, factor < 1 = slower)"""
        try:
            import librosa
            stretched = librosa.effects.time_stretch(audio, rate=factor)
            return stretched
        except:
            # Fallback: simple resampling
            indices = np.round(np.arange(0, len(audio), factor))
            indices = indices[indices < len(audio)].astype(int)
            return audio[indices]
    
    def add_reverb(self, audio, sr, room_size=0.5):
        """Add reverb effect"""
        # Simple reverb using delayed copies
        delay_samples = int(0.05 * sr)  # 50ms delay
        reverb = np.zeros(len(audio) + delay_samples * 3)
        
        reverb[:len(audio)] += audio
        reverb[delay_samples:delay_samples+len(audio)] += audio * 0.4 * room_size
        reverb[delay_samples*2:delay_samples*2+len(audio)] += audio * 0.2 * room_size
        reverb[delay_samples*3:delay_samples*3+len(audio)] += audio * 0.1 * room_size
        
        # Normalize
        reverb = reverb / np.max(np.abs(reverb))
        return reverb[:len(audio)]
    
    def apply_bass_boost(self, audio, sr):
        """Boost bass frequencies"""
        try:
            from scipy import signal
            
            # Low-pass filter at 250 Hz
            nyquist = sr / 2
            cutoff = 250 / nyquist
            b, a = signal.butter(2, cutoff, btype='low')  # type: ignore[assignment]
            
            # Check if audio is long enough
            if len(audio) > 20:
                bass = signal.filtfilt(b, a, audio)
            else:
                bass = signal.lfilter(b, a, audio)
            
            # Mix with original (boost bass)
            return audio * 0.6 + bass * 0.4  # type: ignore[operator, return-value]
        except:
            # Fallback: simple bass boost via FFT
            return audio * 1.1  # Just slightly boost
    
    def apply_treble_boost(self, audio, sr):
        """Boost treble frequencies"""
        try:
            from scipy import signal
            
            # High-pass filter at 2000 Hz
            nyquist = sr / 2
            cutoff = 2000 / nyquist
            b, a = signal.butter(2, cutoff, btype='high')  # type: ignore[assignment]
            
            # Check if audio is long enough
            if len(audio) > 20:
                treble = signal.filtfilt(b, a, audio)
            else:
                treble = signal.lfilter(b, a, audio)
            
            # Mix with original (boost treble)
            return audio * 0.6 + treble * 0.4  # type: ignore[operator, return-value]
        except:
            # Fallback: simple treble boost
            return audio * 1.1
    
    def make_deeper(self, audio, sr):
        """Make voice deeper (lower pitch + bass boost)"""
        print(f"{CYAN}  [1/2] Lowering pitch by 3 semitones...{RESET}")
        shifted = self.pitch_shift(audio, sr, -3)
        
        print(f"{CYAN}  [2/2] Boosting bass frequencies...{RESET}")
        deep = self.apply_bass_boost(shifted, sr)
        
        return deep
    
    def make_brighter(self, audio, sr):
        """Make voice brighter (higher pitch + treble boost)"""
        print(f"{CYAN}  [1/2] Raising pitch by 2 semitones...{RESET}")
        shifted = self.pitch_shift(audio, sr, 2)
        
        print(f"{CYAN}  [2/2] Boosting treble frequencies...{RESET}")
        bright = self.apply_treble_boost(shifted, sr)
        
        return bright
    
    def make_robotic(self, audio, sr):
        """Create robotic voice effect"""
        print(f"{CYAN}  [1/2] Applying frequency modulation...{RESET}")
        
        # Ring modulation
        t = np.arange(len(audio)) / sr
        modulator = np.sin(2 * np.pi * 30 * t)  # 30 Hz modulation
        robotic = audio * (0.7 + 0.3 * modulator)
        
        print(f"{CYAN}  [2/2] Adding subtle distortion...{RESET}")
        # Slight clipping for digital effect
        robotic = np.clip(robotic * 1.2, -1, 1)
        
        return robotic
    
    def make_authoritative(self, audio, sr):
        """Create authoritative commanding voice"""
        print(f"{CYAN}  [1/3] Lowering pitch slightly...{RESET}")
        shifted = self.pitch_shift(audio, sr, -2)
        
        print(f"{CYAN}  [2/3] Adding reverb for presence...{RESET}")
        reverb = self.add_reverb(shifted, sr, room_size=0.3)
        
        print(f"{CYAN}  [3/3] Enhancing low-mids...{RESET}")
        authoritative = self.apply_bass_boost(reverb, sr)
        
        return authoritative
    
    def make_smooth(self, audio, sr):
        """Create smooth, calming voice"""
        try:
            from scipy import signal
            
            print(f"{CYAN}  [1/2] Applying smoothing filter...{RESET}")
            
            # Low-pass filter to remove harsh frequencies
            nyquist = sr / 2
            cutoff = 3000 / nyquist
            b, a = signal.butter(4, cutoff, btype='low')  # type: ignore[assignment, misc]
            
            if len(audio) > 20:
                smooth = signal.filtfilt(b, a, audio)
            else:
                smooth = signal.lfilter(b, a, audio)
            
            print(f"{CYAN}  [2/2] Adding gentle reverb...{RESET}")
            smooth = self.add_reverb(smooth, sr, room_size=0.2)
            
            return smooth
        except:
            # Fallback: just apply reverb
            return self.add_reverb(audio, sr, room_size=0.2)
    
    def create_variations(self):
        """Create multiple voice variations"""
        self.print_header()
        
        print(f"{YELLOW}Creating Omega voice variations...{RESET}\n")
        
        variations = [
            ('deeper', 'Deeper Voice', self.make_deeper),
            ('brighter', 'Brighter Voice', self.make_brighter),
            ('robotic', 'Robotic Effect', self.make_robotic),
            ('authoritative', 'Authoritative Command', self.make_authoritative),
            ('smooth', 'Smooth & Calm', self.make_smooth),
        ]
        
        for voice_key, voice_file in self.voice_files.items():
            if not os.path.exists(voice_file):
                print(f"{RED}✗ Skipping {voice_key}: file not found{RESET}\n")
                continue
            
            print(f"{MAGENTA}{BOLD}{'='*70}{RESET}")
            print(f"{MAGENTA}{BOLD}Processing: {voice_key.upper()} ({voice_file}){RESET}")
            print(f"{MAGENTA}{BOLD}{'='*70}{RESET}\n")
            
            # Load audio
            audio, sr = self.load_audio(voice_file)
            if audio is None:
                continue
            
            # Create variations
            for var_name, var_desc, var_func in variations:
                print(f"{CYAN}[MODIFY] Creating {var_desc}...{RESET}")
                
                try:
                    modified = var_func(audio, sr)
                    
                    # Normalize
                    if np.max(np.abs(modified)) > 0:
                        modified = modified / np.max(np.abs(modified)) * 0.95
                    
                    # Save
                    output_file = f"omega_voice_{voice_key}_{var_name}.wav"
                    if self.save_audio(modified, sr, output_file):
                        self.modifications.append({
                            'source': voice_key,
                            'variation': var_name,
                            'description': var_desc,
                            'file': output_file
                        })
                    
                    print(f"{GREEN}✓ {var_desc} complete{RESET}\n")
                
                except Exception as e:
                    print(f"{RED}✗ Failed: {e}{RESET}\n")
            
            print()
        
        # Summary
        print(f"{GREEN}{BOLD}{'='*70}{RESET}")
        print(f"{GREEN}{BOLD}{'VOICE MODIFICATION COMPLETE':^70}{RESET}")
        print(f"{GREEN}{BOLD}{'='*70}{RESET}\n")
        
        print(f"{CYAN}Created {len(self.modifications)} voice variations:{RESET}\n")
        
        for mod in self.modifications:
            print(f"  {GREEN}✓{RESET} {mod['source'].upper()} - {mod['description']}")
            print(f"    File: {mod['file']}\n")
        
        print(f"{YELLOW}You can now play these modified voices with:{RESET}")
        print(f"  {CYAN}omega_voice_auto.py{RESET} (update to use new files)")
        print(f"  {CYAN}omega_voice_player.py{RESET} (manual selection)\n")


def main():
    try:
        modifier = OmegaVoiceModifier()
        modifier.create_variations()
    except KeyboardInterrupt:
        print(f"\n\n{RED}[INTERRUPTED] Stopped by user{RESET}\n")
    except Exception as e:
        print(f"\n{RED}[ERROR] {e}{RESET}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
