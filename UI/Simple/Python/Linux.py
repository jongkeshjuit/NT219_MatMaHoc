#!/usr/bin/env python3
"""
Crypto++ Compiler GUI Tool - Linux Version
A simple GUI for compiling C++ projects with multiple compilers and crypto libraries on Linux
Optimized for Linux distributions with native package manager integration
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import threading
import os
import json
import shutil
from pathlib import Path
import queue
import time
import platform
import sys

class LinuxCompilerConfig:
    """Configuration manager optimized for Linux systems"""
    
    def __init__(self):
        self.config_file = Path.home() / ".config" / "crypto-compiler" / "config.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Detect Linux distribution
        self.distro = self.detect_distro()
        
        # Default paths for common Linux distributions
        self.default_config = {
            "system": {
                "distro": self.distro,
                "architecture": platform.machine(),
                "python_version": sys.version
            },
            "paths": self.get_default_paths(),
            "compilers": {
                "gcc": {
                    "executable": self.find_executable("g++"),
                    "flags": ["-std=c++17", "-Wall", "-Wextra", "-O3", "-DNDEBUG"],
                    "debug_flags": ["-std=c++17", "-Wall", "-Wextra", "-g", "-O0", "-DDEBUG"],
                    "libs": ["-lpthread"]
                },
                "clang": {
                    "executable": self.find_executable("clang++"),
                    "flags": ["-std=c++17", "-Wall", "-Wextra", "-O3", "-DNDEBUG"],
                    "debug_flags": ["-std=c++17", "-Wall", "-Wextra", "-g", "-O0", "-DDEBUG"],
                    "libs": ["-lpthread"]
                }
            },
            "libraries": {
                "cryptopp": {
                    "system_package": self.get_cryptopp_package(),
                    "include_dirs": ["/usr/include", "/usr/local/include"],
                    "lib_dirs": ["/usr/lib", "/usr/local/lib", "/usr/lib/x86_64-linux-gnu"],
                    "libs": ["cryptopp"]
                },
                "openssl": {
                    "system_package": "libssl-dev",
                    "include_dirs": ["/usr/include/openssl", "/usr/local/include/openssl"],
                    "lib_dirs": ["/usr/lib", "/usr/local/lib", "/usr/lib/x86_64-linux-gnu"],
                    "libs": ["ssl", "crypto"]
                }
            },
            "build": {
                "output_dir": "build",
                "temp_dir": "/tmp/crypto-compiler",
                "parallel_jobs": os.cpu_count() or 4
            }
        }
        
        self.config = self.load_config()
    
    def detect_distro(self):
        """Detect Linux distribution"""
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("ID="):
                        return line.split("=")[1].strip().strip('"')
        except:
            pass
        
        # Fallback detection
        if shutil.which("apt"):
            return "ubuntu"
        elif shutil.which("dnf"):
            return "fedora"
        elif shutil.which("pacman"):
            return "arch"
        else:
            return "generic"
    
    def get_cryptopp_package(self):
        """Get crypto++ package name for current distro"""
        packages = {
            "ubuntu": "libcrypto++-dev",
            "debian": "libcrypto++-dev", 
            "fedora": "cryptopp-devel",
            "centos": "cryptopp-devel",
            "arch": "crypto++",
            "opensuse": "libcryptopp-devel"
        }
        return packages.get(self.distro, "libcrypto++-dev")
    
    def get_default_paths(self):
        """Get default paths for current system"""
        home = str(Path.home())
        return {
            "source_dir": home + "/Projects",
            "custom_cryptopp": "/usr/local",
            "custom_openssl": "/usr/local", 
            "build_output": home + "/Projects/build"
        }
    
    def find_executable(self, name):
        """Find executable in PATH"""
        path = shutil.which(name)
        return path if path else f"/usr/bin/{name}"
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new keys
                    return self.merge_configs(self.default_config, loaded)
        except Exception as e:
            print(f"Error loading config: {e}")
        
        # Save and return default
        self.save_config(self.default_config)
        return self.default_config.copy()
    
    def merge_configs(self, default, loaded):
        """Recursively merge configurations"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self, config=None):
        """Save configuration to file"""
        try:
            config_to_save = config or self.config
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

class LinuxCompilerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.config = LinuxCompilerConfig()
        self.build_process = None
        self.output_queue = queue.Queue()
        
        # Variables
        self.compiler_var = tk.StringVar(value="gcc")
        self.library_var = tk.StringVar(value="cryptopp")
        self.source_var = tk.StringVar(value="main.cpp")
        self.build_type_var = tk.StringVar(value="executable")
        self.build_mode_var = tk.StringVar(value="release")
        self.auto_run_var = tk.BooleanVar(value=True)
        self.parallel_build_var = tk.BooleanVar(value=True)
        
        self.setup_ui()
        self.check_system_dependencies()
        
        # Start output queue processor
        self.process_queue()
    
    def setup_ui(self):
        """Setup the main UI with Linux-style theming"""
        self.root.title("🔐 Crypto++ Compiler Tool - Linux")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        
        # Try to use native Linux theme
        try:
            style = ttk.Style()
            # Use system theme if available
            available_themes = style.theme_names()
            if 'clam' in available_themes:
                style.theme_use('clam')
            elif 'alt' in available_themes:
                style.theme_use('alt')
        except:
            pass
        
        # Create notebook with Linux-style tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Build tab
        self.build_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.build_frame, text="🔨 Build")
        self.setup_build_tab()
        
        # System tab
        self.system_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.system_frame, text="🐧 System")
        self.setup_system_tab()
        
        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ Settings")
        self.setup_settings_tab()
        
        # About tab
        self.about_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.about_frame, text="ℹ️ About")
        self.setup_about_tab()
        
        # Status bar with Linux system info
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side='bottom', fill='x')
        
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var)
        self.status_label.pack(side='left', padx=5)
        
        # System info in status bar
        distro = self.config.config["system"]["distro"]
        arch = self.config.config["system"]["architecture"]
        self.system_label = ttk.Label(self.status_frame, text=f"🐧 {distro} ({arch})")
        self.system_label.pack(side='right', padx=5)
    
    def setup_build_tab(self):
        """Setup the build tab with Linux-optimized controls"""
        main_frame = ttk.Frame(self.build_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Build configuration
        config_frame = ttk.LabelFrame(main_frame, text="Build Configuration", padding=10)
        config_frame.pack(fill='x', pady=(0, 10))
        
        # Compiler and library selection
        row1 = ttk.Frame(config_frame)
        row1.pack(fill='x', pady=(0, 5))
        
        ttk.Label(row1, text="Compiler:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        compiler_combo = ttk.Combobox(row1, textvariable=self.compiler_var,
                                    values=["gcc", "clang"], state="readonly", width=10)
        compiler_combo.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(row1, text="Library:").grid(row=0, column=2, sticky='w', padx=(0, 5))
        library_combo = ttk.Combobox(row1, textvariable=self.library_var,
                                   values=["cryptopp", "openssl"], state="readonly", width=10)
        library_combo.grid(row=0, column=3, padx=(0, 20))
        
        ttk.Label(row1, text="Type:").grid(row=0, column=4, sticky='w', padx=(0, 5))
        type_combo = ttk.Combobox(row1, textvariable=self.build_type_var,
                                values=["executable", "shared_library", "static_library"],
                                state="readonly", width=12)
        type_combo.grid(row=0, column=5)
        
        # Build mode and options
        row2 = ttk.Frame(config_frame)
        row2.pack(fill='x', pady=(0, 5))
        
        ttk.Label(row2, text="Mode:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        mode_combo = ttk.Combobox(row2, textvariable=self.build_mode_var,
                                values=["release", "debug"], state="readonly", width=10)
        mode_combo.grid(row=0, column=1, padx=(0, 20))
        
        auto_run_check = ttk.Checkbutton(row2, text="Auto-run after build", 
                                       variable=self.auto_run_var)
        auto_run_check.grid(row=0, column=2, padx=(0, 20))
        
        parallel_check = ttk.Checkbutton(row2, text="Parallel build", 
                                       variable=self.parallel_build_var)
        parallel_check.grid(row=0, column=3)
        
        # Source file selection
        row3 = ttk.Frame(config_frame)
        row3.pack(fill='x', pady=(0, 5))
        
        ttk.Label(row3, text="Source:").pack(side='left')
        source_entry = ttk.Entry(row3, textvariable=self.source_var, width=50)
        source_entry.pack(side='left', fill='x', expand=True, padx=(5, 5))
        
        browse_btn = ttk.Button(row3, text="📁 Browse", command=self.browse_file)
        browse_btn.pack(side='right')
        
        # Build controls
        controls_frame = ttk.Frame(config_frame)
        controls_frame.pack(fill='x', pady=(10, 0))
        
        self.build_btn = ttk.Button(controls_frame, text="🔨 Build & Run", 
                                   command=self.build_async, style="Accent.TButton")
        self.build_btn.pack(side='left', padx=(0, 5))
        
        self.stop_btn = ttk.Button(controls_frame, text="⏹️ Stop", 
                                  command=self.stop_build)
        self.stop_btn.pack(side='left', padx=(0, 5))
        
        clean_btn = ttk.Button(controls_frame, text="🧹 Clean", 
                              command=self.clean_build)
        clean_btn.pack(side='left', padx=(0, 5))
        
        # Progress bar
        self.progress = ttk.Progressbar(controls_frame, mode='indeterminate')
        self.progress.pack(side='right', fill='x', expand=True, padx=(10, 0))
        self.progress.pack_forget()
        
        # Output area with Linux terminal styling
        output_frame = ttk.LabelFrame(main_frame, text="Build Output", padding=5)
        output_frame.pack(fill='both', expand=True)
        
        self.output = scrolledtext.ScrolledText(output_frame, height=20,
                                               font=('DejaVu Sans Mono', 10),
                                               wrap=tk.WORD, state='disabled',
                                               bg='#000000', fg='#00ff00',
                                               insertbackground='#00ff00')
        self.output.pack(fill='both', expand=True)
        
        # Output controls
        output_controls = ttk.Frame(output_frame)
        output_controls.pack(fill='x', pady=(5, 0))
        
        ttk.Button(output_controls, text="Clear", 
                  command=self.clear_output).pack(side='left')
        ttk.Button(output_controls, text="Save Log", 
                  command=self.save_log).pack(side='left', padx=(5, 0))
        ttk.Button(output_controls, text="Copy Output", 
                  command=self.copy_output).pack(side='left', padx=(5, 0))
    
    def setup_system_tab(self):
        """Setup system information and package management tab"""
        main_frame = ttk.Frame(self.system_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # System information
        sys_info_frame = ttk.LabelFrame(main_frame, text="System Information", padding=10)
        sys_info_frame.pack(fill='x', pady=(0, 10))
        
        info_text = scrolledtext.ScrolledText(sys_info_frame, height=8, state='disabled')
        info_text.pack(fill='x')
        
        # Populate system info
        info_content = self.get_system_info()
        info_text.config(state='normal')
        info_text.insert('1.0', info_content)
        info_text.config(state='disabled')
        
        # Package management
        pkg_frame = ttk.LabelFrame(main_frame, text="Package Management", padding=10)
        pkg_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(pkg_frame, text="Install required development packages:").pack(anchor='w')
        
        pkg_buttons = ttk.Frame(pkg_frame)
        pkg_buttons.pack(fill='x', pady=(5, 0))
        
        ttk.Button(pkg_buttons, text="Install Crypto++", 
                  command=self.install_cryptopp).pack(side='left', padx=(0, 5))
        ttk.Button(pkg_buttons, text="Install OpenSSL", 
                  command=self.install_openssl).pack(side='left', padx=(0, 5))
        ttk.Button(pkg_buttons, text="Install Build Tools", 
                  command=self.install_build_tools).pack(side='left', padx=(0, 5))
        
        # Compiler detection
        detect_frame = ttk.LabelFrame(main_frame, text="Compiler Detection", padding=10)
        detect_frame.pack(fill='x')
        
        ttk.Button(detect_frame, text="🔍 Detect Compilers", 
                  command=self.detect_compilers).pack(side='left')
        ttk.Button(detect_frame, text="🔍 Check Libraries", 
                  command=self.check_libraries).pack(side='left', padx=(5, 0))
        
        self.detect_output = scrolledtext.ScrolledText(detect_frame, height=6, state='disabled')
        self.detect_output.pack(fill='x', pady=(5, 0))
    
    def setup_settings_tab(self):
        """Setup settings configuration tab"""
        main_frame = ttk.Frame(self.settings_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollable settings
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Paths configuration
        paths_frame = ttk.LabelFrame(scrollable_frame, text="Paths Configuration", padding=10)
        paths_frame.pack(fill='x', padx=10, pady=5)
        
        self.path_vars = {}
        for key, value in self.config.config["paths"].items():
            frame = ttk.Frame(paths_frame)
            frame.pack(fill='x', pady=2)
            
            ttk.Label(frame, text=f"{key.replace('_', ' ').title()}:", 
                     width=20).pack(side='left')
            
            var = tk.StringVar(value=value)
            self.path_vars[key] = var
            
            entry = ttk.Entry(frame, textvariable=var, width=60)
            entry.pack(side='left', fill='x', expand=True, padx=(5, 5))
            
            ttk.Button(frame, text="📁", width=3,
                      command=lambda k=key: self.browse_path(k)).pack(side='right')
        
        # Build settings
        build_frame = ttk.LabelFrame(scrollable_frame, text="Build Settings", padding=10)
        build_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(build_frame, text=f"Parallel Jobs: {self.config.config['build']['parallel_jobs']}").pack(anchor='w')
        
        # Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="💾 Save Settings", 
                  command=self.save_settings).pack(side='left')
        ttk.Button(button_frame, text="🔄 Reset Defaults", 
                  command=self.reset_settings).pack(side='left', padx=(10, 0))
        ttk.Button(button_frame, text="📂 Open Config", 
                  command=self.open_config_file).pack(side='left', padx=(10, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_about_tab(self):
        """Setup about tab with Linux-specific information"""
        main_frame = ttk.Frame(self.about_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        about_text = scrolledtext.ScrolledText(main_frame, state='disabled', wrap=tk.WORD)
        about_text.pack(fill='both', expand=True)
        
        content = f"""🔐 Crypto++ Compiler Tool - Linux Edition

A powerful GUI tool for compiling C++ projects with cryptographic libraries on Linux.

🐧 LINUX FEATURES:
✅ Native package manager integration
✅ Automatic dependency detection
✅ Distribution-specific optimizations  
✅ Terminal-style output
✅ System compiler detection
✅ Multi-architecture support

📦 SUPPORTED DISTRIBUTIONS:
• Ubuntu/Debian (apt)
• Fedora/CentOS (dnf/yum)
• Arch Linux (pacman)
• openSUSE (zypper)
• Generic Linux

🔧 SUPPORTED COMPILERS:
• GCC (GNU Compiler Collection)
• Clang (LLVM)

📚 SUPPORTED LIBRARIES:
• Crypto++ (libcrypto++-dev)
• OpenSSL (libssl-dev)

🚀 QUICK START:
1. Install dependencies: Click "Install Build Tools"
2. Configure paths in Settings tab
3. Select source file and build!

💡 TIPS:
• Use package manager to install libraries
• Check System tab for compiler detection
• Debug mode adds -g -O0 flags
• Parallel build uses all CPU cores

🏠 CONFIG LOCATION:
{self.config.config_file}

🔗 INTEGRATION:
This tool integrates with:
• pkg-config for library detection
• ccache for faster compilation
• distcc for distributed builds

Version: 2.0 (Linux Edition)
Platform: {platform.system()} {platform.release()}
Architecture: {platform.machine()}
Python: {sys.version.split()[0]}

Made with ❤️ for Linux developers!
"""
        
        about_text.config(state='normal')
        about_text.insert('1.0', content)
        about_text.config(state='disabled')
    
    def get_system_info(self):
        """Get detailed system information"""
        info = []
        
        # Basic system info
        info.append(f"🐧 System: {platform.system()} {platform.release()}")
        info.append(f"📋 Distribution: {self.config.config['system']['distro']}")
        info.append(f"🏗️ Architecture: {platform.machine()}")
        info.append(f"🐍 Python: {sys.version.split()[0]}")
        info.append(f"💾 CPU Count: {os.cpu_count()}")
        
        # Compiler versions
        info.append("\n🔧 COMPILERS:")
        for compiler in ["gcc", "g++", "clang", "clang++"]:
            path = shutil.which(compiler)
            if path:
                try:
                    result = subprocess.run([compiler, "--version"], 
                                          capture_output=True, text=True, timeout=5)
                    version = result.stdout.split('\n')[0] if result.stdout else "Unknown"
                    info.append(f"  ✅ {compiler}: {version}")
                except:
                    info.append(f"  ⚠️ {compiler}: Found but version unknown")
            else:
                info.append(f"  ❌ {compiler}: Not found")
        
        # Package manager
        info.append(f"\n📦 Package Manager: {self.get_package_manager()}")
        
        # Libraries
        info.append("\n📚 LIBRARIES:")
        for lib in ["cryptopp", "openssl"]:
            status = self.check_library_installed(lib)
            info.append(f"  {'✅' if status else '❌'} {lib}: {'Installed' if status else 'Not found'}")
        
        return '\n'.join(info)
    
    def get_package_manager(self):
        """Detect package manager"""
        managers = {
            "apt": "APT (Debian/Ubuntu)",
            "dnf": "DNF (Fedora)",
            "yum": "YUM (CentOS/RHEL)",
            "pacman": "Pacman (Arch)",
            "zypper": "Zypper (openSUSE)"
        }
        
        for cmd, name in managers.items():
            if shutil.which(cmd):
                return name
        return "Unknown"
    
    def check_library_installed(self, library):
        """Check if library is installed"""
        try:
            if library == "cryptopp":
                # Check for headers and library
                for path in ["/usr/include/cryptopp", "/usr/local/include/cryptopp"]:
                    if os.path.exists(path):
                        return True
            elif library == "openssl":
                for path in ["/usr/include/openssl", "/usr/local/include/openssl"]:
                    if os.path.exists(path):
                        return True
        except:
            pass
        return False
    
    def check_system_dependencies(self):
        """Check system dependencies and show warnings"""
        missing = []
        
        # Check compilers
        if not shutil.which("g++"):
            missing.append("g++ (GNU compiler)")
        if not shutil.which("make"):
            missing.append("make (build tool)")
        
        # Check libraries
        if not self.check_library_installed("cryptopp"):
            missing.append("libcrypto++-dev (Crypto++ library)")
        if not self.check_library_installed("openssl"):
            missing.append("libssl-dev (OpenSSL library)")
        
        if missing:
            msg = "Missing dependencies detected:\n\n" + "\n".join(f"• {item}" for item in missing)
            msg += "\n\nGo to System tab to install them."
            messagebox.showwarning("Missing Dependencies", msg)
    
    def install_cryptopp(self):
        """Install Crypto++ using system package manager"""
        self.install_package(self.config.config["libraries"]["cryptopp"]["system_package"])
    
    def install_openssl(self):
        """Install OpenSSL using system package manager"""
        self.install_package("libssl-dev")
    
    def install_build_tools(self):
        """Install essential build tools"""
        packages = ["build-essential", "cmake", "pkg-config"]
        if self.config.distro == "fedora":
            packages = ["gcc-c++", "cmake", "pkgconfig"]
        elif self.config.distro == "arch":
            packages = ["base-devel", "cmake", "pkgconfig"]
        
        self.install_package(packages)
    
    def install_package(self, packages):
        """Install packages using appropriate package manager"""
        if isinstance(packages, str):
            packages = [packages]
        
        # Detect package manager and build command
        if shutil.which("apt"):
            cmd = ["sudo", "apt", "update", "&&", "sudo", "apt", "install", "-y"] + packages
        elif shutil.which("dnf"):
            cmd = ["sudo", "dnf", "install", "-y"] + packages
        elif shutil.which("yum"):
            cmd = ["sudo", "yum", "install", "-y"] + packages
        elif shutil.which("pacman"):
            cmd = ["sudo", "pacman", "-S", "--noconfirm"] + packages
        elif shutil.which("zypper"):
            cmd = ["sudo", "zypper", "install", "-y"] + packages
        else:
            messagebox.showerror("Error", "No supported package manager found!")
            return
        
        # Run in terminal
        terminal_cmd = f"x-terminal-emulator -e 'bash -c \"{' '.join(cmd)}; read -p \\\"Press Enter to close...\\\"\"\'"
        
        try:
            subprocess.Popen(terminal_cmd, shell=True)
            messagebox.showinfo("Package Installation", "Package installation started in terminal.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start package installation: {e}")
    
    def detect_compilers(self):
        """Detect available compilers and update configuration"""
        self.detect_output.config(state='normal')
        self.detect_output.delete('1.0', tk.END)
        
        compilers = ["gcc", "g++", "clang", "clang++"]
        found = []
        
        for compiler in compilers:
            path = shutil.which(compiler)
            if path:
                try:
                    result = subprocess.run([compiler, "--version"], 
                                          capture_output=True, text=True, timeout=5)
                    version = result.stdout.split('\n')[0] if result.stdout else "Unknown"
                    found.append(f"✅ {compiler}: {path}\n    Version: {version}\n")
                except:
                    found.append(f"⚠️ {compiler}: {path} (version check failed)\n")
            else:
                found.append(f"❌ {compiler}: Not found\n")
        
        self.detect_output.insert('1.0', '\n'.join(found))
        self.detect_output.config(state='disabled')
    
    def check_libraries(self):
        """Check available libraries"""
        self.detect_output.config(state='normal')
        self.detect_output.delete('1.0', tk.END)
        
        libraries = ["cryptopp", "openssl"]
        results = []
        
        for lib in libraries:
            lib_config = self.config.config["libraries"][lib]
            found_include = False
            found_lib = False
            
            # Check include directories
            for inc_dir in lib_config["include_dirs"]:
                if os.path.exists(inc_dir):
                    found_include = True
                    break
            
            # Check library directories
            for lib_dir in lib_config["lib_dirs"]:
                for lib_name in lib_config["libs"]:
                    lib_file = os.path.join(lib_dir, f"lib{lib_name}.so")
                    if os.path.exists(lib_file):
                        found_lib = True
                        break
                if found_lib:
                    break
            
            status = "✅" if (found_include and found_lib) else "⚠️" if found_include else "❌"
            results.append(f"{status} {lib}: Include={found_include}, Library={found_lib}")
        
        self.detect_output.insert('1.0', '\n'.join(results))
        self.detect_output.config(state='disabled')
    
    def browse_file(self):
        """Browse for source file"""
        filename = filedialog.askopenfilename(
            title="Select C++ Source File",
            filetypes=[
                ("C++ files", "*.cpp *.cxx *.cc *.c++"),
                ("C files", "*.c"),
                ("Header files", "*.h *.hpp"),
                ("All files", "*.*")
            ],
            initialdir=self.config.config["paths"]["source_dir"]
        )
        if filename:
            self.source_var.set(filename)
            self.config.config["paths"]["source_dir"] = str(Path(filename).parent)
    
    def browse_path(self, path_key):
        """Browse for directory path"""
        directory = filedialog.askdirectory(
            title=f"Select {path_key.replace('_', ' ').title()} Directory",
            initialdir=self.path_vars[path_key].get()
        )
        if directory:
            self.path_vars[path_key].set(directory)
    
    def build_async(self):
        """Start build process in a separate thread"""
        if self.build_process and self.build_process.poll() is None:
            messagebox.showwarning("Build in Progress", "A build is already running!")
            return
        
        threading.Thread(target=self.build, daemon=True).start()
    
    def build(self):
        """Main build function optimized for Linux"""
        try:
            # Update UI
            self.root.after(0, lambda: self.build_btn.config(state='disabled'))
            self.root.after(0, lambda: self.progress.pack(side='right', fill='x', expand=True, padx=(10, 0)))
            self.root.after(0, lambda: self.progress.start())
            self.root.after(0, lambda: self.status_var.set("Building..."))
            
            # Clear output
            self.root.after(0, self.clear_output)
            
            # Get build parameters
            compiler = self.compiler_var.get()
            library = self.library_var.get()
            source_file = self.source_var.get()
            build_type = self.build_type_var.get()
            build_mode = self.build_mode_var.get()
            
            # Validate source file
            if not os.path.isfile(source_file):
                raise Exception(f"Source file not found: {source_file}")
            
            # Build command
            cmd = self.build_command(compiler, library, source_file, build_type, build_mode)
            
            self.output_queue.put(f"🔨 Building with {compiler.upper()} + {library.upper()} ({build_mode})\n")
            self.output_queue.put(f"📁 Working directory: {Path(source_file).parent}\n")
            self.output_queue.put(f"⚡ Command: {' '.join(cmd)}\n\n")
            
            # Execute build
            env = os.environ.copy()
            if self.parallel_build_var.get():
                env['MAKEFLAGS'] = f'-j{self.config.config["build"]["parallel_jobs"]}'
            
            self.build_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=str(Path(source_file).parent),
                env=env
            )
            
            # Read output with color coding
            for line in self.build_process.stdout:
                self.output_queue.put(line)
            
            self.build_process.wait()
            
            # Check result
            if self.build_process.returncode == 0:
                self.output_queue.put("\n✅ Build successful!\n")
                
                # Auto-run if enabled
                if self.auto_run_var.get() and build_type == "executable":
                    self.root.after(0, lambda: self.run_executable(compiler, source_file))
                    
                self.root.after(0, lambda: self.status_var.set("Build successful"))
            else:
                self.output_queue.put(f"\n❌ Build failed with exit code {self.build_process.returncode}\n")
                self.root.after(0, lambda: self.status_var.set("Build failed"))
                
        except Exception as e:
            self.output_queue.put(f"\n💥 Error: {str(e)}\n")
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
        
        finally:
            # Restore UI
            self.root.after(0, lambda: self.build_btn.config(state='normal'))
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.progress.pack_forget())
    
    def build_command(self, compiler, library, source_file, build_type, build_mode):
        """Generate Linux-optimized build command"""
        config = self.config.config
        
        compiler_config = config["compilers"][compiler]
        lib_config = config["libraries"][library]
        
        cmd = [compiler_config["executable"]]
        
        # Add flags based on build mode
        if build_mode == "debug":
            cmd.extend(compiler_config["debug_flags"])
        else:
            cmd.extend(compiler_config["flags"])
        
        # Include directories
        for inc_dir in lib_config["include_dirs"]:
            if os.path.exists(inc_dir):
                cmd.append(f"-I{inc_dir}")
        
        # Source file
        cmd.append(source_file)
        
        # Output file
        base_name = Path(source_file).stem
        output_dir = Path(source_file).parent / config["build"]["output_dir"] / compiler
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if build_type == "shared_library":
            cmd.append("-shared")
            cmd.append("-fPIC")
            output_file = output_dir / f"lib{base_name}.so"
        elif build_type == "static_library":
            # For static libraries, we'll use ar after compilation
            output_file = output_dir / f"{base_name}.o"
        else:
            output_file = output_dir / f"{base_name}_{compiler}"
        
        cmd.extend(["-o", str(output_file)])
        
        # Library directories
        for lib_dir in lib_config["lib_dirs"]:
            if os.path.exists(lib_dir):
                cmd.append(f"-L{lib_dir}")
        
        # Libraries
        for lib in lib_config["libs"]:
            cmd.append(f"-l{lib}")
        
        # Additional compiler libraries
        cmd.extend(compiler_config["libs"])
        
        # Linux-specific optimizations
        if compiler == "gcc":
            cmd.extend(["-march=native", "-mtune=native"])
        
        return cmd
    
    def run_executable(self, compiler, source_file):
        """Run the built executable"""
        base_name = Path(source_file).stem
        output_dir = Path(source_file).parent / self.config.config["build"]["output_dir"] / compiler
        exe_file = output_dir / f"{base_name}_{compiler}"
        
        if exe_file.exists():
            self.output_queue.put(f"\n🚀 Running {exe_file.name}...\n")
            self.output_queue.put("=" * 60 + "\n")
            
            try:
                run_process = subprocess.Popen(
                    [str(exe_file)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    cwd=str(output_dir),
                    encoding='utf-8',
                    errors='replace'
                )
                
                for line in run_process.stdout:
                    self.output_queue.put(line)
                
                run_process.wait()
                self.output_queue.put("=" * 60 + "\n")
                self.output_queue.put(f"Program finished with exit code {run_process.returncode}\n")
                
            except Exception as e:
                self.output_queue.put(f"Error running executable: {e}\n")
        else:
            self.output_queue.put(f"❌ Executable not found: {exe_file}\n")
    
    def stop_build(self):
        """Stop the current build process"""
        if self.build_process and self.build_process.poll() is None:
            self.build_process.terminate()
            self.output_queue.put("\n⏹️ Build stopped by user\n")
            self.status_var.set("Build stopped")
    
    def clean_build(self):
        """Clean build artifacts"""
        try:
            source_file = self.source_var.get()
            if not source_file:
                messagebox.showwarning("No Source", "Please select a source file first.")
                return
            
            build_dir = Path(source_file).parent / self.config.config["build"]["output_dir"]
            if build_dir.exists():
                import shutil
                shutil.rmtree(build_dir)
                self.output_queue.put(f"🧹 Cleaned build directory: {build_dir}\n")
                self.status_var.set("Build directory cleaned")
            else:
                self.output_queue.put("🧹 No build artifacts to clean\n")
                
        except Exception as e:
            messagebox.showerror("Clean Error", f"Failed to clean build directory: {e}")
    
    def clear_output(self):
        """Clear the output text area"""
        self.output.config(state='normal')
        self.output.delete('1.0', tk.END)
        self.output.config(state='disabled')
    
    def copy_output(self):
        """Copy output to clipboard"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.output.get('1.0', tk.END))
            self.status_var.set("Output copied to clipboard")
        except Exception as e:
            messagebox.showerror("Copy Error", f"Failed to copy output: {e}")
    
    def save_log(self):
        """Save build log to file"""
        filename = filedialog.asksaveasfilename(
            title="Save Build Log",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialdir=self.config.config["paths"]["source_dir"]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.output.get('1.0', tk.END))
                messagebox.showinfo("Success", f"Log saved to {filename}")
                self.status_var.set("Log saved successfully")
            except Exception as e:
                messagebox.showerror("Save Error", f"Failed to save log: {e}")
    
    def save_settings(self):
        """Save current settings"""
        # Update paths from UI
        for key, var in self.path_vars.items():
            self.config.config["paths"][key] = var.get()
        
        if self.config.save_config():
            messagebox.showinfo("Success", "Settings saved successfully!")
            self.status_var.set("Settings saved")
        else:
            messagebox.showerror("Error", "Failed to save settings!")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        if messagebox.askyesno("Confirm Reset", "Reset all settings to defaults?"):
            self.config.config = self.config.default_config.copy()
            
            # Update UI
            for key, var in self.path_vars.items():
                if key in self.config.config["paths"]:
                    var.set(self.config.config["paths"][key])
            
            self.status_var.set("Settings reset to defaults")
    
    def open_config_file(self):
        """Open config file in default editor"""
        try:
            subprocess.Popen(["xdg-open", str(self.config.config_file)])
        except:
            try:
                subprocess.Popen(["gedit", str(self.config.config_file)])
            except:
                messagebox.showinfo("Config File", 
                    f"Config file location:\n{self.config.config_file}\n\n"
                    f"Open with your preferred text editor.")
    
    def process_queue(self):
        """Process output queue and update UI with color coding"""
        try:
            while True:
                line = self.output_queue.get_nowait()
                self.output.config(state='normal')
                
                # Simple color coding for Linux terminal style
                if "error:" in line.lower() or "❌" in line:
                    self.output.tag_config("error", foreground="#ff4444")
                    self.output.insert(tk.END, line, "error")
                elif "warning:" in line.lower() or "⚠️" in line:
                    self.output.tag_config("warning", foreground="#ffaa00")
                    self.output.insert(tk.END, line, "warning")
                elif "✅" in line or "successful" in line.lower():
                    self.output.tag_config("success", foreground="#44ff44")
                    self.output.insert(tk.END, line, "success")
                elif line.startswith("🔨") or line.startswith("📁") or line.startswith("⚡"):
                    self.output.tag_config("info", foreground="#44aaff")
                    self.output.insert(tk.END, line, "info")
                else:
                    self.output.insert(tk.END, line)
                
                self.output.see(tk.END)
                self.output.config(state='disabled')
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_queue)
    
    def run(self):
        """Start the GUI application"""
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        self.status_var.set(f"Ready - {self.config.config['system']['distro']} detected")
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-b>', lambda e: self.build_async())
        self.root.bind('<Control-s>', lambda e: self.save_settings())
        self.root.bind('<Control-l>', lambda e: self.clear_output())
        self.root.bind('<F5>', lambda e: self.build_async())
        
        self.root.mainloop()

def main():
    """Main entry point with Linux-specific error handling"""
    try:
        # Check Python version
        if sys.version_info < (3, 6):
            print("Error: Python 3.6 or higher is required")
            sys.exit(1)
        
        # Check if running on Linux
        if platform.system() != "Linux":
            print(f"Warning: This tool is optimized for Linux, detected {platform.system()}")
        
        # Check for GUI support
        try:
            import tkinter
        except ImportError:
            print("Error: tkinter not available. Install with:")
            print("  Ubuntu/Debian: sudo apt install python3-tk")
            print("  Fedora: sudo dnf install tkinter")
            print("  Arch: sudo pacman -S tk")
            sys.exit(1)
        
        app = LinuxCompilerGUI()
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()