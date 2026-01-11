using Antyplagiat.Helpers;
using Antyplagiat.Models;
using Antyplagiat.Services;
using System;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using System.Windows;

namespace Antyplagiat.ViewModels
{
    public class ProgressViewModel : ViewModelBase
    {
        private readonly MainViewModel _mainViewModel;
        private readonly PythonAnalysisService _pythonService;

        // Dane wejściowe potrzebne do analizy
        private readonly string _filePath;
        private readonly string _level;
        private readonly string _type;

        // Wynik analizy (przechowujemy go do momentu kliknięcia przycisku)
        private AnalysisResult _analysisResult;

        private int _progressValue;
        private string _statusMessage;
        private bool _isAnalysisFinished;

        public int ProgressValue
        {
            get => _progressValue;
            set { _progressValue = value; OnPropertyChanged(); }
        }

        public string StatusMessage
        {
            get => _statusMessage;
            set { _statusMessage = value; OnPropertyChanged(); }
        }

        public bool IsAnalysisFinished
        {
            get => _isAnalysisFinished;
            set
            {
                _isAnalysisFinished = value;
                OnPropertyChanged();
                ShowResultCommand?.RaiseCanExecuteChanged();
            }
        }

        public RelayCommand ShowResultCommand { get; }

        public ProgressViewModel(MainViewModel mainViewModel, string filePath, string level, string type)
        {
            _mainViewModel = mainViewModel;
            _filePath = filePath;
            _level = level;
            _type = type;
            _pythonService = new PythonAnalysisService();

            ShowResultCommand = new RelayCommand(o => NavigateToResult(), o => IsAnalysisFinished);

            ProgressValue = 0;
            StatusMessage = "Inicjalizacja środowiska Python...";
            IsAnalysisFinished = false;

            Task.Run(StartAnalysis);
        }

        private async Task StartAnalysis()
        {
            // Obiekt raportujący postęp do UI
            var progress = new Progress<int>(percent =>
            {
                ProgressValue = percent;
                StatusMessage = $"Postęp sprawdzania... ({percent}%)";
            });

            try
            {

                _analysisResult = await _pythonService.AnalyzeAsync(_filePath, _level, _type, progress);

                ProgressValue = 100;
                StatusMessage = "Analiza zakończona pomyślnie.";
                IsAnalysisFinished = true;
            }
            catch (Exception ex)
            {
                StatusMessage = "Wystąpił błąd.";
                MessageBox.Show($"Błąd procesu: {ex.Message}");

                // W razie błędu możemy wrócić do menu
                Application.Current.Dispatcher.Invoke(() =>
                    _mainViewModel.NavigateTo(new InputViewModel(_mainViewModel)));
            }
        }

        private void NavigateToResult()
        {
            if (_analysisResult != null)
            {
                _mainViewModel.NavigateTo(new ResultViewModel(_mainViewModel, _analysisResult));
            }
        }
    }
}