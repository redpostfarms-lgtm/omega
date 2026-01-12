#!/usr/bin/env python3
"""
Whisper Calibration and Confidence Thresholding
================================================
Implements confidence calibration and thresholding to reduce hallucinations
and overconfidence in noisy conditions.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime

class WhisperCalibration:
    """Whisper confidence calibration and thresholding system"""
    
    def __init__(self):
        self.confidence_threshold = 0.5  # Minimum confidence to accept
        self.no_speech_threshold = 0.6  # Maximum no_speech_prob to accept
        self.avg_logprob_threshold = -0.5  # Minimum avg_logprob to accept
        self.calibration_enabled = True
        
    def should_accept_transcription(self, result: Dict[str, Any]) -> Tuple[bool, str]:
        """Determine if transcription should be accepted based on confidence"""
        if not self.calibration_enabled:
            return True, "Calibration disabled"
        
        # Extract confidence metrics
        avg_logprob = result.get('avg_logprob', -1.0)
        no_speech_prob = result.get('no_speech_prob', 1.0)
        segments = result.get('segments', [])
        
        # Check overall confidence
        if avg_logprob < self.avg_logprob_threshold:
            return False, f"Low average log probability: {avg_logprob:.3f} < {self.avg_logprob_threshold}"
        
        if no_speech_prob > self.no_speech_threshold:
            return False, f"High no-speech probability: {no_speech_prob:.3f} > {self.no_speech_threshold}"
        
        # Check segment-level confidence
        if segments:
            low_confidence_segments = []
            for i, segment in enumerate(segments):
                seg_avg_logprob = segment.get('avg_logprob', -1.0)
                seg_no_speech_prob = segment.get('no_speech_prob', 1.0)
                
                if seg_avg_logprob < self.avg_logprob_threshold:
                    low_confidence_segments.append(i)
                if seg_no_speech_prob > self.no_speech_threshold:
                    low_confidence_segments.append(i)
            
            if low_confidence_segments:
                # Filter out low-confidence segments
                filtered_segments = [seg for i, seg in enumerate(segments) if i not in low_confidence_segments]
                if not filtered_segments:
                    return False, "All segments filtered due to low confidence"
                result['segments'] = filtered_segments
                # Reconstruct text from filtered segments
                result['text'] = ' '.join(seg.get('text', '') for seg in filtered_segments)
        
        return True, "Confidence check passed"
    
    def calibrate_thresholds(self, results: List[Dict[str, Any]], ground_truth: Optional[List[str]] = None):
        """Calibrate confidence thresholds based on results"""
        if not results:
            return
        
        # Calculate optimal thresholds based on results
        avg_logprobs = [r.get('avg_logprob', -1.0) for r in results]
        no_speech_probs = [r.get('no_speech_prob', 1.0) for r in results]
        
        if avg_logprobs:
            # Set threshold at 25th percentile
            avg_logprobs.sort()
            self.avg_logprob_threshold = avg_logprobs[len(avg_logprobs) // 4]
        
        if no_speech_probs:
            # Set threshold at 75th percentile
            no_speech_probs.sort()
            self.no_speech_threshold = no_speech_probs[len(no_speech_probs) * 3 // 4]
    
    def get_calibration_config(self) -> Dict[str, Any]:
        """Get calibration configuration"""
        return {
            "confidence_threshold": self.confidence_threshold,
            "no_speech_threshold": self.no_speech_threshold,
            "avg_logprob_threshold": self.avg_logprob_threshold,
            "calibration_enabled": self.calibration_enabled
        }
    
    def save_config(self, config_file: Path):
        """Save calibration configuration"""
        config = self.get_calibration_config()
        config['timestamp'] = datetime.now().isoformat()
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

def apply_whisper_calibration_patch(speech_file: Path) -> str:
    """Generate patch code for Whisper calibration integration"""
    
    patch_code = '''
# Add this import at the top of the file
from WHISPER_CALIBRATION_AND_CONFIDENCE import WhisperCalibration

# Add calibration instance (in __init__ or at module level)
calibration = WhisperCalibration()

# Modify transcription function to use calibration
# After Whisper transcribe call, add:
if hasattr(result, 'avg_logprob'):
    # Convert result to dict if needed
    result_dict = {
        'text': result.text,
        'avg_logprob': result.avg_logprob if hasattr(result, 'avg_logprob') else -1.0,
        'no_speech_prob': result.no_speech_prob if hasattr(result, 'no_speech_prob') else 1.0,
        'segments': [
            {
                'text': seg.text,
                'avg_logprob': seg.avg_logprob if hasattr(seg, 'avg_logprob') else -1.0,
                'no_speech_prob': seg.no_speech_prob if hasattr(seg, 'no_speech_prob') else 1.0
            }
            for seg in (result.segments if hasattr(result, 'segments') else [])
        ]
    }
    
    # Apply calibration
    accepted, reason = calibration.should_accept_transcription(result_dict)
    if not accepted:
        # Reject transcription - return empty or retry
        return None  # or raise exception, or retry with different settings
    else:
        # Use filtered result
        result = type('Result', (), result_dict)()  # Reconstruct result object
'''
    
    return patch_code

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" " * 20 + "WHISPER CALIBRATION AND CONFIDENCE SYSTEM")
    print("=" * 80)
    print()
    print("Calibration System Created:")
    print("  - Confidence thresholding")
    print("  - No-speech probability filtering")
    print("  - Average log probability checking")
    print("  - Segment-level filtering")
    print()
    print("Integration:")
    print("  - Import WhisperCalibration class")
    print("  - Apply to transcription results")
    print("  - Filter low-confidence segments")
    print()
    print("Status: Calibration system ready for integration")
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
