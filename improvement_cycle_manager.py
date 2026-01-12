#!/usr/bin/env python3
# Improvement Cycle Manager - Tests and improves every 3 conversation cycles
import json
from pathlib import Path
from datetime import datetime
import librosa
import numpy as np

CYCLES_FILE = Path('improvement_cycles.json')
CONVERSATIONS_DIR = Path('conversations')
IMPROVEMENT_INTERVAL = 3  # Improve every 3 cycles

class ImprovementCycleManager:
    def __init__(self):
        self.cycles = self.load_cycles()
        self.current_cycle = len(self.cycles)
    
    def load_cycles(self):
        """Load cycle history."""
        if CYCLES_FILE.exists():
            with open(CYCLES_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def save_cycles(self):
        """Save cycle history."""
        with open(CYCLES_FILE, 'w') as f:
            json.dump(self.cycles, f, indent=2)
    
    def record_cycle(self, conversation_segment, analysis=None):
        """Record a conversation cycle."""
        cycle = {
            'cycle_number': self.current_cycle + 1,
            'timestamp': datetime.now().isoformat(),
            'segment_file': str(conversation_segment) if conversation_segment else None,
            'analysis': analysis,
        }
        self.cycles.append(cycle)
        self.current_cycle += 1
        self.save_cycles()
        return cycle
    
    def should_improve(self):
        """Check if it's time for an improvement cycle."""
        return self.current_cycle > 0 and self.current_cycle % IMPROVEMENT_INTERVAL == 0
    
    def analyze_recent_cycles(self, num_cycles=3):
        """Analyze the most recent cycles for improvement."""
        if len(self.cycles) < num_cycles:
            return None
        
        recent = self.cycles[-num_cycles:]
        analyses = []
        
        for cycle in recent:
            if cycle.get('segment_file') and Path(cycle['segment_file']).exists():
                try:
                    audio, sr = librosa.load(cycle['segment_file'], sr=16000)
                    
                    # Extract features
                    pitches, _ = librosa.piptrack(y=audio, sr=sr)
                    pitch_values = pitches[pitches > 0]
                    avg_pitch = np.mean(pitch_values) if len(pitch_values) > 0 else 0
                    
                    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
                    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
                    avg_mfccs = np.mean(mfccs, axis=1)
                    
                    analyses.append({
                        'cycle': cycle['cycle_number'],
                        'pitch': float(avg_pitch),
                        'spectral_centroid': float(spectral_centroid),
                        'mfccs': avg_mfccs.tolist(),
                    })
                except Exception as e:
                    print(f"Analysis error for cycle {cycle['cycle_number']}: {e}")
        
        if analyses:
            # Calculate improvements
            avg_pitch = np.mean([a['pitch'] for a in analyses])
            avg_centroid = np.mean([a['spectral_centroid'] for a in analyses])
            avg_mfccs = np.mean([np.array(a['mfccs']) for a in analyses], axis=0)
            
            return {
                'cycles_analyzed': num_cycles,
                'avg_pitch': float(avg_pitch),
                'avg_spectral_centroid': float(avg_centroid),
                'avg_mfccs': avg_mfccs.tolist(),
                'recommendations': self.generate_recommendations(avg_pitch, avg_centroid, avg_mfccs)
            }
        
        return None
    
    def generate_recommendations(self, pitch, centroid, mfccs):
        """Generate improvement recommendations based on analysis."""
        recommendations = []
        
        # Compare with reference (clip_0001.wav)
        if Path('clip_0001.wav').exists():
            try:
                ref_audio, sr = librosa.load('clip_0001.wav', sr=16000)
                ref_pitches, _ = librosa.piptrack(y=ref_audio, sr=sr)
                ref_pitch_values = ref_pitches[ref_pitches > 0]
                ref_pitch = np.mean(ref_pitch_values) if len(ref_pitch_values) > 0 else 0
                
                pitch_diff = abs(pitch - ref_pitch)
                if pitch_diff > 50:
                    recommendations.append(f"Pitch adjustment needed: Current {pitch:.1f}Hz vs Reference {ref_pitch:.1f}Hz (diff: {pitch_diff:.1f}Hz)")
                else:
                    recommendations.append(f"Pitch matching well: {pitch:.1f}Hz (ref: {ref_pitch:.1f}Hz)")
            except:
                pass
        
        # Voice quality recommendations
        if centroid < 2000:
            recommendations.append("Voice sounds deeper/darker - consider brighter tone")
        elif centroid > 4000:
            recommendations.append("Voice sounds bright/sharp - consider warmer tone")
        
        recommendations.append(f"Spectral centroid: {centroid:.1f} (optimal: 2500-3500)")
        recommendations.append(f"Voice characteristics captured: {len(mfccs)} MFCC features analyzed")
        
        return recommendations
    
    def run_improvement_cycle(self):
        """Run an improvement cycle: analyze and generate test."""
        print("\n" + "=" * 60)
        print("  IMPROVEMENT CYCLE (Every 3 conversations)")
        print("=" * 60)
        
        analysis = self.analyze_recent_cycles(IMPROVEMENT_INTERVAL)
        if analysis:
            print(f"\n[Analysis] Last {analysis['cycles_analyzed']} cycles:")
            print(f"  Average Pitch: {analysis['avg_pitch']:.2f} Hz")
            print(f"  Average Spectral Centroid: {analysis['avg_spectral_centroid']:.2f}")
            print(f"\n[Recommendations]:")
            for rec in analysis['recommendations']:
                print(f"  • {rec}")
            
            return analysis
        
        return None

if __name__ == "__main__":
    manager = ImprovementCycleManager()
    print(f"Current cycle: {manager.current_cycle}")
    print(f"Next improvement at cycle: {((manager.current_cycle // IMPROVEMENT_INTERVAL) + 1) * IMPROVEMENT_INTERVAL}")
    
    if manager.should_improve():
        manager.run_improvement_cycle()
