using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Antyplagiat.Models
{
    public class AnalysisResult
    {
        // Surowy tekst z konsoli (do debugowania lub logów)
        public string RawLog { get; set; }

        // Przetworzone wartości liczbowe (łatwiej na ich podstawie np. zmienić kolor tekstu na czerwony)
        public double TextPlagiarismPercent { get; set; }
        public double EquationPlagiarismPercent { get; set; }

        // Ścieżka do wygenerowanego raportu PDF
        public string ReportPdfPath { get; set; }

        // Czy analiza zakończyła się sukcesem?
        public bool IsSuccess { get; set; }
        public string ErrorMessage { get; set; }
    }
}
