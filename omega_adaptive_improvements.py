import numpy as np
import json
from pathlib import Path
from datetime import datetime
from collections import deque
import librosa

class AdaptiveConfidenceThreshold:
    """Adaptive confidence thresholding based on audio quality and conditions."""
    
    def __init__(self):
        self.base_threshold = 0.3
        self.min_threshold = 0.2
        self.max_threshold = 0.5
        self.quality_history = deque(maxlen=10)  # Track last 10 recordings
        
    def calculate_audio_quality(self, audio_file):
        """Calculate audio quality metrics for adaptive thresholding."""
        try:
            audio, sr = librosa.load(audio_file, sr=None, duration=2.0)  # Sample first 2 seconds
            
            rms = np.sqrt(np.mean(audio ** 2))
            max_amplitude = np.abs(audio).max()
            zcr = np.mean(np.abs(np.diff(np.sign(audio)))) / 2.0
            
            signal_power = np.mean(audio ** 2)
            noise_estimate = np.percentile(audio ** 2, 10)  # Bottom 10% as noise
            snr_db = 10 * np.log10(signal_power / (noise_estimate + 1e-10)) if noise_estimate > 0 else 20
            
            metrics = {
                'rms': float(rms),
                'max_amplitude': float(max_amplitude),
                'snr_db': float(snr_db),
                'zcr': float(zcr)
            }
            
            self.quality_history.append(metrics)
            return metrics
        except Exception as e:
            print(f"[Adaptive Threshold] Error calculating quality: {e}")
            return {'rms': 0.3, 'max_amplitude': 0.5, 'snr_db': 20, 'zcr': 0.1}
    
    def get_threshold(self, audio_file=None):
        """Get adaptive confidence threshold based on audio quality."""
        if audio_file:
            metrics = self.calculate_audio_quality(audio_file)
        elif len(self.quality_history) > 0:
            metrics = {
                'snr_db': np.mean([q['snr_db'] for q in self.quality_history]),
                'rms': np.mean([q['rms'] for q in self.quality_history])
            }
        else:
            return self.base_threshold
        
        snr_db = metrics.get('snr_db', 20)
        rms = metrics.get('rms', 0.3)
        
        
        if snr_db > 30 and rms > 0.15:
            threshold = self.base_threshold * 0.75
            reason = f"High SNR ({snr_db:.1f}dB) and good RMS ({rms:.2f})"
        elif snr_db > 25 and rms > 0.12:
            threshold = self.base_threshold * 0.9
            reason = f"Good SNR ({snr_db:.1f}dB)"
        elif snr_db < 15 or rms < 0.1:
            threshold = self.base_threshold * 1.4
            reason = f"Low SNR ({snr_db:.1f}dB) or quiet audio (RMS: {rms:.2f})"
        elif snr_db < 20:
            threshold = self.base_threshold * 1.2
            reason = f"Moderate noise (SNR: {snr_db:.1f}dB)"
        else:
            threshold = self.base_threshold
            reason = f"Normal conditions (SNR: {snr_db:.1f}dB)"
        
        threshold = max(self.min_threshold, min(self.max_threshold, threshold))
        
        if audio_file:  # Only log if we're checking a file
            print(f"[Adaptive Threshold] Using {threshold:.3f} (base: {self.base_threshold:.3f}) - {reason}")
        
        return threshold

