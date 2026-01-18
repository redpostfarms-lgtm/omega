# 🌐 OMEGA Tunnel Setup Guide

## Quick Start (For External Phone Access)

If you want to access OMEGA Swarm from **outside your local network** (different Wi-Fi, cellular data), you need a tunnel service like ngrok.

### Option 1: Setup Now

```bash
python setup_tunnel.py setup
```

Follow the prompts to:
1. Get your ngrok account (free): <https://dashboard.ngrok.com/signup>
2. Copy your authtoken: <https://dashboard.ngrok.com/get-started/your-authtoken>
3. Paste it when prompted

### Option 2: Setup Later

The config is ready at `tunnel_config.json`. When you're ready:

```bash
python setup_tunnel.py setup YOUR_TOKEN_HERE
```

Or edit `tunnel_config.json` directly:
```json
{
  "ngrok": {
    "authtoken": "YOUR_ACTUAL_TOKEN_HERE",
    "enabled": true,
    "region": "us"
  }
}
```

Then run:
```bash
python setup_tunnel.py start
```

---

## What This Does

**Without tunnel** (current):
- ✅ Works on same Wi-Fi network (10.0.0.26:5002)
- ❌ Can't access from outside (cellular, different network)

**With tunnel**:
- ✅ Works anywhere with internet
- ✅ Gets public URL like: `https://abc123.ngrok.io`
- ✅ QR codes automatically use tunnel URL
- 🔒 Secure HTTPS connection

---

## Commands

```bash
# Interactive setup wizard
python setup_tunnel.py setup

# Setup with token directly
python setup_tunnel.py setup 2abc123xyz...

# Start tunnel (keep terminal open)
python setup_tunnel.py start

# Check status
python setup_tunnel.py status
```

---

## How It Works

1. **Local Network** (Default - No setup needed)
   - Server: `http://10.0.0.26:5002`
   - Phone must be on same Wi-Fi
   - Fast, no middleman

2. **Tunnel Mode** (After setup)
   - Server still runs locally
   - ngrok creates secure tunnel
   - Public URL: `https://xyz.ngrok.io`
   - QR handler automatically detects and uses tunnel URL
   - Works from anywhere

---

## Integration with OMEGA Swarm

The QR handler (`static/scripts/qr_handler.py`) automatically:
1. Checks for `OMEGA_TUNNEL_URL` environment variable
2. Falls back to network IP (10.0.0.26)
3. Falls back to localhost

**To use tunnel with OMEGA:**

```bash
# Terminal 1: Start tunnel
python setup_tunnel.py start

# Terminal 2: Start OMEGA server
python omega_swarm_server.py
```

QR codes will automatically use the tunnel URL! 📱⚡

---

## Troubleshooting

**"Authentication failed"**
- Run: `python setup_tunnel.py setup YOUR_TOKEN`

**"Can't connect to ngrok"**  
- Check firewall/antivirus
- Try: `.\ngrok.exe http 5002` manually

**"Tunnel URL not detected"**
- Set manually: `$env:OMEGA_TUNNEL_URL = "https://xyz.ngrok.io"`
- Restart server

**Phone can't connect to tunnel URL**
- Make sure OMEGA server is still running on port 5002
- Check ngrok dashboard: <http://127.0.0.1:4040>

---

## Security Note

🔒 ngrok free tier tunnels are public. Anyone with the URL can access your server while it's running. For production use:
- Use ngrok auth (paid)
- Use Cloudflare Tunnel (free, more secure)
- Deploy to proper hosting (Azure, AWS, etc.)

For testing/personal use, ngrok free is fine. The tunnel URL changes each time you restart.
