using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Text;

namespace CryptoCompilerGUI
{
    // Configuration classes
    public class CompilerConfig
    {
        public string Executable { get; set; } = "";
        public List<string> Flags { get; set; } = new List<string>();
        public List<string> Libs { get; set; } = new List<string>();
    }

    public class LibraryConfig
    {
        public object GccLib { get; set; } = "";
        public object ClangLib { get; set; } = "";
        public object MsvcLib { get; set; } = "";
    }

    public class AppConfig
    {
        public Dictionary<string, string> Paths { get; set; } = new Dictionary<string, string>();
        public Dictionary<string, CompilerConfig> Compilers { get; set; } = new Dictionary<string, CompilerConfig>();
        public Dictionary<string, LibraryConfig> Libraries { get; set; } = new Dictionary<string, LibraryConfig>();
    }

    // Main Form
    public partial class MainForm : Form
    {
        private AppConfig config;
        private readonly string configFile = "compiler_config.json";
        private Process buildProcess;
        private bool isBusy = false;

        // UI Controls
        private TabControl mainTabControl;
        private ComboBox compilerCombo, libraryCombo, buildTypeCombo;
        private TextBox sourceFileTextBox;
        private CheckBox autoRunCheckBox;
        private Button buildButton, stopButton, browseButton;
        private RichTextBox outputTextBox;
        private ProgressBar progressBar;
        private StatusStrip statusStrip;
        private ToolStripStatusLabel statusLabel;

        // Settings controls
        private Dictionary<string, TextBox> pathTextBoxes = new Dictionary<string, TextBox>();

        public MainForm()
        {
            InitializeComponent();
            LoadConfiguration();
            UpdateUI();
        }

        private void InitializeComponent()
        {
            this.Text = "🔐 Crypto++ Compiler Tool";
            this.Size = new Size(900, 650);
            this.MinimumSize = new Size(700, 500);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.Icon = SystemIcons.Application;

            // Main Tab Control
            mainTabControl = new TabControl
            {
                Dock = DockStyle.Fill,
                Font = new Font("Segoe UI", 9F)
            };

            // Build Tab
            var buildTab = new TabPage("Build");
            SetupBuildTab(buildTab);
            mainTabControl.TabPages.Add(buildTab);

            // Settings Tab
            var settingsTab = new TabPage("Settings");
            SetupSettingsTab(settingsTab);
            mainTabControl.TabPages.Add(settingsTab);

            // About Tab
            var aboutTab = new TabPage("About");
            SetupAboutTab(aboutTab);
            mainTabControl.TabPages.Add(aboutTab);

            // Status Strip
            statusStrip = new StatusStrip();
            statusLabel = new ToolStripStatusLabel("Ready");
            statusStrip.Items.Add(statusLabel);

            // Add controls to form
            this.Controls.Add(mainTabControl);
            this.Controls.Add(statusStrip);

            // Event handlers
            this.FormClosing += MainForm_FormClosing;
        }

        private void SetupBuildTab(TabPage tab)
        {
            var mainPanel = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                Padding = new Padding(10),
                RowCount = 4,
                ColumnCount = 1
            };

            // Configuration Panel
            var configGroup = new GroupBox
            {
                Text = "Build Configuration",
                Height = 140,
                Dock = DockStyle.Top,
                Padding = new Padding(10)
            };

            var configPanel = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                RowCount = 3,
                ColumnCount = 4
            };

            // Row 1: Compiler, Library, Build Type
            configPanel.Controls.Add(new Label { Text = "Compiler:", TextAlign = ContentAlignment.MiddleRight }, 0, 0);
            compilerCombo = new ComboBox
            {
                DropDownStyle = ComboBoxStyle.DropDownList,
                Items = { "gcc", "clang", "msvc" },
                SelectedIndex = 0,
                Width = 80
            };
            configPanel.Controls.Add(compilerCombo, 1, 0);

            configPanel.Controls.Add(new Label { Text = "Library:", TextAlign = ContentAlignment.MiddleRight }, 2, 0);
            libraryCombo = new ComboBox
            {
                DropDownStyle = ComboBoxStyle.DropDownList,
                Items = { "cryptopp", "openssl" },
                SelectedIndex = 0,
                Width = 80
            };
            configPanel.Controls.Add(libraryCombo, 3, 0);

