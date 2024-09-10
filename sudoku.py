import pygame
import random
import numpy as np
import time
import json  # Oyun kaydetme/yükleme için


# Renkler
BEYAZ = (255, 255, 255)
SİYAH = (0, 0, 0)
MAVI = (0, 0, 255)
KIRMIZI = (255, 0, 0)
SARI = (255, 255, 0)  # Vurgulanmış hücre rengi
YESIL = (0, 255, 0)  # Doğru satır/sütun rengi


# Ekran Boyutu
GENIŞLIK = 500
YÜKSEKLIK = 600  # Düğmeler için yer açmak

# Hücre Boyutu
HÜCRE_BOYUTU = 50

# Oyun Durumu
OYUN_DEVAM_EDIYOR = True
OYUN_BITTI = False

# Seçili Hücre
seçili_satir = -1
seçili_sutun = -1

# Oyun İstatistikleri
çözülen_sudoku_sayisi = 0
ortalama_çözüm_süresi = 0
en_hızlı_çözüm_süresi = float('inf')

# Kaydedilen Oyun Verisi
kaydedilen_oyun = None

# Düğme Özellikleri
DÜGME_GENIŞLIK = 100
DÜGME_YÜKSEKLIK = 40
DÜGME_ARALIK = 10


def olustur_sudoku(zorluk):
    """
    Rastgele bir Sudoku ızgarası oluşturur.
    """
    grid = np.zeros((9, 9), dtype=int)

    # Sudoku ızgarasını doldurmak için algoritma
    def bul_bos(grid):
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    return (i, j)  # Boş bir hücrenin satır ve sütununu döndür
        return None  # Boş hücre yoksa None döndür

    def gecerli_mi(grid, sayi, pozisyon):
        # Satırda aynı sayı olup olmadığını kontrol et
        for i in range(9):
            if grid[pozisyon[0]][i] == sayi and pozisyon[1] != i:
                return False

        # Sütuna aynı sayı olup olmadığını kontrol et
        for i in range(9):
            if grid[i][pozisyon[1]] == sayi and pozisyon[0] != i:
                return False

        # 3x3'lük blokta aynı sayı olup olmadığını kontrol et
        bloklar_satir = pozisyon[0] // 3
        bloklar_sutun = pozisyon[1] // 3
        for i in range(bloklar_satir * 3, bloklar_satir * 3 + 3):
            for j in range(bloklar_sutun * 3, bloklar_sutun * 3 + 3):
                if grid[i][j] == sayi and (i, j) != pozisyon:
                    return False
        return True

    def coz_sudoku(grid):
        bosluk = bul_bos(grid)
        if not bosluk:
            return True  # Sudoku çözüldü
        satir, sutun = bosluk

        for sayi in range(1, 10):
            if gecerli_mi(grid, sayi, (satir, sutun)):
                grid[satir][sutun] = sayi

                if coz_sudoku(grid):
                    return True

                grid[satir][sutun] = 0  # Backtracking
        return False

    coz_sudoku(grid)  # Sudoku ızgarasını çöz

    # Belirli bir zorluk seviyesine göre bazı hücreleri boşalt
    bosluk_sayisi = int(zorluk * 81)
    bos_pozisyonlar = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(bos_pozisyonlar)
    for _ in range(bosluk_sayisi):
        satir, sutun = bos_pozisyonlar.pop()
        grid[satir, sutun] = 0

    return grid

def yazdir_sudoku(grid):
    """
    Sudoku ızgarasını ekrana yazdırır.
    """
    for i in range(9):
        for j in range(9):
            print(grid[i, j], end=" ")
        print()


