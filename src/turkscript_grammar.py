"""
TurkScript dilinin grammarini ve anahtar kelimelerini tanımlayan modul
"""

# TurkScript dilinin tum anahtar kelimeleri
ANAHTAR_KELIMELER = {
    # Temel veri tipleri
    'sayi', 'metin', 'mantik', 'liste',

    # Kosullu kontrol yapilari
    'eger', 'yoksa', 'yoksa_eger', 'dongu', 'icin', 'iken', 'dur', 'devam',

    # Fonksiyon tanimlama ve cagrisi
    'fonksiyon', 'don', 'cagir',

    # Degisken ve sabit tanimlama
    'degisken', 'sabit',

    # Mantiksal islem operatorleri
    've', 'veya', 'degil',

    # Ozel degerler ve atamalar
    'esit', 'dogru', 'yanlis', 'bos',

    # Temel girdi cikti islemleri
    'yazdir', 'oku',
}

# Matematiksel ve mantiksal operatorler
OPERATORLER = {
    '+', '-', '*', '/', '%',        # Aritmetik operatorler
    '==', '!=', '<', '>', '<=', '>=',  # Karsilastirma operatorleri
    '=',                            # Atama operatoru
    '&&', '||', '!',               # Mantiksal operatorler
}

# Kod yapisini belirleyen ayirici karakterler
AYIRICILAR = {
    '(', ')', '{', '}', '[', ']',  # Parantezler ve suslu parantezler
    ';', ',', '.',                 # Noktalama isaretleri
    ':',                           # Iki nokta
}

# Token turlerini tanimlayan sinif
class TokenTuru:
    ANAHTAR_KELIME = "ANAHTAR_KELIME"
    TANIMLAYICI = "TANIMLAYICI"
    SAYI = "SAYI"
    METIN = "METIN"
    OPERATOR = "OPERATOR"
    AYIRICI = "AYIRICI"
    YORUM = "YORUM"
    BOSLUK = "BOSLUK"
    HATA = "HATA"
    EOF = "EOF"

# Syntax highlighting icin renk haritasi
RENK_HARITASI = {
    TokenTuru.ANAHTAR_KELIME: '#0000FF',  # Anahtar kelimeler mavi
    TokenTuru.TANIMLAYICI: '#000000',     # Degisken adlari siyah
    TokenTuru.SAYI: '#FF6600',            # Sayilar turuncu
    TokenTuru.METIN: '#008000',           # String literaller yesil
    TokenTuru.OPERATOR: '#800080',        # Operatorler mor
    TokenTuru.AYIRICI: '#000000',         # Ayiricilar siyah
    TokenTuru.YORUM: '#808080',           # Yorumlar gri
    TokenTuru.HATA: '#FF0000',            # Hatalar kirmizi
}

# Editorde gosterilecek ornek TurkScript kodu
ORNEK_KOD = """// TurkScript Ornegi
degisken sayi x = 10;
degisken metin isim = "Edem";

eger (x > 5) {
    yazdir("x buyuk bir sayi");
} yoksa {
    yazdir("x kucuk bir sayi");
}

fonksiyon topla(a, b) {
    don a + b;
}

degisken sonuc = cagir topla(5, 3);
yazdir(sonuc);
"""