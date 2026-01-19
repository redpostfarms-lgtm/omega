# 🚀 Complete Dependency Installation Guide

## System Status Check
```powershell
C:\Users\Drakalich\check-status.ps1
```

---

## 🔧 Core System Tools

### Essential Build Tools
```powershell
# Windows Build Tools for Python
winget install Microsoft.VisualStudio.2022.BuildTools
```

```powershell
# Git (if not installed)
winget install Git.Git
```

```powershell
# Python 3.11 (recommended for TTS compatibility)
winget install Python.Python.3.11
```

```powershell
# Node.js LTS
winget install OpenJS.NodeJS.LTS
```

---

## 🐋 Container & Orchestration Tools

### Docker & Kubernetes
✅ Docker Desktop - **Already installed**
✅ kubectl - **Already installed** (v1.35.0)

```powershell
# Helm (Kubernetes package manager)
choco install kubernetes-helm
```

```powershell
# Minikube (local Kubernetes cluster)
choco install minikube
```

```powershell
# Docker Compose standalone (if needed)
winget install Docker.DockerCompose
```

---

## 🐍 Python Dependencies

### Core Python Packages
```powershell
cd "H:\The Gatekeeper"
pip install --upgrade pip setuptools wheel
```

```powershell
# Install all requirements
pip install -r requirements.txt
```

```powershell
# Install enhanced requirements (includes all optional)
pip install -r requirements_enhanced.txt
```

### Development Tools
```powershell
# Code formatting & linting
pip install black ruff mypy
```

```powershell
# Testing framework
pip install pytest pytest-asyncio pytest-cov pytest-mock
```

---

## 🎯 AI/ML Enhancement Packages

### GPU Acceleration (if NVIDIA GPU available)
```powershell
# CUDA Toolkit 12.1
winget install NVIDIA.CUDA
```

```powershell
# PyTorch with CUDA support
pip install torch==2.5.1+cu121 torchaudio==2.5.1+cu121 --index-url https://download.pytorch.org/whl/cu121
```

```powershell
# Optional: vLLM for 5-10x faster inference
pip install vllm
```

### Advanced LLM Tools
```powershell
# Hugging Face ecosystem
pip install transformers datasets tokenizers evaluate
```

```powershell
# LangChain for LLM orchestration
pip install langchain langchain-community langchain-openai
```

```powershell
# LlamaIndex for RAG applications
pip install llama-index llama-index-vector-stores-faiss
```

```powershell
# Semantic similarity & embeddings
pip install sentence-transformers faiss-cpu
```

```powershell
# OpenAI API
pip install openai>=1.0.0
```

```powershell
# Anthropic Claude API
pip install anthropic
```

```powershell
# Google AI
pip install google-generativeai
```

---

## 📊 Data Science & Visualization

```powershell
# Core data science
pip install pandas numpy scipy scikit-learn
```

```powershell
# Visualization
pip install matplotlib plotly seaborn
```

```powershell
# Jupyter ecosystem
pip install jupyter jupyterlab notebook ipywidgets
```

```powershell
# Data validation
pip install pandera great-expectations
```

---

## 🔊 Audio & Speech Enhancement

```powershell
# Advanced audio processing
pip install pyannote.audio noisereduce librosa pydub
```

```powershell
# Speech recognition alternatives
pip install vosk whisper openai-whisper
```

```powershell
# Real-time audio
pip install pyaudio sounddevice soundfile
```

```powershell
# Music information retrieval
pip install essentia aubio madmom
```

---

## 🌐 Web & API Development

### Node.js Packages
```powershell
cd "H:\The Gatekeeper"
npm install
```

```powershell
# Express.js web framework
npm install express cors body-parser
```

```powershell
# WebSocket support
npm install ws socket.io
```

```powershell
# API development
npm install axios node-fetch fastify
```

### Python Web Frameworks
```powershell
# FastAPI (async API framework)
pip install fastapi uvicorn[standard] python-multipart
```

```powershell
# Flask (lightweight framework)
pip install flask flask-cors flask-socketio
```

```powershell
# Streamlit (data apps)
pip install streamlit
```

```powershell
# Gradio (ML demos)
pip install gradio
```

---

## 🔐 Security & Authentication

```powershell
# Cryptography & hashing
pip install cryptography bcrypt passlib[bcrypt]
```

```powershell
# JWT authentication
pip install pyjwt[crypto] python-jose[cryptography]
```

```powershell
# OAuth & API auth
pip install authlib httpx-oauth
```

```powershell
# Password management
pip install keyring keyrings.alt
```

---

## 💾 Database & Storage

```powershell
# Redis (in-memory database)
pip install redis hiredis
```

```powershell
# MongoDB
pip install pymongo motor
```

```powershell
# PostgreSQL
pip install psycopg2-binary asyncpg
```

```powershell
# SQLite enhancements
pip install sqlite-utils
```

```powershell
# SQLAlchemy ORM
pip install sqlalchemy alembic
```

```powershell
# Vector databases
pip install chromadb pinecone-client weaviate-client qdrant-client
```

---

## 🔍 Search & Indexing

```powershell
# Elasticsearch
pip install elasticsearch
```

```powershell
# Full-text search
pip install whoosh
```

```powershell
# Document processing
pip install pypdf pdfplumber python-docx python-pptx
```

```powershell
# Web scraping
pip install beautifulsoup4 lxml scrapy selenium playwright
```

```powershell
# Install Playwright browsers
playwright install
```

---

## 📡 Networking & Monitoring

```powershell
# Network analysis
pip install scapy netifaces
```

```powershell
# Monitoring & metrics
pip install prometheus-client grafana-api
```

```powershell
# Logging
pip install structlog loguru python-json-logger
```

