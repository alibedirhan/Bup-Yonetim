# Değişiklik Günlüğü (CHANGELOG)

Bu proje [Semantic Versioning](https://semver.org/) kullanmaktadır.


## [3.3.2] - 2025-12-25 🖼️ PNG UI İKONLARI

### ✅ Düzeltmeler
- Header (Bupiliç) sol logo PNG olarak eklendi ve düzgün hizalandı
- Modül kart ikonları PNG oldu (İskonto, Karlılık, Müşteri Takip, Yaşlandırma)
- Kırpılma sorunu giderildi (sabit width/height + pack(expand=True))
- Linux & Windows görünümü tutarlı hale getirildi

## [3.3.0] - 2024-12-24 🎨 MAJOR TEMA GÜNCELLEMESİ

### ✨ YENİ: Profesyonel Tema Sistemi

HTML prototipinden türetilen mükemmel tema sistemi!

#### 🌞 Light Tema
```
bg_primary:     #f5f5f7   (açık gri arka plan)
bg_secondary:   #ffffff   (beyaz)
bg_card:        #ffffff   (kart arka planı)
text_primary:   #1d1d1f   (koyu metin)
text_secondary: #6e6e73   (ikincil metin)
border:         #d2d2d7   (border)
```

#### 🌙 Dark Tema (Claude Tarzı)
```
bg_primary:     #1a1a2e   (koyu lacivert)
bg_secondary:   #16213e   (daha koyu)
bg_card:        #252542   (kart arka planı)
text_primary:   #f5f5f7   (açık metin - OKUNABILIR!)
text_secondary: #a1a1aa   (ikincil metin)
border:         #3f3f5a   (border)
```

### 🎴 ModernModuleCard Yenilendi
- `update_theme(is_dark)` metodu eklendi
- Tüm metin renkleri dinamik güncelleniyor
- İkon arka planları tema uyumlu
- Hover efektleri tema uyumlu
- Accent bar tasarımı (üst renkli çizgi)

### 🦶 Footer Yenilendi
- Tüm label'lara referans eklendi
- Border ve hover renkleri tema uyumlu
- Butonlar HTML prototipindeki gibi

### 📝 Teknik Detaylar
- `LIGHT_COLORS` ve `DARK_COLORS` sözlükleri
- `module_cards` listesi ile tüm kartlara erişim
- `_update_main_ui_colors()` tüm bileşenleri günceller

## [3.2.9] - 2024-12-24

### 🎨 Dark Tema - Claude Tarzı Yeniden Tasarım

#### Yeni Renk Paleti (Claude Tarzı)
```python
DARK_COLORS = {
    'bg_primary': '#1a1a2e',      # Ana arka plan - koyu lacivert
    'bg_secondary': '#16213e',     # İkincil arka plan
    'bg_header': '#0f0f1a',        # Header - en koyu
    'bg_card': '#252540',          # Kart arka planı
    'text_primary': '#E8E8F0',     # Ana metin - açık gri (okunabilir!)
    'text_secondary': '#A0A0B8',   # İkincil metin
    'border': '#3d3d5c',           # Border
    'hover': '#2d2d44',            # Hover
}
```

#### Modüller ETKİLENMİYOR ✅
- `ctk.set_appearance_mode()` **KALDIRILDI** (tema değiştirmeden)
- Sadece ana ekran renkleri manuel değiştiriliyor
- Modüller açıldığında kendi temasını koruyor

#### Güncellenen Bileşenler
- Header arka planı
- Welcome bölümü başlık/alt başlık
- Footer arka planı ve metin
- Tema/Ayarlar butonları
- Ana pencere arka planı

### 📝 Teknik Detaylar
- UI bileşenlerine referanslar eklendi (`self.header_frame`, `self.welcome_title` vb.)
- `_update_main_ui_colors()` fonksiyonu tüm ana ekran renklerini günceller
- Dark/Light tema geçişi akıcı ve anlık

## [3.2.8] - 2024-12-24

### 🔧 KRİTİK DÜZELTMELER - Tema ve Ayarlar

#### Aydınlık/Karanlık Tema Sorunu ✅ ÇÖZÜLDÜ
- `ctk.set_appearance_mode()` çağrısı düzgün çalışıyor
- Ana pencere arka plan rengi manuel güncelleniyor (dark: #1a1a2e)
- Tema değişikliği anında uygulanıyor
- Logger ile tema değişiklikleri loglanıyor

#### Ayarlar Penceresi Donma Sorunu ✅ ÇÖZÜLDÜ
- **`grab_set()` KALDIRILDI** - Bu donmaya neden oluyordu!
- Bunun yerine `focus_force()` ve `lift()` kullanılıyor
- Pencere referansı `_settings_window` ile takip ediliyor
- Çoklu pencere açılması engellendi

#### Tavuk Animasyonu İyileştirmeleri
- Animasyon sırasında buton disabled yapılıyor
- Hata durumunda animasyon düzgün sonlanıyor
- 60ms frame süresi (daha akıcı)

### 📝 Teknik Detaylar
```python
# ESKİ (SORUNLU):
settings.grab_set()  # BU DONMAYA NEDEN OLUYORDU!

# YENİ (ÇÖZÜM):
settings.focus_force()
settings.lift()
# grab_set KULLANILMIYOR!
```

### 🎯 Test Edilmesi Gerekenler
1. Tavuk ikonuna tıkla → Animasyon + Tema değişmeli
2. Ayarlar → Tema seç → Hemen uygulanmalı
3. Ayarlar → Kapat → Program donmamalı
4. Dark modda arka plan koyu olmalı

## [3.2.7] - 2024-12-24

### 🎨 Ana Ekran Geliştirmeleri

#### Program İkonu
- Bupiliç logosu program ikonu olarak eklendi (`assets/bupilic.ico`)
- Windows EXE dosyasında gösterilecek
- Görev çubuğunda ve pencere başlığında görünecek

#### Aydınlık/Karanlık Tema
- **Tavuk animasyonu** eklendi! 🐔
- Tema değiştirirken 8 frame'lik animasyon: 🐔→🐓→🥚→🐣→🐤→🐥→🐔→🐓
- Gündüz modu: 🐔 (tavuk)
- Gece modu: 🌜 (ay)

#### Ayarlar Penceresi Donma Sorunu
- `grab_release()` eklendi - kapanırken modal kilit düzgün kaldırılıyor
- `WM_DELETE_WINDOW` protokolü eklendi
- Kapat butonu `on_close` fonksiyonunu kullanıyor

### 📦 PyInstaller Güncellemeleri
- `--icon "assets/bupilic.ico"` eklendi
- PIL.Image ve PIL.ImageTk hidden imports eklendi

### 📁 Yeni Dosyalar
- `assets/bupilic.ico` - Windows program ikonu (16x16 - 256x256)
- `assets/bupilic.png` - PNG format ikon

## [3.2.6] - 2024-12-24

### 🔧 ISKONTO_HESABI UI Düzeltmeleri

#### İskonto Sekmesi Layout Sorunu
- Scrollable frame eklendi - tüm kategoriler artık görünür
- Kategori kartları daha kompakt hale getirildi
- Alt kısımda "Önizleme Oluştur" butonu eklendi

#### Progress Bar Sorunu
- Başlangıçta determinate modda başlatılıyor
- `reset()` metodu düzgün çalışıyor
- Indeterminate mod düzgün durduruluyor

#### Buton Okunabilirlik Sorunu
- **Tüm buton renkleri daha koyu** yapıldı (beyaz yazı net okunuyor):
  - Success (Yeşil): `#27AE60` → `#219A52`
  - Danger (Kırmızı): `#C0392B` → `#A93226`
  - Warning (Turuncu): `#E67E22` → `#D35400`
- Hızlı ayar butonlarına border eklendi
- Font weight: bold yapıldı

### 📦 shared/components.py Güncellemeleri
- `ModernButton`: Tüm renk tiplerinde beyaz yazı garantisi
- `ProgressIndicator`: 
  - `_is_indeterminate` flag eklendi
  - `mode="determinate"` açıkça belirtildi
  - Daha sağlam start/stop mantığı

## [3.2.5] - 2024-12-24

### 🔧 Kapsamlı İnceleme - Tüm Modüller

#### YASLANDIRMA/gui Klasörü (6 dosya düzeltildi):
- `__init__.py`: Tüm importlar 3 kademeli fallback'e geçirildi
- `analysis_operations.py`: `from utils import` → `from ..utils import`
- `analysis_tabs.py`: Aynı düzeltme
- `file_operations.py`: Aynı düzeltme
- `main_gui.py`: Tüm importlar (excel_processor, utils, gui modülleri, modules/)
- `tab_methods.py`: format_number_display ve format_turkish_number importları

#### Musteri_Sayisi_Kontrolu (2 dosya düzeltildi):
- `main.py`: `from ui import` → 3 kademeli fallback
- `ui_modern.py`: `from main import ExcelComparisonLogic` → 3 kademeli fallback

### 📦 Teknik Detaylar
- Toplam 8 dosyada import düzeltmesi yapıldı
- Tüm modüllerde frozen mode uyumluluğu sağlandı
- 3 kademeli import stratejisi:
  1. Relative import (`.module` veya `..module`)
  2. Package import (`PACKAGE.module`)
  3. Direct import (`module`)

## [3.2.4] - 2024-12-23

### 🔧 Kritik Düzeltmeler - TÜM MODÜL IMPORT HATALARI
- **YASLANDIRMA modules/**: Analiz modülü yüklenemedi hatası düzeltildi
  - `analysis.py`, `reports.py`, `visualization.py`, `analysis_gui.py`
  - `from utils import` → `from ..utils import` (relative import)
  - 3 kademeli fallback: relative → package → direct import
  
- **KARLILIK_ANALIZI**: Internal import hataları düzeltildi
  - `dashboard_components.py`, `veri_analizi.py`, `gui.py`, `ui_modern.py`
  - Tüm internal importlar frozen mode uyumlu hale getirildi

### 📦 Yeni Bağımlılıklar
- **seaborn>=0.12.0**: Visualization modülü için zorunlu

### 📦 PyInstaller Hidden Imports (Toplam: 180+)
- Tüm seaborn alt modülleri
- KARLILIK_ANALIZI: themes, ui_components, veri_analizi, gui, analiz_dashboard, zaman_analizi
- YASLANDIRMA: gui modülü
- Musteri_Sayisi_Kontrolu: kurulum modülü
- weakref, enum, subprocess modülleri
- collect-all: seaborn eklendi

### 🎯 İmport Stratejisi
Tüm modüllerde 3 kademeli import stratejisi:
```python
try:
    from .module import X  # Relative import (package olarak)
except ImportError:
    try:
        from PACKAGE.module import X  # Absolute import (frozen mode)
    except ImportError:
        from module import X  # Direct import (development)
```

## [3.2.3] - 2024-12-23

### 🔧 Kritik Düzeltmeler
- **logging.handlers**: `No module named 'logging.handlers'` hatası düzeltildi
- **PyInstaller Hidden Imports**: 130+ modül eklendi
  - logging, logging.handlers, logging.config
  - Tüm tkinter alt modülleri (_tkinter, simpledialog)
  - Tüm pandas._libs alt modülleri
  - Tüm pdfminer alt modülleri
  - Tüm openpyxl.styles alt modülleri
  - platform, traceback, tempfile, gc modülleri
- **collect-all**: pdfminer paketi de collect-all'a eklendi
- **collect-data**: fpdf paketi de collect-data'ya eklendi

### 📦 Teknik Değişiklikler
- Workflow'daki hidden-import sayısı 50'den 130+'a çıkarıldı
- Tüm standart kütüphane modülleri açıkça belirtildi

## [3.2.2] - 2024-12-23

### 🔧 Düzeltmeler
- **GitHub Actions**: Spec dosyası sorunu tamamen çözüldü
  - Workflow artık spec dosyasına ihtiyaç duymuyor
  - Tüm PyInstaller parametreleri komut satırında
- **Build Süreci**: Daha güvenilir build sistemi

### 📦 Teknik Değişiklikler
- `.github/workflows/build.yml` tamamen yeniden yazıldı
- Spec dosyası kaldırıldı (gitignore sorunu nedeniyle)
- Tüm hidden imports ve collect-all komutları workflow'a taşındı

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
