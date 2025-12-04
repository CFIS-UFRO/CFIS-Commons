#!/usr/bin/env python3
# --------------------------------------------------------------------------------------------------
# CFIS Conda Launcher
# --------------------------------------------------------------------------------------------------
import argparse
import subprocess
from pathlib import Path
# --------------------------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
ENVIRONMENT_FILE = SCRIPT_DIR / "environment.yml"
MAIN_SCRIPT = SCRIPT_DIR / "src" / "main.py"
PROJECT_NAME = "CFIS Conda Launcher"
# --------------------------------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------------------------------
def log(msg):
    print(f"[CFIS CONDA LAUNCHER] - {msg}")
# --------------------------------------------------------------------------------------------------
# Conda verification
# --------------------------------------------------------------------------------------------------
def check_conda():
    try:
        result = subprocess.run(["conda", "--version"], capture_output=True, text=True, check=True)
        log(f"Conda detected: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        log("Conda not found")
        return False
# --------------------------------------------------------------------------------------------------
# Environment verification
# --------------------------------------------------------------------------------------------------
def check_environment(env_name):
    try:
        result = subprocess.run(["conda", "env", "list"], capture_output=True, text=True, check=True)
        for line in result.stdout.splitlines():
            if line.strip().startswith(env_name + " ") or line.strip().startswith(env_name + "*"):
                log(f"Environment '{env_name}' found")
                return True
        log(f"Environment '{env_name}' not found")
        return False
    except subprocess.CalledProcessError:
        log("Error checking conda environments")
        return False
# --------------------------------------------------------------------------------------------------
# Environment name from YAML
# --------------------------------------------------------------------------------------------------
def get_environment_name():
    try:
        with open(ENVIRONMENT_FILE, "r") as f:
            for line in f:
                if line.strip().startswith("name:"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        return None
    return None
# --------------------------------------------------------------------------------------------------
# Environment creation
# --------------------------------------------------------------------------------------------------
def create_environment(env_file):
    log("Creating environment from environment.yml...")
    try:
        subprocess.run(["conda", "env", "create", "-f", str(env_file)], check=True)
        log("Environment created successfully")
        return True
    except subprocess.CalledProcessError:
        log("Error creating environment")
        return False
# --------------------------------------------------------------------------------------------------
# Environment update
# --------------------------------------------------------------------------------------------------
def update_environment(env_file):
    log("Updating environment from environment.yml...")
    try:
        subprocess.run(["conda", "env", "update", "-f", str(env_file), "--prune"], check=True)
        log("Environment updated successfully")
        return True
    except subprocess.CalledProcessError:
        log("Error updating environment")
        return False
# --------------------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description=f"{PROJECT_NAME} Launcher")
    parser.add_argument("--update", action="store_true", help="Update environment before launching")
    args, unknown_args = parser.parse_known_args()

    log(f"Starting {PROJECT_NAME}")

    # Verify conda installation
    if not check_conda():
        log("Error: Conda is required to run this application")
        exit(1)

    # Get environment name
    env_name = get_environment_name()
    if not env_name:
        log("Error: Could not get environment name from environment.yml")
        exit(1)

    # Check if environment exists, create if not
    if not check_environment(env_name):
        if not create_environment(ENVIRONMENT_FILE):
            log("Error: Failed to create conda environment")
            exit(1)

    # Update environment if requested
    if args.update:
        if not update_environment(ENVIRONMENT_FILE):
            log("Error: Failed to update conda environment")
            exit(1)

    # Launch application
    log("Launching application...")
    try:
        subprocess.run(["conda", "run", "--no-capture-output", "-n", env_name, "python", str(MAIN_SCRIPT)] + unknown_args, check=True)
    except subprocess.CalledProcessError:
        log("Error launching application")
        exit(1)
