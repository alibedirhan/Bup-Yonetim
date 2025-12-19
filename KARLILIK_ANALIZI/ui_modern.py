# -*- coding: utf-8 -*-
"""
KARLILIK_ANALIZI - Modern CustomTkinter UI
Şube ve ürün karlılık analizleri
"""

# Windows/Tk: 'bad screen distance "200.0"' benzeri hataları engelle
import os as _os, sys as _sys

def _ensure_project_root():
    cur = _os.path.abspath(_os.path.dirname(__file__))
    for _ in range(6):
        if _os.path.isdir(_os.path.join(cur, "shared")):
            if cur not in _sys.path:
                _sys.path.insert(0, cur)
            return
        parent = _os.path.dirname(cur)
        if parent == cur:
            return
        cur = parent

try:
    _ensure_project_root()
    from shared.utils import apply_tk_float_fix as _apply_tk_float_fix, setup_turkish_locale as _setup_turkish_locale
    _apply_tk_float_fix()
    _setup_turkish_locale()
except Exception:
    pass

import customtkinter as ctk

# CustomTkinter DPI/scaling bazen float üretebiliyor -> sabitle
try:
    ctk.set_widget_scaling(1.0)
    ctk.set_window_scaling(1.0)
except Exception:
    pass

from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
import threading
import queue
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Modül dizinini path'e ekle
_current_dir = Path(__file__).parent
_parent_dir = _current_dir.parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

# Shared modüller
from shared.theme import COLORS, MODULE_COLORS, FONTS, SIZES
from shared.utils import setup_logging
from shared.components import (
    ModernHeader, ModernCard, ModernButton, StatCard,
    ProgressIndicator, FileSelector, ModernTabView,
    show_success, show_error, show_warning
)

# Karlılık backend
from karlilik import KarlilikAnalizi

logger = setup_logging("KARLILIK_UI")

# Modül renkleri
MODULE_NAME = "KARLILIK_ANALIZI"
ACCENT = MODULE_COLORS[MODULE_NAME]['accent']
ACCENT_HOVER = MODULE_COLORS[MODULE_NAME]['accent_hover']


class KarlilikAnaliziApp(ctk.CTkFrame):
    """Karlılık Analizi Ana Uygulama"""
    
    def __init__(self, master, standalone: bool = False):
        super().__init__(master, fg_color=COLORS['bg_light'])
        
        self.standalone = standalone
        self.master = master
        
        # Thread-safe communication
        self.result_queue = queue.Queue()
        self.is_processing = False
        self._closing = False
        
        # Dosya yolları
        self.karlilik_path = ctk.StringVar()
        self.iskonto_path = ctk.StringVar()
        
        # Karlılık analizi instance
        self.analiz = KarlilikAnalizi(
            progress_callback=self._thread_safe_progress,
            log_callback=self._thread_safe_log
        )
        
        # Analiz sonuçları
        self.analiz_sonucu = None
        
        # UI oluştur
        self._setup_ui()
        
        # Queue kontrol başlat
        self._check_queue()
        
        logger.info("Karlılık Analizi UI başlatıldı")
    
    def _setup_ui(self):
        """Ana UI yapısını oluştur"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ModernHeader(
            self,
            title="📊 Karlılık Analizi",
            subtitle="Excel verilerinizden detaylı karlılık raporları oluşturun",
            module_name=MODULE_NAME
        )
        header.grid(row=0, column=0, sticky="ew")
        
        # Tab view
        self.tabview = ModernTabView(self, module_name=MODULE_NAME)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        # Tabları oluştur
        self.tabview.add("📁 Dosya Seçimi")
        self.tabview.add("📋 İşlem Logları")
        self.tabview.add("📊 Dashboard")
        self.tabview.add("📈 Zaman Analizi")
        
        # Tab içeriklerini oluştur
        self._create_file_tab()
        self._create_log_tab()
        self._create_dashboard_tab()
        self._create_time_analysis_tab()
        
        # Alt kontrol paneli
        self._create_control_panel()
    
    def _create_file_tab(self):
        """Dosya seçimi tabı"""
        tab = self.tabview.tab("📁 Dosya Seçimi")
        tab.grid_columnconfigure(0, weight=1)
        
        # Açıklama
        info_frame = ctk.CTkFrame(tab, fg_color=COLORS['hover_light'], corner_radius=SIZES['corner_radius'])
        info_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 15))
        
        info_text = """💡 Kullanım Adımları:
1. Karlılık Raporu Excel dosyasını seçin (satış verileri içeren)
2. İskonto/Maliyet Excel dosyasını seçin (fiyat bilgileri içeren)
3. "Analizi Başlat" butonuna tıklayın
4. Sonuçları Dashboard sekmesinde inceleyin"""
        
        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(family=FONTS['body'][0], size=12),
            text_color=COLORS['text_secondary'],
            justify="left"
        ).pack(padx=20, pady=15, anchor="w")
        
        # Dosya seçim kartları
        files_frame = ctk.CTkFrame(tab, fg_color="transparent")
        files_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        files_frame.grid_columnconfigure(0, weight=1)
        
        # Karlılık Raporu
        karlilik_card = ModernCard(files_frame, title="📊 Karlılık Raporu", icon="📊")
        karlilik_card.grid(row=0, column=0, sticky="ew", pady=10)
        
        karlilik_inner = ctk.CTkFrame(karlilik_card, fg_color="transparent")
        karlilik_inner.pack(fill="x", padx=20, pady=15)
        
        self.karlilik_entry = ctk.CTkEntry(
            karlilik_inner,
            textvariable=self.karlilik_path,
            placeholder_text="Excel dosyası seçin...",
            height=40,
            corner_radius=SIZES['corner_radius'],
            border_width=1,
            border_color=COLORS['border']
        )
        self.karlilik_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        karlilik_btn = ModernButton(
            karlilik_inner,
            text="Dosya Seç",
            icon="📁",
            command=self._select_karlilik_file,
            module_name=MODULE_NAME,
            width=120
        )
        karlilik_btn.pack(side="right")
        
        # Bilgi etiketi
        self.karlilik_info = ctk.CTkLabel(
            karlilik_card,
            text="",
            font=ctk.CTkFont(family=FONTS['small'][0], size=FONTS['small'][1]),
            text_color=COLORS['text_secondary']
        )
        self.karlilik_info.pack(padx=20, pady=(0, 10))
        
        # İskonto Dosyası
        iskonto_card = ModernCard(files_frame, title="💰 İskonto/Maliyet Dosyası", icon="💰")
        iskonto_card.grid(row=1, column=0, sticky="ew", pady=10)
        
        iskonto_inner = ctk.CTkFrame(iskonto_card, fg_color="transparent")
        iskonto_inner.pack(fill="x", padx=20, pady=15)
        
        self.iskonto_entry = ctk.CTkEntry(
            iskonto_inner,
            textvariable=self.iskonto_path,
            placeholder_text="Excel dosyası seçin...",
            height=40,
            corner_radius=SIZES['corner_radius'],
            border_width=1,
            border_color=COLORS['border']
        )
        self.iskonto_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        iskonto_btn = ModernButton(
            iskonto_inner,
            text="Dosya Seç",
            icon="📁",
            command=self._select_iskonto_file,
            module_name=MODULE_NAME,
            width=120
        )
        iskonto_btn.pack(side="right")
        
        # Bilgi etiketi
        self.iskonto_info = ctk.CTkLabel(
            iskonto_card,
            text="",
            font=ctk.CTkFont(family=FONTS['small'][0], size=FONTS['small'][1]),
            text_color=COLORS['text_secondary']
        )
        self.iskonto_info.pack(padx=20, pady=(0, 10))
        
        # İşlem butonu
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=30)
        
        self.process_btn = ModernButton(
            btn_frame,
            text="Analizi Başlat",
            icon="🚀",
            command=self._start_analysis,
            module_name=MODULE_NAME,
            size='large',
            width=200
        )
        self.process_btn.pack()
    
    def _create_log_tab(self):
        """İşlem logları tabı"""
        tab = self.tabview.tab("📋 İşlem Logları")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Log text alanı
        self.log_text = ctk.CTkTextbox(
            tab,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=COLORS['bg_card'],
            text_color=COLORS['text_primary'],
            corner_radius=SIZES['corner_radius'],
            border_width=1,
            border_color=COLORS['border']
        )
        self.log_text.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Hoşgeldin mesajı
        self._log_message("Karlılık Analizi Modülü Hazır", "info")
        self._log_message("Dosyaları seçerek başlayabilirsiniz.", "info")
    
    def _create_dashboard_tab(self):
        """Dashboard tabı - analiz sonrası doldurulacak"""
        tab = self.tabview.tab("📊 Dashboard")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Placeholder
        self.dashboard_placeholder = ctk.CTkFrame(tab, fg_color="transparent")
        self.dashboard_placeholder.grid(row=0, column=0, sticky="nsew")
        
        placeholder_label = ctk.CTkLabel(
            self.dashboard_placeholder,
            text="📊\n\nAnaliz tamamlandıktan sonra\nburada detaylı dashboard görüntülenecek",
            font=ctk.CTkFont(family=FONTS['body'][0], size=14),
            text_color=COLORS['text_secondary']
        )
        placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Dashboard container (sonra doldurulacak)
        self.dashboard_container = None
    
    def _create_time_analysis_tab(self):
        """Zaman analizi tabı"""
        tab = self.tabview.tab("📈 Zaman Analizi")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Zaman analizi modülünü yükle
        try:
            from zaman_analizi import ZamanAnalizi
            import tkinter.ttk as ttk_notebook
            
            # Zaman analizi için bir ttk.Notebook gerekiyor
            # CTkFrame içine ttk.Notebook yerleştir
            self.zaman_notebook = ttk_notebook.Notebook(tab)
            self.zaman_notebook.pack(fill="both", expand=True, padx=5, pady=5)
            
            # ZamanAnalizi widget'ını oluştur (notebook gerektirir)
            self.zaman_analizi = ZamanAnalizi(self.zaman_notebook)
            
        except ImportError as e:
            logger.warning(f"Zaman analizi modülü yüklenemedi: {e}")
            
            placeholder = ctk.CTkLabel(
                tab,
                text="📈\n\nZaman Analizi modülü yüklenemedi\n\n" + str(e),
                font=ctk.CTkFont(family=FONTS['body'][0], size=14),
                text_color=COLORS['text_secondary']
            )
            placeholder.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            logger.error(f"Zaman analizi oluşturma hatası: {e}", exc_info=True)
            
            placeholder = ctk.CTkLabel(
                tab,
                text=f"📈\n\nZaman Analizi yüklenirken hata oluştu:\n\n{str(e)}",
                font=ctk.CTkFont(family=FONTS['body'][0], size=14),
                text_color=COLORS['error']
            )
            placeholder.place(relx=0.5, rely=0.5, anchor="center")
    
    def _create_control_panel(self):
        """Alt kontrol paneli"""
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        control_frame.grid_columnconfigure(0, weight=1)
        
        # Progress indicator
        self.progress = ProgressIndicator(control_frame, module_name=MODULE_NAME)
        self.progress.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Stat kartları
        stats_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.stat_cards = {}
        
        stats_info = [
            ('products', 'Ürün Sayısı', '📦', '0'),
            ('matched', 'Eşleşen', '✓', '0'),
            ('total_profit', 'Toplam Kar', '💰', '0 ₺'),
            ('avg_profit', 'Ort. Kar', '📊', '0 ₺')
        ]
        
        for i, (key, title, icon, value) in enumerate(stats_info):
            card = StatCard(
                stats_frame,
                title=title,
                value=value,
                icon=icon,
                accent_color=ACCENT
            )
            card.grid(row=0, column=i, padx=8, pady=5, sticky="ew")
            self.stat_cards[key] = card
    
    # === Dosya İşlemleri ===
    
    def _select_karlilik_file(self):
        """Karlılık dosyası seç"""
        file_path = filedialog.askopenfilename(
            title="Karlılık Raporu Seçin",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if file_path:
            self.karlilik_path.set(file_path)
            file_name = Path(file_path).name
            file_size = Path(file_path).stat().st_size / 1024
            self.karlilik_info.configure(
                text=f"✓ {file_name} ({file_size:.1f} KB)",
                text_color=COLORS['success']
            )
            self._log_message(f"Karlılık dosyası seçildi: {file_name}", "success")
    
    def _select_iskonto_file(self):
        """İskonto dosyası seç"""
        file_path = filedialog.askopenfilename(
            title="İskonto/Maliyet Dosyası Seçin",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if file_path:
            self.iskonto_path.set(file_path)
            file_name = Path(file_path).name
            file_size = Path(file_path).stat().st_size / 1024
            self.iskonto_info.configure(
                text=f"✓ {file_name} ({file_size:.1f} KB)",
                text_color=COLORS['success']
            )
            self._log_message(f"İskonto dosyası seçildi: {file_name}", "success")
    
    # === Analiz İşlemleri ===
    
    def _start_analysis(self):
        """Analizi başlat"""
        if self.is_processing:
            show_warning("Uyarı", "Zaten bir işlem devam ediyor!")
            return
        
        karlilik = self.karlilik_path.get()
        iskonto = self.iskonto_path.get()
        
        if not karlilik:
            show_warning("Uyarı", "Lütfen karlılık raporu dosyasını seçin!")
            return
        
        if not iskonto:
            show_warning("Uyarı", "Lütfen iskonto/maliyet dosyasını seçin!")
            return
        
        self.is_processing = True
        self.process_btn.configure(state="disabled", text="İşleniyor...")
        self.progress.set_indeterminate("Analiz başlatılıyor...")
        
        # Log sekmesine geç
        self.tabview.set("📋 İşlem Logları")
        
        # Thread'de çalıştır
        thread = threading.Thread(
            target=self._run_analysis,
            args=(karlilik, iskonto),
            daemon=True
        )
        thread.start()
    
    def _run_analysis(self, karlilik_path: str, iskonto_path: str):
        """Analizi thread'de çalıştır"""
        try:
            self._thread_safe_log("Analiz başlatılıyor...", "info")
            
            # Karlılık dosyasını işle
            result = self.analiz.process_files(karlilik_path, iskonto_path)
            
            if result:
                self.result_queue.put(('complete', result))
            else:
                self.result_queue.put(('error', "Analiz başarısız oldu"))
                
        except Exception as e:
            logger.error(f"Analiz hatası: {e}", exc_info=True)
            self.result_queue.put(('error', str(e)))
    
    def _on_analysis_complete(self, result):
        """Analiz tamamlandığında"""
        self.is_processing = False
        self.analiz_sonucu = result
        
        self._log_message("✓ Analiz başarıyla tamamlandı!", "success")
        
        # İstatistikleri güncelle
        self._update_statistics(result)
        
        # Dashboard'u güncelle
        self._populate_dashboard(result)
        
        # Butonu sıfırla
        self.process_btn.configure(state="normal", text="🚀 Analizi Başlat")
        self.progress.reset()
        
        show_success("Başarılı", "Karlılık analizi tamamlandı!\nDashboard sekmesinde sonuçları görebilirsiniz.")
        
        # Dashboard sekmesine geç
        self.tabview.set("📊 Dashboard")
    
    def _on_analysis_error(self, error_msg: str):
        """Analiz hatası"""
        self.is_processing = False
        self._log_message(f"✗ HATA: {error_msg}", "error")
        
        self.process_btn.configure(state="normal", text="🚀 Analizi Başlat")
        self.progress.reset()
        
        show_error("Hata", f"Analiz sırasında hata oluştu:\n{error_msg}")
    
    def _update_statistics(self, result: Dict):
        """İstatistikleri güncelle"""
        if not result:
            return
        
        try:
            df = result.get('dataframe')
            if df is not None:
                self.stat_cards['products'].set_value(str(len(df)))
                
                matched = result.get('matched_count', 0)
                self.stat_cards['matched'].set_value(str(matched))
                
                if 'Net Kar' in df.columns:
                    total = df['Net Kar'].sum()
                    avg = df['Net Kar'].mean()
                    self.stat_cards['total_profit'].set_value(f"{total:,.2f} ₺")
                    self.stat_cards['avg_profit'].set_value(f"{avg:,.2f} ₺")
        except Exception as e:
            logger.error(f"İstatistik güncelleme hatası: {e}")
    
    def _populate_dashboard(self, result: Dict):
        """Dashboard'u doldur"""
        if self.dashboard_placeholder:
            self.dashboard_placeholder.destroy()
            self.dashboard_placeholder = None
        
        tab = self.tabview.tab("📊 Dashboard")
        
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        scroll_frame.grid_columnconfigure((0, 1), weight=1)
        
        try:
            df = result.get('dataframe')
            if df is None:
                return
            
            # Özet kartlar
            summary_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            summary_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)
            summary_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
            
            # Toplam ürün
            card1 = StatCard(summary_frame, "Toplam Ürün", str(len(df)), "📦", ACCENT)
            card1.grid(row=0, column=0, padx=5, sticky="ew")
            
            # Karlı ürün
            if 'Net Kar' in df.columns:
                karli = len(df[df['Net Kar'] > 0])
                card2 = StatCard(summary_frame, "Karlı Ürün", str(karli), "✓", COLORS['success'])
                card2.grid(row=0, column=1, padx=5, sticky="ew")
                
                # Zararlı ürün
                zarli = len(df[df['Net Kar'] < 0])
                card3 = StatCard(summary_frame, "Zararlı Ürün", str(zarli), "✗", COLORS['error'])
                card3.grid(row=0, column=2, padx=5, sticky="ew")
                
                # Toplam kar
                total = df['Net Kar'].sum()
                card4 = StatCard(summary_frame, "Net Kar", f"{total:,.2f} ₺", "💰", 
                               COLORS['success'] if total > 0 else COLORS['error'])
                card4.grid(row=0, column=3, padx=5, sticky="ew")
            
            # Tablo
            table_card = ModernCard(scroll_frame, title="📋 Ürün Detayları")
            table_card.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)
            
            # Treeview
            columns = list(df.columns)[:8]  # İlk 8 sütun
            
            tree_frame = ctk.CTkFrame(table_card, fg_color="transparent")
            tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor='center')
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Verileri ekle (ilk 100 satır)
            for idx, row in df.head(100).iterrows():
                values = [row[col] if col in row else '' for col in columns]
                tree.insert('', 'end', values=values)
            
        except Exception as e:
            logger.error(f"Dashboard doldurma hatası: {e}")
            error_label = ctk.CTkLabel(
                scroll_frame,
                text=f"Dashboard yüklenirken hata oluştu:\n{str(e)}",
                text_color=COLORS['error']
            )
            error_label.pack(pady=50)
    
    # === Thread-safe İşlemler ===
    
    def _thread_safe_progress(self, value: int, status: str):
        """Thread-safe progress güncelleme"""
        if not self._closing:
            self.result_queue.put(('progress', {'value': value, 'status': status}))
    
    def _thread_safe_log(self, message: str, msg_type: str = 'info'):
        """Thread-safe log mesajı"""
        if not self._closing:
            self.result_queue.put(('log', {'message': message, 'type': msg_type}))
    
    def _check_queue(self):
        """Queue'yu kontrol et"""
        if self._closing:
            return
        
        try:
            while True:
                msg_type, data = self.result_queue.get_nowait()
                
                if msg_type == 'progress':
                    self.progress.set_progress(data['value'], data['status'])
                elif msg_type == 'log':
                    self._log_message(data['message'], data['type'])
                elif msg_type == 'complete':
                    self._on_analysis_complete(data)
                elif msg_type == 'error':
                    self._on_analysis_error(data)
                    
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Queue kontrol hatası: {e}")
        
        # Tekrar kontrol et
        if not self._closing:
            self.after(100, self._check_queue)
    
    def _log_message(self, message: str, msg_type: str = 'info'):
        """Log mesajı ekle"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            icons = {
                'info': 'ℹ️',
                'success': '✅',
                'warning': '⚠️',
                'error': '❌'
            }
            icon = icons.get(msg_type, 'ℹ️')
            
            formatted = f"[{timestamp}] {icon} {message}\n"
            
            self.log_text.insert("end", formatted)
            self.log_text.see("end")
            
        except Exception as e:
            logger.error(f"Log mesajı hatası: {e}")
    
    def cleanup(self):
        """Temizlik işlemleri"""
        self._closing = True
        logger.info("Karlılık Analizi UI kapatılıyor")


def main():
    """Standalone çalıştırma"""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("Bupiliç Karlılık Analizi")
    root.geometry("1200x800")
    root.minsize(1000, 700)
    
    app = KarlilikAnaliziApp(root, standalone=True)
    app.pack(fill="both", expand=True)
    
    def on_close():
        app.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