class AudioQualityAgent:
    """Monitor audio quality and provide feedback."""
    
    def __init__(self):
        self.quality_log = []
        self.warnings = []
    
    def analyze_audio(self, audio_file):
        """Analyze audio quality and return feedback."""
        try:
            audio, sr = librosa.load(audio_file, sr=None, duration=2.0)
            
            rms = np.sqrt(np.mean(audio ** 2))
            max_amplitude = np.abs(audio).max()
            zcr = np.mean(np.abs(np.diff(np.sign(audio)))) / 2.0
            
            signal_power = np.mean(audio ** 2)
            noise_estimate = np.percentile(audio ** 2, 10)
            snr_db = 10 * np.log10(signal_power / (noise_estimate + 1e-10)) if noise_estimate > 0 else 20
            
            clipping_ratio = np.sum(np.abs(audio) > 0.95) / len(audio)
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'file': str(audio_file),
                'rms': float(rms),
                'max_amplitude': float(max_amplitude),
                'snr_db': float(snr_db),
                'zcr': float(zcr),
                'clipping_ratio': float(clipping_ratio),
                'sample_rate': int(sr),
                'duration': len(audio) / sr
            }
            
            feedback = []
            quality_score = 100.0
            
            if snr_db < 15:
                feedback.append(f"⚠️  Low SNR ({snr_db:.1f}dB): High background noise detected")
                quality_score -= 30
            elif snr_db < 20:
                feedback.append(f"⚠️  Moderate SNR ({snr_db:.1f}dB): Some background noise")
                quality_score -= 15
            
            if rms < 0.1:
                feedback.append(f"⚠️  Audio too quiet (RMS: {rms:.3f}): Increase microphone gain or speak closer")
                quality_score -= 25
            elif rms < 0.15:
                feedback.append(f"⚠️  Audio slightly quiet (RMS: {rms:.3f})")
                quality_score -= 10
            
            if clipping_ratio > 0.01:
                feedback.append(f"⚠️  Audio clipping detected ({clipping_ratio*100:.1f}%): Reduce microphone gain")
                quality_score -= 20
            
            if max_amplitude < 0.3:
                feedback.append(f"⚠️  Low amplitude: Audio may be too quiet for recognition")
                quality_score -= 15
            
            if not feedback:
                feedback.append(f"✅ Audio quality: Good (SNR: {snr_db:.1f}dB, RMS: {rms:.3f})")
            
            metrics['quality_score'] = quality_score
            metrics['feedback'] = feedback
            metrics['recommendations'] = self._generate_recommendations(metrics)
            
            self.quality_log.append(metrics)
            
            if len(self.quality_log) > 100:
                self.quality_log.pop(0)
            
            return metrics
            
        except Exception as e:
            print(f"[Audio Quality Agent] Error analyzing {audio_file}: {e}")
            return None
    
    def _generate_recommendations(self, metrics):
        """Generate recommendations based on metrics."""
        recommendations = []
        
        if metrics['snr_db'] < 15:
            recommendations.append("Move to a quieter location or use a directional microphone")
        
        if metrics['rms'] < 0.1:
            recommendations.append("Speak closer to the microphone or increase microphone gain")
        
        if metrics['clipping_ratio'] > 0.01:
            recommendations.append("Reduce microphone gain to prevent clipping")
        
        if metrics['max_amplitude'] < 0.3 and metrics['snr_db'] > 25:
            recommendations.append("Audio is clear but quiet - good quality, just increase volume")
        
        return recommendations
    
    def get_quality_trends(self, num_samples=20):
        """Get quality trends over recent recordings."""
        if len(self.quality_log) < 2:
            return None
        
        recent = self.quality_log[-num_samples:]
        
        trends = {
            'avg_snr': np.mean([q['snr_db'] for q in recent]),
            'avg_rms': np.mean([q['rms'] for q in recent]),
            'avg_quality_score': np.mean([q['quality_score'] for q in recent]),
            'snr_trend': 'improving' if len(recent) > 1 and recent[-1]['snr_db'] > recent[0]['snr_db'] else 'degrading',
            'total_samples': len(recent)
        }
        
        return trends
    
    def save_quality_log(self, filename='audio_quality_log.json'):
        """Save quality log to file."""
        log_file = Path(filename)
        with open(log_file, 'w') as f:
            json.dump(self.quality_log, f, indent=2)
        print(f"[Audio Quality Agent] Quality log saved to {log_file}")
        return log_file

class PerformanceMonitor:
    """Monitor and log performance metrics."""
    
    def __init__(self):
        self.metrics = []
        self.current_session = {
            'start_time': datetime.now().isoformat(),
            'recognition_count': 0,
            'success_count': 0,
            'latencies': [],
            'confidences': [],
            'errors': []
        }
    
    def record_recognition(self, success, latency, confidence=None, error=None):
        """Record a recognition attempt."""
        self.current_session['recognition_count'] += 1
        
        if success:
            self.current_session['success_count'] += 1
        
        if latency:
            self.current_session['latencies'].append(latency)
        
        if confidence is not None:
            self.current_session['confidences'].append(confidence)
        
        if error:
            self.current_session['errors'].append(str(error))
        
        metric = {
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'latency': latency,
            'confidence': confidence,
            'error': error
        }
        self.metrics.append(metric)
    
    def get_session_stats(self):
        """Get current session statistics."""
        stats = {
            'total_attempts': self.current_session['recognition_count'],
            'success_rate': (self.current_session['success_count'] / max(1, self.current_session['recognition_count'])) * 100,
            'avg_latency': np.mean(self.current_session['latencies']) if self.current_session['latencies'] else 0,
            'avg_confidence': np.mean(self.current_session['confidences']) if self.current_session['confidences'] else 0,
            'error_count': len(self.current_session['errors'])
        }
        return stats
    
    def print_stats(self):
        """Print current session statistics."""
        stats = self.get_session_stats()
        print("\n" + "=" * 70)
        print("  PERFORMANCE MONITOR - SESSION STATISTICS")
        print("=" * 70)
        print(f"  Total Recognition Attempts: {stats['total_attempts']}")
        print(f"  Success Rate: {stats['success_rate']:.1f}%")
        print(f"  Average Latency: {stats['avg_latency']:.2f}s")
        print(f"  Average Confidence: {stats['avg_confidence']:.3f}")
        print(f"  Errors: {stats['error_count']}")
        print("=" * 70 + "\n")
    
    def save_metrics(self, filename='performance_metrics.json'):
        """Save performance metrics to file."""
        metrics_file = Path(filename)
        with open(metrics_file, 'w') as f:
            json.dump({
                'session': self.current_session,
                'all_metrics': self.metrics[-100:]  # Last 100 metrics
            }, f, indent=2)
        print(f"[Performance Monitor] Metrics saved to {metrics_file}")
        return metrics_file

adaptive_threshold = AdaptiveConfidenceThreshold()
audio_quality_agent = AudioQualityAgent()
performance_monitor = PerformanceMonitor()

if __name__ == "__main__":
    print("[Optional Improvements] Adaptive systems initialized")
    print("  - Adaptive Confidence Threshold")
    print("  - Audio Quality Agent")
    print("  - Performance Monitor")
