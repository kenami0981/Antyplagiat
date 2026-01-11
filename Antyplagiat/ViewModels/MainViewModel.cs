using Antyplagiat.Helpers;

namespace Antyplagiat.ViewModels
{
    public class MainViewModel : ViewModelBase
    {
        // To pole przechowuje aktualny ViewModel (InputView lub ResultView)
        private ViewModelBase _currentView;

        public ViewModelBase CurrentView
        {
            get => _currentView;
            set
            {
                _currentView = value;
                OnPropertyChanged(); // Powiadamia widok (MainWindow), że treść się zmieniła
            }
        }

        public MainViewModel()
        {
            // Na start uruchamiamy widok wejściowy, przekazując "siebie" (this),
            // aby InputViewModel mógł potem poprosić o zmianę ekranu.
            CurrentView = new InputViewModel(this);
        }

        // Metoda służąca do zmiany ekranu
        public void NavigateTo(ViewModelBase viewModel)
        {
            CurrentView = viewModel;
        }
    }
}