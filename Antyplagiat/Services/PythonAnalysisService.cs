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
        public async Task<AnalysisResult> AnalyzeAsync(string latexPath, string level, string speed, IProgress<int> progressReporter)
        {
            string scriptPath = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "src", "main.py"));

            var psi = new ProcessStartInfo
            {
                FileName = "py",
                Arguments = $"\"{scriptPath}\" \"{latexPath}\" {level} {speed}",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true,
                StandardOutputEncoding = Encoding.UTF8,
                StandardErrorEncoding = Encoding.UTF8
            };

            var outputBuilder = new StringBuilder();
            var errorBuilder = new StringBuilder();

            return await Task.Run(() =>
            {
                using (var process = new Process { StartInfo = psi })
                {
                    process.OutputDataReceived += (s, e) =>
                    {
                        if (e.Data != null)
                        {
                            outputBuilder.AppendLine(e.Data);

                            if (e.Data.StartsWith("PROGRESS:"))
                            {
                                var parts = e.Data.Split(':');
                                if (parts.Length > 1 && int.TryParse(parts[1].Trim(), out int p))
                                {
                                    progressReporter?.Report(p);
                                }
                            }
                        }
                    };

                    process.ErrorDataReceived += (s, e) =>
                    {
                        if (e.Data != null) errorBuilder.AppendLine(e.Data);
                    };

                    process.Start();
                    process.BeginOutputReadLine();
                    process.BeginErrorReadLine();
                    process.WaitForExit();

                    string rawOutput = outputBuilder.ToString();
                    string errorOutput = errorBuilder.ToString();

                    return ParseOutput(rawOutput, errorOutput, latexPath);
                }
            });
        }

        private AnalysisResult ParseOutput(string output, string error, string sourceFilePath)
        {
            var result = new AnalysisResult
            {
                RawLog = output + "\n" + error,
                IsSuccess = true,
                ReportPdfPath = Path.Combine(Path.GetDirectoryName(sourceFilePath), "raport_plagiatu.pdf")
            };

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