# Drone Construction and Design - Complete Technical Guide

**Red Post Farms, LLC | Copyright (c) 2025-2026 | All Rights Reserved**

**Date:** 2026-01-XX  
**Status:** ✅ **COMPREHENSIVE TECHNICAL GUIDE**

---

## Executive Summary

Complete technical guide for drone construction and design with real specifications, no placeholders. Covers all components, design principles, calculations, and assembly procedures.

---

## Table of Contents

1. [Frame Design and Materials](#frame-design)
2. [Motor Specifications and Selection](#motors)
3. [ESC (Electronic Speed Controller) Specifications](#escs)
4. [Flight Controller Specifications](#flight-controller)
5. [Battery Specifications and Selection](#batteries)
6. [Propeller Specifications](#propellers)
7. [GPS and Navigation Modules](#gps)
8. [Power Distribution Board (PDB)](#pdb)
9. [Radio Control System](#radio)
10. [Assembly Procedures](#assembly)
11. [Testing and Calibration](#testing)
12. [Design Calculations](#calculations)

---

## 1. Frame Design and Materials {#frame-design}

### Frame Types

#### **Quadcopter Frame (X Configuration)**
- **Motor Spacing**: 450mm, 550mm, 650mm (diagonal motor-to-motor)
- **Arm Length**: 225mm, 275mm, 325mm (for 450mm, 550mm, 650mm frames)
- **Arm Angle**: 45° from center (X configuration)
- **Center Plate**: 50mm x 50mm to 100mm x 100mm
- **Arm Width**: 15mm to 25mm
- **Arm Thickness**: 3mm to 5mm

#### **Hexacopter Frame (6 Motors)**
- **Motor Spacing**: 550mm to 800mm
- **Arm Configuration**: 60° spacing (6 arms)
- **Center Plate**: 80mm x 80mm to 120mm x 120mm

#### **Octocopter Frame (8 Motors)**
- **Motor Spacing**: 650mm to 1000mm
- **Arm Configuration**: 45° spacing (8 arms)
- **Center Plate**: 100mm x 100mm to 150mm x 150mm

### Materials

#### **Carbon Fiber (CF)**
- **Grade**: T300, T700, T800
- **Thickness**: 1.5mm, 2mm, 3mm, 4mm, 5mm
- **Weave**: 2x2 twill, plain weave, unidirectional
- **Density**: 1.6 g/cm³
- **Tensile Strength**: 3,500-5,000 MPa
- **Modulus**: 230-300 GPa
- **Advantages**: Lightweight, high strength, vibration damping
- **Cost**: $50-$200 per frame kit

#### **Aluminum 6061-T6**
- **Thickness**: 2mm, 3mm, 4mm
- **Density**: 2.7 g/cm³
- **Tensile Strength**: 310 MPa
- **Modulus**: 69 GPa
- **Advantages**: Lower cost, easier machining
- **Disadvantages**: Heavier, less vibration damping

#### **Glass Fiber (GF)**
- **Thickness**: 2mm, 3mm
- **Density**: 1.8 g/cm³
- **Tensile Strength**: 1,000-1,500 MPa
- **Advantages**: Lower cost than carbon fiber
- **Disadvantages**: Heavier, less rigid

### Frame Design Specifications

#### **450mm Quadcopter Frame**
- **Total Weight**: 200-400g (frame only)
- **Motor Mount**: 16mm x 19mm (standard)
- **Propeller Clearance**: 10-15mm minimum
- **Payload Capacity**: 500g-1000g
- **Max Takeoff Weight**: 1.5kg-2.5kg

#### **550mm Quadcopter Frame**
- **Total Weight**: 400-600g (frame only)
- **Motor Mount**: 16mm x 19mm or 25mm x 25mm
- **Propeller Clearance**: 15-20mm minimum
- **Payload Capacity**: 1kg-2kg
- **Max Takeoff Weight**: 3kg-5kg

#### **650mm Quadcopter Frame**
- **Total Weight**: 600-1000g (frame only)
- **Motor Mount**: 25mm x 25mm or 30mm x 30mm
- **Propeller Clearance**: 20-25mm minimum
- **Payload Capacity**: 2kg-5kg
- **Max Takeoff Weight**: 6kg-10kg

---

## 2. Motor Specifications and Selection {#motors}

### Brushless DC Motor (BLDC) Specifications

#### **2212 Motor (22mm stator, 12mm height)**
- **KV Rating**: 920KV, 1000KV, 1400KV, 2300KV
- **Max Current**: 18A-25A
- **Max Power**: 200W-300W
- **Weight**: 55g-65g
- **Shaft Diameter**: 5mm
- **Mounting Pattern**: 16mm x 19mm
- **Thrust (10x4.5 prop, 3S)**: 600g-800g per motor
- **Thrust (10x4.5 prop, 4S)**: 800g-1000g per motor
- **Efficiency**: 75%-85%
- **Price**: $15-$30 per motor

#### **2312 Motor (23mm stator, 12mm height)**
- **KV Rating**: 800KV, 960KV, 1400KV
- **Max Current**: 20A-30A
- **Max Power**: 250W-350W
- **Weight**: 60g-75g
- **Shaft Diameter**: 5mm
- **Mounting Pattern**: 16mm x 19mm
- **Thrust (11x4.7 prop, 3S)**: 800g-1000g per motor
- **Thrust (11x4.7 prop, 4S)**: 1000g-1300g per motor
- **Efficiency**: 75%-85%

#### **2814 Motor (28mm stator, 14mm height)**
- **KV Rating**: 700KV, 800KV, 1000KV
- **Max Current**: 30A-40A
- **Max Power**: 400W-600W
- **Weight**: 90g-110g
- **Shaft Diameter**: 5mm or 6mm
- **Mounting Pattern**: 19mm x 19mm or 25mm x 25mm
- **Thrust (12x4.5 prop, 3S)**: 1200g-1500g per motor
- **Thrust (12x4.5 prop, 4S)**: 1500g-2000g per motor
- **Efficiency**: 80%-88%

#### **3508 Motor (35mm stator, 8mm height)**
- **KV Rating**: 380KV, 480KV, 580KV, 700KV
- **Max Current**: 40A-60A
- **Max Power**: 600W-1000W
- **Weight**: 120g-150g
- **Shaft Diameter**: 6mm
- **Mounting Pattern**: 25mm x 25mm or 30mm x 30mm
- **Thrust (15x5.5 prop, 4S)**: 2000g-3000g per motor
- **Thrust (15x5.5 prop, 6S)**: 3000g-4000g per motor
- **Efficiency**: 82%-90%

### Motor Selection Guide

**For 450mm Frame:**
- **Recommended**: 2212 1400KV or 2300KV
- **Propeller**: 10x4.5 or 10x4.7
- **Battery**: 3S (11.1V) or 4S (14.8V)
- **Total Thrust**: 2400g-4000g (4 motors)

**For 550mm Frame:**
- **Recommended**: 2312 960KV or 2814 800KV
- **Propeller**: 11x4.7 or 12x4.5
- **Battery**: 3S or 4S
- **Total Thrust**: 4000g-6000g (4 motors)

**For 650mm Frame:**
- **Recommended**: 2814 700KV or 3508 580KV
- **Propeller**: 13x4.5 or 15x5.5
- **Battery**: 4S or 6S (22.2V)
- **Total Thrust**: 6000g-12000g (4 motors)

### KV Rating Selection

- **Low KV (300-800)**: Large propellers, high torque, lower RPM, better efficiency
- **Medium KV (800-1500)**: Medium propellers, balanced performance
- **High KV (1500-3000)**: Small propellers, high RPM, faster response

---

## 3. ESC (Electronic Speed Controller) Specifications {#escs}

### ESC Specifications

#### **20A ESC**
- **Continuous Current**: 20A
- **Burst Current**: 25A (10 seconds)
- **Voltage Range**: 2S-4S (7.4V-16.8V)
- **BEC Output**: 5V/2A (optional)
- **Weight**: 8g-12g
- **Size**: 25mm x 15mm x 5mm
- **Firmware**: SimonK, BLHeli, BLHeli_S
- **Price**: $8-$15 per ESC
- **Use Case**: 2212 motors, 450mm frames

#### **30A ESC**
- **Continuous Current**: 30A
- **Burst Current**: 40A (10 seconds)
- **Voltage Range**: 2S-4S or 2S-6S
- **BEC Output**: 5V/3A (optional)
- **Weight**: 12g-18g
- **Size**: 30mm x 18mm x 6mm
- **Firmware**: BLHeli_S, BLHeli_32
- **Price**: $12-$20 per ESC
- **Use Case**: 2312, 2814 motors, 550mm frames

#### **40A ESC**
- **Continuous Current**: 40A
- **Burst Current**: 55A (10 seconds)
- **Voltage Range**: 2S-6S
- **BEC Output**: 5V/5A (optional)
- **Weight**: 18g-25g
- **Size**: 35mm x 20mm x 7mm
- **Firmware**: BLHeli_32, KISS
- **Price**: $18-$30 per ESC
- **Use Case**: 2814, 3508 motors, 650mm frames

#### **50A ESC**
- **Continuous Current**: 50A
- **Burst Current**: 70A (10 seconds)
- **Voltage Range**: 2S-6S
- **BEC Output**: 5V/5A (optional)
- **Weight**: 25g-35g
- **Size**: 40mm x 25mm x 8mm
- **Firmware**: BLHeli_32, KISS
- **Price**: $25-$40 per ESC
- **Use Case**: Large motors, heavy lift frames

### ESC Firmware

#### **SimonK**
- **Update Rate**: 400Hz-500Hz
- **Features**: Basic, reliable
- **Compatibility**: Older ESCs

#### **BLHeli_S**
- **Update Rate**: 500Hz-1000Hz
- **Features**: Damped light, active braking, telemetry
- **Compatibility**: Most modern ESCs

#### **BLHeli_32**
- **Update Rate**: 1000Hz-24000Hz
- **Features**: Advanced filtering, telemetry, RPM filtering
- **Compatibility**: 32-bit ESCs

### ESC Selection Guide

**For 2212 Motors:**
- **Recommended**: 20A or 30A ESC
- **Firmware**: BLHeli_S or BLHeli_32

**For 2312/2814 Motors:**
- **Recommended**: 30A or 40A ESC
- **Firmware**: BLHeli_32

**For 3508 Motors:**
- **Recommended**: 40A or 50A ESC
- **Firmware**: BLHeli_32

---

## 4. Flight Controller Specifications {#flight-controller}

### Pixhawk 4 Flight Controller

#### **Hardware Specifications**
- **Processor**: STM32F765 (32-bit ARM Cortex-M7, 216MHz)
- **RAM**: 512KB
- **Flash**: 2MB
- **IMU**: BMI088 (6-axis: 3-axis gyro + 3-axis accelerometer)
- **IMU 2**: ICM20948 (9-axis: 3-axis gyro + 3-axis accelerometer + 3-axis magnetometer)
- **Barometer**: MS5611
- **GPS**: u-blox M8N or M9N (compatible)
- **Compass**: Built-in magnetometer
- **Voltage Range**: 4.8V-5.5V (via BEC)
- **Current Consumption**: 200mA-500mA
- **Size**: 81.5mm x 50.5mm x 15.5mm
- **Weight**: 15.8g
- **Price**: $150-$250

#### **Sensor Specifications**
- **Gyroscope Range**: ±2000°/s
- **Gyroscope Resolution**: 16-bit
- **Accelerometer Range**: ±16g
- **Accelerometer Resolution**: 16-bit
- **Barometer Range**: 10-1200 mbar
- **Barometer Resolution**: 0.012 mbar
- **Update Rate**: 8kHz (gyro/accel), 100Hz (barometer)

#### **Connectivity**
- **PWM Outputs**: 8 channels (up to 16 with expansion)
- **UART Ports**: 5 (GPS, Telemetry, etc.)
- **I2C Ports**: 2
- **SPI Ports**: 1
- **CAN Bus**: 1
- **USB**: 1 (Micro USB)
- **SD Card**: 1 (for data logging)

### Betaflight Flight Controller (F4/F7)

#### **F4 Flight Controller**
- **Processor**: STM32F405 (168MHz)
- **IMU**: MPU6000 or BMI160
- **Barometer**: BMP280 (optional)
- **Voltage Range**: 5V
- **Size**: 36mm x 36mm (standard)
- **Price**: $30-$80

#### **F7 Flight Controller**
- **Processor**: STM32F7 (216MHz)
- **IMU**: MPU6000, BMI160, or ICM20602
- **Barometer**: BMP280 (optional)
- **Voltage Range**: 5V
- **Size**: 36mm x 36mm (standard)
- **Price**: $50-$120

### ArduPilot-Compatible Flight Controllers

#### **Pixhawk 2.1 (Cube)**
- **Processor**: STM32F427 (180MHz)
- **IMU**: MPU9250
- **Barometer**: MS5611
- **Price**: $200-$300

#### **Pixhawk 6C**
- **Processor**: STM32H7 (480MHz)
- **IMU**: BMI088 + ICM42688-P
- **Barometer**: MS5611
- **Price**: $300-$400

---

## 5. Battery Specifications and Selection {#batteries}

### LiPo Battery Specifications

#### **3S Battery (11.1V Nominal)**
- **Voltage Range**: 9.0V (discharged) to 12.6V (fully charged)
- **Cell Configuration**: 3 cells in series
- **Common Capacities**: 1500mAh, 2200mAh, 3000mAh, 5000mAh
- **C Rating**: 20C, 25C, 30C, 40C, 50C
- **Discharge Rate**: Capacity × C Rating (e.g., 2200mAh × 30C = 66A)
- **Weight**: 120g (1500mAh) to 400g (5000mAh)
- **Dimensions**: Varies by capacity
- **Price**: $15-$50

#### **4S Battery (14.8V Nominal)**
- **Voltage Range**: 12.0V to 16.8V
- **Cell Configuration**: 4 cells in series
- **Common Capacities**: 1500mAh, 2200mAh, 3000mAh, 5000mAh, 6000mAh
- **C Rating**: 20C, 25C, 30C, 40C, 50C, 75C
- **Discharge Rate**: Capacity × C Rating
- **Weight**: 160g (1500mAh) to 550g (6000mAh)
- **Price**: $20-$70

#### **6S Battery (22.2V Nominal)**
- **Voltage Range**: 18.0V to 25.2V
- **Cell Configuration**: 6 cells in series
- **Common Capacities**: 3000mAh, 5000mAh, 6000mAh, 10000mAh
- **C Rating**: 20C, 25C, 30C, 40C
- **Discharge Rate**: Capacity × C Rating
- **Weight**: 450g (3000mAh) to 1500g (10000mAh)
- **Price**: $40-$150

### Battery Selection Guide

**For 450mm Quadcopter:**
- **Recommended**: 3S 2200mAh 30C or 4S 1500mAh 40C
- **Flight Time**: 8-12 minutes (hover)
- **Weight**: 180g-200g

**For 550mm Quadcopter:**
- **Recommended**: 3S 3000mAh 30C or 4S 2200mAh 40C
- **Flight Time**: 10-15 minutes (hover)
- **Weight**: 250g-350g

**For 650mm Quadcopter:**
- **Recommended**: 4S 5000mAh 30C or 6S 5000mAh 25C
- **Flight Time**: 15-20 minutes (hover)
- **Weight**: 500g-700g

### C Rating Explained

- **C Rating**: Maximum safe discharge rate
- **Example**: 2200mAh 30C battery can discharge at 66A (2200mAh × 30 = 66,000mA = 66A)
- **Continuous C**: Sustained discharge rate
- **Burst C**: Short-term discharge rate (10-30 seconds)

---

## 6. Propeller Specifications {#propellers}

### Propeller Nomenclature

**Format**: Diameter × Pitch (e.g., 10×4.5)
- **Diameter**: 10 inches (propeller length)
- **Pitch**: 4.5 inches (theoretical forward travel per rotation)

### Common Propeller Sizes

#### **10×4.5 Propeller**
- **Diameter**: 10 inches (254mm)
- **Pitch**: 4.5 inches (114mm)
- **Material**: Plastic (nylon), carbon fiber, wood
- **Weight**: 5g-8g (plastic), 3g-5g (carbon fiber)
- **Use Case**: 2212 motors, 450mm frames
- **Thrust**: 600g-1000g per motor (depending on motor/KV)
- **Price**: $2-$5 per propeller

#### **11×4.7 Propeller**
- **Diameter**: 11 inches (279mm)
- **Pitch**: 4.7 inches (119mm)
- **Weight**: 6g-10g (plastic), 4g-6g (carbon fiber)
- **Use Case**: 2312 motors, 550mm frames
- **Thrust**: 800g-1300g per motor
- **Price**: $3-$6 per propeller

#### **12×4.5 Propeller**
- **Diameter**: 12 inches (305mm)
- **Pitch**: 4.5 inches (114mm)
- **Weight**: 8g-12g (plastic), 5g-8g (carbon fiber)
- **Use Case**: 2814 motors, 550mm-650mm frames
- **Thrust**: 1200g-2000g per motor
- **Price**: $4-$8 per propeller

#### **13×4.5 Propeller**
- **Diameter**: 13 inches (330mm)
- **Pitch**: 4.5 inches (114mm)
- **Weight**: 10g-15g (plastic), 6g-10g (carbon fiber)
- **Use Case**: 2814 motors, 650mm frames
- **Thrust**: 1500g-2500g per motor
- **Price**: $5-$10 per propeller

#### **15×5.5 Propeller**
- **Diameter**: 15 inches (381mm)
- **Pitch**: 5.5 inches (140mm)
- **Weight**: 15g-25g (plastic), 10g-15g (carbon fiber)
- **Use Case**: 3508 motors, 650mm+ frames
- **Thrust**: 2000g-4000g per motor
- **Price**: $8-$15 per propeller

### Propeller Materials

#### **Plastic (Nylon)**
- **Advantages**: Low cost, durable, good for learning
- **Disadvantages**: Heavier, less efficient
- **Price**: $2-$5 per propeller

#### **Carbon Fiber**
- **Advantages**: Lightweight, rigid, efficient
- **Disadvantages**: Higher cost, more fragile
- **Price**: $10-$30 per propeller

#### **Wood**
- **Advantages**: Lightweight, efficient, quiet
- **Disadvantages**: More fragile, higher cost
- **Price**: $15-$40 per propeller

### Propeller Selection

**For 2212 1400KV Motor:**
- **3S Battery**: 10×4.5 or 10×4.7
- **4S Battery**: 9×4.5 or 10×4.5

**For 2814 800KV Motor:**
- **3S Battery**: 12×4.5 or 13×4.5
- **4S Battery**: 11×4.7 or 12×4.5

**For 3508 580KV Motor:**
- **4S Battery**: 14×4.8 or 15×5.5
- **6S Battery**: 13×4.5 or 15×5.5

---

## 7. GPS and Navigation Modules {#gps}

### u-blox M8N GPS Module

#### **Specifications**
- **Chipset**: u-blox M8N
- **Channels**: 72 channels (concurrent)
- **Update Rate**: 5Hz, 10Hz
- **Accuracy**: 2.5m CEP (Circular Error Probable)
- **Sensitivity**: -167 dBm (acquisition), -160 dBm (tracking)
- **Time to First Fix (TTFF)**: 26 seconds (cold start), 1 second (hot start)
- **Voltage**: 3.3V-5V
- **Current**: 30mA-50mA
- **Size**: 25mm x 25mm
- **Weight**: 5g-10g
- **Price**: $15-$30

#### **Features**
- GPS, GLONASS, BeiDou support
- Compass (magnetometer) included
- LED status indicator
- External antenna connector

### u-blox M9N GPS Module

#### **Specifications**
- **Chipset**: u-blox M9N
- **Channels**: 72 channels
- **Update Rate**: 10Hz, 20Hz
- **Accuracy**: 1.5m CEP
- **Sensitivity**: -167 dBm (acquisition), -160 dBm (tracking)
- **TTFF**: 26 seconds (cold), 1 second (hot)
- **Voltage**: 3.3V-5V
- **Current**: 30mA-50mA
- **Price**: $25-$40

### RTK GPS Modules

#### **u-blox ZED-F9P RTK GPS**
- **Accuracy**: 1cm (with RTK correction), 1.5m (standalone)
- **Update Rate**: 20Hz
- **Channels**: 184 channels
- **RTK Correction**: NTRIP, RTCM 3.x
- **Voltage**: 3.0V-3.6V
- **Current**: 80mA-120mA
- **Price**: $150-$250

---

## 8. Power Distribution Board (PDB) {#pdb}

### PDB Specifications

#### **Standard PDB**
- **Input Voltage**: 2S-6S (7.4V-25.2V)
- **Outputs**: 4-8 ESC power outputs
- **BEC Output**: 5V/3A (optional)
- **Current Rating**: 60A-200A total
- **Size**: 50mm x 50mm to 100mm x 100mm
- **Weight**: 10g-30g
- **Price**: $10-$30

#### **Features**
- **Voltage Monitoring**: Built-in voltage divider
- **Current Monitoring**: Shunt resistor (optional)
- **LED Indicators**: Power status
- **Mounting Holes**: M3 screws

---

## 9. Radio Control System {#radio}

### Transmitter Specifications

#### **FrSky Taranis X9D Plus**
- **Channels**: 16 channels
- **Frequency**: 2.4GHz (D16 protocol)
- **Range**: 1.5km-2km (line of sight)
- **Battery**: 2000mAh LiPo
- **Display**: 128x64 pixel LCD
- **Price**: $200-$300

#### **Spektrum DX6**
- **Channels**: 6 channels
- **Frequency**: 2.4GHz (DSM2/DSMX)
- **Range**: 1km-1.5km
- **Battery**: 4x AA or LiPo
- **Price**: $150-$200

### Receiver Specifications

#### **FrSky X8R Receiver**
- **Channels**: 8 channels (PWM), 16 channels (SBUS)
- **Frequency**: 2.4GHz
- **Range**: 1.5km-2km
- **Voltage**: 4.0V-10V
- **Current**: 30mA
- **Size**: 46mm x 26.5mm x 14.2mm
- **Weight**: 12g
- **Price**: $25-$35

#### **FrSky R-XSR Receiver**
- **Channels**: 8 channels (SBUS)
- **Frequency**: 2.4GHz
- **Range**: 1.5km-2km
- **Voltage**: 4.0V-10V
- **Current**: 25mA
- **Size**: 16mm x 11mm x 4.5mm
- **Weight**: 1.1g
- **Price**: $15-$25

---

## 10. Assembly Procedures {#assembly}

### Step-by-Step Assembly

#### **1. Frame Assembly**
1. Attach arms to center plate using M3 screws
2. Ensure 45° angle for X configuration
3. Check motor mount alignment
4. Verify propeller clearance

#### **2. Motor Installation**
1. Mount motors to arms using M3 screws
2. Ensure proper rotation direction (2 CW, 2 CCW)
3. Secure motor wires along arms
4. Check motor alignment

#### **3. ESC Installation**
1. Mount ESCs to arms or center plate
2. Connect motor wires to ESC (3 wires, any order initially)
3. Connect ESC power wires to PDB
4. Connect ESC signal wires to flight controller

#### **4. Flight Controller Installation**
1. Mount flight controller to center plate (vibration dampening)
2. Connect ESC signal wires (PWM or SBUS)
3. Connect receiver (PWM or SBUS)
4. Connect GPS module
5. Connect power (via BEC or PDB)

#### **5. Battery Installation**
1. Mount battery tray to frame
2. Connect battery to PDB or ESCs
3. Secure battery with straps
4. Check center of gravity (CG)

#### **6. Propeller Installation**
1. Install propellers matching motor rotation
2. Tighten prop nuts securely
3. Check propeller balance
4. Verify clearance

---

## 11. Testing and Calibration {#testing}

### Pre-Flight Checklist

1. **Visual Inspection**
   - Frame integrity
   - Motor mounting
   - Propeller installation
   - Wire connections
   - Battery connection

2. **Electronic Check**
   - Flight controller initialization
   - GPS lock (if applicable)
   - Receiver connection
   - ESC calibration
   - Motor direction verification

3. **Calibration Procedures**
   - **Accelerometer Calibration**: Level surface, follow FC instructions
   - **Compass Calibration**: Rotate drone in figure-8 pattern
   - **ESC Calibration**: Set throttle range for all ESCs
   - **Radio Calibration**: Set channel endpoints and center

4. **Motor Test**
   - Test each motor individually
   - Verify rotation direction
   - Check for vibrations
   - Verify throttle response

5. **First Flight**
   - Start with low throttle
   - Test hover stability
   - Check for drift
   - Test control response

---

## 12. Design Calculations {#calculations}

### Thrust-to-Weight Ratio

**Formula**: TWR = Total Thrust / Total Weight

**Recommended Values**:
- **Minimum**: 2:1 (hover at 50% throttle)
- **Good**: 3:1 (hover at 33% throttle)
- **Excellent**: 4:1 (hover at 25% throttle)

**Example**:
- Total Weight: 2000g
- Total Thrust: 6000g
- TWR = 6000/2000 = 3:1 ✓

### Flight Time Estimation

**Formula**: Flight Time = (Battery Capacity × Battery Efficiency) / (Average Current Draw)

**Example**:
- Battery: 5000mAh (5Ah)
- Efficiency: 80% (0.8)
- Average Current: 30A
- Flight Time = (5 × 0.8) / 30 = 0.133 hours = 8 minutes

### Power Calculation

**Formula**: Power (W) = Voltage (V) × Current (A)

**Example**:
- Battery: 4S (14.8V)
- Current: 30A per motor × 4 motors = 120A total
- Power = 14.8 × 120 = 1776W

### Motor Current Estimation

**Formula**: Current (A) = Thrust (g) / (Motor Efficiency × Voltage × KV × Propeller Constant)

**Simplified**: Use motor datasheet or online calculators

---

## Complete Build Example: 550mm Quadcopter

### Component List

1. **Frame**: 550mm carbon fiber quadcopter frame - $80
2. **Motors**: 4x 2814 800KV brushless motors - $120 ($30 each)
3. **ESCs**: 4x 40A BLHeli_32 ESCs - $80 ($20 each)
4. **Flight Controller**: Pixhawk 4 - $200
5. **Battery**: 4S 5000mAh 30C LiPo - $60
6. **Propellers**: 4x 12×4.5 carbon fiber - $40 ($10 each)
7. **GPS**: u-blox M9N GPS module - $35
8. **PDB**: Power distribution board with BEC - $25
9. **Receiver**: FrSky R-XSR - $20
10. **Radio**: FrSky Taranis X9D Plus - $250
11. **Miscellaneous**: Wires, connectors, screws, etc. - $50

**Total Cost**: ~$960

### Specifications

- **Frame Size**: 550mm diagonal
- **Total Weight**: ~2500g (with battery)
- **Max Takeoff Weight**: 5000g
- **Thrust**: 8000g total (2000g per motor)
- **TWR**: 3.2:1
- **Flight Time**: 12-15 minutes (hover)
- **Payload Capacity**: 1500g-2000g

---

## Safety Considerations

1. **LiPo Battery Safety**
   - Never overcharge or over-discharge
   - Use proper LiPo charger
   - Store at 3.8V per cell
   - Use fireproof bag for storage/charging

2. **Propeller Safety**
   - Always remove propellers when testing
   - Keep clear of spinning propellers
   - Use propeller guards for indoor testing

3. **Radio Safety**
   - Check failsafe settings
   - Test failsafe before flight
   - Maintain line of sight

4. **Flight Safety**
   - Follow local regulations
   - Maintain safe distance from people/property
   - Check weather conditions
   - Have spotter for first flights

---

## Resources and Further Learning

### Educational Programs
- Kansas State University - UAS Design and Integration
- Vaughn College - UAS Design Certificate
- Carroll University - Drone Engineering Major
- WSU Tech - Unmanned Aircraft Systems Program

### Software Tools
- **ArduPilot**: Open-source autopilot software
- **Betaflight**: Flight controller firmware
- **Mission Planner**: Ground control station
- **QGroundControl**: Ground control station

### Testing Equipment
- **Multimeter**: Voltage/current measurement
- **LiPo Checker**: Cell voltage monitoring
- **Propeller Balancer**: Balance propellers
- **Vibration Analyzer**: Check motor/propeller balance

---

**Red Post Farms, LLC | Copyright (c) 2025-2026 | All Rights Reserved**
