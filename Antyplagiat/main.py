import sys
import os
from cleaner import preprocessing
from engine import compare_with_folder
from reporter import create_pdf_report, build_final_text


def run_analysis(input_path, base_path, difficulty_level, mode="all"):
    print("Ścieżka do pliku:", input_path)
    print("Poziom trudności:", difficulty_level)

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku wejściowego: {input_path}")
        return
    except Exception as e:
        print(f"BŁĄD: Nie można odczytać pliku wejściowego: {e}")
        return

    equations, text, clean_text = preprocessing(content)
    final_text = build_final_text(clean_text)


    percent_text, percent_eqs, segments_with_sources = compare_with_folder(
        equations, text, base_path, difficulty_level, mode=mode
    )

    compared_files = [f for f in os.listdir(base_path) if f.endswith(".tex")]

    output_pdf_path = os.path.join(
        os.path.dirname(input_path),
        "raport_plagiatu.pdf"
    )

    create_pdf_report(
        output_pdf_path,
        input_path,
        base_path,
        difficulty_level,
        mode,
        percent_text,
        percent_eqs,
        compared_files,
        final_text,
        segments_with_sources
    )

    print(f"\nPDF zapisany jako: {output_pdf_path}")
    return percent_text, percent_eqs


def main():
    #dane do testów bez argumentów
    STATIC_TEST_FILE = "bazaIO[test]\\test2.tex"
    STATIC_BASE_PATH = "bazaIO"
    STATIC_DIFFICULTY = "średni" # opcje: "niski", "średni", "wysoki", "bardzo_wysoki"
    STATIC_MODE = "fast"  # opcje: "all", "text_only", "eqs_only"

    #uruchomienie analizy z argumentami przekazanymi z C#
    if len(sys.argv) > 1:

        latex_file_path = sys.argv[1] # ścieżka do wybranego pliku
        difficulty = sys.argv[2] # poziom
        script_dir = os.path.dirname(os.path.abspath(__file__))
        baza_path = os.path.join(script_dir, "bazaIO[test]") # ścieżka do bazy
        
        run_analysis(latex_file_path, baza_path, difficulty)
    ## tryb testowy bez argumentów
    else:
        print("--- TRYB TESTOWY (BRAK ARGUMENTÓW) ---")
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, STATIC_TEST_FILE)
        base_dir_path = os.path.join(script_dir, STATIC_BASE_PATH)

        run_analysis(file_path, base_dir_path, STATIC_DIFFICULTY, mode=STATIC_MODE)


if __name__ == "__main__":
    main()