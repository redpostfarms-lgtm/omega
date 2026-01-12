#!/usr/bin/env python3
# Comprehensive Omega Performance Testing and Analysis
import asyncio
import time
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import numpy as np

# Import Omega components
import sys
sys.path.insert(0, str(Path(__file__).parent))

from omega_optimized_speech import recognize_speech_optimized, initialize_whisper, enhance_audio_for_recognition
from omega_optimized_tts import initialize_tts_preload, tts_to_file_optimized
from omega_full_brain import play_audio_background, detect_emotion
from voice_security_system import voice_security

class OmegaPerformanceAnalyzer:
    """Comprehensive performance analysis for Omega."""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'metrics': {},
            'accuracy': {},
            'latency': {},
            'confidence': {},
            'audio_quality': {}
        }
        
    async def test_recognition_accuracy(self, test_audio_dir='conversations'):
        """Test speech recognition accuracy on existing audio files."""
        print("\n" + "=" * 70)
        print("  TESTING RECOGNITION ACCURACY")
        print("=" * 70 + "\n")
        
        audio_dir = Path(test_audio_dir)
        if not audio_dir.exists():
            print(f"[WARNING] Audio directory not found: {audio_dir}")
            return None
        
        # Find recent audio files
        audio_files = sorted(audio_dir.glob('*.wav'), key=lambda p: p.stat().st_mtime, reverse=True)[:10]
        
        if not audio_files:
            print(f"[WARNING] No audio files found in {audio_dir}")
            return None
        
        print(f"[TEST] Found {len(audio_files)} audio files to test\n")
        
        results = {
            'total_files': len(audio_files),
            'recognized': 0,
            'empty': 0,
            'confidences': [],
            'latencies': [],
            'file_results': []
        }
        
        # Initialize Whisper
        print("[TEST] Initializing Whisper model...")
        initialize_whisper()
        
        conversation_context = []  # Test without context first
        
        for i, audio_file in enumerate(audio_files, 1):
            print(f"\n[TEST {i}/{len(audio_files)}] Testing: {audio_file.name}")
            
            # Test recognition
            start_time = time.perf_counter()
            try:
                text = await recognize_speech_optimized(audio_file, conversation_context=conversation_context)
                latency = time.perf_counter() - start_time
                
                results['latencies'].append(latency)
                
                if text and len(text.strip()) > 0:
                    results['recognized'] += 1
                    print(f"  ✅ Recognized: '{text[:80]}...'")
                    print(f"  ⏱️  Latency: {latency:.2f}s")
                    
                    # Try to get confidence from audio properties
                    file_size = audio_file.stat().st_size
                    print(f"  📊 File size: {file_size} bytes")
                    
                    results['file_results'].append({
                        'file': audio_file.name,
                        'recognized': True,
                        'text': text[:100],
                        'latency': latency,
                        'file_size': file_size
                    })
                else:
                    results['empty'] += 1
                    print(f"  ❌ Empty recognition")
                    results['file_results'].append({
                        'file': audio_file.name,
                        'recognized': False,
                        'text': None,
                        'latency': latency,
                        'file_size': audio_file.stat().st_size
                    })
            except Exception as e:
                print(f"  ❌ ERROR: {e}")
                results['file_results'].append({
                    'file': audio_file.name,
                    'recognized': False,
                    'error': str(e)
                })
        
        # Calculate metrics
        recognition_rate = (results['recognized'] / results['total_files']) * 100 if results['total_files'] > 0 else 0
        avg_latency = np.mean(results['latencies']) if results['latencies'] else 0
        
        print(f"\n{'=' * 70}")
        print(f"  RECOGNITION ACCURACY RESULTS")
        print(f"{'=' * 70}")
        print(f"  Total Files Tested: {results['total_files']}")
        print(f"  Successfully Recognized: {results['recognized']}")
        print(f"  Empty Recognitions: {results['empty']}")
        print(f"  Recognition Rate: {recognition_rate:.1f}%")
        print(f"  Average Latency: {avg_latency:.2f}s")
        print(f"  Target: 95%")
        print(f"  Gap to Target: {95 - recognition_rate:.1f}%")
        print(f"{'=' * 70}\n")
        
        results['recognition_rate'] = recognition_rate
        results['avg_latency'] = avg_latency
        results['gap_to_target'] = 95 - recognition_rate
        
        self.results['accuracy'] = results
        return results
    
    def analyze_audio_quality(self, audio_file):
        """Analyze audio quality metrics."""
        try:
            import librosa
            import soundfile as sf
            
            audio, sr = librosa.load(audio_file, sr=None)
            
            # Calculate metrics
            rms = np.sqrt(np.mean(audio ** 2))
            max_amplitude = np.abs(audio).max()
            zcr = np.mean(np.abs(np.diff(np.sign(audio)))) / 2.0
            
            # Estimate SNR (rough)
            signal_power = np.mean(audio ** 2)
            noise_estimate = np.percentile(audio ** 2, 10)  # Bottom 10% as noise
            snr_db = 10 * np.log10(signal_power / (noise_estimate + 1e-10)) if noise_estimate > 0 else 0
            
            metrics = {
                'sample_rate': sr,
                'duration': len(audio) / sr,
                'rms': float(rms),
                'max_amplitude': float(max_amplitude),
                'zcr': float(zcr),
                'snr_db': float(snr_db),
                'is_mono': len(audio.shape) == 1 or audio.shape[0] == 1,
                'is_16khz': sr == 16000
            }
            
            return metrics
        except Exception as e:
            print(f"[AUDIO QUALITY] Error analyzing {audio_file}: {e}")
            return None
    
    async def test_full_pipeline(self):
        """Test the full conversation pipeline."""
        print("\n" + "=" * 70)
        print("  TESTING FULL PIPELINE PERFORMANCE")
        print("=" * 70 + "\n")
        
        # Test components
        components = {
            'whisper_init': None,
            'tts_init': None,
            'recognition': [],
            'tts_generation': [],
            'audio_playback': []
        }
        
        # Initialize models
        print("[PIPELINE TEST] Initializing models...")
        start = time.perf_counter()
        initialize_whisper()
        components['whisper_init'] = time.perf_counter() - start
        
        start = time.perf_counter()
        initialize_tts_preload()
        components['tts_init'] = time.perf_counter() - start
        
        print(f"  Whisper init: {components['whisper_init']:.2f}s")
        print(f"  TTS init: {components['tts_init']:.2f}s")
        
        # Test on sample audio if available
        test_audio = Path('conversations')
        if test_audio.exists():
            audio_files = list(test_audio.glob('*.wav'))[:3]
            for audio_file in audio_files:
                start = time.perf_counter()
                text = await recognize_speech_optimized(audio_file)
                components['recognition'].append(time.perf_counter() - start)
        
        self.results['metrics']['pipeline'] = components
        return components
    
    def calculate_performance_gap(self):
        """Calculate gaps to 95% target."""
        gaps = {}
        
        if 'accuracy' in self.results and 'recognition_rate' in self.results['accuracy']:
            current_rate = self.results['accuracy']['recognition_rate']
            gaps['recognition'] = {
                'current': current_rate,
                'target': 95.0,
                'gap': 95.0 - current_rate,
                'improvement_needed': ((95.0 - current_rate) / max(current_rate, 1)) * 100
            }
        
        return gaps
    
    def generate_report(self):
        """Generate comprehensive performance report."""
        report = {
            'summary': {
                'timestamp': self.results['timestamp'],
                'recognition_rate': self.results['accuracy'].get('recognition_rate', 0),
                'target_rate': 95.0,
                'gap': self.results['accuracy'].get('gap_to_target', 0),
                'avg_latency': self.results['accuracy'].get('avg_latency', 0)
            },
            'detailed_results': self.results,
            'gaps': self.calculate_performance_gap(),
            'recommendations': []
        }
        
        # Add recommendations based on gaps
        if report['summary']['gap'] > 0:
            report['recommendations'].append({
                'priority': 'HIGH',
                'area': 'Recognition Accuracy',
                'gap': report['summary']['gap'],
                'suggestions': [
                    'Upgrade to Whisper Large-v2 or Large-v3',
                    'Implement WebRTC VAD for better speech detection',
                    'Add multi-model ensemble (Whisper + DeepSpeech)',
                    'Enhanced audio preprocessing (spectral subtraction)',
                    'Fine-tune Whisper on domain-specific data'
                ]
            })
        
        return report
    
    def save_report(self, filename='omega_performance_report.json'):
        """Save performance report to file."""
        report = self.generate_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n[REPORT] Saved to: {filename}")
        return report

async def main():
    """Run comprehensive performance analysis."""
    print("=" * 70)
    print("  OMEGA PERFORMANCE ANALYZER")
    print("=" * 70)
    
    analyzer = OmegaPerformanceAnalyzer()
    
    # Test recognition accuracy
    await analyzer.test_recognition_accuracy()
    
    # Test full pipeline
    await analyzer.test_full_pipeline()
    
    # Generate and save report
    report = analyzer.save_report()
    
    # Print summary
    print("\n" + "=" * 70)
    print("  PERFORMANCE SUMMARY")
    print("=" * 70)
    print(f"  Current Recognition Rate: {report['summary']['recognition_rate']:.1f}%")
    print(f"  Target Rate: {report['summary']['target_rate']:.1f}%")
    print(f"  Gap: {report['summary']['gap']:.1f}%")
    print(f"  Average Latency: {report['summary']['avg_latency']:.2f}s")
    print("=" * 70)
    
    if report['recommendations']:
        print("\n  RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"\n  [{rec['priority']}] {rec['area']}: {rec['gap']:.1f}% gap")
            for suggestion in rec['suggestions']:
                print(f"    - {suggestion}")
    
    return report

if __name__ == "__main__":
    asyncio.run(main())
