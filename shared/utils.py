# -*- coding: utf-8 -*-
"""
BUP-ALL-IN-ONE Ortak Yardımcı Modül
Tüm alt programlarda kullanılan ortak fonksiyonlar
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import Optional
import locale
import tkinter as _tk
import re

# ============================================================================
# FROZEN MODE VE PATH YÖNETİMİ
# ============================================================================

def is_frozen() -> bool:
    """PyInstaller frozen modda mı kontrol et"""
    return getattr(sys, 'frozen', False)

def get_base_path() -> Path:
    """Uygulama base path'ini döndür"""
    if is_frozen():
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent

def get_app_dir() -> Path:
    """Uygulama dizinini döndür (exe yanı veya script dizini)"""
    if is_frozen():
        return Path(sys.executable).parent
    return Path(__file__).parent.parent

def get_data_dir() -> Path:
    """Veri dizinini döndür ve oluştur"""
    data_dir = get_app_dir() / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def get_logs_dir() -> Path:
    """Log dizinini döndür ve oluştur"""
    logs_dir = get_app_dir() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir

def get_exports_dir() -> Path:
    """Export dizinini döndür ve oluştur"""
    exports_dir = get_app_dir() / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    return exports_dir

def get_resource_path(relative_path: str) -> Path:
    """Resource dosyası için path döndür"""
    base_path = get_base_path()
    resource_path = base_path / relative_path
    
    if resource_path.exists():
        return resource_path
    
    # Alternatif konumlar
    alt_paths = [
        get_app_dir() / relative_path,
        Path(relative_path),
    ]
    
    for path in alt_paths:
        if path.exists():
            return path
    
    return resource_path  # Varsayılan döndür (olmasa bile)

# =========================================================================
# UYGULAMA / PENCERE İKONU
# =========================================================================

def apply_window_icon(
    window: _tk.Misc,
    *,
    prefer_chicken: bool = True,
    ico_rel: str = "assets/bupilic.ico",
    png_rel: str = "assets/tavuk.png",
    fallback_png_rel: str = "assets/bupilic.png",
) -> None:
    """Verilen Tk/CTk penceresine ikon uygula (Windows + Linux).

    - Windows'ta mümkünse PNG'den ICO üretip iconbitmap ile set eder (title bar/taskbar).
    - Tüm platformlarda iconphoto ile de set eder (özellikle Linux).

    Not: PhotoImage referansı GC ile silinmesin diye pencere üzerinde saklanır.
    """
    try:
        # Kaynakları bul
        png_path = get_resource_path(png_rel)
        if not png_path.exists():
            png_path = get_resource_path(fallback_png_rel)

        ico_path = get_resource_path(ico_rel)

        # 1) Windows: tavuk PNG varsa ICO üret (tavuk ikon istendiği için)
        if sys.platform.startswith("win"):
            try:
                if prefer_chicken and png_path.exists():
                    # Data dizinine cache'le (exe yanında yazılabilir alan)
                    out_ico = get_data_dir() / "app_icon_chicken.ico"
                    if (not out_ico.exists()) or (out_ico.stat().st_size < 1024):
                        from PIL import Image  # lazy
                        img = Image.open(png_path).convert("RGBA")
                        # Çoklu boyut üret
                        img.save(
                            out_ico,
                            format="ICO",
                            sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
                        )
                    window.iconbitmap(str(out_ico))
                elif ico_path.exists():
                    window.iconbitmap(str(ico_path))
            except Exception:
                # iconbitmap başarısız olursa devam
                pass

        # 2) iconphoto (Linux'ta kritik, Windows'ta da işe yarar)
        if png_path.exists():
            try:
                from PIL import Image, ImageTk  # lazy
                img = Image.open(png_path)
                photo = ImageTk.PhotoImage(img)
                window.iconphoto(True, photo)
                # Referansı tut
                setattr(window, "_bup_icon_photo", photo)
            except Exception:
                pass

    except Exception:
        # İkon ayarlaması hiçbir zaman uygulamayı düşürmemeli
        return

# ============================================================================
# LOGGING SİSTEMİ
# ============================================================================

def setup_logging(
    module_name: str,
    log_level: int = logging.INFO,
    max_bytes: int = 5 * 1024 * 1024,  # 5MB
    backup_count: int = 3
) -> logging.Logger:
    """
    Modül için logging sistemi kur.

    Args:
        module_name: Log dosyası için modül adı
        log_level: Minimum log seviyesi
        max_bytes: Maksimum log dosyası boyutu
        backup_count: Yedek dosya sayısı

    Returns:
        Logger instance
    """
    logger = logging.getLogger(module_name)

    # Seviyeyi her zaman ayarla
    logger.setLevel(log_level)

    # Root logger'a akmasın; aksi halde çift log görürsün
    logger.propagate = False

    # Daha önce handler eklendiyse tekrar ekleme
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Dosya handler
    log_file = get_logs_dir() / f"{module_name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# ============================================================================
