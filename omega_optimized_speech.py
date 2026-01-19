import asyncio
import sys
from pathlib import Path
import numpy as np

try:
    from omega_adaptive_improvements import adaptive_threshold, audio_quality_agent, performance_monitor
    HAS_ADAPTIVE_IMPROVEMENTS = True
except ImportError:
    HAS_ADAPTIVE_IMPROVEMENTS = False
    print("[Speech Recognition] Optional adaptive improvements not available")

USE_WHISPER = True
whisper_model = None

def initialize_whisper():
    """Initialize faster-whisper model (one-time, loads model into memory)."""
    global whisper_model, USE_WHISPER
    
    if whisper_model is not None:
        return whisper_model
    
    try:
        from faster_whisper import WhisperModel
        print("[Speech Recognition] Loading Whisper model (base, improved accuracy)...")
        
        try:
            whisper_model = WhisperModel("large-v3", device="cpu", compute_type="int8")
            print("[Speech Recognition] Whisper Large-v3 model ready (offline mode, latest & best accuracy, int8 quantized)")
        except Exception as e:
            print(f"[Speech Recognition] Large-v3 failed: {e}, trying Large-v2...")
            try:
                whisper_model = WhisperModel("large-v2", device="cpu", compute_type="int8")
                print("[Speech Recognition] Whisper Large-v2 model ready (fallback)")
            except Exception as e2:
                print(f"[Speech Recognition] Large-v2 failed: {e2}, falling back to base model")
                whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
                print("[Speech Recognition] Whisper base model ready (final fallback)")
        USE_WHISPER = True
        return whisper_model
    except ImportError:
        print("[Speech Recognition] faster-whisper not installed, using Google API fallback")
        print("[INFO] Install with: pip install faster-whisper")
        USE_WHISPER = False
        return None
    except Exception as e:
        print(f"[Speech Recognition] Whisper initialization error: {e}")
        USE_WHISPER = False
        return None

def enhance_audio_for_recognition(audio_file):
    """Enhance audio quality for better recognition: denoise, normalize, amplify."""
    try:
        import librosa
        import soundfile as sf
        
        # CRITICAL FIX: Load audio and ensure 16kHz mono (Whisper requirement)
        audio, sr_original = librosa.load(audio_file, sr=None, mono=False)
        
        if len(audio.shape) > 1:
            audio = librosa.to_mono(audio)
            print("[Audio Enhancement] Converted stereo to mono")
        
        if sr_original != 16000:
            audio = librosa.resample(audio, orig_sr=sr_original, target_sr=16000)
            print(f"[Audio Enhancement] Resampled from {sr_original}Hz to 16000Hz")
        
        sr = 16000  # Now guaranteed to be 16kHz
        
        try:
            import noisereduce as nr
            audio = nr.reduce_noise(y=audio, sr=sr, stationary=True, prop_decrease=0.8)
            print("[Audio Enhancement] Denoising applied")
        except ImportError:
            print("[Audio Enhancement] noisereduce not available, skipping denoising")
        except Exception as e:
            print(f"[Audio Enhancement] Denoising failed: {e}")
        
        try:
            audio_mean = np.mean(audio)
            audio_std = np.std(audio) + 1e-10  # Prevent division by zero
            
            audio_normalized = (audio - audio_mean) / audio_std
            
            max_normalized = np.abs(audio_normalized).max()
            if max_normalized > 0:
                audio = audio_normalized / max_normalized * 0.95  # Scale to 95% max
            
            print("[Audio Enhancement] CMVN-style normalization applied (zero mean, unit variance)")
        except Exception as e:
            print(f"[Audio Enhancement] CMVN normalization failed: {e}, using standard normalization")
        
        max_val = np.abs(audio).max()
        if max_val > 0:
            audio = audio / max_val * 0.95
            if max_val < 0.3:
                boost_factor = min(0.7 / max_val, 3.0)  # Boost but limit to 3x
                audio = audio * boost_factor
                print(f"[Audio Enhancement] Amplified audio (boost: {boost_factor:.2f}x)")
            audio = np.clip(audio, -1.0, 1.0)  # Prevent clipping
        
        try:
            from scipy import signal
            sos = signal.butter(4, 80, 'hp', fs=sr, output='sos')
            audio = signal.sosfilt(sos, audio)
            print("[Audio Enhancement] High-pass filter applied (80Hz cutoff)")
            
            try:
                harmonic, percussive = librosa.effects.hpss(audio)
                audio = 0.7 * harmonic + 0.3 * audio
                print("[Audio Enhancement] Harmonic/Percussive separation applied")
            except Exception as e:
                print(f"[Audio Enhancement] HPSS failed: {e}")
                
            noise_frame_len = int(0.5 * sr)
            if len(audio) > noise_frame_len:
                noise_estimate = np.abs(np.fft.fft(audio[:noise_frame_len]))
                noise_power = np.mean(noise_estimate ** 2)
                
                audio_fft = np.fft.fft(audio)
                audio_magnitude = np.abs(audio_fft)
                audio_phase = np.angle(audio_fft)
                
                alpha = 2.0  # Over-subtraction factor
                beta = 0.01  # Spectral floor
                enhanced_magnitude = np.maximum(
                    audio_magnitude - alpha * noise_power,
                    beta * audio_magnitude
                )
                
                enhanced_fft = enhanced_magnitude * np.exp(1j * audio_phase)
                audio = np.real(np.fft.ifft(enhanced_fft))
                print("[Audio Enhancement] Spectral subtraction applied")
        except ImportError:
            print("[Audio Enhancement] scipy not available, skipping enhanced preprocessing")
        except Exception as e:
            print(f"[Audio Enhancement] Enhanced preprocessing failed: {e}")
        
        # CRITICAL: Final validation - ensure audio is exactly 16kHz mono before saving
        if len(audio.shape) > 1:
            audio = librosa.to_mono(audio)
            print("[Audio Enhancement] Final validation: Ensured mono channel")
        
        if sr != 16000:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
            sr = 16000
            print(f"[Audio Enhancement] Final validation: Resampled to 16kHz")
        
        enhanced_file = str(audio_file).replace('.wav', '_enhanced.wav')
        sf.write(enhanced_file, audio, sr)
        print(f"[Audio Enhancement] Saved enhanced audio: {enhanced_file} (16kHz mono, validated)")
        return enhanced_file
    except Exception as e:
        print(f"[Audio Enhancement] Warning: {e}, using original audio")
        import traceback
        traceback.print_exc()
        return audio_file

