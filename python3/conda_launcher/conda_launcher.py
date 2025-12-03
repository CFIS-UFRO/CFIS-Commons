#!/usr/bin/env python3
# --------------------------------------------------------------------------------------------------
# CFIS Conda Launcher
# --------------------------------------------------------------------------------------------------
import argparse
import subprocess
import tempfile
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
# Environment file cleanup
# --------------------------------------------------------------------------------------------------
def clean_yml_content(yml_content):
    """Remove prefix lines and build strings from conda environment YAML content."""
    cleaned_lines = []
    for line in yml_content.splitlines():
        # Skip prefix lines
        if line.startswith("prefix:"):
            continue

        # Remove build strings from dependencies (e.g., python=3.9.7=h12debd9_1 -> python=3.9.7)
        stripped = line.lstrip()
        if stripped.startswith("- ") and "=" in stripped:
            # Count the number of '=' in the line
            eq_count = stripped.count("=")
            if eq_count > 1:
                # Find the position of the second '='
                first_eq = stripped.find("=")
                second_eq = stripped.find("=", first_eq + 1)
                # Keep everything before the second '=' (including the indent)
                indent = len(line) - len(stripped)
                line = " " * indent + stripped[:second_eq]

        cleaned_lines.append(line)

    return cleaned_lines
# --------------------------------------------------------------------------------------------------
# Load and clean environment file
# --------------------------------------------------------------------------------------------------
def load_and_clean_environment_file():
    try:
        with open(ENVIRONMENT_FILE, "r") as f:
            content = f.read()
        cleaned_lines = clean_yml_content(content)
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False)
        temp_file.write("\n".join(cleaned_lines) + "\n")
        temp_file.close()
        return Path(temp_file.name)
    except Exception as e:
        log(f"Error loading and cleaning environment file: {e}")
        return None
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
# Environment save
# --------------------------------------------------------------------------------------------------
def save_environment(env_name):
    log(f"Saving environment '{env_name}' to environment.yml...")
    try:
        result = subprocess.run(["conda", "env", "export", "-n", env_name], capture_output=True, text=True, check=True)
        cleaned_lines = clean_yml_content(result.stdout)
        with open(ENVIRONMENT_FILE, "w") as f:
            f.write("\n".join(cleaned_lines) + "\n")
        log("Environment saved successfully")
        return True
    except subprocess.CalledProcessError:
        log(f"Error saving environment '{env_name}'")
        return False
# --------------------------------------------------------------------------------------------------
# Install package
# --------------------------------------------------------------------------------------------------
def install_package(env_name, package_name):
    log(f"Installing package '{package_name}' in environment '{env_name}'...")
    try:
        subprocess.run(["conda", "install", "-n", env_name, "-y", package_name], check=True)
        log(f"Package '{package_name}' installed successfully")
        return True
    except subprocess.CalledProcessError:
        log(f"Error installing package '{package_name}'")
        return False
# --------------------------------------------------------------------------------------------------
# Uninstall package
# --------------------------------------------------------------------------------------------------
def uninstall_package(env_name, package_name):
    log(f"Uninstalling package '{package_name}' from environment '{env_name}'...")
    try:
        subprocess.run(["conda", "remove", "-n", env_name, "-y", package_name], check=True)
        log(f"Package '{package_name}' uninstalled successfully")
        return True
    except subprocess.CalledProcessError:
        log(f"Error uninstalling package '{package_name}'")
        return False
# --------------------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description=f"{PROJECT_NAME} Launcher")
    parser.add_argument("command", nargs="?", choices=["update_environment", "save_environment"],
                        help="Command to execute (optional)")
    parser.add_argument("--install", metavar="PACKAGE", help="Install a package with conda and update environment.yml")
    parser.add_argument("--uninstall", metavar="PACKAGE", help="Uninstall a package with conda and update environment.yml")
    args, unknown_args = parser.parse_known_args()
    # Load and clean environment file
    TEMP_ENV_FILE = load_and_clean_environment_file()
    if not TEMP_ENV_FILE:
        log("Error: Could not load and clean environment.yml")
        exit(1)
    try:
        # Verify conda installation for all operations
        if not check_conda():
            log("Error: Conda is required to run this application")
            exit(1)
        # Handle --install command
        if args.install:
            log(f"Installing package: {args.install}")
            env_name = get_environment_name()
            if not env_name:
                log("Error: Could not get environment name from environment.yml")
                exit(1)
            if not check_environment(env_name):
                log(f"Error: Environment '{env_name}' does not exist. Please run the launcher without arguments to create it first.")
                exit(1)
            if not install_package(env_name, args.install):
                log("Error: Failed to install package")
                exit(1)
            if not save_environment(env_name):
                log("Error: Failed to save environment to environment.yml")
                exit(1)
            log("Package installed and environment.yml updated successfully")
            exit(0)
        # Handle --uninstall command
        if args.uninstall:
            log(f"Uninstalling package: {args.uninstall}")
            env_name = get_environment_name()
            if not env_name:
                log("Error: Could not get environment name from environment.yml")
                exit(1)
            if not check_environment(env_name):
                log(f"Error: Environment '{env_name}' does not exist.")
                exit(1)
            if not uninstall_package(env_name, args.uninstall):
                log("Error: Failed to uninstall package")
                exit(1)
            if not save_environment(env_name):
                log("Error: Failed to save environment to environment.yml")
                exit(1)
            log("Package uninstalled and environment.yml updated successfully")
            exit(0)
        # Handle command-line commands
        if args.command:
            log(f"Running command: {args.command}")
            if args.command == "update_environment":
                if not update_environment(TEMP_ENV_FILE):
                    log("Error: Failed to update conda environment")
                    exit(1)
                exit(0)
            elif args.command == "save_environment":
                env_name = get_environment_name()
                if not env_name:
                    log("Error: Could not get environment name from environment.yml")
                    exit(1)
                if not save_environment(env_name):
                    log("Error: Failed to save conda environment")
                    exit(1)
                exit(0)
        # Normal application launch
        log(f"Starting {PROJECT_NAME}")
        # Setup environment
        env_name = get_environment_name()
        if not env_name:
            log("Error: Could not get environment name from environment.yml")
            exit(1)
        if not check_environment(env_name):
            if not create_environment(TEMP_ENV_FILE):
                log("Error: Failed to create conda environment")
                exit(1)
        # Launch application
        log("Launching application...")
        try:
            subprocess.run(["conda", "run", "-n", env_name, "python", str(MAIN_SCRIPT)] + unknown_args, check=True)
        except subprocess.CalledProcessError:
            log("Error launching application")
            exit(1)
    finally:
        # Clean up temporary file
        if TEMP_ENV_FILE and TEMP_ENV_FILE.exists():
            TEMP_ENV_FILE.unlink()
