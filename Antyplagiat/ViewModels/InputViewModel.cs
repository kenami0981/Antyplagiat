using Antyplagiat.Helpers;
using Antyplagiat.Models;
using Antyplagiat.Services;
using Microsoft.Win32;
using System.Threading.Tasks;
using System.Windows; 

namespace Antyplagiat.ViewModels
{
    public class InputViewModel : ViewModelBase
    {
        private readonly MainViewModel _mainViewModel;
        private readonly PythonAnalysisService _pythonService;

        private string _selectedFilePath;
        private bool _isBusy;

        public bool LevelLow { get; set; }
        public bool LevelMedium { get; set; }
        public bool LevelHigh { get; set; }
        public bool LevelVeryHigh { get; set; }

        public bool TypeFast { get; set; }
        public bool TypeNormal { get; set; }

        public string SelectedFilePath
        {
            get => _selectedFilePath;
            set
            {
                _selectedFilePath = value;
                OnPropertyChanged();
                // Gdy zmienia się ścieżka, aktualizujemy też tekst wyświetlany na przycisku
                OnPropertyChanged(nameof(FileNameDisplay));
            }
        }

        // Pomocnicza właściwość dla Widoku - pokazuje nazwę pliku lub domyślny tekst
        public string FileNameDisplay => string.IsNullOrEmpty(SelectedFilePath)
            ? "Wybierz plik LaTeX"
            : System.IO.Path.GetFileName(SelectedFilePath);

        // Flaga blokująca przycisk podczas analizy
        public bool IsBusy
        {
            get => _isBusy;
            set
            {
                _isBusy = value;
                OnPropertyChanged();
                // Odświeżamy stan przycisku (czy jest aktywny)
                AnalyzeCommand.RaiseCanExecuteChanged();
            }
        }

        // Komendy (akcje wywoływane przez przyciski)
        public RelayCommand SelectFileCommand { get; }
        public RelayCommand AnalyzeCommand { get; }

        public InputViewModel(MainViewModel mainViewModel)
        {
            _mainViewModel = mainViewModel;
            _pythonService = new PythonAnalysisService();

            SelectFileCommand = new RelayCommand(o => SelectFile());

            // Komenda Analizy: wykonaj AnalyzeDocs, ale tylko jeśli !IsBusy
            AnalyzeCommand = new RelayCommand(async o => await AnalyzeDocs(), o => !IsBusy);
        }

        private void SelectFile()
        {
            OpenFileDialog dialog = new OpenFileDialog
            {
                Filter = "Pliki LaTeX (*.tex)|*.tex|Wszystkie pliki (*.*)|*.*"
            };

            if (dialog.ShowDialog() == true)
            {
                SelectedFilePath = dialog.FileName;
            }
        }

        private SimilarityLevels? GetSelectedLevel()
        {
            if (LevelLow) return SimilarityLevels.Low;
            if (LevelMedium) return SimilarityLevels.Medium;
            if (LevelHigh) return SimilarityLevels.High;
            if (LevelVeryHigh) return SimilarityLevels.VeryHigh;
            return null;
        }

        private TestTypes? GetSelectedType()
        {
            if (TypeFast) return TestTypes.Fast;
            if (TypeNormal) return TestTypes.Normal;
            return null; 
        }

        private async Task AnalyzeDocs()
        {
            // 1. Walidacja
            if (string.IsNullOrEmpty(SelectedFilePath) || !System.IO.File.Exists(SelectedFilePath))
            {
                MessageBox.Show("Nie wybrano poprawnego pliku .tex!", "Błąd", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            var level = GetSelectedLevel();
            if (level == null)
            {
                MessageBox.Show("Musisz zaznaczyć poziom podobieństwa!", "Błąd", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            var type = GetSelectedType();
            if (type == null)
            {
                MessageBox.Show("Musisz zaznaczyć typ analizy!", "Błąd", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            IsBusy = true;

            try
            {
                string pyLevel = "";
                if (level == SimilarityLevels.Low) pyLevel = "niski";
                if (level == SimilarityLevels.Medium) pyLevel = "średni";
                if (level == SimilarityLevels.High) pyLevel = "wysoki";
                if (level == SimilarityLevels.VeryHigh) pyLevel = "bardzo_wysoki";

                string pyType = "";
                if (type == TestTypes.Fast) pyType = "fast";
                if (type == TestTypes.Normal) pyType = "normal";

                _mainViewModel.NavigateTo(new ProgressViewModel(_mainViewModel, SelectedFilePath, pyLevel, pyType));
            }
            catch (System.Exception ex)
            {
                MessageBox.Show($"Krytyczny błąd aplikacji:\n{ex.Message}", "Błąd", MessageBoxButton.OK, MessageBoxImage.Error);
            }
            finally
            {
                IsBusy = false;
            }
        }
    }
}