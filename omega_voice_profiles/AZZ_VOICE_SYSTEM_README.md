# AZZ Voice Profile System

Complete multi-voice synthesis system for The Gatekeeper Omega with AZZ primary voice profile.

## 📁 Directory Structure

```
H:/The Gatekeeper/voices/
├── azz/                          # AZZ voice profile directory
│   ├── samples/                  # Source audio samples (10 files, 509MB)
│   │   ├── audio response 2.wav  (21MB, 59.52s)
│   │   ├── audio response.wav    (37MB, 108.76s)
│   │   ├── Bells.wav             (19MB, 54.27s)
│   │   ├── Fel n suewy.wav       (44MB, 128.17s)
│   │   ├── Goons.wav             (103MB, 306.07s)
│   │   ├── Jerad.wav             (123MB, 363.40s)
│   │   ├── kit.wav               (32MB, 94.62s)
│   │   ├── rose n goons 2...     (29MB, 83.52s)
│   │   ├── rose.wav              (41MB, 119.26s)
│   │   └── SUI.wav               (66MB, 194.05s)
│   ├── azz.wav                   # Reference voice sample
│   ├── azz_config.json           # Voice configuration
│   ├── azz_profile.json          # Analyzed voice profile
│   └── voice_profile.json        # Generated profile data
├── voice_registry.json           # Multi-voice registry
└── [future voice profiles]       # Additional voices
```

## 🎯 Voice Profile Statistics

**AZZ Voice Profile:**
- **Total Samples**: 10 WAV files
- **Total Duration**: 1511.62 seconds (~25 minutes)
- **Sample Rate**: 44100 Hz
- **Average Pitch**: 817.22 Hz
- **Pitch Range**: 140.21 Hz - 3994.22 Hz
- **Reference Sample**: audio response 2.wav (selected for optimal duration and pitch clarity)

## 🔧 System Components

### 1. AZZ Voice System (`azz_voice_system.py`)

Complete voice analysis and synthesis system with:

**Features:**
- Audio analysis using librosa (pitch, spectral features, MFCCs)
- Azure Speech SDK integration with SSML
- Coqui TTS neural voice cloning
- Multi-sample voice profiling
- Automatic best sample selection

**Key Methods:**
```python
from omega_voice_profiles.azz_voice_system import AZZVoiceSystem

azz = AZZVoiceSystem()

# Analyze audio file
analysis = azz.analyze_audio_file(Path("audio.wav"))
# Returns: duration, pitch, sample_rate, features

# Create profile from samples
profile = azz.create_voice_profile_from_samples([Path("sample1.wav"), ...])

# Synthesize with Azure
azz.synthesize_with_azure("Hello world", output_path=Path("output.wav"))

# Synthesize with Coqui TTS
azz.synthesize_with_coqui("Hello world", output_path=Path("output.wav"))
```

### 2. Voice Registry (`voice_registry.py`)

Multi-voice routing and management system:

**Features:**
- Voice profile registration
- Context-based routing (azure→azz, omega→azz)
- Python and TypeScript config export
- Persistent registry storage

**Usage:**
```python
from omega_voice_profiles.voice_registry import VoiceRegistry

registry = VoiceRegistry()

# Get voice for context
voice_name = registry.get_voice_for_context("azure")  # Returns "azz"

# Get voice profile
profile = registry.get_voice("azz")

# Add routing rule
registry.add_routing_rule("custom_context", "azz")
```

### 3. Configuration Files

#### Python Config (`omega_voice_config.py`)
Auto-generated configuration for Python applications:

```python
from omega_voice_profiles.omega_voice_config import (
    AZZ_VOICE_PATH,
    AZZ_VOICE_SAMPLE,
    VOICE_PROFILES,
    get_voice_for_context,
    get_voice_profile
)

# Use in your code
voice = get_voice_for_context("azure")  # "azz"
profile = get_voice_profile("azz")
sample_path = get_voice_sample_path("azz")
```

