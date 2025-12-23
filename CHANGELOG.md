# Değişiklik Günlüğü (CHANGELOG)

Bu proje [Semantic Versioning](https://semver.org/) kullanmaktadır.

## [3.2.1] - 2024-12-23

### 🔧 Düzeltmeler
- **Karlılık Analizi**: "Analiz modülü yüklenemedi" hatası düzeltildi
  - Import yolları düzeltildi (relative/absolute fallback)
  - `__init__.py` dosyasına modül export'ları eklendi
- **Yaşlandırma**: Dosya yükleme sonrası hata düzeltildi
  - Import yolları düzeltildi
  - Modül yükleme sırası düzenlendi
- **Müşteri Takip**: Araç-Plasiyer resim/excel kaydetme sorunu analiz edildi
- **PyInstaller**: Tüm proje modülleri hidden imports'a eklendi

### 📦 Teknik Değişiklikler
- `KARLILIK_ANALIZI/__init__.py`: KarlilikAnalizi export eklendi
- `YASLANDIRMA/__init__.py`: ExcelProcessor export eklendi
- `BUP_Yonetim.spec`: 30+ proje modülü hidden imports'a eklendi

## [3.2.0] - 2024-12-23

### 🔧 Düzeltmeler
- Windows EXE build sorunları tamamen çözüldü
- PyInstaller yapılandırması optimize edildi
- Runtime hook eklenerek path ve locale sorunları giderildi
- Tüm hidden imports eklendi

### 📦 Build İyileştirmeleri
- Yeni `BUP_Yonetim.spec` dosyası eklendi
- `runtime_hook.py` eklendi (EXE için path düzeltmeleri)
- GitHub Actions workflow güncellendi
- `fpdf2` kütüphanesi requirements'a eklendi
- `numpy` kütüphanesi requirements'a eklendi

### 📋 Teknik Detaylar
- CustomTkinter data files otomatik dahil ediliyor
- pdfplumber ve pdfminer bağımlılıkları tam olarak paketleniyor
- Matplotlib backends tam olarak dahil ediliyor
- Türkçe karakter desteği (cp1254) dahil ediliyor

## [3.1.2] - 2024-12-19

### 🐛 Düzeltmeler
- Tk float locale sorunu için geçici çözüm eklendi
- Exception hooks iyileştirildi

## [3.1.0] - 2024-12-18

### ✨ Yeni Özellikler
- Tüm modüller CustomTkinter'a dönüştürüldü
- Modern ana menü arayüzü
- Otomatik güncelleme kontrolü
- GitHub Actions ile otomatik build

### 📦 Modüller
- **İskonto Hesaplama**: PDF fiyat listesi işleme (maks. 3 PDF)
- **Karlılık Analizi**: Excel analiz ve dashboard
- **Müşteri Takip**: Dönem bazlı karşılaştırma
- **Yaşlandırma**: Cari hesap yaşlandırma

## [3.0.0] - 2024-12-15

### 🎉 İlk Major Release
- Proje baştan yapılandırıldı
- Modern UI tasarımı
- Shared modül mimarisi

---

## Geliştirici
**Ali Bedirhan**
- GitHub: [@alibedirhan](https://github.com/alibedirhan)
- YouTube: [@ali_bedirhan](https://youtube.com/@ali_bedirhan)
