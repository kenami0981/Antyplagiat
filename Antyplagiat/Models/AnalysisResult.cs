using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Antyplagiat.Models
{
    public class AnalysisResult
    {
        public string RawLog { get; set; }

        public double TextPlagiarismPercent { get; set; }
        public double EquationPlagiarismPercent { get; set; }

        public string ReportPdfPath { get; set; }

        public bool IsSuccess { get; set; }
        public string ErrorMessage { get; set; }
    }
}
