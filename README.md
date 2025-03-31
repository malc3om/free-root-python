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
fr.run_command('echo \"print(\'Hello from Ubuntu\')\" > test.py')

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

## Troubleshooting

### Package System Issues

If you encounter package installation errors like:

```
E: dpkg was interrupted, you must manually run 'dpkg --configure -a' to correct the problem.
```

You can fix it using these commands:

```python
# Fix interrupted package installation
fr.run_command('dpkg --configure -a')

# Then update and install packages
fr.run_command('apt-get update')
fr.run_command('apt-get install -y your-package-name')
```

For more stubborn package issues, try:

```python
# Remove lock files if needed
fr.run_command('rm -f /var/lib/dpkg/lock /var/lib/dpkg/lock-frontend')
fr.run_command('rm -f /var/lib/apt/lists/lock /var/cache/apt/archives/lock')

# Fix interrupted package installation
fr.run_command('dpkg --configure -a')

# Fix broken dependencies
fr.run_command('apt-get install -f -y')
```

### Advanced Package System Recovery

If you encounter severe package system errors or dependency issues, use this more aggressive approach:

```python
# Fix package system with multiple fallback commands
fr.run_command('dpkg --configure -a || true')
fr.run_command('apt-get update -y || true')
fr.run_command('apt-get install -y --reinstall libc6 || true')
fr.run_command('apt-get install -y --fix-broken || true')
fr.run_command('apt-get update && apt-get install -y libc-bin libc6 || true')
fr.run_command('apt-get update && apt-get upgrade -y || true')
```

### Locale Issues

If you see locale warnings like "warning: setlocale: LC_ALL: cannot change locale", install locale support:

```python
fr.run_command("apt-get install -y locales")
fr.run_command("locale-gen en_US.UTF-8")
fr.run_command("update-locale LANG=en_US.UTF-8")
```

### Import Issues

If you have trouble importing the module, try adding the package location to your Python path:

```python
import sys
sys.path.append('/path/to/site-packages')
import freeroot
fr = freeroot.setup_ubuntu()
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