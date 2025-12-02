# Conda Launcher

A Python launcher that uses the system's Python executable to create a Conda environment and run the main script inside it.

# Dependencies

- Python 3.8+
- Conda

# Integration guide for developers

## 1. Create the Conda environment for your project

```bash
conda create -n myproject python=<version>
conda activate myproject
# Install your project dependencies
conda install numpy pandas scikit-learn ...
```

## 2. Export the environment specification

```bash
conda env export > environment.yml
```

It is recommended to delete the last line from the exported file: `prefix: ...`.

### 3. Configure the launcher

Edit the launcher script to specify:
- Path to your `environment.yml` file
- Path to your main script (e.g., `src/main.py`)

### 4. Project structure

Your project structure should look like this:

```
project/
├── launcher.py              # Conda launcher script
├── environment.yml          # Conda environment specification
└── src/
    └── main.py              # Your main application script
```

## Usage

Once configured, simply run the launcher:

```bash
python3 launcher.py
```

The launcher will handle environment setup and run your main script automatically.

### Supported commands

```bash
# Run the main script (default behavior)
python3 launcher.py [args...]

# Update the conda environment from environment.yml
python3 launcher.py update_environment

# Save the current environment to environment.yml
python3 launcher.py save_environment

# Install a package and update environment.yml
python3 launcher.py --install PACKAGE_NAME

# Uninstall a package and update environment.yml
python3 launcher.py --uninstall PACKAGE_NAME
```

Any unrecognized arguments are passed transparently to the main script.