# GLOBAL EXCEPTION HOOK (EXE'de sessiz crash olmasın)
# ============================================================================

def install_exception_hooks(logger: Optional[logging.Logger] = None) -> None:
    """Tüm yakalanmayan hataları crash.log dosyasına yaz ve (varsa) logger'a geçir.

    Not: Bu fonksiyon yalnızca hook kurar; logger handler/level kurmaz.
    Logging kurulumu setup_logging() ile yapılmalıdır.
    """
    import traceback

    crash_file = get_logs_dir() / "crash.log"

    # Logger yoksa en azından adlandırılmış bir logger kullan (handler eklemiyoruz).
    if logger is None:
        logger = logging.getLogger("BUP_CRASH")

    def _write(exc_type, exc, tb):
        try:
            text = "".join(traceback.format_exception(exc_type, exc, tb))
        except Exception:
            text = f"{exc_type}: {exc}"

        # crash.log'a yaz
        try:
            crash_file.parent.mkdir(parents=True, exist_ok=True)
            with crash_file.open("a", encoding="utf-8") as f:
                f.write("\n" + "=" * 80 + "\n")
                f.write(datetime.now().isoformat(sep=" ", timespec="seconds") + "\n")
                f.write(text + "\n")
        except Exception:
            pass

        # logger'a da düşür
        try:
            logger.error("Unhandled exception", exc_info=(exc_type, exc, tb))
        except Exception:
            pass

    # Orijinal hook'u sakla ki frozen değilken terminale traceback da basabilelim
    _orig_sys_hook = sys.excepthook

    def _sys_hook(exc_type, exc, tb):
        _write(exc_type, exc, tb)
        if not is_frozen() and callable(_orig_sys_hook):
            try:
                _orig_sys_hook(exc_type, exc, tb)
            except Exception:
                pass

    sys.excepthook = _sys_hook

    # Thread exceptions (Py3.8+)
    try:
        import threading
        _orig_thread_hook = getattr(threading, 'excepthook', None)

        def _thread_hook(args):
            _write(args.exc_type, args.exc_value, args.exc_traceback)
            if not is_frozen() and callable(_orig_thread_hook):
                try:
                    _orig_thread_hook(args)
                except Exception:
                    pass

        threading.excepthook = _thread_hook  # type: ignore[attr-defined]
    except Exception:
        pass

# ============================================================================
# LOCALE VE TÜRKÇE KARAKTER DESTEĞİ
# ============================================================================

def setup_turkish_locale():
    """Türkçe locale ayarlarını kur"""
    try:
        # Numeric için C locale (Tk için önemli)
        locale.setlocale(locale.LC_NUMERIC, 'C')
    except:
        pass
    
    try:
        # Diğerleri için Türkçe
        if sys.platform == 'win32':
            locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
        else:
            locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
    except:
        pass

def safe_turkish_text(text: str) -> str:
    """Türkçe karakterleri ASCII'ye çevir (PDF için)"""
    if not isinstance(text, str):
        return str(text)
    
    replacements = {
        'İ': 'I', 'ı': 'i', 'Ğ': 'G', 'ğ': 'g',
        'Ü': 'U', 'ü': 'u', 'Ş': 'S', 'ş': 's',
        'Ö': 'O', 'ö': 'o', 'Ç': 'C', 'ç': 'c'
    }
    
    for turkish, replacement in replacements.items():
        text = text.replace(turkish, replacement)
    
    return text

# ============================================================================
# TK FLOAT FIX (Locale sorunu için)
# ============================================================================

