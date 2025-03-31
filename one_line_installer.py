#!/usr/bin/env python3
"""
One-line Ubuntu installer for notebooks

Run this with:

```python
import requests; exec(requests.get('https://raw.githubusercontent.com/malc3om/free-root-python/main/one_line_installer.py').text)
```

"""

import sys
import subprocess
import tempfile
import os
from pathlib import Path

def install():
    """Install FreeRoot Python in one line"""
    print("Installing FreeRoot Python...")
    
    # Install from GitHub
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', 
            'git+https://github.com/malc3om/free-root-python.git'
        ])
    except subprocess.CalledProcessError:
        print("Error installing package. Trying alternate method...")
        
        # Alternative method if pip install fails
        with tempfile.TemporaryDirectory() as tmp_dir:
            os.chdir(tmp_dir)
            try:
                # Clone repository
                subprocess.check_call(['git', 'clone', 'https://github.com/malc3om/free-root-python.git'])
                os.chdir('free-root-python')
                
                # Install locally
                subprocess.check_call([sys.executable, 'setup.py', 'install'])
            except subprocess.CalledProcessError as e:
                print(f"Installation failed: {e}")
                return

    # Import the module
    try:
        from freeroot import setup_ubuntu
        
        # Set up Ubuntu
        fr = setup_ubuntu()
        
        # Make fr available in the global scope
        globals()['fr'] = fr
        
        print("\nSuccess! Ubuntu is ready to use.")
        print("The 'fr' object is now available for running commands:")
        print("  fr.run_command('uname -a')")
    except Exception as e:
        print(f"Error setting up Ubuntu: {e}")

# Run the installation
install()