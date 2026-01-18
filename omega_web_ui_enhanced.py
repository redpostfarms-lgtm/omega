#!/usr/bin/env python3
"""
Omega Enhanced Web UI
=====================
Modern, feature-rich web interface for Omega Control Panel
Based on Control Panel UI Design specifications

Features:
- 1980s/90s sci-fi aesthetic with modern responsive design
- Real-time monitoring and controls
- Voice interaction support
- Audio visualization
- System status dashboard
- Dark theme with glowing elements
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging

# Setup paths
BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'omega_enhanced_ui_secret_2026'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# HTML Template with 1980s/90s Sci-Fi Aesthetic
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ω OMEGA Control Panel</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            color: #00ff00;
            overflow-x: hidden;
            min-height: 100vh;
        }

        /* Header with Omega Logo */
        .header {
            background: linear-gradient(180deg, #1a1a1a 0%, #0d0d0d 100%);
            border-bottom: 3px solid #ffd700;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(255, 215, 0, 0.3);
        }

        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
        }

        .omega-logo {
            width: 80px;
            height: 80px;
            filter: drop-shadow(0 0 10px rgba(255, 0, 0, 0.5));
        }

        h1 {
            font-size: 3em;
            color: #ff0000;
            text-shadow: 0 0 20px rgba(255, 0, 0, 0.8), 0 0 40px rgba(255, 0, 0, 0.4);
            letter-spacing: 10px;
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }

        .subtitle {
            color: #ffd700;
            font-size: 1.2em;
            margin-top: 10px;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.6);
        }

        /* Main Container */
        .container {
            max-width: 1600px;
            margin: 30px auto;
            padding: 20px;
            display: grid;
            grid-template-columns: 1fr 2fr 1fr;
            grid-template-rows: auto auto 1fr;
            gap: 20px;
        }

        /* Tab Navigation */
        .tab-navigation {
            grid-column: 1 / -1;
            display: flex;
            gap: 10px;
            background: rgba(10, 10, 20, 0.9);
            border: 2px solid #9933ff;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 0 20px rgba(153, 51, 255, 0.3);
        }

        .tab-btn {
            flex: 1;
            padding: 12px 20px;
            background: rgba(153, 51, 255, 0.2);
            border: 2px solid #9933ff;
            border-radius: 5px;
            color: #9933ff;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .tab-btn:hover {
            background: rgba(153, 51, 255, 0.4);
            box-shadow: 0 0 15px rgba(153, 51, 255, 0.5);
        }

        .tab-btn.active {
            background: #9933ff;
            color: #000;
            box-shadow: 0 0 25px rgba(153, 51, 255, 0.8);
        }

        /* Mode Tabs - Knight Rider Style - Below Voice Box */
        .mode-tabs {
            grid-column: 1 / -1;
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }

        .mode-tab {
            flex: 1;
            padding: 15px 25px;
            font-size: 1.1em;
            font-weight: bold;
            text-transform: uppercase;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Courier New', monospace;
            letter-spacing: 2px;
            position: relative;
            overflow: hidden;
        }

        .mode-tab:before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            transition: left 0.5s;
        }

        .mode-tab:hover:before {
            left: 100%;
        }

        .mode-tab-auto {
            background: linear-gradient(135deg, #ffaa00 0%, #ff8800 100%);
            color: #000;
            box-shadow: 0 0 20px rgba(255, 170, 0, 0.5);
        }

        .mode-tab-auto:hover {
            box-shadow: 0 0 30px rgba(255, 170, 0, 0.8);
            transform: scale(1.02);
        }

        .mode-tab-auto.active {
            box-shadow: 0 0 40px rgba(255, 170, 0, 1);
            animation: glow-yellow 1s ease-in-out infinite;
        }

        .mode-tab-normal {
            background: linear-gradient(135deg, #00ff00 0%, #00cc00 100%);
            color: #000;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        }

        .mode-tab-normal:hover {
            box-shadow: 0 0 30px rgba(0, 255, 0, 0.8);
            transform: scale(1.02);
        }

        .mode-tab-normal.active {
            box-shadow: 0 0 40px rgba(0, 255, 0, 1);
            animation: glow-green 1s ease-in-out infinite;
        }

        .mode-tab-pursuit {
            background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
            color: #fff;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
        }

        .mode-tab-pursuit:hover {
            box-shadow: 0 0 30px rgba(255, 0, 0, 0.8);
            transform: scale(1.02);
        }

        .mode-tab-pursuit.active {
            box-shadow: 0 0 40px rgba(255, 0, 0, 1);
            animation: glow-red 1s ease-in-out infinite;
        }

        @keyframes glow-red {
            0%, 100% { box-shadow: 0 0 40px rgba(255, 0, 0, 1); }
            50% { box-shadow: 0 0 60px rgba(255, 0, 0, 1), 0 0 80px rgba(255, 0, 0, 0.5); }
        }

        .tab-content {
            display: none;
            grid-column: 1 / -1;
            grid-row: 2 / -1;
        }

        .tab-content.active {
            display: contents;
        }

        /* Panel Base Style */
        .panel {
            background: rgba(10, 10, 20, 0.9);
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
        }

        .panel-title {
            color: #00ffff;
            font-size: 1.3em;
            margin-bottom: 15px;
            text-transform: uppercase;
            border-bottom: 2px solid #00ffff;
            padding-bottom: 10px;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
        }

        /* Audio Visualizer Display - KITT Voice Box Style */
        .kitt-voice-box {
            background: #000;
            border: 3px solid #ff0000;
            border-radius: 8px;
            height: 120px;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            padding: 20px;
            box-shadow: inset 0 0 30px rgba(255, 0, 0, 0.4), 0 0 20px rgba(255, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
        }

        /* KITT-style scanning effect overlay */
        .kitt-voice-box::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 50%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 0, 0, 0.4), transparent);
            animation: kitt-scan-voice 2s linear infinite;
        }

        .kitt-voice-box.talking::before {
            animation: kitt-scan-voice 0.3s linear infinite;
        }

        @keyframes kitt-scan-voice {
            0% { left: -50%; }
            100% { left: 100%; }
        }

        .voice-box-bar {
            width: 80px;
            background: linear-gradient(180deg, #ff0000 0%, #cc0000 50%, #660000 100%);
            border-radius: 4px;
            transition: height 0.1s ease;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.9), 0 0 30px rgba(255, 0, 0, 0.5);
            position: relative;
            z-index: 1;
            height: 30px;
        }

        .voice-box-bar.active {
            box-shadow: 0 0 30px rgba(255, 0, 0, 1), 0 0 50px rgba(255, 0, 0, 0.8);
            background: linear-gradient(180deg, #ff3333 0%, #ff0000 50%, #cc0000 100%);
        }

        .voice-box-bar.talking {
            animation: voice-bar-pulse 0.3s ease-in-out infinite;
        }

        @keyframes voice-bar-pulse {
            0%, 100% { height: 30px; }
            50% { height: 80px; }
        }

        .voice-box-bar:nth-child(2).talking {
            animation-delay: 0.1s;
        }

        .voice-box-bar:nth-child(3).talking {
            animation-delay: 0.2s;
        }

        /* KITT Scanner Bar - Fixed at Bottom */
        .kitt-scanner {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 8px;
            background: #000;
            border-top: 2px solid #ff0000;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            padding: 0 20px;
            box-shadow: 0 -5px 30px rgba(255, 0, 0, 0.5);
        }

        .kitt-bar {
            width: 8px;
            height: 6px;
            background: linear-gradient(180deg, #ff0000 0%, #990000 100%);
            border-radius: 1px;
            transition: all 0.08s ease;
            box-shadow: 0 0 15px rgba(255, 0, 0, 0.8);
            position: relative;
        }

        .kitt-bar.active {
            height: 8px;
            box-shadow: 0 0 25px rgba(255, 0, 0, 1), 0 0 35px rgba(255, 0, 0, 0.8);
            background: linear-gradient(180deg, #ff3333 0%, #ff0000 100%);
        }

        /* KITT scanning effect overlay */
        .kitt-scanner::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 30%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 0, 0, 0.4), transparent);
            animation: kitt-scan-bottom 2s linear infinite;
            pointer-events: none;
        }

        .kitt-scanner.fast::before {
            animation: kitt-scan-bottom 0.5s linear infinite;
        }

        @keyframes kitt-scan-bottom {
            0% { left: -30%; }
            100% { left: 100%; }
        }

        /* Control Buttons - Sci-Fi Style */
        .control-buttons {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin: 20px 0;
        }

        .btn {
            padding: 15px 30px;
            font-size: 1.2em;
            font-weight: bold;
            text-transform: uppercase;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Courier New', monospace;
            letter-spacing: 2px;
            position: relative;
            overflow: hidden;
        }

        .btn:before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            transition: left 0.5s;
        }

        .btn:hover:before {
            left: 100%;
        }

        .btn-auto-cruise {
            background: linear-gradient(135deg, #ffaa00 0%, #ff8800 100%);
            color: #000;
            box-shadow: 0 0 20px rgba(255, 170, 0, 0.5);
        }

        .btn-auto-cruise:hover {
            box-shadow: 0 0 30px rgba(255, 170, 0, 0.8);
            transform: scale(1.05);
        }

        .btn-auto-cruise.active {
            box-shadow: 0 0 40px rgba(255, 170, 0, 1);
            animation: glow-yellow 1s ease-in-out infinite;
        }

        .btn-normal-cruise {
            background: linear-gradient(135deg, #00ff00 0%, #00cc00 100%);
            color: #000;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        }

        .btn-normal-cruise:hover {
            box-shadow: 0 0 30px rgba(0, 255, 0, 0.8);
            transform: scale(1.05);
        }

        .btn-normal-cruise.active {
            box-shadow: 0 0 40px rgba(0, 255, 0, 1);
            animation: glow-green 1s ease-in-out infinite;
        }

        .btn-pursuit {
            background: linear-gradient(135deg, #00aaff 0%, #0088ff 100%);
            color: #fff;
            box-shadow: 0 0 20px rgba(0, 170, 255, 0.5);
        }

        .btn-pursuit:hover {
            box-shadow: 0 0 30px rgba(0, 170, 255, 0.8);
            transform: scale(1.05);
        }

        .btn-pursuit.active {
            box-shadow: 0 0 40px rgba(0, 170, 255, 1);
            animation: glow-blue 1s ease-in-out infinite;
        }

        /* Glow Animations */
        @keyframes glow-yellow {
            0%, 100% { box-shadow: 0 0 40px rgba(255, 170, 0, 1); }
            50% { box-shadow: 0 0 60px rgba(255, 170, 0, 1), 0 0 80px rgba(255, 170, 0, 0.5); }
        }

        @keyframes glow-green {
            0%, 100% { box-shadow: 0 0 40px rgba(0, 255, 0, 1); }
            50% { box-shadow: 0 0 60px rgba(0, 255, 0, 1), 0 0 80px rgba(0, 255, 0, 0.5); }
        }

        @keyframes glow-blue {
            0%, 100% { box-shadow: 0 0 40px rgba(0, 170, 255, 1); }
            50% { box-shadow: 0 0 60px rgba(0, 170, 255, 1), 0 0 80px rgba(0, 170, 255, 0.5); }
        }

        /* Side Control Buttons */
        .side-controls {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 20px;
        }

        .side-btn {
            padding: 12px;
            font-size: 0.9em;
            font-weight: bold;
            border: 2px solid;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
        }

        .side-btn-pink {
            background: rgba(255, 20, 147, 0.2);
            border-color: #ff1493;
            color: #ff1493;
        }

        .side-btn-pink:hover {
            background: rgba(255, 20, 147, 0.4);
            box-shadow: 0 0 15px rgba(255, 20, 147, 0.5);
        }

        .side-btn-red {
            background: rgba(255, 0, 0, 0.2);
            border-color: #ff0000;
            color: #ff0000;
        }

        .side-btn-red:hover {
            background: rgba(255, 0, 0, 0.4);
            box-shadow: 0 0 15px rgba(255, 0, 0, 0.5);
        }

        .side-btn-blue {
            background: rgba(0, 170, 255, 0.2);
            border-color: #00aaff;
            color: #00aaff;
        }

        .side-btn-blue:hover {
            background: rgba(0, 170, 255, 0.4);
            box-shadow: 0 0 15px rgba(0, 170, 255, 0.5);
        }

        /* Status Indicators */
        .status-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-top: 20px;
        }

        .status-item {
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid #00ffff;
            border-radius: 5px;
            padding: 15px;
            text-align: center;
        }

        .status-label {
            font-size: 0.9em;
            color: #00ffff;
            margin-bottom: 8px;
        }

        .status-value {
            font-size: 1.5em;
            color: #00ff00;
            font-weight: bold;
            text-shadow: 0 0 10px rgba(0, 255, 0, 0.5);
        }

        .status-value.warning {
            color: #ffaa00;
        }

        .status-value.error {
            color: #ff0000;
        }

        /* Console Output */
        .console {
            background: #000;
            border: 2px solid #ffff00;
            border-radius: 5px;
            padding: 15px;
            height: 250px;
            overflow-y: auto;
            font-size: 0.9em;
            box-shadow: inset 0 0 20px rgba(255, 255, 0, 0.1);
        }

        .console-line {
            color: #00ff00;
            margin-bottom: 5px;
            text-shadow: 0 0 5px rgba(0, 255, 0, 0.3);
        }

        .console-line.error {
            color: #ff0000;
        }

        .console-line.warning {
            color: #ffaa00;
        }

        .console-line.info {
            color: #00ffff;
        }

        /* RGB Controls */
        .rgb-controls {
            background: rgba(10, 10, 20, 0.9);
            border: 2px solid #0088ff;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 20px rgba(0, 136, 255, 0.3);
            margin-top: 20px;
        }

        .rgb-title {
            color: #0088ff;
            font-size: 1.1em;
            margin-bottom: 15px;
            text-transform: uppercase;
            border-bottom: 2px solid #0088ff;
            padding-bottom: 8px;
            text-shadow: 0 0 10px rgba(0, 136, 255, 0.5);
        }

        .rgb-slider-group {
            margin-bottom: 15px;
        }

        .rgb-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.95em;
        }

        .rgb-label-text {
            font-weight: bold;
        }

        .rgb-label-value {
            color: #00ffff;
        }

        .rgb-slider {
            width: 100%;
            height: 8px;
            border-radius: 4px;
            outline: none;
            -webkit-appearance: none;
            background: rgba(255, 255, 255, 0.2);
        }

        .rgb-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            cursor: pointer;
            border: 2px solid #fff;
        }

        .rgb-slider::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            cursor: pointer;
            border: 2px solid #fff;
        }

        .rgb-slider.red::-webkit-slider-thumb {
            background: #ff0000;
            box-shadow: 0 0 10px rgba(255, 0, 0, 0.8);
        }

        .rgb-slider.red::-moz-range-thumb {
            background: #ff0000;
            box-shadow: 0 0 10px rgba(255, 0, 0, 0.8);
        }

        .rgb-slider.green::-webkit-slider-thumb {
            background: #00ff00;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.8);
        }

        .rgb-slider.green::-moz-range-thumb {
            background: #00ff00;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.8);
        }

        .rgb-slider.blue::-webkit-slider-thumb {
            background: #0088ff;
            box-shadow: 0 0 10px rgba(0, 136, 255, 0.8);
        }

        .rgb-slider.blue::-moz-range-thumb {
            background: #0088ff;
            box-shadow: 0 0 10px rgba(0, 136, 255, 0.8);
        }

        .rgb-preview {
            width: 100%;
            height: 60px;
            border: 2px solid #0088ff;
            border-radius: 5px;
            margin-top: 15px;
            box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.5);
        }

        /* Chat Box */
        .chat-container {
            background: rgba(10, 10, 20, 0.9);
            border: 2px solid #ffff00;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 0 20px rgba(255, 255, 0, 0.3);
            margin-top: 20px;
            display: flex;
            flex-direction: column;
            height: 300px;
        }

        .chat-title {
            color: #ffff00;
            font-size: 1.1em;
            margin-bottom: 10px;
            text-transform: uppercase;
            border-bottom: 2px solid #ffff00;
            padding-bottom: 8px;
            text-shadow: 0 0 10px rgba(255, 255, 0, 0.5);
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            background: #000;
            border: 1px solid #ffff00;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
            box-shadow: inset 0 0 10px rgba(255, 255, 0, 0.1);
        }

        .chat-message {
            margin-bottom: 8px;
            padding: 5px;
            border-radius: 3px;
        }

        .chat-message.user {
            color: #00ffff;
            text-align: right;
        }

        .chat-message.system {
            color: #ffff00;
        }

        .chat-input-container {
            display: flex;
            gap: 10px;
        }

        .chat-input {
            flex: 1;
            background: rgba(0, 0, 0, 0.7);
            border: 2px solid #ffff00;
            border-radius: 5px;
            padding: 10px;
            color: #ffff00;
            font-family: 'Courier New', monospace;
            font-size: 0.95em;
        }

        .chat-input:focus {
            outline: none;
            box-shadow: 0 0 10px rgba(255, 255, 0, 0.5);
        }

        .chat-send-btn {
            padding: 10px 20px;
            background: linear-gradient(135deg, #ffff00 0%, #ffaa00 100%);
            border: 2px solid #ffff00;
            border-radius: 5px;
            color: #000;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .chat-send-btn:hover {
            box-shadow: 0 0 15px rgba(255, 255, 0, 0.7);
            transform: scale(1.05);
        }

        /* Voice Control - Relocated to side */
        .voice-control {
            position: fixed;
            right: 40px;
            bottom: 40px;
            z-index: 1000;
        }

        .voice-btn {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: radial-gradient(circle, #ff0000 0%, #cc0000 100%);
            border: 4px solid #ffd700;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2em;
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.5);
        }

        .voice-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 0 40px rgba(255, 0, 0, 0.8);
        }

        .voice-btn.active {
            animation: voice-pulse 1s ease-in-out infinite;
            background: radial-gradient(circle, #00ff00 0%, #00cc00 100%);
            border-color: #00ff00;
        }

        .voice-btn.listening {
            animation: voice-listening 0.5s ease-in-out infinite;
            background: radial-gradient(circle, #00ff00 0%, #00aa00 100%);
            border-color: #00ff00;
            box-shadow: 0 0 40px rgba(0, 255, 0, 1);
        }

        @keyframes voice-pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.15); }
        }

        @keyframes voice-listening {
            0%, 100% { box-shadow: 0 0 40px rgba(0, 255, 0, 1); }
            50% { box-shadow: 0 0 60px rgba(0, 255, 0, 1), 0 0 80px rgba(0, 255, 0, 0.5); }
        }

        .voice-status-indicator {
            position: absolute;
            top: -30px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.8);
            border: 2px solid #00ffff;
            border-radius: 5px;
            padding: 5px 10px;
            font-size: 0.8em;
            color: #00ffff;
            white-space: nowrap;
            display: none;
        }

        .voice-control:hover .voice-status-indicator {
            display: block;
        }

        /* Responsive Design */
        @media (max-width: 1200px) {
            .container {
                grid-template-columns: 1fr;
            }
        }

        /* Scan Lines Effect */
        body:before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(
                0deg,
                rgba(0, 255, 0, 0.03) 0px,
                transparent 1px,
                transparent 2px,
                rgba(0, 255, 0, 0.03) 3px
            );
            pointer-events: none;
            z-index: 9999;
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <div class="logo-container">
            <img src="/images/omega_logo_red_gold_wreath.png" alt="Omega Logo" class="omega-logo">
            <div>
                <h1>Ω OMEGA</h1>
                <div class="subtitle">CONTROL PANEL SYSTEM</div>
            </div>
            <img src="/images/omega_logo_red_gold_wreath.png" alt="Omega Logo" class="omega-logo">
        </div>
    </div>

    <!-- Main Container -->
    <div class="container">
        <!-- Tab 1 Content (Main Control) -->
        <div class="tab-content active" id="tab-1">
            <!-- Left Panel: System Status -->
            <div class="panel">
                <div class="panel-title">⚡ System Status</div>
                
                <div class="status-grid">
                    <div class="status-item">
                        <div class="status-label">CPU</div>
                        <div class="status-value" id="cpu-status">--</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Memory</div>
                        <div class="status-value" id="memory-status">--</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Disk</div>
                        <div class="status-value" id="disk-status">--</div>
                    </div>
                    <div class="status-item">
                        <div class="status-label">Network</div>
                        <div class="status-value" id="network-status">ONLINE</div>
                    </div>
                </div>

                <!-- Side Controls (Left) -->
                <div class="side-controls" style="margin-top: 30px;">
                    <button class="side-btn side-btn-blue" onclick="handleSideControl('AIR')">AIR</button>
                    <button class="side-btn side-btn-blue" onclick="handleSideControl('OIL')">OIL</button>
                    <button class="side-btn side-btn-pink" onclick="handleSideControl('P1')">P1</button>
                    <button class="side-btn side-btn-pink" onclick="handleSideControl('P2')">P2</button>
                </div>
            </div>

            <!-- Center Panel: Main Controls -->
            <div class="panel">
                <div class="panel-title">🎛️ KITT Voice Interface</div>
                
                <!-- KITT Voice Box with 3 Bars -->
                <div class="kitt-voice-box" id="kitt-voice-box">
                    <div class="voice-box-bar" id="voice-bar-1"></div>
                    <div class="voice-box-bar" id="voice-bar-2"></div>
                    <div class="voice-box-bar" id="voice-bar-3"></div>
                </div>

                <!-- Mode Tabs (Under Voice Box) -->
                <div class="mode-tabs">
                    <button class="mode-tab mode-tab-auto active" id="mode-auto" onclick="switchMode('auto')">
                        🚀 AUTO CRUISE
                    </button>
                    <button class="mode-tab mode-tab-normal" id="mode-normal" onclick="switchMode('normal')">
                        ⚡ NORMAL CRUISE
                    </button>
                    <button class="mode-tab mode-tab-pursuit" id="mode-pursuit" onclick="switchMode('pursuit')">
                        🎯 PURSUIT MODE
                    </button>
                </div>

                <!-- Status Display -->
                <div style="padding: 20px; text-align: center; color: #00ffff; font-size: 1.2em;">
                    <p style="margin-bottom: 10px;">Mode: <span id="current-mode-display" style="color: #ffaa00; font-weight: bold;">AUTO CRUISE</span></p>
                    <p style="color: #00ff00;">● All systems nominal</p>
                </div>
            </div>

            <!-- Right Panel: Console & RGB Controls -->
                <div class="panel-title">📟 System Console</div>
                
                <!-- Console Output (Yellow Area) -->
                <div class="console" id="console">
                    <div class="console-line info">[SYSTEM] Omega Control Panel initialized</div>
                    <div class="console-line">[OK] All systems nominal</div>
                    <div class="console-line info">[INFO] Awaiting commands...</div>
                </div>

                <!-- RGB Controls (Blue Area) -->
                <div class="rgb-controls">
                    <div class="rgb-title">🎨 RGB Controls</div>
                    
                    <div class="rgb-slider-group">
                        <div class="rgb-label">
                            <span class="rgb-label-text" style="color: #ff0000;">RED</span>
                            <span class="rgb-label-value" id="rgb-r-value">128</span>
                        </div>
                        <input type="range" min="0" max="255" value="128" class="rgb-slider red" id="rgb-r" oninput="updateRGB()">
                    </div>

                    <div class="rgb-slider-group">
                        <div class="rgb-label">
                            <span class="rgb-label-text" style="color: #00ff00;">GREEN</span>
                            <span class="rgb-label-value" id="rgb-g-value">128</span>
                        </div>
                        <input type="range" min="0" max="255" value="128" class="rgb-slider green" id="rgb-g" oninput="updateRGB()">
                    </div>

                    <div class="rgb-slider-group">
                        <div class="rgb-label">
                            <span class="rgb-label-text" style="color: #0088ff;">BLUE</span>
                            <span class="rgb-label-value" id="rgb-b-value">128</span>
                        </div>
                        <input type="range" min="0" max="255" value="128" class="rgb-slider blue" id="rgb-b" oninput="updateRGB()">
                    </div>

                    <div class="rgb-preview" id="rgb-preview"></div>
                </div>

                <!-- Side Controls (Right) -->
                <div class="side-controls" style="margin-top: 20px;">
                    <button class="side-btn side-btn-blue" onclick="handleSideControl('S1')">S1</button>
                    <button class="side-btn side-btn-blue" onclick="handleSideControl('S2')">S2</button>
                    <button class="side-btn side-btn-red" onclick="handleSideControl('P3')">P3</button>
                    <button class="side-btn side-btn-red" onclick="handleSideControl('P4')">P4</button>
                </div>
            </div>
        </div>

        <!-- Tab 2 Content (Chat Interface) -->
        <div class="tab-content" id="tab-2">
            <div class="panel" style="grid-column: 1 / -1;">
                <div class="panel-title">💬 Communication Center</div>
                
                <!-- Chat Box (Yellow Area) -->
                <div class="chat-container">
                    <div class="chat-title">Text Chat</div>
                    <div class="chat-messages" id="chat-messages">
                        <div class="chat-message system">[SYSTEM] Chat interface ready</div>
                    </div>
                    <div class="chat-input-container">
                        <input type="text" class="chat-input" id="chat-input" placeholder="Type message here..." onkeypress="handleChatKeypress(event)">
                        <button class="chat-send-btn" onclick="sendChatMessage()">SEND</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Tab 3 Content (Additional Features) -->
        <div class="tab-content" id="tab-3">
            <div class="panel" style="grid-column: 1 / -1;">
                <div class="panel-title">⚙️ Advanced Settings</div>
                <div style="padding: 20px; text-align: center; color: #00ffff; font-size: 1.2em;">
                    Additional features will be added here
                </div>
            </div>
        </div>

        <!-- Tab 4 Content (Diagnostics) -->
        <div class="tab-content" id="tab-4">
            <div class="panel" style="grid-column: 1 / -1;">
                <div class="panel-title">🔧 System Diagnostics</div>
                <div style="padding: 20px; text-align: center; color: #00ffff; font-size: 1.2em;">
                    Diagnostic tools will be added here
                </div>
            </div>
        </div>
    </div>

    <!-- KITT Scanner Bar - Fixed at Bottom -->
    <div class="kitt-scanner" id="kitt-scanner">
        <!-- Scanner bars will be generated by JavaScript -->
    </div>

    <!-- Voice Control (Relocated to bottom right) -->
    <div class="voice-control">
        <div class="voice-status-indicator" id="voice-status-indicator">Ready</div>
        <button class="voice-btn" id="voice-btn" onclick="toggleVoice()">
            🎤
        </button>
    </div>

    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script>
        // Initialize Socket.IO
        const socket = io();
        
        // Current mode
        let currentMode = 'auto';
        let voiceActive = false;

        // Initialize KITT scanner at bottom
        const kittScanner = document.getElementById('kitt-scanner');
        const numKittBars = 80;
        const kittBars = [];
        
        for (let i = 0; i < numKittBars; i++) {
            const bar = document.createElement('div');
            bar.className = 'kitt-bar';
            kittScanner.appendChild(bar);
            kittBars.push(bar);
        }

        // KITT-style scanner animation
        let scanPosition = 0;
        let scanDirection = 1;
        let scanSpeed = 150; // Slowed down from 80ms
        let scanInterval;
        
        function animateKittScanner() {
            kittBars.forEach((bar, index) => {
                // Distance from scan position
                const distance = Math.abs(index - scanPosition);
                
                // Active bars based on distance
                if (distance === 0) {
                    bar.classList.add('active');
                } else if (distance <= 3) {
                    bar.classList.add('active');
                } else {
                    bar.classList.remove('active');
                }
            });
            
            // Move scan position
            scanPosition += scanDirection;
            if (scanPosition >= numKittBars - 1 || scanPosition <= 0) {
                scanDirection *= -1;
            }
        }

        // Start KITT scanner animation
        function startScanner(speed) {
            if (scanInterval) clearInterval(scanInterval);
            scanSpeed = speed;
            scanInterval = setInterval(animateKittScanner, scanSpeed);
            
            // Update scanner class for fast animation
            if (speed < 100) {
                kittScanner.classList.add('fast');
            } else {
                kittScanner.classList.remove('fast');
            }
        }

        // Start with normal speed
        startScanner(150);

        // Switch mode tabs (Auto, Normal, Pursuit)
        function switchMode(mode) {
            // Remove active class from all mode tabs
            document.querySelectorAll('.mode-tab').forEach(tab => tab.classList.remove('active'));
            
            // Add active class to selected mode
            document.getElementById('mode-' + mode).classList.add('active');
            
            currentMode = mode;
            
            // Update display text
            const modeDisplay = document.getElementById('current-mode-display');
            let modeText = '';
            let modeColor = '';
            
            if (mode === 'auto') {
                modeText = 'AUTO CRUISE';
                modeColor = '#ffaa00';
                startScanner(150); // Normal speed
            } else if (mode === 'normal') {
                modeText = 'NORMAL CRUISE';
                modeColor = '#00ff00';
                startScanner(200); // Slower
            } else if (mode === 'pursuit') {
                modeText = 'PURSUIT MODE';
                modeColor = '#ff0000';
                startScanner(40); // Fast like Knight Rider in pursuit!
            }
            
            modeDisplay.textContent = modeText;
            modeDisplay.style.color = modeColor;
            
            logConsole(`[MODE] ${modeText} activated`, 'info');
            
            // Emit to server
            socket.emit('mode_change', { mode: mode });
        }

        // Tab switching function (for additional tabs if needed)
        function switchTab(tabNumber) {
            // Hide all tab contents
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // Remove active class from all tab buttons
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected tab content
            document.getElementById('tab-' + tabNumber).classList.add('active');
            
            // Add active class to clicked button
            document.querySelectorAll('.tab-btn')[tabNumber - 1].classList.add('active');
            
            logConsole(`[TAB] Switched to Tab ${tabNumber}`, 'info');
        }

        // RGB Controls
        function updateRGB() {
            const r = document.getElementById('rgb-r').value;
            const g = document.getElementById('rgb-g').value;
            const b = document.getElementById('rgb-b').value;
            
            document.getElementById('rgb-r-value').textContent = r;
            document.getElementById('rgb-g-value').textContent = g;
            document.getElementById('rgb-b-value').textContent = b;
            
            const preview = document.getElementById('rgb-preview');
            preview.style.background = `rgb(${r}, ${g}, ${b})`;
            preview.style.boxShadow = `inset 0 0 20px rgba(0, 0, 0, 0.5), 0 0 20px rgba(${r}, ${g}, ${b}, 0.5)`;
            
            // Emit to server
            socket.emit('rgb_change', { r: parseInt(r), g: parseInt(g), b: parseInt(b) });
        }

        // Initialize RGB preview
        updateRGB();

        // Chat functions
        function sendChatMessage() {
            const input = document.getElementById('chat-input');
            const message = input.value.trim();
            
            if (message) {
                const messagesDiv = document.getElementById('chat-messages');
                const msgDiv = document.createElement('div');
                msgDiv.className = 'chat-message user';
                msgDiv.textContent = `[USER] ${message}`;
                messagesDiv.appendChild(msgDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
                
                // Emit to server
                socket.emit('chat_message', { message: message });
                
                input.value = '';
                
                logConsole(`[CHAT] Message sent: ${message}`, 'info');
            }
        }

        function handleChatKeypress(event) {
            if (event.key === 'Enter') {
                sendChatMessage();
            }
        }

        // Socket event handlers
        socket.on('chat_response', function(data) {
            const messagesDiv = document.getElementById('chat-messages');
            const msgDiv = document.createElement('div');
            msgDiv.className = 'chat-message system';
            msgDiv.textContent = `[OMEGA] ${data.message}`;
            messagesDiv.appendChild(msgDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        });

        // Handle side controls
        function handleSideControl(control) {
            logConsole(`[CONTROL] ${control} activated`, 'warning');
            socket.emit('side_control', { control: control });
        }

        // Voice recognition setup
        let recognition = null;
        let isListening = false;
        let isTalking = false;
        let micPermissionGranted = false;
        
        // Check microphone permission on load
        async function checkMicPermission() {
            try {
                if (navigator.permissions && navigator.permissions.query) {
                    const result = await navigator.permissions.query({ name: 'microphone' });
                    micPermissionGranted = (result.state === 'granted');
                    console.log('Microphone permission:', result.state);
                    
                    result.onchange = () => {
                        micPermissionGranted = (result.state === 'granted');
                        console.log('Microphone permission changed:', result.state);
                    };
                } else {
                    // Browser doesn't support permission API, assume granted
                    micPermissionGranted = true;
                }
            } catch (e) {
                console.log('Permission check not supported, assuming granted');
                micPermissionGranted = true;
            }
        }
        
        // Check permissions on load
        checkMicPermission();
        
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            recognition.onstart = function() {
                console.log('Voice recognition started');
                isListening = true;
                const voiceBtn = document.getElementById('voice-btn');
                const statusIndicator = document.getElementById('voice-status-indicator');
                const voiceBox = document.getElementById('kitt-voice-box');
                
                voiceBtn.classList.add('listening');
                voiceBox.classList.add('talking');
                statusIndicator.textContent = 'Listening...';
                statusIndicator.style.borderColor = '#00ff00';
                statusIndicator.style.color = '#00ff00';
                logConsole('[VOICE] Listening...', 'info');
                
                // Animate voice bars
                startVoiceAnimation();
            };
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                console.log('Recognized:', transcript);
                logConsole(`[VOICE] Recognized: "${transcript}"`, 'info');
                
                // Send to server
                socket.emit('voice_command', { command: transcript });
                
                // Process voice commands
                processVoiceCommand(transcript.toLowerCase());
                
                // Speak response
                speak(`Command received: ${transcript}`);
            };
            
            recognition.onerror = function(event) {
                console.error('Voice recognition error:', event.error);
                logConsole(`[VOICE] Error: ${event.error}`, 'error');
                isListening = false;
                stopVoiceAnimation();
                const voiceBtn = document.getElementById('voice-btn');
                const voiceBox = document.getElementById('kitt-voice-box');
                voiceBtn.classList.remove('listening');
                voiceBox.classList.remove('talking');
                updateVoiceStatus('Ready');
                
                if (event.error === 'not-allowed') {
                    alert('Microphone access denied. Please allow microphone access in your browser settings.');
                }
            };
            
            recognition.onend = function() {
                console.log('Voice recognition ended');
                isListening = false;
                stopVoiceAnimation();
                const voiceBtn = document.getElementById('voice-btn');
                const voiceBox = document.getElementById('kitt-voice-box');
                voiceBtn.classList.remove('listening');
                voiceBox.classList.remove('talking');
                updateVoiceStatus('Ready');
            };
        } else {
            console.error('Speech recognition not supported');
            logConsole('[VOICE] Speech recognition not supported in this browser', 'error');
        }
        
        // Voice animation for 3 bars
        let voiceAnimationInterval;
        function startVoiceAnimation() {
            const bars = [
                document.getElementById('voice-bar-1'),
                document.getElementById('voice-bar-2'),
                document.getElementById('voice-bar-3')
            ];
            
            bars.forEach(bar => bar.classList.add('talking'));
            
            voiceAnimationInterval = setInterval(() => {
                bars.forEach((bar, index) => {
                    const randomHeight = 30 + Math.random() * 60;
                    bar.style.height = randomHeight + 'px';
                });
            }, 100);
        }
        
        function stopVoiceAnimation() {
            const bars = [
                document.getElementById('voice-bar-1'),
                document.getElementById('voice-bar-2'),
                document.getElementById('voice-bar-3')
            ];
            
            bars.forEach(bar => {
                bar.classList.remove('talking');
                bar.style.height = '30px';
            });
            
            if (voiceAnimationInterval) {
                clearInterval(voiceAnimationInterval);
            }
        }
        
        // Text-to-Speech function
        function speak(text) {
            if ('speechSynthesis' in window) {
                // Cancel any ongoing speech
                speechSynthesis.cancel();
                
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 1.0;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;
                
                utterance.onstart = function() {
                    isTalking = true;
                    startVoiceAnimation();
                    const voiceBox = document.getElementById('kitt-voice-box');
                    voiceBox.classList.add('talking');
                    logConsole('[TTS] Speaking...', 'info');
                };
                
                utterance.onend = function() {
                    isTalking = false;
                    stopVoiceAnimation();
                    const voiceBox = document.getElementById('kitt-voice-box');
                    voiceBox.classList.remove('talking');
                    logConsole('[TTS] Speech complete', 'info');
                };
                
                utterance.onerror = function(event) {
                    console.error('Speech synthesis error:', event);
                    isTalking = false;
                    stopVoiceAnimation();
                };
                
                speechSynthesis.speak(utterance);
            } else {
                console.error('Speech synthesis not supported');
                logConsole('[TTS] Text-to-speech not supported', 'error');
            }
        }
        
        function updateVoiceStatus(text) {
            const statusIndicator = document.getElementById('voice-status-indicator');
            statusIndicator.textContent = text;
            if (text === 'Ready') {
                statusIndicator.style.borderColor = '#00ffff';
                statusIndicator.style.color = '#00ffff';
            }
        }
        
        function toggleVoice() {
            console.log('Toggle voice clicked');
            
            if (!recognition) {
                logConsole('[VOICE] Speech recognition not supported in this browser', 'error');
                alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
                return;
            }
            
            if (isListening) {
                console.log('Stopping recognition...');
                recognition.stop();
            } else {
                console.log('Starting recognition...');
                try {
                    recognition.start();
                } catch (e) {
                    console.error('Error starting recognition:', e);
                    logConsole(`[VOICE] Error: ${e.message}`, 'error');
                    
                    // If already started, stop and restart
                    if (e.message && e.message.includes('already started')) {
                        recognition.stop();
                        setTimeout(() => {
                            try {
                                recognition.start();
                            } catch (e2) {
                                console.error('Error restarting:', e2);
                            }
                        }, 100);
                    }
                }
            }
        }
        
        function processVoiceCommand(command) {
            // Process voice commands
            if (command.includes('auto cruise') || command.includes('auto mode')) {
                switchMode('auto');
            } else if (command.includes('normal cruise') || command.includes('normal mode')) {
                switchMode('normal');
            } else if (command.includes('pursuit') || command.includes('pursuit mode')) {
                switchMode('pursuit');
            } else if (command.includes('tab') || command.includes('switch')) {
                // Extract tab number
                for (let i = 1; i <= 4; i++) {
                    if (command.includes(i.toString()) || command.includes(['one', 'two', 'three', 'four'][i-1])) {
                        switchTab(i);
                        break;
                    }
                }
            } else {
                logConsole(`[VOICE] Command not recognized: "${command}"`, 'warning');
            }
        }

        // Log to console
        function logConsole(message, type = '') {
            const console = document.getElementById('console');
            const line = document.createElement('div');
            line.className = 'console-line ' + type;
            line.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            console.appendChild(line);
            console.scrollTop = console.scrollHeight;
            
            // Keep only last 50 lines
            const lines = console.querySelectorAll('.console-line');
            if (lines.length > 50) {
                lines[0].remove();
            }
        }

        // Update system status
        function updateStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('cpu-status').textContent = data.cpu + '%';
                    document.getElementById('memory-status').textContent = data.memory + '%';
                    document.getElementById('disk-status').textContent = data.disk + '%';
                })
                .catch(error => console.error('Error fetching status:', error));
        }

        // Socket.IO event handlers
        socket.on('connect', () => {
            logConsole('[SOCKET] Connected to server', 'info');
        });

        socket.on('console_update', (data) => {
            logConsole(data.message, data.type || '');
        });

        socket.on('status_update', (data) => {
            if (data.cpu) document.getElementById('cpu-status').textContent = data.cpu + '%';
            if (data.memory) document.getElementById('memory-status').textContent = data.memory + '%';
            if (data.disk) document.getElementById('disk-status').textContent = data.disk + '%';
        });

        // Update status every 5 seconds
        setInterval(updateStatus, 5000);
        updateStatus();

        // Initialize
        logConsole('[INIT] Interface ready', 'info');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main UI page"""
    return HTML_TEMPLATE