def apply_tk_float_fix():
    """
    Tk'ye giden 'screen distance' değerlerini otomatik olarak int'e dönüştürür
    "200.0" -> "200", 200.0 -> 200
    """
    # Orijinal metotları sakla
    _orig_options = _tk.Misc._options
    _orig_setup = _tk.BaseWidget._setup
    
    _DISTANCE_KEYS = {
        "padx", "pady", "ipadx", "ipady", "bd", "borderwidth",
        "highlightthickness", "width", "height", "wraplength",
        "insertwidth", "insertborderwidth"
    }
    
    def _sanitize_distance_value(v):
        try:
            if isinstance(v, float):
                return int(round(v))
            if isinstance(v, (list, tuple)):
                return type(v)(_sanitize_distance_value(x) for x in v)
            if isinstance(v, str):
                if re.match(r'^\d+\.0*$', v.strip()):
                    return str(int(float(v)))
                elif re.match(r'^\d*\.\d+$', v.strip()):
                    try:
                        return str(int(round(float(v))))
                    except ValueError:
                        pass
            return v
        except:
            return v
    
    def _sanitize_mapping(m):
        try:
            if isinstance(m, dict):
                return {k: _sanitize_distance_value(v) for k, v in m.items()}
        except:
            pass
        return m
    
    def _patched_options(self, cnf, kw=None):
        if kw:
            for k in list(kw.keys()):
                try:
                    if (k in _DISTANCE_KEYS) or isinstance(kw[k], (float, list, tuple)) \
                       or (isinstance(kw[k], str) and ('.' in str(kw[k]))):
                        kw[k] = _sanitize_distance_value(kw[k])
                except:
                    continue
        return _orig_options(self, cnf, kw)
    
    def _patched_setup(self, master, cnf):
        try:
            cnf = _sanitize_mapping(cnf)
        except:
            pass
        return _orig_setup(self, master, cnf)
    
    # Patch uygula
    _tk.Misc._options = _patched_options
    _tk.BaseWidget._setup = _patched_setup

# ============================================================================
# DOSYA İŞLEMLERİ
# ============================================================================

def get_clean_filename(filename: str, max_length: int = 50) -> str:
    """Dosya adından temiz bir isim oluştur"""
    # Uzantıyı kaldır
    base_name = Path(filename).stem
    
    # Özel karakterleri temizle
    clean_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_'))
    
    # Fazla boşlukları temizle
    clean_name = ' '.join(clean_name.split())
    
    # Uzunluk sınırla
    if len(clean_name) > max_length:
        clean_name = clean_name[:max_length]
    
    return clean_name if clean_name else "Dosya"

def format_file_size(size_bytes: int) -> str:
    """Dosya boyutunu okunabilir formata çevir"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def format_number(number: float, decimal_places: int = 2) -> str:
    """Sayıyı Türkçe formatta göster"""
    formatted = f"{number:,.{decimal_places}f}"
    # Türkçe format: 1.234,56
    formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
    return formatted

def format_currency(amount: float) -> str:
    """Para birimini Türkçe formatta göster"""
    return f"{format_number(amount)} ₺"

# ============================================================================
# TARİH İŞLEMLERİ
# ============================================================================

def get_timestamp() -> str:
    """Şu anki zamanı dosya adı için uygun formatta döndür"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_date_display() -> str:
    """Şu anki tarihi gösterim için döndür"""
    return datetime.now().strftime("%d.%m.%Y %H:%M")

def get_date_short() -> str:
    """Kısa tarih formatı"""
    return datetime.now().strftime("%d.%m.%Y")

# ============================================================================
# SİSTEM KONTROL
# ============================================================================

def check_dependencies(required_modules: list) -> tuple:
    """
    Gerekli modülleri kontrol et
    
    Returns:
        (bool, list): (Tümü mevcut mu, eksik modüller listesi)
    """
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    return len(missing) == 0, missing

def get_system_info() -> dict:
    """Sistem bilgilerini döndür"""
    import platform
    
    return {
        'os': platform.system(),
        'os_version': platform.version(),
        'python_version': sys.version,
        'platform': platform.platform(),
        'machine': platform.machine(),
        'frozen': is_frozen()
    }

# ============================================================================
# UYGULAMA BAŞLATMA
# ============================================================================

def initialize_app(module_name: str) -> logging.Logger:
    """
    Uygulama başlangıcında gerekli tüm ayarları yap
    
    Args:
        module_name: Modül adı
    
    Returns:
        Logger instance
    """
    # Tk float fix uygula
    apply_tk_float_fix()
    
    # Türkçe locale ayarla
    setup_turkish_locale()
    
    # Logging kur
    logger = setup_logging(module_name)
    
    # Global exception hook (crash.log)
    install_exception_hooks(logger)

    # Bilgilendirme
    logger.info("=" * 60)
    logger.info(f"{module_name} başlatılıyor...")
    logger.info(f"Frozen mod: {is_frozen()}")
    logger.info(f"Base path: {get_base_path()}")
    logger.info(f"App dir: {get_app_dir()}")
    logger.info("=" * 60)
    
    return logger

# Modül yüklendiğinde otomatik çalıştır
apply_tk_float_fix()
