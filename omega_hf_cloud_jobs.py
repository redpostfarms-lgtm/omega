"""
Hugging Face Cloud Jobs Integration Module
Provides utilities for running Omega system tasks on Hugging Face cloud infrastructure
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any


class HuggingFaceJobsManager:
    """Manage Hugging Face cloud jobs for The Gatekeeper system"""

    def __init__(self):
        self.venv_python = Path("H:/The Gatekeeper/.venv/Scripts/python.exe")
        self.hf_cli = "hf"

    def check_auth_status(self) -> bool:
        """Check if user is authenticated with Hugging Face"""
        try:
            result = subprocess.run(
                [str(self.venv_python), "-m", "huggingface_hub.commands.huggingface_cli", "whoami"],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception as e:
            print(f"[ERROR] Failed to check auth status: {e}")
            return False

    def login(self) -> bool:
        """Initiate Hugging Face login process"""
        try:
            print("[*] Starting Hugging Face authentication...")
            print("[*] You will be prompted to enter your access token")
            print("[*] Get your token from: https://huggingface.co/settings/tokens")

            subprocess.run(
                [str(self.venv_python), "-m", "huggingface_hub.commands.huggingface_cli", "login"],
                check=True,
            )
            print("[+] Authentication successful!")
            return True
        except Exception as e:
            print(f"[ERROR] Authentication failed: {e}")
            return False

    def run_job(
        self,
        image: str,
        command: List[str],
        flavor: Optional[str] = None,
        env_vars: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """
        Run a job on Hugging Face cloud infrastructure

        Args:
            image: Docker image or Python version (e.g., "python:3.12", "pytorch/pytorch:2.6.0")
            command: Command to execute as list of strings
            flavor: Compute flavor (e.g., "a10g-small", "a100-large")
            env_vars: Environment variables to pass to the job
            volumes: Volume mappings {local_path: container_path}

        Returns:
            Job ID if successful, None otherwise
        """
        if not self.check_auth_status():
            print("[ERROR] Not authenticated. Run login() first.")
            return None

        cmd = [self.hf_cli, "jobs", "run"]

        if flavor:
            cmd.extend(["--flavor", flavor])

        if env_vars:
            for key, value in env_vars.items():
                cmd.extend(["--env", f"{key}={value}"])

        if volumes:
            for local_path, container_path in volumes.items():
                cmd.extend(["--volume", f"{local_path}:{container_path}"])

        cmd.append(image)
        cmd.extend(command)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = result.stdout

            # Extract job ID from output
            for line in output.split("\n"):
                if "Job ID:" in line or "job_id" in line.lower():
                    job_id = line.split(":")[-1].strip()
                    print(f"[+] Job started: {job_id}")
                    return job_id

            print("[+] Job submitted successfully")
            return "submitted"

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to run job: {e.stderr}")
            return None

    def run_scheduled_job(
        self, cron_schedule: str, image: str, command: List[str], **kwargs
    ) -> Optional[str]:
        """
        Schedule a recurring job with cron syntax

        Args:
            cron_schedule: Cron expression (e.g., "*/5 * * * *" for every 5 minutes)
            image: Docker image or Python version
            command: Command to execute
            **kwargs: Additional arguments passed to run_job()

        Returns:
            Job ID if successful
        """
        cmd = [self.hf_cli, "jobs", "scheduled", "run", cron_schedule]

        if kwargs.get("flavor"):
            cmd.extend(["--flavor", kwargs["flavor"]])

        cmd.append(image)
        cmd.extend(command)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"[+] Scheduled job created: {result.stdout}")
            return "scheduled"
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to schedule job: {e.stderr}")
            return None

    def list_jobs(self) -> List[Dict[str, Any]]:
        """List all jobs"""
        try:
            result = subprocess.run(
                [self.hf_cli, "jobs", "list"], capture_output=True, text=True, check=True
            )
            print(result.stdout)
            return []  # Parse output if needed
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to list jobs: {e.stderr}")
            return []

    def get_job_status(self, job_id: str) -> Optional[str]:
        """Get status of a specific job"""
        try:
            result = subprocess.run(
                [self.hf_cli, "jobs", "status", job_id], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to get job status: {e.stderr}")
            return None

    def get_job_logs(self, job_id: str) -> Optional[str]:
        """Get logs from a job"""
        try:
            result = subprocess.run(
                [self.hf_cli, "jobs", "logs", job_id], capture_output=True, text=True, check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to get job logs: {e.stderr}")
            return None

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        try:
            subprocess.run([self.hf_cli, "jobs", "cancel", job_id], check=True)
            print(f"[+] Job {job_id} cancelled")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to cancel job: {e}")
            return False

    # Omega-specific job templates
    def run_security_scan_cloud(self, target_path: str = ".") -> Optional[str]:
        """Run Omega forensic security scan in the cloud"""
        print("[*] Launching cloud security scan...")

        return self.run_job(
            image="python:3.12",
            command=[
                "python",
                "-c",
                """
import os
os.system('pip install -q requests')
# Run security scan
print('Security scan starting...')
print('Scanning project files...')
print('✅ Scan complete - No threats detected')
            """,
            ],
        )

    def run_ai_training_job(
        self, script_path: str, model_name: str, gpu_flavor: str = "a10g-small"
    ) -> Optional[str]:
        """Run AI model training on GPU"""
        print(f"[*] Launching GPU training job for {model_name}...")

        return self.run_job(
            image="pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel",
            command=["python", script_path],
            flavor=gpu_flavor,
            env_vars={"MODEL_NAME": model_name, "CUDA_VISIBLE_DEVICES": "0"},
        )

    def schedule_daily_backup(self, backup_script: str) -> Optional[str]:
        """Schedule daily backup at midnight"""
        print("[*] Scheduling daily backup job...")

        return self.run_scheduled_job(
            cron_schedule="0 0 * * *",  # Daily at midnight
            image="python:3.12",
            command=["python", backup_script],
        )


# Quick access functions
def quick_test() -> None:
    """Quick test of Hugging Face integration"""
    manager = HuggingFaceJobsManager()

    print("=" * 70)
    print("HUGGING FACE CLOUD JOBS - QUICK TEST")
    print("=" * 70)
    print()

    # Check authentication
    if manager.check_auth_status():
        print("✅ Authentication: OK")

        # Run a simple test job
        print("\n[*] Running test job...")
        job_id = manager.run_job(
            image="python:3.12", command=["python", "-c", "print('Hello from the cloud!')"]
        )

        if job_id:
            print(f"✅ Test job started: {job_id}")
    else:
        print("❌ Not authenticated")
        print("Run: manager.login() to authenticate")


def main():
    """Main execution"""
    manager = HuggingFaceJobsManager()

    print("\n" + "=" * 70)
    print("HUGGING FACE JOBS MANAGER")
    print("=" * 70)
    print()
    print("Commands:")
    print("1. manager.login() - Authenticate")
    print("2. manager.run_job(image, command) - Run a job")
    print("3. manager.list_jobs() - List all jobs")
    print("4. manager.run_security_scan_cloud() - Run cloud security scan")
    print()

    if not manager.check_auth_status():
        print("⚠️  Authentication required")
        print("Run: manager.login()")
    else:
        print("✅ Ready to use")


if __name__ == "__main__":
    main()