@app.route('/images/<path:filename>')
def serve_image(filename):
    """Serve images"""
    return send_from_directory(IMAGES_DIR, filename)

@app.route('/api/status')
def get_status():
    """Get system status"""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        return jsonify({
            'cpu': round(cpu, 1),
            'memory': round(memory, 1),
            'disk': round(disk, 1),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'cpu': 0,
            'memory': 0,
            'disk': 0,
            'error': str(e)
        })

@socketio.on('mode_change')
def handle_mode_change(data):
    """Handle mode change"""
    mode = data.get('mode')
    logger.info(f"Mode changed to: {mode}")
    emit('console_update', {
        'message': f'[SERVER] Mode changed to {mode.upper()}',
        'type': 'info'
    }, broadcast=True)

@socketio.on('side_control')
def handle_side_control(data):
    """Handle side control activation"""
    control = data.get('control')
    logger.info(f"Side control activated: {control}")
    emit('console_update', {
        'message': f'[SERVER] Control {control} processed',
        'type': 'warning'
    }, broadcast=True)

@socketio.on('voice_control')
def handle_voice_control(data):
    """Handle voice control toggle"""
    active = data.get('active')
    logger.info(f"Voice control: {'activated' if active else 'deactivated'}")
    emit('console_update', {
        'message': f'[SERVER] Voice recognition {"enabled" if active else "disabled"}',
        'type': 'info'
    }, broadcast=True)

