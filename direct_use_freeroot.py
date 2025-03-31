#!/usr/bin/env python3
"""
Direct-Use FreeRoot: Standalone Ubuntu PRoot environment for Python notebooks

HOW TO USE:
1. Copy this file to your notebook environment
2. Run it with:
   %run direct_use_freeroot.py
   
   Or import directly:
   from direct_use_freeroot import fr

3. Use the 'fr' object to run Ubuntu commands:
   fr.run_command('uname -a')
"""

import os
import platform
import subprocess
import tempfile
import urllib.request
import sys
import shutil
import stat
import tarfile
import io


class FreeRoot:
    def __init__(self, rootfs_dir=None):
        self.user_home = os.path.expanduser("~")
        self.rootfs_dir = rootfs_dir or os.path.join(self.user_home, "rootfs")
        
        self.arch = platform.machine()
        if self.arch == "x86_64":
            self.arch_alt = "amd64"
        elif self.arch == "aarch64":
            self.arch_alt = "arm64"
        else:
            raise RuntimeError(f"Unsupported CPU architecture: {self.arch}")
        
        self.proot_url = f"https://raw.githubusercontent.com/foxytouxxx/freeroot/main/proot-{self.arch}"
        self.ubuntu_url = f"http://cdimage.ubuntu.com/ubuntu-base/releases/20.04/release/ubuntu-base-20.04.4-base-{self.arch_alt}.tar.gz"
        self.proot_path = os.path.join(self.rootfs_dir, "usr", "local", "bin", "proot")
        self.installed_flag = os.path.join(self.rootfs_dir, ".installed")

    def _download_file(self, url, target_path=None, return_data=False, max_retries=3):
        for i in range(max_retries):
            try:
                print(f"Downloading {url}")
                if return_data:
                    with urllib.request.urlopen(url) as response:
                        return response.read()
                else:
                    if target_path:
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        urllib.request.urlretrieve(url, target_path)
                        return True
            except Exception as e:
                print(f"Attempt {i+1} failed: {e}")
        return False if not return_data else None

    def _setup_proot(self):
        data = self._download_file(self.proot_url, return_data=True)
        if not data:
            raise RuntimeError("Failed to download PRoot")
            
        os.makedirs(os.path.dirname(self.proot_path), exist_ok=True)
        with open(self.proot_path, 'wb') as f:
            f.write(data)
        os.chmod(self.proot_path, os.stat(self.proot_path).st_mode | stat.S_IEXEC)

    def _extract_rootfs(self):
        data = self._download_file(self.ubuntu_url, return_data=True)
        if not data:
            raise RuntimeError("Failed to download Ubuntu")
            
        print(f"Extracting Ubuntu rootfs to {self.rootfs_dir}")
        os.makedirs(self.rootfs_dir, exist_ok=True)
        
        # Use Python's tarfile instead of system tar command
        tar_data = io.BytesIO(data)
        with tarfile.open(fileobj=tar_data, mode='r:gz') as tar:
            tar.extractall(path=self.rootfs_dir)

    def _configure_rootfs(self):
        # Configure /etc/resolv.conf to enable networking
        resolv_conf = os.path.join(self.rootfs_dir, "etc", "resolv.conf")
        os.makedirs(os.path.dirname(resolv_conf), exist_ok=True)
        try:
            with open(resolv_conf, "w") as f:
                f.write("nameserver 8.8.8.8\nnameserver 1.1.1.1\n")
        except Exception as e:
            print(f"Warning: Could not configure resolv.conf: {e}")

    def install(self):
        if os.path.exists(self.installed_flag):
            print("FreeRoot is already installed.")
            return
        
        self._setup_proot()
        self._extract_rootfs()
        self._configure_rootfs()
        
        # Create installed flag file
        with open(self.installed_flag, 'w') as f:
            f.write('installed')
        print("FreeRoot installation complete.")

    def run_command(self, command, working_dir=None, env=None):
        if not os.path.exists(self.installed_flag):
            self.install()
            
        full_cmd = [
            self.proot_path,
            f"--rootfs={self.rootfs_dir}",
            "-0",
            "-w", working_dir or "/root",
            "-b", "/dev",
            "-b", "/sys",
            "-b", "/proc",
            "-b", f"{self.rootfs_dir}/etc/resolv.conf:/etc/resolv.conf",
            "--kill-on-exit",
            "bash", "-c", command
        ]
        
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
        if target_dir is None:
            repo_name = repo_url.split("/")[-1].replace(".git", "")
            target_dir = repo_name
        
        cmd = f"git clone {repo_url}"
        if branch:
            cmd += f" --branch {branch}"
        cmd += f" {target_dir}"
        
        return self.run_command(cmd)

    def start_shell(self):
        if not os.path.exists(self.installed_flag):
            self.install()
        
        cmd = [
            self.proot_path,
            f"--rootfs={self.rootfs_dir}",
            "-0",
            "-w", "/root",
            "-b", "/dev",
            "-b", "/sys",
            "-b", "/proc",
            "-b", f"{self.rootfs_dir}/etc/resolv.conf:/etc/resolv.conf",
            "--kill-on-exit",
            "bash"
        ]
        
        subprocess.run(cmd)

    def cleanup(self):
        if os.path.exists(self.rootfs_dir):
            shutil.rmtree(self.rootfs_dir)
            print(f"Cleaned up {self.rootfs_dir}")


# Create fr object for immediate use
fr = FreeRoot()