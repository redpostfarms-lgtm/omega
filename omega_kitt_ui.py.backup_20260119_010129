#!/usr/bin/env python3
"""
omega_kitt_ui.py - Knight Rider Omega Dashboard (Final 2026 Build)
===================================================================
Complete standalone Pygame-based Knight Rider-inspired dashboard for Omega.
Features:
- Real-time FFT frequency spectrum with mic input
- Multi-octave Perlin noise screen shake
- Audio-reactive color shifts and glow effects
- Peak hold visualization with labels
- Logarithmic frequency scaling
- Octave grid lines with pulsing glow
- Vignette and flash effects
- State persistence
"""

import pygame
import sys
import time
import json
import random
import threading
import os
import math
import numpy as np
from pathlib import Path

# Check if surfarray is available (may not be on all systems)
try:
    import pygame.surfarray
    SURFARRAY_AVAILABLE = True
except (ImportError, AttributeError):
    SURFARRAY_AVAILABLE = False

# External dependencies (graceful degradation)
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("PyAudio not installed → using simulated spectrum. pip install pyaudio numpy")

try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

pygame.init()
pygame.mixer.init()

# Screen setup
WIDTH, HEIGHT = 1280, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("Omega - KITT Dashboard")

# Colors
BLACK = (0, 0, 0)
RED = (220, 40, 40)
YELLOW = (255, 220, 0)
GREEN = (60, 255, 60)
ORANGE = (255, 140, 0)
GRAY = (30, 30, 40)
WHITE = (240, 240, 240)
PEAK_HOLD_COLOR = (255, 255, 180)

# Fonts
f_small = pygame.font.SysFont("couriernew", 14)
f_tiny = pygame.font.SysFont("couriernew", 10)
f_med = pygame.font.SysFont("couriernew", 22, bold=True)

# State
state_file = Path(__file__).parent / "omega_state.json"
mute = False
locked = False
cursor_zoom = False
scanner_pos = 0
scanner_dir = 1
temp_levels = {"CPU": 38.0, "GPU": 45.0, "RAM": 55.0}
active_agents = ["Ara", "Drax", "Kael"]
dormant_agents = ["Vera", "Lorin", "Elowen"]
file_alerts = []

# Audio / FFT settings
CHUNK = 1024
FORMAT = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None
CHANNELS = 1
RATE = 44100
LOG_BINS = 64
F_MIN = 20.0
F_MAX = RATE / 2.0

# Generate log-spaced bin centers
log_freqs = np.logspace(np.log10(F_MIN), np.log10(F_MAX), LOG_BINS)
bin_edges = np.concatenate(([F_MIN], np.sqrt(log_freqs[:-1] * log_freqs[1:]), [F_MAX]))

SPECTRUM_HEIGHT = 180
DECAY_RATE = 0.015
HOLD_TIMEOUT = 10.0
LABEL_THRESHOLD = 0.20
DB_MIN = -60

spectrum_data = np.zeros(LOG_BINS)
peak_hold = np.zeros(LOG_BINS)
peak_decay_timer = np.zeros(LOG_BINS)

# Frequency labels
FREQUENCY_LABELS = [
    (100, "100 Hz"),
    (200, "200 Hz"),
    (500, "500 Hz"),
    (1000, "1 kHz"),
    (2000, "2 kHz"),
    (5000, "5 kHz"),
    (10000, "10 kHz")
]

# Octave frequencies
OCTAVE_FREQS = [31.25, 62.5, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]
GRID_COLOR_LOW = (180, 20, 20)
GRID_COLOR_HIGH = (0, 220, 255)
COLOR_SHIFT_THRESHOLD = 0.35

# Scanner colors
SCANNER_COLOR_LOW = (220, 40, 40)
SCANNER_COLOR_HIGH = (0, 220, 255)
SCANNER_GLOW_WIDTH = 3
SCANNER_GLOW_INTENSITY = 3

# Pulse/Energy settings
BASE_PULSE_SPEED = 0.4
ENERGY_BOOST_FACTOR = 1.5
MIN_ENERGY_FLOOR = 0.1
pulse_phase = 0.0
pulse_factor = 1.0
current_energy = 0.0
energy_boost = 1.0

# Flash settings
EXTREME_PEAK_THRESHOLD = 2.0
FLASH_DURATION = 0.7
FLASH_WHITE_MIX = 0.45
flash_timer = 0.0
flash_intensity = 0.0

