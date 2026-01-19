#!/usr/bin/env python3
"""
Omega Multi-AI Automation Orchestrator
Runs silently with elevated privileges via Task Scheduler
"""
import os
import sys
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configure logging (runs headlessly, log to file)
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "omega_automation.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama not available - local LLM features disabled")

try:
    import win32com.client as win32
    OFFICE_AVAILABLE = True
except ImportError:
    OFFICE_AVAILABLE = False
    logger.warning("pywin32 not available - Office automation disabled")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not available - external AI features disabled")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not available - using environment variables directly")


class LocalLLMClient:
    """Local LLM client (Ollama or OpenAI-compatible API)"""
    
    def __init__(self, model: str = "llama2", base_url: Optional[str] = None):
        self.model = model
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
    def query(self, prompt: str, system: Optional[str] = None) -> str:
        """Query local LLM"""
        if not OLLAMA_AVAILABLE:
            raise RuntimeError("Ollama not available")
        
        try:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            
            response = ollama.chat(model=self.model, messages=messages)
            return response['message']['content']
        except Exception as e:
            logger.error(f"Local LLM query failed: {e}")
            raise


class ExternalAIClient:
    """External AI client (Grok, Claude, GPT, etc.)"""
    
    def __init__(self, api_url: str, api_key: str, model: str = "grok-beta"):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        
    def query(self, prompt: str) -> str:
        """Query external AI"""
        if not REQUESTS_AVAILABLE:
            raise RuntimeError("requests not available")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        try:
            response = requests.post(self.api_url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"External AI query failed: {e}")
            raise


class OfficeAutomation:
    """Microsoft Office automation via COM API (no GUI clicks)"""
    
    def __init__(self):
        if not OFFICE_AVAILABLE:
            raise RuntimeError("pywin32 not available")
        self.excel = None
        self.word = None
        
    def open_excel(self, visible: bool = False):
        """Open Excel application (headless)"""
        try:
            self.excel = win32.Dispatch("Excel.Application")
            self.excel.Visible = visible
            self.excel.DisplayAlerts = False  # Suppress dialogs
            logger.info("Excel application opened")
            return self.excel
        except Exception as e:
            logger.error(f"Failed to open Excel: {e}")
            raise
    
    def process_excel_file(self, file_path: str, process_func):
        """Process Excel file with custom function"""
        if not self.excel:
            self.open_excel(visible=False)
        
        try:
            wb = self.excel.Workbooks.Open(file_path)
            result = process_func(wb)
            wb.Save()
            wb.Close()
            logger.info(f"Processed Excel file: {file_path}")
            return result
        except Exception as e:
            logger.error(f"Excel processing failed: {e}")
            raise
    
    def close_excel(self):
        """Close Excel application"""
        if self.excel:
            try:
                self.excel.Quit()
                self.excel = None
                logger.info("Excel application closed")
            except Exception as e:
                logger.warning(f"Error closing Excel: {e}")
    
    def open_word(self, visible: bool = False):
        """Open Word application (headless)"""
        try:
            self.word = win32.Dispatch("Word.Application")
            self.word.Visible = visible
            self.word.DisplayAlerts = 0  # Suppress dialogs
            logger.info("Word application opened")
            return self.word
        except Exception as e:
            logger.error(f"Failed to open Word: {e}")
            raise
    
    def process_word_document(self, file_path: str, process_func):
        """Process Word document with custom function"""
        if not self.word:
            self.open_word(visible=False)
        
        try:
            doc = self.word.Documents.Open(file_path)
            result = process_func(doc)
            doc.Save()
            doc.Close()
            logger.info(f"Processed Word document: {file_path}")
            return result
        except Exception as e:
            logger.error(f"Word processing failed: {e}")
            raise
    
    def close_word(self):
        """Close Word application"""
        if self.word:
            try:
                self.word.Quit()
                self.word = None
                logger.info("Word application closed")
            except Exception as e:
                logger.warning(f"Error closing Word: {e}")
    
    def cleanup(self):
        """Cleanup all Office applications"""
        self.close_excel()
        self.close_word()


