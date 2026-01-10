using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using System.IO;
using System.Threading;


namespace Antyplagiat
{
    /// <summary>
    /// Logika interakcji dla klasy Ekran1.xaml
    /// </summary>
    /// 
    public class PythonResult
    {
        public string RawOutput { get; set; }
    }

    public partial class Ekran1 : UserControl
    {
        private MainWindow _main;
        private string selectedLatexFile;

        public Ekran1(MainWindow main)
        {
            InitializeComponent();
            _main = main;
        }
        
            
         
        public async Task<string> RunPythonSafeAsync(string scriptPath, string args)
        {
            var psi = new ProcessStartInfo
            {
                FileName = "py",
                Arguments = $"\"{scriptPath}\" {args}",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8
            };

            var process = new Process();
            process.StartInfo = psi;

            var outputBuilder = new StringBuilder();
            var errorBuilder = new StringBuilder();

            // Eventy — ODBIERAJĄ strumienie w tle
            process.OutputDataReceived += (s, e) =>
            {
                if (e.Data != null) outputBuilder.AppendLine(e.Data);
            };
            process.ErrorDataReceived += (s, e) =>
            {
                if (e.Data != null) errorBuilder.AppendLine(e.Data);
            };

            process.Start();
            process.BeginOutputReadLine();
            process.BeginErrorReadLine();

            await WaitForExitAsync(process);

            return outputBuilder.ToString() + "\n" + errorBuilder.ToString();
        }
        public static Task WaitForExitAsync(Process process)
        {
            if (process.HasExited)
                return Task.CompletedTask;

            var tcs = new TaskCompletionSource<object>();
            process.EnableRaisingEvents = true;
            process.Exited += (s, e) => tcs.TrySetResult(null);
            return tcs.Task;
        }



        private void SelectLatexFile_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog dialog = new OpenFileDialog();
            dialog.Filter = "Pliki LaTeX (*.tex)|*.tex|Wszystkie pliki (*.*)|*.*";

            if (dialog.ShowDialog() == true)
            {
                selectedLatexFile = dialog.FileName;
                MessageBox.Show($"Wybrano plik:\n{selectedLatexFile}", "OK", MessageBoxButton.OK, MessageBoxImage.Information);
            }
        }
        private async void CheckDocClicked(object sender, RoutedEventArgs e)
        {
            
            if (string.IsNullOrEmpty(selectedLatexFile) || !File.Exists(selectedLatexFile))
            {
                MessageBox.Show("Nie wybrano pliku .tex!", "Błąd", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            if (!(PoziomNiski.IsChecked == true ||
                  PoziomSredni.IsChecked == true ||
                  PoziomWysoki.IsChecked == true ||
                  PoziomBardzoWysoki.IsChecked == true))
            {
                MessageBox.Show("Musisz zaznaczyć poziom podobieństwa!", "Błąd", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            //Kod co ma dalej być jeśli walidacja się powiodła
            
            string level = GetLevel();

            string speed = "normal"; //na razie stała wartość

            string script = System.IO.Path.Combine(
                AppDomain.CurrentDomain.BaseDirectory, "..", "..","src", "main.py"
            );
            script = System.IO.Path.GetFullPath(script);

            string result = await RunPythonSafeAsync(script, $"\"{selectedLatexFile}\" {level} {speed}");
            MessageBox.Show(result);
            Console.Write(result);
            PythonResult r = new PythonResult
            {
                RawOutput = result
            };

            _main.Content = new Ekran2(r, selectedLatexFile);











            //            string level = GetLevel();

            //            string script = System.IO.Path.Combine(
            //    AppDomain.CurrentDomain.BaseDirectory, "..", "..", "analiza.py"
            //);
            //script = System.IO.Path.GetFullPath(script);

            //string result = RunPython1(script, $"\"{selectedLatexFile}\" {level}");

            //MessageBox.Show("Wynik:\n" + result);
        }
        private string GetLevel()
        {
            if (PoziomNiski.IsChecked == true) return "niski";
            if (PoziomSredni.IsChecked == true) return "średni";
            if (PoziomWysoki.IsChecked == true) return "wysoki";
            if (PoziomBardzoWysoki.IsChecked == true) return "bardzo_wysoki";
            return "brak";
        }
        public string RunPython1(string scriptPath, string args)
        {
            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = $"\"{scriptPath}\" {args}",
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            var process = Process.Start(psi);

            // limit czasu – jak python nie odpowiada → ucinamy
            if (!process.WaitForExit(5000))  // 5 sekund
            {
                process.Kill();
                return "[PYTHON ERROR]\nTimeout – Python nie zwrócił żadnego wyniku!";
            }

            string output = process.StandardOutput.ReadToEnd();
            string error = process.StandardError.ReadToEnd();

            if (!string.IsNullOrWhiteSpace(error))
                return output + "\n[PYTHON ERROR]\n" + error;

            return output;
        }

        public string RunPython(string scriptPath, string args)
        {
            ProcessStartInfo psi = new ProcessStartInfo();
            psi.FileName = "py";
            psi.Arguments = $"\"{scriptPath}\" {args}";
            psi.RedirectStandardOutput = true;
            psi.RedirectStandardError = true;       // <──── MUSI BYĆ
            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;

            var process = Process.Start(psi);

            // Odczyt wyjść
            string output = process.StandardOutput.ReadToEnd();
            string error = process.StandardError.ReadToEnd();

            process.WaitForExit();

            if (process.ExitCode != 0)
                return output + "\n[PYTHON ERROR]\n" + error;

            return output;
        }

    }

}
