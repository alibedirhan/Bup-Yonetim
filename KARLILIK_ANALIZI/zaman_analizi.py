# zaman_analizi.py - Düzeltilmiş ve Hatasız Versiyon

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
import threading
import weakref
import json
import queue
import gc
from typing import Optional, Dict, Any, List, Tuple, Callable

# Yeni modül importları
try:
    from ui_components import UIComponents
    UI_COMPONENTS_AVAILABLE = True
except ImportError:
    UI_COMPONENTS_AVAILABLE = False

try:
    from themes import get_colors, get_color, apply_theme_to_app, ThemeType
    THEMES_AVAILABLE = True
except ImportError:
    THEMES_AVAILABLE = False

try:
    from data_operations import JSONOperations, DataValidator, DataCleaner, DataAnalyzer
    DATA_OPERATIONS_AVAILABLE = True
except ImportError:
    DATA_OPERATIONS_AVAILABLE = False

# Optional dependencies - Graceful degradation
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from tkcalendar import DateEntry
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False


class SafeUIComponents:
    """Fallback UI components when ui_components module is not available"""
    
    @staticmethod
    def create_modern_button(parent, text, command, bg_color='#3b82f6', 
                           fg_color='white', padx=20, pady=10, **kwargs):
        """Fallback modern button"""
        try:
            return tk.Button(
                parent, text=text, command=command, bg=bg_color, fg=fg_color,
                relief='flat', bd=0, padx=padx, pady=pady, cursor='hand2',
                font=('Segoe UI', 11, 'bold'), **kwargs
            )
        except Exception:
            return tk.Button(parent, text=text, command=command)
    
    @staticmethod
    def create_section_header(parent, title, bg_color='#3b82f6', **kwargs):
        """Fallback section header"""
        try:
            header = tk.Frame(parent, bg=bg_color, height=60)
            header.pack(fill='x', pady=(0, 20))
            header.pack_propagate(False)
            
            tk.Label(
                header, text=title, font=('Segoe UI', 16, 'bold'),
                fg='white', bg=bg_color
            ).pack(expand=True)
            
            return header
        except Exception:
            return tk.Frame(parent)
    
    @staticmethod
    def create_scrollable_frame(parent, colors=None, **kwargs):
        """Fallback scrollable frame"""
        try:
            canvas = tk.Canvas(parent, highlightthickness=0)
            scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas)
            
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            
            def configure_scroll_region(event=None):
                canvas.configure(scrollregion=canvas.bbox("all"))
            
            scrollable_frame.bind("<Configure>", configure_scroll_region)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            return canvas, scrollable_frame, scrollbar
        except Exception:
            fallback = tk.Frame(parent)
            fallback.pack(fill='both', expand=True)
            return None, fallback, None