            // Row 2: Build Type and Auto-run
            configPanel.Controls.Add(new Label { Text = "Type:", TextAlign = ContentAlignment.MiddleRight }, 0, 1);
            buildTypeCombo = new ComboBox
            {
                DropDownStyle = ComboBoxStyle.DropDownList,
                Items = { "executable", "shared_library" },
                SelectedIndex = 0,
                Width = 120
            };
            configPanel.Controls.Add(buildTypeCombo, 1, 1);

            autoRunCheckBox = new CheckBox
            {
                Text = "Auto-run after build",
                Checked = true,
                AutoSize = true
            };
            configPanel.Controls.Add(autoRunCheckBox, 2, 1);
            configPanel.SetColumnSpan(autoRunCheckBox, 2);

            // Row 3: Source File
            configPanel.Controls.Add(new Label { Text = "Source File:", TextAlign = ContentAlignment.MiddleRight }, 0, 2);
            sourceFileTextBox = new TextBox
            {
                Text = "main.cpp",
                Anchor = AnchorStyles.Left | AnchorStyles.Right
            };
            configPanel.Controls.Add(sourceFileTextBox, 1, 2);
            configPanel.SetColumnSpan(sourceFileTextBox, 2);

            browseButton = new Button
            {
                Text = "📁 Browse",
                Width = 80
            };
            browseButton.Click += BrowseButton_Click;
            configPanel.Controls.Add(browseButton, 3, 2);

            configGroup.Controls.Add(configPanel);

            // Build Controls Panel
            var buildControlsPanel = new Panel
            {
                Height = 60,
                Dock = DockStyle.Top
            };

            buildButton = new Button
            {
                Text = "🔨 Build & Run",
                Size = new Size(120, 35),
                Location = new Point(10, 10),
                Font = new Font("Segoe UI", 10F, FontStyle.Bold),
                BackColor = Color.FromArgb(0, 120, 215),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat
            };
            buildButton.Click += BuildButton_Click;

            stopButton = new Button
            {
                Text = "⏹️ Stop",
                Size = new Size(80, 35),
                Location = new Point(140, 10),
                Enabled = false
            };
            stopButton.Click += StopButton_Click;

            progressBar = new ProgressBar
            {
                Style = ProgressBarStyle.Marquee,
                Location = new Point(230, 20),
                Size = new Size(200, 20),
                Visible = false
            };

            buildControlsPanel.Controls.AddRange(new Control[] { buildButton, stopButton, progressBar });

            // Output Panel
            var outputGroup = new GroupBox
            {
                Text = "Build Output",
                Dock = DockStyle.Fill,
                Padding = new Padding(5)
            };

            var outputPanel = new Panel { Dock = DockStyle.Fill };

            outputTextBox = new RichTextBox
            {
                Dock = DockStyle.Fill,
                Font = new Font("Consolas", 9F),
                ReadOnly = true,
                BackColor = Color.Black,
                ForeColor = Color.White,
                WordWrap = false
            };

            var outputButtonsPanel = new Panel
            {
                Height = 35,
                Dock = DockStyle.Bottom
            };

            var clearButton = new Button
            {
                Text = "Clear",
                Size = new Size(60, 25),
                Location = new Point(5, 5)
            };
            clearButton.Click += (s, e) => outputTextBox.Clear();

            var saveLogButton = new Button
            {
                Text = "Save Log",
                Size = new Size(70, 25),
                Location = new Point(75, 5)
            };
            saveLogButton.Click += SaveLogButton_Click;

            outputButtonsPanel.Controls.AddRange(new Control[] { clearButton, saveLogButton });
            outputPanel.Controls.AddRange(new Control[] { outputTextBox, outputButtonsPanel });
            outputGroup.Controls.Add(outputPanel);

