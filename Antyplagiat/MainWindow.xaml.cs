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
using System.Diagnostics;

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
            string level = GetLevel();

            string script = System.IO.Path.Combine(
    AppDomain.CurrentDomain.BaseDirectory, "..", "..", "analiza.py"
);
            script = System.IO.Path.GetFullPath(script);

            string result = RunPython(script, $"\"{selectedLatexFile}\" {level}");

            MessageBox.Show("Wynik:\n" + result);
        }
        private string GetLevel()
        {
            if (PoziomNiski.IsChecked == true) return "niski";
            if (PoziomSredni.IsChecked == true) return "średni";
            if (PoziomWysoki.IsChecked == true) return "wysoki";
            if (PoziomBardzoWysoki.IsChecked == true) return "bardzo_wysoki";
            return "brak";
        }

        public string RunPython(string scriptPath, string args)
        {
            ProcessStartInfo psi = new ProcessStartInfo();
            psi.FileName = "py";
            psi.Arguments = $"\"{scriptPath}\" {args}";
            psi.RedirectStandardOutput = true;
            psi.RedirectStandardError = true;       // <──── MUSI BYĆ
            psi.UseShellExecute = false;
            psi.CreateNoWindow = true;

            var process = Process.Start(psi);

            // Odczyt wyjść
            string output = process.StandardOutput.ReadToEnd();
            string error = process.StandardError.ReadToEnd();

            process.WaitForExit();

            if (!string.IsNullOrWhiteSpace(error))
                return "Błąd z Pythona:\n" + error;

            return output;
        }

    }
}
