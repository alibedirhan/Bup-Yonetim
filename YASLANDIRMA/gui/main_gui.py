#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - Ana GUI Sınıfı (Modüler)
Temizlenmiş ve modüler yapıya dönüştürülmüş ana GUI sınıfı
"""

import os
import sys
from pathlib import Path

# Modül dizinlerini path'e ekle
_gui_dir = Path(__file__).parent
_yaslandirma_dir = _gui_dir.parent
if str(_yaslandirma_dir) not in sys.path:
    sys.path.insert(0, str(_yaslandirma_dir))
if str(_gui_dir) not in sys.path:
    sys.path.insert(0, str(_gui_dir))

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
import pandas as pd
import threading
import logging
from datetime import datetime
import tkinter as tk

# Ana modül importları - frozen mode için düzeltme
try:
    from ..excel_processor import ExcelProcessor, ExcelProcessorError
    from ..utils import format_number_display
except ImportError:
    try:
        from YASLANDIRMA.excel_processor import ExcelProcessor, ExcelProcessorError
        from YASLANDIRMA.utils import format_number_display
    except ImportError:
        from excel_processor import ExcelProcessor, ExcelProcessorError
        from utils import format_number_display

# GUI modüllerini import et - frozen mode için düzeltme
try:
    from .file_tab import create_file_processing_tab
    from .analysis_tabs import create_analysis_overview_tab, create_arac_detail_tab
    from .other_tabs import create_assignment_tab, create_reports_tab, create_charts_tab
    from .ui_helpers import (
        ToolTip, add_tooltip, ProgressManager, ThreadedAnalysis,
        show_help_dialog, show_about_dialog, show_quick_help, show_keyboard_shortcuts
    )
    from .tab_methods import TabMethods
    from .file_operations import FileOperations
    from .analysis_operations import AnalysisOperations
except ImportError:
    try:
        from YASLANDIRMA.gui.file_tab import create_file_processing_tab
        from YASLANDIRMA.gui.analysis_tabs import create_analysis_overview_tab, create_arac_detail_tab
        from YASLANDIRMA.gui.other_tabs import create_assignment_tab, create_reports_tab, create_charts_tab
        from YASLANDIRMA.gui.ui_helpers import (
            ToolTip, add_tooltip, ProgressManager, ThreadedAnalysis,
            show_help_dialog, show_about_dialog, show_quick_help, show_keyboard_shortcuts
        )
        from YASLANDIRMA.gui.tab_methods import TabMethods
        from YASLANDIRMA.gui.file_operations import FileOperations
        from YASLANDIRMA.gui.analysis_operations import AnalysisOperations
    except ImportError:
        from file_tab import create_file_processing_tab
        from analysis_tabs import create_analysis_overview_tab, create_arac_detail_tab
        from other_tabs import create_assignment_tab, create_reports_tab, create_charts_tab
        from ui_helpers import (
            ToolTip, add_tooltip, ProgressManager, ThreadedAnalysis,
            show_help_dialog, show_about_dialog, show_quick_help, show_keyboard_shortcuts
        )
        from tab_methods import TabMethods
        from file_operations import FileOperations
        from analysis_operations import AnalysisOperations

# Analiz modülü import
try:
    sys.path.insert(0, str(_yaslandirma_dir / 'modules'))
    try:
        from ..modules.analysis import AnalysisEngine
        from ..modules.assignment import AssignmentManager
        from ..modules.data_manager import DataManager
        from ..modules.reports import ReportGenerator
        from ..modules.visualization import VisualizationEngine
    except ImportError:
        try:
            from YASLANDIRMA.modules.analysis import AnalysisEngine
            from YASLANDIRMA.modules.assignment import AssignmentManager
            from YASLANDIRMA.modules.data_manager import DataManager
            from YASLANDIRMA.modules.reports import ReportGenerator
            from YASLANDIRMA.modules.visualization import VisualizationEngine
        except ImportError:
            from analysis import AnalysisEngine
            from assignment import AssignmentManager
            from data_manager import DataManager
            from reports import ReportGenerator
            from visualization import VisualizationEngine
    ANALYSIS_MODULE_AVAILABLE = True
except ImportError as e:
    ANALYSIS_MODULE_AVAILABLE = False
    print(f"Analiz modülü yüklenemedi: {e}")

logger = logging.getLogger(__name__)

# Tema ayarları
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ExcelProcessorGUI(TabMethods, FileOperations, AnalysisOperations):
    """Ana GUI sınıfı - Modüler yapı"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Excel Cari Yaşlandırma İşleyici - v2.0 (Modüler)")
        self.root.geometry("1600x900")
        
        # Icon ayarla (varsa)
        try:
            if Path("icon.ico").exists():
                self.root.iconbitmap("icon.ico")
        except Exception as e:
            logger.debug(f"Icon yüklenemedi: {e}")
        
        # Değişkenler
        self.file_path = None
        self.processed_df = None
        self.processor = ExcelProcessor()
        
        # Analiz modülü değişkenleri
        if ANALYSIS_MODULE_AVAILABLE:
            self.init_analysis_modules()
        
        # UI komponentlerini önce tanımla
        self.init_ui_components()
        
        # UI oluştur
        self.setup_ui()
        
        # Analiz verilerini yükle
        if ANALYSIS_MODULE_AVAILABLE:
            self.load_saved_analysis_data()
        
        # Uygulama kapanırken cleanup
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.setup_enhancements()
        self.setup_keyboard_shortcuts()
    
    def init_analysis_modules(self):
        """Analiz modüllerini başlat"""
        self.analysis_engine = AnalysisEngine()
        self.assignment_manager = AssignmentManager()
        self.data_manager = DataManager()
        self.report_generator = ReportGenerator()
        self.visualization_engine = VisualizationEngine()
        self.current_analysis_results = {}
        self.current_assignments = {}
        self.selected_arac = None
    
    def init_ui_components(self):
        """UI komponentlerini başlat"""
        self.main_status_label = None
        self.analysis_indicator = None
        self.progress = None
        self.status_label = None
        self.file_label = None
        self.stats_label = None
        self.process_btn = None
        self.preview_btn = None
        self.save_btn = None
        self.restore_btn = None
        self.analyze_btn = None
        self.tree = None
        self.notebook = None
        self.select_btn = None

        if ANALYSIS_MODULE_AVAILABLE:
            self.report_type_var = None
            self.report_all_arac_var = None
            self.current_report_df = None
            self.current_chart_figure = None    
            self.arac_selection_frame = None
            self.arac_checkboxes = {}
            self.report_tree = None
            self.report_status_label = None
            self.generate_report_btn = None
            self.export_report_btn = None
            self.chart_type_var = None
            self.chart_arac_dropdown = None
            self.create_chart_btn = None
            self.save_chart_btn = None
            self.chart_display_frame = None
            self.chart_placeholder_label = None
    
    def setup_ui(self):
        """Ana UI yapısını oluştur"""
        try:
            # Ana container
            main_container = ctk.CTkFrame(self.root)
            main_container.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Üst panel (kontroller)
            self.setup_top_panel(main_container)
            
            # Alt panel (notebook - analiz entegre)
            self.setup_main_notebook(main_container)
            
            # Durum çubuğu
            self.setup_status_bar(main_container)
            
        except Exception as e:
            logger.error(f"UI oluşturma hatası: {e}")
            messagebox.showerror("Hata", f"Arayüz oluşturulamadı: {e}")
    
    def setup_top_panel(self, parent):
        """Üst kontrol panelini oluştur - TOOLTIP'Lİ VERSİYON"""
        top_frame = ctk.CTkFrame(parent, height=80)
        top_frame.pack(fill="x", padx=5, pady=5)
        top_frame.pack_propagate(False)
        
        # Başlık
        title = ctk.CTkLabel(
            top_frame, 
            text="Excel Cari Yaşlandırma İşleyici & ARAÇ Analiz Sistemi",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(side="left", padx=20, pady=20)
        
        # Butonlar frame
        buttons_frame = ctk.CTkFrame(top_frame)
        buttons_frame.pack(side="right", padx=20, pady=10)
        
        button_style = {
            "height": 40,
            "font": ctk.CTkFont(size=12, weight="bold"),
            "corner_radius": 8
        }
        
        # Dosya Seç butonu + Tooltip
        self.select_btn = ctk.CTkButton(
            buttons_frame,
            text="Dosya Seç",
            command=self.select_file,
            **button_style
        )
        self.select_btn.pack(side="left", padx=5)
        add_tooltip(self.select_btn, 
            "Excel dosyası seçin\n(.xlsx veya .xls formatında)\n\nCari yaşlandırma raporu formatında olmalıdır")
        
        # İşleme Başla butonu + Tooltip
        self.process_btn = ctk.CTkButton(
            buttons_frame,
            text="İşleme Başla",
            command=self.process_file,
            state="disabled",
            **button_style
        )
        self.process_btn.pack(side="left", padx=5)
        add_tooltip(self.process_btn,
            "Excel dosyasını işlemeye başla\n\n• İlk 2 satır silinir\n• Veri temizlenir\n• Kategoriler düzenlenir")
        
        # Analiz Başlat butonu + Tooltip (sadece analiz modülü varsa)
        if ANALYSIS_MODULE_AVAILABLE:
            self.analyze_btn = ctk.CTkButton(
                buttons_frame,
                text="Analiz Başlat",
                command=self.start_analysis,
                state="disabled",
                fg_color=("#FF6B35", "#FF8C42"),
                hover_color=("#E55A2B", "#E67832"),
                **button_style
            )
            self.analyze_btn.pack(side="left", padx=5)
            add_tooltip(self.analyze_btn,
                "ARAÇ bazlı analiz başlat\n\n• Her ARAÇ için müşteri analizi\n• Bakiye hesaplaması\n• Yaşlandırma analizi")
        
        # Kaydet butonu + Tooltip
        self.save_btn = ctk.CTkButton(
            buttons_frame,
            text="Kaydet",
            command=self.save_file,
            state="disabled",
            fg_color="green",
            hover_color="dark green",
            **button_style
        )
        self.save_btn.pack(side="left", padx=5)
        add_tooltip(self.save_btn,
            "İşlenmiş veriyi Excel dosyası olarak kaydet\n\nOrijinal dosya değişmez")
    
    def setup_main_notebook(self, parent):
        """Ana notebook panelini oluştur (analiz entegre)"""
        # Notebook
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Tab'ları oluştur
        create_file_processing_tab(self.notebook, self)
        
        if ANALYSIS_MODULE_AVAILABLE:
            create_analysis_overview_tab(self.notebook, self)
            create_arac_detail_tab(self.notebook, self)
            create_assignment_tab(self.notebook, self)
            create_reports_tab(self.notebook, self)
            create_charts_tab(self.notebook, self)
        else:
            self.create_analysis_unavailable_tab()
    
    def setup_status_bar(self, parent):
        """Durum çubuğunu oluştur"""
        status_frame = ctk.CTkFrame(parent, height=30)
        status_frame.pack(fill="x", side="bottom", padx=5, pady=5)
        status_frame.pack_propagate(False)
        
        self.main_status_label = ctk.CTkLabel(
            status_frame,
            text="Hazır - Excel dosyası seçin",
            font=ctk.CTkFont(size=12)
        )
        self.main_status_label.pack(side="left", padx=10, pady=5)
        
        # Analiz durumu (varsa)
        if ANALYSIS_MODULE_AVAILABLE:
            self.analysis_indicator = ctk.CTkLabel(
                status_frame,
                text="Analiz: Hazır",
                font=ctk.CTkFont(size=12),
                text_color="green"
            )
            self.analysis_indicator.pack(side="right", padx=10, pady=5)
    
    def create_analysis_unavailable_tab(self):
        """Analiz modülü mevcut değil tab'ı"""
        unavailable_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(unavailable_frame, text="Analiz Modülü")
        
        # Uyarı mesajı
        warning_frame = ctk.CTkFrame(unavailable_frame, fg_color=("orange", "dark orange"))
        warning_frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        ctk.CTkLabel(
            warning_frame,
            text="Analiz Modülü Yüklenemedi",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        ).pack(pady=20)
        
        ctk.CTkLabel(
            warning_frame,
            text="Analiz özellikleri kullanılamaz.\n\nLütfen modules/ klasörünün ve tüm modül dosyalarının\nmevcut olduğundan emin olun.",
            font=ctk.CTkFont(size=14),
            text_color="white",
            justify="center"
        ).pack(pady=20)
    
    def setup_treeview_style(self):
        """Treeview stilini ayarla"""
        try:
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("Treeview", 
                           background="#2b2b2b",
                           foreground="white",
                           fieldbackground="#2b2b2b",
                           rowheight=25)
            style.configure("Treeview.Heading",
                           background="#1f538d",
                           foreground="white",
                           font=('Arial', 10, 'bold'))
            style.map("Treeview", background=[("selected", "#1f538d")])
        except Exception as e:
            logger.warning(f"Treeview stil ayarlanamadı: {e}")
    
    def setup_enhancements(self):
        """GUI iyileştirmelerini kur"""
        # Progress manager'ı başlat
        if hasattr(self, 'progress') and hasattr(self, 'status_label'):
            self.progress_manager = ProgressManager(self.progress, self.status_label)
    
    def setup_keyboard_shortcuts(self):
        """Klavye kısayollarını ayarla"""
        try:
            # Dosya işlemleri
            self.root.bind("<Control-o>", lambda e: self.select_file())
            self.root.bind("<Control-s>", lambda e: self.save_file() if self.save_btn.cget("state") == "normal" else None)
            self.root.bind("<F5>", lambda e: self.process_file() if self.process_btn.cget("state") == "normal" else None)
            
            # Analiz işlemleri
            if ANALYSIS_MODULE_AVAILABLE:
                self.root.bind("<Control-a>", lambda e: self.start_analysis() if self.analyze_btn.cget("state") == "normal" else None)
            
            # Tab geçişleri
            self.root.bind("<Control-KeyPress-1>", lambda e: self.notebook.select(0))
            if ANALYSIS_MODULE_AVAILABLE:
                for i in range(2, 7):
                    self.root.bind(f"<Control-KeyPress-{i}>", lambda e, idx=i-1: self.notebook.select(idx))
            
            # Yardım
            self.root.bind("<F1>", lambda e: show_keyboard_shortcuts(self))
            self.root.bind("<Control-h>", lambda e: show_quick_help(self))
            
        except Exception as e:
            logger.error(f"Klavye kısayolu ayarlama hatası: {e}")
    
    def create_menu_bar(self):
        """Menü çubuğu oluştur"""
        try:
            # CustomTkinter ile menü çubuğu yerine buton çubuğu
            menu_frame = ctk.CTkFrame(self.root, height=40)
            menu_frame.pack(fill="x", side="top", before=self.root.winfo_children()[0])
            menu_frame.pack_propagate(False)
            
            # Menü butonları
            menu_style = {"height": 30, "font": ctk.CTkFont(size=12)}
            
            help_btn = ctk.CTkButton(
                menu_frame,
                text="Yardım",
                command=lambda: show_help_dialog(self.root),
                width=80,
                **menu_style
            )
            help_btn.pack(side="right", padx=5, pady=5)
            
            about_btn = ctk.CTkButton(
                menu_frame,
                text="Hakkında", 
                command=lambda: show_about_dialog(self.root),
                width=80,
                **menu_style
            )
            about_btn.pack(side="right", padx=5, pady=5)
            
            # Ana başlık
            app_title = ctk.CTkLabel(
                menu_frame,
                text="Excel Cari Yaşlandırma İşleyici & ARAÇ Analiz Sistemi v2.0",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            app_title.pack(side="left", padx=10, pady=5)
            
        except Exception as e:
            logger.error(f"Menü çubuğu oluşturma hatası: {e}")
    
    def on_closing(self):
        """Uygulama kapanırken çağrılır"""
        try:
            # Analiz verilerini kaydet (eğer varsa)
            if ANALYSIS_MODULE_AVAILABLE and hasattr(self, 'current_analysis_results') and self.current_analysis_results:
                try:
                    settings = self.data_manager.load_settings()
                    if settings.get('auto_save', True):
                        self.save_analysis_data()
                except Exception as save_error:
                    logger.warning(f"Otomatik kaydetme hatası: {save_error}")
            
            # Grafikleri temizle
            if ANALYSIS_MODULE_AVAILABLE and hasattr(self, 'visualization_engine'):
                try:
                    self.visualization_engine.clear_figures()
                except Exception:
                    pass
            
            # Thread'lerin bitmesini bekle
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            logger.error(f"Kapanış hatası: {e}")
    
    def run(self):
        """Uygulamayı başlat"""
        try:
            # Menü çubuğunu oluştur
            self.create_menu_bar()
            
            # Ana loop
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Uygulama çalıştırma hatası: {e}")
            messagebox.showerror("Kritik Hata", f"Uygulama başlatılamadı: {str(e)}")