def ciz_sudoku_izgarasi(ekran, grid):
    """
    Sudoku ızgarasını ekrana çizer.
    """
    for i in range(9):
        for j in range(9):
            if grid[i][j] != 0:
                sayi = font.render(str(grid[i][j]), True, SİYAH)
                ekran.blit(sayi, (j * HÜCRE_BOYUTU + 20, i * HÜCRE_BOYUTU + 20))

            # Seçili hücreyi vurgula
            if i == seçili_satir and j == seçili_sutun:
                pygame.draw.rect(ekran, SARI, (j * HÜCRE_BOYUTU, i * HÜCRE_BOYUTU, HÜCRE_BOYUTU, HÜCRE_BOYUTU), 3)  

            # Satır ve sütun doğrulama ve vurgulama (sadece dolu olanlar vurgulanacak)
            satir_dolu = True
            sutun_dolu = True
            for k in range(9):
                if grid[i][k] == 0:
                    satir_dolu = False
                if grid[k][j] == 0:
                    sutun_dolu = False
            
            if satir_dolu:
                satir_dogru = True
                sayilar = []
                for k in range(9):
                    if grid[i][k] not in sayilar:
                        sayilar.append(grid[i][k])
                    else:
                        satir_dogru = False
                if satir_dogru:
                    pygame.draw.rect(ekran, YESIL, (0, i * HÜCRE_BOYUTU, GENIŞLIK, HÜCRE_BOYUTU), 3)
                else:
                    pygame.draw.rect(ekran, KIRMIZI, (0, i * HÜCRE_BOYUTU, GENIŞLIK, HÜCRE_BOYUTU), 3)
            
            if sutun_dolu:
                sutun_dogru = True
                sayilar = []
                for k in range(9):
                    if grid[k][j] not in sayilar:
                        sayilar.append(grid[k][j])
                    else:
                        sutun_dogru = False
                if sutun_dogru:
                    pygame.draw.rect(ekran, YESIL, (j * HÜCRE_BOYUTU, 0, HÜCRE_BOYUTU, YÜKSEKLIK), 3)
                else:
                    pygame.draw.rect(ekran, KIRMIZI, (j * HÜCRE_BOYUTU, 0, HÜCRE_BOYUTU, YÜKSEKLIK), 3)


def olay_isle(ekran, grid):
    global OYUN_DEVAM_EDIYOR, seçili_satir, seçili_sutun, OYUN_BITTI, çözülen_sudoku_sayisi, ortalama_çözüm_süresi, en_hızlı_çözüm_süresi, başlangıç_zamani
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            OYUN_DEVAM_EDIYOR = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pozisyon = pygame.mouse.get_pos()
            satir = pozisyon[1] // HÜCRE_BOYUTU
            sutun = pozisyon[0] // HÜCRE_BOYUTU

            if 0 <= satir < 9 and 0 <= sutun < 9:
                seçili_satir = satir
                seçili_sutun = sutun
            
            # Düğme kontrolü
            if 500 <= pozisyon[1] <= 500 + DÜGME_YÜKSEKLIK:
                if 0 <= pozisyon[0] <= DÜGME_GENIŞLIK:
                    yeni_oyun(ekran) # grid parametresi kaldırıldı
                elif DÜGME_GENIŞLIK + DÜGME_ARALIK <= pozisyon[0] <= DÜGME_GENIŞLIK * 2 + DÜGME_ARALIK:
                    kaydet_oyun(grid)
                elif DÜGME_GENIŞLIK * 2 + DÜGME_ARALIK * 2 <= pozisyon[0] <= DÜGME_GENIŞLIK * 3 + DÜGME_ARALIK * 2:
                    yukle_oyun(ekran)
                elif DÜGME_GENIŞLIK * 3 + DÜGME_ARALIK * 3 <= pozisyon[0] <= DÜGME_GENIŞLIK * 4 + DÜGME_ARALIK * 3:
                    OYUN_DEVAM_EDIYOR = False

        elif event.type == pygame.KEYDOWN:
            if pygame.key.get_focused():  # Pencere odaklanmışsa
                if event.key == pygame.K_KP1:
                    if seçili_satir != -1 and seçili_sutun != -1:
                        grid[seçili_satir][seçili_sutun] = 1
                elif event.key == pygame.K_KP2:
                    if seçili_satir != -1 and seçili_sutun != -1:
                        grid[seçili_satir][seçili_sutun] = 2
                elif event.key == pygame.K_KP3:
                    if seçili_satir != -1 and seçili_sutun != -1:
                        grid[seçili_satir][seçili_sutun] = 3
                elif event.key == pygame.K_KP4:
                    if seçili_satir != -1 and seçili_sutun != -1:
                        grid[seçili_satir][seçili_sutun] = 4
                elif event.key == pygame.K_KP5:
                    if seçili_satir != -1 and seçili_sutun != -1:
                        grid[seçili_satir][seçili_sutun] = 5
                elif event.key == pygame.K_KP6:
                    if seçili_satir != -1 and seçili_sutun != -1:
                        grid[seçili_satir][seçili_sutun] = 6
                elif event.key == pygame.K_KP7:
                    if seçili_satir != -1 and seçili_sutun != -1:
                        grid[seçili_satir][seçili_sutun] = 7
                elif event.key == pygame.K_KP8:
                    if seçili_satir != -1 and seçili_sutun != -1:
                        grid[seçili_satir][seçili_sutun] = 8
                elif event.key == pygame.K_KP9:
                    if seçili_satir != -1 and seçili_sutun != -1:
                        grid[seçili_satir][seçili_sutun] = 9

    if not OYUN_BITTI:
        kontrol_et_sudoku(ekran, grid)
    