class OmegaOrchestrator:
    """Main orchestrator for multi-AI system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.local_llm = None
        self.external_ai = None
        self.office = None
        
        # Initialize components
        if config.get("local_llm", {}).get("enabled", False):
            llm_config = config["local_llm"]
            self.local_llm = LocalLLMClient(
                model=llm_config.get("model", "llama2"),
                base_url=llm_config.get("base_url")
            )
            logger.info("Local LLM initialized")
        
        if config.get("external_ai", {}).get("enabled", False):
            ai_config = config["external_ai"]
            self.external_ai = ExternalAIClient(
                api_url=ai_config["api_url"],
                api_key=ai_config["api_key"],
                model=ai_config.get("model", "grok-beta")
            )
            logger.info("External AI initialized")
        
        if config.get("office", {}).get("enabled", False):
            try:
                self.office = OfficeAutomation()
                logger.info("Office automation initialized")
            except Exception as e:
                logger.warning(f"Office automation not available: {e}")
    
    def process_task(self, task_description: str) -> Dict[str, Any]:
        """Process a task using available AI agents"""
        logger.info(f"Processing task: {task_description}")
        results = {}
        
        # Step 1: Analyze with local LLM
        if self.local_llm:
            try:
                local_response = self.local_llm.query(
                    prompt=task_description,
                    system="You are Omega, an intelligent assistant. Analyze tasks and provide solutions."
                )
                results["local_llm"] = local_response
                logger.info("Local LLM analysis completed")
            except Exception as e:
                logger.error(f"Local LLM failed: {e}")
        
        # Step 2: Consult external AI
        if self.external_ai:
            try:
                external_response = self.external_ai.query(
                    f"Analyze and provide insights: {task_description}"
                )
                results["external_ai"] = external_response
                logger.info("External AI consultation completed")
            except Exception as e:
                logger.error(f"External AI failed: {e}")
        
        # Step 3: Combine results
        if results:
            combined = self._combine_results(results)
            results["combined"] = combined
        
        return results
    
    def _combine_results(self, results: Dict[str, Any]) -> str:
        """Combine results from multiple AI sources"""
        combined_parts = []
        if "local_llm" in results:
            combined_parts.append(f"Local Analysis: {results['local_llm']}")
        if "external_ai" in results:
            combined_parts.append(f"External Insights: {results['external_ai']}")
        return "\n\n".join(combined_parts)
    
    def process_office_task(self, file_path: str, task_type: str = "excel") -> Dict[str, Any]:
        """Process Office file with AI assistance"""
        if not self.office:
            raise RuntimeError("Office automation not available")
        
        logger.info(f"Processing Office file: {file_path} ({task_type})")
        results = {}
        
        if task_type == "excel":
            def process_excel(wb):
                # Example: Read cell A1, process with AI, write to B1
                sheet = wb.Sheets(1)
                value = sheet.Cells(1, 1).Value
                
                # Process with AI
                if self.local_llm:
                    processed = self.local_llm.query(f"Analyze this data: {value}")
                    sheet.Cells(1, 2).Value = processed
                    results["processed_value"] = processed
                
                return "Excel processing completed"
            
            self.office.process_excel_file(file_path, process_excel)
        
        elif task_type == "word":
            def process_word(doc):
                # Example: Get first paragraph, enhance with AI
                if doc.Paragraphs.Count > 0:
                    text = doc.Paragraphs(1).Range.Text
                    
                    if self.local_llm:
                        enhanced = self.local_llm.query(f"Enhance this text: {text}")
                        results["enhanced_text"] = enhanced
                
                return "Word processing completed"
            
            self.office.process_word_document(file_path, process_word)
        
        return results
    
    def cleanup(self):
        """Cleanup resources"""
        if self.office:
            self.office.cleanup()


def load_config() -> Dict[str, Any]:
    """Load configuration from file or environment"""
    config_file = Path(__file__).parent / "omega_automation_config.json"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    
    # Default configuration
    return {
        "local_llm": {
            "enabled": os.getenv("LOCAL_LLM_ENABLED", "false").lower() == "true",
            "model": os.getenv("LOCAL_LLM_MODEL", "llama2"),
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        },
        "external_ai": {
            "enabled": os.getenv("EXTERNAL_AI_ENABLED", "false").lower() == "true",
            "api_url": os.getenv("EXTERNAL_AI_URL", ""),
            "api_key": os.getenv("EXTERNAL_AI_KEY", ""),
            "model": os.getenv("EXTERNAL_AI_MODEL", "grok-beta")
        },
        "office": {
            "enabled": os.getenv("OFFICE_ENABLED", "true").lower() == "true"
        },
        "tasks": []
    }


def main():
    """Main entry point"""
    logger.info("Omega Automation Orchestrator starting...")
    
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded")
        
        # Initialize orchestrator
        orchestrator = OmegaOrchestrator(config)
        logger.info("Orchestrator initialized")
        
        # Process configured tasks
        tasks = config.get("tasks", [])
        if tasks:
            for task in tasks:
                try:
                    if task.get("type") == "office":
                        result = orchestrator.process_office_task(
                            task["file_path"],
                            task.get("task_type", "excel")
                        )
                    else:
                        result = orchestrator.process_task(task["description"])
                    
                    logger.info(f"Task completed: {task.get('name', 'unnamed')}")
                except Exception as e:
                    logger.error(f"Task failed: {e}")
        
        # Cleanup
        orchestrator.cleanup()
        logger.info("Omega Automation Orchestrator completed")
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
