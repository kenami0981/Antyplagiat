using Antyplagiat.Helpers;
using Antyplagiat.Models;
using System.IO;

namespace Antyplagiat.ViewModels
{
    public class ResultViewModel : ViewModelBase
    {
        private readonly MainViewModel _mainViewModel;

        // Dane do wyświetlenia w View
        public string ResultText { get; set; }
        public string PdfPath { get; set; }

        public RelayCommand GoBackCommand { get; }

        // Konstruktor przyjmuje wynik analizy
        public ResultViewModel(MainViewModel mainViewModel, AnalysisResult result)
        {
            _mainViewModel = mainViewModel;

            // Mapowanie danych z modelu na format tekstowy dla widoku
            // Np.: "Plagiat Tekstu: 23.5%\nPlagiat Równań: 0%"
            ResultText = FormatResultText(result);

            // Przekazanie ścieżki do PDF (widok obsłuży ładowanie w Code-Behind)
            PdfPath = result.ReportPdfPath;

            // Komenda powrotu - tworzymy nowy InputViewModel
            GoBackCommand = new RelayCommand(o =>
            {
                _mainViewModel.NavigateTo(new InputViewModel(_mainViewModel));
            });
        }

        private string FormatResultText(AnalysisResult result)
        {
            if (!result.IsSuccess)
                return "Błąd analizy danych.";

            // Formatowanie liczb do 2 miejsc po przecinku
            string textP = result.TextPlagiarismPercent.ToString("F2");
            string eqP = result.EquationPlagiarismPercent.ToString("F2");

            return $"Plagiat Tekstu: {textP}%\nPlagiat Równań: {eqP}%";
        }
    }
}