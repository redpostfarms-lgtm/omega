# OMEGA PWA

A voice-activated AI assistant with a classic 3-bar LED voice box display and scanner animation.

## Features

- **3-Bar LED Voice Box** - Authentic VU meter style display that reacts to speech
- **Scanner Animation** - Sweeping red light effect
- **Voice Recognition** - Talk using Web Speech API
- **Text-to-Speech** - Responses with synthesized voice
- **PWA Install** - Add to home screen for app-like experience
- **QR Code Install** - Scan to install on other devices
- **Offline Support** - Works without internet via Service Worker

## Quick Start

### 1. Install Dependencies

```bash
pip install flask Pillow --break-system-packages
```

### 2. Generate Icons

```bash
python generate_icons.py
```

### 3. Run the Server

```bash
python server.py
```

### 4. Open in Browser

Navigate to `http://localhost:5000`

## Mobile Testing (HTTPS Required)

PWA features require HTTPS. For local testing on mobile:

### Using ngrok (Recommended)

```bash
# Install ngrok from https://ngrok.com
ngrok http 5000
# Use the https:// URL provided
```

## Project Structure

```
omega-pwa/
├── index.html          # Main app (HTML + CSS + JS)
├── manifest.json       # PWA manifest
├── sw.js              # Service Worker
├── server.py          # Flask development server
├── generate_icons.py  # Icon generator script
├── icons/             # PWA icons (generated)
└── README.md
```

## Voice Box Design

The interface features an authentic 3-bar LED VU meter design:

- **3 horizontal rows** of 20 LED segments each
- **Center-out animation** - LEDs light from center outward based on audio level
- **Metallic bezel** housing with dark panel
- **Red LED glow** effect when active

## Customization

### Change LED Count

In `index.html`, modify:

```javascript
ledsPerRow: 20,  // Number of LEDs per row
rows: 3,         // Number of rows
```

### Change the Voice

```javascript
utterance.rate = 0.95;   // Speed (0.1 - 10)
utterance.pitch = 0.85;  // Pitch (0 - 2)
```

### Connect to AI Backend

Replace `generateResponse()` with your API:

```javascript
async generateResponse(input) {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
    });
    const data = await response.json();
    return data.reply;
}
```

## Browser Support

| Feature | Chrome | Firefox | Safari | Edge |
|---------|--------|---------|--------|------|
| PWA Install | ✅ | ⚠️ | ⚠️ | ✅ |
| Speech Recognition | ✅ | ❌ | ⚠️ | ✅ |
| Text-to-Speech | ✅ | ✅ | ✅ | ✅ |
| Service Worker | ✅ | ✅ | ✅ | ✅ |

## License

MIT License