async def recognize_speech_optimized(wav_file, conversation_context=None):
    """Optimized speech recognition with audio enhancement - offline Whisper or Google API fallback.
    
    Args:
        wav_file: Path to audio file
        conversation_context: Optional conversation history (list of (speaker, text) tuples) for context-aware recognition
    """
    global whisper_model
    import time
    
    if HAS_ADAPTIVE_IMPROVEMENTS:
        quality_metrics = audio_quality_agent.analyze_audio(wav_file)
        if quality_metrics and quality_metrics.get('feedback'):
            for feedback_msg in quality_metrics['feedback']:
                print(f"[Audio Quality] {feedback_msg}")
            if quality_metrics.get('recommendations'):
                for rec in quality_metrics['recommendations']:
                    print(f"[Audio Quality Recommendation] {rec}")
    
    recognition_start = time.perf_counter()
    
    # Build initial_prompt from conversation context (CRITICAL IMPROVEMENT: Context-aware recognition)
    initial_prompt = None
    if conversation_context and len(conversation_context) > 0:
        context_words = []
        for speaker, text in conversation_context[-5:]:  # Last 5 turns
            context_words.append(text)
        context_text = ' '.join(context_words)
        words = context_text.split()
        if len(words) > 100:
            context_text = ' '.join(words[-100:])
        initial_prompt = context_text
        print(f"[Context-Aware Recognition] Using {len(words)} words of conversation context")
    
    if USE_WHISPER:
        if whisper_model is None:
            whisper_model = initialize_whisper()
        
        if whisper_model:
            try:
                loop = asyncio.get_event_loop()
                
                recognition_confidence = [None]  # Use list to allow modification in nested function
                
                def enhance_and_transcribe():
                    enhanced_file = enhance_audio_for_recognition(str(wav_file))
                    
                    # CRITICAL: Validate audio file exists and has content
                    import os
                    if not os.path.exists(enhanced_file):
                        print(f"[Whisper ERROR] Enhanced file not found: {enhanced_file}")
                        enhanced_file = str(wav_file)  # Use original
                    
                    file_size = os.path.getsize(enhanced_file) if os.path.exists(enhanced_file) else 0
                    if file_size < 1000:
                        print(f"[Whisper WARNING] Audio file is very small ({file_size} bytes) - may be empty")
                    
                    # CRITICAL: Validate audio format (16kHz mono) before transcription
                    try:
                        import librosa
                        audio_check, sr_check = librosa.load(enhanced_file, sr=None, mono=False, duration=0.1)
                        if len(audio_check.shape) > 1:
                            print(f"[Audio Validation] WARNING: Audio is not mono, converting...")
                            audio_check = librosa.to_mono(audio_check)
                        if sr_check != 16000:
                            print(f"[Audio Validation] WARNING: Sample rate is {sr_check}Hz, should be 16kHz")
                    except Exception as e:
                        print(f"[Audio Validation] Could not validate audio format: {e}")
                    
                    segments, info = whisper_model.transcribe(
                        enhanced_file,
                        beam_size=5,  # Better beam search for accuracy
                        language="en",
                        vad_filter=False,  # DISABLED VAD - may be over-filtering (was True)
                        temperature=0.0,  # Deterministic (best accuracy)
                        best_of=3,  # Try 3 variations, pick best (increased from 2)
                        condition_on_previous_text=True,  # ENABLED: Use previous text context
                        initial_prompt=initial_prompt,  # CRITICAL: Conversation context for better disambiguation
                        word_timestamps=False,  # Faster processing
                    )
                    
                    # Collect all segments with ADAPTIVE CONFIDENCE THRESHOLDING (CRITICAL IMPROVEMENT)
                    if HAS_ADAPTIVE_IMPROVEMENTS:
                        CONFIDENCE_THRESHOLD = adaptive_threshold.get_threshold(enhanced_file)
                        print(f"[Adaptive Threshold] Using dynamic threshold: {CONFIDENCE_THRESHOLD:.3f}")
                    else:
                        CONFIDENCE_THRESHOLD = 0.3  # Base threshold
                    
                    MIN_SEGMENT_CONFIDENCE = 0.2  # Absolute minimum for any segment
                    
                    texts = []
                    rejected_texts = []
                    segment_count = 0
                    total_confidence = 0.0
                    segment_count_with_confidence = 0
                    all_confidences = []  # Track all confidences for return
                    
                    for segment in segments:
                        segment_count += 1
                        text = segment.text.strip()
                        
                        confidence = None
                        if hasattr(segment, 'avg_logprob'):
                            confidence = min(1.0, max(0.0, (segment.avg_logprob + 1.0)))
                        
                        no_speech_prob = None
                        if hasattr(segment, 'no_speech_prob'):
                            no_speech_prob = segment.no_speech_prob
                        
                        if confidence is not None and no_speech_prob is not None:
                            if no_speech_prob > 0.5:
                                confidence = confidence * (1.0 - no_speech_prob)  # Reduce confidence
                        
                        if text and len(text) > 0:
                            if confidence is not None:
                                if confidence >= CONFIDENCE_THRESHOLD:
                                    texts.append(text)
                                    total_confidence += confidence
                                    segment_count_with_confidence += 1
                                    all_confidences.append(confidence)  # Track for return
                                    print(f"[Whisper] ACCEPTED segment (confidence: {confidence:.2f}, no_speech: {no_speech_prob:.2f if no_speech_prob else 'N/A'}): {text[:50]}")
                                elif confidence >= MIN_SEGMENT_CONFIDENCE:
                                    rejected_texts.append((text, confidence))
                                    print(f"[Whisper] REJECTED low-confidence segment (confidence: {confidence:.2f}, no_speech: {no_speech_prob:.2f if no_speech_prob else 'N/A'}): {text[:50]}")
                                else:
                                    print(f"[Whisper] REJECTED very low-confidence segment (confidence: {confidence:.2f}): {text[:50]} [likely hallucination]")
                            else:
                                # No confidence available - accept but log warning
                                texts.append(text)
                                print(f"[Whisper] ACCEPTED segment (no confidence available): {text[:50]}")
                        
                        if segment_count > 50:
                            break
                    
                    full_text = ' '.join(texts).strip()
                    avg_confidence = np.mean(all_confidences) if all_confidences else (total_confidence / segment_count_with_confidence if segment_count_with_confidence > 0 else 0.0)
                    
                    if segment_count_with_confidence > 0:
                        print(f"[Whisper] Average confidence: {avg_confidence:.2f} ({segment_count_with_confidence} accepted segments, {len(rejected_texts)} rejected)")
                    if len(rejected_texts) > 0:
                        print(f"[Whisper] Rejected {len(rejected_texts)} low-confidence segments (reduces hallucinations)")
                    
                    if not full_text or len(full_text) < 2:
                        print("[Whisper] First pass returned empty, trying original file with relaxed settings...")
                        try:
                            segments2, info2 = whisper_model.transcribe(
                                str(wav_file),  # Use original file
                                beam_size=3,  # Smaller beam for speed
                                language="en",
                                vad_filter=False,  # No VAD
                                temperature=0.2,  # Slight randomness (was 0.0)
                                best_of=5,  # More variations
                                condition_on_previous_text=True,  # Use previous text context
                                initial_prompt=initial_prompt,  # Use conversation context
                            )
                            texts2 = []
                            fallback_confidences = []
                            for segment in segments2:
                                text = segment.text.strip()
                                if text and len(text) > 1:  # More than single character
                                    texts2.append(text)
                                    if hasattr(segment, 'avg_logprob'):
                                        conf = min(1.0, max(0.0, (segment.avg_logprob + 1.0)))
                                        fallback_confidences.append(conf)
                                if len(texts2) >= 5:  # Limit segments
                                    break
                            fallback_text = ' '.join(texts2).strip()
                            if fallback_text:
                                print(f"[Whisper Fallback] Got text from original file: {fallback_text[:50]}")
                                fallback_confidence = np.mean(fallback_confidences) if fallback_confidences else 0.6
                                recognition_confidence[0] = fallback_confidence
                                return fallback_text
                        except Exception as e:
                            print(f"[Whisper Fallback] Error: {e}")
                    
                    recognition_confidence[0] = avg_confidence
                    return full_text
                
                text = await loop.run_in_executor(None, enhance_and_transcribe)
                
                recognition_latency = time.perf_counter() - recognition_start
                
                avg_confidence = recognition_confidence[0]
                if avg_confidence is None and text:
                    avg_confidence = min(0.9, 0.5 + (len(text) / 100) * 0.2)
                
                if HAS_ADAPTIVE_IMPROVEMENTS:
                    performance_monitor.record_recognition(
                        success=bool(text and len(text.strip()) > 0),
                        latency=recognition_latency,
                        confidence=avg_confidence if avg_confidence else None
                    )
                
                if text and len(text.strip()) > 0:
                    print(f"[Whisper Base] Recognized: {text}")
                    return text.strip()
                else:
                    print("[Whisper] Recognition returned empty - audio may be too quiet, unclear, or non-speech")
                    print("[Whisper] Audio file exists but transcription is empty - checking audio quality...")
                    
                    if HAS_ADAPTIVE_IMPROVEMENTS:
                        performance_monitor.record_recognition(
                            success=False,
                            latency=time.perf_counter() - recognition_start,
                            confidence=0.0,
                            error="Empty recognition result"
                        )
                    try:
                        segments_orig, _ = whisper_model.transcribe(
                            str(wav_file),
                            beam_size=5,
                            language="en",
                            vad_filter=False,  # No VAD for fallback
                            temperature=0.0,
                            condition_on_previous_text=True,  # Use previous text context
                            initial_prompt=initial_prompt,  # Use conversation context
                        )
                        for segment in segments_orig:
                            if segment.text.strip():
                                print(f"[Whisper Fallback] Got text from original file: {segment.text.strip()}")
                                return segment.text.strip()
                    except:
                        pass
                    return None
            except StopIteration:
                print("[Whisper] No segments returned")
                return None
            except Exception as e:
                print(f"[Whisper ERROR] {e}, falling back to Google API")
                import traceback
                traceback.print_exc()
                USE_WHISPER = False
    
    try:
        import speech_recognition as sr
        
        # CRITICAL FIX: Safe rate limiter import with fallback
        try:
            from rate_limiter import GOOGLE_SPEECH_LIMITER
            RATE_LIMITER_AVAILABLE = True
        except ImportError:
            print("[WARNING] rate_limiter not available, rate limiting disabled for Google API")
            GOOGLE_SPEECH_LIMITER = None
            RATE_LIMITER_AVAILABLE = False
        
        loop = asyncio.get_event_loop()
        recognizer = sr.Recognizer()
        
        # CRITICAL FIX: Null check before using rate limiter
        if RATE_LIMITER_AVAILABLE and GOOGLE_SPEECH_LIMITER:
            GOOGLE_SPEECH_LIMITER.wait_if_needed("google_speech")
            if not GOOGLE_SPEECH_LIMITER.allow("google_speech"):
                wait_time = GOOGLE_SPEECH_LIMITER.wait_time("google_speech")
                await asyncio.sleep(wait_time)
        
        def recognize():
            with sr.AudioFile(wav_file) as source:
                audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
        
        text = await loop.run_in_executor(None, recognize)
        
        # CRITICAL FIX: Null check before recording success/failure
        if RATE_LIMITER_AVAILABLE and GOOGLE_SPEECH_LIMITER:
            GOOGLE_SPEECH_LIMITER.record_success("google_speech")
        
        print(f"[Google API] Recognized: {text[:50]}...")
        return text
    except sr.UnknownValueError:
        # CRITICAL FIX: Null check in exception handler
        if RATE_LIMITER_AVAILABLE and GOOGLE_SPEECH_LIMITER:
            GOOGLE_SPEECH_LIMITER.record_failure("google_speech")
        return None
    except sr.RequestError as e:
        # CRITICAL FIX: Null check in exception handler
        if RATE_LIMITER_AVAILABLE and GOOGLE_SPEECH_LIMITER:
            GOOGLE_SPEECH_LIMITER.record_failure("google_speech")
        print(f"[Speech Recognition] API error: {e}")
        return None
    except Exception as e:
        print(f"[Speech Recognition ERROR] {e}")
        return None

if __name__ == "__main__":
    print("[Speech Recognition Optimized] Initializing...")
    initialize_whisper()
