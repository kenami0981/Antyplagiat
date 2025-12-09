using PdfiumViewer;
using System;
using System.Collections.Generic;
using System.IO;
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
using System.Windows.Shapes;
using System.Windows.Forms.Integration;

using static Antyplagiat.Ekran1;

namespace Antyplagiat
{
    public partial class Ekran2 : UserControl
    {
        private PythonResult _result;
        private string _pdfPath;
        
        public Ekran2(PythonResult result, string latexFilePath)
        {

            InitializeComponent();
            if (result != null && !string.IsNullOrEmpty(result.RawOutput))
            {
                // przykładowe linie w wyniku:
                // "Plagiat Tekstu: 100.00%"
                // "Plagiat Równań: 100.00%"

                string textPercent = "Brak danych";
                string eqPercent = "Brak danych";

                var lines = result.RawOutput.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);
                foreach (var line in lines)
                {
                    if (line.StartsWith("Plagiat Tekstu:"))
                        textPercent = line.Substring("Plagiat Tekstu:".Length).Trim();
                    else if (line.Contains("Plagiat R"))
                        eqPercent = line.Split(':')[1].Trim();
                }

                WynikText.Text = $"Plagiat Tekstu: {textPercent}\nPlagiat Równań: {eqPercent}";
            }
            else
            {
                WynikText.Text = "Wystąpił błąd analizy.";
            }

            string directory = System.IO.Path.GetDirectoryName(latexFilePath);
            _pdfPath = System.IO.Path.Combine(directory, "raport_plagiatu.pdf");

            if (!File.Exists(_pdfPath))
            {
                MessageBox.Show("Nie znaleziono pliku PDF:\n" + _pdfPath);
                return;
            }

            var pdfViewer = new PdfViewer();
            pdfViewer.Document = PdfDocument.Load(_pdfPath);
            pdfViewer.ZoomMode = PdfViewerZoomMode.FitWidth;

            PdfHost.Child = pdfViewer;

        }

    }

}

