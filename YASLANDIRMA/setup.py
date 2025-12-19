#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - Kurulum Scripti
Gerekli klasörleri oluşturur ve bağımlılıkları kontrol eder
"""

import os
import sys
from pathlib import Path
import subprocess

def create_directory_structure():
    """Gerekli klasör yapısını oluştur"""
    directories = [
        "modules",
        "data",
        "data/backups", 
        "logs",
        "exports",
        "charts"
    ]
    
    print("📁 Klasör yapısı oluşturuluyor...")
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {directory}/")
    
    print("📁 Klasör yapısı hazır!")

def create_init_files():
    """__init__.py dosyalarını oluştur"""
    init_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - Modules Package
"""

__version__ = "1.0.0"
'''
    
    modules_init = Path("modules/__init__.py")
    if not modules_init.exists():
        with open(modules_init, 'w', encoding='utf-8') as f:
            f.write(init_content)
        print("✅ modules/__init__.py oluşturuldu")

def check_python_version():
    """Python versiyonunu kontrol et"""
    print("🐍 Python versiyonu kontrol ediliyor...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 veya üzeri gereklidir!")
        print(f"   Mevcut versiyon: {sys.version}")
        return False
    
    print(f"✅ Python versiyonu uygun: {sys.version_info.major}.{sys.version_info.minor}")
    return True

def install_requirements():
    """Gerekli paketleri yükle"""
    print("📦 Gerekli paketler yükleniyor...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt dosyası bulunamadı!")
        return False
    
    try:
        # pip install çalıştır
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Tüm paketler başarıyla yüklendi!")
            return True
        else:
            print(f"❌ Paket yükleme hatası: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Paket yükleme hatası: {e}")
        return False

def check_module_files():
    """Modül dosyalarının varlığını kontrol et"""
    print("🔍 Modül dosyaları kontrol ediliyor...")
    
    required_files = [
        "main.py",
        "gui.py", 
        "excel_processor.py",
        "utils.py",
        "modules/analysis.py",
        "modules/assignment.py",
        "modules/data_manager.py",
        "modules/reports.py",
        "modules/visualization.py",
        "modules/analysis_gui.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print("\n❌ Eksik dosyalar:")
        for file_path in missing_files:
            print(f"  ❌ {file_path}")
        return False
    
    print("✅ Tüm modül dosyaları mevcut!")
    return True

def test_imports():
    """Import testleri yap"""
    print("🧪 Import testleri yapılıyor...")
    
    test_modules = [
        ("pandas", "Veri işleme"),
        ("customtkinter", "GUI framework"),
        ("matplotlib", "Görselleştirme"),
        ("numpy", "Sayısal hesaplamalar"),
        ("openpyxl", "Excel işlemleri")
    ]
    
    failed_imports = []
    
    for module_name, description in test_modules:
        try:
            __import__(module_name)
            print(f"  ✅ {module_name} - {description}")
        except ImportError:
            print(f"  ❌ {module_name} - {description}")
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"\n❌ Eksik paketler: {', '.join(failed_imports)}")
        print("Lütfen 'pip install -r requirements.txt' komutunu çalıştırın")
        return False
    
    print("✅ Tüm import testleri başarılı!")
    return True

def create_sample_config():
    """Örnek konfigürasyon dosyası oluştur"""
    config_content = '''{
    "ui_theme": "dark",
    "auto_save": true,
    "auto_save_interval": 300,
    "backup_enabled": true,
    "max_backup_count": 10,
    "analysis_cache_timeout": 300,
    "default_export_format": "xlsx",
    "notifications_enabled": true,
    "chart_dpi": 300
}'''
    
    config_file = Path("data/settings.json")
    if not config_file.exists():
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ Örnek ayar dosyası oluşturuldu: data/settings.json")

def main():
    """Ana kurulum fonksiyonu"""
    print("🚀 Excel İşleme Uygulaması Kurulum Scripti")
    print("=" * 50)
    
    # Python versiyon kontrolü
    if not check_python_version():
        sys.exit(1)
    
    # Klasör yapısı oluştur
    create_directory_structure()
    
    # __init__.py dosyaları oluştur
    create_init_files()
    
    # Modül dosyaları kontrol et
    if not check_module_files():
        print("\n❌ Kurulum başarısız! Eksik dosyalar var.")
        print("Lütfen tüm dosyaların doğru yerlerde olduğundan emin olun.")
        sys.exit(1)
    
    # Paketleri yükle
    if not install_requirements():
        print("\n⚠️  Paket yükleme başarısız, manuel yükleme gerekebilir.")
        print("Komut: pip install -r requirements.txt")
    
    # Import testleri
    if not test_imports():
        print("\n❌ Import testleri başarısız!")
        sys.exit(1)
    
    # Örnek config oluştur
    create_sample_config()
    
    print("\n" + "=" * 50)
    print("🎉 KURULUM TAMAMLANDI!")
    print("\n📋 Kullanım:")
    print("   python3 main.py")
    print("\n📁 Klasör yapısı:")
    print("   ├── modules/          # Analiz modülleri")
    print("   ├── data/             # Veri dosyaları")
    print("   ├── logs/             # Log dosyaları")
    print("   ├── exports/          # Export dosyaları")
    print("   └── charts/           # Grafik dosyaları")
    print("\n🚀 Uygulamayı başlatabilirsiniz!")

if __name__ == "__main__":
    main()