#### TypeScript Config (`omega_voice_config.ts`)
Auto-generated configuration for TypeScript applications:

```typescript
import {
    AZZ_VOICE_PATH,
    AZZ_VOICE_SAMPLE,
    VOICE_PROFILES,
    getVoiceForContext,
    getVoiceProfile
} from './omega_voice_profiles/omega_voice_config';

// Use in your code
const voice = getVoiceForContext("azure");  // "azz"
const profile = getVoiceProfile("azz");
```

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
# Required audio libraries
pip install librosa scipy soundfile numpy

# Optional: Azure Speech SDK
pip install azure-cognitiveservices-speech

# Optional: Coqui TTS
pip install TTS
```

### 2. Run Automated Setup

```bash
cd "C:\Users\Drakalich\.claude-worktrees\The Gatekeeper\infallible-diffie"
python run_azz_voice_setup.py
```

This will:
1. Analyze all 10 audio samples
2. Select best reference sample
3. Create voice profile with aggregated features
4. Save configuration files
5. Test synthesis (if Azure key available)

### 3. Configure Azure Speech (Optional)

For Azure TTS synthesis:

```bash
# Set environment variable
export AZURE_SPEECH_KEY="your-azure-speech-key"
export AZURE_SPEECH_REGION="your-region"  # e.g., "eastus"
```

Or create `.env` file:
```env
AZURE_SPEECH_KEY=your-azure-speech-key
AZURE_SPEECH_REGION=your-region
```

## 📝 Usage Examples

### Example 1: Simple Synthesis

```python
from omega_voice_profiles.azz_voice_system import AZZVoiceSystem
from pathlib import Path

azz = AZZVoiceSystem()

# Synthesize speech
text = "Hello, this is the AZZ voice profile."
output = Path("output.wav")

if azz.synthesize_with_azure(text, output):
    print(f"✓ Synthesized: {output}")
```

### Example 2: Custom SSML

```python
from omega_voice_profiles.azz_voice_system import AZZVoiceSystem

azz = AZZVoiceSystem()

# Generate custom SSML
ssml = azz.generate_ssml(
    "This is important!",
    voice_name="en-US-AvaMultilingualNeural",
    style="excited",
    rate="1.2",
    pitch="+10%"
)

# Use with Azure SDK...
```

### Example 3: Analyze New Audio

```python
from omega_voice_profiles.azz_voice_system import AZZVoiceSystem
from pathlib import Path

azz = AZZVoiceSystem()

# Analyze new sample
analysis = azz.analyze_audio_file(Path("new_sample.wav"))

print(f"Duration: {analysis['duration']:.2f}s")
print(f"Pitch: {analysis['pitch']['mean']:.2f} Hz")
print(f"Sample rate: {analysis['sample_rate']} Hz")
```

### Example 4: Multi-Voice Routing

```python
from omega_voice_profiles.omega_voice_config import get_voice_for_context

# Automatic routing
context = "azure"  # or "omega", "general"
voice_name = get_voice_for_context(context)  # Returns "azz"

