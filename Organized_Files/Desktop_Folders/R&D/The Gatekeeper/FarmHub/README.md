# FarmHub Sensor Core

**Red Post Farms, LLC | Copyright (c) 2025-2026 | All Rights Reserved**

## Overview

FarmHub Sensor Core reads 43 sensors every second, aggregates every 5 minutes, predicts anomalies 6 hours out, and triggers alerts only on real risk.

**Zero cost. Zero cloud. Zero lag. All local.**

---

## Installation

```bash
pip install paho-mqtt redis numpy
```

---

## Deployment

**Run once, done:**
```bash
python D:\RPF_BRAIN\FarmHub\sensor_hub.py
```

**Add to startup (brain_wakeup.bat):**
```bat
python D:\RPF_BRAIN\FarmHub\sensor_hub.py
```

---

## Sensors (43 Total)

- Temperature: air (inside/outside), soil root, water reservoir
- Humidity: air barn, soil, leaf
- Pressure: barometric, water tank
- Air Quality: CO2, VOC, PM2.5, PM10, O3, ozone, ammonia
- Water Quality: pH, TDS, EC, ORPC
- Flow: main in, irrigation out, tap, drain
- Light: UV index, PAR (lux/umol), spectrum
- Weather: wind speed/direction, rain, leaf wetness
- Power: battery voltage/SOC, panel voltage, MPPT current
- Soil: moisture (2 sensors), oxygen, temperature
- System: electrical noise, WiFi RSSI, UPS status

---

## Features

- ✅ Reads all 43 sensors every second
- ✅ Aggregates data every 5 minutes
- ✅ Predicts anomalies 6 hours ahead
- ✅ Triggers alerts only on real risk
- ✅ Self-heals if sensors offline > 2 min
- ✅ Switches to battery-only if < 30%
- ✅ Retrains model weekly (Sunday 3 AM)
- ✅ Voice interface (Vosk STT, Piper TTS)
- ✅ Logs to CSV and text files

---

## Voice Commands

- "FarmHub, status" → Get current sensor status
- "FarmHub, predict rain" → Get rain prediction
- "FarmHub, predict [sensor]" → Get prediction for sensor

---

## Output Files

- `sensor_log.csv` - All sensor data (5-min aggregates)
- `anomaly_log.txt` - Anomalies and alerts
- `thresholds.json` - Sensor thresholds (configurable)

---

## Integration

- MQTT broker: localhost:1883
- Redis cache: localhost:6379
- Model: llama3.2-3b-tiny-onnx (1.2GB)
- TTS: Piper ryan-deep
- STT: Vosk en-us-zero

---

**The doors of knowledge opens. FarmHub is awake.**

**Red Post Farms, LLC - 2025-2026 | All Rights Reserved**