def kontrol_et_sudoku(ekran, grid):
    global OYUN_BITTI, çözülen_sudoku_sayisi, ortalama_çözüm_süresi, en_hızlı_çözüm_süresi, başlangıç_zamani
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return  # Sudoku tamamlanmadı

    # Sudoku tamamlandı, doğruluğunu kontrol et
    dogru_mu = True
    for i in range(9):
        satir_sayilar = set()
        sutun_sayilar = set()
        for j in range(9):
            if grid[i][j] in satir_sayilar or grid[j][i] in sutun_sayilar:
                dogru_mu = False
                break
            satir_sayilar.add(grid[i][j])
            sutun_sayilar.add(grid[j][i])
        if not dogru_mu:
            break

    if dogru_mu:
        OYUN_BITTI = True
        bitis_zamani = time.time()
        gecen_zaman = bitis_zamani - başlangıç_zamani
        çözülen_sudoku_sayisi += 1
        ortalama_çözüm_süresi = (ortalama_çözüm_süresi * (çözülen_sudoku_sayisi - 1) + gecen_zaman) / çözülen_sudoku_sayisi
        en_hızlı_çözüm_süresi = min(en_hızlı_çözüm_süresi, gecen_zaman)
        goster_sonuc(ekran)

def goster_sonuc(ekran):
    """
    Oyun bittiğinde sonuç ekranını gösterir.
    """
    font = pygame.font.SysFont(None, 48)
    sonuc_mesaji = font.render("Tebrikler! Sudoku'yu Çözdünüz!", True, YESIL)
    ekran.blit(sonuc_mesaji, (GENIŞLIK // 2 - 200, YÜKSEKLIK // 2 - 50))

    font = pygame.font.SysFont(None, 30)
    istatistikler_mesaji = font.render(f"Geçen Zaman: {round(time.time() - başlangıç_zamani, 2)} sn", True, SİYAH)
    ekran.blit(istatistikler_mesaji, (GENIŞLIK // 2 - 150, YÜKSEKLIK // 2 + 20))

    istatistikler_mesaji = font.render(f"Çözülen Sudoku Sayısı: {çözülen_sudoku_sayisi}", True, SİYAH)
    ekran.blit(istatistikler_mesaji, (GENIŞLIK // 2 - 150, YÜKSEKLIK // 2 + 50))

    istatistikler_mesaji = font.render(f"Ortalama Çözüm Süresi: {round(ortalama_çözüm_süresi, 2)} sn", True, SİYAH)
    ekran.blit(istatistikler_mesaji, (GENIŞLIK // 2 - 150, YÜKSEKLIK // 2 + 80))

    istatistikler_mesaji = font.render(f"En Hızlı Çözüm Süresi: {round(en_hızlı_çözüm_süresi, 2)} sn", True, SİYAH)
    ekran.blit(istatistikler_mesaji, (GENIŞLIK // 2 - 150, YÜKSEKLIK // 2 + 110))

    pygame.display.update()


def kaydet_oyun(grid):
    global kaydedilen_oyun
    kaydedilen_oyun = {
        "grid": grid.tolist()
    }
    with open("kaydedilen_oyun.json", "w") as dosya:
        json.dump(kaydedilen_oyun, dosya)

def yukle_oyun(ekran):
    global kaydedilen_oyun, grid
    try:
        with open("kaydedilen_oyun.json", "r") as dosya:
            kaydedilen_oyun = json.load(dosya)
            grid = np.array(kaydedilen_oyun["grid"])
    except FileNotFoundError:
        print("Kaydedilen oyun bulunamadı.")
    yeni_oyun(ekran, grid)

def yeni_oyun(ekran): # grid parametresi kaldırıldı
    global OYUN_BITTI, başlangıç_zamani, grid # grid eklendi
    OYUN_BITTI = False
    zorluk_seviyesi = 0.5  # Zorluk seviyesi ayarlanabilir
    grid = olustur_sudoku(zorluk_seviyesi)  # yeni grid oluşturuluyor
    başlangıç_zamani = time.time()

def ciz_dugmeler(ekran):
    """
    Düğmeleri ekrana çizer.
    """
    yeni_oyun_dugme = pygame.Rect(0, 500, DÜGME_GENIŞLIK, DÜGME_YÜKSEKLIK)
    kaydet_dugme = pygame.Rect(DÜGME_GENIŞLIK + DÜGME_ARALIK, 500, DÜGME_GENIŞLIK, DÜGME_YÜKSEKLIK)
    yukle_dugme = pygame.Rect(DÜGME_GENIŞLIK * 2 + DÜGME_ARALIK * 2, 500, DÜGME_GENIŞLIK, DÜGME_YÜKSEKLIK)
    cikis_dugme = pygame.Rect(DÜGME_GENIŞLIK * 3 + DÜGME_ARALIK * 3, 500, DÜGME_GENIŞLIK, DÜGME_YÜKSEKLIK)

    pygame.draw.rect(ekran, MAVI, yeni_oyun_dugme)
    pygame.draw.rect(ekran, MAVI, kaydet_dugme)
    pygame.draw.rect(ekran, MAVI, yukle_dugme)
    pygame.draw.rect(ekran, KIRMIZI, cikis_dugme)


    font = pygame.font.SysFont(None, 24)
    yeni_oyun_yazisi = font.render("Yeni Oyun", True, BEYAZ)
    ekran.blit(yeni_oyun_yazisi, (yeni_oyun_dugme.centerx - 40, yeni_oyun_dugme.centery - 10))

    kaydet_yazisi = font.render("Kaydet", True, BEYAZ)
    ekran.blit(kaydet_yazisi, (kaydet_dugme.centerx - 30, kaydet_dugme.centery - 10))

    yukle_yazisi = font.render("Yükle", True, BEYAZ)
    ekran.blit(yukle_yazisi, (yukle_dugme.centerx - 30, yukle_dugme.centery - 10))

    cikis_yazisi = font.render("Çıkış", True, BEYAZ)
    ekran.blit(cikis_yazisi, (cikis_dugme.centerx - 30, cikis_dugme.centery - 10))

def main():
    global font, başlangıç_zamani, grid
    pygame.init()
    ekran = pygame.display.set_mode((GENIŞLIK, YÜKSEKLIK))
    pygame.display.set_caption("Sudoku")
    font = pygame.font.SysFont(None, 30)

    zorluk_seviyesi = 0.5  # 0 ile 1 arasında bir değer (0 kolay, 1 zor)
    grid = olustur_sudoku(zorluk_seviyesi)
    başlangıç_zamani = time.time()  # Oyun başlangıç zamanını kaydet

    while OYUN_DEVAM_EDIYOR:
        ekran.fill(BEYAZ)
        ciz_sudoku_izgarasi(ekran, grid)
        ciz_dugmeler(ekran)
        olay_isle(ekran, grid)

        pygame.display.update()


if __name__ == "__main__":
    main()
    pygame.quit() 