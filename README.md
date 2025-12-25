# 🐔 Bupiliç Yönetim Sistemi v3.3.2

[![Build](https://github.com/alibedirhan/Bup-Yonetim/actions/workflows/build.yml/badge.svg)](https://github.com/alibedirhan/Bup-Yonetim/actions)
[![Release](https://img.shields.io/github/v/release/alibedirhan/Bup-Yonetim)](https://github.com/alibedirhan/Bup-Yonetim/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/alibedirhan/Bup-Yonetim/total)](https://github.com/alibedirhan/Bup-Yonetim/releases)

Tavukçuluk sektörü için modern işletme yönetim sistemi.


### v3.3.2 Notları
- UI içi PNG ikonlar (header + modül kartları)
- Layout stabilizasyonu (kırpma sorunu giderildi)

## 📥 İndirme

**[⬇️ Son Sürümü İndir](https://github.com/alibedirhan/Bup-Yonetim/releases/latest)**

## ✨ Özellikler

| Modül | Açıklama |
|-------|----------|
| 💰 İskonto Hesaplama | PDF fiyat listelerinden otomatik iskonto (maks. 3 PDF) |
| 📊 Karlılık Analizi | Şube ve ürün bazlı karlılık raporları + Dashboard |
| 👥 Müşteri Takip | Dönem bazlı müşteri karşılaştırma ve trend takibi |
| 📈 Yaşlandırma | Cari hesap yaşlandırma ve raporlama |

## 🖥️ Arayüz

> Görseli tıklayınca tam çözünürlükte açılır.

<p align="center">
  <a href="https://raw.githubusercontent.com/alibedirhan/Bup-Yonetim/main/docs/media/ui%402x.png">
    <img src="https://raw.githubusercontent.com/alibedirhan/Bup-Yonetim/main/docs/media/ui%402x.png" alt="BUP-YONETIM arayüz" width="900">
  </a>
</p>

## 🎬 Demo

> GIF önizlemedir. Tam kalite video için görsele tıklayın.

<p align="center">
  <a href="https://raw.githubusercontent.com/alibedirhan/Bup-Yonetim/main/docs/media/demo_1280.mp4">
    <img src="https://raw.githubusercontent.com/alibedirhan/Bup-Yonetim/main/docs/media/demo.gif" alt="BUP-YONETIM demo (GIF)" width="900">
  </a>
</p>

<p align="center">
  <a href="https://raw.githubusercontent.com/alibedirhan/Bup-Yonetim/main/docs/media/demo_1280.mp4"><b>▶ Tam kalite video (MP4)</b></a>
</p>


## 💻 Sistem Gereksinimleri

- Windows 10/11 (64-bit)
- 4 GB RAM
- 200 MB disk alanı
- **Ekstra kurulum gerekmez!**

## 🚀 Kurulum

1. Releases sayfasından ZIP dosyasını indirin
2. ZIP'i istediğiniz konuma çıkarın
3. `BUP_Yonetim.exe` dosyasını çalıştırın
4. İlk açılışta `data/`, `logs/`, `exports/` klasörleri otomatik oluşturulur

## 📁 Proje Yapısı

```
BUP_Yonetim/
├── BUP_Yonetim.exe          # Ana uygulama
├── data/                     # Uygulama verileri
│   └── backups/             # Yedekler
├── logs/                     # Log dosyaları
├── exports/                  # Dışa aktarılan dosyalar
│   ├── excel/               # Excel dosyaları
│   └── pdf/                 # PDF dosyaları
└── README.txt               # Kullanım kılavuzu
```

## 🛠️ Geliştirici Kurulumu

```bash
# Repoyu klonla
git clone https://github.com/alibedirhan/Bup-Yonetim.git
cd Bup-Yonetim

# Sanal ortam oluştur
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Bağımlılıkları yükle
pip install -r requirements.txt

# Çalıştır
python main.py

# EXE oluştur
pyinstaller BUP_Yonetim.spec --clean
```

## 📝 Değişiklik Günlüğü

Detaylar için [CHANGELOG.md](CHANGELOG.md) dosyasına bakın.

## 👨‍💻 Geliştirici

**Ali Bedirhan** 
- GitHub: [@alibedirhan](https://github.com/alibedirhan)
- YouTube: [@ali_bedirhan](https://youtube.com/@ali_bedirhan)

## 📄 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.
