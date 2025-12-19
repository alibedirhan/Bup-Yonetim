#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Excel Karşılaştırma Uygulaması - Otomatik Kurulum Scripti
Gerekli paketlerin kurulumunu otomatik olarak yapar.

Kullanım:
    python kurulum.py
"""

import subprocess
import sys
import os
import platform
import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional

# Constants
PYTHON_MIN_VERSION = (3, 7)
MAX_INSTALL_TIME = 120  # seconds
REQUIREMENTS_FILE = "requirements.txt"

# Gerekli paketler - optimized versions
REQUIRED_PACKAGES = [
    "pandas>=2.0.0,<3.0.0",
    "openpyxl>=3.0.9,<4.0.0", 
    "xlrd>=2.0.1,<3.0.0",
    "matplotlib>=3.5.0,<4.0.0"
]

OPTIONAL_PACKAGES = [
    "tkinterdnd2>=0.3.0"
]

class InstallationManager:
    """Kurulum yönetici sınıfı"""
    
    def __init__(self):
        self.failed_packages: List[str] = []
        self.installed_packages: List[str] = []
        self.python_executable = sys.executable
        
    def check_python_version(self) -> bool:
        """Python versiyonunu kontrol et"""
        python_version = sys.version_info[:2]
        
        if python_version < PYTHON_MIN_VERSION:
            print("HATA: Bu uygulama Python 3.7 veya daha yüksek bir versiyon gerektirir.")
            print(f"Şu anki Python versiyonu: {sys.version}")
            print("Lütfen Python'u güncelleyin: https://www.python.org/downloads/")
            return False
        
        print(f"✓ Python versiyonu uyumlu: {sys.version}")
        return True
    
    def create_requirements_file(self) -> bool:
        """requirements.txt dosyasını oluştur veya güncelle"""
        try:
            # Mevcut requirements.txt'i oku (varsa)
            existing_packages = set()
            req_path = Path(REQUIREMENTS_FILE)
            
            if req_path.exists():
                with open(req_path, "r", encoding="utf-8") as f:
                    existing_packages = {
                        line.strip() for line in f 
                        if line.strip() and not line.startswith('#')
                    }
            
            # Yeni paketleri ekle
            all_packages = list(existing_packages) + REQUIRED_PACKAGES
            
            # Duplicate'leri kaldır (paket adına göre)
            unique_packages = {}
            for package in all_packages:
                pkg_name = package.split('>=')[0].split('==')[0].split('<')[0].strip()
                unique_packages[pkg_name] = package
            
            # Dosyayı yaz
            with open(req_path, "w", encoding="utf-8") as f:
                f.write("# Excel Karşılaştırma Uygulaması - Gerekli Paketler\n")
                f.write("# Python 3.7+ gereklidir\n")
                f.write("# Pandas 2.x uyumluluğu için güncellenmiştir\n\n")
                
                f.write("# Ana bağımlılıklar\n")
                for package in sorted(unique_packages.values()):
                    f.write(f"{package}\n")
                
                f.write("\n# Opsiyonel - Drag & Drop desteği için\n")
                f.write("# tkinterdnd2 kurulumu başarısız olursa normal gözat butonları kullanılır\n")
            
            print(f"✓ '{REQUIREMENTS_FILE}' dosyası güncellendi.")
            return True
            
        except Exception as e:
            print(f"HATA: requirements.txt oluşturulurken hata: {e}")
            return False
    
    def upgrade_pip(self) -> bool:
        """pip'i güncelle"""
        try:
            print("\n📦 pip güncelleniyor...")
            result = subprocess.run(
                [self.python_executable, "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✓ pip güncellendi")
                return True
            else:
                print(f"⚠ pip güncellemesi başarısız: {result.stderr.strip()}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠ pip güncellemesi zaman aşımına uğradı")
            return False
        except Exception as e:
            print(f"⚠ pip güncellemesi sırasında hata: {e}")
            return False
    
    def install_package(self, package_name: str, optional: bool = False) -> bool:
        """Tek bir paketi kur"""
        try:
            print(f"  → {package_name} kuruluyor...")
            result = subprocess.run(
                [self.python_executable, "-m", "pip", "install", package_name, "--no-warn-script-location"],
                capture_output=True,
                text=True,
                timeout=MAX_INSTALL_TIME
            )
            
            if result.returncode == 0:
                print(f"  ✓ {package_name} başarıyla kuruldu")
                self.installed_packages.append(package_name)
                return True
            else:
                error_msg = result.stderr.strip()
                if optional:
                    print(f"  ⚠ {package_name} kurulamadı (opsiyonel): {error_msg}")
                    return True  # Opsiyonel paketler için başarılı say
                else:
                    print(f"  ✗ {package_name} kurulumu başarısız: {error_msg}")
                    self.failed_packages.append(package_name)
                    return False
                    
        except subprocess.TimeoutExpired:
            error_msg = f"{package_name} kurulumu zaman aşımına uğradı"
            print(f"  ✗ {error_msg}")
            if not optional:
                self.failed_packages.append(package_name)
            return optional
            
        except Exception as e:
            error_msg = f"{package_name} kurulumu sırasında hata: {e}"
            print(f"  ✗ {error_msg}")
            if not optional:
                self.failed_packages.append(package_name)
            return optional
    
    def check_pandas_version(self) -> bool:
        """Pandas versiyonunu kontrol et ve uyarı ver"""
        try:
            import pandas as pd
            version = pd.__version__
            major_version = int(version.split('.')[0])
            
            print(f"✓ Pandas versiyonu: {version}")
            
            if major_version >= 2:
                print("  ✓ Pandas 2.x - Modern API desteği mevcut")
                return True
            elif major_version == 1:
                print("  ⚠ Pandas 1.x - Bazı fonksiyonlar deprecated olabilir")
                print("  → Pandas 2.x'e güncellemeyi düşünün: pip install --upgrade pandas")
                return True
            else:
                print("  ⚠ Çok eski Pandas versiyonu, güncelleme gerekli")
                return False
                
        except ImportError:
            print("  ✗ Pandas henüz kurulmamış")
            return False
        except Exception as e:
            print(f"  ⚠ Pandas versiyonu kontrol edilemedi: {e}")
            return True
    
    def install_requirements(self) -> bool:
        """Gerekli paketleri kur"""
        print("Excel Karşılaştırma Uygulaması - Paket Kurulumu")
        print("=" * 55)
        
        # Python versiyonunu kontrol et
        if not self.check_python_version():
            return False
        
        # Platform bilgisi
        print(f"✓ İşletim sistemi: {platform.system()} {platform.release()}")
        
        # requirements.txt dosyasını oluştur/güncelle
        if not self.create_requirements_file():
            return False
        
        try:
            # pip'i güncelle
            self.upgrade_pip()
            
            # Ana paketleri kur
            print("\n📦 Ana paketler kuruluyor...")
            
            for package in REQUIRED_PACKAGES:
                if not self.install_package(package):
                    # Ana paket kurulumu başarısız
                    pass
            
            # Pandas versiyonunu kontrol et
            if not self.failed_packages:
                print("\n🔍 Pandas versiyonu kontrol ediliyor...")
                self.check_pandas_version()
            
            # Opsiyonel paketleri kur
            print("\n📦 Opsiyonel paketler kuruluyor...")
            for package in OPTIONAL_PACKAGES:
                self.install_package(package, optional=True)
            
            # Sonuçları değerlendir
            return self._evaluate_results()
        
        except subprocess.CalledProcessError as e:
            print(f"\n⚠ Paket kurulumu sırasında pip hatası: {e}")
            self._show_troubleshooting_tips()
            return False
        except KeyboardInterrupt:
            print("\n⚠ Kurulum kullanıcı tarafından iptal edildi")
            return False
        except Exception as e:
            print(f"\n⚠ Beklenmeyen hata: {e}")
            self._show_troubleshooting_tips()
            return False
    
    def _evaluate_results(self) -> bool:
        """Kurulum sonuçlarını değerlendir"""
        if self.failed_packages:
            print(f"\n⚠ Bazı ana paketler kurulamadı: {', '.join(self.failed_packages)}")
            print("\nManuel kurulum deneyin:")
            for package in self.failed_packages:
                print(f"  pip install {package}")
            return False
        else:
            print("\n✅ Tüm paketler başarıyla kuruldu!")
            print(f"Toplam {len(self.installed_packages)} paket kuruldu.")
            print("\nUygulamayı başlatmak için:")
            print("  python main.py        # Windows")
            print("  python3 main.py       # Linux/Mac")
            return True
    
    def _show_troubleshooting_tips(self) -> None:
        """Sorun giderme ipuçları göster"""
        print("\n🔧 Sorun giderme önerileri:")
        print("1. İnternet bağlantınızı kontrol edin")
        print("2. pip'i manuel güncelleyin: python -m pip install --upgrade pip")
        print("3. Yönetici olarak çalıştırmayı deneyin")
        print("4. Sanal ortam kullanmayı deneyin:")
        print("   python -m venv venv")
        print("   venv\\Scripts\\activate  # Windows")
        print("   source venv/bin/activate  # Linux/Mac")
        print("5. Ubuntu/Debian için:")
        print("   sudo apt update && sudo apt install python3-pip python3-tk")
    
    def verify_installation(self) -> bool:
        """Kurulumu doğrula"""
        print("\n🔍 Kurulum doğrulanıyor...")
        
        required_modules = [
            ("pandas", "Veri işleme"),
            ("openpyxl", "Excel dosya desteği"),
            ("xlrd", "Eski Excel formatları"),
            ("matplotlib", "Grafik oluşturma"),
            ("tkinter", "Kullanıcı arayüzü")
        ]
        
        optional_modules = [
            ("tkinterdnd2", "Drag & Drop desteği")
        ]
        
        missing_modules = []
        
        # Ana modülleri kontrol et
        for module, description in required_modules:
            try:
                if module == "pandas":
                    import pandas as pd
                    print(f"  ✓ {module} ({pd.__version__}) - {description}")
                elif module == "matplotlib":
                    import matplotlib
                    print(f"  ✓ {module} ({matplotlib.__version__}) - {description}")
                elif module == "openpyxl":
                    import openpyxl
                    print(f"  ✓ {module} ({openpyxl.__version__}) - {description}")
                else:
                    __import__(module)
                    print(f"  ✓ {module} - {description}")
            except ImportError:
                print(f"  ✗ {module} - {description} (EKSİK)")
                missing_modules.append(module)
            except Exception:
                print(f"  ⚠ {module} - {description} (versiyon kontrol edilemedi)")
        
        # Opsiyonel modülleri kontrol et
        for module, description in optional_modules:
            try:
                __import__(module)
                print(f"  ✓ {module} - {description}")
            except ImportError:
                print(f"  ⚠ {module} - {description} (opsiyonel - eksik)")
        
        if missing_modules:
            print(f"\n⚠ Eksik modüller: {', '.join(missing_modules)}")
            print("\nManuel kurulum:")
            if "tkinter" in missing_modules:
                print("  Ubuntu/Debian: sudo apt install python3-tk")
                print("  CentOS/RHEL: sudo yum install tkinter")
            print("  Diğer paketler: pip install " + " ".join(missing_modules))
            return False
        else:
            print("\n✅ Tüm gerekli modüller mevcut!")
            return True
    
    def show_system_info(self) -> None:
        """Sistem bilgilerini göster"""
        print("\n📋 Sistem Bilgileri:")
        print(f"  • Python: {sys.version}")
        print(f"  • Platform: {platform.platform()}")
        print(f"  • İşlemci: {platform.processor() or 'Bilinmiyor'}")
        
        # pip versiyonu
        try:
            result = subprocess.run(
                [self.python_executable, "-m", "pip", "--version"], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"  • pip: {result.stdout.strip()}")
        except:
            print("  • pip: Versiyon alınamadı")


def prompt_user_to_run_app(installer: InstallationManager) -> None:
    """Kullanıcıya uygulamayı çalıştırmak isteyip istemediğini sor"""
    try:
        print("\n🎉 Kurulum başarıyla tamamlandı!")
        print("\n🔥 Kullanım:")
        print("  python main.py        # Windows")
        print("  python3 main.py       # Linux/Mac")
        print("\n💡 İpucu: Deprecation warning'ları göz ardı edilebilir,")
        print("   program normal çalışır.")
        
        response = input("\nUygulamayı şimdi başlatmak ister misiniz? (y/n): ").strip().lower()
        
        if response in ['y', 'yes', 'evet', 'e']:
            print("\n🚀 Uygulama başlatılıyor...")
            try:
                subprocess.run([installer.python_executable, "main.py"])
            except FileNotFoundError:
                print("⚠ main.py dosyası bulunamadı!")
                print("Lütfen main.py dosyasının mevcut dizinde olduğundan emin olun.")
            except KeyboardInterrupt:
                print("\n⚠ Uygulama kullanıcı tarafından sonlandırıldı")
        else:
            print("\n✅ Kurulum tamamlandı. İyi kullanımlar!")
            
    except KeyboardInterrupt:
        print("\n\n⚠ Program kullanıcı tarafından sonlandırıldı.")
    except Exception as e:
        print(f"\n⚠ Uygulama başlatma hatası: {e}")


def show_failure_instructions() -> None:
    """Kurulum başarısız olduğunda yönergeleri göster"""
    print("\n⚠ Kurulum başarısız!")
    print("\n🔧 Manuel kurulum adımları:")
    print("  1. pip install --upgrade pip")
    print("  2. pip install pandas>=2.0.0 openpyxl xlrd matplotlib")
    print("  3. pip install tkinterdnd2  # Opsiyonel")
    print("\n🐧 Ubuntu/Debian için:")
    print("  sudo apt update")
    print("  sudo apt install python3-pip python3-tk")
    print("  pip3 install pandas openpyxl xlrd matplotlib tkinterdnd2")
    
    input("\nÇıkmak için Enter tuşuna basın...")


def main():
    """Ana fonksiyon"""
    installer = InstallationManager()
    
    try:
        # Sistem bilgilerini göster
        installer.show_system_info()
        
        # Kurulumu başlat
        if installer.install_requirements():
            # Kurulumu doğrula
            if installer.verify_installation():
                prompt_user_to_run_app(installer)
            else:
                print("\n⚠ Kurulum tamamlandı ancak bazı modüller eksik olabilir.")
                print("Yukarıdaki talimatları takip ederek eksik modülleri kurun.")
                input("\nÇıkmak için Enter tuşuna basın...")
        else:
            show_failure_instructions()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠ Program kullanıcı tarafından sonlandırıldı.")
        sys.exit(0)
    except Exception as e:
        print(f"\n⚠ Kritik hata: {e}")
        print("\n🔧 Sorun giderme:")
        print("  1. Python kurulumunuzu kontrol edin")
        print("  2. Terminal/Command Prompt'u yönetici olarak çalıştırın")
        print("  3. İnternet bağlantınızı kontrol edin")
        print("  4. Antivirüs yazılımınızın Python'u engellemediğinden emin olun")
        sys.exit(1)


if __name__ == "__main__":
    main()