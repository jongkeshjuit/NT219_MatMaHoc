import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import json
import threading
from pathlib import Path

class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Compiler Build Tool")
        self.root.geometry("800x700")
        
        # Load configuration
        self.config_file = "compiler_config.json"
        self.config = self.load_config()
        
        self.setup_ui()
        self.load_saved_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        default_config = {
            "gcc_path": "C:\\msys64\\mingw64\\bin\\g++.exe",
            "clang_path": "C:\\msys64\\mingw64\\bin\\clang++.exe",
            "msvc_path": "cl.exe",
            "csc_path": "csc.exe",
            "javac_path": "javac",
            "java_path": "java",
            "cryptopp_include": "",
            "cryptopp_lib_gcc": "",
            "cryptopp_lib_clang": "",
            "cryptopp_lib_msvc": "",
            "openssl_include_gcc": "",
            "openssl_lib_gcc": "",
            "openssl_include_clang": "",
            "openssl_lib_clang": "",
            "openssl_include_msvc": "",
            "openssl_lib_msvc": "",
            "jdk_include": "",
            "jdk_include_win32": ""
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
        except Exception as e:
            print(f"Error loading config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Build tab
        self.build_frame = ttk.Frame(notebook)
        notebook.add(self.build_frame, text="Build")
        self.setup_build_tab()
        
        # Configuration tab
        self.config_frame = ttk.Frame(notebook)
        notebook.add(self.config_frame, text="Configuration")
        self.setup_config_tab()
    
    def setup_build_tab(self):
        """Setup the build tab"""
        # Language selection
        lang_frame = ttk.LabelFrame(self.build_frame, text="Language & Build Type")
        lang_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(lang_frame, text="Language:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.language_var = tk.StringVar(value="C++")
        language_combo = ttk.Combobox(lang_frame, textvariable=self.language_var, 
                                     values=["C++", "C#", "Java", "JNI"], state="readonly")
        language_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        language_combo.bind("<<ComboboxSelected>>", self.on_language_change)
        
        ttk.Label(lang_frame, text="Compiler:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.compiler_var = tk.StringVar(value="GCC")
        self.compiler_combo = ttk.Combobox(lang_frame, textvariable=self.compiler_var, 
                                          values=["GCC", "Clang", "MSVC"], state="readonly")
        self.compiler_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=2)
        
        ttk.Label(lang_frame, text="Build Type:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.build_type_var = tk.StringVar(value="Executable")
        build_type_combo = ttk.Combobox(lang_frame, textvariable=self.build_type_var, 
                                       values=["Executable", "Shared Library"], state="readonly")
        build_type_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        
        ttk.Label(lang_frame, text="Library:").grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.library_var = tk.StringVar(value="None")
        library_combo = ttk.Combobox(lang_frame, textvariable=self.library_var, 
                                    values=["None", "CryptoPP", "OpenSSL"], state="readonly")
        library_combo.grid(row=1, column=3, sticky="ew", padx=5, pady=2)
        
        # Configure grid weights
        lang_frame.columnconfigure(1, weight=1)
        lang_frame.columnconfigure(3, weight=1)
        
        # File selection
        file_frame = ttk.LabelFrame(self.build_frame, text="File Selection")
        file_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(file_frame, text="Input File:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.input_file_var = tk.StringVar()
        input_entry = ttk.Entry(file_frame, textvariable=self.input_file_var)
        input_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(file_frame, text="Browse", command=self.browse_input_file).grid(row=0, column=2, padx=5, pady=2)
        
        ttk.Label(file_frame, text="Output File:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.output_file_var = tk.StringVar()
        output_entry = ttk.Entry(file_frame, textvariable=self.output_file_var)
        output_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(file_frame, text="Browse", command=self.browse_output_file).grid(row=1, column=2, padx=5, pady=2)
        
        file_frame.columnconfigure(1, weight=1)
        
        # Build options
        options_frame = ttk.LabelFrame(self.build_frame, text="Build Options")
        options_frame.pack(fill="x", padx=5, pady=5)
        
        self.debug_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Debug Mode", variable=self.debug_var).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        self.optimize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Optimization", variable=self.optimize_var).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        self.auto_run_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Auto Run", variable=self.auto_run_var).grid(row=0, column=2, sticky="w", padx=5, pady=2)
        
        # Command preview
        cmd_frame = ttk.LabelFrame(self.build_frame, text="Command Preview")
        cmd_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.command_text = tk.Text(cmd_frame, height=6, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(cmd_frame, orient="vertical", command=self.command_text.yview)
        self.command_text.configure(yscrollcommand=scrollbar.set)
        
        self.command_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Build button and output
        action_frame = ttk.Frame(self.build_frame)
        action_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(action_frame, text="Update Command", command=self.update_command_preview).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Build", command=self.build_project).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Run Executable", command=self.run_executable).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Debug", command=self.debug_executable).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Open Output Folder", command=self.open_output_folder).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Clear Output", command=self.clear_output).pack(side="left", padx=5)
        
        # Output with tabs for different types
        output_notebook = ttk.Notebook(self.build_frame)
        output_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Build output tab
        build_output_frame = ttk.Frame(output_notebook)
        output_notebook.add(build_output_frame, text="Build Output")
        
        self.output_text = tk.Text(build_output_frame, height=8)
        build_scrollbar = ttk.Scrollbar(build_output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=build_scrollbar.set)
        
        self.output_text.pack(side="left", fill="both", expand=True)
        build_scrollbar.pack(side="right", fill="y")
        
        # Runtime output tab
        runtime_output_frame = ttk.Frame(output_notebook)
        output_notebook.add(runtime_output_frame, text="Runtime Output")
        
        self.runtime_text = tk.Text(runtime_output_frame, height=8)
        runtime_scrollbar = ttk.Scrollbar(runtime_output_frame, orient="vertical", command=self.runtime_text.yview)
        self.runtime_text.configure(yscrollcommand=runtime_scrollbar.set)
        
        self.runtime_text.pack(side="left", fill="both", expand=True)
        runtime_scrollbar.pack(side="right", fill="y")
        
        # Debug output tab
        debug_output_frame = ttk.Frame(output_notebook)
        output_notebook.add(debug_output_frame, text="Debug Output")
        
        self.debug_text = tk.Text(debug_output_frame, height=8)
        debug_scrollbar = ttk.Scrollbar(debug_output_frame, orient="vertical", command=self.debug_text.yview)
        self.debug_text.configure(yscrollcommand=debug_scrollbar.set)
        
        self.debug_text.pack(side="left", fill="both", expand=True)
        debug_scrollbar.pack(side="right", fill="y")
        
        # Error analysis frame
        error_frame = ttk.LabelFrame(debug_output_frame, text="Error Analysis")
        error_frame.pack(fill="x", padx=5, pady=5)
        
        self.error_summary = tk.Text(error_frame, height=3, bg="#fff2f2")
        self.error_summary.pack(fill="x", padx=5, pady=5)
    
    def setup_config_tab(self):
        """Setup the configuration tab"""
        # Create scrollable frame
        canvas = tk.Canvas(self.config_frame)
        scrollbar_config = ttk.Scrollbar(self.config_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_config.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_config.pack(side="right", fill="y")
        
        # Compiler paths
        compiler_frame = ttk.LabelFrame(scrollable_frame, text="Compiler Paths")
        compiler_frame.pack(fill="x", padx=5, pady=5)
        
        self.config_vars = {}
        
        compiler_configs = [
            ("GCC Path", "gcc_path"),
            ("Clang Path", "clang_path"),
            ("MSVC Path", "msvc_path"),
            ("C# Compiler Path", "csc_path"),
            ("Java Compiler Path", "javac_path"),
            ("Java Runtime Path", "java_path")
        ]
        
        for i, (label, key) in enumerate(compiler_configs):
            ttk.Label(compiler_frame, text=f"{label}:").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            var = tk.StringVar()
            self.config_vars[key] = var
            entry = ttk.Entry(compiler_frame, textvariable=var, width=50)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            ttk.Button(compiler_frame, text="Browse", 
                      command=lambda k=key: self.browse_config_file(k)).grid(row=i, column=2, padx=5, pady=2)
        
        compiler_frame.columnconfigure(1, weight=1)
        
        # CryptoPP paths
        cryptopp_frame = ttk.LabelFrame(scrollable_frame, text="CryptoPP Library Paths")
        cryptopp_frame.pack(fill="x", padx=5, pady=5)
        
        cryptopp_configs = [
            ("Include Directory", "cryptopp_include"),
            ("GCC Library Directory", "cryptopp_lib_gcc"),
            ("Clang Library Directory", "cryptopp_lib_clang"),
            ("MSVC Library Directory", "cryptopp_lib_msvc")
        ]
        
        for i, (label, key) in enumerate(cryptopp_configs):
            ttk.Label(cryptopp_frame, text=f"{label}:").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            var = tk.StringVar()
            self.config_vars[key] = var
            entry = ttk.Entry(cryptopp_frame, textvariable=var, width=50)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            ttk.Button(cryptopp_frame, text="Browse", 
                      command=lambda k=key: self.browse_config_directory(k)).grid(row=i, column=2, padx=5, pady=2)
        
        cryptopp_frame.columnconfigure(1, weight=1)
        
        # OpenSSL paths
        openssl_frame = ttk.LabelFrame(scrollable_frame, text="OpenSSL Library Paths")
        openssl_frame.pack(fill="x", padx=5, pady=5)
        
        openssl_configs = [
            ("GCC Include Directory", "openssl_include_gcc"),
            ("GCC Library Directory", "openssl_lib_gcc"),
            ("Clang Include Directory", "openssl_include_clang"),
            ("Clang Library Directory", "openssl_lib_clang"),
            ("MSVC Include Directory", "openssl_include_msvc"),
            ("MSVC Library Directory", "openssl_lib_msvc")
        ]
        
        for i, (label, key) in enumerate(openssl_configs):
            ttk.Label(openssl_frame, text=f"{label}:").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            var = tk.StringVar()
            self.config_vars[key] = var
            entry = ttk.Entry(openssl_frame, textvariable=var, width=50)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            ttk.Button(openssl_frame, text="Browse", 
                      command=lambda k=key: self.browse_config_directory(k)).grid(row=i, column=2, padx=5, pady=2)
        
        openssl_frame.columnconfigure(1, weight=1)
        
        # JDK paths
        jdk_frame = ttk.LabelFrame(scrollable_frame, text="JDK Paths (for JNI)")
        jdk_frame.pack(fill="x", padx=5, pady=5)
        
        jdk_configs = [
            ("JDK Include Directory", "jdk_include"),
            ("JDK Win32 Include Directory", "jdk_include_win32")
        ]
        
        for i, (label, key) in enumerate(jdk_configs):
            ttk.Label(jdk_frame, text=f"{label}:").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            var = tk.StringVar()
            self.config_vars[key] = var
            entry = ttk.Entry(jdk_frame, textvariable=var, width=50)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            ttk.Button(jdk_frame, text="Browse", 
                      command=lambda k=key: self.browse_config_directory(k)).grid(row=i, column=2, padx=5, pady=2)
        
        jdk_frame.columnconfigure(1, weight=1)
        
        # Save button
        save_frame = ttk.Frame(scrollable_frame)
        save_frame.pack(fill="x", padx=5, pady=10)
        ttk.Button(save_frame, text="Save Configuration", command=self.save_configuration).pack()
    
    def load_saved_config(self):
        """Load saved configuration into UI"""
        for key, var in self.config_vars.items():
            if key in self.config:
                var.set(self.config[key])
    
    def on_language_change(self, event=None):
        """Handle language change"""
        language = self.language_var.get()
        if language == "C++":
            self.compiler_combo.configure(values=["GCC", "Clang", "MSVC"])
        elif language == "C#":
            self.compiler_combo.configure(values=["CSC"])
            self.compiler_var.set("CSC")
        elif language == "Java":
            self.compiler_combo.configure(values=["JAVAC"])
            self.compiler_var.set("JAVAC")
        elif language == "JNI":
            self.compiler_combo.configure(values=["GCC", "Clang", "MSVC"])
    
    def browse_input_file(self):
        """Browse for input file"""
        language = self.language_var.get()
        if language == "C++":
            filetypes = [("C++ files", "*.cpp *.cxx *.cc"), ("C files", "*.c"), ("All files", "*.*")]
        elif language == "C#":
            filetypes = [("C# files", "*.cs"), ("All files", "*.*")]
        elif language == "Java" or language == "JNI":
            filetypes = [("Java files", "*.java"), ("All files", "*.*")]
        else:
            filetypes = [("All files", "*.*")]
        
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            self.input_file_var.set(filename)
            # Auto-generate output filename
            self.auto_generate_output_filename()
    
    def browse_output_file(self):
        """Browse for output file"""
        language = self.language_var.get()
        build_type = self.build_type_var.get()
        
        if language == "C++":
            if build_type == "Executable":
                filetypes = [("Executable files", "*.exe"), ("All files", "*.*")]
            else:
                filetypes = [("DLL files", "*.dll"), ("All files", "*.*")]
        elif language == "C#":
            filetypes = [("Executable files", "*.exe"), ("All files", "*.*")]
        elif language == "Java":
            filetypes = [("Class files", "*.class"), ("All files", "*.*")]
        else:
            filetypes = [("All files", "*.*")]
        
        filename = filedialog.asksaveasfilename(filetypes=filetypes)
        if filename:
            self.output_file_var.set(filename)
    
    def auto_generate_output_filename(self):
        """Auto-generate output filename based on input"""
        input_file = self.input_file_var.get()
        if not input_file:
            return
        
        input_path = Path(input_file)
        language = self.language_var.get()
        compiler = self.compiler_var.get().lower()
        build_type = self.build_type_var.get()
        
        # Create compiler-specific output directory
        output_dir = input_path.parent / compiler
        output_dir.mkdir(exist_ok=True)
        
        if language == "C++":
            if build_type == "Executable":
                ext = ".exe"
            else:
                ext = ".dll"
            output_filename = f"{input_path.stem}_{compiler}{ext}"
        elif language == "C#":
            output_filename = f"{input_path.stem}_cs.exe"
        elif language == "Java":
            output_filename = f"{input_path.stem}.class"
        else:
            output_filename = f"{input_path.stem}_{compiler}.exe"
        
        output_path = output_dir / output_filename
        self.output_file_var.set(str(output_path))
    
    def browse_config_file(self, key):
        """Browse for configuration file"""
        filename = filedialog.askopenfilename(
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.config_vars[key].set(filename)
    
    def browse_config_directory(self, key):
        """Browse for configuration directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.config_vars[key].set(directory)
    
    def save_configuration(self):
        """Save configuration"""
        for key, var in self.config_vars.items():
            self.config[key] = var.get()
        self.save_config()
        messagebox.showinfo("Success", "Configuration saved successfully!")
    
    def generate_command(self):
        """Generate build command based on current settings"""
        language = self.language_var.get()
        compiler = self.compiler_var.get()
        build_type = self.build_type_var.get()
        library = self.library_var.get()
        input_file = self.input_file_var.get()
        output_file = self.output_file_var.get()
        
        if not input_file or not output_file:
            return "Please select input and output files"
        
        if language == "C++":
            return self.generate_cpp_command(compiler, build_type, library, input_file, output_file)
        elif language == "C#":
            return self.generate_csharp_command(input_file, output_file)
        elif language == "Java":
            return self.generate_java_command(input_file, output_file)
        elif language == "JNI":
            return self.generate_jni_command(compiler, input_file, output_file)
        
        return "Unsupported language"
    
    def generate_cpp_command(self, compiler, build_type, library, input_file, output_file):
        """Generate C++ build command"""
        cmd_parts = []
        
        # Compiler path
        compiler_key = f"{compiler.lower()}_path"
        compiler_path = self.config.get(compiler_key, "")
        if not compiler_path:
            return f"Please configure {compiler} compiler path"
        
        cmd_parts.append(f'"{compiler_path}"')
        
        # Compiler-specific flags
        if compiler in ["GCC", "Clang"]:
            if self.debug_var.get():
                cmd_parts.extend(["-g2"])
            if self.optimize_var.get():
                cmd_parts.extend(["-O3", "-DNDEBUG"])
            else:
                cmd_parts.extend(["-O0", "-DDEBUG"])
            
            cmd_parts.extend([f'"{input_file}"', "-o", f'"{output_file}"'])
            cmd_parts.extend(["-D_WIN32_WINNT=0x0501", "-lpthread", "-Wall", "-std=c++17"])
            
            if build_type == "Shared Library":
                cmd_parts.insert(-4, "-shared")
                
        elif compiler == "MSVC":
            cmd_parts.extend(["/MTd", "/GS", "/W4", "/Zi", "/nologo", "/EHsc"])
            if self.optimize_var.get():
                cmd_parts.append("/O2")
            
            output_dir = Path(output_file).parent
            cmd_parts.extend([f"/Fo{output_dir}\\", f"/Fd{output_dir}\\vc140.pdb"])
            cmd_parts.append(f'"{input_file}"')
            cmd_parts.extend(["/link", f"/OUT:{output_file}"])
            
            if build_type == "Shared Library":
                cmd_parts.append("/DLL")
        
        # Library-specific flags
        if library == "CryptoPP":
            self.add_cryptopp_flags(cmd_parts, compiler)
        elif library == "OpenSSL":
            self.add_openssl_flags(cmd_parts, compiler)
        
        # Add auto-run if enabled
        if self.auto_run_var.get() and build_type == "Executable":
            output_dir = Path(output_file).parent
            output_name = Path(output_file).name
            cmd_parts.extend(["&&", "cd", f'"{output_dir}"', "&&", f'"{output_name}"'])
        
        return " ".join(cmd_parts)
    
    def add_cryptopp_flags(self, cmd_parts, compiler):
        """Add CryptoPP library flags"""
        include_dir = self.config.get("cryptopp_include", "")
        lib_dir = self.config.get(f"cryptopp_lib_{compiler.lower()}", "")
        
        if include_dir:
            if compiler == "MSVC":
                cmd_parts.insert(-2, f"/I{include_dir}")
            else:
                cmd_parts.extend([f"-I{include_dir}"])
        
        if lib_dir:
            if compiler == "MSVC":
                cmd_parts.extend([f"/LIBPATH:{lib_dir}", "cryptlib.lib", "crypt32.lib", "ws2_32.lib", "/MACHINE:X64"])
            else:
                cmd_parts.extend([f"-L{lib_dir}", "-lcryptopp"])
    
    def add_openssl_flags(self, cmd_parts, compiler):
        """Add OpenSSL library flags"""
        include_dir = self.config.get(f"openssl_include_{compiler.lower()}", "")
        lib_dir = self.config.get(f"openssl_lib_{compiler.lower()}", "")
        
        if include_dir:
            if compiler == "MSVC":
                cmd_parts.insert(-2, f"/I{include_dir}")
            else:
                cmd_parts.extend([f"-I{include_dir}"])
        
        if lib_dir:
            if compiler == "MSVC":
                cmd_parts.extend([f"/LIBPATH:{lib_dir}", "libssl.lib", "libcrypto.lib", "crypt32.lib", "ws2_32.lib", "/MACHINE:X64"])
            else:
                cmd_parts.extend([f"-L{lib_dir}", "-lssl", "-lcrypto", "-lcrypt32", "-lws2_32", "-lpthread"])
    
    def generate_csharp_command(self, input_file, output_file):
        """Generate C# build command"""
        csc_path = self.config.get("csc_path", "csc.exe")
        cmd_parts = [f'"{csc_path}"', "/nologo"]
        
        if self.debug_var.get():
            cmd_parts.append("/debug")
        if self.optimize_var.get():
            cmd_parts.append("/optimize+")
        
        cmd_parts.extend(["/warn:4", f'"{input_file}"', f"/out:{output_file}"])
        
        if self.auto_run_var.get():
            cmd_parts.extend(["&&", f'"{output_file}"'])
        
        return " ".join(cmd_parts)
    
    def generate_java_command(self, input_file, output_file):
        """Generate Java build command"""
        javac_path = self.config.get("javac_path", "javac")
        cmd_parts = [f'"{javac_path}"', f'"{input_file}"']
        
        if self.auto_run_var.get():
            java_path = self.config.get("java_path", "java")
            class_name = Path(input_file).stem
            input_dir = Path(input_file).parent
            cmd_parts.extend(["&&", "cd", f'"{input_dir}"', "&&", f'"{java_path}"', class_name])
        
        return " ".join(cmd_parts)
    
    def generate_jni_command(self, compiler, input_file, output_file):
        """Generate JNI build command"""
        # This is simplified - JNI requires multiple steps
        return "JNI build requires multiple steps. Use the full JNI workflow."
    
    def update_command_preview(self):
        """Update command preview"""
        command = self.generate_command()
        self.command_text.delete(1.0, tk.END)
        self.command_text.insert(1.0, command)
    
    def build_project(self):
        """Build the project"""
        command = self.generate_command()
        if "Please" in command or "Unsupported" in command:
            messagebox.showerror("Error", command)
            return
        
        self.output_text.insert(tk.END, f"Executing: {command}\n\n")
        self.output_text.see(tk.END)
        
        # Run in separate thread to avoid freezing UI
        thread = threading.Thread(target=self.execute_build, args=(command,))
        thread.daemon = True
        thread.start()
    
    def execute_build(self, command):
        """Execute build command in separate thread"""
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding="utf-8",
                errors="replace"
            )
            
            # Read output and errors
            stdout, stderr = process.communicate()
            
            # Display output
            if stdout:
                self.root.after(0, self.append_output, stdout)
            if stderr:
                self.root.after(0, self.append_output, f"\n--- STDERR ---\n{stderr}")
                self.root.after(0, self.analyze_errors, stderr)
            
            if process.returncode == 0:
                self.root.after(0, self.append_output, "\n✅ Build completed successfully!\n")
            else:
                self.root.after(0, self.append_output, f"\n❌ Build failed with return code {process.returncode}\n")
                
        except Exception as e:
            self.root.after(0, self.append_output, f"\n❌ Error executing command: {str(e)}\n")
    
    def analyze_errors(self, error_text):
        """Analyze and categorize build errors"""
        if not hasattr(self, 'error_summary'):
            return
            
        error_analysis = []
        lines = error_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Common error patterns
            if 'error:' in line.lower():
                if 'no such file or directory' in line.lower():
                    error_analysis.append("❌ Missing file/header - Check include paths")
                elif 'undefined reference' in line.lower():
                    error_analysis.append("❌ Linking error - Check library paths")
                elif 'permission denied' in line.lower():
                    error_analysis.append("❌ Permission denied - Check file permissions")
                elif 'syntax error' in line.lower():
                    error_analysis.append("❌ Syntax error in source code")
                else:
                    error_analysis.append(f"❌ {line}")
            elif 'warning:' in line.lower():
                error_analysis.append(f"⚠️ {line}")
        
        if error_analysis:
            summary = "\n".join(error_analysis[:10])  # Show first 10 errors
            if len(error_analysis) > 10:
                summary += f"\n... and {len(error_analysis) - 10} more errors"
        else:
            summary = "No specific errors detected in output"
        
        self.error_summary.delete(1.0, tk.END)
        self.error_summary.insert(1.0, summary)
    
    def run_executable(self):
        """Run the compiled executable"""
        output_file = self.output_file_var.get()
        if not output_file:
            messagebox.showerror("Error", "No output file specified")
            return
        
        if not os.path.exists(output_file):
            messagebox.showerror("Error", f"Output file does not exist: {output_file}")
            return
        
        # Check if it's an executable
        if not output_file.endswith(('.exe', '.jar')):
            language = self.language_var.get()
            if language == "Java":
                self.run_java_class()
                return
            else:
                messagebox.showerror("Error", "Not an executable file")
                return
        
        self.runtime_text.insert(tk.END, f"🚀 Running: {output_file}\n")
        self.runtime_text.insert(tk.END, "=" * 50 + "\n")
        self.runtime_text.see(tk.END)
        
        # Run in separate thread
        thread = threading.Thread(target=self.execute_runtime, args=(output_file,))
        thread.daemon = True
        thread.start()
    
    def execute_runtime(self, executable_path):
        """Execute the compiled program"""
        try:
            # Change to executable directory
            exe_dir = os.path.dirname(executable_path)
            exe_name = os.path.basename(executable_path)
            exe_full_path = os.path.abspath(executable_path)
            
            process = subprocess.Popen(
                exe_full_path,
                cwd=exe_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding="utf-8",
                errors="replace",
            )
            
            # Read output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.root.after(0, self.append_runtime_output, output)
            
            # Get any remaining output
            stdout, stderr = process.communicate()
            if stdout:
                self.root.after(0, self.append_runtime_output, stdout)
            if stderr:
                self.root.after(0, self.append_runtime_output, f"\n--- Runtime Errors ---\n{stderr}")
            
            self.root.after(0, self.append_runtime_output, f"\n🏁 Program finished with exit code: {process.returncode}\n")
            
        except Exception as e:
            self.root.after(0, self.append_runtime_output, f"\n❌ Runtime error: {str(e)}\n")
    
    def run_java_class(self):
        """Run Java class file"""
        input_file = self.input_file_var.get()
        if not input_file:
            messagebox.showerror("Error", "No input file specified")
            return
        
        java_path = self.config.get("java_path", "java")
        class_name = Path(input_file).stem
        class_dir = Path(input_file).parent
        
        command = f'cd "{class_dir}" && "{java_path}" {class_name}'
        
        self.runtime_text.insert(tk.END, f"🚀 Running Java: {command}\n")
        self.runtime_text.insert(tk.END, "=" * 50 + "\n")
        self.runtime_text.see(tk.END)
        
        thread = threading.Thread(target=self.execute_java_runtime, args=(command,))
        thread.daemon = True
        thread.start()
    
    def execute_java_runtime(self, command):
        """Execute Java program"""
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding="utf-8",
                errors="replace"
            )
            
            stdout, stderr = process.communicate()
            
            if stdout:
                self.root.after(0, self.append_runtime_output, stdout)
            if stderr:
                self.root.after(0, self.append_runtime_output, f"\n--- Runtime Errors ---\n{stderr}")
            
            self.root.after(0, self.append_runtime_output, f"\n🏁 Java program finished with exit code: {process.returncode}\n")
            
        except Exception as e:
            self.root.after(0, self.append_runtime_output, f"\n❌ Java runtime error: {str(e)}\n")
    
    def debug_executable(self):
        """Debug the executable with GDB"""
        output_file = self.output_file_var.get()
        if not output_file:
            messagebox.showerror("Error", "No output file specified")
            return
        
        if not os.path.exists(output_file):
            messagebox.showerror("Error", f"Output file does not exist: {output_file}")
            return
        
        compiler = self.compiler_var.get()
        
        # Determine debugger based on compiler
        if compiler in ["GCC", "Clang"]:
            debugger = "gdb"
            debug_command = f'gdb "{output_file}"'
        elif compiler == "MSVC":
            # For MSVC, we can't easily launch debugger, but can check if debug info exists
            pdb_file = output_file.replace('.exe', '.pdb')
            if os.path.exists(pdb_file):
                messagebox.showinfo("Debug Info", f"Debug symbols found: {pdb_file}\nUse Visual Studio debugger to debug this executable.")
                return
            else:
                messagebox.showwarning("No Debug Info", "No debug symbols found. Rebuild with debug mode enabled.")
                return
        else:
            messagebox.showerror("Error", "Debug not supported for this compiler")
            return
        
        self.debug_text.insert(tk.END, f"🐛 Starting debugger: {debug_command}\n")
        self.debug_text.insert(tk.END, "💡 Basic GDB commands:\n")
        self.debug_text.insert(tk.END, "  - run: Start the program\n")
        self.debug_text.insert(tk.END, "  - break main: Set breakpoint at main\n")
        self.debug_text.insert(tk.END, "  - step: Step through code\n")
        self.debug_text.insert(tk.END, "  - continue: Continue execution\n")
        self.debug_text.insert(tk.END, "  - backtrace: Show call stack\n")
        self.debug_text.insert(tk.END, "  - quit: Exit debugger\n")
        self.debug_text.insert(tk.END, "=" * 50 + "\n")
        self.debug_text.see(tk.END)
        
        # Try to launch debugger in external terminal
        try:
            if os.name == 'nt':  # Windows
                # Try to launch in new command prompt
                debug_cmd = f'start cmd /k "cd /d {os.path.dirname(output_file)} && {debug_command}"'
                subprocess.Popen(debug_cmd, shell=True)
                self.debug_text.insert(tk.END, "🚀 Debugger launched in new terminal window\n")
            else:  # Linux/Mac
                debug_cmd = f'gnome-terminal -- bash -c "cd {os.path.dirname(output_file)} && {debug_command}; exec bash"'
                subprocess.Popen(debug_cmd, shell=True)
                self.debug_text.insert(tk.END, "🚀 Debugger launched in new terminal window\n")
        except Exception as e:
            self.debug_text.insert(tk.END, f"❌ Failed to launch debugger: {e}\n")
            self.debug_text.insert(tk.END, f"💡 Manual command: {debug_command}\n")
    
    def open_output_folder(self):
        """Open the output folder in file explorer"""
        output_file = self.output_file_var.get()
        if not output_file:
            messagebox.showerror("Error", "No output file specified")
            return
        
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            messagebox.showerror("Error", f"Output directory does not exist: {output_dir}")
            return
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(output_dir)
            elif os.name == 'posix':  # Linux/Mac
                subprocess.Popen(['xdg-open', output_dir])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {e}")
    
    def append_runtime_output(self, text):
        """Append text to runtime output"""
        if hasattr(self, 'runtime_text'):
            self.runtime_text.insert(tk.END, text)
            self.runtime_text.see(tk.END)
    
    def append_output(self, text):
        """Append text to output (called from main thread)"""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
    
    def clear_output(self):
        """Clear all outputs"""
        self.output_text.delete(1.0, tk.END)
        if hasattr(self, 'runtime_text'):
            self.runtime_text.delete(1.0, tk.END)
        if hasattr(self, 'debug_text'):
            self.debug_text.delete(1.0, tk.END)
        if hasattr(self, 'error_summary'):
            self.error_summary.delete(1.0, tk.END)

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = CompilerGUI(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Bind events
    def on_closing():
        """Handle window closing"""
        app.save_config()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Auto-update command preview when settings change
    def update_preview(*args):
        app.update_command_preview()
    
    app.language_var.trace('w', update_preview)
    app.compiler_var.trace('w', update_preview)
    app.build_type_var.trace('w', update_preview)
    app.library_var.trace('w', update_preview)
    app.input_file_var.trace('w', update_preview)
    app.output_file_var.trace('w', update_preview)
    app.debug_var.trace('w', update_preview)
    app.optimize_var.trace('w', update_preview)
    app.auto_run_var.trace('w', update_preview)
    
    root.mainloop()

if __name__ == "__main__":
    main()