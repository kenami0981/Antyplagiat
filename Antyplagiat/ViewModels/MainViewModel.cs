using Antyplagiat.Helpers;

namespace Antyplagiat.ViewModels
{
    public class MainViewModel : ViewModelBase
    {
        private ViewModelBase _currentView;

        public ViewModelBase CurrentView
        {
            get => _currentView;
            set
            {
                _currentView = value;
                OnPropertyChanged(); 
            }
        }

        public MainViewModel()
        {
            CurrentView = new InputViewModel(this);
        }

        public void NavigateTo(ViewModelBase viewModel)
        {
            CurrentView = viewModel;
        }
    }
}