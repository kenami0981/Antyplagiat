using System.IO;
using System.Windows;
using System.Windows.Controls;
using PdfiumViewer;
using Antyplagiat.ViewModels; // Pamiętaj o dodaniu usinga do ViewModeli

namespace Antyplagiat.Views
{
    public partial class ResultView : UserControl
    {
        public ResultView()
        {
            InitializeComponent();
        }

        private void PdfHost_Loaded(object sender, RoutedEventArgs e)
        {
            // Próba rzutowania DataContext na nasz ViewModel
            if (DataContext is ResultViewModel viewModel)
            {
                if (!string.IsNullOrEmpty(viewModel.PdfPath) && File.Exists(viewModel.PdfPath))
                {
                    try
                    {
                        var pdfViewer = new PdfViewer();
                        pdfViewer.Document = PdfDocument.Load(viewModel.PdfPath);
                        pdfViewer.ZoomMode = PdfViewerZoomMode.FitWidth;

                        // Przypisanie kontrolki WinForms do Hosta WPF
                        PdfHost.Child = pdfViewer;
                    }
                    catch (System.Exception ex)
                    {
                        MessageBox.Show($"Nie udało się załadować PDF: {ex.Message}");
                    }
                }
            }
        }
    }
}