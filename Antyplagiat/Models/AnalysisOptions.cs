using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Antyplagiat.Models
{
    public class AnalysisOptions
    {
        public string FilePath { get; set; }
        public SimilarityLevels Similarity { get; set; }
        // Opcjonalnie, jeśli planujesz to zmieniać w przyszłości:
        public string Speed { get; set; } = "normal";
    }
}
