"""
TurkScript Parser (Sözdizimi Analizcisi)
Tokenlari parse eden ve syntax hatalarini bulan modul
"""

from lexer import Token, TokenTuru
from turkscript_grammar import ANAHTAR_KELIMELER

class ParseHatasi(Exception):
    """Sozdizimi hatasi icin ozel exception sinifi"""
    def __init__(self, mesaj, satir=0, sutun=0):
        self.mesaj = mesaj  # hata aciklamasi
        self.satir = satir  # hatanin oldugu satir
        self.sutun = sutun  # hatanin oldugu sutun
        super().__init__(self.mesaj)

class TurkScriptParser:
    """TurkScript icin yukaridan asagi parser sinifi"""

    def __init__(self, tokenlar):
        self.tokenlar = tokenlar  # lexer'dan gelen token dizisi
        self.mevcut_indeks = 0    # su anda islenen token indeksi
        self.hatalar = []         # bulunan syntax hatalari

    def mevcut_token(self):
        """Su anda islenen tokeni getir"""
        if self.mevcut_indeks >= len(self.tokenlar):
            return Token(TokenTuru.EOF, "", 0, 0)  # liste bittiyse EOF
        return self.tokenlar[self.mevcut_indeks]

    def sonraki_token(self):
        """Bir sonraki tokene ilerle"""
        if self.mevcut_indeks < len(self.tokenlar) - 1:
            self.mevcut_indeks += 1     # indeksi artir
        return self.mevcut_token()      # yeni pozisyondaki token

    def bekle(self, beklenen_tur, beklenen_deger=None):
        """Belirli bir token turunu veya degerini bekle"""
        token = self.mevcut_token()

        # Token turu dogru mu kontrol et
        if token.tur != beklenen_tur:
            hata_mesaji = f"Beklenen: {beklenen_tur}, Bulunan: {token.tur}"
            self.hatalar.append({
                'mesaj': hata_mesaji,
                'satir': token.satir,
                'sutun': token.sutun
            })
            raise ParseHatasi(hata_mesaji, token.satir, token.sutun)

        # Token degeri dogru mu kontrol et
        if beklenen_deger and token.deger != beklenen_deger:
            hata_mesaji = f"Beklenen değer: '{beklenen_deger}', Bulunan: '{token.deger}'"
            self.hatalar.append({
                'mesaj': hata_mesaji,
                'satir': token.satir,
                'sutun': token.sutun
            })
            raise ParseHatasi(hata_mesaji, token.satir, token.sutun)

        self.sonraki_token()  # dogru token, bir sonrakine gec
        return token

    def parse_program(self):
        """Tum programi bastan sona analiz et"""
        try:
            while self.mevcut_token().tur != TokenTuru.EOF:  # dosya bitene kadar
                if self.mevcut_token().tur == TokenTuru.BOSLUK:
                    self.sonraki_token()  # bosluk karakterlerini atla
                    continue

                if self.mevcut_token().tur == TokenTuru.YORUM:
                    self.sonraki_token()  # yorum satirlarini atla
                    continue

                self.parse_statement()  # her kod satirini analiz et

        except ParseHatasi as e:
            self.sonraki_token()  # hata varsa devam etmeye calis

    def parse_statement(self):
        """Tek bir kod satirini analiz et"""
        token = self.mevcut_token()

        if token.tur == TokenTuru.ANAHTAR_KELIME:
            if token.deger == 'degisken':
                self.parse_degisken_tanimla()  # degisken tanimlama
            elif token.deger == 'eger':
                self.parse_eger_statement()  # kosullu ifade
            elif token.deger == 'dongu' or token.deger == 'iken':
                self.parse_dongu_statement()  # dongu yapisi
            elif token.deger == 'fonksiyon':
                self.parse_fonksiyon_tanimla()  # fonksiyon tanimlama
            elif token.deger == 'yazdir':
                self.parse_yazdir_statement()  # ekrana yazma
            elif token.deger == 'don':
                self.parse_return_statement()  # fonksiyon donusu
            else:
                self.sonraki_token()  # tanimsiz anahtar kelime

        elif token.tur == TokenTuru.TANIMLAYICI:
            self.parse_assignment_or_call()  # atama veya cagrim

        else:
            # Beklenmeyen token tipi
            hata_mesaji = f"Beklenmeyen token: {token.deger}"
            self.hatalar.append({
                'mesaj': hata_mesaji,
                'satir': token.satir,
                'sutun': token.sutun
            })
            self.sonraki_token()

    def parse_degisken_tanimla(self):
        """Yeni degisken tanimlama analizini yap"""
        self.bekle(TokenTuru.ANAHTAR_KELIME, 'degisken')  # "degisken" sozcugu

        # Opsiyonel veri tipi belirtme
        if self.mevcut_token().deger in ['sayi', 'metin', 'mantik', 'liste']:
            self.bekle(TokenTuru.ANAHTAR_KELIME)  # tip belirtecini gec

        self.bekle(TokenTuru.TANIMLAYICI)    # degisken ismi
        self.bekle(TokenTuru.OPERATOR, '=')  # esittir isareti
        self.parse_ifade()                   # atanan deger
        self.bekle(TokenTuru.AYIRICI, ';')   # satir sonu

    def parse_eger_statement(self):
        """Kosullu ifade yapisini analiz et"""
        self.bekle(TokenTuru.ANAHTAR_KELIME, 'eger')  # "eger" sozcugu
        self.bekle(TokenTuru.AYIRICI, '(')
        self.parse_ifade()  # kosul ifadesi
        self.bekle(TokenTuru.AYIRICI, ')')
        self.bekle(TokenTuru.AYIRICI, '{')

        # if blogunun icerigini analiz et
        while (self.mevcut_token().tur != TokenTuru.AYIRICI or
               self.mevcut_token().deger != '}'):
            if self.mevcut_token().tur == TokenTuru.EOF:
                break  # dosya bittiyse cik
            if self.mevcut_token().tur == TokenTuru.BOSLUK:
                self.sonraki_token()  # bosluk atla
                continue
            self.parse_statement()  # blok icindeki satirlar

        self.bekle(TokenTuru.AYIRICI, '}')  # blok kapanisi

        # Else blogu var mi kontrol et
        if (self.mevcut_token().tur == TokenTuru.ANAHTAR_KELIME and
            self.mevcut_token().deger == 'yoksa'):
            self.sonraki_token()  # "yoksa" gec
            self.bekle(TokenTuru.AYIRICI, '{')

            while (self.mevcut_token().tur != TokenTuru.AYIRICI or
                   self.mevcut_token().deger != '}'):
                if self.mevcut_token().tur == TokenTuru.EOF:
                    break
                if self.mevcut_token().tur == TokenTuru.BOSLUK:
                    self.sonraki_token()
                    continue
                self.parse_statement()

            self.bekle(TokenTuru.AYIRICI, '}')

    def parse_dongu_statement(self):
        """Dongu yapisini analiz et"""
        self.bekle(TokenTuru.ANAHTAR_KELIME)  # "dongu" veya "iken"
        self.bekle(TokenTuru.AYIRICI, '(')
        self.parse_ifade()  # dongu kosulu
        self.bekle(TokenTuru.AYIRICI, ')')
        self.bekle(TokenTuru.AYIRICI, '{')

        # dongu icerigini analiz et
        while (self.mevcut_token().tur != TokenTuru.AYIRICI or
               self.mevcut_token().deger != '}'):
            if self.mevcut_token().tur == TokenTuru.EOF:
                break
            if self.mevcut_token().tur == TokenTuru.BOSLUK:
                self.sonraki_token()
                continue
            self.parse_statement()  # dongu icindeki kodlar

        self.bekle(TokenTuru.AYIRICI, '}')

    def parse_fonksiyon_tanimla(self):
        """Fonksiyon tanimlama yapisini analiz et"""
        self.bekle(TokenTuru.ANAHTAR_KELIME, 'fonksiyon')
        self.bekle(TokenTuru.TANIMLAYICI)  # fonksiyon ismi
        self.bekle(TokenTuru.AYIRICI, '(')

        # Parametre listesini analiz et
        while (self.mevcut_token().tur != TokenTuru.AYIRICI or
               self.mevcut_token().deger != ')'):
            if self.mevcut_token().tur == TokenTuru.TANIMLAYICI:
                self.sonraki_token()  # parametre ismi
                if (self.mevcut_token().tur == TokenTuru.AYIRICI and
                    self.mevcut_token().deger == ','):
                    self.sonraki_token()  # virgul varsa gec
            else:
                break

        self.bekle(TokenTuru.AYIRICI, ')')
        self.bekle(TokenTuru.AYIRICI, '{')

        # Fonksiyon govdesini analiz et
        while (self.mevcut_token().tur != TokenTuru.AYIRICI or
               self.mevcut_token().deger != '}'):
            if self.mevcut_token().tur == TokenTuru.EOF:
                break
            if self.mevcut_token().tur == TokenTuru.BOSLUK:
                self.sonraki_token()
                continue
            self.parse_statement()  # fonksiyon icindeki kodlar

        self.bekle(TokenTuru.AYIRICI, '}')

    def parse_yazdir_statement(self):
        """Yazdir komutunu analiz et"""
        self.bekle(TokenTuru.ANAHTAR_KELIME, 'yazdir')
        self.bekle(TokenTuru.AYIRICI, '(')
        self.parse_ifade()  # yazdirilacak ifade
        self.bekle(TokenTuru.AYIRICI, ')')
        self.bekle(TokenTuru.AYIRICI, ';')

    def parse_return_statement(self):
        """Fonksiyon donus komutunu analiz et"""
        self.bekle(TokenTuru.ANAHTAR_KELIME, 'don')
        self.parse_ifade()  # dondurulecek deger
        self.bekle(TokenTuru.AYIRICI, ';')

    def parse_assignment_or_call(self):
        """Atama veya fonksiyon cagrisi analiz et"""
        self.bekle(TokenTuru.TANIMLAYICI)  # degisken/fonksiyon ismi

        if (self.mevcut_token().tur == TokenTuru.OPERATOR and
            self.mevcut_token().deger == '='):
            # Bu bir degisken ataması
            self.bekle(TokenTuru.OPERATOR, '=')  # esittir
            self.parse_ifade()   # atanan deger
            self.bekle(TokenTuru.AYIRICI, ';')  # satir sonu
        elif (self.mevcut_token().tur == TokenTuru.AYIRICI and
              self.mevcut_token().deger == '('):
            # Bu bir fonksiyon cagrisi
            self.bekle(TokenTuru.AYIRICI, '(')

            while (self.mevcut_token().tur != TokenTuru.AYIRICI or
                   self.mevcut_token().deger != ')'):
                self.parse_ifade()  # parametre degeri
                if (self.mevcut_token().tur == TokenTuru.AYIRICI and
                    self.mevcut_token().deger == ','):
                    self.sonraki_token()  # virgul varsa gec
                else:
                    break

            self.bekle(TokenTuru.AYIRICI, ')')
            self.bekle(TokenTuru.AYIRICI, ';')

    def parse_ifade(self):
        """Genel ifade yapisini analiz et"""
        self.parse_mantiksal_ifade()

    def parse_mantiksal_ifade(self):
        """Mantiksal operatorlu ifadeleri analiz et"""
        self.parse_karsilastirma_ifade()

        while (self.mevcut_token().tur == TokenTuru.ANAHTAR_KELIME and
               self.mevcut_token().deger in ['ve', 'veya']):
            self.sonraki_token()
            self.parse_karsilastirma_ifade()

    def parse_karsilastirma_ifade(self):
        """Karsilastirma operatorlu ifadeleri analiz et"""
        self.parse_aritmetik_ifade()

        while (self.mevcut_token().tur == TokenTuru.OPERATOR and
               self.mevcut_token().deger in ['==', '!=', '<', '>', '<=', '>=']):
            self.sonraki_token()
            self.parse_aritmetik_ifade()

    def parse_aritmetik_ifade(self):
        """Toplama ve cikarma operatorlu ifadeleri analiz et"""
        self.parse_terim()

        while (self.mevcut_token().tur == TokenTuru.OPERATOR and
               self.mevcut_token().deger in ['+', '-']):
            self.sonraki_token()
            self.parse_terim()

    def parse_terim(self):
        """Carpma ve bolme operatorlu ifadeleri analiz et"""
        self.parse_faktor()

        while (self.mevcut_token().tur == TokenTuru.OPERATOR and
               self.mevcut_token().deger in ['*', '/', '%']):
            self.sonraki_token()
            self.parse_faktor()

    def parse_faktor(self):
        """Temel ifade elemanlarini analiz et"""
        token = self.mevcut_token()

        if token.tur == TokenTuru.SAYI:
            self.sonraki_token()
        elif token.tur == TokenTuru.METIN:
            self.sonraki_token()
        elif token.tur == TokenTuru.TANIMLAYICI:
            self.sonraki_token()
            # Fonksiyon cagrisi mi kontrol et
            if (self.mevcut_token().tur == TokenTuru.AYIRICI and
                    self.mevcut_token().deger == '('):
                self.bekle(TokenTuru.AYIRICI, '(')
                while (self.mevcut_token().tur != TokenTuru.AYIRICI or
                       self.mevcut_token().deger != ')'):
                    self.parse_ifade()
                    if (self.mevcut_token().tur == TokenTuru.AYIRICI and
                            self.mevcut_token().deger == ','):
                        self.sonraki_token()
                    else:
                        break
                self.bekle(TokenTuru.AYIRICI, ')')
        elif token.tur == TokenTuru.ANAHTAR_KELIME and token.deger in ['dogru', 'yanlis']:
            self.sonraki_token()
        # Fonksiyon cagri komutu icin ozel durum
        elif token.tur == TokenTuru.ANAHTAR_KELIME and token.deger == 'cagir':
            self.sonraki_token()  # 'cagir' gecildi
            self.bekle(TokenTuru.TANIMLAYICI)  # fonksiyon ismi
            self.bekle(TokenTuru.AYIRICI, '(')  # parantez acilisi
            # Parametre listesini isle
            while (self.mevcut_token().tur != TokenTuru.AYIRICI or
                   self.mevcut_token().deger != ')'):
                self.parse_ifade()
                if (self.mevcut_token().tur == TokenTuru.AYIRICI and
                        self.mevcut_token().deger == ','):
                    self.sonraki_token()
                else:
                    break
            self.bekle(TokenTuru.AYIRICI, ')')  # parantez kapanisi
        elif token.tur == TokenTuru.AYIRICI and token.deger == '(':
            # Parantezli ifade
            self.bekle(TokenTuru.AYIRICI, '(')
            self.parse_ifade()
            self.bekle(TokenTuru.AYIRICI, ')')
        else:
            hata_mesaji = f"Beklenmeyen token faktörde: {token.deger}"
            self.hatalar.append({
                'mesaj': hata_mesaji,
                'satir': token.satir,
                'sutun': token.sutun
            })

    def parse(self):
        """Ana parsing islemini baslat"""
        self.hatalar = []
        self.mevcut_indeks = 0

        try:
            self.parse_program()
        except Exception as e:
            self.hatalar.append({
                'mesaj': f"Parse hatası: {str(e)}",
                'satir': 0,
                'sutun': 0
            })

        return len(self.hatalar) == 0

    def get_hatalar(self):
        """Bulunan tum hatalari dondur"""
        return self.hatalar