@socketio.on('rgb_change')
def handle_rgb_change(data):
    """Handle RGB color change"""
    r = data.get('r', 0)
    g = data.get('g', 0)
    b = data.get('b', 0)
    logger.info(f"RGB changed to: R={r}, G={g}, B={b}")
    emit('console_update', {
        'message': f'[RGB] Color set to RGB({r}, {g}, {b})',
        'type': 'info'
    }, broadcast=True)

@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle chat message from user"""
    message = data.get('message', '')
    logger.info(f"Chat message received: {message}")
    
    # Echo response (you can add AI processing here)
    response = f"Message received: {message}"
    
    emit('chat_response', {
        'message': response
    })
    
    emit('console_update', {
        'message': f'[CHAT] User: {message}',
        'type': 'info'
    }, broadcast=True)

@socketio.on('voice_command')
def handle_voice_command(data):
    """Handle voice command from user"""
    command = data.get('command', '')
    logger.info(f"Voice command received: {command}")
    
    emit('console_update', {
        'message': f'[VOICE] Command: {command}',
        'type': 'info'
    }, broadcast=True)

def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description='Omega Enhanced Web UI')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5001, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print(" " * 20 + "Ω OMEGA ENHANCED WEB UI")
    print("=" * 80)
    print(f"\n🚀 Starting server on http://{args.host}:{args.port}")
    print(f"🎛️  Access the control panel at: http://localhost:{args.port}")
    print("\n✅ Features:")
    print("   • 1980s/90s Sci-Fi Aesthetic")
    print("   • Real-time Audio Visualization")
    print("   • Voice Control Support")
    print("   • System Monitoring")
    print("   • WebSocket Communication")
    print("\n📝 Press Ctrl+C to stop")
    print("=" * 80)
    print()
    
    try:
        socketio.run(
            app,
            host=args.host,
            port=args.port,
            debug=args.debug,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"\n❌ Server error: {e}")

if __name__ == '__main__':
    main()
