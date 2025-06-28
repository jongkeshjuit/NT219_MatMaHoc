#!/usr/bin/env python3
"""
Crypto++ Compiler GUI Tool
A simple GUI for compiling C++ projects with multiple compilers (GCC, Clang, MSVC)
and crypto libraries (Crypto++, OpenSSL)
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import subprocess
import threading
import os
import json
from pathlib import Path
import queue
import time

class CompilerConfig:
    """Configuration manager for compiler paths and settings"""
    
    def __init__(self):
        self.config_file = "compiler_config.json"
        self.default_config = {
            "paths": {
                "cryptopp_root": "D:/cryptopp-libs",
                "openssl_root": "D:/openssl350", 
                "msys64_root": "C:/msys64/mingw64",
                "source_dir": "."
            },
            "compilers": {
                "gcc": {
                    "executable": "C:/msys64/mingw64/bin/g++.exe",
                    "flags": ["-g2", "-O3", "-DNDEBUG", "-Wall", "-std=c++17"],
                    "libs": ["-lpthread"]
                },
                "clang": {
                    "executable": "C:/msys64/mingw64/bin/clang++.exe", 
                    "flags": ["-g2", "-O3", "-DNDEBUG", "-Wall", "-std=c++17"],
                    "libs": ["-lpthread"]
                },
                "msvc": {
                    "executable": "cl.exe",
                    "flags": ["/MTd", "/O2", "/W4", "/nologo", "/EHsc"],
                    "libs": ["crypt32.lib", "ws2_32.lib"]
                }
            },
            "libraries": {
                "cryptopp": {
                    "gcc_lib": "cryptopp",
                    "clang_lib": "cryptopp", 
                    "msvc_lib": "cryptlib.lib"
                },
                "openssl": {
                    "gcc_lib": ["ssl", "crypto"],
                    "clang_lib": ["ssl", "crypto"],
                    "msvc_lib": ["libssl.lib", "libcrypto.lib"]
                }
            }
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
        
        # Return default config and save it
        self.save_config(self.default_config)
        return self.default_config.copy()
    
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

class CompilerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.config = CompilerConfig()
        self.build_process = None
        self.output_queue = queue.Queue()
        
        # Variables
        self.compiler_var = tk.StringVar(value="gcc")
        self.library_var = tk.StringVar(value="cryptopp") 
        self.source_var = tk.StringVar(value="main.cpp")
        self.build_type_var = tk.StringVar(value="executable")
        self.auto_run_var = tk.BooleanVar(value=True)
        
        self.setup_ui()
        self.setup_styles()
        
        # Start output queue processor
        self.process_queue()
    
    def setup_ui(self):
        """Setup the main UI"""
        self.root.title("🔐 Crypto++ Compiler Tool")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Build tab
        self.build_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.build_frame, text="Build")
        self.setup_build_tab()
        
        # Config tab
        self.config_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.config_frame, text="Settings")
        self.setup_config_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                                   relief='sunken', anchor='w')
        self.status_bar.pack(side='bottom', fill='x')
    
    def setup_build_tab(self):
        """Setup the build configuration tab"""
        # Main container with padding
        main_frame = ttk.Frame(self.build_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Top frame for controls
        controls_frame = ttk.LabelFrame(main_frame, text="Build Configuration", padding=10)
        controls_frame.pack(fill='x', pady=(0, 10))
        
        # Row 1: Compiler and Library
        row1 = ttk.Frame(controls_frame)
        row1.pack(fill='x', pady=(0, 10))
        
        ttk.Label(row1, text="Compiler:").pack(side='left')
        compiler_combo = ttk.Combobox(row1, textvariable=self.compiler_var,
                                    values=["gcc", "clang", "msvc"], 
                                    state="readonly", width=10)
        compiler_combo.pack(side='left', padx=(5, 20))
        
        ttk.Label(row1, text="Library:").pack(side='left')
        library_combo = ttk.Combobox(row1, textvariable=self.library_var,
                                   values=["cryptopp", "openssl"],
                                   state="readonly", width=10)
        library_combo.pack(side='left', padx=(5, 20))
        
        ttk.Label(row1, text="Type:").pack(side='left')
        type_combo = ttk.Combobox(row1, textvariable=self.build_type_var,
                                values=["executable", "shared_library"],
                                state="readonly", width=12)
        type_combo.pack(side='left', padx=(5, 0))
        
        # Row 2: Source file selection
        row2 = ttk.Frame(controls_frame)
        row2.pack(fill='x', pady=(0, 10))
        
        ttk.Label(row2, text="Source File:").pack(side='left')
        source_entry = ttk.Entry(row2, textvariable=self.source_var, width=40)
        source_entry.pack(side='left', fill='x', expand=True, padx=(5, 5))
        
        browse_btn = ttk.Button(row2, text="📁 Browse", command=self.browse_file)
        browse_btn.pack(side='right')
        
        # Row 3: Options and Build button
        row3 = ttk.Frame(controls_frame)
        row3.pack(fill='x')
        
        auto_run_check = ttk.Checkbutton(row3, text="Auto-run after build", 
                                       variable=self.auto_run_var)
        auto_run_check.pack(side='left')
        
        # Build button (right side)
        button_frame = ttk.Frame(row3)
        button_frame.pack(side='right')
        
        self.build_btn = ttk.Button(button_frame, text="🔨 Build & Run", 
                                   command=self.build_async, style="Accent.TButton")
        self.build_btn.pack(side='left', padx=(5, 0))
        
        stop_btn = ttk.Button(button_frame, text="⏹️ Stop", 
                            command=self.stop_build)
        stop_btn.pack(side='left', padx=(5, 0))
        
        # Progress bar
        self.progress = ttk.Progressbar(controls_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=(10, 0))
        self.progress.pack_forget()  # Hidden by default
        
        # Output area
        output_frame = ttk.LabelFrame(main_frame, text="Build Output", padding=5)
        output_frame.pack(fill='both', expand=True)
        
        self.output = scrolledtext.ScrolledText(output_frame, height=15,
                                               font=('Consolas', 10),
                                               wrap=tk.WORD,
                                               state='disabled')
        self.output.pack(fill='both', expand=True)
        
        # Output control buttons
        output_controls = ttk.Frame(output_frame)
        output_controls.pack(fill='x', pady=(5, 0))
        
        ttk.Button(output_controls, text="Clear", 
                  command=self.clear_output).pack(side='left')
        ttk.Button(output_controls, text="Save Log", 
                  command=self.save_log).pack(side='left', padx=(5, 0))
    
    def setup_config_tab(self):
        """Setup the configuration tab"""
        # Scrollable frame for config
        canvas = tk.Canvas(self.config_frame)
        scrollbar = ttk.Scrollbar(self.config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Paths configuration
        paths_frame = ttk.LabelFrame(scrollable_frame, text="Library Paths", padding=10)
        paths_frame.pack(fill='x', padx=10, pady=5)
        
        self.path_vars = {}
        for key, value in self.config.config["paths"].items():
            frame = ttk.Frame(paths_frame)
            frame.pack(fill='x', pady=2)
            
            ttk.Label(frame, text=f"{key.replace('_', ' ').title()}:", 
                     width=15).pack(side='left')
            
            var = tk.StringVar(value=value)
            self.path_vars[key] = var
            
            entry = ttk.Entry(frame, textvariable=var, width=50)
            entry.pack(side='left', fill='x', expand=True, padx=(5, 5))
            
            ttk.Button(frame, text="📁", width=3,
                      command=lambda k=key: self.browse_path(k)).pack(side='right')
        
        # Compiler settings
        compiler_frame = ttk.LabelFrame(scrollable_frame, text="Compiler Settings", padding=10)
        compiler_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(compiler_frame, text="Compiler executables and flags can be modified here.", 
                 style="TLabel").pack(anchor='w')
        
        # Save/Reset buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="💾 Save Settings", 
                  command=self.save_settings).pack(side='left')
        ttk.Button(button_frame, text="🔄 Reset to Defaults", 
                  command=self.reset_settings).pack(side='left', padx=(10, 0))
        ttk.Button(button_frame, text="📂 Open Config File", 
                  command=self.open_config_file).pack(side='left', padx=(10, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_styles(self):
        """Setup custom styles"""
        style = ttk.Style()
        
        # Try to use a modern theme
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Custom button style
        style.configure("Accent.TButton",
                       font=('Segoe UI', 10, 'bold'))
    
    def browse_file(self):
        """Browse for source file"""
        filename = filedialog.askopenfilename(
            title="Select C++ Source File",
            filetypes=[
                ("C++ files", "*.cpp *.cxx *.cc *.c++"),
                ("C files", "*.c"),
                ("All files", "*.*")
            ],
            initialdir=self.config.config["paths"]["source_dir"]
        )
        if filename:
            self.source_var.set(filename)
            # Update source directory
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
        """Main build function"""
        try:
            # Update UI
            self.root.after(0, lambda: self.build_btn.config(state='disabled'))
            self.root.after(0, lambda: self.progress.pack(fill='x', pady=(10, 0)))
            self.root.after(0, lambda: self.progress.start())
            self.root.after(0, lambda: self.status_var.set("Building..."))
            
            # Clear output
            self.root.after(0, self.clear_output)
            
            # Get build parameters
            compiler = self.compiler_var.get()
            library = self.library_var.get()
            source_file = self.source_var.get()
            build_type = self.build_type_var.get()
            
            # Build command
            cmd = self.build_command(compiler, library, source_file, build_type)
            
            self.output_queue.put(f"🔨 Building with {compiler.upper()} + {library.upper()}\n")
            self.output_queue.put(f"Command: {' '.join(cmd)}\n\n")
            
            # Execute build
            self.build_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=str(Path(source_file).parent) if os.path.isfile(source_file) else "."
            )
            
            # Read output
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
            self.output_queue.put(f"\nError: {str(e)}\n")
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
        
        finally:
            # Restore UI
            self.root.after(0, lambda: self.build_btn.config(state='normal'))
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.progress.pack_forget())
    
    def build_command(self, compiler, library, source_file, build_type):
        """Generate build command based on parameters"""
        config = self.config.config
        
        compiler_config = config["compilers"][compiler]
        lib_config = config["libraries"][library]
        paths = config["paths"]
        
        cmd = [compiler_config["executable"]]
        cmd.extend(compiler_config["flags"])
        
        # Include directory
        if library == "cryptopp":
            include_dir = f"{paths['cryptopp_root']}/include"
            lib_dir = f"{paths['cryptopp_root']}/lib/{compiler}"
        else:  # openssl
            include_dir = f"{paths['openssl_root']}/{compiler}/include"
            lib_dir = f"{paths['openssl_root']}/{compiler}/lib" + ("64" if compiler != "msvc" else "")
        
        # Source file
        cmd.append(source_file)
        
        # Output file
        base_name = Path(source_file).stem
        output_dir = Path(source_file).parent / compiler
        output_dir.mkdir(exist_ok=True)
        
        if build_type == "shared_library":
            if compiler == "msvc":
                output_file = output_dir / f"{base_name}_{compiler}.dll"
            else:
                output_file = output_dir / f"{base_name}_{compiler}.dll"
        else:
            output_file = output_dir / f"{base_name}_{compiler}.exe"
        
        # Compiler-specific syntax
        if compiler == "msvc":
            cmd.extend([f"/I{include_dir}"])
            cmd.extend([f"/Fo{output_dir}/"])
            cmd.extend(["/link"])
            if build_type == "shared_library":
                cmd.extend(["/DLL"])
            cmd.extend([f"/OUT:{output_file}"])
            cmd.extend([f"/LIBPATH:{lib_dir}"])
            
            # Libraries
            if library == "cryptopp":
                cmd.append(lib_config["msvc_lib"])
            else:
                cmd.extend(lib_config["msvc_lib"])
            cmd.extend(compiler_config["libs"])
            cmd.append("/MACHINE:X64")
        else:
            if build_type == "shared_library":
                cmd.append("-shared")
            cmd.extend([f"-I{include_dir}"])
            cmd.extend(["-o", str(output_file)])
            cmd.extend([f"-L{lib_dir}"])
            
            # Libraries  
            if library == "cryptopp":
                cmd.append(f"-l{lib_config[f'{compiler}_lib']}")
            else:
                for lib in lib_config[f"{compiler}_lib"]:
                    cmd.append(f"-l{lib}")
            cmd.extend(compiler_config["libs"])
        
        return cmd
    
    def run_executable(self, compiler, source_file):
        """Run the built executable"""
        base_name = Path(source_file).stem
        output_dir = Path(source_file).parent / compiler
        exe_file = output_dir / f"{base_name}_{compiler}.exe"
        
        if exe_file.exists():
            self.output_queue.put(f"\n🚀 Running {exe_file.name}...\n")
            self.output_queue.put("=" * 50 + "\n")
            
            try:
                run_process = subprocess.Popen(
                    [str(exe_file)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    cwd=str(output_dir),
                    encoding="utf-8",
                    errors="replace"
                )
                
                for line in run_process.stdout:
                    self.output_queue.put(line)
                
                run_process.wait()
                self.output_queue.put("=" * 50 + "\n")
                self.output_queue.put(f"Program finished with exit code {run_process.returncode}\n")
                
            except Exception as e:
                self.output_queue.put(f"Error running executable: {e}\n")
    
    def stop_build(self):
        """Stop the current build process"""
        if self.build_process and self.build_process.poll() is None:
            self.build_process.terminate()
            self.output_queue.put("\n⏹️ Build stopped by user\n")
            self.status_var.set("Build stopped")
    
    def clear_output(self):
        """Clear the output text area"""
        self.output.config(state='normal')
        self.output.delete(1.0, tk.END)
        self.output.config(state='disabled')
    
    def save_log(self):
        """Save build log to file"""
        filename = filedialog.asksaveasfilename(
            title="Save Build Log",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(self.output.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Log saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log: {e}")
    
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
                var.set(self.config.config["paths"][key])
            
            self.status_var.set("Settings reset to defaults")
    
    def open_config_file(self):
        """Open config file in default editor"""
        try:
            os.startfile(self.config.config_file)
        except:
            messagebox.showinfo("Config File", f"Config file location:\n{os.path.abspath(self.config.config_file)}")
    
    def process_queue(self):
        """Process output queue and update UI"""
        try:
            while True:
                line = self.output_queue.get_nowait()
                self.output.config(state='normal')
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
        
        self.status_var.set("Ready - Select source file and click Build")
        self.root.mainloop()

def main():
    """Main entry point"""
    try:
        app = CompilerGUI()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()