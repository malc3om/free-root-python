# FreeRoot Python

A Python notebook-friendly version of [freeroot](https://github.com/foxytouxxx/freeroot) - run Ubuntu in your Python notebook environment with just one command!

## Overview

FreeRoot Python allows you to run a lightweight Ubuntu environment directly in your Python notebooks using PRoot technology. This gives you access to a complete Linux environment without requiring root privileges or containers.

## Features

- **Easy to Use**: Just one Python command to set up an Ubuntu environment
- **Notebook-Friendly**: Designed to work in Jupyter, Colab, and other notebook environments
- **No Root Required**: Uses PRoot to provide a virtual root environment without requiring actual root privileges
- **Cross-Platform**: Works on x86_64 and ARM64 architectures
- **Customizable**: Configure your Ubuntu environment with simple Python commands
- **Git Integration**: Directly clone repositories into your Ubuntu environment

## Installation

```bash
pip install git+https://github.com/malc3om/free-root-python.git
```

## Quick Start

```python
from freeroot import setup_ubuntu

# Set up Ubuntu with one command
fr = setup_ubuntu()

# Run commands in Ubuntu
print(fr.run_command('uname -a'))
```

## Examples

### Installing packages in Ubuntu

```python
# Update package lists and install Python
fr.run_command('apt-get update && apt-get install -y python3 python3-pip')

# Install more packages
fr.run_command('apt-get install -y wget curl nano')
```

### Running Python code in Ubuntu

```python
# Create a Python script
fr.run_command('echo "print(\'Hello from Ubuntu\')" > test.py')

# Run the script
output = fr.run_command('python3 test.py')
print(output)
```

### Cloning Git repositories

```python
# Clone a repository
fr.clone_repo('https://github.com/username/repo.git')

# Clone a specific branch to a specific directory
fr.clone_repo('https://github.com/username/repo.git', 
              target_dir='custom-dir', 
              branch='develop')
```

### Cleaning up

```python
# Remove the Ubuntu environment when done
fr.cleanup()
```

## Advanced Usage

For more advanced usage, see the `example.ipynb` notebook in this repository.

## How It Works

FreeRoot Python:

1. Downloads an Ubuntu base system
2. Sets up PRoot to provide a virtual root environment
3. Configures the environment for immediate use
4. Provides a Python API to interact with the environment

## Prerequisites

- Python 3.6 or higher
- Internet connection (for downloading Ubuntu)
- tar command for extracting the rootfs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

- Based on [freeroot](https://github.com/foxytouxxx/freeroot) by foxytouxxx
- Uses PRoot technology
- Ubuntu base system from Canonical

---

**Note:** This package is intended for educational and development purposes. Use responsibly and at your own risk.