# Vignette settings
VIGNETTE_STRENGTH_BASE = 0.35
VIGNETTE_STRENGTH_FLASH = 0.90
vignette_surf = None

# Shake settings (Multi-octave Perlin)
SHAKE_DURATION = 0.75
SHAKE_INTENSITY_MAX = 22.0
SHAKE_SPEED = 9.5
SHAKE_HURST = 0.42
shake_timer = 0.0
shake_start_time = 0.0
shake_offset = (0, 0)

# Scanner hold timer (replaces blocking sleep)
scanner_hold_timer = 0.0
SCANNER_HOLD_DURATION = 0.4

# Cached PerlinNoise2D instance (optimization)
_cached_perlin = None

# Peak reset
PEAK_RESET_FLASH = 0.0
FLASH_DURATION_RESET = 0.8

# PyAudio globals (will be set by start_audio_stream)
p_audio = None
stream_audio = None
audio_active = False

# UI buffer for shake
ui_buffer = pygame.Surface((WIDTH, HEIGHT))

# Multi-octave Perlin Noise Class
class PerlinNoise2D:
    def __init__(self, seed=42):
        np.random.seed(seed)
        self.p = np.arange(256, dtype=int)
        np.random.shuffle(self.p)
        self.p = np.concatenate([self.p, self.p])

    def fade(self, t):
        return 6*t**5 - 15*t**4 + 10*t**3

    def lerp(self, t, a, b):
        return a + t * (b - a)

    def grad(self, hashv, x, y):
        h = hashv & 15
        u = x if (h < 8) else y
        v = y if (h < 4) else (x if h in (12,14) else 0)
        return (u if (h&1)==0 else -u) + 2*(v if (h&2)==0 else -v)

    def noise(self, x, y):
        X = int(np.floor(x)) & 255
        Y = int(np.floor(y)) & 255
        x -= np.floor(x)
        y -= np.floor(y)
        u = self.fade(x)
        v = self.fade(y)
        aa = self.p[self.p[X] + Y]
        ab = self.p[self.p[X] + Y + 1]
        ba = self.p[self.p[X + 1] + Y]
        bb = self.p[self.p[X + 1] + Y + 1]
        return self.lerp(v,
                         self.lerp(u, self.grad(aa, x, y),   self.grad(ba, x-1, y  )),
                         self.lerp(u, self.grad(ab, x, y-1), self.grad(bb, x-1, y-1)))

def fbm_2d(x, y, H=0.5, octaves=7, lacunarity=2.0, scale=1.0, seed=42):
    """Fractal Brownian Motion with Hurst exponent control"""
    global _cached_perlin
    if _cached_perlin is None:
        _cached_perlin = PerlinNoise2D(seed=seed)
    
    persistence = 2 ** (-H)
    frequency = scale
    amplitude = 1.0
    total = 0.0
    max_value = 0.0

    for i in range(octaves):
        total += amplitude * _cached_perlin.noise(x * frequency, y * frequency)
        max_value += amplitude
        amplitude *= persistence
        frequency *= lacunarity

    return total / max_value

# State management
def load_state():
    global active_agents, dormant_agents, temp_levels, file_alerts
    if state_file.exists():
        try:
            with open(state_file, "r") as f:
                data = json.load(f)
                active_agents = data.get("active_agents", active_agents)
                dormant_agents = data.get("dormant_agents", dormant_agents)
                temp_levels = data.get("temps", temp_levels)
                file_alerts = data.get("alerts", file_alerts)
        except Exception as e:
            print(f"Error loading state: {e}")

