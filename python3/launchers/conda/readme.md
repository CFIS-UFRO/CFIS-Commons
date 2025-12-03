# Conda Launcher

A Python launcher that uses the system's Python executable to create a Conda environment and run the main script inside it.

# Dependencies

- Python 3.8+
- Conda

# Integration guide for developers

## 1. Create the environment specification file

Create an `environment.yml` file based on the included example ([environment.yml](environment.yml)). The file structure is:

```yaml
name: your-environment-name      # Environment name
channels:
  - conda-forge                  # Package sources
  - defaults
dependencies:
  - python=3.11                  # Python version
  - numpy                        # Conda packages
  - pandas
  - matplotlib
  - pip:                         # Pip packages (optional)
    - requests
```

**Key sections:**
- `name`: Conda environment name.
- `channels`: Channels used to retrieve the packages.
- `dependencies`:
  - Python version: `python=x.xx`
  - Conda packages, for packages coming from the conda channels, like: `numpy`, `pandas`, ...
  - Pip packages, for packages coming from the pip repository.

## 2. Configure the launcher

Edit the launcher script to specify:
- Path to your `environment.yml` file
- Path to your main script (e.g., `src/main.py`)

## 3. Project structure

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

The launcher will:
1. Verify conda is installed
2. Check if the environment exists
3. Create the environment if needed
4. Launch your application

### Supported commands

```bash
# Run the main script (default behavior)
python3 launcher.py [args...]

# Update the conda environment before launching
python3 launcher.py --update [args...]
```

Any unrecognized arguments are passed transparently to the main script.
