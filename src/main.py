"""
TurkScript Syntax Highlighter - main.py
Real-Time Grammar-Based Syntax Highlighter with GUI
"""

import sys
import traceback
from gui import TurkScriptGUI

def main():
    """Uygulamanin baslatildigi ana fonksiyon"""
    print("TurkScript Syntax Highlighter başlatılıyor...")
    print("=" * 50)
    print("Proje:     Real-Time Grammar-Based Syntax Highlighter")
    print("Ad Soyad:  Edem Makhsudov")
    print("Ogr No:    22360859373")
    print("Dil:       TurkScript (Türkçe anahtar kelimelerle)")
    print("GUI:       Python Tkinter")
    print("=" * 50)

    try:
        # Ana GUI uygulamasini olustur ve baslat
        app = TurkScriptGUI()
        print("GUI başarıyla yüklendi!")
        print("Syntax highlighting aktif...")
        app.run()

    except ImportError as e:
        # Gerekli moduller bulunamazsa hata mesaji
        print(f"Modül import hatası: {e}")
        print("Gerekli modüllerin yüklendiğinden emin olun:")
        print("- tkinter (Python ile birlikte gelir)")
        print("- lexer.py, turkscript_parser.py, gui.py dosyaları")
        sys.exit(1)

    except Exception as e:
        # Beklenmeyen hata durumunda detayli bilgi
        print(f"Beklenmeyen hata: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()