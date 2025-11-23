using Microsoft.Win32;
using System;
using System.Collections.Generic;
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
using System.Windows.Navigation;
using System.Windows.Shapes;
using System.IO;

namespace Antyplagiat
{
    /// <summary>
    /// Logika interakcji dla klasy MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private string selectedLatexFile = null;
        public MainWindow()
        {
            InitializeComponent();
        }

        private void SelectLatexFile_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog dialog = new OpenFileDialog();
            dialog.Filter = "Pliki LaTeX (*.tex)|*.tex|Wszystkie pliki (*.*)|*.*";

            if (dialog.ShowDialog() == true)
            {
                selectedLatexFile = dialog.FileName;
                MessageBox.Show($"Wybrano plik:\n{selectedLatexFile}", "OK", MessageBoxButton.OK, MessageBoxImage.Information);
            }
        }
        private void CheckDocClicked(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(selectedLatexFile) || !File.Exists(selectedLatexFile))
            {
                MessageBox.Show("Nie wybrano pliku .tex!", "Błąd", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            if (!(PoziomNiski.IsChecked == true ||
                  PoziomSredni.IsChecked == true ||
                  PoziomWysoki.IsChecked == true ||
                  PoziomBardzoWysoki.IsChecked == true))
            {
                MessageBox.Show("Musisz zaznaczyć poziom poprawności!", "Błąd", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            //Kod co ma dalej być jeśli walidacja się powiodła
            MessageBox.Show("OK");
        }
    }
}