```powershell
# Performance profiling
pip install memory-profiler line-profiler py-spy
```

---

## 🎮 UI & Desktop Automation

```powershell
# GUI frameworks
pip install pygame PyQt6 PySide6 tkinter
```

```powershell
# Desktop automation
pip install pyautogui pynput keyboard mouse
```

```powershell
# System tray
pip install pystray
```

```powershell
# Notifications
pip install plyer win10toast
```

---

## 🖥️ System & Hardware Control

```powershell
# System monitoring
pip install psutil py-cpuinfo GPUtil
```

```powershell
# Windows Management
pip install WMI pywin32 winshell
```

```powershell
# RGB lighting control
pip install openrgb-python
```

```powershell
# Hardware monitoring
pip install pySMART sensors
```

---

## 🔄 Async & Concurrency

```powershell
# Async utilities
pip install aiofiles aiohttp aiodns aioredis
```

```powershell
# Task queues
pip install celery redis rq
```

```powershell
# Rate limiting
pip install ratelimit slowapi
```

---

## 📝 Documentation & Code Quality

```powershell
# Documentation
pip install sphinx sphinx-rtd-theme mkdocs mkdocs-material
```

```powershell
# Code quality
pip install pylint flake8 bandit safety
```

```powershell
# Pre-commit hooks
pip install pre-commit
```

```powershell
# Type checking
pip install mypy pyright
```

---

## 🧪 Testing & QA

```powershell
# Testing frameworks
pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-xdist
```

```powershell
# Property-based testing
pip install hypothesis
```

```powershell
# Behavior testing
pip install behave pytest-bdd
```

```powershell
# Load testing
pip install locust
```

---

## 🔧 DevOps & CI/CD Tools

```powershell
# Terraform
choco install terraform
```

```powershell
# Ansible
pip install ansible
```

```powershell
# GitHub CLI
winget install GitHub.cli
```

```powershell
# Azure CLI
winget install Microsoft.AzureCLI
```

```powershell
# AWS CLI
winget install Amazon.AWSCLI
```

---

## 📦 Package Management Tools

```powershell
# Chocolatey (if not installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

```powershell
# pip-tools for dependency management
pip install pip-tools pipdeptree
```

```powershell
# Poetry (alternative package manager)
pip install poetry
```

---

## 🎨 Optional Enhancement Tools

### Code Editors & IDEs
```powershell
# VS Code extensions via CLI
code --install-extension ms-python.python
code --install-extension ms-azuretools.vscode-docker
code --install-extension ms-kubernetes-tools.vscode-kubernetes-tools
code --install-extension GitHub.copilot
code --install-extension eamodio.gitlens
```

### Terminal Enhancements
```powershell
# Windows Terminal
winget install Microsoft.WindowsTerminal
```

```powershell
# PowerShell 7
winget install Microsoft.PowerShell
```

```powershell
# Oh My Posh (terminal theme)
winget install JanDeDobbeleer.OhMyPosh
```

### Productivity Tools
```powershell
# Postman (API testing)
winget install Postman.Postman
```

```powershell
# DBeaver (database client)
winget install dbeaver.dbeaver
```

```powershell
# Redis Desktop Manager
choco install another-redis-desktop-manager
```

---

## 🚀 Quick Install Scripts

### Install Everything Python
```powershell
cd "H:\The Gatekeeper"
pip install -r requirements_enhanced.txt
pip install black ruff mypy pytest pytest-asyncio pytest-cov
pip install langchain langchain-openai sentence-transformers
pip install fastapi uvicorn streamlit gradio
pip install chromadb faiss-cpu
pip install openai anthropic google-generativeai
pip install jupyterlab notebook
```

### Install Everything Node.js
```powershell
cd "H:\The Gatekeeper"
npm install
npm install express axios ws socket.io cors
```

### Install All System Tools
```powershell
# Run as Administrator
winget install Microsoft.VisualStudio.2022.BuildTools
winget install Git.Git
winget install OpenJS.NodeJS.LTS
winget install Microsoft.PowerShell
winget install Microsoft.WindowsTerminal
winget install GitHub.cli
choco install kubernetes-helm
```

---

## ✅ Verification Commands

```powershell
# Check Python installation
python --version
pip list
```

```powershell
# Check Node.js installation
node --version
npm list -g --depth=0
```

```powershell
# Check Docker
docker --version
docker ps
```

```powershell
# Check kubectl
kubectl version --client
```

```powershell
# Check system resources
systeminfo
```

```powershell
# Check GPU (if NVIDIA)
nvidia-smi
```

---

## 📊 Post-Installation

### Run System Tests
```powershell
cd "H:\The Gatekeeper"
pytest tests/
```

### Start Development Environment
```powershell
# Start Docker containers
cd C:\Users\Drakalich\.jupyter
docker compose up -d
```

```powershell
# Start Jupyter Lab
jupyter lab
```

```powershell
# Run status check
C:\Users\Drakalich\check-status.ps1
```

---

## 🆘 Troubleshooting

### If pip install fails with SSL errors
```powershell
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package>
```

### If npm install fails
```powershell
npm config set strict-ssl false
npm install
npm config set strict-ssl true
```

### Clear cache if needed
```powershell
pip cache purge
npm cache clean --force
```

### Reinstall Python packages
```powershell
pip install --force-reinstall --no-cache-dir <package>
```

---

## 📝 Notes

- **Python 3.11** recommended for TTS compatibility (not 3.14)
- **CUDA 12.1** required for GPU acceleration
- Some packages require **Visual Studio Build Tools**
- **Admin privileges** required for some installations
- **Restart required** after installing WSL, Docker, or CUDA

---

**Last Updated:** January 18, 2026
**Environment:** Windows with WSL 2, Docker Desktop, Python 3.11
