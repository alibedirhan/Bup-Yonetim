# -*- coding: utf-8 -*-
"""
Musteri_Sayisi_Kontrolu - Ana Modül
Excel karşılaştırma uygulaması
"""

import os
import sys
from pathlib import Path

# Modül dizinini path'e ekle
_current_dir = Path(__file__).parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))

import tkinter as tk
from tkinter import messagebox
import pandas as pd
import re
import json
import logging
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import threading
from typing import Optional, Dict, List, Tuple, Any

# Constants
MAX_FILE_SIZE_MB = 100
EXCEL_CHUNK_SIZE = 1000
SUPPORTED_EXTENSIONS = {'.xlsx', '.xls'}
CONFIG_FILES = ['config.json', 'vehicle_config.json', 'drivers.json']
DEFAULT_OUTPUT_NAME = "karşılaştırma_sonucu"

# UI import kontrolü
try:
    from ui import ModernExcelComparisonUI
except ImportError as e:
    print(f"HATA: ui.py import edilemedi: {e}")
    ModernExcelComparisonUI = None

# Logging sistemi kurulumu
def setup_logging() -> None:
    """Logging sistemini kur"""
    try:
        logging.basicConfig(
            filename='app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )
    except TypeError:  # Python < 3.9 için encoding parametresi desteklenmez
        logging.basicConfig(
            filename='app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

setup_logging()


class VehicleDriverSetupDialog:
    """Araç-Plasiyer Eşleştirme Dialog'u"""
    
    def __init__(self, parent: tk.Tk, existing_data: Optional[Dict[str, str]] = None):
        self.parent = parent
        self.existing_data = existing_data or {}
        self.result: Optional[Dict[str, str]] = None
        self.dialog: Optional[tk.Toplevel] = None
        self.entries: Dict[str, tk.Entry] = {}
        
    def show_setup_dialog(self) -> Optional[Dict[str, str]]:
        """Araç-plasiyer eşleştirme dialog'unu göster"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Araç-Plasiyer Eşleştirmesi")
        self.dialog.geometry("500x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Dialog'u ortala
        self._center_dialog()
        
        # UI bileşenlerini oluştur
        self._create_dialog_ui()
        
        # Dialog'u modal yap ve sonucu döndür
        self.dialog.wait_window()
        return self.result
    
    def _center_dialog(self) -> None:
        """Dialog'u ekranın ortasına yerleştir"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"500x600+{x}+{y}")
    
    def _create_dialog_ui(self) -> None:
        """Dialog UI bileşenlerini oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        title_label = tk.Label(
            main_frame,
            text="Araç-Plasiyer Eşleştirmesi",
            font=('Segoe UI', 12, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Açıklama
        desc_label = tk.Label(
            main_frame,
            text="Lütfen her araç numarası için plasiyer adını girin.\nBoş bırakılan araçlar kullanılmayacak.",
            font=('Segoe UI', 9),
            justify=tk.LEFT
        )
        desc_label.pack(pady=(0, 15))
        
        # Scrollable area oluştur
        self._create_scrollable_area(main_frame)
        
        # Butonları oluştur
        self._create_dialog_buttons(main_frame)
    
    def _create_scrollable_area(self, parent: tk.Frame) -> None:
        """Kaydırılabilir alan oluştur"""
        canvas = tk.Canvas(parent, height=350)
        scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 20 araç için entry oluştur
        for i in range(1, 21):
            vehicle_num = f"{i:02d}"
            self._create_vehicle_entry(scrollable_frame, vehicle_num)
            
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_vehicle_entry(self, parent: tk.Frame, vehicle_num: str) -> None:
        """Tek araç için entry oluştur"""
        vehicle_frame = tk.Frame(parent)
        vehicle_frame.pack(fill=tk.X, pady=2)
        
        label = tk.Label(
            vehicle_frame,
            text=f"Araç {vehicle_num}:",
            width=10,
            anchor='w',
            font=('Segoe UI', 9)
        )
        label.pack(side=tk.LEFT)
        
        entry = tk.Entry(
            vehicle_frame, 
            width=30,
            font=('Segoe UI', 9)
        )
        entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.entries[vehicle_num] = entry
        
        # Mevcut veriyi yükle
        if vehicle_num in self.existing_data:
            entry.insert(0, self.existing_data[vehicle_num])
    
    def _create_dialog_buttons(self, parent: tk.Frame) -> None:
        """Dialog butonlarını oluştur"""
        button_frame = tk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=15)
        
        # Örnek veriler yükle
        load_sample_btn = tk.Button(
            button_frame,
            text="Örnek Veriler",
            command=self._load_sample_data,
            bg="#2196F3",
            fg="white",
            font=('Segoe UI', 9),
            padx=20
        )
        load_sample_btn.pack(side=tk.LEFT, padx=5)
        
        # İptal butonu
        cancel_btn = tk.Button(
            button_frame,
            text="İptal",
            command=self._cancel,
            bg="#f44336",
            fg="white",
            font=('Segoe UI', 9),
            padx=20
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Kaydet butonu
        save_btn = tk.Button(
            button_frame,
            text="Kaydet",
            command=self._save_config,
            bg="#4CAF50",
            fg="white",
            font=('Segoe UI', 9, 'bold'),
            padx=20
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
    
    def _load_sample_data(self) -> None:
        """Örnek verileri yükle"""
        sample_data = {
            "01": "Ahmet ALTILI",
            "02": "Erhan AYDOĞDU", 
            "04": "Soner TANAY",
            "05": "Süleyman TANAY",
            "06": "Hakan YILMAZ"
        }
        
        for vehicle_num, driver_name in sample_data.items():
            if vehicle_num in self.entries:
                self.entries[vehicle_num].delete(0, tk.END)
                self.entries[vehicle_num].insert(0, driver_name)
    
    def _save_config(self) -> None:
        """Konfigürasyonu kaydet"""
        vehicle_drivers = {}
        for vehicle_num, entry in self.entries.items():
            driver_name = entry.get().strip()
            if driver_name:
                vehicle_drivers[vehicle_num] = driver_name
        
        if not vehicle_drivers:
            messagebox.showwarning("Uyarı", "En az bir araç-plasiyer eşleştirmesi yapmalısınız!")
            return
        
        config = {"vehicle_drivers": vehicle_drivers}
        
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            self.result = vehicle_drivers
            messagebox.showinfo("Başarılı", f"{len(vehicle_drivers)} araç-plasiyer eşleştirmesi kaydedildi!")
            self.dialog.destroy()
            
        except Exception as e:
            logging.error(f"Config kaydetme hatası: {e}")
            messagebox.showerror("Hata", f"Kaydetme hatası: {e}")
    
    def _cancel(self) -> None:
        """İptal et"""
        self.result = None
        self.dialog.destroy()


class ExcelComparisonLogic:
    """Excel karşılaştırma iş mantığı"""
    
    def __init__(self):
        self.file1_path = tk.StringVar()
        self.file2_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.case_sensitive = tk.BooleanVar(value=False)
        self.output_path.set("")
        self.ui: Optional[ModernExcelComparisonUI] = None
        self.vehicle_drivers: Dict[str, str] = {}
        self._load_vehicle_drivers()
        
    def _load_vehicle_drivers(self) -> None:
        """Araç-plasiyer eşleştirmesini dosyadan yükler"""
        try:
            # Config dosyalarını dene
            for config_file in CONFIG_FILES:
                if Path(config_file).exists():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                            vehicle_drivers = config.get('vehicle_drivers', {})
                            if vehicle_drivers:
                                self.vehicle_drivers = vehicle_drivers
                                logging.info(f"Araç-plasiyer konfigürasyonu yüklendi: {config_file}")
                                return
                    except (json.JSONDecodeError, KeyError) as e:
                        logging.warning(f"Config dosyası okuma hatası {config_file}: {e}")
                        continue
            
            # Çevre değişkenlerini dene
            env_config = {}
            for i in range(1, 21):
                key = f"DRIVER_{i:02d}"
                if key in os.environ:
                    env_config[f"{i:02d}"] = os.environ[key]
            
            if env_config:
                self.vehicle_drivers = env_config
                logging.info("Araç-plasiyer konfigürasyonu çevre değişkenlerinden yüklendi")
            else:
                logging.warning("Araç-plasiyer konfigürasyonu bulunamadı!")
                
        except Exception as e:
            logging.error(f"Config yükleme hatası: {e}")
            self.vehicle_drivers = {}
    
    def set_ui(self, ui: 'ModernExcelComparisonUI') -> None:
        """UI referansını ayarla"""
        self.ui = ui
        
        if not self.vehicle_drivers:
            self._prompt_config_setup()
    
    def _prompt_config_setup(self) -> None:
        """Kullanıcıdan config setup'ı iste"""
        if not self.ui or not hasattr(self.ui, 'root'):
            return
            
        response = messagebox.askyesno(
            "Araç-Plasiyer Eşleştirmesi",
            "Araç-plasiyer eşleştirmesi bulunamadı.\n\n"
            "Şimdi eşleştirme yapmak ister misiniz?\n\n"
            "Evet: Eşleştirme ekranını aç\n"
            "Hayır: Varsayılan örnek config oluştur"
        )
        
        if response:
            if self.show_vehicle_setup_dialog():
                logging.info("Kullanıcı araç-plasiyer eşleştirmesi yaptı")
            else:
                logging.info("Kullanıcı araç-plasiyer eşleştirmesini iptal etti")
        else:
            self._create_default_config()
            self._load_vehicle_drivers()
    
    def _create_default_config(self) -> None:
        """Varsayılan config dosyasını oluştur"""
        default_config = {
            "vehicle_drivers": {
                "01": "Plasiyer 1",
                "02": "Plasiyer 2",
                "03": "Plasiyer 3",
                "04": "Plasiyer 4",
                "05": "Plasiyer 5"
            }
        }
        
        try:
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            
            logging.info("Varsayılan config.json dosyası oluşturuldu")
            
            if self.ui:
                self.ui.show_info("Bilgi", 
                    "Varsayılan config.json dosyası oluşturuldu.\n"
                    "Daha sonra Ayarlar menüsünden düzenleyebilirsiniz.")
                    
        except Exception as e:
            logging.error(f"Varsayılan config oluşturma hatası: {e}")
            if self.ui:
                self.ui.show_error("Hata", f"Config dosyası oluşturulamadı: {e}")
    
    def show_vehicle_setup_dialog(self) -> bool:
        """Araç-plasiyer eşleştirme dialog'unu göster"""
        if not self.ui or not hasattr(self.ui, 'root'):
            logging.error("UI referansı bulunamadı")
            return False
            
        try:
            dialog = VehicleDriverSetupDialog(self.ui.root, self.vehicle_drivers)
            result = dialog.show_setup_dialog()
            
            if result:
                self.vehicle_drivers = result
                return True
            return False
        except Exception as e:
            logging.error(f"Vehicle setup dialog hatası: {e}")
            return False
    
    def edit_vehicle_drivers(self) -> None:
        """Araç-plasiyer eşleştirmesini düzenle"""
        if not self.ui:
            return
        
        dialog = VehicleDriverSetupDialog(self.ui.root, self.vehicle_drivers)
        result = dialog.show_setup_dialog()
        
        if result:
            self.vehicle_drivers = result
            self.ui.show_info("Başarılı", "Araç-plasiyer eşleştirmesi güncellendi!")
    
    def validate_file_size(self, file_path: str) -> Tuple[bool, str]:
        """Dosya boyutunu kontrol et"""
        try:
            file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
            if file_size_mb > MAX_FILE_SIZE_MB:
                return False, f"Dosya boyutu çok büyük ({file_size_mb:.1f}MB). Maximum {MAX_FILE_SIZE_MB}MB destekleniyor."
            return True, ""
        except Exception as e:
            return False, f"Dosya boyutu kontrol edilemedi: {e}"
    
    def validate_excel_file(self, file_path: str) -> Tuple[bool, str]:
        """Excel dosyasının geçerli olup olmadığını kontrol eder"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return False, "Dosya bulunamadı!"
                
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                return False, f"Geçersiz dosya formatı! Desteklenen formatlar: {', '.join(SUPPORTED_EXTENSIONS)}"
                
            is_valid, error_msg = self.validate_file_size(file_path)
            if not is_valid:
                return False, error_msg
                
            # Basit Excel okuma testi
            pd.read_excel(file_path, nrows=1)
            return True, ""
            
        except PermissionError:
            return False, "Dosyaya erişim izni yok!"
        except pd.errors.EmptyDataError:
            return False, "Excel dosyası boş!"
        except Exception as e:
            return False, f"Geçersiz Excel dosyası: {e}"
    
    def _find_header_row(self, df: pd.DataFrame) -> int:
        """DataFrame içinde başlık satırını bulur"""
        try:
            # String'e çevir ve 'Cari Ünvan' ara
            df_str = df.astype(str)
            mask = df_str.apply(
                lambda row: row.str.contains("Cari Ünvan", case=False, na=False).any(), 
                axis=1
            )
            
            if mask.any():
                return mask.idxmax()
            return -1
        except Exception as e:
            logging.error(f"Başlık satırı bulma hatası: {e}")
            # Alternatif yöntem
            for i, row in df.iterrows():
                for value in row.values:
                    if isinstance(value, str) and "Cari Ünvan" in value:
                        return i
            return -1
    
    def _extract_vehicle_number(self, depo_text: str) -> Optional[str]:
        """Depo kartı metninden araç numarasını çıkarır"""
        if not isinstance(depo_text, str):
            return None
                
        logging.debug(f"Araç numarası çıkarma denemesi: '{depo_text}'")
                
        # Optimized regex patterns
        patterns = [
            r'[İI][Zz][Mm][İi][Rr]\s+[Aa][Rr][Aa][ÇçĞğ]\s+(\d{1,2})',
            r'[Aa]ra[çc]\s*(\d{1,2})',
            r'[Vv]ehicle\s*(\d{1,2})',
            r'(\d{1,2})\s*[Nn]o',
            r'\b(\d{1,2})\b'
        ]
        
        for pattern in patterns:
            try:
                match = re.search(pattern, depo_text)
                if match:
                    vehicle_num = f"{int(match.group(1)):02d}"
                    logging.debug(f"Araç numarası bulundu: {vehicle_num}")
                    
                    if vehicle_num in self.vehicle_drivers:
                        return vehicle_num
                    else:
                        logging.warning(f"Araç {vehicle_num} config'de bulunamadı")
            except (ValueError, AttributeError) as e:
                logging.warning(f"Regex hatası: {e}")
                continue
                        
        logging.warning(f"Hiçbir pattern eşleşmedi: '{depo_text}'")
        return None
    
    def _create_filename_with_driver(self, depo_text: str) -> str:
        """Depo kartından araç numarası çıkarıp plasiyer adıyla dosya adı oluşturur"""
        try:
            vehicle_num = self._extract_vehicle_number(depo_text)
            
            if vehicle_num and vehicle_num in self.vehicle_drivers:
                driver_name = self.vehicle_drivers[vehicle_num]
                filename = f"Arac_{vehicle_num}_{driver_name}"
                return self._sanitize_filename(filename)
            else:
                return self._sanitize_filename(depo_text) if depo_text else DEFAULT_OUTPUT_NAME
                
        except Exception as e:
            logging.error(f"Plasiyerli dosya adı oluşturma hatası: {e}")
            return self._sanitize_filename(depo_text) if depo_text else DEFAULT_OUTPUT_NAME
    
    def _sanitize_filename(self, filename: str) -> str:
        """Dosya adını güvenli hale getirir"""
        # Güvenli olmayan karakterleri kaldır
        invalid_chars = r'[\\/*?:"<>|]'
        safe_name = re.sub(invalid_chars, '', filename)
        safe_name = safe_name.strip()
        
        # Uzunluk kontrolü
        if len(safe_name) > 100:
            safe_name = safe_name[:100]
            
        return safe_name if safe_name else DEFAULT_OUTPUT_NAME
    
    def update_output_filename(self, file_path: str) -> None:
        """Seçilen dosyaya göre çıktı dosya adını günceller"""
        logging.debug(f"update_output_filename çağrıldı: {file_path}")
        
        try:
            is_valid, error_msg = self.validate_file_size(file_path)
            if not is_valid:
                logging.warning(f"Dosya boyutu hatası: {error_msg}")
                if self.ui:
                    self.ui.show_warning("Uyarı", error_msg)
                default_name = f"output_{datetime.now().strftime('%H%M%S')}"
                self.output_path.set(default_name)
                return
            
            # Sadece ilk 10 satırı oku
            df = pd.read_excel(file_path, header=None, nrows=10)
            logging.debug(f"Excel dosyası okundu, {len(df)} satır")
            
            depo_name = None
            for i in range(min(10, len(df))):
                if len(df.columns) == 0:
                    continue
                    
                row_str = str(df.iloc[i, 0])
                logging.debug(f"Satır {i}: '{row_str[:100]}...'")
                
                if "Cari Kategori 3" in row_str:
                    logging.debug(f"CARİ KATEGORİ 3 BULUNDU: {row_str[:100]}...")
                    match = re.search(r'\[(.*?)\]\s*(.*?)(?:\n|\r\n|$)', row_str)
                    if match and match.group(2):
                        depo_name = match.group(2).strip()
                        logging.debug(f"Araç adı çıkarıldı: '{depo_name}'")
                        break
            
            if depo_name:
                filename_with_driver = self._create_filename_with_driver(depo_name)
                logging.debug(f"Oluşturulan dosya adı: '{filename_with_driver}'")
                self.output_path.set(filename_with_driver)
            else:
                default_name = f"karşılaştırma_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                logging.debug(f"Varsayılan ad kullanılıyor: '{default_name}'")
                self.output_path.set(default_name)
                
        except Exception as e:
            default_name = f"karşılaştırma_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.output_path.set(default_name)
            logging.error(f"Filename güncelleme hatası: {e}")
            if self.ui:
                self.ui.show_warning("Uyarı", f"Dosya adı güncellenemedi: {default_name}")
    
    def _save_results_as_image(self, unique_cari_unvan_list: List[str], output_path: str, depo_name: Optional[str] = None) -> Tuple[bool, str]:
        """Sonuçları resim dosyası olarak kaydeder"""
        try:
            fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
            plt.rcParams['font.family'] = 'DejaVu Sans'
            
            if depo_name:
                vehicle_num = self._extract_vehicle_number(depo_name)
                if vehicle_num and vehicle_num in self.vehicle_drivers:
                    driver_name = self.vehicle_drivers[vehicle_num]
                    title = f"Araç {vehicle_num} - {driver_name}"
                else:
                    title = depo_name
                plt.suptitle(title, fontsize=16, fontweight='bold')
            else:
                plt.suptitle("Eksik Cari Ünvanlar", fontsize=16, fontweight='bold')
                
            cell_text = []
            for i, unvan in enumerate(unique_cari_unvan_list, 1):
                display_unvan = unvan if len(str(unvan)) <= 80 else str(unvan)[:77] + "..."
                cell_text.append([i, display_unvan])
                
            if not cell_text:
                cell_text = [["", "Tüm cari ünvanlar her iki dosyada da mevcut."]]
                
            plt.axis('off')
            table = plt.table(
                cellText=cell_text,
                colLabels=["#", "Cari Ünvan"],
                loc='center',
                cellLoc='left',
                colWidths=[0.1, 0.9]
            )
            
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1, 1.5)
            
            # Tablo styling
            for (i, j), cell in table.get_celld().items():
                if i == 0:
                    cell.set_text_props(fontweight='bold')
                    cell.set_facecolor('#e6e6e6')
                else:
                    if i % 2 == 0:
                        cell.set_facecolor('#f9f9f9')
            
            full_output_path = str(Path(output_path).resolve())
            
            # Dizin oluştur
            output_dir = Path(full_output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            plt.savefig(full_output_path, bbox_inches='tight', dpi=150, 
                       facecolor='white', edgecolor='none')
            plt.close(fig)  # Memory leak önleme
            
            return True, full_output_path
            
        except PermissionError as e:
            error_msg = f"Resim kaydetme izin hatası: {output_path} - {e}"
            logging.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Resim kaydetme hatası: {e}"
            logging.error(error_msg)
            return False, error_msg
        finally:
            plt.close('all')  # Tüm figürleri temizle
    
    def compare_files_thread(self) -> None:
        """Dosya karşılaştırmasını ayrı thread'de çalıştır"""
        try:
            self._compare_files_internal()
        except Exception as e:
            logging.error(f"Thread hatası: {e}")
            if self.ui:
                error_message = f"İşlem sırasında beklenmeyen hata: {e}"
                self.ui.root.after(0, lambda msg=error_message: self.ui.show_error("Hata", msg))
        finally:
            # UI'ı reset et
            if self.ui:
                self.ui.root.after(0, self.ui.reset_ui)
    
    def compare_files(self) -> None:
        """Excel dosyalarını karşılaştırır - Ana fonksiyon"""
        thread = threading.Thread(target=self.compare_files_thread, daemon=True)
        thread.start()
    
    def _compare_files_internal(self) -> None:
        """Excel dosyalarını karşılaştırır ve sonuçları gösterir"""
        file1_path = self.file1_path.get()
        file2_path = self.file2_path.get()
        output_path = self.output_path.get()
        
        # Input validation
        if not file1_path or not file2_path:
            if self.ui:
                self.ui.root.after(0, lambda: self.ui.show_error("Hata", "Lütfen her iki Excel dosyasını da seçin!"))
            return
        
        # File validation
        for file_path, file_desc in [(file1_path, "Eski tarihli"), (file2_path, "Yeni tarihli")]:
            is_valid, error_msg = self.validate_excel_file(file_path)
            if not is_valid:
                if self.ui:
                    self.ui.root.after(0, lambda e=error_msg, d=file_desc: self.ui.show_error("Hata", f"{d} dosya hatası: {e}"))
                return
        
        self.clear_results()
        
        try:
            logging.info(f"Dosyalar okunuyor: {file1_path}, {file2_path}")
            
            # İlk 15 satırı oku (header detection için)
            df1_header_search = pd.read_excel(file1_path, header=None, nrows=15)
            df2_header_search = pd.read_excel(file2_path, header=None, nrows=15)
            
            # Depo adını bul
            depo_name = self._extract_depo_name(df1_header_search)
            
            # Header satırlarını bul
            header_row1 = self._find_header_row(df1_header_search)
            header_row2 = self._find_header_row(df2_header_search)
            
            if header_row1 == -1 or header_row2 == -1:
                if self.ui:
                    self.ui.root.after(0, lambda: self.ui.show_error("Hata", "Excel dosyalarında 'Cari Ünvan' başlığı bulunamadı!"))
                return
            
            # Tam dosyaları oku
            df1 = pd.read_excel(file1_path, header=header_row1)
            df2 = pd.read_excel(file2_path, header=header_row2)
            
            # Sütun adlarını temizle
            df1.columns = [col.strip() if isinstance(col, str) else col for col in df1.columns]
            df2.columns = [col.strip() if isinstance(col, str) else col for col in df2.columns]
            
            # Cari Ünvan sütunlarını bul
            cari_unvan_col1 = self._find_cari_unvan_column(df1.columns)
            cari_unvan_col2 = self._find_cari_unvan_column(df2.columns)
            
            if not cari_unvan_col1 or not cari_unvan_col2:
                if self.ui:
                    self.ui.root.after(0, lambda: self.ui.show_error("Hata", "Bir veya daha fazla Excel dosyasında 'Cari Ünvan' sütunu bulunamadı."))
                return
            
            # Veri işleme ve karşılaştırma
            cari_unvan_list1 = self._extract_cari_unvan_list(df1, cari_unvan_col1)
            cari_unvan_list2 = self._extract_cari_unvan_list(df2, cari_unvan_col2)
            
            # Karşılaştırma yap
            unique_cari_unvan_list = self._perform_comparison(cari_unvan_list1, cari_unvan_list2)
            
            # Sonuçları göster
            status_text = f"Toplam {len(cari_unvan_list1)} cari ünvandan {len(unique_cari_unvan_list)} tanesi yeni dosyada bulunmuyor."
            if self.ui:
                self.ui.update_results(unique_cari_unvan_list, status_text)
            
            logging.info(f"Karşılaştırma tamamlandı. {len(unique_cari_unvan_list)} farklılık bulundu.")
            
            # Sonuçları kaydet
            self._save_results(unique_cari_unvan_list, output_path, depo_name)
        
        except MemoryError:
            if self.ui:
                self.ui.root.after(0, lambda: self.ui.show_error("Hata", "Dosyalar çok büyük, bellek yetersiz!"))
        except pd.errors.EmptyDataError:
            if self.ui:
                self.ui.root.after(0, lambda: self.ui.show_error("Hata", "Excel dosyalarından biri boş veya bozuk!"))
        except PermissionError:
            if self.ui:
                self.ui.root.after(0, lambda: self.ui.show_error("Hata", "Dosyalara erişim izni yok!"))
        except Exception as e:
            logging.error(f"Karşılaştırma hatası: {e}")
            if self.ui:
                error_message = f"İşlem sırasında bir hata oluştu: {e}"
                self.ui.root.after(0, lambda msg=error_message: self.ui.show_error("Hata", msg))
    
    def _extract_depo_name(self, df: pd.DataFrame) -> Optional[str]:
        """DataFrame'den depo adını çıkar"""
        try:
            for i in range(min(10, len(df))):
                if len(df.columns) == 0:
                    continue
                    
                row_str = str(df.iloc[i, 0])
                if "Cari Kategori 3" in row_str:
                    match = re.search(r'\[(.*?)\]\s*(.*?)(?:\n|\r\n|$)', row_str)
                    if match and match.group(2):
                        return match.group(2).strip()
            return None
        except Exception as e:
            logging.error(f"Depo adı çıkarma hatası: {e}")
            return None
    
    def _find_cari_unvan_column(self, columns) -> Optional[str]:
        """Cari Ünvan sütununu bul"""
        for col in columns:
            if isinstance(col, str) and "Cari Ünvan" in col:
                return col
        return None
    
    def _extract_cari_unvan_list(self, df: pd.DataFrame, cari_unvan_col: str) -> List[str]:
        """Cari ünvan listesini çıkar ve temizle"""
        cari_unvan_list = df[cari_unvan_col].dropna().apply(
            lambda x: x.strip() if isinstance(x, str) else str(x).strip()
        ).tolist()
        
        # Boş değerleri filtrele
        return [x for x in cari_unvan_list if x and x.strip()]
    
    def _perform_comparison(self, list1: List[str], list2: List[str]) -> List[str]:
        """İki liste arasında karşılaştırma yap"""
        if not self.case_sensitive.get():
            # Case-insensitive karşılaştırma
            list2_upper_set = {unvan.upper() for unvan in list2}
            unique_list = [
                unvan for unvan in list1 
                if unvan.upper() not in list2_upper_set
            ]
        else:
            # Case-sensitive karşılaştırma
            list2_set = set(list2)
            unique_list = [unvan for unvan in list1 if unvan not in list2_set]
        
        # Duplicate'leri kaldır (sırayı koruyarak)
        seen = set()
        return [x for x in unique_list if not (x in seen or seen.add(x))]
    
    def _save_results(self, unique_cari_unvan_list: List[str], output_path: str, depo_name: Optional[str]) -> None:
        """Sonuçları kaydet"""
        if not output_path or output_path.strip() == "":
            output_path = f"{DEFAULT_OUTPUT_NAME}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            logging.warning(f"Output path boş, varsayılan oluşturuldu: {output_path}")
            
        current_dir = Path.cwd()
        logging.info(f"Çalışma dizini: {current_dir}")
        logging.info(f"Output path: {output_path}")
        logging.info(f"Sonuç listesi uzunluğu: {len(unique_cari_unvan_list)}")
            
        try:
            save_excel = self.ui.save_excel.get() if self.ui else True
            save_image = self.ui.save_image.get() if self.ui else False
            
            logging.info(f"Save Excel: {save_excel}, Save Image: {save_image}")
            
            saved_files = []
            
            if save_excel:
                success, result_path = self._save_as_excel(unique_cari_unvan_list, output_path, depo_name)
                if success:
                    saved_files.append(f"Excel: {result_path}")
                elif self.ui:
                    err_msg = result_path
                    self.ui.root.after(0, lambda m=err_msg: self.ui.show_error("Hata", m))
            
            if save_image:
                image_path = str(current_dir / f"{output_path}.png")
                success, result_msg = self._save_results_as_image(unique_cari_unvan_list, image_path, depo_name)
                if success:
                    saved_files.append(f"Resim: {result_msg}")
                elif self.ui:
                    err_msg = result_msg
                    self.ui.root.after(0, lambda m=err_msg: self.ui.show_error("Hata", m))
            
            # Sonuç mesajı göster
            self._show_save_result(saved_files, save_excel, save_image)
                    
        except Exception as e:
            error_msg = f"Sonuç kaydetme genel hatası: {e}"
            logging.error(error_msg)
            if self.ui:
                self.ui.root.after(0, lambda m=error_msg: self.ui.show_error("Hata", m))
    
    def _save_as_excel(self, unique_cari_unvan_list: List[str], output_path: str, depo_name: Optional[str]) -> Tuple[bool, str]:
        """Excel olarak kaydet"""
        try:
            excel_path = Path.cwd() / f"{output_path}.xlsx"
            logging.info(f"Excel dosyası kaydediliyor: {excel_path}")
            
            # Dizin oluştur
            excel_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Tablo verisi oluştur
            table_data = [[i, unvan] for i, unvan in enumerate(unique_cari_unvan_list, 1)]
            result_df = pd.DataFrame(table_data, columns=["#", "Cari Ünvan"])
            
            try:
                # Gelişmiş Excel formatı ile kaydet
                self._save_excel_with_formatting(result_df, excel_path, depo_name)
            except ImportError:
                # Basit format ile kaydet
                logging.warning("openpyxl.styles import edilemedi, basit format kullanılıyor")
                result_df.to_excel(excel_path, index=False)
            
            logging.info(f"Excel dosyası başarıyla kaydedildi: {excel_path}")
            return True, str(excel_path)
            
        except PermissionError as e:
            error_msg = f"Excel dosyası kaydetme izni yok: {e}"
            logging.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Excel dosyası kaydedilemedi: {e}"
            logging.error(error_msg)
            return False, error_msg
    
    def _save_excel_with_formatting(self, result_df: pd.DataFrame, excel_path: Path, depo_name: Optional[str]) -> None:
        """Formatlanmış Excel kaydet"""
        from openpyxl.styles import Font, Border, Side, Alignment
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            if depo_name:
                # Header ekle
                vehicle_num = self._extract_vehicle_number(depo_name)
                if vehicle_num and vehicle_num in self.vehicle_drivers:
                    driver_name = self.vehicle_drivers[vehicle_num]
                    header_text = f"Araç {vehicle_num} - {driver_name}"
                else:
                    header_text = depo_name
                
                header_df = pd.DataFrame({"A": [header_text], "B": [""]})
                header_df.to_excel(writer, sheet_name='Sheet1', index=False, header=False, startrow=0)
                result_df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=2)
                
                # Styling uygula
                self._apply_excel_styling(writer, header_text, len(result_df))
            else:
                result_df.to_excel(writer, sheet_name='Sheet1', index=False)
    
    def _apply_excel_styling(self, writer, header_text: str, data_rows: int) -> None:
        """Excel styling uygula"""
        from openpyxl.styles import Font, Border, Side, Alignment
        
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        
        # Font ve border tanımları
        bold_font = Font(bold=True, color="000000", size=12)
        header_font = Font(bold=True, color="000000", size=10)
        normal_font = Font(color="000000", size=10)
        
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
        
        center_alignment = Alignment(horizontal='center', vertical='center')
        left_alignment = Alignment(horizontal='left', vertical='center')
        
        # Header styling
        worksheet.merge_cells('A1:B1')
        worksheet['A1'] = header_text
        worksheet['A1'].font = bold_font
        worksheet['A1'].alignment = center_alignment
        worksheet['A1'].border = thin_border
        
        # Tablo header styling
        worksheet['A3'].font = header_font
        worksheet['A3'].alignment = center_alignment
        worksheet['A3'].border = thin_border
        
        worksheet['B3'].font = header_font
        worksheet['B3'].alignment = center_alignment
        worksheet['B3'].border = thin_border
        
        # Veri satırları styling
        for row in range(4, data_rows + 4):
            worksheet[f'A{row}'].font = normal_font
            worksheet[f'A{row}'].alignment = center_alignment
            worksheet[f'A{row}'].border = thin_border
            
            worksheet[f'B{row}'].font = normal_font
            worksheet[f'B{row}'].alignment = left_alignment
            worksheet[f'B{row}'].border = thin_border
        
        # Sütun genişlikleri
        worksheet.column_dimensions['A'].width = 8
        worksheet.column_dimensions['B'].width = 60
    
    def _show_save_result(self, saved_files: List[str], save_excel: bool, save_image: bool) -> None:
        """Kaydetme sonucunu göster"""
        if saved_files:
            success_message = "Sonuçlar başarıyla kaydedildi:\n\n" + "\n".join(saved_files)
            logging.info(success_message)
            if self.ui:
                self.ui.root.after(0, lambda m=success_message: self.ui.show_info("Başarılı", m))
        elif not save_excel and not save_image:
            warning_msg = "Lütfen en az bir kaydetme formatı seçin (Excel veya Resim)!"
            logging.warning(warning_msg)
            if self.ui:
                self.ui.root.after(0, lambda m=warning_msg: self.ui.show_warning("Uyarı", m))
        else:
            error_msg = "Hiçbir dosya kaydedilemedi. Lütfen log dosyasını kontrol edin."
            logging.error(error_msg)
            if self.ui:
                self.ui.root.after(0, lambda m=error_msg: self.ui.show_error("Hata", m))
    
    def clear_results(self) -> None:
        """Sonuç listesini temizler"""
        if self.ui:
            self.ui.clear_results()


class ExcelComparisonApp:
    """Ana uygulama sınıfı"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.logic = ExcelComparisonLogic()
        self.ui = ModernExcelComparisonUI(root, self.logic)
        self.logic.set_ui(self.ui)


def check_dependencies() -> bool:
    """Gerekli bağımlılıkları kontrol et"""
    required_modules = ['pandas', 'openpyxl', 'matplotlib']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"Eksik modüller: {', '.join(missing)}")
        print("Kurulum için: python kurulum.py")
        return False
    
    return True


def create_root_window() -> tk.Tk:
    """Root window oluştur (DnD desteği ile veya olmadan)"""
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
        logging.info("tkinterdnd2 başarıyla yüklendi - Drag & Drop aktif")
        return root
    except ImportError:
        root = tk.Tk()
        logging.warning("tkinterdnd2 bulunamadı - Normal mod aktif")
        messagebox.showwarning(
            "Bilgi", 
            "Drag & Drop özelliği için 'tkinterdnd2' kütüphanesini yükleyin:\n\n"
            "pip install tkinterdnd2\n\n"
            "Şimdilik normal gözat butonlarıyla devam ediliyor."
        )
        return root


def main():
    """Ana program fonksiyonu"""
    try:
        # Bağımlılık kontrolü
        if not check_dependencies():
            sys.exit(1)
        
        # Root window oluştur
        root = create_root_window()
        if not root:
            raise RuntimeError("Tkinter root window oluşturulamadı")
        
        # Uygulamayı başlat
        try:
            app = ExcelComparisonApp(root)
            if not app.logic or not app.ui:
                raise RuntimeError("Uygulama bileşenleri başlatılamadı")
        except Exception as e:
            logging.error(f"Uygulama başlatma hatası: {e}")
            messagebox.showerror(
                "Başlatma Hatası", 
                f"Uygulama başlatılamadı:\n{e}\n\n"
                "Lütfen tüm dosyaların mevcut olduğundan emin olun."
            )
            return
        
        logging.info("Uygulama başarıyla başlatıldı")
        
        try:
            root.mainloop()
        except KeyboardInterrupt:
            logging.info("Uygulama kullanıcı tarafından sonlandırıldı")
        except Exception as e:
            logging.error(f"Ana döngü hatası: {e}")
            messagebox.showerror("Çalışma Hatası", f"Uygulama çalışırken hata oluştu: {e}")
        finally:
            try:
                if root:
                    root.quit()
                    root.destroy()
            except:
                pass
        
    except Exception as e:
        error_msg = f"Kritik uygulama hatası: {e}"
        logging.critical(error_msg)
        try:
            messagebox.showerror("Kritik Hata", error_msg)
        except:
            print(error_msg)
        sys.exit(1)


def main():
    root = tk.Tk()
    app = ExcelComparisonApp(root)
    root.mainloop()


def run_program():
    main()

if __name__ == "__main__":
    main()
