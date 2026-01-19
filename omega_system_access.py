"""
Omega System Initialization and Access Manager
Loads all installed packages, credentials, and provides unified access
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import importlib

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from omega_credentials import credentials


class OmegaSystemAccess:
    """
    Unified access point for all Omega system capabilities
    Provides access to installed packages, credentials, and configurations
    """

    def __init__(self):
        self.credentials = credentials
        self.installed_packages = {}
        self.capabilities = {}
        self._initialize_system()

    def _initialize_system(self):
        """Initialize and verify all system components"""
        print("=" * 60)
        print("🌟 OMEGA SYSTEM INITIALIZATION")
        print("=" * 60)

        print(f"\n✓ User: {self.credentials.omega_user}")
        print(f"✓ Email: {self.credentials.email}")
        print(f"✓ Git: {self.credentials.git_name} <{self.credentials.git_email}>")

        self._check_ai_ml_packages()

        self._check_data_science_packages()

        self._check_web_packages()

        self._check_database_packages()

        self._check_security_packages()

        print("\n" + "=" * 60)
        print(f"✅ OMEGA READY - {len(self.installed_packages)} packages loaded")
        print("=" * 60 + "\n")

    def _check_ai_ml_packages(self):
        """Check and load AI/ML packages"""
        print("\n🤖 AI/ML Capabilities:")
        ai_packages = {
            "langchain": "LangChain",
            "langchain_openai": "LangChain OpenAI",
            "openai": "OpenAI API",
            "anthropic": "Anthropic Claude",
            "transformers": "Hugging Face Transformers",
            "sentence_transformers": "Sentence Transformers",
            "torch": "PyTorch",
        }
        self._load_packages(ai_packages, "AI/ML")

    def _check_data_science_packages(self):
        """Check and load Data Science packages"""
        print("\n📊 Data Science Capabilities:")
        ds_packages = {
            "pandas": "Pandas",
            "numpy": "NumPy",
            "matplotlib": "Matplotlib",
            "plotly": "Plotly",
            "scipy": "SciPy",
            "sklearn": "Scikit-learn",
        }
        self._load_packages(ds_packages, "Data Science")

    def _check_web_packages(self):
        """Check and load Web Development packages"""
        print("\n🌐 Web Development Capabilities:")
        web_packages = {
            "fastapi": "FastAPI",
            "flask": "Flask",
            "streamlit": "Streamlit",
            "gradio": "Gradio",
            "uvicorn": "Uvicorn",
            "aiohttp": "AIOHTTP",
        }
        self._load_packages(web_packages, "Web")

    def _check_database_packages(self):
        """Check and load Database packages"""
        print("\n💾 Database Capabilities:")
        db_packages = {
            "redis": "Redis",
            "pymongo": "MongoDB",
            "psycopg2": "PostgreSQL",
            "chromadb": "ChromaDB",
            "sqlalchemy": "SQLAlchemy",
        }
        self._load_packages(db_packages, "Database")

    def _check_security_packages(self):
        """Check and load Security packages"""
        print("\n🔐 Security Capabilities:")
        security_packages = {
            "cryptography": "Cryptography",
            "jwt": "PyJWT",
            "jose": "Python-JOSE",
        }
        self._load_packages(security_packages, "Security")

    def _load_packages(self, packages: Dict[str, str], category: str):
        """Load and verify packages"""
        for module_name, display_name in packages.items():
            try:
                module = importlib.import_module(module_name)
                self.installed_packages[module_name] = module
                self.capabilities[display_name] = {
                    "module": module,
                    "category": category,
                    "version": getattr(module, "__version__", "unknown"),
                }
                version = getattr(module, "__version__", "")
                version_str = f" v{version}" if version else ""
                print(f"  ✓ {display_name}{version_str}")
            except ImportError as e:
                print(f"  ✗ {display_name} - Not installed")

    def get_package(self, name: str):
        """Get an installed package by name"""
        return self.installed_packages.get(name)

    def get_capability(self, name: str) -> Optional[Dict[str, Any]]:
        """Get capability information"""
        return self.capabilities.get(name)

    def list_capabilities(self) -> Dict[str, Any]:
        """List all available capabilities"""
        return self.capabilities

    def get_ai_client(self, provider: str = "openai"):
        """
        Get an AI client for the specified provider

        Args:
            provider: 'openai', 'anthropic', or 'huggingface'

        Returns:
            Configured client instance
        """
        api_key = self.credentials.get_api_key(provider)

        if provider == "openai":
            import openai

            client = openai.OpenAI(api_key=api_key) if api_key else None
            return client

        elif provider == "anthropic":
            import anthropic

            client = anthropic.Anthropic(api_key=api_key) if api_key else None
            return client

        elif provider == "huggingface":
            token = self.credentials.get_api_key("huggingface")
            return {"token": token} if token else None

        return None

    def create_web_app(self, framework: str = "fastapi"):
        """
        Create a web application instance

        Args:
            framework: 'fastapi', 'flask', or 'streamlit'

        Returns:
            App instance
        """
        if framework == "fastapi":
            from fastapi import FastAPI

            return FastAPI(title="Omega System API")

        elif framework == "flask":
            from flask import Flask

            return Flask("omega_system")

        return None

    def connect_database(self, db_type: str = "redis", **kwargs):
        """
        Connect to a database

        Args:
            db_type: 'redis', 'mongodb', 'postgres', or 'chromadb'
            **kwargs: Connection parameters

        Returns:
            Database connection/client
        """
        if db_type == "redis":
            import redis

            return redis.Redis(**kwargs)

        elif db_type == "mongodb":
            from pymongo import MongoClient

            return MongoClient(**kwargs)

        elif db_type == "postgres":
            import psycopg2

            return psycopg2.connect(**kwargs)

        elif db_type == "chromadb":
            import chromadb

            return chromadb.Client()

        return None

    def get_credentials(self):
        """Get system credentials"""
        return {
            "user": self.credentials.omega_user,
            "email": self.credentials.email,
            "git_name": self.credentials.git_name,
            "git_email": self.credentials.git_email,
        }

    def system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        return {
            "user": self.credentials.omega_user,
            "email": self.credentials.email,
            "total_packages": len(self.installed_packages),
            "capabilities": list(self.capabilities.keys()),
            "categories": list(set(c["category"] for c in self.capabilities.values())),
        }


omega = OmegaSystemAccess()


if __name__ == "__main__":
    status = omega.system_status()
    print("\n📋 System Status Summary:")
    print(f"   User: {status['user']}")
    print(f"   Email: {status['email']}")
    print(f"   Total Packages: {status['total_packages']}")
    print(f"   Categories: {', '.join(status['categories'])}")
    print(f"\n   Available Capabilities:")
    for cap in sorted(status["capabilities"]):
        print(f"     • {cap}")
