# -*- coding: utf-8 -*-
"""
BUP-ALL-IN-ONE PyInstaller Runtime Hook
Bu dosya EXE çalıştırıldığında ilk önce yürütülür.
Path, locale ve Tk sorunlarını düzeltir.
"""

import os
import sys
import locale

def _setup_paths():
    """EXE için path ayarları"""
    if getattr(sys, 'frozen', False):
        # PyInstaller frozen mode
        base_path = sys._MEIPASS
        app_dir = os.path.dirname(sys.executable)
        
        # MEIPASS'ı path'e ekle
        if base_path not in sys.path:
            sys.path.insert(0, base_path)
        
        # Alt dizinleri de ekle
        for subdir in ['shared', 'ISKONTO_HESABI', 'KARLILIK_ANALIZI', 
                       'Musteri_Sayisi_Kontrolu', 'YASLANDIRMA']:
            subpath = os.path.join(base_path, subdir)
            if os.path.isdir(subpath) and subpath not in sys.path:
                sys.path.insert(0, subpath)
        
        # Çalışma dizinini ayarla
        os.chdir(app_dir)
        
        # data, logs, exports dizinlerini oluştur
        for dirname in ['data', 'logs', 'exports', 'data/backups', 
                        'exports/excel', 'exports/pdf']:
            dirpath = os.path.join(app_dir, dirname)
            os.makedirs(dirpath, exist_ok=True)

def _setup_locale():
    """Locale ayarları - Tk float sorunu için kritik"""
    try:
        # NUMERIC locale'i C yaparak float->string dönüşüm sorunlarını çöz
        locale.setlocale(locale.LC_NUMERIC, 'C')
    except:
        pass
    
    try:
        # Diğer locale ayarları
        if sys.platform == 'win32':
            try:
                locale.setlocale(locale.LC_ALL, 'Turkish_Turkey.1254')
            except:
                try:
                    locale.setlocale(locale.LC_ALL, '')
                except:
                    pass
    except:
        pass

def _setup_environment():
    """Ortam değişkenleri"""
    # Tk için gerekli olabilecek ayarlar
    if sys.platform == 'win32':
        # DPI awareness
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

# Hook çalıştır
_setup_paths()
_setup_locale()
_setup_environment()
