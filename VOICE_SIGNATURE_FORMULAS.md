# Voice Signature Formulas

**Date:** January 10, 2026  
**Location:** `voice_security_system.py`

---

## Overview

Voice signature comparison uses a weighted similarity formula to match voices. This document details all formulas used in the voice security system.

---

## 1. Voice Signature Extraction

### 1.1 Pitch/Fundamental Frequency (F0)

**Method:** `librosa.piptrack()` (autocorrelation-based)  
**Weight:** 40% (increased from 30%)

**Features Extracted:**
- Mean pitch
- Standard deviation

**Formula:**
```text
pitch_values = librosa.piptrack(y=audio, sr=sr, threshold=0.1)
pitch_mean = mean(pitch_values[pitch_values > 0])
pitch_std = std(pitch_values[pitch_values > 0])
```text

---

### 1.2 MFCCs (Mel-Frequency Cepstral Coefficients)

**Method:** `librosa.feature.mfcc()` (8 coefficients)  
**Weight:** 50% (most important, primary feature)

**Features Extracted:**
- Mean of 8 MFCC coefficients across time

**Formula:**
```text
mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=8)
mfccs_mean = mean(mfccs, axis=1)  # Mean across time
```text

---

### 1.3 Spectral Centroid

**Method:** `librosa.feature.spectral_centroid()`  
**Weight:** 10% (reduced from 15%)

**Features Extracted:**
- Mean spectral centroid

**Formula:**
```text
spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
centroid_mean = mean(spectral_centroids)
```text

---

## 2. Voice Signature Comparison

### 2.1 Overall Similarity Formula

**Location:** `voice_security_system.py::compare_voice_signatures()`

**Formula:**
```text
overall_sim = (pitch_sim * 0.4) + (mfcc_sim * 0.5) + (centroid_sim * 0.1)
```text

**Weights:**
- Pitch similarity: 40%
- MFCC similarity: 50% (most important)
- Spectral centroid similarity: 10%

---

### 2.2 Pitch Similarity

**Formula:**
```text
pitch_sim = 1.0 - min(abs(pitch1['mean'] - pitch2['mean']) / 200.0, 1.0)
```text

**Where:**
- `pitch1['mean']` = mean pitch of first voice (Hz)
- `pitch2['mean']` = mean pitch of second voice (Hz)
- `200.0` = normalization factor (typical pitch range)

**Range:** [0, 1] where 1.0 = identical pitch, 0.0 = very different pitch

---

### 2.3 MFCC Similarity

**Formula:**
```text
mfcc_diff = ||mfcc1 - mfcc2||  # Euclidean distance
mfcc_sim = 1.0 / (1.0 + mfcc_diff / 10.0)
```text

**Where:**
- `mfcc1` = MFCC mean vector of first voice (8 coefficients)
- `mfcc2` = MFCC mean vector of second voice (8 coefficients)
- `||.||` = Euclidean norm (L2 norm)
- `10.0` = scaling factor

**Range:** [0, 1] where 1.0 = identical MFCCs, 0.0 = very different MFCCs

**Alternative Form (using cosine similarity):**
```text
mfcc_sim = dot(mfcc1, mfcc2) / (||mfcc1|| * ||mfcc2||)
```text

**Current Implementation:** Euclidean distance-based (as shown above)

---

### 2.4 Spectral Centroid Similarity

**Formula:**
```text
centroid_sim = 1.0 - min(abs(centroid1 - centroid2) / 2000.0, 1.0)
```text

**Where:**
- `centroid1` = spectral centroid mean of first voice (Hz)
- `centroid2` = spectral centroid mean of second voice (Hz)
- `2000.0` = normalization factor (typical spectral centroid range)

**Range:** [0, 1] where 1.0 = identical centroid, 0.0 = very different centroid

---

## 3. Voice Verification Threshold

**Location:** `voice_security_system.py::verify_voice()`

**Formula:**
```text
authorized = overall_sim >= threshold
```text

**Default Threshold:** 0.85 (85% similarity required)

**Range:** [0.0, 1.0]

---

## 4. Complete Comparison Algorithm

**Pseudocode:**
```text
function compare_voice_signatures(sig1, sig2):
    similarities = []
    
    // 1. Pitch similarity (40% weight)
    pitch_sim = 1.0 - min(abs(sig1.pitch.mean - sig2.pitch.mean) / 200.0, 1.0)
    similarities.append(pitch_sim * 0.4)
    
    // 2. MFCC similarity (50% weight)
    mfcc_diff = ||sig1.mfccs_mean - sig2.mfccs_mean||
    mfcc_sim = 1.0 / (1.0 + mfcc_diff / 10.0)
    similarities.append(mfcc_sim * 0.5)
    
    // 3. Spectral centroid similarity (10% weight)
    centroid_sim = 1.0 - min(abs(sig1.spectral.centroid_mean - sig2.spectral.centroid_mean) / 2000.0, 1.0)
    similarities.append(centroid_sim * 0.1)
    
    // Overall similarity (weighted sum)
    overall_sim = sum(similarities)
    
    // Clamp to [0, 1]
    return min(max(overall_sim, 0.0), 1.0)
end function
```text

---

## 5. Optimization Notes

### Reduced Features (Optimized Version)

**Original Features (removed):**
- Chroma features (15% weight) - Removed for performance
- Spectral rolloff - Removed (redundant with centroid)
- Spectral bandwidth - Removed (redundant with centroid)
- Zero-crossing rate - Removed (not used in comparison)
- Harmonic ratio - Removed (not used in comparison)
- Tempo - Removed (not used in comparison)
- Spectral envelope - Removed (redundant with centroid)

**Current Features (optimized):**
- Pitch (mean) - 40% weight
- MFCCs (8 coefficients, mean) - 50% weight
- Spectral centroid (mean) - 10% weight

**Result:** Faster comparison while maintaining accuracy

---

## 6. Mathematical Formulation

### Complete Formula (Combined)

Given two voice signatures `sig1` and `sig2`:

```text
similarity(sig1, sig2) = 
    0.4 * pitch_sim(sig1, sig2) +
    0.5 * mfcc_sim(sig1, sig2) +
    0.1 * centroid_sim(sig1, sig2)
```text

Where:

```text
pitch_sim(sig1, sig2) = 1.0 - min(|sig1.pitch_mean - sig2.pitch_mean| / 200.0, 1.0)

mfcc_sim(sig1, sig2) = 1.0 / (1.0 + ||sig1.mfccs_mean - sig2.mfccs_mean|| / 10.0)

centroid_sim(sig1, sig2) = 1.0 - min(|sig1.centroid_mean - sig2.centroid_mean| / 2000.0, 1.0)
```text

---

## Status: ✅ DOCUMENTED

**All voice signature formulas documented.**