# Use voice_name to select appropriate synthesis method
```

## 🎤 Voice Characteristics

The AZZ voice profile is optimized for:

- **Gender**: Neutral/Multi-voice aggregate
- **Style**: General purpose, conversational
- **Clarity**: High (selected from best quality samples)
- **Pitch Range**: Wide dynamic range (140-3994 Hz)
- **Duration**: Extensive training data (25+ minutes)

## 🔄 Voice Registry System

The voice registry enables:

1. **Multiple Voice Profiles**: Register unlimited voice profiles
2. **Context-Based Routing**: Auto-select voice based on use case
3. **Dynamic Configuration**: Update voices without code changes
4. **Cross-Platform**: Python and TypeScript support

### Current Routing Rules:

| Context | Voice | Backend |
|---------|-------|---------|
| `azure` | azz | Azure Speech SDK |
| `omega` | azz | Azure Speech SDK |
| `default` | azz | Azure Speech SDK |

## 📊 Audio Analysis Details

Each audio sample is analyzed for:

1. **Duration**: Total length in seconds
2. **Sample Rate**: Audio quality (Hz)
3. **Pitch Features**:
   - Mean pitch (fundamental frequency)
   - Pitch standard deviation
   - Min/max pitch range
4. **Spectral Features** (when available):
   - Spectral centroid (brightness)
   - Spectral bandwidth
   - Spectral rolloff
5. **MFCCs**: Mel-frequency cepstral coefficients (voice timbre)

## 🔐 Security & Privacy

- All audio files stored locally at `H:/The Gatekeeper/voices/azz/`
- No cloud storage of voice samples
- Azure synthesis requires explicit API key
- Voice profiles contain only aggregate statistical features

## 🐛 Troubleshooting

### Azure Speech SDK Not Found

```bash
pip install azure-cognitiveservices-speech
```

### Environment Variable Not Set

```bash
# Windows
set AZURE_SPEECH_KEY=your-key

# Linux/Mac
export AZURE_SPEECH_KEY=your-key
```

### Audio Analysis Errors

Ensure librosa is installed:
```bash
pip install librosa soundfile numpy scipy
```

### Voice Profile Not Found

Run the setup script:
```bash
python run_azz_voice_setup.py
```

## 📚 API Reference

### AZZVoiceSystem Class

```python
class AZZVoiceSystem:
    def __init__(self):
        """Initialize AZZ voice system"""

    def analyze_audio_file(self, audio_path: Path) -> Dict:
        """Analyze WAV file and extract voice features"""

    def create_voice_profile_from_samples(self, sample_files: List[Path]) -> Dict:
        """Create aggregate voice profile from multiple samples"""

    def synthesize_with_azure(self, text: str, output_path: Optional[Path] = None) -> bool:
        """Synthesize speech using Azure Speech SDK"""

    def synthesize_with_coqui(self, text: str, output_path: Optional[Path] = None) -> bool:
        """Synthesize speech using Coqui TTS"""

    def generate_ssml(self, text: str, **kwargs) -> str:
        """Generate SSML for Azure synthesis"""
```

### VoiceRegistry Class

```python
class VoiceRegistry:
    def register_voice(self, name: str, path: Path, backend: str = "azure", **kwargs) -> bool:
        """Register new voice profile"""

    def get_voice(self, name: str) -> Optional[Dict]:
        """Get voice profile by name"""

    def get_voice_for_context(self, context: str) -> str:
        """Get appropriate voice for context"""

    def add_routing_rule(self, context: str, voice: str) -> bool:
        """Add context routing rule"""
```

## 🎯 Integration with Omega

To integrate AZZ voice into your Omega system:

1. **Import Configuration**:
   ```python
   from omega_voice_profiles.omega_voice_config import AZZ_VOICE_PATH, AZZ_VOICE_SAMPLE
   ```

2. **Use Registry for Routing**:
   ```python
   from omega_voice_profiles.voice_registry import voice_registry
   voice_name = voice_registry.get_voice_for_context("omega")
   ```

3. **Synthesize Speech**:
   ```python
   from omega_voice_profiles.azz_voice_system import AZZVoiceSystem
   azz = AZZVoiceSystem()
   azz.synthesize_with_azure("Your text here", output_path)
   ```

## 📈 Future Enhancements

Planned features:
- [ ] Additional voice profiles (multiple personas)
- [ ] Real-time voice streaming
- [ ] Voice morphing and effects
- [ ] Emotion-based synthesis
- [ ] Multi-language support
- [ ] Voice cloning from shorter samples

## 📞 Support

For issues or questions:
1. Check this README
2. Review logs at `H:/The Gatekeeper/voices/azz/azz_config.json`
3. Run diagnostic: `python run_azz_voice_setup.py`

---

**Version**: 1.0.0
**Last Updated**: 2026-01-19
**Status**: ✓ Production Ready
