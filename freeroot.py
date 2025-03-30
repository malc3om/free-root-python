#!/usr/bin/env python3
"""
FreeRoot Python - Ubuntu PRoot environment for Python notebooks
Based on https://github.com/foxytouxxx/freeroot
"""

import os
import platform
import subprocess
import tempfile
import urllib.request
from pathlib import Path
import sys
import shutil
import stat
from IPython.display import clear_output, HTML, display

class FreeRoot:
    def __init__(self, rootfs_dir=None):
        """Initialize FreeRoot with a directory for the root filesystem"""
        self.rootfs_dir = rootfs_dir or os.path.join(os.getcwd(), "rootfs")
        self.arch = platform.machine()
        
        # Set architecture alternative name for Ubuntu
        if self.arch == "x86_64":
            self.arch_alt = "amd64"
        elif self.arch == "aarch64":
            self.arch_alt = "arm64"
        else:
            raise RuntimeError(f"Unsupported CPU architecture: {self.arch}")
        
        # URLs and paths
        self.proot_url = f"https://raw.githubusercontent.com/foxytouxxx/freeroot/main/proot-{self.arch}"
        self.ubuntu_url = f"http://cdimage.ubuntu.com/ubuntu-base/releases/20.04/release/ubuntu-base-20.04.4-base-{self.arch_alt}.tar.gz"
        self.proot_path = os.path.join(self.rootfs_dir, "usr", "local", "bin", "proot")
        self.installed_flag = os.path.join(self.rootfs_dir, ".installed")

    def _download_file(self, url, target_path, max_retries=5):
        """Download a file with retries"""
        retries = 0
        while retries < max_retries:
            try:
                print(f"Downloading {url} to {target_path}")
                urllib.request.urlretrieve(url, target_path)
                
                # Verify file was downloaded
                if os.path.getsize(target_path) > 0:
                    return True
                
                print("Download failed, retrying...")
                retries += 1
            except Exception as e:
                print(f"Error downloading: {e}")
                retries += 1
        
        return False

    def _setup_proot(self):
        """Download and set up PRoot binary"""
        os.makedirs(os.path.dirname(self.proot_path), exist_ok=True)
        
        if not self._download_file(self.proot_url, self.proot_path, max_retries=5):
            raise RuntimeError("Failed to download PRoot binary")
        
        # Make executable
        os.chmod(self.proot_path, os.stat(self.proot_path).st_mode | stat.S_IEXEC)

    def _extract_rootfs(self):
        """Download and extract Ubuntu rootfs"""
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            if not self._download_file(self.ubuntu_url, temp_path, max_retries=5):
                raise RuntimeError("Failed to download Ubuntu rootfs")
            
            # Create rootfs directory
            os.makedirs(self.rootfs_dir, exist_ok=True)
            
            # Extract rootfs
            print(f"Extracting Ubuntu rootfs to {self.rootfs_dir}")
            subprocess.run(["tar", "-xf", temp_path, "-C", self.rootfs_dir], check=True)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def _configure_rootfs(self):
        """Configure the root filesystem"""
        # Set DNS
        resolv_conf = os.path.join(self.rootfs_dir, "etc", "resolv.conf")
        with open(resolv_conf, "w") as f:
            f.write("nameserver 1.1.1.1\nnameserver 1.0.0.1\n")
        
        # Create installed flag
        with open(self.installed_flag, "w") as f:
            pass
    
    def install(self):
        """Install Ubuntu rootfs and PRoot"""
        if os.path.exists(self.installed_flag):
            print("FreeRoot is already installed.")
            return

        print("############################################################")
        print("#                  FreeRoot Python Installer               #")
        print("#                                                          #")
        print("############################################################")
        
        try:
            self._extract_rootfs()
            self._setup_proot()
            self._configure_rootfs()
            
            clear_output(wait=True)
            display(HTML("""
            <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px; text-align: center;">
              <h3 style="color: #2c3e50;">✅ FreeRoot Python Installation Complete!</h3>
              <p>Ubuntu environment is ready to use</p>
            </div>
            """))
        except Exception as e:
            print(f"Installation failed: {e}")
            if os.path.exists(self.rootfs_dir):
                print(f"Cleaning up {self.rootfs_dir}")
                shutil.rmtree(self.rootfs_dir, ignore_errors=True)
            raise

    def run_command(self, command, working_dir="/root", env=None):
        """Run a command in the PRoot environment"""
        if not os.path.exists(self.installed_flag):
            raise RuntimeError("FreeRoot is not installed. Run install() first.")
        
        proot_cmd = [
            self.proot_path,
            f"--rootfs={self.rootfs_dir}",
            "-0", "-w", working_dir,
            "-b", "/dev", "-b", "/sys", "-b", "/proc",
            "-b", f"{os.path.join(self.rootfs_dir, 'etc/resolv.conf')}:/etc/resolv.conf",
            "--kill-on-exit"
        ]
        
        if isinstance(command, str):
            command = ["bash", "-c", command]
        
        full_cmd = proot_cmd + command
        
        environ = os.environ.copy()
        if env:
            environ.update(env)
        
        try:
            result = subprocess.run(
                full_cmd,
                env=environ,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}")
            print(f"Error output: {e.stderr}")
            raise

    def clone_repo(self, repo_url, target_dir=None, branch=None):
        """
        Clone a git repository into the Ubuntu environment
        
        Parameters:
        -----------
        repo_url : str
            URL of the git repository to clone
        target_dir : str, optional
            Directory where to clone the repository (relative to /root).
            If None, the repository will be cloned to /root/{repo_name}
        branch : str, optional
            Branch to clone. If None, the default branch will be used
            
        Returns:
        --------
        str
            Output of the git clone command
        """
        if not os.path.exists(self.installed_flag):
            raise RuntimeError("FreeRoot is not installed. Run install() first.")
        
        # Install git if it's not already installed
        try:
            self.run_command("which git >/dev/null 2>&1 || (apt-get update && apt-get install -y git)")
        except Exception as e:
            print(f"Failed to ensure git is installed: {e}")
            raise
        
        # Prepare git clone command
        clone_cmd = f"git clone {repo_url}"
        
        # Add branch if specified
        if branch:
            clone_cmd += f" --branch {branch}"
        
        # Add target directory if specified
        if target_dir:
            clone_cmd += f" {target_dir}"
            work_dir = "/root"
        else:
            # Extract repo name from URL to determine where it was cloned
            repo_name = repo_url.split('/')[-1]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            work_dir = "/root"
            target_dir = repo_name
        
        # Run the clone command
        output = self.run_command(clone_cmd)
        
        # Print success message
        full_path = f"/root/{target_dir}"
        print(f"Repository cloned successfully to {full_path}")
        
        return output

    def start_shell(self):
        """Start an interactive shell in the PRoot environment"""
        if not os.path.exists(self.installed_flag):
            raise RuntimeError("FreeRoot is not installed. Run install() first.")
        
        proot_cmd = [
            self.proot_path,
            f"--rootfs={self.rootfs_dir}",
            "-0", "-w", "/root",
            "-b", "/dev", "-b", "/sys", "-b", "/proc",
            "-b", f"{os.path.join(self.rootfs_dir, 'etc/resolv.conf')}:/etc/resolv.conf",
            "--kill-on-exit",
            "bash"
        ]
        
        print("Starting interactive shell in Ubuntu environment...")
        print("(Note: This may not work in all notebook environments)")
        try:
            subprocess.run(proot_cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Shell exited with code {e.returncode}")

    def cleanup(self):
        """Remove the FreeRoot installation"""
        if os.path.exists(self.rootfs_dir):
            print(f"Removing FreeRoot installation at {self.rootfs_dir}")
            shutil.rmtree(self.rootfs_dir, ignore_errors=True)
            print("FreeRoot removed successfully")

# Helper function for quick setup
def setup_ubuntu():
    """One-command setup for FreeRoot Ubuntu environment"""
    fr = FreeRoot()
    fr.install()
    return fr

# For direct script execution
if __name__ == "__main__":
    fr = setup_ubuntu()
    print("FreeRoot Ubuntu environment is ready!")
    print("Access it by importing this module in your notebook:")
    print("  from freeroot import FreeRoot")
    print("  fr = FreeRoot()")
    print("  fr.run_command('uname -a')")