using Antyplagiat.Models;
using System;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Text;
using System.Threading.Tasks;

namespace Antyplagiat.Services
{
    public class PythonAnalysisService
    {
        // ZMIANA: Zwracamy Task<AnalysisResult>, a nie Task<string>
        public async Task<AnalysisResult> AnalyzeAsync(string latexPath, string level, string speed = "normal")
        {
            string scriptPath = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "src", "main.py"));

            var psi = new ProcessStartInfo
            {
                FileName = "py", // lub "python"
                Arguments = $"\"{scriptPath}\" \"{latexPath}\" {level} {speed}",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8
            };

            string rawOutput = "";
            string errorOutput = "";

            // Uruchomienie procesu
            await Task.Run(() =>
            {
                using (var process = new Process { StartInfo = psi })
                {
                    var outputBuilder = new StringBuilder();
                    var errorBuilder = new StringBuilder();

                    process.OutputDataReceived += (s, e) => { if (e.Data != null) outputBuilder.AppendLine(e.Data); };
                    process.ErrorDataReceived += (s, e) => { if (e.Data != null) errorBuilder.AppendLine(e.Data); };

                    process.Start();
                    process.BeginOutputReadLine();
                    process.BeginErrorReadLine();
                    process.WaitForExit();

                    rawOutput = outputBuilder.ToString();
                    errorOutput = errorBuilder.ToString();
                }
            });

            // Parsowanie wyniku do modelu AnalysisResult
            return ParseOutput(rawOutput, errorOutput, latexPath);
        }

        private AnalysisResult ParseOutput(string output, string error, string sourceFilePath)
        {
            var result = new AnalysisResult
            {
                RawLog = output + "\n" + error,
                IsSuccess = true,
                // Zakładamy, że PDF tworzy się w tym samym folderze co plik .tex
                ReportPdfPath = Path.Combine(Path.GetDirectoryName(sourceFilePath), "raport_plagiatu.pdf")
            };

            // Jeśli Python zwrócił błąd w strumieniu błędu, oznaczamy to (chyba że to tylko ostrzeżenia)
            // Tutaj prosta logika: jeśli output jest pusty, a jest błąd -> fail.
            if (string.IsNullOrWhiteSpace(output) && !string.IsNullOrWhiteSpace(error))
            {
                result.IsSuccess = false;
                result.ErrorMessage = "Błąd Pythona: " + error;
                return result;
            }

            try
            {
                var lines = output.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);
                foreach (var line in lines)
                {
                    // Szukamy linii w stylu "Plagiat Tekstu: 45.00%"
                    if (line.Contains("Plagiat Tekstu:"))
                    {
                        var val = line.Split(':')[1].Trim().Replace("%", "");
                        if (double.TryParse(val, NumberStyles.Any, CultureInfo.InvariantCulture, out double tp))
                            result.TextPlagiarismPercent = tp;
                    }
                    else if (line.Contains("Plagiat Równań:") || line.Contains("Plagiat R"))
                    {
                        var val = line.Split(':')[1].Trim().Replace("%", "");
                        if (double.TryParse(val, NumberStyles.Any, CultureInfo.InvariantCulture, out double ep))
                            result.EquationPlagiarismPercent = ep;
                    }
                }
            }
            catch (Exception ex)
            {
                result.IsSuccess = false;
                result.ErrorMessage = "Błąd parsowania wyników: " + ex.Message;
            }

            return result;
        }
    }
}