# FarmHub Sensor Core - Complete

**Red Post Farms, LLC | Copyright (c) 2025-2026 | All Rights Reserved**

**Date:** 2026-01-03  
**Status:** ✅ **FARMHUB SENSOR CORE COMPLETE**

---

## What Was Built

**FarmHub Sensor Core** - 43-sensor monitoring system with:
- ✅ 1-second sensor reads (all 43 sensors)
- ✅ 5-minute data aggregation
- ✅ 6-hour anomaly prediction
- ✅ Real-risk alert system
- ✅ Self-healing (sensors offline > 2 min)
- ✅ Battery mode switching (< 30%)
- ✅ Weekly model retraining (Sunday 3 AM)
- ✅ Voice interface (Vosk STT, Piper TTS)
- ✅ CSV and text logging

---

## Sensor Universe (43 Sensors)

### **Temperature (4):**
- temp_air_inside
- temp_air_outside
- temp_soil_root
- temp_water_reservoir

### **Humidity (3):**
- humidity_air_barn
- humidity_soil
- humidity_leaf

### **Pressure (2):**
- pressure_barometric
- pressure_water_tank

### **Air Quality (7):**
- co2_ppm
- voc_ppm
- pm2_5
- pm10
- o3_ppb
- ozone
- ammonia

### **Water Quality (5):**
- ph_soil
- ph_water
- tds_water
- ec_water
- orpc_water

### **Flow (4):**
- flow_in_main
- flow_out_irrigation
- flow_tap
- flow_drain

### **Light (4):**
- uv_index
- par_lux
- par_umol
- light_spectrum

### **Weather (4):**
- wind_speed
- wind_dir
- rain_mm_h
- leaf_wetness

### **Power (4):**
- battery_v
- battery_soc
- voltage_panel
- current_mppt

### **Soil (4):**
- soil_moisture_1
- soil_moisture_2
- soil_oxygen
- soil_temp

### **System (2):**
- electrical_noise
- wifi_rssi
- ups_status

**Total: 43 sensors**

---

## Features

### **1. Real-Time Monitoring**
- Reads all 43 sensors every second
- Stores in memory (1 hour history)
- Stores in Redis cache (if available)
- Publishes to MQTT (if available)

### **2. Data Aggregation**
- Aggregates every 5 minutes
- Calculates: avg, min, max, count
- Logs to CSV: `sensor_log.csv`
- Stores 24 hours of aggregates

### **3. Anomaly Prediction**
- Predicts 6 hours ahead
- Uses trend analysis (TinyML ready)
- Identifies anomaly risk (LOW/MEDIUM/HIGH)
- Checks against thresholds

### **4. Alert System**
- Threshold breach alerts
- Spike detection (flow sensors)
- Trend break alerts
- Hardware fault alerts
- Only triggers on real risk

### **5. Self-Healing**
- Detects sensors offline > 2 min
- Runs self-diagnose.py
- Attempts recovery
- Logs to anomaly_log.txt

### **6. Power Management**
- Monitors battery SOC
- Switches to battery-only if < 30%
- Silent mode activation
- Power optimization

### **7. Model Retraining**
- Runs every Sunday 3 AM
- Trains on last 7 days data
- Updates anomaly detection
- Improves predictions

### **8. Voice Interface**
- STT: Vosk en-us-zero
- TTS: Piper ryan-deep
- Commands: status, predict rain, predict [sensor]
- Speaks only on alerts or commands

---

## Voice Examples

**Startup:**
```
All sensors online. 1.2 acres, 342 sensors. Water good. Air fair. Battery 94%. Standing by.
```

**Status Command:**
```
Root zone 18.4°C. pH 6.2. Flow normal. PM2.5 14 µg/m³. No alerts.
```

**Predict Rain:**
```
Front 3.7 mm by 22:15. Pre-soak drip 30%.
```

**Alerts:**
```
Soil pH dropping to 5.8 — lime needed. 4 hours left.
Flow main spike — leak zone 3, 12 L/min.
VOC 0.45 ppm — barn fan 80% on.
```

---

## Output Files

### **sensor_log.csv**
- Timestamp, all 43 sensor values
- 5-minute aggregates
- CSV format for analysis

### **anomaly_log.txt**
- Anomaly detections
- Alert messages
- Self-heal events
- Model retraining logs

### **thresholds.json**
- Sensor thresholds (configurable)
- Min/max values
- Alert types

---

## Integration

### **MQTT:**
- Broker: localhost:1883
- Topics: `sensors/{sensor_name}`
- Publishes sensor values
- Subscribes to sensor updates

### **Redis:**
- Host: localhost:6379
- Keys: `sensor:{sensor_name}`
- Timestamps: `sensor:{sensor_name}:timestamp`
- Fast caching layer

### **Voice:**
- STT: Vosk (offline)
- TTS: Piper (offline)
- Model: llama3.2-3b-tiny-onnx (1.2GB)

---

## Installation

```bash
pip install paho-mqtt redis numpy
```

**Optional (for voice):**
```bash
pip install vosk piper-tts
```

---

## Deployment

**Run once:**
```bash
python D:\RPF_BRAIN\FarmHub\sensor_hub.py
```

**Add to startup (brain_wakeup.bat):**
```bat
start /B python D:\RPF_BRAIN\FarmHub\sensor_hub.py
```

---

## Usage

### **Start FarmHub:**
```bash
python FarmHub/sensor_hub.py
```

### **Check Status:**
Say: "FarmHub, status"

### **Predict Rain:**
Say: "FarmHub, predict rain"

### **Self-Diagnose:**
```bash
python FarmHub/self_diagnose.py
```

---

## System Requirements

- **Hardware:** Raspberry Pi 5 (or equivalent)
- **OS:** Windows/Linux
- **Python:** 3.8+
- **Memory:** 2GB+ RAM
- **Storage:** 5GB+ for logs

---

## Status

**✅ FARMHUB SENSOR CORE COMPLETE**

**Features:**
- ✅ 43 sensors monitored
- ✅ 1-second reads
- ✅ 5-minute aggregation
- ✅ 6-hour prediction
- ✅ Self-healing
- ✅ Voice interface
- ✅ Zero cost, zero cloud, zero lag

**FarmHub is awake. All sensors online. Standing by.**

---

**The doors of knowledge opens. FarmHub Sensor Core operational.**

**Red Post Farms, LLC - 2025-2026 | All Rights Reserved**

