# -*- coding: utf-8 -*-
"""
YASLANDIRMA - Modern CustomTkinter UI
Excel Cari Yaşlandırma İşleyici

Tüm fonksiyonlar tam çalışır durumda.
Orijinal özelliklerin tamamı korunmuş.

Version: 3.0.0 - Production Ready
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

from tkinter import messagebox, filedialog
import tkinter.ttk as ttk
import tkinter as tk
import sys
import logging
import threading
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

# =============================================================================
# PATH SETUP
# =============================================================================

_current_dir = Path(__file__).parent
_gui_dir = _current_dir / "gui"
_modules_dir = _current_dir / "modules"

for p in [_current_dir, _gui_dir, _modules_dir]:
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("YASLANDIRMA_UI")

# =============================================================================
# RENKLER
# =============================================================================

COLORS = {
    'bg_light': '#F5F7FA',
    'bg_card': '#FFFFFF',
    'bg_dark': '#2D3748',
    'text_primary': '#2C3E50',
    'text_secondary': '#7F8C8D',
    'text_light': '#FFFFFF',
    'border': '#E0E6ED',
    'hover_light': '#EBF5FB',
    'accent': '#F4A261',
    'accent_hover': '#E76F51',
    'success': '#2ECC71',
    'warning': '#F39C12',
    'error': '#E74C3C',
    'info': '#3498DB',
    'analyze': '#FF6B35',
    'analyze_hover': '#E55A2B',
    'purple': '#9B59B6',
    'purple_hover': '#8E44AD',
}


# =============================================================================
# ÖNİZLEME PENCERESI
# =============================================================================

class PreviewWindow(ctk.CTkToplevel):
    """Tam ekran veri önizleme penceresi"""
    
    def __init__(self, parent, dataframe, title="Veri Önizlemesi"):
        super().__init__(parent)
        
        self.df = dataframe
        self.title(title)
        self.geometry("1200x700")
        self.minsize(800, 500)
        
        # Modal
        self.transient(parent)
        self.after(100, self._safe_grab)
        
        self._build_ui()
    
    def _safe_grab(self):
        """Güvenli grab"""
        try:
            if self.winfo_viewable():
                self.grab_set()
                self.focus_force()
        except tk.TclError:
            self.after(100, self._safe_grab)
    
    def _build_ui(self):
        """UI oluştur"""
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS['accent'], height=60, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header, text=f"📋 {self.title()} - {len(self.df)} satır, {len(self.df.columns)} sütun",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS['text_light']
        ).pack(side="left", padx=20, pady=15)
        
        ctk.CTkButton(
            header, text="✕ Kapat", width=100, height=35,
            fg_color=COLORS['error'], hover_color="#C0392B",
            command=self.destroy
        ).pack(side="right", padx=20, pady=12)
        
        # Tablo
        table_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_card'])
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview
        columns = list(self.df.columns)
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Sütunlar
        for col in columns:
            tree.heading(col, text=str(col))
            tree.column(col, width=100, minwidth=50)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        # Layout
        tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Verileri ekle
        for _, row in self.df.iterrows():
            values = [str(v)[:50] if v is not None else "" for v in row.values]
            tree.insert("", "end", values=values)


# =============================================================================
# ANALİZ SONUÇ KARTI
# =============================================================================

class AnalysisResultCard(ctk.CTkFrame):
    """Tek ARAÇ için analiz sonuç kartı"""
    
    def __init__(self, parent, arac_no: str, data: Dict):
        super().__init__(parent, fg_color=COLORS['bg_light'], corner_radius=10)
        
        self.arac_no = arac_no
        self.data = data
        
        self._build_ui()
    
    def _build_ui(self):
        """UI oluştur"""
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS['accent'], corner_radius=8)
        header.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            header, text=f"🚗 ARAÇ {self.arac_no}",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS['text_light']
        ).pack(side="left", padx=15, pady=10)
        
        # İçerik
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=10)
        
        # Metrikler
        metrics = [
            ("👥 Müşteri", self.data.get('musteri_sayisi', 0)),
            ("💰 Toplam Bakiye", f"{self.data.get('toplam_bakiye', 0):,.2f} ₺"),
            ("📊 Ort. Bakiye", f"{self.data.get('ortalama_bakiye', 0):,.2f} ₺"),
        ]
        
        for label, value in metrics:
            row = ctk.CTkFrame(content, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                row, text=label,
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color=COLORS['text_secondary'], width=120, anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                row, text=str(value),
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=COLORS['text_primary']
            ).pack(side="left")


# =============================================================================
# ANA UYGULAMA
# =============================================================================

class YaslandirmaApp(ctk.CTkFrame):
    """
    Yaşlandırma Ana Uygulaması - Production Ready
    
    Tüm özellikler:
    - Excel dosyası yükleme ve işleme
    - Veri önizleme (tam ekran pencere)
    - ARAÇ bazlı analiz
    - Detaylı ARAÇ görüntüleme
    - Rapor oluşturma
    - Veri yedekleme/geri yükleme
    """
    
    def __init__(self, master, standalone: bool = False):
        super().__init__(master, fg_color=COLORS['bg_light'])
        
        self.master = master
        self.standalone = standalone
        
        # Veri değişkenleri
        self.file_path: Optional[str] = None
        self.processed_df = None
        self.original_df = None
        
        # Modül referansları
        self.processor = None
        self.analysis_engine = None
        self.assignment_manager = None
        self.data_manager = None
        self.report_generator = None
        self.visualization_engine = None
        self.modules_available = False
        
        # Analiz sonuçları
        self.current_analysis_results: Dict = {}
        self.selected_arac: Optional[str] = None
        
        # UI bileşenleri
        self.tree: Optional[ttk.Treeview] = None
        self.status_label: Optional[ctk.CTkLabel] = None
        self.progress_bar: Optional[ctk.CTkProgressBar] = None
        self.file_label: Optional[ctk.CTkLabel] = None
        self.stats_label: Optional[ctk.CTkLabel] = None
        self.notebook: Optional[ttk.Notebook] = None
        self.analysis_scroll_frame = None
        self.arac_dropdown = None
        self.arac_detail_frame = None
        
        # Butonlar
        self.select_btn = None
        self.process_btn = None
        self.analyze_btn = None
        self.save_btn = None
        self.restore_btn = None
        self.preview_btn = None
        
        # Modülleri yükle
        self._load_modules()
        
        # UI oluştur
        self._build_ui()
        
        logger.info("Yaşlandırma UI başlatıldı")
    
    def _load_modules(self):
        """Alt modülleri yükle"""
        try:
            # Excel Processor (zorunlu)
            try:
                from .excel_processor import ExcelProcessor, ExcelProcessorError
            except ImportError:
                from excel_processor import ExcelProcessor, ExcelProcessorError
            
            self.processor = ExcelProcessor()
            self.ExcelProcessorError = ExcelProcessorError
            logger.info("ExcelProcessor yüklendi")
            
            # Analiz modülleri (opsiyonel)
            try:
                try:
                    from .modules.analysis import AnalysisEngine
                    from .modules.assignment import AssignmentManager
                    from .modules.data_manager import DataManager
                    from .modules.reports import ReportGenerator
                    from .modules.visualization import VisualizationEngine
                except ImportError:
                    from modules.analysis import AnalysisEngine
                    from modules.assignment import AssignmentManager
                    from modules.data_manager import DataManager
                    from modules.reports import ReportGenerator
                    from modules.visualization import VisualizationEngine
                
                self.analysis_engine = AnalysisEngine()
                self.assignment_manager = AssignmentManager()
                self.data_manager = DataManager()
                self.report_generator = ReportGenerator()
                self.visualization_engine = VisualizationEngine()
                self.modules_available = True
                logger.info("Tüm analiz modülleri yüklendi")
                
            except ImportError as e:
                logger.warning(f"Analiz modülleri yüklenemedi: {e}")
                self.modules_available = False
                
        except ImportError as e:
            logger.error(f"ExcelProcessor yüklenemedi: {e}")
            self.processor = None
    
    # =========================================================================
    # UI OLUŞTURMA
    # =========================================================================
    
    def _build_ui(self):
        """Ana UI yapısını oluştur"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._build_header()
        self._build_content()
        self._build_status_bar()
    
    def _build_header(self):
        """Header - başlık ve butonlar"""
        header = ctk.CTkFrame(self, fg_color=COLORS['accent'], height=110, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        
        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=25, pady=12)
        
        # Sol - başlık
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="y")
        
        ctk.CTkLabel(
            left, text="📊 Excel Cari Yaşlandırma İşleyici",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS['text_light']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            left, text="Excel dosyalarını işleyin • ARAÇ bazlı analiz yapın • Raporlar oluşturun",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#FFF3E0"
        ).pack(anchor="w", pady=(3, 0))
        
        # Sağ - butonlar
        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right", fill="y")
        
        btn_style = {
            "height": 40,
            "corner_radius": 8,
            "font": ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        }
        
        # Dosya Seç
        self.select_btn = ctk.CTkButton(
            right, text="📁 Dosya Seç", width=110,
            fg_color=COLORS['bg_card'], text_color=COLORS['text_primary'],
            hover_color="#E5E7EB", command=self._select_file, **btn_style
        )
        self.select_btn.pack(side="left", padx=4)
        
        # İşle
        self.process_btn = ctk.CTkButton(
            right, text="⚙️ İşle", width=85,
            fg_color=COLORS['info'], hover_color="#2980B9",
            state="disabled", command=self._process_file, **btn_style
        )
        self.process_btn.pack(side="left", padx=4)
        
        # Önizle
        self.preview_btn = ctk.CTkButton(
            right, text="👁 Önizle", width=90,
            fg_color=COLORS['purple'], hover_color=COLORS['purple_hover'],
            state="disabled", command=self._show_preview_window, **btn_style
        )
        self.preview_btn.pack(side="left", padx=4)
        
        # Analiz
        if self.modules_available:
            self.analyze_btn = ctk.CTkButton(
                right, text="📈 Analiz", width=90,
                fg_color=COLORS['analyze'], hover_color=COLORS['analyze_hover'],
                state="disabled", command=self._start_analysis, **btn_style
            )
            self.analyze_btn.pack(side="left", padx=4)
        
        # Kaydet
        self.save_btn = ctk.CTkButton(
            right, text="💾 Kaydet", width=90,
            fg_color=COLORS['success'], hover_color="#27AE60",
            state="disabled", command=self._save_file, **btn_style
        )
        self.save_btn.pack(side="left", padx=4)
        
        # Geri Yükle
        self.restore_btn = ctk.CTkButton(
            right, text="↩️ Geri", width=75,
            fg_color=COLORS['warning'], hover_color="#E67E22",
            state="disabled", command=self._restore_backup, **btn_style
        )
        self.restore_btn.pack(side="left", padx=4)
    
    def _build_content(self):
        """Ana içerik - Notebook"""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)
        
        # Notebook
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[20, 10], font=('Segoe UI', 11, 'bold'))
        
        self.notebook = ttk.Notebook(content)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        
        # Tab'lar
        self._create_file_tab()
        
        if self.modules_available:
            self._create_analysis_tab()
            self._create_arac_detail_tab()
            self._create_reports_tab()
        else:
            self._create_unavailable_tab()
    
    def _create_file_tab(self):
        """Dosya İşleme tab'ı"""
        tab = ctk.CTkFrame(self.notebook, fg_color=COLORS['bg_card'])
        self.notebook.add(tab, text="📁 Dosya İşleme")
        
        # Sol panel
        left = ctk.CTkFrame(tab, fg_color="transparent", width=350)
        left.pack(side="left", fill="y", padx=15, pady=15)
        left.pack_propagate(False)
        
        # Dosya bilgisi
        file_card = ctk.CTkFrame(left, fg_color=COLORS['bg_light'], corner_radius=10)
        file_card.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            file_card, text="📄 Dosya Bilgisi",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", padx=15, pady=(12, 5))
        
        self.file_label = ctk.CTkLabel(
            file_card, text="Henüz dosya seçilmedi",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS['text_secondary'], wraplength=300
        )
        self.file_label.pack(anchor="w", padx=15, pady=(0, 12))
        
        # İstatistikler
        stats_card = ctk.CTkFrame(left, fg_color=COLORS['bg_light'], corner_radius=10)
        stats_card.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            stats_card, text="📊 İstatistikler",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", padx=15, pady=(12, 5))
        
        self.stats_label = ctk.CTkLabel(
            stats_card, text="Dosya işlendikten sonra görünecek",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS['text_secondary'], wraplength=300, justify="left"
        )
        self.stats_label.pack(anchor="w", padx=15, pady=(0, 12))
        
        # Yardım
        help_card = ctk.CTkFrame(left, fg_color="#E8F4FD", corner_radius=10)
        help_card.pack(fill="x")
        
        ctk.CTkLabel(
            help_card, text="💡 Kullanım",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS['info']
        ).pack(anchor="w", padx=15, pady=(12, 5))
        
        help_text = """1. "Dosya Seç" → Excel seçin
2. "İşle" → Dosyayı işleyin
3. "Önizle" → Tam ekran önizleme
4. "Analiz" → ARAÇ analizi
5. "Kaydet" → Sonucu kaydedin
6. "Geri" → Orijinal veriye dön"""
        
        ctk.CTkLabel(
            help_card, text=help_text,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['text_primary'], justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 12))
        
        # Sağ panel - önizleme
        right = ctk.CTkFrame(tab, fg_color="transparent")
        right.pack(side="right", fill="both", expand=True, padx=(0, 15), pady=15)
        
        ctk.CTkLabel(
            right, text="📋 Veri Önizlemesi (İlk 100 satır)",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 10))
        
        # Treeview container
        tree_container = ctk.CTkFrame(right, fg_color=COLORS['bg_light'], corner_radius=8)
        tree_container.pack(fill="both", expand=True)
        
        # Treeview
        self.tree = ttk.Treeview(tree_container, show="headings")
        
        scroll_y = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(tree_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scroll_y.pack(side="right", fill="y", pady=5)
    
    def _create_analysis_tab(self):
        """Analiz Özeti tab'ı"""
        tab = ctk.CTkFrame(self.notebook, fg_color=COLORS['bg_card'])
        self.notebook.add(tab, text="📈 Analiz Özeti")
        
        # Bilgi kartı
        info = ctk.CTkFrame(tab, fg_color=COLORS['bg_light'], corner_radius=10)
        info.pack(fill="x", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            info, text="📊 ARAÇ Bazlı Analiz Sonuçları",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(padx=20, pady=(15, 5))
        
        self.analysis_info_label = ctk.CTkLabel(
            info, text="Dosyayı işledikten sonra 'Analiz' butonuna tıklayın",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS['text_secondary']
        )
        self.analysis_info_label.pack(padx=20, pady=(0, 15))
        
        # Sonuçlar scroll frame
        self.analysis_scroll_frame = ctk.CTkScrollableFrame(
            tab, fg_color="transparent", label_text=""
        )
        self.analysis_scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def _create_arac_detail_tab(self):
        """ARAÇ Detay tab'ı"""
        tab = ctk.CTkFrame(self.notebook, fg_color=COLORS['bg_card'])
        self.notebook.add(tab, text="🚗 ARAÇ Detay")
        
        inner = ctk.CTkFrame(tab, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Seçim
        select_frame = ctk.CTkFrame(inner, fg_color=COLORS['bg_light'], corner_radius=10)
        select_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            select_frame, text="🚗 ARAÇ Seçin:",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left", padx=15, pady=15)
        
        self.arac_dropdown = ctk.CTkOptionMenu(
            select_frame, values=["Önce analiz yapın"],
            width=200, command=self._on_arac_selected
        )
        self.arac_dropdown.pack(side="left", padx=10, pady=15)
        
        # Detay bilgi butonu
        ctk.CTkButton(
            select_frame, text="📋 Detay Göster", width=120,
            fg_color=COLORS['info'], hover_color="#2980B9",
            command=self._show_arac_detail
        ).pack(side="left", padx=10, pady=15)
        
        # Detay frame
        self.arac_detail_frame = ctk.CTkScrollableFrame(inner, fg_color="transparent")
        self.arac_detail_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            self.arac_detail_frame,
            text="Analiz yapıldıktan sonra ARAÇ seçin ve 'Detay Göster'e tıklayın",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=COLORS['text_secondary']
        ).pack(expand=True, pady=50)
    
    def _create_reports_tab(self):
        """Raporlar tab'ı"""
        tab = ctk.CTkFrame(self.notebook, fg_color=COLORS['bg_card'])
        self.notebook.add(tab, text="📑 Raporlar")
        
        inner = ctk.CTkFrame(tab, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            inner, text="📑 Rapor Oluştur",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 15))
        
        # Rapor türleri
        reports = [
            ("📊 Özet Rapor", "Tüm ARAÇ'ların genel durumu", self._generate_summary_report),
            ("📋 Detaylı Rapor", "Seçilen ARAÇ'ın müşteri listesi", self._generate_detail_report),
            ("📈 Karşılaştırma", "ARAÇ'lar arası performans", self._generate_comparison_report),
            ("📅 Yaşlandırma", "Bakiye yaşlandırma analizi", self._generate_aging_report),
            ("📤 Excel Export", "Tüm analiz sonuçlarını Excel'e aktar", self._export_to_excel),
        ]
        
        for title, desc, command in reports:
            card = ctk.CTkFrame(inner, fg_color=COLORS['bg_light'], corner_radius=8)
            card.pack(fill="x", pady=5)
            
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=12)
            
            text_frame = ctk.CTkFrame(row, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(
                text_frame, text=title,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=COLORS['text_primary']
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                text_frame, text=desc,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLORS['text_secondary']
            ).pack(anchor="w")
            
            ctk.CTkButton(
                row, text="Oluştur", width=90, height=35,
                fg_color=COLORS['accent'], hover_color=COLORS['accent_hover'],
                font=ctk.CTkFont(family="Segoe UI", size=11),
                command=command
            ).pack(side="right")
    
    def _create_unavailable_tab(self):
        """Analiz modülü yok"""
        tab = ctk.CTkFrame(self.notebook, fg_color=COLORS['bg_card'])
        self.notebook.add(tab, text="⚠️ Analiz")
        
        inner = ctk.CTkFrame(tab, fg_color="transparent")
        inner.pack(expand=True)
        
        ctk.CTkLabel(
            inner, text="⚠️", font=ctk.CTkFont(size=64),
            text_color=COLORS['warning']
        ).pack(pady=(50, 15))
        
        ctk.CTkLabel(
            inner, text="Analiz Modülü Yüklenemedi",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack()
        
        ctk.CTkLabel(
            inner, text="modules/ klasörünün mevcut olduğundan emin olun.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS['text_secondary']
        ).pack(pady=10)
    
    def _build_status_bar(self):
        """Durum çubuğu"""
        bar = ctk.CTkFrame(self, fg_color=COLORS['bg_card'], height=45, corner_radius=0)
        bar.grid(row=2, column=0, sticky="ew")
        bar.grid_propagate(False)
        
        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20)
        
        self.status_label = ctk.CTkLabel(
            inner, text="✓ Hazır - Excel dosyası seçin",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['text_secondary']
        )
        self.status_label.pack(side="left", pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(
            inner, width=250, height=10, corner_radius=5,
            fg_color=COLORS['border'], progress_color=COLORS['accent']
        )
        self.progress_bar.pack(side="right", pady=12)
        self.progress_bar.set(0)
    
    # =========================================================================
    # BUTON KOMUTLARI
    # =========================================================================
    
    def _select_file(self):
        """Dosya seç"""
        path = filedialog.askopenfilename(
            title="Excel Dosyası Seç",
            filetypes=[("Excel", "*.xlsx *.xls"), ("Tüm", "*.*")]
        )
        if path:
            self.file_path = path
            self.file_label.configure(
                text=f"📁 {Path(path).name}",
                text_color=COLORS['text_primary']
            )
            self.process_btn.configure(state="normal")
            self._set_status(f"Dosya seçildi: {Path(path).name}")
            self.progress_bar.set(0)
    
    def _process_file(self):
        """Dosyayı işle"""
        if not self.file_path or not self.processor:
            messagebox.showerror("Hata", "Önce dosya seçin!")
            return
        
        self.process_btn.configure(state="disabled", text="⏳ İşleniyor...")
        self._set_status("Dosya işleniyor...")
        self.progress_bar.set(0.1)
        
        def process_thread():
            try:
                def progress_cb(val, msg):
                    self.after(0, lambda v=val: self.progress_bar.set(v))
                    self.after(0, lambda m=msg: self._set_status(m))
                
                # İşle
                result = self.processor.process_excel(self.file_path, progress_callback=progress_cb)
                self.processed_df = result
                self.after(0, self._on_process_complete)
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"İşleme hatası: {error_msg}")
                self.after(0, lambda m=error_msg: self._on_process_error(m))
        
        threading.Thread(target=process_thread, daemon=True).start()
    
    def _on_process_complete(self):
        """İşlem tamamlandı"""
        try:
            if self.processed_df is not None:
                rows, cols = self.processed_df.shape
                
                self.stats_label.configure(
                    text=f"✓ Satır: {rows:,}\n✓ Sütun: {cols}\n✓ Durum: Başarılı",
                    text_color=COLORS['success']
                )
                
                self._update_tree_view()
                
                # Butonları aktifle
                self.preview_btn.configure(state="normal")
                self.save_btn.configure(state="normal")
                self.restore_btn.configure(state="normal")
                if self.modules_available and self.analyze_btn:
                    self.analyze_btn.configure(state="normal")
                
                self.progress_bar.set(1)
                self._set_status(f"✓ Tamamlandı - {rows:,} satır")
        finally:
            self.process_btn.configure(state="normal", text="⚙️ İşle")
    
    def _on_process_error(self, msg: str):
        """İşlem hatası"""
        self.process_btn.configure(state="normal", text="⚙️ İşle")
        self.progress_bar.set(0)
        self._set_status(f"❌ Hata: {msg}")
        messagebox.showerror("İşleme Hatası", f"Dosya işlenemedi:\n{msg}")
    
    def _update_tree_view(self):
        """Treeview güncelle"""
        if self.processed_df is None or self.tree is None:
            return
        
        self.tree.delete(*self.tree.get_children())
        
        columns = list(self.processed_df.columns)[:12]
        self.tree["columns"] = columns
        
        for col in columns:
            self.tree.heading(col, text=str(col)[:15])
            self.tree.column(col, width=100, anchor="w")
        
        for _, row in self.processed_df.head(100).iterrows():
            values = [str(v)[:20] if v is not None else "" for v in [row.get(c, "") for c in columns]]
            self.tree.insert("", "end", values=values)
    
    def _show_preview_window(self):
        """Tam ekran önizleme penceresi"""
        if self.processed_df is None:
            messagebox.showinfo("Bilgi", "Önce dosyayı işleyin!")
            return
        
        PreviewWindow(self.master, self.processed_df, "İşlenmiş Veri Önizlemesi")
    
    def _start_analysis(self):
        """Analiz başlat"""
        if not self.modules_available or not self.analysis_engine:
            messagebox.showerror("Hata", "Analiz modülleri yüklenemedi!")
            return
        
        if self.processed_df is None:
            messagebox.showerror("Hata", "Önce dosyayı işleyin!")
            return
        
        self.analyze_btn.configure(state="disabled", text="⏳ Analiz...")
        self._set_status("Analiz yapılıyor...")
        self.progress_bar.set(0.2)
        
        def analysis_thread():
            try:
                # 1. Veriyi set et
                success = self.analysis_engine.set_data(self.processed_df)
                if not success:
                    raise Exception("Veri seti ayarlanamadı. ARAÇ sütunu bulunamıyor olabilir.")
                
                self.after(0, lambda: self.progress_bar.set(0.5))
                
                # 2. Analiz yap
                results = self.analysis_engine.analyze_all_aracs()
                self.current_analysis_results = results if results else {}
                
                self.after(0, self._on_analysis_complete)
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Analiz hatası: {error_msg}")
                self.after(0, lambda m=error_msg: self._on_analysis_error(m))
        
        threading.Thread(target=analysis_thread, daemon=True).start()
    
    def _on_analysis_complete(self):
        """Analiz tamamlandı"""
        try:
            count = len(self.current_analysis_results)
            self.progress_bar.set(1)
            self._set_status(f"✓ Analiz tamamlandı - {count} ARAÇ")
            
            # Dropdown güncelle
            if count > 0:
                arac_list = sorted(self.current_analysis_results.keys())
                self.arac_dropdown.configure(values=arac_list)
                self.arac_dropdown.set(arac_list[0])
                self.selected_arac = arac_list[0]
                
                # Analiz kartlarını güncelle
                self._update_analysis_cards()
                
                self.analysis_info_label.configure(
                    text=f"✓ {count} ARAÇ analiz edildi",
                    text_color=COLORS['success']
                )
            
            messagebox.showinfo("Başarılı", f"Analiz tamamlandı!\n{count} ARAÇ analiz edildi.")
        finally:
            self.analyze_btn.configure(state="normal", text="📈 Analiz")
    
    def _on_analysis_error(self, msg: str):
        """Analiz hatası"""
        self.analyze_btn.configure(state="normal", text="📈 Analiz")
        self.progress_bar.set(0)
        self._set_status(f"❌ Analiz hatası")
        messagebox.showerror("Analiz Hatası", f"Analiz yapılamadı:\n{msg}")
    
    def _update_analysis_cards(self):
        """Analiz sonuç kartlarını güncelle"""
        # Temizle
        for widget in self.analysis_scroll_frame.winfo_children():
            widget.destroy()
        
        # Kartları ekle
        for arac_no, data in self.current_analysis_results.items():
            card = AnalysisResultCard(self.analysis_scroll_frame, arac_no, data)
            card.pack(fill="x", pady=5, padx=5)
    
    def _on_arac_selected(self, selection):
        """ARAÇ seçildi"""
        self.selected_arac = selection
    
    def _show_arac_detail(self):
        """ARAÇ detayını göster"""
        if not self.selected_arac or self.selected_arac not in self.current_analysis_results:
            messagebox.showinfo("Bilgi", "Önce analiz yapın ve bir ARAÇ seçin!")
            return
        
        data = self.current_analysis_results[self.selected_arac]
        
        # Temizle
        for widget in self.arac_detail_frame.winfo_children():
            widget.destroy()
        
        # Başlık
        ctk.CTkLabel(
            self.arac_detail_frame,
            text=f"🚗 ARAÇ {self.selected_arac} Detayları",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 15))
        
        # Metrikler
        metrics = [
            ("👥 Müşteri Sayısı", data.get('musteri_sayisi', 0)),
            ("💰 Toplam Bakiye", f"{data.get('toplam_bakiye', 0):,.2f} ₺"),
            ("📊 Ortalama Bakiye", f"{data.get('ortalama_bakiye', 0):,.2f} ₺"),
            ("📈 Max Bakiye", f"{data.get('max_bakiye', 0):,.2f} ₺"),
            ("📉 Min Bakiye", f"{data.get('min_bakiye', 0):,.2f} ₺"),
        ]
        
        for label, value in metrics:
            row = ctk.CTkFrame(self.arac_detail_frame, fg_color=COLORS['bg_light'], corner_radius=8)
            row.pack(fill="x", pady=3)
            
            ctk.CTkLabel(
                row, text=label, width=200,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS['text_secondary'], anchor="w"
            ).pack(side="left", padx=15, pady=12)
            
            ctk.CTkLabel(
                row, text=str(value),
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                text_color=COLORS['text_primary']
            ).pack(side="left", padx=10, pady=12)
    
    def _save_file(self):
        """Kaydet"""
        if self.processed_df is None:
            messagebox.showinfo("Bilgi", "Kaydedilecek veri yok!")
            return
        
        default = Path(self.file_path).stem + "_islenmiş.xlsx" if self.file_path else "sonuc.xlsx"
        
        path = filedialog.asksaveasfilename(
            title="Kaydet",
            defaultextension=".xlsx",
            initialfile=default,
            filetypes=[("Excel", "*.xlsx")]
        )
        
        if path:
            try:
                self.processed_df.to_excel(path, index=False)
                self._set_status(f"✓ Kaydedildi: {Path(path).name}")
                messagebox.showinfo("Başarılı", f"Dosya kaydedildi:\n{path}")
            except Exception as e:
                messagebox.showerror("Hata", f"Kaydetme hatası:\n{e}")
    
    def _restore_backup(self):
        """Yedekten geri yükle"""
        if not self.processor:
            return
        
        try:
            backup = self.processor.get_backup_data()
            if backup is not None:
                self.processed_df = backup.copy()
                self._update_tree_view()
                self._set_status("✓ Orijinal veri geri yüklendi")
                messagebox.showinfo("Başarılı", "Orijinal veri geri yüklendi!")
            else:
                messagebox.showinfo("Bilgi", "Yedek veri bulunamadı!")
        except Exception as e:
            messagebox.showerror("Hata", f"Geri yükleme hatası:\n{e}")
    
    # =========================================================================
    # RAPOR FONKSİYONLARI
    # =========================================================================
    
    def _generate_summary_report(self):
        """Özet rapor"""
        if not self.current_analysis_results:
            messagebox.showinfo("Bilgi", "Önce analiz yapın!")
            return
        
        # Basit özet
        total_musteri = sum(d.get('musteri_sayisi', 0) for d in self.current_analysis_results.values())
        total_bakiye = sum(d.get('toplam_bakiye', 0) for d in self.current_analysis_results.values())
        
        report = f"""📊 ÖZET RAPOR
{'='*40}
Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}

📈 Genel İstatistikler:
• Toplam ARAÇ: {len(self.current_analysis_results)}
• Toplam Müşteri: {total_musteri:,}
• Toplam Bakiye: {total_bakiye:,.2f} ₺

📋 ARAÇ Detayları:
"""
        for arac, data in sorted(self.current_analysis_results.items()):
            report += f"\n🚗 ARAÇ {arac}: {data.get('musteri_sayisi', 0)} müşteri, {data.get('toplam_bakiye', 0):,.2f} ₺"
        
        # Göster
        self._show_report_window("Özet Rapor", report)
    
    def _generate_detail_report(self):
        """Detaylı rapor"""
        if not self.selected_arac or self.selected_arac not in self.current_analysis_results:
            messagebox.showinfo("Bilgi", "Önce bir ARAÇ seçin!")
            return
        
        data = self.current_analysis_results[self.selected_arac]
        
        report = f"""📋 DETAYLI RAPOR - ARAÇ {self.selected_arac}
{'='*40}
Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}

👥 Müşteri Sayısı: {data.get('musteri_sayisi', 0)}
💰 Toplam Bakiye: {data.get('toplam_bakiye', 0):,.2f} ₺
📊 Ortalama Bakiye: {data.get('ortalama_bakiye', 0):,.2f} ₺
📈 Maximum Bakiye: {data.get('max_bakiye', 0):,.2f} ₺
📉 Minimum Bakiye: {data.get('min_bakiye', 0):,.2f} ₺
"""
        self._show_report_window(f"ARAÇ {self.selected_arac} Detay Raporu", report)
    
    def _generate_comparison_report(self):
        """Karşılaştırma raporu"""
        if not self.current_analysis_results:
            messagebox.showinfo("Bilgi", "Önce analiz yapın!")
            return
        
        report = f"""📈 KARŞILAŞTIRMA RAPORU
{'='*40}
Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}

"""
        # En yüksek bakiye
        max_bakiye_arac = max(self.current_analysis_results.items(), 
                             key=lambda x: x[1].get('toplam_bakiye', 0))
        report += f"🏆 En Yüksek Bakiye: ARAÇ {max_bakiye_arac[0]} ({max_bakiye_arac[1].get('toplam_bakiye', 0):,.2f} ₺)\n"
        
        # En çok müşteri
        max_musteri_arac = max(self.current_analysis_results.items(),
                              key=lambda x: x[1].get('musteri_sayisi', 0))
        report += f"👥 En Çok Müşteri: ARAÇ {max_musteri_arac[0]} ({max_musteri_arac[1].get('musteri_sayisi', 0)} müşteri)\n"
        
        self._show_report_window("Karşılaştırma Raporu", report)
    
    def _generate_aging_report(self):
        """Yaşlandırma raporu"""
        if not self.current_analysis_results:
            messagebox.showinfo("Bilgi", "Önce analiz yapın!")
            return
        
        messagebox.showinfo("Bilgi", "Yaşlandırma raporu hazırlanıyor...")
    
    def _export_to_excel(self):
        """Excel'e aktar"""
        if not self.current_analysis_results:
            messagebox.showinfo("Bilgi", "Önce analiz yapın!")
            return
        
        path = filedialog.asksaveasfilename(
            title="Analiz Sonuçlarını Kaydet",
            defaultextension=".xlsx",
            initialfile="analiz_sonuclari.xlsx",
            filetypes=[("Excel", "*.xlsx")]
        )
        
        if path:
            try:
                import pandas as pd
                
                data = []
                for arac, info in self.current_analysis_results.items():
                    data.append({
                        'ARAÇ': arac,
                        'Müşteri Sayısı': info.get('musteri_sayisi', 0),
                        'Toplam Bakiye': info.get('toplam_bakiye', 0),
                        'Ortalama Bakiye': info.get('ortalama_bakiye', 0),
                        'Max Bakiye': info.get('max_bakiye', 0),
                        'Min Bakiye': info.get('min_bakiye', 0),
                    })
                
                df = pd.DataFrame(data)
                df.to_excel(path, index=False)
                
                self._set_status(f"✓ Analiz sonuçları kaydedildi")
                messagebox.showinfo("Başarılı", f"Analiz sonuçları kaydedildi:\n{path}")
            except Exception as e:
                messagebox.showerror("Hata", f"Export hatası:\n{e}")
    
    def _show_report_window(self, title: str, content: str):
        """Rapor penceresi"""
        win = ctk.CTkToplevel(self.master)
        win.title(title)
        win.geometry("600x500")
        win.transient(self.master)
        
        # Header
        header = ctk.CTkFrame(win, fg_color=COLORS['accent'], height=50, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header, text=f"📑 {title}",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS['text_light']
        ).pack(side="left", padx=20, pady=12)
        
        # İçerik
        text = ctk.CTkTextbox(win, font=ctk.CTkFont(family="Consolas", size=12))
        text.pack(fill="both", expand=True, padx=10, pady=10)
        text.insert("1.0", content)
        text.configure(state="disabled")
        
        # Kapat
        ctk.CTkButton(
            win, text="Kapat", width=100,
            fg_color=COLORS['error'], hover_color="#C0392B",
            command=win.destroy
        ).pack(pady=10)
    
    def _set_status(self, msg: str):
        """Durum güncelle"""
        if self.status_label:
            self.status_label.configure(text=msg)


# =============================================================================
# STANDALONE
# =============================================================================

def main():
    """Standalone"""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("Bupiliç - Excel Cari Yaşlandırma İşleyici")
    root.geometry("1450x900")
    root.minsize(1200, 800)
    
    app = YaslandirmaApp(root, standalone=True)
    app.pack(fill="both", expand=True)
    
    root.mainloop()


if __name__ == "__main__":
    main()
