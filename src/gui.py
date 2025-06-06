"""
TurkScript Syntax Highlighter GUI
Basit metin editoru ile syntax highlighting
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import time
from lexer import TurkScriptLexer, TokenTuru
from turkscript_grammar import RENK_HARITASI, ORNEK_KOD

# Parser import'unu düzelt
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from turkscript_parser import TurkScriptParser

class TurkScriptGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TurkScript Syntax Highlighter")
        self.root.geometry("1000x600")
        self.root.configure(bg='#f0f0f0')

        # Lexer ve Parser nesneleri olustur
        self.lexer = TurkScriptLexer()
        self.parser = None

        # Anlık guncelleme ayarlari
        self.son_guncelleme = 0
        self.guncelleme_gecikmesi = 300

        self.setup_gui()
        self.ornek_kodu_yukle()

    def setup_gui(self):
        """Ana GUI bilesenleri olustur"""
        # Ana kapsayici frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Sol kisim - Kod editoru
        sol_frame = tk.LabelFrame(main_frame, text="TurkScript Kod Editörü",
                                 font=('Arial', 10, 'bold'), bg='#f0f0f0')
        sol_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Kod yazma alani
        self.metin_editor = scrolledtext.ScrolledText(
            sol_frame,
            wrap=tk.NONE,
            font=('Consolas', 12),
            bg='white',
            fg='black',
            insertbackground='black',
            selectbackground='lightblue',
            width=50,
            height=25,
            padx=10,
            pady=10
        )
        self.metin_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Metin degisikligi olaylarini izle
        self.metin_editor.bind('<KeyRelease>', self.metin_degisti)
        self.metin_editor.bind('<Button-1>', self.metin_degisti)

        # Sag kisim - Bilgi panelleri
        sag_frame = tk.Frame(main_frame, bg='#f0f0f0')
        sag_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        # Hata gosterim paneli
        hata_frame = tk.LabelFrame(sag_frame, text="Hatalar",
                                  font=('Arial', 9, 'bold'), bg='#f0f0f0')
        hata_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.hata_text = scrolledtext.ScrolledText(
            hata_frame,
            height=8,
            width=35,
            font=('Consolas', 9),
            bg='#ffe6e6',
            fg='#cc0000',
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.hata_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Token analiz paneli
        lexer_frame = tk.LabelFrame(sag_frame, text="Lexer Bilgisi",
                                   font=('Arial', 9, 'bold'), bg='#f0f0f0')
        lexer_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.lexer_text = scrolledtext.ScrolledText(
            lexer_frame,
            height=8,
            width=35,
            font=('Consolas', 9),
            bg='#e6f3ff',
            fg='#0066cc',
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.lexer_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Dil yardim paneli
        yardim_frame = tk.LabelFrame(sag_frame, text="TurkScript Yardım",
                                    font=('Arial', 9, 'bold'), bg='#f0f0f0')
        yardim_frame.pack(fill=tk.BOTH, expand=True)

        yardim_text = """TurkScript Anahtar Kelimeler:

Veri Tipleri:
sayi, metin, mantik, liste

Kontrol Yapıları:
eger, yoksa, dongu, iken

Fonksiyonlar:
fonksiyon, don, cagir

Değişkenler:
degisken, sabit

Mantıksal:
ve, veya, degil
dogru, yanlis

Giriş/Çıkış:
yazdir, oku