class SafeDataOperations:
    """Fallback data operations when data_operations module is not available"""
    
    @staticmethod
    def read_json_safe(file_path):
        """Safe JSON reading"""
        try:
            if not os.path.exists(file_path):
                return {}
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    @staticmethod
    def write_json_safe(data, file_path):
        """Safe JSON writing"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    @staticmethod
    def clean_numeric(value):
        """Clean numeric values"""
        try:
            if pd.isna(value):
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                cleaned = value.replace('₺', '').replace('TL', '').replace(',', '.').strip()
                return float(cleaned)
            return 0.0
        except Exception:
            return 0.0


class ZamanAnalizi:
    """Dönem bazlı analiz ve karşılaştırma modülü - Düzeltilmiş ve Güvenilir Versiyon"""
    
    def __init__(self, parent_notebook):
        """Initialize ZamanAnalizi module with comprehensive error handling"""
        
        # Critical state management
        self._closing = False
        self._initialization_complete = False
        self._initializing_data_file = False
        self._widgets_destroyed = False
        self._cleanup_scheduled = False
        
        # Core attributes
        self.notebook = parent_notebook
        self.data_file = "analiz_gecmisi.json"
        
        # Setup logging with safety
        self._setup_logging()
        
        # Initialize fallback systems
        self._init_fallback_systems()
        
        # Widget references - Initialize all to None
        self._init_widget_references()
        
        # Thread-safe communication
        self.message_queue = queue.Queue()
        self.active_threads = set()
        
        # Cleanup tracking
        self.cleanup_functions = []
        
        try:
            # Initialize the module
            self._safe_init()
        except Exception as e:
            self.logger.error(f"Critical initialization error: {e}")
            self._show_initialization_error(str(e))
    
    def _setup_logging(self):
        """Setup logging with safety checks"""
        try:
            self.logger = logging.getLogger(f"{__name__}_{id(self)}")
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.INFO)
        except Exception:
            # Fallback to print if logging fails
            class FallbackLogger:
                def info(self, msg): print(f"INFO: {msg}")
                def error(self, msg): print(f"ERROR: {msg}")
                def warning(self, msg): print(f"WARNING: {msg}")
                def debug(self, msg): print(f"DEBUG: {msg}")
            self.logger = FallbackLogger()
    
    def _init_fallback_systems(self):
        """Initialize fallback systems"""
        # Color system fallback
        if THEMES_AVAILABLE:
            self.colors = get_colors()
        else:
            self.colors = {
                'bg_primary': '#f8fafc', 'bg_secondary': '#ffffff',
                'primary': '#3b82f6', 'success': '#10b981',
                'warning': '#f59e0b', 'danger': '#ef4444',
                'info': '#06b6d4', 'text_primary': '#1f2937',
                'text_secondary': '#6b7280'
            }
        
        # UI Components fallback
        if UI_COMPONENTS_AVAILABLE:
            self.ui = UIComponents
        else:
            self.ui = SafeUIComponents
        
        # Data operations fallback
        if DATA_OPERATIONS_AVAILABLE:
            self.data_ops = type('DataOps', (), {
                'JSONOperations': JSONOperations,
                'DataValidator': DataValidator,
                'DataCleaner': DataCleaner,
                'DataAnalyzer': DataAnalyzer
            })()
        else:
            self.data_ops = SafeDataOperations
    
    def _init_widget_references(self):
        """Initialize all widget references to None"""
        self.main_frame = None
        self.sub_notebook = None
        self.start_date = None
        self.end_date = None
        self.period_name = None
        self.karlilik_path = None
        self.iskonto_path = None
        self.karlilik_label = None
        self.iskonto_label = None
        self.history_tree = None
        self.period1_combo = None
        self.period2_combo = None
        self.period1_var = None
        self.period2_var = None
        self.comparison_canvas = None
        self.comparison_results_frame = None
        self._widgets = weakref.WeakSet()
    
    def _safe_init(self):
        """Safe initialization with comprehensive error handling"""
        try:
            # Data file initialization
            if not self._init_data_file_safe():
                self.logger.warning("Data file initialization failed, continuing with limited functionality")
            
            # UI setup
            if not self._setup_ui_safe():
                raise Exception("UI setup failed critically")
            
            # Post-initialization tasks
            self._schedule_post_init()
            
            self._initialization_complete = True
            self.logger.info("ZamanAnalizi initialization completed successfully")
            
        except Exception as e:
            self.logger.error(f"Safe initialization failed: {e}")
            raise
    
    def _init_data_file_safe(self):
        """Initialize data file with comprehensive safety"""
        if self._initializing_data_file:
            return False
        
        try:
            self._initializing_data_file = True
            
            data_path = Path(self.data_file)
            
            if not data_path.exists():
                initial_data = {
                    "analizler": [],
                    "son_guncelleme": datetime.now().isoformat(),
                    "version": "1.0"
                }
                
                if hasattr(self.data_ops, 'JSONOperations'):
                    success = self.data_ops.JSONOperations.write_json_safe(initial_data, self.data_file)
                else:
                    success = self.data_ops.write_json_safe(initial_data, self.data_file)
                
                if not success:
                    self.logger.error("Failed to create initial data file")
                    return False
            
            # Validate existing file
            return self._validate_data_file_safe()
            
        except Exception as e:
            self.logger.error(f"Data file initialization error: {e}")
            return False
        finally:
            self._initializing_data_file = False
    
    def _validate_data_file_safe(self):
        """Validate data file with safety checks"""
        try:
            if hasattr(self.data_ops, 'JSONOperations'):
                data = self.data_ops.JSONOperations.read_json_safe(self.data_file)
            else:
                data = self.data_ops.read_json_safe(self.data_file)
            
            if not data:
                return self._create_minimal_data_file()
            
            # Basic structure validation
            if not isinstance(data.get('analizler'), list):
                data['analizler'] = []
                if hasattr(self.data_ops, 'JSONOperations'):
                    self.data_ops.JSONOperations.write_json_safe(data, self.data_file)
                else:
                    self.data_ops.write_json_safe(data, self.data_file)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Data file validation error: {e}")
            return self._create_minimal_data_file()
    
    def _create_minimal_data_file(self):
        """Create minimal working data file"""
        try:
            minimal_data = {
                "analizler": [],
                "son_guncelleme": datetime.now().isoformat(),
                "version": "1.0"
            }
            
            if hasattr(self.data_ops, 'JSONOperations'):
                success = self.data_ops.JSONOperations.write_json_safe(minimal_data, self.data_file)
            else:
                success = self.data_ops.write_json_safe(minimal_data, self.data_file)
            
            return success
        except Exception:
            return False
    
    def _setup_ui_safe(self):
        """Setup UI with comprehensive error handling"""
        try:
            # Create main frame
            self.main_frame = ttk.Frame(self.notebook)
            if not self._check_widget_exists(self.main_frame):
                raise Exception("Failed to create main frame")
            
            self.notebook.add(self.main_frame, text="📅 Dönem Analizi")
            self._widgets.add(self.main_frame)
            
            # Create sub-notebook
            self.sub_notebook = ttk.Notebook(self.main_frame)
            if not self._check_widget_exists(self.sub_notebook):
                raise Exception("Failed to create sub-notebook")
            
            self.sub_notebook.pack(fill='both', expand=True, padx=10, pady=10)
            self._widgets.add(self.sub_notebook)
            
            # Create tabs
            self._create_all_tabs()
            
            return True
            
        except Exception as e:
            self.logger.error(f"UI setup error: {e}")
            return False
    
    def _create_all_tabs(self):
        """Create all tabs with individual error handling"""
        tabs = [
            ("Data Entry", self._create_data_entry_tab),
            ("History", self._create_history_tab),
            ("Comparison", self._create_comparison_tab)
        ]
        
        for tab_name, tab_creator in tabs:
            try:
                tab_creator()
                self.logger.info(f"{tab_name} tab created successfully")
            except Exception as e:
                self.logger.error(f"{tab_name} tab creation failed: {e}")
                self._create_error_tab(tab_name, str(e))
    
    def _create_data_entry_tab(self):
        """Create data entry tab with error handling"""
        try:
            entry_frame = ttk.Frame(self.sub_notebook)
            self.sub_notebook.add(entry_frame, text="📊 Veri Girişi")
            self._widgets.add(entry_frame)
            
            main_container = tk.Frame(entry_frame, bg=self.colors['bg_primary'])
            main_container.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Create sections
            self._create_section_header_safe(main_container, "📅 Yeni Dönem Analizi")
            self._create_date_selection_section_safe(main_container)
            self._create_file_selection_section_safe(main_container)
            self._create_analysis_button_safe(main_container)
            
        except Exception as e:
            self.logger.error(f"Data entry tab creation error: {e}")
            raise
    
    def _create_section_header_safe(self, parent, title):
        """Create section header with safety"""
        try:
            return self.ui.create_section_header(parent, title, bg_color=self.colors['primary'])
        except Exception as e:
            self.logger.error(f"Section header creation error: {e}")
            # Fallback header
            tk.Label(parent, text=title, font=('Segoe UI', 16, 'bold')).pack(pady=10)
    
    def _create_date_selection_section_safe(self, parent):
        """Create date selection with comprehensive error handling"""
        try:
            date_section = tk.LabelFrame(
                parent, text="📅 Analiz Dönemi", font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text_primary'], bg=self.colors['bg_secondary'], padx=20, pady=20
            )
            date_section.pack(fill='x', pady=(0, 20))
            
            date_row = tk.Frame(date_section, bg=self.colors['bg_secondary'])
            date_row.pack(fill='x', pady=10)
            
            if CALENDAR_AVAILABLE:
                self._create_calendar_widgets_safe(date_row)
            else:
                self._create_manual_date_widgets_safe(date_row)
            
            self._create_period_name_section_safe(date_section)
            
        except Exception as e:
            self.logger.error(f"Date selection section error: {e}")
            # Fallback: simple text entry
            tk.Label(parent, text="Dönem adı girin:").pack()
            self.period_name = tk.Entry(parent)
            self.period_name.pack()
    
    def _create_calendar_widgets_safe(self, parent):
        """Create calendar widgets with error handling"""
        try:
            tk.Label(parent, text="Başlangıç:", font=('Segoe UI', 11, 'bold'),
                    fg=self.colors['text_primary'], bg=self.colors['bg_secondary']).pack(side='left', padx=(0, 10))
            
            self.start_date = DateEntry(parent, width=12, background='darkblue',
                                      foreground='white', borderwidth=2, date_pattern='dd.mm.yyyy')
            self.start_date.pack(side='left', padx=(0, 30))
            
            tk.Label(parent, text="Bitiş:", font=('Segoe UI', 11, 'bold'),
                    fg=self.colors['text_primary'], bg=self.colors['bg_secondary']).pack(side='left', padx=(0, 10))
            
            self.end_date = DateEntry(parent, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='dd.mm.yyyy')
            self.end_date.pack(side='left')
            
        except Exception as e:
            self.logger.error(f"Calendar widgets error: {e}")
            self._create_manual_date_widgets_safe(parent)
    
    def _create_manual_date_widgets_safe(self, parent):
        """Create manual date widgets"""
        try:
            tk.Label(parent, text="⚠️ Takvim modülü bulunamadı. Dönem adını manuel girin.",
                    font=('Segoe UI', 10), fg=self.colors['warning'], bg=self.colors['bg_secondary']).pack(pady=10)
            self.start_date = None
            self.end_date = None
        except Exception as e:
            self.logger.error(f"Manual date widgets error: {e}")
    
    def _create_period_name_section_safe(self, parent):
        """Create period name section with safety"""
        try:
            name_row = tk.Frame(parent, bg=self.colors['bg_secondary'])
            name_row.pack(fill='x', pady=(10, 0))
            
            tk.Label(name_row, text="Dönem Adı:", font=('Segoe UI', 11, 'bold'),
                    fg=self.colors['text_primary'], bg=self.colors['bg_secondary']).pack(side='left', padx=(0, 10))
            
            self.period_name = tk.Entry(name_row, font=('Segoe UI', 11), width=30,
                                      bg=self.colors.get('input_bg', '#f8fafc'),
                                      fg=self.colors['text_primary'], relief='solid', bd=1)
            self.period_name.pack(side='left', padx=(0, 20))
            
            if CALENDAR_AVAILABLE and self.start_date and self.end_date:
                auto_btn = self.ui.create_modern_button(name_row, text="🤖 Otomatik İsim",
                                                      command=self._generate_auto_name_safe,
                                                      bg_color=self.colors['info'], padx=15, pady=5)
                auto_btn.pack(side='left')
                
        except Exception as e:
            self.logger.error(f"Period name section error: {e}")
    
    def _create_file_selection_section_safe(self, parent):
        """Create file selection with comprehensive safety"""
        try:
            files_section = tk.LabelFrame(parent, text="📁 Dosya Seçimi", font=('Segoe UI', 12, 'bold'),
                                        fg=self.colors['text_primary'], bg=self.colors['bg_secondary'], padx=20, pady=20)
            files_section.pack(fill='x', pady=(0, 20))
            
            self.karlilik_path = tk.StringVar()
            self.iskonto_path = tk.StringVar()
            
            self._create_file_input_safe(files_section, "Karlılık Dosyası:", "karlilik", self.colors['primary'])
            self._create_file_input_safe(files_section, "İskonto Dosyası:", "iskonto", self.colors['success'])
            
        except Exception as e:
            self.logger.error(f"File selection section error: {e}")
    
    def _create_file_input_safe(self, parent, label_text, file_type, button_color):
        """Create file input with safety"""
        try:
            file_row = tk.Frame(parent, bg=self.colors['bg_secondary'])
            file_row.pack(fill='x', pady=(0, 15))
            
            tk.Label(file_row, text=label_text, font=('Segoe UI', 11, 'bold'),
                    fg=self.colors['text_primary'], bg=self.colors['bg_secondary']).pack(anchor='w')
            
            file_frame = tk.Frame(file_row, bg=self.colors['bg_secondary'])
            file_frame.pack(fill='x', pady=(5, 0))
            
            file_label = tk.Label(file_frame, text="Henüz dosya seçilmedi...", font=('Segoe UI', 10),
                                 fg=self.colors['text_secondary'], bg='#f8f9fa', relief='solid', bd=1,
                                 anchor='w', padx=10, pady=8)
            file_label.pack(side='left', fill='x', expand=True, padx=(0, 10))
            
            if file_type == 'karlilik':
                self.karlilik_label = file_label
            else:
                self.iskonto_label = file_label
            
            file_btn = self.ui.create_modern_button(file_frame, text="📂 Dosya Seç",
                                                  command=lambda: self._select_file_safe(file_type),
                                                  bg_color=button_color, padx=20, pady=8)
            file_btn.pack(side='right')
            
        except Exception as e:
            self.logger.error(f"File input creation error: {e}")
    
    def _create_analysis_button_safe(self, parent):
        """Create analysis button with safety"""
        try:
            analyze_btn = self.ui.create_modern_button(parent, text="🚀 Analizi Başlat ve Kaydet",
                                                     command=self._start_period_analysis_safe,
                                                     bg_color=self.colors['warning'],
                                                     font=('Segoe UI', 14, 'bold'), pady=15)
            analyze_btn.pack(fill='x', pady=20)
        except Exception as e:
            self.logger.error(f"Analysis button creation error: {e}")
    
    def _create_history_tab(self):
        """Create history tab with error handling"""
        try:
            history_frame = ttk.Frame(self.sub_notebook)
            self.sub_notebook.add(history_frame, text="📚 Veri Geçmişi")
            self._widgets.add(history_frame)
            
            main_container = tk.Frame(history_frame, bg=self.colors['bg_primary'])
            main_container.pack(fill='both', expand=True, padx=20, pady=20)
            
            self._create_section_header_safe(main_container, "📚 Analiz Geçmişi")
            self._create_history_treeview_safe(main_container)
            self._create_history_buttons_safe(main_container)
            
        except Exception as e:
            self.logger.error(f"History tab creation error: {e}")
            raise
    
    def _create_history_treeview_safe(self, parent):
        """Create history treeview with safety"""
        try:
            tree_container = tk.Frame(parent, bg=self.colors['bg_secondary'])
            tree_container.pack(fill='both', expand=True)
            
            columns = ('ID', 'Dönem Adı', 'Başlangıç', 'Bitiş', 'Toplam Kar', 'Ürün Sayısı', 'Tarih')
            self.history_tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=15)
            
            column_widths = [50, 200, 100, 100, 120, 100, 150]
            for col, width in zip(columns, column_widths):
                self.history_tree.heading(col, text=col)
                self.history_tree.column(col, width=width)
            
            scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=self.history_tree.yview)
            self.history_tree.configure(yscrollcommand=scrollbar.set)
            
            self.history_tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
            
        except Exception as e:
            self.logger.error(f"History treeview creation error: {e}")
    
    def _create_history_buttons_safe(self, parent):
        """Create history buttons with safety"""
        try:
            button_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
            button_frame.pack(fill='x', pady=(20, 0))
            
            refresh_btn = self.ui.create_modern_button(button_frame, text="🔄 Yenile",
                                                     command=self._load_existing_data_safe,
                                                     bg_color=self.colors['info'], padx=20, pady=10)
            refresh_btn.pack(side='left', padx=(0, 10))
            
            delete_btn = self.ui.create_modern_button(button_frame, text="🗑️ Seçili Veriyi Sil",
                                                    command=self._delete_selected_data_safe,
                                                    bg_color=self.colors['danger'], padx=20, pady=10)
            delete_btn.pack(side='left')
            
        except Exception as e:
            self.logger.error(f"History buttons creation error: {e}")
    
    def _create_comparison_tab(self):
        """Create comparison tab with error handling"""
        try:
            comparison_frame = ttk.Frame(self.sub_notebook)
            self.sub_notebook.add(comparison_frame, text="⚖️ Dönem Karşılaştırma")
            self._widgets.add(comparison_frame)
            
            main_container = tk.Frame(comparison_frame, bg=self.colors['bg_primary'])
            main_container.pack(fill='both', expand=True, padx=20, pady=20)
            
            self._create_section_header_safe(main_container, "⚖️ Dönem Karşılaştırması")
            self._create_period_selection_safe(main_container)
            self._create_compare_button_safe(main_container)
            self._create_comparison_results_area_safe(main_container)
            
        except Exception as e:
            self.logger.error(f"Comparison tab creation error: {e}")
            raise
    
    def _create_period_selection_safe(self, parent):
        """Create period selection with safety"""
        try:
            selection_frame = tk.LabelFrame(parent, text="🎯 Dönem Seçimi", font=('Segoe UI', 12, 'bold'),
                                          fg=self.colors['text_primary'], bg=self.colors['bg_secondary'], padx=20, pady=20)
            selection_frame.pack(fill='x', pady=(0, 20))
            
            self.period1_var = tk.StringVar()
            self.period2_var = tk.StringVar()
            
            # Period 1
            period1_row = tk.Frame(selection_frame, bg=self.colors['bg_secondary'])
            period1_row.pack(fill='x', pady=(0, 15))
            
            tk.Label(period1_row, text="1. Dönem:", font=('Segoe UI', 11, 'bold'),
                    fg=self.colors['text_primary'], bg=self.colors['bg_secondary']).pack(side='left', padx=(0, 10))
            
            self.period1_combo = ttk.Combobox(period1_row, textvariable=self.period1_var,
                                            font=('Segoe UI', 11), width=40, state='readonly')
            self.period1_combo.pack(side='left')
            
            # Period 2
            period2_row = tk.Frame(selection_frame, bg=self.colors['bg_secondary'])
            period2_row.pack(fill='x')
            
            tk.Label(period2_row, text="2. Dönem:", font=('Segoe UI', 11, 'bold'),
                    fg=self.colors['text_primary'], bg=self.colors['bg_secondary']).pack(side='left', padx=(0, 10))
            
            self.period2_combo = ttk.Combobox(period2_row, textvariable=self.period2_var,
                                            font=('Segoe UI', 11), width=40, state='readonly')
            self.period2_combo.pack(side='left')
            
        except Exception as e:
            self.logger.error(f"Period selection creation error: {e}")
    
    def _create_compare_button_safe(self, parent):
        """Create compare button with safety"""
        try:
            compare_btn = self.ui.create_modern_button(parent, text="📊 Dönemleri Karşılaştır",
                                                     command=self._compare_periods_safe,
                                                     bg_color=self.colors['primary'],
                                                     font=('Segoe UI', 14, 'bold'), pady=15)
            compare_btn.pack(fill='x', pady=(0, 20))
        except Exception as e:
            self.logger.error(f"Compare button creation error: {e}")
    
    def _create_comparison_results_area_safe(self, parent):
        """Create comparison results area with safety"""
        try:
            canvas_container = tk.Frame(parent, bg=self.colors['bg_primary'])
            canvas_container.pack(fill='both', expand=True)
            
            self.comparison_canvas, self.comparison_results_frame, scrollbar = self.ui.create_scrollable_frame(
                canvas_container, self.colors, setup_mouse_wheel=True
            )
            
        except Exception as e:
            self.logger.error(f"Comparison results area creation error: {e}")
            # Fallback to simple frame
            self.comparison_results_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
            self.comparison_results_frame.pack(fill='both', expand=True)
    
    def _create_error_tab(self, tab_name, error_message):
        """Create error tab for failed components"""
        try:
            error_frame = ttk.Frame(self.sub_notebook)
            self.sub_notebook.add(error_frame, text=f"⚠️ {tab_name} (Hata)")
            
            error_container = tk.Frame(error_frame, bg=self.colors['bg_primary'])
            error_container.pack(fill='both', expand=True, padx=20, pady=20)
            
            tk.Label(error_container, text=f"⚠️ {tab_name} Yüklenemedi",
                    font=('Segoe UI', 16, 'bold'), fg=self.colors['danger'],
                    bg=self.colors['bg_primary']).pack(pady=(50, 20))
            
            tk.Label(error_container, text=f"Hata: {error_message}",
                    font=('Segoe UI', 12), fg=self.colors['text_secondary'],
                    bg=self.colors['bg_primary']).pack()
            
        except Exception as e:
            self.logger.error(f"Error tab creation failed: {e}")
    
    def _schedule_post_init(self):
        """Schedule post-initialization tasks"""
        try:
            if self.main_frame and self._check_widget_exists(self.main_frame):
                self.main_frame.after(1000, self._post_init_tasks)
        except Exception as e:
            self.logger.error(f"Post-init scheduling error: {e}")
    
    def _post_init_tasks(self):
        """Post-initialization tasks with safety"""
        try:
            if not self._closing and self._initialization_complete:
                self._load_existing_data_safe()
                self._start_message_queue_processing()
        except Exception as e:
            self.logger.error(f"Post-init tasks error: {e}")
    
    def _start_message_queue_processing(self):
        """Start message queue processing"""
        try:
            if not self._closing:
                self._process_message_queue()
                if self.main_frame and self._check_widget_exists(self.main_frame):
                    self.main_frame.after(100, self._start_message_queue_processing)
        except Exception as e:
            self.logger.error(f"Message queue processing error: {e}")
    
    def _process_message_queue(self):
        """Process messages from background threads"""
        try:
            processed = 0
            while processed < 10:  # Process max 10 messages per cycle
                try:
                    message_type, data = self.message_queue.get_nowait()
                    self._handle_queue_message(message_type, data)
                    processed += 1
                except queue.Empty:
                    break
                except Exception as e:
                    self.logger.error(f"Queue message processing error: {e}")
                    break
        except Exception as e:
            self.logger.error(f"Message queue processing error: {e}")
    
    def _handle_queue_message(self, message_type, data):
        """Handle queue messages with safety"""
        try:
            if message_type == 'analysis_complete':
                self._on_analysis_complete_safe(data)
            elif message_type == 'analysis_error':
                self._on_analysis_error_safe(data)
            elif message_type == 'delete_complete':
                self._on_delete_complete_safe()
            elif message_type == 'load_data':
                self._load_existing_data_safe()
            elif message_type == 'update_combos':
                self._update_comparison_combos_safe(data)
            elif message_type == 'comparison_complete':
                self._handle_comparison_complete(data)
        except Exception as e:
            self.logger.error(f"Queue message handling error: {e}")
    
    def _check_widget_exists(self, widget):
        """Check if widget exists and is valid"""
        try:
            return widget is not None and widget.winfo_exists()
        except (tk.TclError, AttributeError):
            return False
    
    def _safe_widget_operation(self, widget, operation, *args, **kwargs):
        """Perform widget operation safely"""
        try:
            if self._check_widget_exists(widget):
                return operation(*args, **kwargs)
            return None
        except (tk.TclError, AttributeError) as e:
            self.logger.debug(f"Widget operation failed: {e}")
            return None
    
    def _generate_auto_name_safe(self):
        """Generate automatic period name with safety"""
        try:
            if not CALENDAR_AVAILABLE or not self._check_widget_exists(self.start_date) or not self._check_widget_exists(self.end_date):
                self._show_message("Uyarı", "Takvim modülü bulunamadı. Manuel isim girin.")
                return
            
            start = self.start_date.get_date()
            end = self.end_date.get_date()
            
            days_diff = (end - start).days + 1
            
            if days_diff <= 7:
                week_num = start.isocalendar()[1]
                month_name = start.strftime("%B")
                auto_name = f"{month_name} {week_num}. Hafta"
            elif days_diff <= 31:
                month_name = start.strftime("%B %Y")
                auto_name = f"{month_name}"
            else:
                start_str = start.strftime("%d.%m")
                end_str = end.strftime("%d.%m.%Y")
                auto_name = f"{start_str} - {end_str}"
            
            if self._check_widget_exists(self.period_name):
                self.period_name.delete(0, tk.END)
                self.period_name.insert(0, auto_name)
                
        except Exception as e:
            self.logger.error(f"Auto name generation error: {e}")
            self._show_message("Hata", f"Otomatik isim oluşturulamadı: {e}")
    
    def _select_file_safe(self, file_type):
        """File selection with comprehensive safety"""
        try:
            title = f"{'Karlılık' if file_type == 'karlilik' else 'İskonto'} Dosyasını Seçin"
            
            filename = filedialog.askopenfilename(
                title=title,
                filetypes=[("Excel dosyaları", "*.xlsx *.xls"), ("Tüm dosyalar", "*.*")]
            )
            
            if not filename:
                return
            
            if not os.path.exists(filename):
                self._show_message("Hata", "Seçilen dosya bulunamadı!")
                return
            
            # Update path variable
            if file_type == 'karlilik' and self.karlilik_path:
                self.karlilik_path.set(filename)
                label_widget = self.karlilik_label
            elif file_type == 'iskonto' and self.iskonto_path:
                self.iskonto_path.set(filename)
                label_widget = self.iskonto_label
            else:
                return
            
            # Update display
            if self._check_widget_exists(label_widget):
                display_name = os.path.basename(filename)
                label_widget.config(text=f"✅ {display_name}", fg=self.colors['success'])
                
        except Exception as e:
            self.logger.error(f"File selection error: {e}")
            self._show_message("Hata", f"Dosya seçim hatası: {e}")
    
    def _start_period_analysis_safe(self):
        """Start period analysis with comprehensive safety"""
        try:
            if not self._validate_analysis_inputs_safe():
                return
            
            thread = threading.Thread(
                target=self._run_period_analysis_safe,
                daemon=True,
                name=f"PeriodAnalysis_{id(self)}"
            )
            self.active_threads.add(thread)
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Period analysis start error: {e}")
            self._show_message("Hata", f"Analiz başlatma hatası: {e}")
    
    def _validate_analysis_inputs_safe(self):
        """Validate analysis inputs with safety"""
        try:
            karlilik_path = self.karlilik_path.get() if self.karlilik_path else ""
            iskonto_path = self.iskonto_path.get() if self.iskonto_path else ""
            
            if not karlilik_path or not iskonto_path:
                self._show_message("Eksik Dosya", "Lütfen hem karlılık hem de iskonto dosyalarını seçin!")
                return False
            
            period_name = ""
            if self._check_widget_exists(self.period_name):
                period_name = self.period_name.get().strip()
            
            if not period_name:
                self._show_message("Eksik Bilgi", "Lütfen dönem adını girin!")
                return False
            
            # File existence check
            for path in [karlilik_path, iskonto_path]:
                if not os.path.exists(path):
                    self._show_message("Hata", f"Dosya bulunamadı: {os.path.basename(path)}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Input validation error: {e}")
            return False
    
    def _run_period_analysis_safe(self):
        """Run period analysis in background thread"""
        try:
            self.logger.info("Period analysis thread started")
            
            # Import karlılık module
            try:
                from karlilik import KarlilikAnalizi
            except ImportError:
                self._queue_message('analysis_error', "Karlılık analizi modülü bulunamadı!")
                return
            
            # Get file paths
            karlilik_path = self.karlilik_path.get() if self.karlilik_path else ""
            iskonto_path = self.iskonto_path.get() if self.iskonto_path else ""
            
            if not karlilik_path or not iskonto_path:
                self._queue_message('analysis_error', "Dosya yolları bulunamadı!")
                return
            
            # Progress callback
            def progress_callback(value, status):
                self.logger.info(f"Progress {value}%: {status}")
            
            # Log callback
            def log_callback(message, msg_type='info'):
                self.logger.info(f"[{msg_type.upper()}] {message}")
            
            # Run analysis
            analiz = KarlilikAnalizi(progress_callback, log_callback)
            result_df = analiz.analyze(karlilik_path, iskonto_path)
            
            if result_df is not None and not result_df.empty:
                self._queue_message('analysis_complete', result_df)
            else:
                self._queue_message('analysis_error', "Analiz tamamlanamadı!")
                
        except Exception as e:
            self.logger.error(f"Period analysis error: {e}")
            self._queue_message('analysis_error', str(e))
        finally:
            self.logger.info("Period analysis thread finished")
            # Remove from active threads
            current_thread = threading.current_thread()
            self.active_threads.discard(current_thread)
    
    def _queue_message(self, message_type, data):
        """Queue message for main thread"""
        try:
            if not self._closing:
                self.message_queue.put((message_type, data))
        except Exception as e:
            self.logger.error(f"Queue message error: {e}")
    
    def _on_analysis_complete_safe(self, result_df):
        """Handle analysis completion safely"""
        try:
            self._save_analysis_data_safe(result_df)
            self._show_message("Başarılı", "Dönem analizi tamamlandı ve kaydedildi!")
            self._clear_entry_form_safe()
            self._load_existing_data_safe()
            
        except Exception as e:
            self.logger.error(f"Analysis complete handler error: {e}")
            self._show_message("Hata", f"Sonuç kaydetme hatası: {e}")
    
    def _on_analysis_error_safe(self, error_msg):
        """Handle analysis error safely"""
        try:
            self._show_message("Hata", f"Analiz sırasında hata: {error_msg}")
        except Exception as e:
            self.logger.error(f"Analysis error handler error: {e}")
    
    def _save_analysis_data_safe(self, result_df):
        """Save analysis data with comprehensive safety"""
        try:
            # Read existing data
            if hasattr(self.data_ops, 'JSONOperations'):
                data = self.data_ops.JSONOperations.read_json_safe(self.data_file)
            else:
                data = self.data_ops.read_json_safe(self.data_file)
            
            if not data:
                data = {"analizler": [], "son_guncelleme": datetime.now().isoformat()}
            
            # Calculate summary data
            toplam_kar = 0
            urun_sayisi = len(result_df)
            
            try:
                if 'Net Kar' in result_df.columns:
                    if hasattr(self.data_ops, 'DataAnalyzer'):
                        kar_stats = self.data_ops.DataAnalyzer.calculate_basic_statistics(result_df, 'Net Kar')
                        toplam_kar = kar_stats.get('sum', 0)
                    else:
                        toplam_kar = result_df['Net Kar'].sum()
            except Exception:
                toplam_kar = 0
            
            # Get date information
            baslangic_tarihi = "01.01.2024"
            bitis_tarihi = "31.12.2024"
            
            if CALENDAR_AVAILABLE and self._check_widget_exists(self.start_date) and self._check_widget_exists(self.end_date):
                try:
                    baslangic_tarihi = self.start_date.get_date().strftime("%d.%m.%Y")
                    bitis_tarihi = self.end_date.get_date().strftime("%d.%m.%Y")
                except Exception:
                    today = datetime.now()
                    baslangic_tarihi = today.strftime("%d.%m.%Y")
                    bitis_tarihi = today.strftime("%d.%m.%Y")
            
            # Get period name
            period_name = "Bilinmeyen Dönem"
            if self._check_widget_exists(self.period_name):
                period_name = self.period_name.get().strip() or "Bilinmeyen Dönem"
            
            # Get file names
            karlilik_file = "bilinmiyor.xlsx"
            iskonto_file = "bilinmiyor.xlsx"
            
            if self.karlilik_path:
                try:
                    karlilik_path = self.karlilik_path.get()
                    if karlilik_path:
                        karlilik_file = os.path.basename(karlilik_path)
                except Exception:
                    pass
            
            if self.iskonto_path:
                try:
                    iskonto_path = self.iskonto_path.get()
                    if iskonto_path:
                        iskonto_file = os.path.basename(iskonto_path)
                except Exception:
                    pass
            
            # Create new analysis record
            new_analysis = {
                "id": len(data["analizler"]) + 1,
                "donem_adi": period_name,
                "baslangic_tarihi": baslangic_tarihi,
                "bitis_tarihi": bitis_tarihi,
                "olusturma_tarihi": datetime.now().isoformat(),
                "toplam_kar": round(float(toplam_kar), 2) if toplam_kar else 0.0,
                "urun_sayisi": int(urun_sayisi),
                "karlilik_dosya": karlilik_file,
                "iskonto_dosya": iskonto_file,
                "analiz_detayi": result_df.to_dict('records')
            }
            
            data["analizler"].append(new_analysis)
            data["son_guncelleme"] = datetime.now().isoformat()
            
            # Save data
            if hasattr(self.data_ops, 'JSONOperations'):
                success = self.data_ops.JSONOperations.write_json_safe(data, self.data_file)
            else:
                success = self.data_ops.write_json_safe(data, self.data_file)
            
            if not success:
                raise Exception("JSON dosyası kaydedilemedi")
            
            self.logger.info("Analysis data saved successfully")
            
        except Exception as e:
            self.logger.error(f"Save analysis data error: {e}")
            raise Exception(f"Veri kaydetme hatası: {e}")
    
    def _clear_entry_form_safe(self):
        """Clear entry form with safety"""
        try:
            if self._check_widget_exists(self.period_name):
                self.period_name.delete(0, tk.END)
            
            if self.karlilik_path:
                self.karlilik_path.set("")
            if self.iskonto_path:
                self.iskonto_path.set("")
            
            default_text = "Henüz dosya seçilmedi..."
            default_color = self.colors['text_secondary']
            
            if self._check_widget_exists(self.karlilik_label):
                self.karlilik_label.config(text=default_text, fg=default_color)
            
            if self._check_widget_exists(self.iskonto_label):
                self.iskonto_label.config(text=default_text, fg=default_color)
                
        except Exception as e:
            self.logger.error(f"Form clear error: {e}")
    
    def _load_existing_data_safe(self):
        """Load existing data with comprehensive safety"""
        try:
            # Clear existing tree items
            if self._check_widget_exists(self.history_tree):
                for item in self.history_tree.get_children():
                    try:
                        self.history_tree.delete(item)
                    except tk.TclError:
                        pass
            
            # Read data
            if hasattr(self.data_ops, 'JSONOperations'):
                data = self.data_ops.JSONOperations.read_json_safe(self.data_file)
            else:
                data = self.data_ops.read_json_safe(self.data_file)
            
            if not data:
                self.logger.info("No data file found")
                return
            
            # Populate tree
            if self._check_widget_exists(self.history_tree):
                for analiz in data.get("analizler", []):
                    try:
                        creation_date = "Bilinmiyor"
                        try:
                            creation_date = datetime.fromisoformat(analiz["olusturma_tarihi"]).strftime("%d.%m.%Y %H:%M")
                        except (ValueError, KeyError):
                            pass
                        
                        self.history_tree.insert('', 'end', values=(
                            analiz.get("id", "N/A"),
                            analiz.get("donem_adi", "Bilinmiyor"),
                            analiz.get("baslangic_tarihi", "N/A"),
                            analiz.get("bitis_tarihi", "N/A"),
                            f"₺{analiz.get('toplam_kar', 0):,.2f}",
                            f"{analiz.get('urun_sayisi', 0)} ürün",
                            creation_date
                        ))
                    except Exception as e:
                        self.logger.warning(f"Tree item insert error: {e}")
                        continue
            
            # Update comparison combos
            self._update_comparison_combos_safe(data.get("analizler", []))
            
        except Exception as e:
            self.logger.error(f"Load existing data error: {e}")
    
    def _update_comparison_combos_safe(self, analizler):
        """Update comparison comboboxes with safety"""
        try:
            if not self._check_widget_exists(self.period1_combo) or not self._check_widget_exists(self.period2_combo):
                return
            
            period_list = []
            for analiz in analizler:
                try:
                    donem_adi = analiz.get('donem_adi', 'Bilinmiyor')
                    baslangic = analiz.get('baslangic_tarihi', 'N/A')
                    bitis = analiz.get('bitis_tarihi', 'N/A')
                    period_text = f"{donem_adi} ({baslangic} - {bitis})"
                    period_list.append(period_text)
                except Exception:
                    continue
            
            try:
                self.period1_combo['values'] = period_list
                self.period2_combo['values'] = period_list
            except tk.TclError:
                pass
            
        except Exception as e:
            self.logger.error(f"Combo update error: {e}")
    
    def _delete_selected_data_safe(self):
        """Delete selected data with safety"""
        try:
            if not self._check_widget_exists(self.history_tree):
                return
            
            selected_item = self.history_tree.selection()
            if not selected_item:
                self._show_message("Seçim Hatası", "Lütfen silinecek veriyi seçin!")
                return
            
            result = messagebox.askyesno("Silme Onayı", "Seçili analiz verisi kalıcı olarak silinecek. Emin misiniz?")
            
            if result:
                try:
                    item = selected_item[0]
                    values = self.history_tree.item(item, 'values')
                    
                    if not values:
                        return
                    
                    selected_id = int(values[0])
                    
                    thread = threading.Thread(
                        target=self._run_delete_data_safe,
                        args=(selected_id,),
                        daemon=True,
                        name=f"DeleteData_{id(self)}"
                    )
                    self.active_threads.add(thread)
                    thread.start()
                    
                except (ValueError, IndexError) as e:
                    self.logger.error(f"Delete selection error: {e}")
                    self._show_message("Hata", "Silme işlemi için geçersiz seçim!")
                    
        except Exception as e:
            self.logger.error(f"Delete selected data error: {e}")
            self._show_message("Hata", f"Silme işlemi hatası: {e}")
    
    def _run_delete_data_safe(self, selected_id):
        """Run data deletion in background thread"""
        try:
            # Read data
            if hasattr(self.data_ops, 'JSONOperations'):
                data = self.data_ops.JSONOperations.read_json_safe(self.data_file)
            else:
                data = self.data_ops.read_json_safe(self.data_file)
            
            if not data:
                self._queue_message('analysis_error', "Veri dosyası bulunamadı!")
                return
            
            # Filter out selected item
            original_count = len(data["analizler"])
            data["analizler"] = [a for a in data["analizler"] if a.get("id") != selected_id]
            data["son_guncelleme"] = datetime.now().isoformat()
            
            if len(data["analizler"]) == original_count:
                self._queue_message('analysis_error', "Silinecek veri bulunamadı!")
                return
            
            # Save data
            if hasattr(self.data_ops, 'JSONOperations'):
                success = self.data_ops.JSONOperations.write_json_safe(data, self.data_file)
            else:
                success = self.data_ops.write_json_safe(data, self.data_file)
            
            if success:
                self._queue_message('delete_complete', None)
            else:
                self._queue_message('analysis_error', "Silme işlemi başarısız!")
            
        except Exception as e:
            self.logger.error(f"Delete data error: {e}")
            self._queue_message('analysis_error', str(e))
        finally:
            # Remove from active threads
            current_thread = threading.current_thread()
            self.active_threads.discard(current_thread)
    
    def _on_delete_complete_safe(self):
        """Handle delete completion safely"""
        try:
            self._load_existing_data_safe()
            self._show_message("Başarılı", "Analiz verisi silindi!")
        except Exception as e:
            self.logger.error(f"Delete complete handler error: {e}")
    
    def _compare_periods_safe(self):
        """Compare periods with safety"""
        try:
            if not self._validate_period_selection_safe():
                return
            
            thread = threading.Thread(
                target=self._run_period_comparison_safe,
                daemon=True,
                name=f"PeriodComparison_{id(self)}"
            )
            self.active_threads.add(thread)
            thread.start()
            
        except Exception as e:
            self.logger.error(f"Compare periods error: {e}")
            self._show_message("Hata", f"Karşılaştırma hatası: {e}")
    
    def _validate_period_selection_safe(self):
        """Validate period selection with safety"""
        try:
            period1_value = self.period1_var.get() if self.period1_var else ""
            period2_value = self.period2_var.get() if self.period2_var else ""
            
            if not period1_value or not period2_value:
                self._show_message("Seçim Hatası", "Lütfen iki dönem seçin!")
                return False
            
            if period1_value == period2_value:
                self._show_message("Seçim Hatası", "Lütfen farklı iki dönem seçin!")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Period selection validation error: {e}")
            return False
    
    def _run_period_comparison_safe(self):
        """Run period comparison in background thread"""
        try:
            # Read data
            if hasattr(self.data_ops, 'JSONOperations'):
                data = self.data_ops.JSONOperations.read_json_safe(self.data_file)
            else:
                data = self.data_ops.read_json_safe(self.data_file)
            
            if not data:
                self._queue_message('analysis_error', "Veri dosyası bulunamadı!")
                return
            
            period1_value = self.period1_var.get() if self.period1_var else ""
            period2_value = self.period2_var.get() if self.period2_var else ""
            
            if not period1_value or not period2_value:
                self._queue_message('analysis_error', "Dönem seçimleri bulunamadı!")
                return
            
            # Find period data
            period1_data = None
            period2_data = None
            
            for analiz in data.get("analizler", []):
                donem_adi = analiz.get('donem_adi', '')
                baslangic = analiz.get('baslangic_tarihi', '')
                bitis = analiz.get('bitis_tarihi', '')
                period_text = f"{donem_adi} ({baslangic} - {bitis})"
                
                if period_text == period1_value:
                    period1_data = analiz
                elif period_text == period2_value:
                    period2_data = analiz
            
            if not period1_data or not period2_data:
                self._queue_message('analysis_error', "Seçili dönemler bulunamadı!")
                return
            
            # Queue comparison display
            self._queue_message('comparison_complete', (period1_data, period2_data))
            
        except Exception as e:
            self.logger.error(f"Period comparison error: {e}")
            self._queue_message('analysis_error', str(e))
        finally:
            # Remove from active threads
            current_thread = threading.current_thread()
            self.active_threads.discard(current_thread)
    
    def _handle_comparison_complete(self, period_data):
        """Handle comparison completion"""
        try:
            period1_data, period2_data = period_data
            self._display_comparison_results_safe(period1_data, period2_data)
        except Exception as e:
            self.logger.error(f"Comparison complete handler error: {e}")
    
    def _display_comparison_results_safe(self, period1, period2):
        """Display comparison results with comprehensive safety"""
        try:
            if not self._check_widget_exists(self.comparison_results_frame):
                return
            
            # Clear existing content
            for widget in self.comparison_results_frame.winfo_children():
                try:
                    widget.destroy()
                except tk.TclError:
                    pass
            
            # Main title
            main_title = tk.Label(
                self.comparison_results_frame,
                text="📊 Dönem Karşılaştırma Sonuçları",
                font=('Segoe UI', 16, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['bg_primary']
            )
            main_title.pack(pady=(0, 20))
            
            # Create sections
            self._create_period_info_section_safe(period1, period2)
            self._create_kpi_comparison_safe(period1, period2)
            
            if MATPLOTLIB_AVAILABLE:
                self._create_chart_comparison_safe(period1, period2)
            else:
                self._create_simple_comparison_table_safe(period1, period2)
            
        except Exception as e:
            self.logger.error(f"Display comparison results error: {e}")
            try:
                error_label = tk.Label(
                    self.comparison_results_frame,
                    text=f"⚠️ Karşılaştırma gösterimi hatası: {str(e)}",
                    font=('Segoe UI', 12),
                    fg=self.colors['danger'],
                    bg=self.colors['bg_primary']
                )
                error_label.pack(pady=20)
            except Exception:
                pass
    
    def _create_period_info_section_safe(self, period1, period2):
        """Create period info section with safety"""
        try:
            periods_frame = tk.Frame(self.comparison_results_frame, bg=self.colors['bg_primary'])
            periods_frame.pack(fill='x', pady=(0, 30))
            
            # Period 1 info
            period1_frame = tk.Frame(periods_frame, bg='white', relief='solid', bd=1)
            period1_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
            
            tk.Label(period1_frame, text="📅 1. DÖNEM", font=('Segoe UI', 12, 'bold'),
                    fg=self.colors['primary'], bg='white').pack(pady=10)
            
            period1_text = f"{period1.get('donem_adi', 'Bilinmiyor')}\n{period1.get('baslangic_tarihi', 'N/A')} - {period1.get('bitis_tarihi', 'N/A')}"
            tk.Label(period1_frame, text=period1_text, font=('Segoe UI', 11),
                    fg=self.colors['text_primary'], bg='white').pack(pady=(0, 10))
            
            # Period 2 info
            period2_frame = tk.Frame(periods_frame, bg='white', relief='solid', bd=1)
            period2_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
            
            tk.Label(period2_frame, text="📅 2. DÖNEM", font=('Segoe UI', 12, 'bold'),
                    fg=self.colors['info'], bg='white').pack(pady=10)
            
            period2_text = f"{period2.get('donem_adi', 'Bilinmiyor')}\n{period2.get('baslangic_tarihi', 'N/A')} - {period2.get('bitis_tarihi', 'N/A')}"
            tk.Label(period2_frame, text=period2_text, font=('Segoe UI', 11),
                    fg=self.colors['text_primary'], bg='white').pack(pady=(0, 10))
            
        except Exception as e:
            self.logger.error(f"Period info section creation error: {e}")
    
    def _create_kpi_comparison_safe(self, period1, period2):
        """Create KPI comparison with safety"""
        try:
            kpi_section = tk.LabelFrame(
                self.comparison_results_frame,
                text="💰 Temel Metrikler Karşılaştırması",
                font=('Segoe UI', 14, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['bg_secondary'],
                padx=20,
                pady=20
            )
            kpi_section.pack(fill='x', pady=(0, 30))
            
            kpi_container = tk.Frame(kpi_section, bg=self.colors['bg_secondary'])
            kpi_container.pack(fill='x')
            
            # Safe numeric conversion
            if hasattr(self.data_ops, 'DataCleaner'):
                p1_kar = self.data_ops.DataCleaner.clean_numeric(period1.get('toplam_kar', 0))
                p2_kar = self.data_ops.DataCleaner.clean_numeric(period2.get('toplam_kar', 0))
            else:
                p1_kar = self.data_ops.clean_numeric(period1.get('toplam_kar', 0))
                p2_kar = self.data_ops.clean_numeric(period2.get('toplam_kar', 0))
            
            p1_urun = int(period1.get('urun_sayisi', 0))
            p2_urun = int(period2.get('urun_sayisi', 0))
            
            # Calculate changes
            kar_change = p2_kar - p1_kar
            kar_percent = (kar_change / p1_kar * 100) if p1_kar != 0 else 0
            
            self._create_comparison_card_safe(
                kpi_container, "💰 Toplam Kar",
                f"₺{p1_kar:,.0f}", f"₺{p2_kar:,.0f}",
                kar_change, kar_percent, 0
            )
            
            urun_change = p2_urun - p1_urun
            urun_percent = (urun_change / p1_urun * 100) if p1_urun != 0 else 0
            
            self._create_comparison_card_safe(
                kpi_container, "📦 Ürün Sayısı",
                f"{p1_urun} ürün", f"{p2_urun} ürün",
                urun_change, urun_percent, 1
            )
            
            avg_kar1 = p1_kar / p1_urun if p1_urun > 0 else 0
            avg_kar2 = p2_kar / p2_urun if p2_urun > 0 else 0
            avg_change = avg_kar2 - avg_kar1
            avg_percent = (avg_change / avg_kar1 * 100) if avg_kar1 != 0 else 0
            
            self._create_comparison_card_safe(
                kpi_container, "📈 Ort. Kar/Ürün",
                f"₺{avg_kar1:,.0f}", f"₺{avg_kar2:,.0f}",
                avg_change, avg_percent, 2
            )
            
            # Configure grid
            for i in range(3):
                kpi_container.grid_columnconfigure(i, weight=1)
                
        except Exception as e:
            self.logger.error(f"KPI comparison creation error: {e}")
    
    def _create_comparison_card_safe(self, parent, title, value1, value2, change, percent, column):
        """Create comparison card with safety"""
        try:
            card_container = tk.Frame(parent, bg=self.colors['bg_secondary'])
            card_container.grid(row=0, column=column, padx=15, pady=10, sticky='ew')
            
            card_frame = tk.Frame(card_container, bg='white', relief='solid', bd=1)
            card_frame.pack(fill='both', expand=True)
            
            inner_frame = tk.Frame(card_frame, bg='white')
            inner_frame.pack(fill='both', expand=True, padx=20, pady=15)
            
            # Title
            tk.Label(inner_frame, text=title, font=('Segoe UI', 11, 'bold'),
                    fg=self.colors['text_primary'], bg='white').pack()
            
            # Values
            values_frame = tk.Frame(inner_frame, bg='white')
            values_frame.pack(fill='x', pady=(10, 5))
            
            tk.Label(values_frame, text=value1, font=('Segoe UI', 12, 'bold'),
                    fg=self.colors['primary'], bg='white').pack()
            
            tk.Label(values_frame, text="vs", font=('Segoe UI', 9),
                    fg=self.colors['text_secondary'], bg='white').pack(pady=3)
            
            tk.Label(values_frame, text=value2, font=('Segoe UI', 12, 'bold'),
                    fg=self.colors['info'], bg='white').pack()
            
            # Change indicators
            change_color = self.colors['success'] if change >= 0 else self.colors['danger']
            change_icon = "📈" if change >= 0 else "📉"
            
            change_text = f"{change_icon} {change:+,.0f}" if abs(change) >= 1 else f"{change_icon} {change:+.2f}"
            
            tk.Label(inner_frame, text=change_text, font=('Segoe UI', 10, 'bold'),
                    fg=change_color, bg='white').pack()
            
            tk.Label(inner_frame, text=f"({percent:+.1f}%)", font=('Segoe UI', 9),
                    fg=change_color, bg='white').pack()
            
        except Exception as e:
            self.logger.error(f"Comparison card creation error: {e}")
    
    def _create_chart_comparison_safe(self, period1, period2):
        """Create chart comparison with Matplotlib"""
        try:
            chart_section = tk.LabelFrame(
                self.comparison_results_frame,
                text="📊 Grafik Karşılaştırması",
                font=('Segoe UI', 14, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['bg_secondary'],
                padx=20,
                pady=20
            )
            chart_section.pack(fill='x', pady=(0, 30))
            
            fig = Figure(figsize=(12, 6), dpi=100, facecolor='white')
            gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
            
            # Safe numeric conversion
            if hasattr(self.data_ops, 'DataCleaner'):
                p1_kar = self.data_ops.DataCleaner.clean_numeric(period1.get('toplam_kar', 0))
                p2_kar = self.data_ops.DataCleaner.clean_numeric(period2.get('toplam_kar', 0))
            else:
                p1_kar = self.data_ops.clean_numeric(period1.get('toplam_kar', 0))
                p2_kar = self.data_ops.clean_numeric(period2.get('toplam_kar', 0))
            
            p1_urun = int(period1.get('urun_sayisi', 0))
            p2_urun = int(period2.get('urun_sayisi', 0))
            
            periods = [period1.get('donem_adi', 'Dönem 1')[:15], period2.get('donem_adi', 'Dönem 2')[:15]]
            profits = [p1_kar, p2_kar]
            colors = [self.colors['primary'], self.colors['info']]
            
            # Bar chart for profits
            ax1 = fig.add_subplot(gs[0, 0])
            bars = ax1.bar(periods, profits, color=colors, alpha=0.8)
            ax1.set_title('Toplam Kar Karşılaştırması', fontsize=12, fontweight='bold')
            ax1.set_ylabel('Kar (₺)')
            ax1.tick_params(axis='x', rotation=45)
            
            for bar, profit in zip(bars, profits):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'₺{profit:,.0f}', ha='center', va='bottom', fontsize=10)
            
            # Pie chart for product distribution
            ax2 = fig.add_subplot(gs[0, 1])
            sizes = [p1_urun, p2_urun]
            if sum(sizes) > 0:
                ax2.pie(sizes, labels=periods, autopct='%1.0f%%', colors=colors, startangle=90)
                ax2.set_title('Ürün Sayısı Dağılımı', fontsize=12, fontweight='bold')
            
            # Line chart for trend
            ax3 = fig.add_subplot(gs[1, :])
            
            try:
                date1 = datetime.strptime(period1.get('baslangic_tarihi', '01.01.2024'), '%d.%m.%Y')
                date2 = datetime.strptime(period2.get('baslangic_tarihi', '01.02.2024'), '%d.%m.%Y')
                dates = [date1, date2]
            except ValueError:
                dates = [datetime.now() - timedelta(days=30), datetime.now()]
            
            avg_profits = [
                p1_kar / p1_urun if p1_urun > 0 else 0,
                p2_kar / p2_urun if p2_urun > 0 else 0
            ]
            
            ax3.plot(dates, avg_profits, marker='o', linewidth=3, markersize=8, color=self.colors['success'])
            ax3.set_title('Ortalama Ürün Karı Trend Analizi', fontsize=12, fontweight='bold')
            ax3.set_ylabel('Ortalama Kar (₺)')
            ax3.grid(True, alpha=0.3)
            
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y'))
            ax3.tick_params(axis='x', rotation=45)
            
            canvas = FigureCanvasTkAgg(fig, chart_section)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
        except Exception as e:
            self.logger.error(f"Chart comparison creation error: {e}")
            self._create_simple_comparison_table_safe(period1, period2)
    
    def _create_simple_comparison_table_safe(self, period1, period2):
        """Create simple comparison table without Matplotlib"""
        try:
            table_section = tk.LabelFrame(
                self.comparison_results_frame,
                text="📊 Karşılaştırma Tablosu",
                font=('Segoe UI', 14, 'bold'),
                fg=self.colors['text_primary'],
                bg=self.colors['bg_secondary'],
                padx=20,
                pady=20
            )
            table_section.pack(fill='x', pady=(0, 30))
            
            table_frame = tk.Frame(table_section, bg=self.colors['bg_secondary'])
            table_frame.pack(fill='x', padx=20, pady=20)
            
            # Headers
            headers = ["Metrik", "1. Dönem", "2. Dönem", "Değişim"]
            for i, header in enumerate(headers):
                label = tk.Label(
                    table_frame, text=header, font=('Segoe UI', 11, 'bold'),
                    bg=self.colors['primary'], fg='white', relief='solid', bd=1,
                    padx=10, pady=8
                )
                label.grid(row=0, column=i, sticky='ew')
            
            # Safe numeric conversion
            if hasattr(self.data_ops, 'DataCleaner'):
                p1_kar = self.data_ops.DataCleaner.clean_numeric(period1.get('toplam_kar', 0))
                p2_kar = self.data_ops.DataCleaner.clean_numeric(period2.get('toplam_kar', 0))
            else:
                p1_kar = self.data_ops.clean_numeric(period1.get('toplam_kar', 0))
                p2_kar = self.data_ops.clean_numeric(period2.get('toplam_kar', 0))
            
            p1_urun = int(period1.get('urun_sayisi', 0))
            p2_urun = int(period2.get('urun_sayisi', 0))
            
            # Table rows
            rows = [
                ("Toplam Kar", f"₺{p1_kar:,.0f}", f"₺{p2_kar:,.0f}", f"₺{p2_kar - p1_kar:+,.0f}"),
                ("Ürün Sayısı", f"{p1_urun}", f"{p2_urun}", f"{p2_urun - p1_urun:+}"),
                ("Ort. Kar/Ürün", 
                 f"₺{p1_kar/p1_urun:,.0f}" if p1_urun > 0 else "₺0",
                 f"₺{p2_kar/p2_urun:,.0f}" if p2_urun > 0 else "₺0",
                 f"₺{(p2_kar/p2_urun if p2_urun > 0 else 0) - (p1_kar/p1_urun if p1_urun > 0 else 0):+,.0f}")
            ]
            
            for row_idx, row_data in enumerate(rows, 1):
                for col_idx, cell_data in enumerate(row_data):
                    bg_color = 'white' if row_idx % 2 == 1 else '#f8f9fa'
                    label = tk.Label(
                        table_frame, text=cell_data, font=('Segoe UI', 10),
                        bg=bg_color, fg=self.colors['text_primary'], relief='solid', bd=1,
                        padx=10, pady=6
                    )
                    label.grid(row=row_idx, column=col_idx, sticky='ew')
            
            # Configure grid
            for i in range(4):
                table_frame.grid_columnconfigure(i, weight=1)
                
        except Exception as e:
            self.logger.error(f"Simple comparison table creation error: {e}")
    
    def _show_message(self, title, message, msg_type="info"):
        """Show message with safety"""
        try:
            if msg_type == "error":
                messagebox.showerror(title, message)
            elif msg_type == "warning":
                messagebox.showwarning(title, message)
            else:
                messagebox.showinfo(title, message)
        except Exception as e:
            self.logger.error(f"Message display error: {e}")
            print(f"{title}: {message}")
    
    def _show_initialization_error(self, error_msg):
        """Show initialization error with fallback UI"""
        try:
            error_frame = ttk.Frame(self.notebook)
            self.notebook.add(error_frame, text="⚠️ Dönem Analizi (Hata)")
            
            error_container = tk.Frame(error_frame, bg='#f8fafc')
            error_container.pack(fill='both', expand=True, padx=20, pady=20)
            
            tk.Label(
                error_container,
                text="⚠️ Dönem Analizi Modülü Başlatılamadı",
                font=('Segoe UI', 16, 'bold'),
                fg='#ef4444',
                bg='#f8fafc'
            ).pack(pady=(50, 20))
            
            tk.Label(
                error_container,
                text=f"Hata: {error_msg}",
                font=('Segoe UI', 12),
                fg='#6b7280',
                bg='#f8fafc'
            ).pack()
            
            tk.Label(
                error_container,
                text="Lütfen gerekli modüllerin yüklü olduğundan emin olun.",
                font=('Segoe UI', 11),
                fg='#6b7280',
                bg='#f8fafc'
            ).pack(pady=20)
            
        except Exception as e:
            self.logger.error(f"Error display creation failed: {e}")
    
    def cleanup(self):
        """Comprehensive cleanup with safety"""
        if self._cleanup_scheduled:
            return
        
        try:
            self._cleanup_scheduled = True
            self._closing = True
            
            self.logger.info("Starting ZamanAnalizi cleanup...")
            
            # Wait for active threads
            for thread in list(self.active_threads):
                if thread.is_alive():
                    self.logger.info(f"Waiting for thread {thread.name} to finish...")
                    thread.join(timeout=2.0)
                    if thread.is_alive():
                        self.logger.warning(f"Thread {thread.name} did not finish in time")
            
            self.active_threads.clear()
            
            # Clear message queue
            try:
                while not self.message_queue.empty():
                    self.message_queue.get_nowait()
            except Exception:
                pass
            
            # Execute cleanup functions
            for cleanup_func in self.cleanup_functions:
                try:
                    cleanup_func()
                except Exception as e:
                    self.logger.debug(f"Cleanup function error: {e}")
            
            self.cleanup_functions.clear()
            
            # Clear widget references
            self._clear_widget_references()
            
            # Clear weak reference set
            self._widgets.clear()
            
            # Force garbage collection
            gc.collect()
            
            self.logger.info("ZamanAnalizi cleanup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
        finally:
            self._widgets_destroyed = True
    
    def _clear_widget_references(self):
        """Clear all widget references safely"""
        widget_attrs = [
            'main_frame', 'sub_notebook', 'start_date', 'end_date', 'period_name',
            'karlilik_path', 'iskonto_path', 'karlilik_label', 'iskonto_label',
            'history_tree', 'period1_combo', 'period2_combo', 'period1_var',
            'period2_var', 'comparison_canvas', 'comparison_results_frame'
        ]
        
        for attr in widget_attrs:
            try:
                setattr(self, attr, None)
            except Exception:
                pass
    
    def __del__(self):
        """Destructor with safety"""
        try:
            if not self._widgets_destroyed and not self._closing:
                self.cleanup()
        except Exception:
            pass