def save_state():
    data = {
        "active_agents": active_agents,
        "dormant_agents": dormant_agents,
        "temps": temp_levels,
        "alerts": file_alerts
    }
    try:
        with open(state_file, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving state: {e}")

load_state()

# Background save thread
def auto_save_worker():
    """Background thread for auto-saving state"""
    while True:
        time.sleep(12)
        try:
            save_state()
        except Exception as e:
            print(f"Auto-save error: {e}")

threading.Thread(target=auto_save_worker, daemon=True).start()

# Audio setup
def start_audio_stream():
    global p_audio, stream_audio, audio_active
    if not PYAUDIO_AVAILABLE:
        return False
    try:
        p_audio = pyaudio.PyAudio()
        stream_audio = p_audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        audio_active = True
        print("Microphone stream active → FFT spectrum ready!")
        return True
    except Exception as e:
        print(f"Audio error: {e}")
        return False

audio_active = start_audio_stream()

# Vignette creation (optimized)
def create_vignette(width, height):
    """Create vignette - optimized version"""
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    center_x, center_y = width // 2, height // 2
    max_r = np.hypot(center_x, center_y)
    
    if SURFARRAY_AVAILABLE:
        # Fast numpy-based version
        try:
            y_coords, x_coords = np.ogrid[:height, :width]
            dist_from_center = np.sqrt((x_coords - center_x)**2 + (y_coords - center_y)**2)
            alpha = np.clip(255 * (dist_from_center / max_r) ** 2 * VIGNETTE_STRENGTH_BASE, 0, 255).astype(np.uint8)
            rgba_array = np.zeros((height, width, 4), dtype=np.uint8)
            rgba_array[:, :, 3] = alpha
            pygame.surfarray.blit_array(surf, rgba_array)
            return surf
        except Exception:
            pass  # Fall through to slower method
    
    # Fallback: optimized circle drawing (sparse sampling)
    step = max(1, max_r // 200)  # Sample every N pixels instead of every pixel
    for r in range(max_r, 0, -step):
        alpha = int(255 * (r / max_r) ** 2 * VIGNETTE_STRENGTH_BASE)
        alpha = max(0, min(255, alpha))
        pygame.draw.circle(surf, (0, 0, 0, alpha), (center_x, center_y), r)
    
    return surf

vignette_surf = create_vignette(WIDTH, HEIGHT)

# Boot sequence
def boot_sequence():
    screen.fill(BLACK)
    txt = f_med.render("OMEGA ONLINE", True, GREEN)
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 50))
    pygame.display.flip()
    time.sleep(1.2)

    screen.fill(BLACK)
    txt = f_small.render("GATEKEEPER: SCANNING...", True, ORANGE)
    screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    time.sleep(1.5)

    screen.fill(BLACK)
    pygame.display.flip()

boot_sequence()

# Drawing functions
def draw_scanlines(surface):
    for y in range(0, HEIGHT, 10):
        pygame.draw.line(surface, (10, 10, 10), (0, y), (WIDTH, y), 1)

