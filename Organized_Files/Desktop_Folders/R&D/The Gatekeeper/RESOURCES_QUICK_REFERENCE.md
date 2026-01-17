# Free Resources - Quick Reference

**Red Post Farms, LLC | Copyright (c) 2025-2026 | All Rights Reserved**

Quick lookup for free, open-source resources to improve The Gatekeeper system.

---

## 🎯 Top 3 High-Impact Improvements

### 1. **Scrapy** → Web Scraping (Runtime: 95% → 98%)
```bash
pip install scrapy
```text
- **Why:** Built-in retry logic, concurrent requests, better error handling
- **Repo:** https://github.com/scrapy/scrapy
- **Impact:** 20-30% fewer scraping failures

### 2. **Vosk** → Offline Voice Recognition
```bash
pip install vosk
# Download models from: https://alphacephei.com/vosk/models
```text
- **Why:** 100% offline, no API keys, low latency
- **Repo:** https://github.com/alphacep/vosk-api
- **Impact:** Eliminates Google API dependency

### 3. **ChromaDB** → Vector Knowledge Storage
```bash
pip install chromadb sentence-transformers
```text
- **Why:** Semantic search, better knowledge retrieval
- **Repo:** https://github.com/chroma-core/chroma
- **Impact:** Faster, more accurate knowledge lookup

---

## 📋 Component-Based Resources

### Web Scraping
| Library | Install | Purpose | License |
| --------- | --------- | --------- | --------- |
| **Scrapy** | `pip install scrapy` | Framework (retries, concurrency) | BSD-3 |
| **Playwright** | `pip install playwright` | JavaScript rendering | Apache 2.0 |
| **httpx** | `pip install httpx` | Async HTTP client | BSD |
| **lxml** | `pip install lxml` | Fast HTML parser | BSD |

### Voice Recognition (All Offline)
| Library | Install | Purpose | License |
| --------- | --------- | --------- | --------- |
| **Vosk** | `pip install vosk` | Offline STT (primary) | Apache 2.0 |
| **SpeechBrain** | `pip install speechbrain` | Voiceprint biometrics | Apache 2.0 |
| **Coqui TTS** | `pip install TTS` | Text-to-speech | MPL 2.0 |
| **DeepSpeech** | `pip install deepspeech` | Mozilla STT (alternative) | MPL 2.0 |

### Knowledge Base
| Library | Install | Purpose | License |
| --------- | --------- | --------- | --------- |
| **ChromaDB** | `pip install chromadb` | Vector database | Apache 2.0 |
| **FAISS** | `pip install faiss-cpu` | Fast similarity search | MIT |
| **Sentence Transformers** | `pip install sentence-transformers` | Text embeddings | Apache 2.0 |

### Agent Systems
| Library | Install | Purpose | License |
| --------- | --------- | --------- | --------- |
| **CrewAI** | `pip install crewai` | Multi-agent framework | MIT |
| **LangChain** | `pip install langchain` | Agent orchestration | MIT |
| **AutoGen** | `pip install pyautogen` | Conversational agents | MIT |

### Hardware Monitoring
| Library | Install | Purpose | License |
| --------- | --------- | --------- | --------- |
| **pySMART** | `pip install pySMART` | Disk health (SMART) | LGPL |
| **nvidia-ml-py** | `pip install nvidia-ml-py` | GPU monitoring | BSD |

### Document Generation
| Library | Install | Purpose | License |
| --------- | --------- | --------- | --------- |
| **ReportLab** | `pip install reportlab` | PDF generation | BSD |
| **WeasyPrint** | `pip install weasyprint` | HTML→PDF | BSD-3 |

### Security
| Library | Install | Purpose | License |
| --------- | --------- | --------- | --------- |
| **cryptography** | `pip install cryptography` | Encryption | Apache 2.0/BSD |
| **keyring** | `pip install keyring` | Credential storage | MIT |

---

## 🚀 Quick Install All (Recommended)

```bash
# High Priority
pip install scrapy vosk chromadb sentence-transformers

# Medium Priority
pip install speechbrain crewai langchain lxml httpx

# Optional
pip install playwright reportlab weasyprint cryptography keyring
```text

---

## 📁 Integration Points

| Component | Current | Recommended Upgrade | File to Edit |
| ----------- | --------- | --------------------- | -------------- |
| Web Scraping | `requests` + `BeautifulSoup` | **Scrapy** | `planetary_search.py` |
| Voice Recognition | `speech_recognition` (Google API) | **Vosk** | `voice_listener.py` |
| Voiceprint Auth | Custom numpy | **SpeechBrain** | `voiceprint_auth.py` |
| Knowledge Base | JSON files | **ChromaDB** | `brain_prime.py` |
| Agent Council | Custom | **CrewAI** | `agent_council_v2.py` |
| TTS | `pyttsx3` | **Coqui TTS** | `voice_tuner.py` |
| Hardware | `psutil`, `GPUtil` | Add **pySMART** | `hardware_scan.py` |
| PDFs | `python-docx` → PDF | **ReportLab** | `white_page.py` |

---

## 🔗 All Repository Links

### Web Scraping
- Scrapy: https://github.com/scrapy/scrapy
- Playwright: https://github.com/microsoft/playwright
- httpx: https://github.com/encode/httpx
- lxml: https://github.com/lxml/lxml

### Voice
- Vosk: https://github.com/alphacep/vosk-api
- SpeechBrain: https://github.com/speechbrain/speechbrain
- Coqui TTS: https://github.com/coqui-ai/TTS
- DeepSpeech: https://github.com/mozilla/DeepSpeech

### Knowledge
- ChromaDB: https://github.com/chroma-core/chroma
- FAISS: https://github.com/facebookresearch/faiss
- Sentence Transformers: https://github.com/UKPLab/sentence-transformers

### Agents
- CrewAI: https://github.com/joaomdmoura/crewAI
- LangChain: https://github.com/langchain-ai/langchain
- AutoGen: https://github.com/microsoft/autogen

### Documents
- ReportLab: https://github.com/MrBitcoin/reportlab
- WeasyPrint: https://github.com/Kozea/WeasyPrint

---

**For detailed information, see:** `FREE_RESOURCES_COMPREHENSIVE.md`

**Red Post Farms, LLC - 2025-2026 | All Rights Reserved**

