"""
TurkScript Lexical Analyzer (Leksik Analizci)
Kaynak kodu tokenlara ayiran modul
"""

import re
from turkscript_grammar import ANAHTAR_KELIMELER, OPERATORLER, AYIRICILAR, TokenTuru

class Token:
    """Her kod parcasini temsil eden token sinifi"""
    def __init__(self, tur, deger, satir, sutun, baslangic=0, bitis=0):
        self.tur = tur
        self.deger = deger
        self.satir = satir
        self.sutun = sutun
        self.baslangic = baslangic
        self.bitis = bitis

    def __str__(self):
        return f"Token({self.tur}, '{self.deger}', {self.satir}:{self.sutun})"

class TurkScriptLexer:
    """TurkScript dilini analiz eden lexer sinifi"""

    def __init__(self, kaynak_kod=""):
        self.kaynak_kod = kaynak_kod
        self.pozisyon = 0
        self.satir = 1
        self.sutun = 1
        self.uzunluk = len(kaynak_kod)
        self.tokenlar = []
        self.hatalar = []

    def mevcut_karakter(self):
        """Su anki pozisyondaki karakteri getir"""
        if self.pozisyon >= self.uzunluk:
            return '\0'
        return self.kaynak_kod[self.pozisyon]

    def sonraki_karakter(self):
        """Bir sonraki karakteri goster"""
        if self.pozisyon + 1 >= self.uzunluk:
            return '\0'
        return self.kaynak_kod[self.pozisyon + 1]

    def ileri_git(self):
        """Okuma pozisyonunu bir adim ileri tasir"""
        if self.pozisyon < self.uzunluk:
            if self.mevcut_karakter() == '\n':
                self.satir += 1
                self.sutun = 1
            else:
                self.sutun += 1
            self.pozisyon += 1

    def bosluk_atla(self):
        """Gereksiz bosluk karakterlerini atlar"""
        while self.mevcut_karakter() in ' \t\r':
            self.ileri_git()

    def sayi_oku(self):
        """Tam sayi veya ondalik sayi okur"""
        baslangic_pozisyon = self.pozisyon
        baslangic_sutun = self.sutun
        sayi_str = ""

        # Tam kisim icin rakam oku
        while self.mevcut_karakter().isdigit():
            sayi_str += self.mevcut_karakter()
            self.ileri_git()

        # Ondalik kisim varsa onu da oku
        if self.mevcut_karakter() == '.' and self.sonraki_karakter().isdigit():
            sayi_str += self.mevcut_karakter()
            self.ileri_git()
            while self.mevcut_karakter().isdigit():
                sayi_str += self.mevcut_karakter()
                self.ileri_git()

        return Token(TokenTuru.SAYI, sayi_str, self.satir, baslangic_sutun,
                    baslangic_pozisyon, self.pozisyon)

    def metin_oku(self):
        """Tirnak icindeki string metni okur"""
        baslangic_pozisyon = self.pozisyon
        baslangic_sutun = self.sutun
        quote_char = self.mevcut_karakter()
        metin_str = quote_char
        self.ileri_git()

        # Kapanıs tirnagina kadar oku
        while self.mevcut_karakter() != '\0' and self.mevcut_karakter() != quote_char:
            if self.mevcut_karakter() == '\\':
                # Kacis karakterleri icin
                metin_str += self.mevcut_karakter()
                self.ileri_git()
                if self.mevcut_karakter() != '\0':
                    metin_str += self.mevcut_karakter()
                    self.ileri_git()
            else:
                metin_str += self.mevcut_karakter()
                self.ileri_git()

        if self.mevcut_karakter() == quote_char:
            metin_str += self.mevcut_karakter()
            self.ileri_git()
            return Token(TokenTuru.METIN, metin_str, self.satir, baslangic_sutun,
                        baslangic_pozisyon, self.pozisyon)
        else:
            # Kapanmamis string hatasi
            self.hatalar.append(f"Kapatilmamis string: {self.satir}:{baslangic_sutun}")
            return Token(TokenTuru.HATA, metin_str, self.satir, baslangic_sutun,
                        baslangic_pozisyon, self.pozisyon)

    def tanimlayici_oku(self):
        """Degisken adi veya anahtar kelime okur"""
        baslangic_pozisyon = self.pozisyon
        baslangic_sutun = self.sutun
        kelime = ""

        # Ilk karakter harf veya alt cizgi olmali
        if self.mevcut_karakter().isalpha() or self.mevcut_karakter() == '_':
            kelime += self.mevcut_karakter()
            self.ileri_git()

        # Devam eden karakterler harf, rakam veya alt cizgi
        while (self.mevcut_karakter().isalnum() or self.mevcut_karakter() == '_'):
            kelime += self.mevcut_karakter()
            self.ileri_git()

        # Anahtar kelime mi yoksa tanimlayici mi?
        if kelime in ANAHTAR_KELIMELER:
            token_turu = TokenTuru.ANAHTAR_KELIME
        else:
            token_turu = TokenTuru.TANIMLAYICI

        return Token(token_turu, kelime, self.satir, baslangic_sutun,
                    baslangic_pozisyon, self.pozisyon)

    def yorum_oku(self):
        """Cift slash ile baslayan yorum satirini okur"""
        baslangic_pozisyon = self.pozisyon
        baslangic_sutun = self.sutun
        yorum = ""

        if self.mevcut_karakter() == '/' and self.sonraki_karakter() == '/':
            # Satir sonuna kadar tum yorumu oku
            while self.mevcut_karakter() != '\0' and self.mevcut_karakter() != '\n':
                yorum += self.mevcut_karakter()
                self.ileri_git()

            return Token(TokenTuru.YORUM, yorum, self.satir, baslangic_sutun,
                        baslangic_pozisyon, self.pozisyon)

        return None

    def operator_oku(self):
        """Matematiksel ve mantiksal operatorleri okur"""
        baslangic_pozisyon = self.pozisyon
        baslangic_sutun = self.sutun

        # Once iki karakterli operatorleri kontrol et
        iki_karakter = self.mevcut_karakter() + self.sonraki_karakter()
        if iki_karakter in OPERATORLER:
            self.ileri_git()
            self.ileri_git()
            return Token(TokenTuru.OPERATOR, iki_karakter, self.satir, baslangic_sutun,
                        baslangic_pozisyon, self.pozisyon)

        # Tek karakterli operatorleri kontrol et
        tek_karakter = self.mevcut_karakter()
        if tek_karakter in OPERATORLER:
            self.ileri_git()
            return Token(TokenTuru.OPERATOR, tek_karakter, self.satir, baslangic_sutun,
                        baslangic_pozisyon, self.pozisyon)

        return None

    def sonraki_token(self):
        """Kaynak koddan bir sonraki tokeni al"""
        self.bosluk_atla()

        # Dosya sonu kontrolu
        if self.pozisyon >= self.uzunluk:
            return Token(TokenTuru.EOF, "", self.satir, self.sutun,
                        self.pozisyon, self.pozisyon)

        karakter = self.mevcut_karakter()

        # Yeni satir karakteri
        if karakter == '\n':
            token = Token(TokenTuru.BOSLUK, karakter, self.satir, self.sutun,
                         self.pozisyon, self.pozisyon + 1)
            self.ileri_git()
            return token

        # Sayi literal kontrolu
        if karakter.isdigit():
            return self.sayi_oku()

        # String literal kontrolu
        if karakter in '"\'':
            return self.metin_oku()

        # Yorum satiri kontrolu
        if karakter == '/' and self.sonraki_karakter() == '/':
            return self.yorum_oku()

        # Tanimlayici veya anahtar kelime kontrolu
        if karakter.isalpha() or karakter == '_':
            return self.tanimlayici_oku()

        # Operator kontrolu
        operator_token = self.operator_oku()
        if operator_token:
            return operator_token

        # Ayirici karakter kontrolu
        if karakter in AYIRICILAR:
            token = Token(TokenTuru.AYIRICI, karakter, self.satir, self.sutun,
                         self.pozisyon, self.pozisyon + 1)
            self.ileri_git()
            return token

        # Bilinmeyen karakter - hata durumu
        hata_token = Token(TokenTuru.HATA, karakter, self.satir, self.sutun,
                          self.pozisyon, self.pozisyon + 1)
        self.hatalar.append(f"Bilinmeyen karakter '{karakter}': {self.satir}:{self.sutun}")
        self.ileri_git()
        return hata_token

    def tokenize(self, kaynak_kod=None):
        """Tum kaynak kodu tokenlara ayir"""
        if kaynak_kod is not None:
            self.kaynak_kod = kaynak_kod
            self.pozisyon = 0
            self.satir = 1
            self.sutun = 1
            self.uzunluk = len(kaynak_kod)

        # Onceki sonuclari temizle
        self.tokenlar = []
        self.hatalar = []

        # Tum tokenleri sira ile al
        while True:
            token = self.sonraki_token()
            self.tokenlar.append(token)

            if token.tur == TokenTuru.EOF:
                break

        return self.tokenlar

    def get_hatalar(self):
        """Analiz sirasinda bulunan hatalari dondur"""
        return self.hatalar