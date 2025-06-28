using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Text.Json;
using System.Collections.Generic;

namespace MultiCompiler
{
    public partial class MainForm : Form
    {
        private Dictionary<string, string> config;
        private string configFile = "compiler_config.json";
        private TabControl tabControl;
        private TabPage buildTab;
        private TabPage configTab;
        private ComboBox languageCombo, compilerCombo, buildTypeCombo, libraryCombo;
        private TextBox inputFileText, outputFileText, commandText, outputText, runtimeText, debugText, errorSummary;
        private CheckBox debugCheck, optimizeCheck, autoRunCheck;
        private Dictionary<string, TextBox> configTextBoxes;

        public MainForm()
        {
            InitializeComponent();
            LoadConfig();
            SetupUI();
            LoadSavedConfig();
        }

        private void InitializeComponent()
        {
            this.Size = new Size(800, 700);
            this.Text = "Multi-Compiler Build Tool";
            this.FormClosing += MainForm_FormClosing;
        }

        private void LoadConfig()
        {
            config = new Dictionary<string, string>
            {
                {"gcc_path", "C:\\msys64\\mingw64\\bin\\g++.exe"},
                {"clang_path", "C:\\msys64\\mingw64\\bin\\clang++.exe"},
                {"msvc_path", "cl.exe"},
                {"csc_path", "csc.exe"},
                {"javac_path", "javac"},
                {"java_path", "java"},
                {"cryptopp_include", ""},
                {"cryptopp_lib_gcc", ""},
                {"cryptopp_lib_clang", ""},
                {"cryptopp_lib_msvc", ""},
                {"openssl_include_gcc", ""},
                {"openssl_lib_gcc", ""},
                {"openssl_include_clang", ""},
                {"openssl_lib_clang", ""},
                {"openssl_include_msvc", ""},
                {"openssl_lib_msvc", ""},
                {"jdk_include", ""},
                {"jdk_include_win32", ""}
            };

            try
            {
                if (File.Exists(configFile))
                {
                    string json = File.ReadAllText(configFile);
                    var loadedConfig = JsonSerializer.Deserialize<Dictionary<string, string>>(json);
                    foreach (var kvp in loadedConfig)
                        config[kvp.Key] = kvp.Value;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error loading config: {ex.Message}");
            }
        }

        private void SaveConfig()
        {
            try
            {
                string json = JsonSerializer.Serialize(config, new JsonSerializerOptions { WriteIndented = true });
                File.WriteAllText(configFile, json);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to save config: {ex.Message}", "Error");
            }
        }

        private void SetupUI()
        {
            tabControl = new TabControl
            {
                Dock = DockStyle.Fill
            };
            Controls.Add(tabControl);

            SetupBuildTab();
            SetupConfigTab();
        }

        private void SetupBuildTab()
        {
            buildTab = new TabPage("Build");
            tabControl.Controls.Add(buildTab);

            // Language selection
            var langGroup = new GroupBox
            {
                Text = "Language & Build Type",
                Location = new Point(10, 10),
                Size = new Size(760, 100)
            };
            buildTab.Controls.Add(langGroup);

            var langLabel = new Label { Text = "Language:", Location = new Point(10, 20), AutoSize = true };
            languageCombo = new ComboBox
            {
                Location = new Point(80, 20),
                Width = 150,
                DropDownStyle = ComboBoxStyle.DropDownList
            };
            languageCombo.Items.AddRange(new[] { "C++", "C#", "Java", "JNI" });
            languageCombo.SelectedIndex = 0;
            languageCombo.SelectedIndexChanged += LanguageCombo_SelectedIndexChanged;

            var compilerLabel = new Label { Text = "Compiler:", Location = new Point(240, 20), AutoSize = true };
            compilerCombo = new ComboBox
            {
                Location = new Point(310, 20),
                Width = 150,
                DropDownStyle = ComboBoxStyle.DropDownList
            };
            compilerCombo.Items.AddRange(new[] { "GCC", "Clang", "MSVC" });
            compilerCombo.SelectedIndex = 0;

            var buildTypeLabel = new Label { Text = "Build Type:", Location = new Point(10, 50), AutoSize = true };
            buildTypeCombo = new ComboBox
            {
                Location = new Point(80, 50),
                Width = 150,
                DropDownStyle = ComboBoxStyle.DropDownList
            };
            buildTypeCombo.Items.AddRange(new[] { "Executable", "Shared Library" });
            buildTypeCombo.SelectedIndex = 0;

            var libraryLabel = new Label { Text = "Library:", Location = new Point(240, 50), AutoSize = true };
            libraryCombo = new ComboBox
            {
                Location = new Point(310, 50),
                Width = 150,
                DropDownStyle = ComboBoxStyle.DropDownList
            };
            libraryCombo.Items.AddRange(new[] { "None", "CryptoPP", "OpenSSL" });
            libraryCombo.SelectedIndex = 0;

            langGroup.Controls.AddRange(new Control[] { langLabel, languageCombo, compilerLabel, compilerCombo,
                buildTypeLabel, buildTypeCombo, libraryLabel, libraryCombo });

            // File selection
            var fileGroup = new GroupBox
            {
                Text = "File Selection",
                Location = new Point(10, 120),
                Size = new Size(760, 100)
            };
            buildTab.Controls.Add(fileGroup);

            var inputLabel = new Label { Text = "Input File:", Location = new Point(10, 30), AutoSize = true };
            inputFileText = new TextBox { Location = new Point(80, 30), Width = 600 };
            var inputBrowse = new Button
            {
                Text = "Browse",
                Location = new Point(690, 30),
                Width = 60
            };
            inputBrowse.Click += BrowseInputFile;

            var outputLabel = new Label { Text = "Output File:", Location = new Point(10, 60), AutoSize = true };
            outputFileText = new TextBox { Location = new Point(80, 60), Width = 600 };
            var outputBrowse = new Button
            {
                Text = "Browse",
                Location = new Point(690, 60),
                Width = 60
            };
            outputBrowse.Click += BrowseOutputFile;

            fileGroup.Controls.AddRange(new Control[] { inputLabel, inputFileText, inputBrowse,
                outputLabel, outputFileText, outputBrowse });

            // Build options
            var optionsGroup = new GroupBox
            {
                Text = "Build Options",
                Location = new Point(10, 230),
                Size = new Size(760, 50)
            };
            buildTab.Controls.Add(optionsGroup);

            debugCheck = new CheckBox { Text = "Debug Mode", Location = new Point(10, 20), Checked = true };
            optimizeCheck = new CheckBox { Text = "Optimization", Location = new Point(150, 20), Checked = true };
            autoRunCheck = new CheckBox { Text = "Auto Run", Location = new Point(300, 20) };
            optionsGroup.Controls.AddRange(new Control[] { debugCheck, optimizeCheck, autoRunCheck });

            // Command preview
            var cmdGroup = new GroupBox
            {
                Text = "Command Preview",
                Location = new Point(10, 290),
                Size = new Size(760, 100)
            };
            buildTab.Controls.Add(cmdGroup);

            commandText = new TextBox
            {
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                Location = new Point(10, 20),
                Size = new Size(740, 70)
            };
            cmdGroup.Controls.Add(commandText);

            // Action buttons
            var actionPanel = new FlowLayoutPanel
            {
                Location = new Point(10, 400),
                Size = new Size(760, 40),
                FlowDirection = FlowDirection.LeftToRight
            };
            buildTab.Controls.Add(actionPanel);

            var buttons = new[]
            {
                new Button { Text = "Update Command", Width = 120 },
                new Button { Text = "Build", Width = 120 },
                new Button { Text = "Run Executable", Width = 120 },
                new Button { Text = "Debug", Width = 120 },
                new Button { Text = "Open Output Folder", Width = 120 },
                new Button { Text = "Clear Output", Width = 120 }
            };
            buttons[0].Click += (s, e) => UpdateCommandPreview();
            buttons[1].Click += (s, e) => BuildProject();
            buttons[2].Click += (s, e) => RunExecutable();
            buttons[3].Click += (s, e) => DebugExecutable();
            buttons[4].Click += (s, e) => OpenOutputFolder();
            buttons[5].Click += (s, e) => ClearOutput();
            actionPanel.Controls.AddRange(buttons);

            // Output tabs
            var outputTabs = new TabControl
            {
                Location = new Point(10, 450),
                Size = new Size(760, 200)
            };
            buildTab.Controls.Add(outputTabs);

            var buildOutputTab = new TabPage("Build Output");
            outputText = new TextBox
            {
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                Dock = DockStyle.Fill
            };
            buildOutputTab.Controls.Add(outputText);
            outputTabs.TabPages.Add(buildOutputTab);

            var runtimeOutputTab = new TabPage("Runtime Output");
            runtimeText = new TextBox
            {
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                Dock = DockStyle.Fill
            };
            runtimeOutputTab.Controls.Add(runtimeText);
            outputTabs.TabPages.Add(runtimeOutputTab);

            var debugOutputTab = new TabPage("Debug Output");
            debugText = new TextBox
            {
                Multiline = true,
                ScrollBars = ScrollBars.Vertical,
                Location = new Point(0, 0),
                Size = new Size(740, 140)
            };
            var errorGroup = new GroupBox
            {
                Text = "Error Analysis",
                Location = new Point(0, 140),
                Size = new Size(740, 60)
            };
            errorSummary = new TextBox
            {
                Multiline = true,
                BackColor = Color.FromArgb(255, 242, 242),
                Location = new Point(10, 20),
                Size = new Size(720, 30)
            };
            errorGroup.Controls.Add(errorSummary);
            debugOutputTab.Controls.AddRange(new Control[] { debugText, errorGroup });
            outputTabs.TabPages.Add(debugOutputTab);

            // Auto-update command preview
            languageCombo.SelectedIndexChanged += (s, e) => UpdateCommandPreview();
            compilerCombo.SelectedIndexChanged += (s, e) => UpdateCommandPreview();
            buildTypeCombo.SelectedIndexChanged += (s, e) => UpdateCommandPreview();
            libraryCombo.SelectedIndexChanged += (s, e) => UpdateCommandPreview();
            inputFileText.TextChanged += (s, e) => UpdateCommandPreview();
            outputFileText.TextChanged += (s, e) => UpdateCommandPreview();
            debugCheck.CheckedChanged += (s, e) => UpdateCommandPreview();
            optimizeCheck.CheckedChanged += (s, e) => UpdateCommandPreview();
            autoRunCheck.CheckedChanged += (s, e) => UpdateCommandPreview();
        }

        private void SetupConfigTab()
        {
            configTab = new TabPage("Configuration");
            tabControl.Controls.Add(configTab);

            var panel = new Panel
            {
                AutoScroll = true,
                Dock = DockStyle.Fill
            };
            configTab.Controls.Add(panel);

            configTextBoxes = new Dictionary<string, TextBox>();
            int yPos = 10;

            // Compiler paths
            var compilerGroup = new GroupBox
            {
                Text = "Compiler Paths",
                Location = new Point(10, yPos),
                Size = new Size(740, 180)
            };
            panel.Controls.Add(compilerGroup);
            yPos += 190;

            string[] compilerConfigs = {
                "GCC Path|gcc_path",
                "Clang Path|clang_path",
                "MSVC Path|msvc_path",
                "C# Compiler Path|csc_path",
                "Java Compiler Path|javac_path",
                "Java Runtime Path|java_path"
            };

            for (int i = 0; i < compilerConfigs.Length; i++)
            {
                var parts = compilerConfigs[i].Split('|');
                var label = new Label { Text = parts[0] + ":", Location = new Point(10, 30 + i * 30), AutoSize = true };
                var textBox = new TextBox { Location = new Point(150, 30 + i * 30), Width = 500 };
                var button = new Button
                {
                    Text = "Browse",
                    Location = new Point(660, 30 + i * 30),
                    Width = 60
                };
                button.Tag = parts[1];
                button.Click += BrowseConfigFile;
                compilerGroup.Controls.AddRange(new Control[] { label, textBox, button });
                configTextBoxes[parts[1]] = textBox;
            }

            // CryptoPP paths
            var cryptoppGroup = new GroupBox
            {
                Text = "CryptoPP Library Paths",
                Location = new Point(10, yPos),
                Size = new Size(740, 120)
            };
            panel.Controls.Add(cryptoppGroup);
            yPos += 130;

            string[] cryptoppConfigs = {
                "Include Directory|cryptopp_include",
                "GCC Library Directory|cryptopp_lib_gcc",
                "Clang Library Directory|cryptopp_lib_clang",
                "MSVC Library Directory|cryptopp_lib_msvc"
            };

            for (int i = 0; i < cryptoppConfigs.Length; i++)
            {
                var parts = cryptoppConfigs[i].Split('|');
                var label = new Label { Text = parts[0] + ":", Location = new Point(10, 30 + i * 30), AutoSize = true };
                var textBox = new TextBox { Location = new Point(150, 30 + i * 30), Width = 500 };
                var button = new Button
                {
                    Text = "Browse",
                    Location = new Point(660, 30 + i * 30),
                    Width = 60
                };
                button.Tag = parts[1];
                button.Click += BrowseConfigDirectory;
                cryptoppGroup.Controls.AddRange(new Control[] { label, textBox, button });
                configTextBoxes[parts[1]] = textBox;
            }

            // OpenSSL paths
            var opensslGroup = new GroupBox
            {
                Text = "OpenSSL Library Paths",
                Location = new Point(10, yPos),
                Size = new Size(740, 180)
            };
            panel.Controls.Add(opensslGroup);
            yPos += 190;

            string[] opensslConfigs = {
                "GCC Include Directory|openssl_include_gcc",
                "GCC Library Directory|openssl_lib_gcc",
                "Clang Include Directory|openssl_include_clang",
                "Clang Library Directory|openssl_lib_clang",
                "MSVC Include Directory|openssl_include_msvc",
                "MSVC Library Directory|openssl_lib_msvc"
            };

            for (int i = 0; i < opensslConfigs.Length; i++)
            {
                var parts = opensslConfigs[i].Split('|');
                var label = new Label { Text = parts[0] + ":", Location = new Point(10, 30 + i * 30), AutoSize = true };
                var textBox = new TextBox { Location = new Point(150, 30 + i * 30), Width = 500 };
                var button = new Button
                {
                    Text = "Browse",
                    Location = new Point(660, 30 + i * 30),
                    Width = 60
                };
                button.Tag = parts[1];
                button.Click += BrowseConfigDirectory;
                opensslGroup.Controls.AddRange(new Control[] { label, textBox, button });
                configTextBoxes[parts[1]] = textBox;
            }

            // JDK paths
            var jdkGroup = new GroupBox
            {
                Text = "JDK Paths (for JNI)",
                Location = new Point(10, yPos),
                Size = new Size(740, 90)
            };
            panel.Controls.Add(jdkGroup);

            string[] jdkConfigs = {
                "JDK Include Directory|jdk_include",
                "JDK Win32 Include Directory|jdk_include_win32"
            };

            for (int i = 0; i < jdkConfigs.Length; i++)
            {
                var parts = jdkConfigs[i].Split('|');
                var label = new Label { Text = parts[0] + ":", Location = new Point(10, 30 + i * 30), AutoSize = true };
                var textBox = new TextBox { Location = new Point(150, 30 + i * 30), Width = 500 };
                var button = new Button
                {
                    Text = "Browse",
                    Location = new Point(660, 30 + i * 30),
                    Width = 60
                };
                button.Tag = parts[1];
                button.Click += BrowseConfigDirectory;
                jdkGroup.Controls.AddRange(new Control[] { label, textBox, button });
                configTextBoxes[parts[1]] = textBox;
            }

            var saveButton = new Button
            {
                Text = "Save Configuration",
                Location = new Point(10, yPos + 100),
                Width = 150
            };
            saveButton.Click += (s, e) => SaveConfiguration();
            panel.Controls.Add(saveButton);
        }

        private void LoadSavedConfig()
        {
            foreach (var kvp in configTextBoxes)
            {
                if (config.ContainsKey(kvp.Key))
                    kvp.Value.Text = config[kvp.Key];
            }
        }

        private void LanguageCombo_SelectedIndexChanged(object sender, EventArgs e)
        {
            string language = languageCombo.SelectedItem.ToString();
            if (language == "C++")
                compilerCombo.Items.AddRange(new[] { "GCC", "Clang", "MSVC" });
            else if (language == "C#")
            {
                compilerCombo.Items.Clear();
                compilerCombo.Items.Add("CSC");
                compilerCombo.SelectedIndex = 0;
            }
            else if (language == "Java")
            {
                compilerCombo.Items.Clear();
                compilerCombo.Items.Add("JAVAC");
                compilerCombo.SelectedIndex = 0;
            }
            else if (language == "JNI")
                compilerCombo.Items.AddRange(new[] { "GCC", "Clang", "MSVC" });
        }

        private void BrowseInputFile(object sender, EventArgs e)
        {
            var dialog = new OpenFileDialog();
            string language = languageCombo.SelectedItem.ToString();
            if (language == "C++")
                dialog.Filter = "C++ files (*.cpp;*.cxx;*.cc)|*.cpp;*.cxx;*.cc|C files (*.c)|*.c|All files (*.*)|*.*";
            else if (language == "C#")
                dialog.Filter = "C# files (*.cs)|*.cs|All files (*.*)|*.*";
            else if (language == "Java" || language == "JNI")
                dialog.Filter = "Java files (*.java)|*.java|All files (*.*)|*.*";
            else
                dialog.Filter = "All files (*.*)|*.*";

            if (dialog.ShowDialog() == DialogResult.OK)
            {
                inputFileText.Text = dialog.FileName;
                AutoGenerateOutputFilename();
            }
        }

        private void BrowseOutputFile(object sender, EventArgs e)
        {
            var dialog = new SaveFileDialog();
            string language = languageCombo.SelectedItem.ToString();
            string buildType = buildTypeCombo.SelectedItem.ToString();

            if (language == "C++")
                dialog.Filter = buildType == "Executable" ? "Executable files (*.exe)|*.exe|All files (*.*)|*.*" :
                    "DLL files (*.dll)|*.dll|All files (*.*)|*.*";
            else if (language == "C#")
                dialog.Filter = "Executable files (*.exe)|*.exe|All files (*.*)|*.*";
            else if (language == "Java")
                dialog.Filter = "Class files (*.class)|*.class|All files (*.*)|*.*";
            else
                dialog.Filter = "All files (*.*)|*.*";

            if (dialog.ShowDialog() == DialogResult.OK)
                outputFileText.Text = dialog.FileName;
        }

        private void AutoGenerateOutputFilename()
        {
            if (string.IsNullOrEmpty(inputFileText.Text))
                return;

            string language = languageCombo.SelectedItem.ToString();
            string compiler = compilerCombo.SelectedItem.ToString().ToLower();
            string buildType = buildTypeCombo.SelectedItem.ToString();
            string inputFile = inputFileText.Text;
            string outputDir = Path.Combine(Path.GetDirectoryName(inputFile), compiler);
            Directory.CreateDirectory(outputDir);

            string outputFilename;
            if (language == "C++")
                outputFilename = buildType == "Executable" ? $"{Path.GetFileNameWithoutExtension(inputFile)}_{compiler}.exe" :
                    $"{Path.GetFileNameWithoutExtension(inputFile)}_{compiler}.dll";
            else if (language == "C#")
                outputFilename = $"{Path.GetFileNameWithoutExtension(inputFile)}_cs.exe";
            else if (language == "Java")
                outputFilename = $"{Path.GetFileNameWithoutExtension(inputFile)}.class";
            else
                outputFilename = $"{Path.GetFileNameWithoutExtension(inputFile)}_{compiler}.exe";

            outputFileText.Text = Path.Combine(outputDir, outputFilename);
        }

        private void BrowseConfigFile(object sender, EventArgs e)
        {
            var dialog = new OpenFileDialog
            {
                Filter = "Executable files (*.exe)|*.exe|All files (*.*)|*.*"
            };
            if (dialog.ShowDialog() == DialogResult.OK)
                configTextBoxes[(string)((Button)sender).Tag].Text = dialog.FileName;
        }

        private void BrowseConfigDirectory(object sender, EventArgs e)
        {
            using (var dialog = new FolderBrowserDialog())
            {
                if (dialog.ShowDialog() == DialogResult.OK)
                    configTextBoxes[(string)((Button)sender).Tag].Text = dialog.SelectedPath;
            }
        }

        private void SaveConfiguration()
        {
            foreach (var kvp in configTextBoxes)
                config[kvp.Key] = kvp.Value.Text;
            SaveConfig();
            MessageBox.Show("Configuration saved successfully!", "Success");
        }

        private string GenerateCommand()
        {
            string language = languageCombo.SelectedItem.ToString();
            string compiler = compilerCombo.SelectedItem.ToString();
            string buildType = buildTypeCombo.SelectedItem.ToString();
            string library = libraryCombo.SelectedItem.ToString();
            string inputFile = inputFileText.Text;
            string outputFile = outputFileText.Text;

            if (string.IsNullOrEmpty(inputFile) || string.IsNullOrEmpty(outputFile))
                return "Please select input and output files";

            if (language == "C++")
                return GenerateCppCommand(compiler, buildType, library, inputFile, outputFile);
            else if (language == "C#")
                return GenerateCSharpCommand(inputFile, outputFile);
            else if (language == "Java")
                return GenerateJavaCommand(inputFile, outputFile);
            else if (language == "JNI")
                return GenerateJniCommand(compiler, inputFile, outputFile);

            return "Unsupported language";
        }

        private string GenerateCppCommand(string compiler, string buildType, string library, string inputFile, string outputFile)
        {
            var cmdParts = new List<string>();
            string compilerKey = $"{compiler.ToLower()}_path";
            string compilerPath = config.ContainsKey(compilerKey) ? config[compilerKey] : "";
            if (string.IsNullOrEmpty(compilerPath))
                return $"Please configure {compiler} compiler path";

            cmdParts.Add($"\"{compilerPath}\"");
            if (compiler == "GCC" || compiler == "Clang")
            {
                if (debugCheck.Checked)
                    cmdParts.Add("-g2");
                if (optimizeCheck.Checked)
                    cmdParts.AddRange(new[] { "-O3", "-DNDEBUG" });
                else
                    cmdParts.AddRange(new[] { "-O0", "-DDEBUG" });

                cmdParts.AddRange(new[] { $"\"{inputFile}\"", "-o", $"\"{outputFile}\"" });
                cmdParts.AddRange(new[] { "-D_WIN32_WINNT=0x0501", "-lpthread", "-Wall", "-std=c++17" });
                if (buildType == "Shared Library")
                    cmdParts.Insert(cmdParts.Count - 4, "-shared");
            }
            else if (compiler == "MSVC")
            {
                cmdParts.AddRange(new[] { "/MTd", "/GS", "/W4", "/Zi", "/nologo", "/EHsc" });
                if (optimizeCheck.Checked)
                    cmdParts.Add("/O2");

                string outputDir = Path.GetDirectoryName(outputFile);
                cmdParts.AddRange(new[] { $"/Fo{outputDir}\\", $"/Fd{outputDir}\\vc140.pdb" });
                cmdParts.Add($"\"{inputFile}\"");
                cmdParts.AddRange(new[] { "/link", $"/OUT:{outputFile}" });
                if (buildType == "Shared Library")
                    cmdParts.Add("/DLL");
            }

            if (library == "CryptoPP")
                AddCryptoPPFlags(cmdParts, compiler);
            else if (library == "OpenSSL")
                AddOpenSSLFlags(cmdParts, compiler);

            // if (autoRunCheck.Checked && buildType == "Executable")
            // {
            //     string outputDir = Path.GetDirectoryName(outputFile);
            //     string outputName = Path.GetFileName(outputFile);
            //     cmdParts.AddRange(new[] { "&&", "cd", $"\"{outputDir}\"", "&&", $"\"{outputName}\"" });
            // }

            return string.Join(" ", cmdParts);
        }

        private void AddCryptoPPFlags(List<string> cmdParts, string compiler)
        {
            string includeDir = config.ContainsKey("cryptopp_include") ? config["cryptopp_include"] : "";
            string libDir = config.ContainsKey($"cryptopp_lib_{compiler.ToLower()}") ? config[$"cryptopp_lib_{compiler.ToLower()}"] : "";

            if (!string.IsNullOrEmpty(includeDir))
                cmdParts.Add(compiler == "MSVC" ? $"/I{includeDir}" : $"-I{includeDir}");

            if (!string.IsNullOrEmpty(libDir))
            {
                if (compiler == "MSVC")
                    cmdParts.AddRange(new[] { $"/LIBPATH:{libDir}", "cryptlib.lib", "crypt32.lib", "ws2_32.lib", "/MACHINE:X64" });
                else
                    cmdParts.AddRange(new[] { $"-L{libDir}", "-lcryptopp" });
            }
        }

        private void AddOpenSSLFlags(List<string> cmdParts, string compiler)
        {
            string includeDir = config.ContainsKey($"openssl_include_{compiler.ToLower()}") ? config[$"openssl_include_{compiler.ToLower()}"] : "";
            string libDir = config.ContainsKey($"openssl_lib_{compiler.ToLower()}") ? config[$"openssl_lib_{compiler.ToLower()}"] : "";

            if (!string.IsNullOrEmpty(includeDir))
                cmdParts.Add(compiler == "MSVC" ? $"/I{includeDir}" : $"-I{includeDir}");

            if (!string.IsNullOrEmpty(libDir))
            {
                if (compiler == "MSVC")
                    cmdParts.AddRange(new[] { $"/LIBPATH:{libDir}", "libssl.lib", "libcrypto.lib", "crypt32.lib", "ws2_32.lib", "/MACHINE:X64" });
                else
                    cmdParts.AddRange(new[] { $"-L{libDir}", "-lssl", "-lcrypto", "-lcrypt32", "-lws2_32", "-lpthread" });
            }
        }

        private string GenerateCSharpCommand(string inputFile, string outputFile)
        {
            var cmdParts = new List<string> { $"\"{config["csc_path"]}\"", "/nologo" };
            if (debugCheck.Checked)
                cmdParts.Add("/debug");
            if (optimizeCheck.Checked)
                cmdParts.Add("/optimize+");

            cmdParts.AddRange(new[] { "/warn:4", $"\"{inputFile}\"", $"/out:{outputFile}" });
            if (autoRunCheck.Checked)
                cmdParts.AddRange(new[] { "&&", $"\"{outputFile}\"" });

            return string.Join(" ", cmdParts);
        }

        private string GenerateJavaCommand(string inputFile, string outputFile)
        {
            var cmdParts = new List<string> { $"\"{config["javac_path"]}\"", $"\"{inputFile}\"" };
            if (autoRunCheck.Checked)
            {
                string javaPath = config["java_path"];
                string className = Path.GetFileNameWithoutExtension(inputFile);
                string inputDir = Path.GetDirectoryName(inputFile);
                cmdParts.AddRange(new[] { "&&", "cd", $"\"{inputDir}\"", "&&", $"\"{javaPath}\"", className });
            }
            return string.Join(" ", cmdParts);
        }

        private string GenerateJniCommand(string compiler, string inputFile, string outputFile)
        {
            return "JNI build requires multiple steps. Use the full JNI workflow.";
        }

        private void UpdateCommandPreview()
        {
            commandText.Text = GenerateCommand();
        }

        private async void BuildProject()
        {
            string command = GenerateCommand();
            if (command.Contains("Please") || command.Contains("Unsupported"))
            {
                MessageBox.Show(command, "Error");
                return;
            }

            outputText.AppendText($"Executing: {command}\r\n\r\n");
            await Task.Run(() => ExecuteBuild(command));
            // Nếu auto-run, chạy file thực thi sau khi build thành công
            if (autoRunCheck.Checked)
            {
                RunExecutable();
            }
        }

        private void ExecuteBuild(string command)
        {
            try
            {
                // Tách executable và arguments
                int firstQuote = command.IndexOf('"', 1);
                string exePath = command.Substring(1, firstQuote - 1);
                string args = command.Substring(firstQuote + 1).Trim();

                var process = new Process
                {
                    StartInfo = new ProcessStartInfo
                    {
                        FileName = exePath,
                        Arguments = args,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        UseShellExecute = false,
                        CreateNoWindow = true,
                        StandardOutputEncoding = Encoding.UTF8,
                        StandardErrorEncoding = Encoding.UTF8
                    }
                };

                process.Start();

                string stdout = process.StandardOutput.ReadToEnd();
                string stderr = process.StandardError.ReadToEnd();
                process.WaitForExit();

                BeginInvoke(new Action(() =>
                {
                    if (!string.IsNullOrEmpty(stdout))
                        outputText.AppendText(stdout);
                    if (!string.IsNullOrEmpty(stderr))
                    {
                        outputText.AppendText($"\r\n--- STDERR ---\r\n{stderr}");
                        AnalyzeErrors(stderr);
                    }

                    outputText.AppendText(process.ExitCode == 0 ?
                        "\r\n✅ Build completed successfully!\r\n" :
                        $"\r\n❌ Build failed with return code {process.ExitCode}\r\n");
                }));
            }
            catch (Exception ex)
            {
                BeginInvoke(new Action(() => outputText.AppendText($"\r\n❌ Error executing command: {ex.Message}\r\n")));
            }
        }

        private void AnalyzeErrors(string errorText)
        {
            var errorAnalysis = new List<string>();
            foreach (string line in errorText.Split(new[] { "\r\n", "\n" }, StringSplitOptions.None))
            {
                if (string.IsNullOrEmpty(line))
                    continue;

                if (line.ToLower().Contains("error:"))
                {
                    if (line.ToLower().Contains("no such file or directory"))
                        errorAnalysis.Add("❌ Missing file/header - Check include paths");
                    else if (line.ToLower().Contains("undefined reference"))
                        errorAnalysis.Add("❌ Linking error - Check library paths");
                    else if (line.ToLower().Contains("permission denied"))
                        errorAnalysis.Add("❌ Permission denied - Check file permissions");
                    else if (line.ToLower().Contains("syntax error"))
                        errorAnalysis.Add("❌ Syntax error in source code");
                    else
                        errorAnalysis.Add($"❌ {line}");
                }
                else if (line.ToLower().Contains("warning:"))
                    errorAnalysis.Add($"⚠️ {line}");
            }

            string summary = errorAnalysis.Count > 0 ?
                string.Join("\r\n", errorAnalysis.Take(10)) + (errorAnalysis.Count > 10 ? $"\r\n... and {errorAnalysis.Count - 10} more errors" : "") :
                "No specific errors detected in output";

            BeginInvoke(new Action(() => errorSummary.Text = summary));
        }

        private async void RunExecutable()
        {
            string outputFile = outputFileText.Text;
            if (string.IsNullOrEmpty(outputFile))
            {
                MessageBox.Show("No output file specified", "Error");
                return;
            }

            if (!File.Exists(outputFile))
            {
                MessageBox.Show($"Output file does not exist: {outputFile}", "Error");
                return;
            }

            if (!outputFile.EndsWith(".exe") && !outputFile.EndsWith(".jar"))
            {
                if (languageCombo.SelectedItem.ToString() == "Java")
                {
                    RunJavaClass();
                    return;
                }
                MessageBox.Show("Not an executable file", "Error");
                return;
            }

            runtimeText.AppendText($"🚀 Running: {outputFile}\r\n{new string('=', 50)}\r\n");
            await Task.Run(() => ExecuteRuntime(outputFile));
        }

        private void ExecuteRuntime(string executablePath)
        {
            try
            {
                string exeDir = Path.GetDirectoryName(executablePath);
                string exeName = Path.GetFileName(executablePath);

                var process = new Process
                {
                    StartInfo = new ProcessStartInfo
                    {
                        FileName = executablePath,
                        WorkingDirectory = exeDir,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        UseShellExecute = false,
                        CreateNoWindow = true,
                        StandardOutputEncoding = Encoding.UTF8,
                        StandardErrorEncoding = Encoding.UTF8
                    }
                };

                process.Start();

                string stdout = process.StandardOutput.ReadToEnd();
                string stderr = process.StandardError.ReadToEnd();
                process.WaitForExit();

                BeginInvoke(new Action(() =>
                {
                    if (!string.IsNullOrEmpty(stdout))
                    {
                        runtimeText.AppendText(stdout);
                        outputText.AppendText(stdout);
                    }
                    if (!string.IsNullOrEmpty(stderr))
                    {
                        runtimeText.AppendText($"\r\n--- Runtime Errors ---\r\n{stderr}");
                        outputText.AppendText($"\r\n--- Runtime Errors ---\r\n{stderr}");
                    }
                    string finishMsg = $"\r\n🏁 Program finished with exit code: {process.ExitCode}\r\n";
                    runtimeText.AppendText(finishMsg);
                    outputText.AppendText(finishMsg);
                }));
            }
            catch (Exception ex)
            {
                string errorMsg = $"❌ Error running executable: {ex.Message}\r\n";
                runtimeText.AppendText(errorMsg);
                outputText.AppendText(errorMsg);
                // BeginInvoke(new Action(() => runtimeText.AppendText($"\r\n❌ Runtime error: {ex.Message}\r\n")));
            }
        }

        private async void RunJavaClass()
        {
            string inputFile = inputFileText.Text;
            if (string.IsNullOrEmpty(inputFile))
            {
                MessageBox.Show("No input file specified", "Error");
                return;
            }

            string javaPath = config["java_path"];
            string className = Path.GetFileNameWithoutExtension(inputFile);
            string classDir = Path.GetDirectoryName(inputFile);
            string command = $"cd \"{classDir}\" && \"{javaPath}\" {className}";

            runtimeText.AppendText($"🚀 Running Java: {command}\r\n{new string('=', 50)}\r\n");
            await Task.Run(() => ExecuteJavaRuntime(command));
        }

        private void ExecuteJavaRuntime(string command)
        {
            try
            {
                var process = new Process
                {
                    StartInfo = new ProcessStartInfo
                    {
                        FileName = "cmd.exe",
                        Arguments = $"/c {command}",
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        UseShellExecute = false,
                        CreateNoWindow = true,
                        StandardOutputEncoding = Encoding.UTF8,
                        StandardErrorEncoding = Encoding.UTF8
                    }
                };

                process.Start();

                string stdout = process.StandardOutput.ReadToEnd();
                string stderr = process.StandardError.ReadToEnd();
                process.WaitForExit();

                BeginInvoke(new Action(() =>
                {
                    if (!string.IsNullOrEmpty(stdout))
                        runtimeText.AppendText(stdout);
                    if (!string.IsNullOrEmpty(stderr))
                        runtimeText.AppendText($"\r\n--- Runtime Errors ---\r\n{stderr}");
                    runtimeText.AppendText($"\r\n🏁 Java program finished with exit code: {process.ExitCode}\r\n");
                }));
            }
            catch (Exception ex)
            {
                BeginInvoke(new Action(() => runtimeText.AppendText($"\r\n❌ Java runtime error: {ex.Message}\r\n")));
            }
        }

        private void DebugExecutable()
        {
            string outputFile = outputFileText.Text;
            if (string.IsNullOrEmpty(outputFile))
            {
                MessageBox.Show("No output file specified", "Error");
                return;
            }

            if (!File.Exists(outputFile))
            {
                MessageBox.Show($"Output file does not exist: {outputFile}", "Error");
                return;
            }

            string compiler = compilerCombo.SelectedItem.ToString();
            if (compiler == "GCC" || compiler == "Clang")
            {
                string debugCommand = $"gdb \"{outputFile}\"";
                debugText.AppendText($"🐛 Starting debugger: {debugCommand}\r\n");
                debugText.AppendText("💡 Basic GDB commands:\r\n");
                debugText.AppendText("  - run: Start the program\r\n");
                debugText.AppendText("  - break main: Set breakpoint at main\r\n");
                debugText.AppendText("  - step: Step through code\r\n");
                debugText.AppendText("  - continue: Continue execution\r\n");
                debugText.AppendText("  - backtrace: Show call stack\r\n");
                debugText.AppendText("  - quit: Exit debugger\r\n");
                debugText.AppendText($"{new string('=', 50)}\r\n");

                try
                {
                    Process.Start("cmd.exe", $"/k cd /d {Path.GetDirectoryName(outputFile)} && {debugCommand}");
                    debugText.AppendText("🚀 Debugger launched in new terminal window\r\n");
                }
                catch (Exception ex)
                {
                    debugText.AppendText($"❌ Failed to launch debugger: {ex.Message}\r\n");
                    debugText.AppendText($"💡 Manual command: {debugCommand}\r\n");
                }
            }
            else if (compiler == "MSVC")
            {
                string pdbFile = outputFile.Replace(".exe", ".pdb");
                if (File.Exists(pdbFile))
                    MessageBox.Show($"Debug symbols found: {pdbFile}\r\nUse Visual Studio debugger to debug this executable.", "Debug Info");
                else
                    MessageBox.Show("No debug symbols found. Rebuild with debug mode enabled.", "No Debug Info");
            }
            else
                MessageBox.Show("Debug not supported for this compiler", "Error");
        }

        private void OpenOutputFolder()
        {
            string outputFile = outputFileText.Text;
            if (string.IsNullOrEmpty(outputFile))
            {
                MessageBox.Show("No output file specified", "Error");
                return;
            }

            string outputDir = Path.GetDirectoryName(outputFile);
            if (!Directory.Exists(outputDir))
            {
                MessageBox.Show($"Output directory does not exist: {outputDir}", "Error");
                return;
            }

            try
            {
                Process.Start("explorer.exe", outputDir);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to open folder: {ex.Message}", "Error");
            }
        }

        private void ClearOutput()
        {
            outputText.Clear();
            runtimeText.Clear();
            debugText.Clear();
            errorSummary.Clear();
        }

        private void MainForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            SaveConfig();
        }

        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainForm());
        }
    }
}