            // Add all panels to main panel
            mainPanel.Controls.AddRange(new Control[] { configGroup, buildControlsPanel, outputGroup });
            mainPanel.RowStyles.Add(new RowStyle(SizeType.Absolute, 150));
            mainPanel.RowStyles.Add(new RowStyle(SizeType.Absolute, 70));
            mainPanel.RowStyles.Add(new RowStyle(SizeType.Percent, 100));

            tab.Controls.Add(mainPanel);
        }

        private void SetupSettingsTab(TabPage tab)
        {
            var scrollPanel = new Panel { Dock = DockStyle.Fill, AutoScroll = true };
            var mainPanel = new TableLayoutPanel
            {
                Dock = DockStyle.Top,
                AutoSize = true,
                ColumnCount = 1,
                Padding = new Padding(10)
            };

            // Paths Group
            var pathsGroup = new GroupBox
            {
                Text = "Library Paths",
                AutoSize = true,
                Dock = DockStyle.Top,
                Padding = new Padding(10)
            };

            var pathsPanel = new TableLayoutPanel
            {
                Dock = DockStyle.Fill,
                AutoSize = true,
                ColumnCount = 3
            };

            int row = 0;
            var defaultPaths = new Dictionary<string, string>
            {
                ["cryptopp_root"] = @"D:\cryptopp-libs",
                ["openssl_root"] = @"D:\openssl350",
                ["msys64_root"] = @"C:\msys64\mingw64",
                ["source_dir"] = "."
            };

            foreach (var kvp in defaultPaths)
            {
                var label = new Label
                {
                    Text = kvp.Key.Replace("_", " ").ToTitleCase() + ":",
                    TextAlign = ContentAlignment.MiddleRight,
                    AutoSize = true
                };
                pathsPanel.Controls.Add(label, 0, row);

                var textBox = new TextBox
                {
                    Text = config?.Paths.ContainsKey(kvp.Key) == true ? config.Paths[kvp.Key] : kvp.Value,
                    Width = 400,
                    Anchor = AnchorStyles.Left | AnchorStyles.Right
                };
                pathTextBoxes[kvp.Key] = textBox;
                pathsPanel.Controls.Add(textBox, 1, row);

                var browseBtn = new Button
                {
                    Text = "📁",
                    Width = 30,
                    Tag = kvp.Key
                };
                browseBtn.Click += PathBrowseButton_Click;
                pathsPanel.Controls.Add(browseBtn, 2, row);

                pathsPanel.RowStyles.Add(new RowStyle(SizeType.AutoSize));
                row++;
            }

            pathsGroup.Controls.Add(pathsPanel);

            // Buttons Panel
            var buttonsPanel = new Panel
            {
                Height = 50,
                Dock = DockStyle.Top
            };

            var saveButton = new Button
            {
                Text = "💾 Save Settings",
                Size = new Size(120, 30),
                Location = new Point(10, 10),
                BackColor = Color.FromArgb(16, 124, 16),
                ForeColor = Color.White,
                FlatStyle = FlatStyle.Flat
            };
            saveButton.Click += SaveSettingsButton_Click;

            var resetButton = new Button
            {
                Text = "🔄 Reset to Defaults",
                Size = new Size(140, 30),
                Location = new Point(140, 10)
            };
            resetButton.Click += ResetSettingsButton_Click;

            var openConfigButton = new Button
            {
                Text = "📂 Open Config File",
                Size = new Size(130, 30),
                Location = new Point(290, 10)
            };
            openConfigButton.Click += OpenConfigButton_Click;

            buttonsPanel.Controls.AddRange(new Control[] { saveButton, resetButton, openConfigButton });

            mainPanel.Controls.AddRange(new Control[] { pathsGroup, buttonsPanel });
            scrollPanel.Controls.Add(mainPanel);
            tab.Controls.Add(scrollPanel);
        }

        private void SetupAboutTab(TabPage tab)
        {
            var panel = new Panel { Dock = DockStyle.Fill, Padding = new Padding(20) };

            var aboutText = new RichTextBox
            {
                Dock = DockStyle.Fill,
                ReadOnly = true,
                BorderStyle = BorderStyle.None,
                BackColor = this.BackColor,
                Font = new Font("Segoe UI", 10F),
                Text = @"🔐 Crypto++ Compiler Tool

A powerful GUI tool for compiling C++ projects with multiple compilers and crypto libraries.

Features:
✅ Multi-compiler support (GCC, Clang, MSVC)
✅ Multi-library support (Crypto++, OpenSSL)
✅ Real-time build output
✅ Configurable paths and settings
✅ Auto-run executables
✅ Build log saving
✅ Professional Windows interface

Supported Compilers:
• GCC (MinGW-w64)
• Clang (LLVM)
• Microsoft Visual C++ (MSVC)

Supported Libraries:
• Crypto++ (Wei Dai's C++ cryptography library)
• OpenSSL (Cryptography and SSL/TLS toolkit)

Version: 1.0
Built with: C# WinForms (.NET Framework)
Author: Crypto Developer

🚀 Happy Coding!"
            };

            panel.Controls.Add(aboutText);
            tab.Controls.Add(panel);
        }

        private void LoadConfiguration()
        {
            try
            {
                if (File.Exists(configFile))
                {
                    var json = File.ReadAllText(configFile);
                    config = JsonSerializer.Deserialize<AppConfig>(json);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error loading configuration: {ex.Message}", "Configuration Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }

            // Set defaults if config is null
            if (config == null)
            {
                config = CreateDefaultConfig();
                SaveConfiguration();
            }
        }

        private AppConfig CreateDefaultConfig()
        {
            return new AppConfig
            {
                Paths = new Dictionary<string, string>
                {
                    ["cryptopp_root"] = @"D:\cryptopp-libs",
                    ["openssl_root"] = @"D:\openssl350",
                    ["msys64_root"] = @"C:\msys64\mingw64",
                    ["source_dir"] = "."
                },
                Compilers = new Dictionary<string, CompilerConfig>
                {
                    ["gcc"] = new CompilerConfig
                    {
                        Executable = @"C:\msys64\mingw64\bin\g++.exe",
                        Flags = new List<string> { "-g2", "-O3", "-DNDEBUG", "-Wall", "-std=c++17" },
                        Libs = new List<string> { "-lpthread" }
                    },
                    ["clang"] = new CompilerConfig
                    {
                        Executable = @"C:\msys64\mingw64\bin\clang++.exe",
                        Flags = new List<string> { "-g2", "-O3", "-DNDEBUG", "-Wall", "-std=c++17" },
                        Libs = new List<string> { "-lpthread" }
                    },
                    ["msvc"] = new CompilerConfig
                    {
                        Executable = "cl.exe",
                        Flags = new List<string> { "/MTd", "/O2", "/W4", "/nologo", "/EHsc" },
                        Libs = new List<string> { "crypt32.lib", "ws2_32.lib" }
                    }
                },
                Libraries = new Dictionary<string, LibraryConfig>
                {
                    ["cryptopp"] = new LibraryConfig
                    {
                        GccLib = "cryptopp",
                        ClangLib = "cryptopp",
                        MsvcLib = "cryptlib.lib"
                    },
                    ["openssl"] = new LibraryConfig
                    {
                        GccLib = new List<string> { "ssl", "crypto" },
                        ClangLib = new List<string> { "ssl", "crypto" },
                        MsvcLib = new List<string> { "libssl.lib", "libcrypto.lib" }
                    }
                }
            };
        }

        private void SaveConfiguration()
        {
            try
            {
                var options = new JsonSerializerOptions { WriteIndented = true };
                var json = JsonSerializer.Serialize(config, options);
                File.WriteAllText(configFile, json);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error saving configuration: {ex.Message}", "Configuration Error",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void UpdateUI()
        {
            if (pathTextBoxes.Count > 0)
            {
                foreach (var kvp in pathTextBoxes)
                {
                    if (config.Paths.ContainsKey(kvp.Key))
                    {
                        kvp.Value.Text = config.Paths[kvp.Key];
                    }
                }
            }
        }

        private async void BuildButton_Click(object sender, EventArgs e)
        {
            if (isBusy) return;

            if (string.IsNullOrWhiteSpace(sourceFileTextBox.Text))
            {
                MessageBox.Show("Please select a source file.", "Missing Source File",
                    MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            if (!File.Exists(sourceFileTextBox.Text))
            {
                MessageBox.Show("Source file does not exist.", "File Not Found",
                    MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            await BuildProject();
        }

        private async Task BuildProject()
        {
            isBusy = true;
            buildButton.Enabled = false;
            stopButton.Enabled = true;
            progressBar.Visible = true;
            outputTextBox.Clear();

            var compiler = compilerCombo.Text;
            var library = libraryCombo.Text;
            var buildType = buildTypeCombo.Text;
            var sourceFile = sourceFileTextBox.Text;

            AppendOutput($"🔨 Building with {compiler.ToUpper()} + {library.ToUpper()}\n", Color.Cyan);

            try
            {
                var cmd = BuildCommand(compiler, library, sourceFile, buildType);
                AppendOutput($"Command: {string.Join(" ", cmd)}\n\n", Color.Yellow);

                var workingDir = Path.GetDirectoryName(sourceFile);
                buildProcess = new Process
                {
                    StartInfo = new ProcessStartInfo
                    {
                        FileName = cmd[0],
                        Arguments = string.Join(" ", cmd.Skip(1).Select(arg => arg.Contains(" ") ? $"\"{arg}\"" : arg)),
                        WorkingDirectory = workingDir,
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    }
                };

                buildProcess.OutputDataReceived += (s, e) =>
                {
                    if (e.Data != null)
                        this.Invoke(new Action(() => AppendOutput(e.Data + "\n", Color.White)));
                };

                buildProcess.ErrorDataReceived += (s, e) =>
                {
                    if (e.Data != null)
                        this.Invoke(new Action(() => AppendOutput(e.Data + "\n", Color.Red)));
                };

                buildProcess.Start();
                buildProcess.BeginOutputReadLine();
                buildProcess.BeginErrorReadLine();

                await Task.Run(() => buildProcess.WaitForExit());

                if (buildProcess.ExitCode == 0)
                {
                    AppendOutput("\n✅ Build successful!\n", Color.LightGreen);
                    statusLabel.Text = "Build successful";

                    if (autoRunCheckBox.Checked && buildType == "executable")
                    {
                        await RunExecutable(compiler, sourceFile);
                    }
                }
                else
                {
                    AppendOutput($"\n❌ Build failed with exit code {buildProcess.ExitCode}\n", Color.Red);
                    statusLabel.Text = "Build failed";
                }
            }
            catch (Exception ex)
            {
                AppendOutput($"\nError: {ex.Message}\n", Color.Red);
                statusLabel.Text = $"Error: {ex.Message}";
            }
            finally
            {
                isBusy = false;
                buildButton.Enabled = true;
                stopButton.Enabled = false;
                progressBar.Visible = false;
                buildProcess = null;
            }
        }

        private List<string> BuildCommand(string compiler, string library, string sourceFile, string buildType)
        {
            var compilerConfig = config.Compilers[compiler];
            var cmd = new List<string> { compilerConfig.Executable };
            cmd.AddRange(compilerConfig.Flags);

            // Include and library directories
            string includeDir, libDir;
            if (library == "cryptopp")
            {
                includeDir = Path.Combine(config.Paths["cryptopp_root"], "include");
                libDir = Path.Combine(config.Paths["cryptopp_root"], "lib", compiler);
            }
            else
            {
                var libSuffix = compiler == "msvc" ? "" : "64";
                includeDir = Path.Combine(config.Paths["openssl_root"], compiler, "include");
                libDir = Path.Combine(config.Paths["openssl_root"], compiler, "lib" + libSuffix);
            }

            cmd.Add(sourceFile);

            // Output
            var baseName = Path.GetFileNameWithoutExtension(sourceFile);
            var outputDir = Path.Combine(Path.GetDirectoryName(sourceFile), compiler);
            Directory.CreateDirectory(outputDir);

            var extension = buildType == "shared_library" ? ".dll" : ".exe";
            var outputFile = Path.Combine(outputDir, $"{baseName}_{compiler}{extension}");

            if (compiler == "msvc")
            {
                cmd.Add($"/I{includeDir}");
                cmd.Add($"/Fo{outputDir}\\");
                cmd.Add("/link");
                if (buildType == "shared_library") cmd.Add("/DLL");
                cmd.Add($"/OUT:{outputFile}");
                cmd.Add($"/LIBPATH:{libDir}");

                // Add libraries
                var libConfig = config.Libraries[library];
                if (library == "cryptopp")
                {
                    cmd.Add(libConfig.MsvcLib.ToString());
                }
                else
                {
                    var libs = JsonSerializer.Deserialize<List<string>>(libConfig.MsvcLib.ToString());
                    cmd.AddRange(libs);
                }
                cmd.AddRange(compilerConfig.Libs);
                cmd.Add("/MACHINE:X64");
            }
            else
            {
                if (buildType == "shared_library") cmd.Add("-shared");
                cmd.Add($"-I{includeDir}");
                cmd.Add("-o");
                cmd.Add(outputFile);
                cmd.Add($"-L{libDir}");

                // Add libraries
                var libConfig = config.Libraries[library];
                if (library == "cryptopp")
                {
                    cmd.Add($"-l{libConfig.GccLib}");
                }
                else
                {
                    var libs = JsonSerializer.Deserialize<List<string>>(
                        compiler == "gcc" ? libConfig.GccLib.ToString() : libConfig.ClangLib.ToString());
                    foreach (var lib in libs)
                        cmd.Add($"-l{lib}");
                }
                cmd.AddRange(compilerConfig.Libs);
            }

            return cmd;
        }

        private async Task RunExecutable(string compiler, string sourceFile)
        {
            var baseName = Path.GetFileNameWithoutExtension(sourceFile);
            var outputDir = Path.Combine(Path.GetDirectoryName(sourceFile), compiler);
            var exeFile = Path.Combine(outputDir, $"{baseName}_{compiler}.exe");

            if (File.Exists(exeFile))
            {
                AppendOutput($"\n🚀 Running {Path.GetFileName(exeFile)}...\n", Color.Cyan);
                AppendOutput(new string('=', 50) + "\n", Color.Gray);

                try
                {
                    var runProcess = new Process
                    {
                        StartInfo = new ProcessStartInfo
                        {
                            FileName = exeFile,
                            WorkingDirectory = outputDir,
                            UseShellExecute = false,
                            RedirectStandardOutput = true,
                            RedirectStandardError = true,
                            CreateNoWindow = true,
                            StandardOutputEncoding = Encoding.UTF8,
                            StandardErrorEncoding = Encoding.UTF8
                        }
                    };

                    runProcess.OutputDataReceived += (s, e) =>
                    {
                        if (e.Data != null)
                            this.Invoke(new Action(() => AppendOutput(e.Data + "\n", Color.White)));
                    };

                    runProcess.Start();
                    // runProcess.StartInfo.StandardOutputEncoding = System.Text.Encoding.UTF8;
                    // runProcess.StartInfo.StandardErrorEncoding = System.Text.Encoding.UTF8;
                    // runProcess.BeginErrorReadLine();
                    runProcess.BeginOutputReadLine();
                    await Task.Run(() => runProcess.WaitForExit());

                    AppendOutput(new string('=', 50) + "\n", Color.Gray);
                    AppendOutput($"Program finished with exit code {runProcess.ExitCode}\n", Color.LightGreen);
                }
                catch (Exception ex)
                {
                    AppendOutput($"Error running executable: {ex.Message}\n", Color.Red);
                }
            }
        }

        private void AppendOutput(string text, Color color)
        {
            outputTextBox.SelectionStart = outputTextBox.TextLength;
            outputTextBox.SelectionLength = 0;
            outputTextBox.SelectionColor = color;
            outputTextBox.AppendText(text);
            outputTextBox.ScrollToCaret();
        }

        private void StopButton_Click(object sender, EventArgs e)
        {
            if (buildProcess != null && !buildProcess.HasExited)
            {
                buildProcess.Kill();
                AppendOutput("\n⏹️ Build stopped by user\n", Color.Yellow);
                statusLabel.Text = "Build stopped";
            }
        }

        private void BrowseButton_Click(object sender, EventArgs e)
        {
            using (var dialog = new OpenFileDialog())
            {
                dialog.Filter = "C++ Files|*.cpp;*.cxx;*.cc;*.c++|C Files|*.c|All Files|*.*";
                dialog.Title = "Select C++ Source File";

                if (config.Paths.ContainsKey("source_dir"))
                    dialog.InitialDirectory = config.Paths["source_dir"];

                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    sourceFileTextBox.Text = dialog.FileName;
                    config.Paths["source_dir"] = Path.GetDirectoryName(dialog.FileName);
                }
            }
        }

        private void PathBrowseButton_Click(object sender, EventArgs e)
        {
            var button = sender as Button;
            var pathKey = button.Tag.ToString();

            using (var dialog = new FolderBrowserDialog())
            {
                dialog.Description = $"Select {pathKey.Replace("_", " ").ToTitleCase()} Directory";
                dialog.SelectedPath = pathTextBoxes[pathKey].Text;

                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    pathTextBoxes[pathKey].Text = dialog.SelectedPath;
                }
            }
        }

        private void SaveSettingsButton_Click(object sender, EventArgs e)
        {
            foreach (var kvp in pathTextBoxes)
            {
                config.Paths[kvp.Key] = kvp.Value.Text;
            }

            SaveConfiguration();
            MessageBox.Show("Settings saved successfully!", "Settings Saved",
                MessageBoxButtons.OK, MessageBoxIcon.Information);
            statusLabel.Text = "Settings saved";
        }

        private void ResetSettingsButton_Click(object sender, EventArgs e)
        {
            if (MessageBox.Show("Reset all settings to defaults?", "Confirm Reset",
                MessageBoxButtons.YesNo, MessageBoxIcon.Question) == DialogResult.Yes)
            {
                config = CreateDefaultConfig();
                UpdateUI();
                statusLabel.Text = "Settings reset to defaults";
            }
        }

        private void OpenConfigButton_Click(object sender, EventArgs e)
        {
            try
            {
                Process.Start("notepad.exe", Path.GetFullPath(configFile));
            }
            catch
            {
                MessageBox.Show($"Config file location:\n{Path.GetFullPath(configFile)}",
                    "Config File Location", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        private void SaveLogButton_Click(object sender, EventArgs e)
        {
            using (var dialog = new SaveFileDialog())
            {
                dialog.Filter = "Text Files|*.txt|All Files|*.*";
                dialog.Title = "Save Build Log";
                dialog.DefaultExt = "txt";

                if (dialog.ShowDialog() == DialogResult.OK)
                {
                    try
                    {
                        File.WriteAllText(dialog.FileName, outputTextBox.Text);
                        MessageBox.Show($"Log saved to {dialog.FileName}", "Log Saved",
                            MessageBoxButtons.OK, MessageBoxIcon.Information);
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show($"Failed to save log: {ex.Message}", "Save Error",
                            MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }
                }
            }
        }

        private void MainForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (buildProcess != null && !buildProcess.HasExited)
            {
                var result = MessageBox.Show("A build is in progress. Do you want to stop it and exit?",
                    "Build in Progress", MessageBoxButtons.YesNo, MessageBoxIcon.Question);

                if (result == DialogResult.Yes)
                {
                    buildProcess.Kill();
                }
                else
                {
                    e.Cancel = true;
                }
            }
        }
    }

    // Extension methods
    public static class StringExtensions
    {
        public static string ToTitleCase(this string input)
        {
            if (string.IsNullOrEmpty(input))
                return input;

            var words = input.Split(' ', '_', '-');
            for (int i = 0; i < words.Length; i++)
            {
                if (words[i].Length > 0)
                {
                    words[i] = char.ToUpper(words[i][0]) + words[i].Substring(1).ToLower();
                }
            }
            return string.Join(" ", words);
        }
    }

    // Program entry point
    public class Program
    {
        [STAThread]
        public static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            try
            {
                Application.Run(new MainForm());
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Fatal error: {ex.Message}\n\nStack trace:\n{ex.StackTrace}",
                    "Application Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}