def draw_glowing_scanner(surface):
    global scanner_pos, scanner_dir, scanner_hold_timer
    # Handle hold timer (non-blocking)
    if scanner_hold_timer > 0:
        scanner_hold_timer -= 1/60.0
        return  # Don't move during hold
    
    scanner_pos += 8 * scanner_dir
    if scanner_pos > WIDTH - 80 or scanner_pos < 0:
        scanner_dir *= -1
        scanner_hold_timer = SCANNER_HOLD_DURATION  # Start hold timer

    # Core scanner bar
    base_color = pygame.Color(SCANNER_COLOR_LOW).lerp(
        pygame.Color(SCANNER_COLOR_HIGH),
        min(1.0, max(0.0, (energy_boost - COLOR_SHIFT_THRESHOLD) / (2.5 - COLOR_SHIFT_THRESHOLD)))
    )
    pygame.draw.rect(surface, base_color, (scanner_pos, 8, 60, 4))

    # Glow layers
    glow_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pulse_brightness = 0.8 + 0.2 * pulse_factor
    pulse_alpha_base = int(80 * pulse_factor * energy_boost)

    for layer in range(1, SCANNER_GLOW_INTENSITY + 1):
        alpha = int(pulse_alpha_base / (layer + 1))
        offset = layer * 1.5
        glow_color = (
            min(255, int(base_color.r * pulse_brightness)),
            min(255, int(base_color.g * pulse_brightness)),
            min(255, int(base_color.b * pulse_brightness)),
            alpha
        )
        glow_rect = pygame.Rect(scanner_pos - offset, 8 - offset/2, 60 + offset*2, 4 + offset)
        pygame.draw.rect(glow_surf, glow_color, glow_rect, border_radius=2)

    if SCANNER_GLOW_INTENSITY > 1:
        scaled = pygame.transform.smoothscale(glow_surf, (WIDTH//2, HEIGHT//2))
        glow_surf = pygame.transform.smoothscale(scaled, (WIDTH, HEIGHT))

    surface.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

def draw_dashed_vertical_line_glow(surface, x, y_start, y_end, dash_length=10, gap_length=8, width=1, glow_intensity=4):
    """Draws dashed vertical line with audio-reactive pulsing glow + color shift"""
    if y_start > y_end:
        y_start, y_end = y_end, y_start

    # Core dashes (steady red)
    y = y_start
    while y < y_end:
        segment_end = min(y + dash_length, y_end)
        pygame.draw.line(surface, GRID_COLOR_LOW, (x, y), (x, segment_end), width)
        y += dash_length + gap_length

    # Pulsing glow with color shift
    glow_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    pulse_alpha_base = int(70 * pulse_factor)
    pulse_brightness = 0.75 + 0.25 * pulse_factor

    shift_amount = min(1.0, max(0.0, (energy_boost - COLOR_SHIFT_THRESHOLD) / (2.5 - COLOR_SHIFT_THRESHOLD)))
    glow_base_color = pygame.Color(GRID_COLOR_LOW).lerp(pygame.Color(GRID_COLOR_HIGH), shift_amount)

    for layer in range(1, glow_intensity + 1):
        alpha = int(pulse_alpha_base / (layer + 1))
        offset = layer * 1.8

        y = y_start
        while y < y_end:
            segment_end = min(y + dash_length, y_end)
            layer_color = (
                min(255, int(glow_base_color.r * pulse_brightness)),
                min(255, int(glow_base_color.g * pulse_brightness)),
                min(255, int(glow_base_color.b * pulse_brightness)),
                alpha
            )
            pygame.draw.line(glow_surf, layer_color, (x, y), (x, segment_end), width + int(offset))
            y += dash_length + gap_length

    if glow_intensity > 1:
        scaled = pygame.transform.smoothscale(glow_surf, (surface.get_width()//2, surface.get_height()//2))
        glow_surf = pygame.transform.smoothscale(scaled, surface.get_size())

    surface.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

def draw_fft_spectrum(surface):
    global spectrum_data, peak_hold, peak_decay_timer, current_energy, stream_audio, mute

    current_energy = 0.0

    # Check mute first - if muted, skip audio processing
    if mute:
        spectrum_data = np.zeros(LOG_BINS)
        current_energy = 0.0
    elif audio_active and stream_audio:
        try:
            data = stream_audio.read(CHUNK, exception_on_overflow=False)
            audio_np = np.frombuffer(data, dtype=np.int16).astype(np.float32)
            audio_np *= np.hanning(len(audio_np))

            fft_vals = np.abs(np.fft.rfft(audio_np))
            fft_freqs = np.fft.rfftfreq(len(audio_np), 1.0 / RATE)
            fft_db = 20 * np.log10(fft_vals + 1e-8)

            bin_magnitudes = np.zeros(LOG_BINS)
            for i in range(LOG_BINS):
                mask = (fft_freqs >= bin_edges[i]) & (fft_freqs < bin_edges[i+1])
                if np.any(mask):
                    bin_magnitudes[i] = np.mean(fft_db[mask])
                else:
                    bin_magnitudes[i] = -100

            bin_magnitudes = np.clip((bin_magnitudes + 100) / 100.0, 0, 1)
            spectrum_data = bin_magnitudes
            current_energy = np.mean(spectrum_data)

        except Exception as e:
            print(f"Audio processing error: {e}")
            spectrum_data = np.random.rand(LOG_BINS) * 0.3
            current_energy = np.mean(spectrum_data)
    else:
        spectrum_data = np.random.rand(LOG_BINS) * 0.6 + 0.2
        current_energy = np.mean(spectrum_data)

    # Update peak hold
    for i in range(LOG_BINS):
        if spectrum_data[i] > peak_hold[i]:
            peak_hold[i] = spectrum_data[i]
            peak_decay_timer[i] = 0.0
        else:
            peak_decay_timer[i] += 1/60.0
            if peak_decay_timer[i] > 0.5:
                peak_hold[i] = max(peak_hold[i] - DECAY_RATE, 0)

    if current_energy < 0.05:
        for i in range(LOG_BINS):
            peak_decay_timer[i] += 1/60.0
        if peak_decay_timer[0] > HOLD_TIMEOUT:
            peak_hold.fill(0)
            peak_decay_timer.fill(0)

    # Draw bars
    bar_width = WIDTH // (LOG_BINS + 2)
    for i in range(LOG_BINS):
        x = (i + 1) * bar_width
        h_current = int(spectrum_data[i] * SPECTRUM_HEIGHT)
        h_peak = int(peak_hold[i] * SPECTRUM_HEIGHT)

        color = (255, max(100 - h_current, 20), max(100 - h_current, 20))
        pygame.draw.rect(surface, color, (x, 380 - h_current, bar_width-4, h_current), border_radius=3)

        if h_peak > 0:
            pygame.draw.line(surface, PEAK_HOLD_COLOR, (x, 380 - h_peak), (x + bar_width-4, 380 - h_peak), 2)

        # Peak labels
        if peak_hold[i] > LABEL_THRESHOLD and h_peak > 0:
            db_approx = 20 * np.log10(peak_hold[i] + 1e-8)
            db_text = f"{int(db_approx)} dB" if db_approx > DB_MIN else "< -60 dB"
            label = f_tiny.render(db_text, True, WHITE)
            label_rect = label.get_rect(midtop=(x + (bar_width-4)/2, 380 - h_peak - 18))
            shadow = f_tiny.render(db_text, True, (0, 0, 0))
            surface.blit(shadow, (label_rect.x + 1, label_rect.y + 1))
            surface.blit(label, label_rect)

    # Octave grid lines
    spectrum_top = 380 - SPECTRUM_HEIGHT
    spectrum_bottom = 380

    for octave_hz in OCTAVE_FREQS:
        if octave_hz < F_MIN or octave_hz > F_MAX:
            continue

        bin_index = np.argmin(np.abs(log_freqs - octave_hz))
        x_pos = int((bin_index + 0.5) * bar_width) + (bar_width // 2)

        draw_dashed_vertical_line_glow(
            surface,
            x_pos,
            spectrum_top,
            spectrum_bottom,
            dash_length=12,
            gap_length=8,
            width=1,
            glow_intensity=4
        )

        if octave_hz >= 1000:
            lbl_text = f"{int(octave_hz//1000)}k"
        else:
            lbl_text = f"{int(octave_hz)}"
        lbl = f_tiny.render(lbl_text, True, (100, 100, 120))
        lbl_rect = lbl.get_rect(midtop=(x_pos, spectrum_bottom + 4))
        surface.blit(lbl, lbl_rect)

    # Frequency axis labels
    label_y = 380 + SPECTRUM_HEIGHT + 20
    for target_hz, text in FREQUENCY_LABELS:
        bin_index = np.argmin(np.abs(log_freqs - target_hz))
        x_pos = int((bin_index + 0.5) * bar_width) + (bar_width // 2)
        lbl = f_tiny.render(text, True, (180, 180, 220))
        lbl_rect = lbl.get_rect(midtop=(x_pos, label_y))
        shadow = f_tiny.render(text, True, (0, 0, 0))
        surface.blit(shadow, (lbl_rect.x + 1, lbl_rect.y + 1))
        surface.blit(lbl, lbl_rect)

    scale_text = f"~{F_MIN:.0f} Hz → {F_MAX/1000:.0f} kHz (log scale)"
    scale_lbl = f_tiny.render(scale_text, True, (120, 120, 120))
    surface.blit(scale_lbl, (WIDTH//2 - scale_lbl.get_width()//2, label_y + 25))

def draw_stats(surface):
    """Draw system statistics"""
    for i, (key, val) in enumerate(temp_levels.items()):
        y = 620 + i * 30
        color = GREEN if val < 60 else YELLOW if val < 80 else RED
        pygame.draw.rect(surface, color, (WIDTH - 220, y, 180, 24), 2)
        txt = f_small.render(f"{key}: {val:.1f}%", True, WHITE)
        surface.blit(txt, (WIDTH - 210, y + 4))

def draw_agents(surface):
    """Draw agent status panel"""
    pygame.draw.rect(surface, GRAY, (WIDTH - 180, 20, 160, 280), 1)
    txt = f_small.render("ACTIVE AGENTS", True, GREEN)
    surface.blit(txt, (WIDTH - 170, 30))
    for i, name in enumerate(active_agents):
        pygame.draw.circle(surface, (80, 180, 255), (WIDTH - 140, 70 + i*45), 18)
        txt = f_tiny.render(name[:3], True, WHITE)
        surface.blit(txt, (WIDTH - 150, 90 + i*45))

# Main loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_m:
                mute = not mute
            if event.key == pygame.K_l:
                locked = not locked
            if event.key == pygame.K_F1:
                cursor_zoom = not cursor_zoom
            if event.key == pygame.K_r:
                peak_hold.fill(0)
                peak_decay_timer.fill(0)
                PEAK_RESET_FLASH = FLASH_DURATION_RESET

    # Pulse & energy calculations
    pulse_phase += BASE_PULSE_SPEED / 60.0
    baseline_pulse = 0.7 + 0.3 * np.sin(pulse_phase)
    energy_boost = MIN_ENERGY_FLOOR + (current_energy * ENERGY_BOOST_FACTOR)
    energy_boost = min(energy_boost, 2.5)
    pulse_factor = baseline_pulse * energy_boost

    # Flash trigger
    if energy_boost > EXTREME_PEAK_THRESHOLD and flash_timer <= 0:
        flash_timer = FLASH_DURATION
        flash_intensity = 1.0

    if flash_timer > 0:
        flash_timer -= 1/60.0
        flash_intensity = flash_timer / FLASH_DURATION

    # Shake trigger
    if energy_boost > EXTREME_PEAK_THRESHOLD and shake_timer <= 0:
        shake_timer = SHAKE_DURATION
        shake_start_time = time.time()

    if shake_timer > 0:
        elapsed = time.time() - shake_start_time
        shake_timer = max(0, SHAKE_DURATION - elapsed)
        progress = 1.0 - (shake_timer / SHAKE_DURATION)
        intensity = SHAKE_INTENSITY_MAX * (1.0 - progress**1.8)

        if intensity > 0.5:
            t = elapsed * SHAKE_SPEED
            nx = t + 100.0
            ny = t * 0.7 + 300.0

            offset_x = fbm_2d(nx, ny, H=SHAKE_HURST, octaves=6, lacunarity=2.1) * 2 - 1
            offset_y = fbm_2d(nx + 500, ny + 700, H=SHAKE_HURST, octaves=6, lacunarity=2.1) * 2 - 1

            shake_offset = (int(offset_x * intensity), int(offset_y * intensity))
        else:
            shake_offset = (0, 0)
    else:
        shake_offset = (0, 0)

    # Decay peak reset flash
    if PEAK_RESET_FLASH > 0:
        PEAK_RESET_FLASH -= 1/60.0

    # Draw to buffer
    ui_buffer.fill(BLACK)

    draw_glowing_scanner(ui_buffer)
    draw_fft_spectrum(ui_buffer)
    draw_stats(ui_buffer)
    draw_agents(ui_buffer)
    draw_scanlines(ui_buffer)

    # Vignette
    if vignette_surf:
        current_vignette_strength = VIGNETTE_STRENGTH_BASE + \
            (VIGNETTE_STRENGTH_FLASH - VIGNETTE_STRENGTH_BASE) * flash_intensity
        vignette_surf.set_alpha(int(255 * current_vignette_strength))
        ui_buffer.blit(vignette_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    # Flash overlay
    if flash_intensity > 0:
        flash_base = pygame.Color(GRID_COLOR_HIGH)
        flash_color = flash_base.lerp(pygame.Color(255, 255, 255), FLASH_WHITE_MIX)
        alpha = int(flash_intensity * 90)

        flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        center = (WIDTH // 2, HEIGHT // 2)
        for r in range(0, max(WIDTH, HEIGHT), 5):
            r_alpha = int(alpha * (1 - (r / max(WIDTH, HEIGHT))**1.5))
            pygame.draw.circle(flash_surf, (*flash_color[:3], r_alpha), center, r)

        ui_buffer.blit(flash_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # Peak reset flash
    if PEAK_RESET_FLASH > 0:
        alpha = int(255 * (PEAK_RESET_FLASH / FLASH_DURATION_RESET))
        txt = f_med.render("PEAKS RESET", True, (255, 255, 255))
        txt_surf = txt.copy()
        txt_surf.set_alpha(alpha)
        ui_buffer.blit(txt_surf, (WIDTH//2 - txt.get_width()//2, 100))

    # Cursor zoom
    if cursor_zoom:
        mx, my = pygame.mouse.get_pos()
        pygame.draw.circle(ui_buffer, (255, 60, 60, 80), (mx, my), 100, 4)

    # Blit buffer to screen with shake
    screen.fill(BLACK)
    screen.blit(ui_buffer, shake_offset)

    pygame.display.flip()
    clock.tick(60)

# Cleanup
if audio_active and stream_audio:
    stream_audio.stop_stream()
    stream_audio.close()
    p_audio.terminate()

save_state()
pygame.quit()
sys.exit()
