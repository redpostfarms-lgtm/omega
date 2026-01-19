"""
Omega Confidence Calibration
=============================
Post-hoc calibration framework to reduce overconfidence and hallucinations.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json
from datetime import datetime
from scipy.special import expit, logit

class ConfidenceCalibrator:
    """Post-hoc confidence calibration for Whisper outputs"""
    
    def __init__(self, calibration_file: Optional[Path] = None):
        self.base_dir = Path(__file__).parent.absolute()
        self.calibration_file = calibration_file or (self.base_dir / "calibration_data.json")
        self.bias = 0.0  # Calibration bias
        self.calibrated = False
        
        self.load_calibration()
    
    def calibrate_confidence(self, confidence: float, use_calibration: bool = True) -> float:
        """
        Calibrate confidence score to reduce overconfidence.
        
        Formula: calibrated_confidence = sigmoid(logit(confidence) + bias)
        
        Args:
            confidence: Raw confidence score [0, 1]
            use_calibration: Whether to apply calibration
            
        Returns:
            Calibrated confidence score [0, 1]
        """
        if not use_calibration or not self.calibrated:
            return confidence
        
        confidence = np.clip(confidence, 1e-7, 1.0 - 1e-7)
        
        try:
            logit_conf = logit(confidence)
            calibrated_logit = logit_conf + self.bias
            calibrated_confidence = expit(calibrated_logit)
            return float(np.clip(calibrated_confidence, 0.0, 1.0))
        except Exception as e:
            print(f"[Calibration] Error calibrating confidence: {e}")
            return confidence
    
    def fit_calibration(self, confidences: List[float], true_labels: List[bool], 
                       validation_confidences: Optional[List[float]] = None,
                       validation_labels: Optional[List[bool]] = None):
        """
        Fit calibration bias from validation data.
        
        Formula: bias = mean(logit(calibrated) - logit(confidence))
        
        Args:
            confidences: List of confidence scores
            true_labels: List of true labels (True = correct, False = incorrect)
            validation_confidences: Optional validation confidences
            validation_labels: Optional validation labels
        """
        if validation_confidences is None:
            validation_confidences = confidences
            validation_labels = true_labels
        
        best_bias = 0.0
        best_ece = float('inf')
        
        for bias_candidate in np.arange(-2.0, 2.1, 0.1):
            ece = self._calculate_ece(validation_confidences, validation_labels, bias_candidate)
            if ece < best_ece:
                best_ece = ece
                best_bias = bias_candidate
        
        self.bias = float(best_bias)
        self.calibrated = True
        
        self.save_calibration()
        
        print(f"[Calibration] Calibration fitted: bias = {self.bias:.3f}, ECE = {best_ece:.3f}")
    
    def _calculate_ece(self, confidences: List[float], labels: List[bool], 
                      bias: float, n_bins: int = 10) -> float:
        """Calculate Expected Calibration Error (ECE)"""
        if len(confidences) == 0:
            return float('inf')
        
        calibrated_confidences = [self.calibrate_confidence(c, use_calibration=False) 
                                  for c in confidences]
        calibrated_confidences = [np.clip(c, 1e-7, 1.0 - 1e-7) for c in calibrated_confidences]
        
        calibrated_confidences = [expit(logit(c) + bias) for c in calibrated_confidences]
        
        bins = np.linspace(0, 1, n_bins + 1)
        ece = 0.0
        
        for i in range(n_bins):
            bin_mask = [(calibrated_confidences[j] >= bins[i]) and 
                       (calibrated_confidences[j] < bins[i + 1]) 
                       for j in range(len(calibrated_confidences))]
            bin_confidences = [calibrated_confidences[j] for j in range(len(calibrated_confidences)) 
                             if bin_mask[j]]
            bin_labels = [labels[j] for j in range(len(labels)) if bin_mask[j]]
            
            if len(bin_confidences) > 0:
                bin_accuracy = sum(bin_labels) / len(bin_labels)
                bin_confidence = np.mean(bin_confidences)
                bin_weight = len(bin_confidences) / len(calibrated_confidences)
                ece += bin_weight * abs(bin_accuracy - bin_confidence)
        
        return ece
    
    def save_calibration(self):
        """Save calibration parameters"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "bias": self.bias,
            "calibrated": self.calibrated
        }
        
        try:
            with open(self.calibration_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Calibration] Error saving calibration: {e}")
    
    def load_calibration(self):
        """Load calibration parameters"""
        if not self.calibration_file.exists():
            return
        
        try:
            with open(self.calibration_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.bias = data.get("bias", 0.0)
                self.calibrated = data.get("calibrated", False)
        except Exception as e:
            print(f"[Calibration] Error loading calibration: {e}")

_calibrator = None

def get_calibrator() -> ConfidenceCalibrator:
    """Get global calibrator instance"""
    global _calibrator
    if _calibrator is None:
        _calibrator = ConfidenceCalibrator()
    return _calibrator

def calibrate_confidence(confidence: float, use_calibration: bool = True) -> float:
    """Calibrate confidence score"""
    return get_calibrator().calibrate_confidence(confidence, use_calibration)

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" " * 20 + "OMEGA CONFIDENCE CALIBRATION")
    print("=" * 80)
    print()
    
    calibrator = ConfidenceCalibrator()
    print("[OK] Confidence calibration framework initialized")
    print(f"  - Bias: {calibrator.bias:.3f}")
    print(f"  - Calibrated: {calibrator.calibrated}")
    print()
    print("Usage:")
    print("  from omega_confidence_calibration import calibrate_confidence")
    print("  calibrated = calibrate_confidence(raw_confidence)")
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
