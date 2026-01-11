using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Antyplagiat.Models
{
    public enum SimilarityLevels
    {
        Low,        // Odpowiada "niski" w skrypcie Python
        Medium,     // "średni"
        High,       // "wysoki"
        VeryHigh    // "bardzo_wysoki"
    }

    public enum TestTypes
    {         
        Fast,   // Odpowiada "fast" w skrypcie Python
        Normal  // "normal"
    }
}
