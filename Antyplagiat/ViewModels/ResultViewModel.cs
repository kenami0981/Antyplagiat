using Antyplagiat.Helpers;
using Antyplagiat.Models;
using System.IO;

namespace Antyplagiat.ViewModels
{
    public class ResultViewModel : ViewModelBase
    {
        private readonly MainViewModel _mainViewModel;

        public string ResultText { get; set; }
        public string PdfPath { get; set; }

        public RelayCommand GoBackCommand { get; }

        public ResultViewModel(MainViewModel mainViewModel, AnalysisResult result)
        {
            _mainViewModel = mainViewModel;


            ResultText = FormatResultText(result);

            PdfPath = result.ReportPdfPath;


            GoBackCommand = new RelayCommand(o =>
            {
                _mainViewModel.NavigateTo(new InputViewModel(_mainViewModel));
            });
        }

        private string FormatResultText(AnalysisResult result)
        {
            if (!result.IsSuccess)
                return "Błąd analizy danych.";

            string textP = result.TextPlagiarismPercent.ToString("F2");
            string eqP = result.EquationPlagiarismPercent.ToString("F2");

            return $"Plagiat Tekstu: {textP}%\nPlagiat Równań: {eqP}%";
        }
    }
}