Örnek Kod:
degisken sayi x = 10;
eger (x > 5) {
    yazdir("Büyük");
}"""

        self.yardim_text = tk.Text(
            yardim_frame,
            height=10,
            width=35,
            font=('Consolas', 9),
            bg='#f0fff0',
            fg='#006600',
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.yardim_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Yardim metnini panele yukle
        self.yardim_text.config(state=tk.NORMAL)
        self.yardim_text.insert(tk.END, yardim_text)
        self.yardim_text.config(state=tk.DISABLED)

        # Alt durum gosterge cubugu
        self.status_label = tk.Label(
            self.root,
            text="📝 Hazır",
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#f0f0f0',
            font=('Arial', 9),
            fg='blue'
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

    def ornek_kodu_yukle(self):
        """Baslangiç ornek kodunu editore yukle"""
        self.metin_editor.insert('1.0', ORNEK_KOD.strip())
        self.syntax_highlighting_uygula()

    def metin_degisti(self, event=None):
        """Kullanici metin degistirdiginde cagrilir"""
        self.status_label.config(text="⏳ Analiz ediliyor...", fg='orange')
        self.son_guncelleme = time.time()
        # Gecikmeli analiz baslatir
        self.root.after(self.guncelleme_gecikmesi, self.gec_guncelleme)

    def gec_guncelleme(self):
        """Belirli gecikme sonrasi guncelleme yapar"""
        if time.time() - self.son_guncelleme >= self.guncelleme_gecikmesi / 1000:
            self.syntax_highlighting_uygula()

    def syntax_highlighting_uygula(self):
        """Kod renklendirilmesini uygular"""
        try:
            # Editordeki metni al
            metin = self.metin_editor.get('1.0', tk.END)

            # Onceki renklendirmeleri temizle
            for tag in self.metin_editor.tag_names():
                if tag not in ('sel', 'current'):
                    self.metin_editor.tag_delete(tag)

            # Kodu tokenize et
            tokenlar = self.lexer.tokenize(metin)

            # Token istatistiklerini guncelle
            self.lexer_bilgisini_guncelle(tokenlar)

            # Sozdizimi analizi yap
            self.parser = TurkScriptParser(tokenlar)
            parse_basarili = self.parser.parse()

            # Hatalari kullaniciya goster
            self.hatalari_goster()

            # Toplam hata sayisini hesapla
            parser_hatalari = self.parser.get_hatalar() if self.parser else []
            lexer_hatalari = self.lexer.get_hatalar()
            toplam_hata = len(parser_hatalari) + len(lexer_hatalari)

            # Gecerli token sayisini hesapla
            toplam_token = len([t for t in tokenlar if t.tur not in [TokenTuru.EOF, TokenTuru.BOSLUK]])

            # Her token icin renk uygula
            for token in tokenlar:
                if token.tur in [TokenTuru.EOF, TokenTuru.BOSLUK]:
                    continue

                # Token konumunu editorde bul
                baslangic_pos = self.pozisyon_hesapla(metin, token.baslangic)
                bitis_pos = self.pozisyon_hesapla(metin, token.bitis)

                # Uygun rengi uygula
                if token.tur in RENK_HARITASI:
                    tag_name = f"{token.tur}_{token.baslangic}"
                    self.metin_editor.tag_add(tag_name, baslangic_pos, bitis_pos)
                    self.metin_editor.tag_config(tag_name,
                                               foreground=RENK_HARITASI[token.tur])

                    # Anahtar kelimeler kalin yazi
                    if token.tur == TokenTuru.ANAHTAR_KELIME:
                        self.metin_editor.tag_config(tag_name,
                                                   font=('Consolas', 12, 'bold'))

            # Durum mesajini guncelle
            if toplam_token == 0:
                self.status_label.config(text="📝 Boş doküman", fg='gray')
            elif toplam_hata == 0:
                self.status_label.config(
                    text=f"✓ Analiz tamamlandı - {toplam_token} token, hata yok",
                    fg='green'
                )
            else:
                self.status_label.config(
                    text=f"⚠ {toplam_hata} hata bulundu - {toplam_token} token analiz edildi",
                    fg='red'
                )

        except Exception as e:
            self.status_label.config(text=f"❌ Kritik hata: {str(e)}", fg='red')

    def pozisyon_hesapla(self, metin, char_pozisyon):
        """Karakter pozisyonunu editor pozisyonuna donustur"""
        if char_pozisyon >= len(metin):
            return tk.END

        satir = 1
        sutun = 0

        # Karakter karakter ilerlе ve konum hesapla
        for i, char in enumerate(metin[:char_pozisyon]):
            if char == '\n':
                satir += 1
                sutun = 0
            else:
                sutun += 1

        return f"{satir}.{sutun}"

    def lexer_bilgisini_guncelle(self, tokenlar):
        """Token analiz sonuclarini goster"""
        self.lexer_text.config(state=tk.NORMAL)
        self.lexer_text.delete('1.0', tk.END)

        # Her token turunden kac tane var say
        token_sayilari = {}
        for token in tokenlar:
            if token.tur != TokenTuru.EOF:
                token_sayilari[token.tur] = token_sayilari.get(token.tur, 0) + 1

        bilgi = "Token İstatistikleri:\n"
        bilgi += "=" * 20 + "\n"

        # Token istatistiklerini listele
        for tur, sayi in sorted(token_sayilari.items()):
            bilgi += f"{tur}: {sayi}\n"

        bilgi += f"\nToplam: {sum(token_sayilari.values())}\n"

        # Lexer hatalarini da goster
        lexer_hatalari = self.lexer.get_hatalar()
        if lexer_hatalari:
            bilgi += "\nLexer Hataları:\n"
            bilgi += "=" * 15 + "\n"
            for hata in lexer_hatalari:
                bilgi += f"• {hata}\n"

        self.lexer_text.insert(tk.END, bilgi)
        self.lexer_text.config(state=tk.DISABLED)

    def hatalari_goster(self):
        """Bulunan hatalari kullaniciya goster"""
        self.hata_text.config(state=tk.NORMAL)
        self.hata_text.delete('1.0', tk.END)

        toplam_hata = 0

        # Parser hatalarini goster
        if self.parser:
            parser_hatalari = self.parser.get_hatalar()

            if parser_hatalari:
                self.hata_text.insert(tk.END, "Sözdizimi Hataları:\n")
                self.hata_text.insert(tk.END, "=" * 20 + "\n")

                for hata in parser_hatalari:
                    hata_text = f"Satır {hata['satir']}: {hata['mesaj']}\n\n"
                    self.hata_text.insert(tk.END, hata_text)
                    toplam_hata += 1

        # Lexer hatalarini goster
        lexer_hatalari = self.lexer.get_hatalar()
        if lexer_hatalari:
            if toplam_hata > 0:
                self.hata_text.insert(tk.END, "\n")

            self.hata_text.insert(tk.END, "Lexer Hataları:\n")
            self.hata_text.insert(tk.END, "=" * 15 + "\n")

            for hata in lexer_hatalari:
                self.hata_text.insert(tk.END, f"• {hata}\n")
                toplam_hata += 1

        # Hata yoksa basarili mesaji
        if toplam_hata == 0:
            self.hata_text.insert(tk.END, "✓ Hata bulunamadı!\n\n")
            self.hata_text.insert(tk.END, "Kod başarıyla analiz edildi.")

        self.hata_text.config(state=tk.DISABLED)

    def run(self):
        """Uygulamayi baslat"""
        self.root.mainloop()