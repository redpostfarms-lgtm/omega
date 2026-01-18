# TTS Monitoring Integration

## Overview
The TTS (Text-to-Speech) system now has full monitoring integration with the Omega monitoring infrastructure. This enables real-time tracking of performance metrics, error rates, and system health.

## What Was Added

### 1. **omega_full_brain.py** - Main Voice System
Added monitoring to:
- **TTS Generation** (`omega_speak` function)
  - Tracks total TTS generations
  - Records generation duration (in seconds)
  - Logs events with emotion, text length, and duration
  - Tracks TTS errors

- **Speech Recognition** (`recognize_speech_async` function)
  - Tracks total speech recognition requests
  - Records recognition duration
  - Tracks recognition errors (UnknownValue, RequestError, Generic)
  - Logs all events with context

### 2. **omega_optimized_tts.py** - Optimized TTS
Added monitoring to:
- **Optimized TTS Generation** (`tts_to_file_optimized` function)
  - Tracks total TTS generations
  - Records generation duration
  - Logs generation events with text length and output file
  - Tracks errors

### 3. **omega_monitoring.py** - Monitoring Infrastructure
Enhanced with:
- `tts_generation_errors` counter
- `speech_recognition_duration` histogram

## Metrics Tracked

### Counters (Total Counts)
| Metric Name | Description |
|-------------|-------------|
| `tts_generation_total` | Total number of TTS generations |
| `tts_generation_errors` | Total number of TTS errors |
| `speech_recognition_total` | Total number of speech recognition requests |
| `speech_recognition_errors` | Total number of speech recognition errors |

### Histograms (Duration Tracking)
| Metric Name | Description |
|-------------|-------------|
| `tts_generation_duration` | TTS generation time (seconds) |
| `speech_recognition_duration` | Speech recognition time (seconds) |

### Event Logs
Structured logs include:
- `tts_generation` - Successful TTS generations (duration, emotion, text_length)
- `tts_error` - TTS errors (error message)
- `speech_recognition` - Successful recognitions (duration, text_length)
- `speech_recognition_error` - Recognition errors (error type, duration)

## How to Use

### 1. View Real-time Metrics

```python
from omega_monitoring import get_monitor

monitor = get_monitor()
metrics = monitor.get_metrics()

print(f"Total TTS Generations: {metrics['counters']['tts_generation_total']}")
print(f"TTS Errors: {metrics['counters']['tts_generation_errors']}")
print(f"Average TTS Duration: {metrics['histograms']['tts_generation_duration']['mean']:.2f}s")
```

### 2. Save Metrics to File

```python
from omega_monitoring import get_monitor

monitor = get_monitor()
monitor.save_metrics()  # Saves to metrics.json
```

### 3. Start Prometheus Server (Optional)

If you have `prometheus-client` installed:

```python
from omega_monitoring import get_monitor

monitor = get_monitor()
monitor.start_prometheus_server(port=8000)
# Metrics available at http://localhost:8000
```

### 4. Run the Test

```bash
py -3.11 test_tts_monitoring.py
```

This will:
- Initialize TTS model
- Generate a test audio file
- Verify monitoring is working
- Display metrics
- Save results to `metrics.json`

## Example Output

```
=================================================================
  TTS MONITORING INTEGRATION TEST
=================================================================

[1/5] Monitor initialized
[2/5] Initializing TTS model...
      ✓ TTS model ready
[3/5] Baseline TTS generations: 0
[4/5] Generating test audio...
      ✓ Audio generated: test_monitoring.wav
[5/5] Checking metrics...

=================================================================
  RESULTS
=================================================================
  TTS Generations: 0 → 1
  TTS Errors: 0
  Average Duration: 1.234s
  Min Duration: 1.234s
  Max Duration: 1.234s
=================================================================

✓ SUCCESS: TTS monitoring is working!
  Counter incremented: 0 → 1
  Metrics saved to: metrics.json
```

## Monitoring Dashboard

### System Health Monitor Integration

The monitoring integrates with `gatekeeper_system_health_monitor.py`:

```bash
py -3.11 gatekeeper_system_health_monitor.py
```

This provides:
- Overall system health status
- Component health checks
- CPU, Memory, Disk usage
- Network metrics
- Alert system

### Metrics File Format

The `metrics.json` file contains:

```json
{
  "counters": {
    "tts_generation_total": 5,
    "tts_generation_errors": 0,
    "speech_recognition_total": 10,
    "speech_recognition_errors": 2
  },
  "histograms": {
    "tts_generation_duration": {
      "count": 5,
      "min": 0.8,
      "max": 2.1,
      "mean": 1.4,
      "values": [1.2, 1.5, 0.8, 2.1, 1.3]
    }
  },
  "gauges": {},
  "timestamp": "2026-01-17T12:00:00"
}
```

## Benefits

1. **Performance Tracking** - Monitor TTS generation speed over time
2. **Error Detection** - Quickly identify and diagnose issues
3. **Usage Analytics** - Understand system usage patterns
4. **Capacity Planning** - Track resource usage for scaling decisions
5. **Quality Assurance** - Ensure TTS performance meets targets
6. **Debugging** - Structured logs help troubleshoot problems

## Next Steps

### Optional Enhancements

1. **Prometheus Dashboard**
   - Install Grafana
   - Create TTS performance dashboard
   - Set up alerts for high error rates

2. **Enhanced Logging**
   - Install `structlog` for better structured logging
   - Configure log rotation
   - Export logs to external systems

3. **Performance Analysis**
   - Track TTS quality metrics
   - Monitor voice cloning performance
   - Analyze emotion detection accuracy

## Files Modified

- `omega_full_brain.py` - Added monitoring to main voice system
- `omega_optimized_tts.py` - Added monitoring to optimized TTS
- `omega_monitoring.py` - Enhanced monitoring infrastructure

## Files Created

- `test_tts_monitoring.py` - Test script to verify monitoring
- `TTS_MONITORING_INTEGRATION.md` - This documentation

## Troubleshooting

### "omega_monitoring module not found"
- Ensure you're in the correct directory
- Check that `omega_monitoring.py` exists

### Metrics not updating
- Run `test_tts_monitoring.py` to verify
- Check that imports are correct
- Verify monitoring functions are being called

### Prometheus not working
- Install: `py -3.11 -m pip install prometheus-client`
- Check firewall settings for port 8000
- Verify server started without errors

## Status

✅ **COMPLETE** - TTS monitoring is fully integrated and tested

Last Updated: 2026-01-17
