# analiz_dashboard.py - Profesyonel Düzeltilmiş Versiyon - Güvenlik: 9/10

import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import platform
import weakref
import gc
import logging
from typing import Optional, Dict, Any, List, Tuple, Union
from functools import lru_cache

# Modül importları - Güvenli fallback ile
try:
    from veri_analizi import VeriAnalizi
    VERI_ANALIZI_AVAILABLE = True
except ImportError:
    VERI_ANALIZI_AVAILABLE = False

try:
    from dashboard_components import DashboardComponents
    DASHBOARD_COMPONENTS_AVAILABLE = True
except ImportError:
    DASHBOARD_COMPONENTS_AVAILABLE = False

try:
    from ui_components import UIComponents
    UI_COMPONENTS_AVAILABLE = True
except ImportError:
    UI_COMPONENTS_AVAILABLE = False

try:
    from themes import get_colors, get_color
    THEMES_AVAILABLE = True
except ImportError:
    THEMES_AVAILABLE = False

try:
    from data_operations import DataCleaner, DataAnalyzer, DataValidator
    DATA_OPERATIONS_AVAILABLE = True
except ImportError:
    DATA_OPERATIONS_AVAILABLE = False


class SafeFallbacks:
    """Güvenli fallback implementasyonları"""
    
    @staticmethod
    def get_default_colors():
        """Varsayılan renk paleti"""
        return {
            'bg_primary': '#f8fafc',
            'bg_secondary': '#ffffff', 
            'bg_accent': '#e2e8f0',
            'bg_hover': '#f1f5f9',
            'primary': '#3b82f6',
            'primary_dark': '#2563eb',
            'primary_light': '#93c5fd',
            'success': '#10b981',
            'success_dark': '#059669',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'info': '#06b6d4',
            'text_primary': '#1f2937',
            'text_secondary': '#6b7280',
            'text_light': '#9ca3af',
            'border': '#e5e7eb',
            'shadow': '#f3f4f6',
            'input_bg': '#f8fafc'
        }
    
    @staticmethod
    def safe_numeric_conversion(value, default=0.0):
        """Güvenli sayısal dönüşüm"""
        try:
            if pd.isna(value):
                return default
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                cleaned = value.replace('₺', '').replace('TL', '').replace(',', '.').strip()
                return float(cleaned)
            return default
        except (ValueError, TypeError):
            return default


class DataValidationError(Exception):
    """Veri doğrulama hatası"""
    pass


class WidgetError(Exception):
    """Widget işlem hatası"""
    pass


class AnalyzDashboard:
    """
    Modern Dashboard arayüzü - Profesyonel Refactored Versiyon
    Güvenilirlik: 9/10
    """
    
    def __init__(self, parent_notebook: ttk.Notebook, df: pd.DataFrame):
        """
        Dashboard başlatıcı - Comprehensive error handling ile
        
        Args:
            parent_notebook: Ana notebook widget'ı
            df: Analiz edilecek DataFrame
        """
        # Logging setup
        self._setup_logging()
        
        # State management
        self._is_destroyed = False
        self._cleanup_scheduled = False
        self._widget_refs = weakref.WeakSet()
        self._cleanup_functions = []
        
        # Core attributes with validation
        self.notebook = self._validate_notebook(parent_notebook)
        self.df = self._validate_and_prepare_dataframe(df)
        
        # Platform detection
        self.os_platform = platform.system()
        
        # Initialize systems with fallbacks
        self._init_color_system()
        self._init_analysis_system()
        
        # Dashboard frame - ANA DEĞİŞİKLİK: main_container'ı döndüreceğiz
        self.main_container = None
        self.dashboard_frame = None
        self.canvas = None
        self.scrollable_frame = None
        self.scrollbar = None
        self.main_frame = None
        
        # Setup dashboard
        self._safe_setup_dashboard()
    
    def _setup_logging(self):
        """Logging sistemi kurulumu"""
        try:
            self.logger = logging.getLogger(f"{__name__}_{id(self)}")
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.INFO)
        except Exception:
            # Fallback logger
            class FallbackLogger:
                def info(self, msg): print(f"Dashboard INFO: {msg}")
                def error(self, msg): print(f"Dashboard ERROR: {msg}")
                def warning(self, msg): print(f"Dashboard WARNING: {msg}")
                def debug(self, msg): print(f"Dashboard DEBUG: {msg}")
            self.logger = FallbackLogger()
    
    def _validate_notebook(self, notebook: ttk.Notebook) -> ttk.Notebook:
        """Notebook widget'ını doğrula"""
        if notebook is None:
            raise ValueError("Parent notebook cannot be None")
        
        try:
            if not notebook.winfo_exists():
                raise ValueError("Parent notebook is destroyed")
        except tk.TclError:
            raise ValueError("Parent notebook is invalid")
        
        return notebook
    
    def _validate_and_prepare_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame'i doğrula ve hazırla"""
        if df is None:
            self.logger.warning("DataFrame is None, creating empty DataFrame")
            return pd.DataFrame()
        
        if df.empty:
            self.logger.warning("DataFrame is empty")
            return pd.DataFrame()
        
        try:
            # Deep copy for safety
            validated_df = df.copy(deep=True)
            
            # Data type optimization
            for col in validated_df.columns:
                if validated_df[col].dtype == 'object':
                    try:
                        # String sütunlarını optimize et
                        validated_df[col] = validated_df[col].astype('string')
                    except Exception:
                        pass
            
            self.logger.info(f"DataFrame validated: {len(validated_df)} rows, {len(validated_df.columns)} columns")
            return validated_df
            
        except Exception as e:
            self.logger.error(f"DataFrame validation error: {e}")
            return pd.DataFrame()
    
    def _init_color_system(self):
        """Renk sistemi başlatma"""
        try:
            if THEMES_AVAILABLE:
                self.colors = get_colors()
                self.logger.debug("Theme system loaded successfully")
            else:
                self.colors = SafeFallbacks.get_default_colors()
                self.logger.warning("Using fallback color system")
        except Exception as e:
            self.logger.error(f"Color system initialization error: {e}")
            self.colors = SafeFallbacks.get_default_colors()
    
    def _init_analysis_system(self):
        """Analiz sistemi başlatma"""
        try:
            if VERI_ANALIZI_AVAILABLE and not self.df.empty:
                self.analiz = VeriAnalizi(self.df)
                self.logger.debug("VeriAnalizi initialized successfully")
            else:
                self.analiz = None
                if not VERI_ANALIZI_AVAILABLE:
                    self.logger.warning("VeriAnalizi module not available")
                else:
                    self.logger.warning("DataFrame empty, VeriAnalizi not initialized")
        except Exception as e:
            self.logger.error(f"Analysis system initialization error: {e}")
            self.analiz = None
    
    def _safe_setup_dashboard(self):
        """Dashboard kurulumunu güvenli şekilde yap"""
        try:
            self._create_scrollable_frame()
            self._create_header()
            self._create_kpi_section()
            self._create_analysis_tabs()
            self._create_search_section()
            
            self.logger.info("Dashboard setup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Dashboard setup error: {e}")
            self._create_error_dashboard(str(e))
    
    def _create_error_dashboard(self, error_msg: str):
        """Hata durumunda basit dashboard oluştur"""
        try:
            # ANA DEĞİŞİKLİK: main_container oluştur
            self.main_container = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
            self._widget_refs.add(self.main_container)
            
            error_container = tk.Frame(self.main_container, bg=self.colors['bg_primary'])
            error_container.pack(fill='both', expand=True, padx=20, pady=20)
            
            tk.Label(
                error_container,
                text="Dashboard Yükleme Hatası",
                font=('Segoe UI', 16, 'bold'),
                fg=self.colors['danger'],
                bg=self.colors['bg_primary']
            ).pack(pady=(50, 20))
            
            tk.Label(
                error_container,
                text=f"Hata: {error_msg}",
                font=('Segoe UI', 12),
                fg=self.colors['text_secondary'],
                bg=self.colors['bg_primary']
            ).pack()
            
        except Exception as e:
            self.logger.error(f"Error dashboard creation failed: {e}")
    
    def get_frame(self) -> Optional[tk.Frame]:
        """Dashboard frame'ini güvenli şekilde döndür - ANA DÜZELTME"""
        try:
            # ANA DEĞİŞİKLİK: main_container'ı döndür, dashboard_frame değil
            if self.main_container and self.main_container.winfo_exists():
                return self.main_container
            return None
        except (tk.TclError, AttributeError):
            return None
    
    def _check_widget_exists(self, widget) -> bool:
        """Widget varlığını güvenli şekilde kontrol et"""
        try:
            return widget is not None and widget.winfo_exists()
        except (tk.TclError, AttributeError):
            return False
    
    def _create_scrollable_frame(self):
        """Scroll edilebilir ana frame oluştur"""
        try:
            # Ana container - ANA DEĞİŞİKLİK: main_container'ı oluştur
            self.main_container = tk.Frame(self.notebook, bg=self.colors['bg_primary'])
            self._widget_refs.add(self.main_container)
            
            # Dashboard frame
            self.dashboard_frame = ttk.Frame(self.main_container)
            self.dashboard_frame.pack(fill='both', expand=True)
            self._widget_refs.add(self.dashboard_frame)
            
            # Scroll container
            scroll_container = tk.Frame(self.dashboard_frame, bg=self.colors['bg_primary'])
            scroll_container.pack(fill='both', expand=True, padx=20, pady=20)
            self._widget_refs.add(scroll_container)
            
            # UI Components ile scrollable frame oluştur
            if UI_COMPONENTS_AVAILABLE:
                try:
                    self.canvas, self.scrollable_frame, self.scrollbar = UIComponents.create_scrollable_frame(
                        scroll_container, 
                        self.colors, 
                        setup_mouse_wheel=True
                    )
                    
                    if self.canvas:
                        self._widget_refs.add(self.canvas)
                    if self.scrollable_frame:
                        self._widget_refs.add(self.scrollable_frame)
                    if self.scrollbar:
                        self._widget_refs.add(self.scrollbar)
                        
                except Exception as e:
                    self.logger.warning(f"UIComponents scrollable frame failed: {e}")
                    self._create_fallback_scrollable_frame(scroll_container)
            else:
                self._create_fallback_scrollable_frame(scroll_container)
            
            # Ana içerik frame
            if self.scrollable_frame and self._check_widget_exists(self.scrollable_frame):
                self.main_frame = tk.Frame(self.scrollable_frame, bg=self.colors['bg_primary'])
                self.main_frame.pack(fill='both', expand=True, padx=30, pady=30)
                self._widget_refs.add(self.main_frame)
            else:
                raise WidgetError("Scrollable frame creation failed")
                
        except Exception as e:
            self.logger.error(f"Scrollable frame creation error: {e}")
            # Fallback basit frame
            self.main_frame = tk.Frame(self.dashboard_frame, bg=self.colors['bg_primary'])
            self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            self._widget_refs.add(self.main_frame)
    
    def _create_fallback_scrollable_frame(self, parent):
        """Fallback scrollable frame"""
        try:
            self.canvas = tk.Canvas(parent, bg=self.colors['bg_primary'], highlightthickness=0)
            self.scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
            self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg_primary'])
            
            def configure_scroll_region(event=None):
                if self._check_widget_exists(self.canvas):
                    self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            self.scrollable_frame.bind("<Configure>", configure_scroll_region)
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            
            canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            
            self.canvas.pack(side="left", fill="both", expand=True)
            self.scrollbar.pack(side="right", fill="y")
            
            # Widget referanslarını kaydet
            for widget in [self.canvas, self.scrollbar, self.scrollable_frame]:
                if widget:
                    self._widget_refs.add(widget)
                    
        except Exception as e:
            self.logger.error(f"Fallback scrollable frame error: {e}")
            # En son fallback
            self.scrollable_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
            self.scrollable_frame.pack(fill='both', expand=True)
            self._widget_refs.add(self.scrollable_frame)
    
    def _create_header(self):
        """Modern header oluştur"""
        try:
            if not self._check_widget_exists(self.main_frame):
                raise WidgetError("Main frame not available for header")
            
            header_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'], height=120)
            header_frame.pack(fill='x', pady=(0, 30))
            header_frame.pack_propagate(False)
            self._widget_refs.add(header_frame)
            
            # Gradient container
            gradient_frame = tk.Frame(header_frame, bg=self.colors['primary'])
            gradient_frame.pack(fill='both', expand=True)
            self._widget_refs.add(gradient_frame)
            
            # Header içerik
            content_frame = tk.Frame(gradient_frame, bg=self.colors['primary'])
            content_frame.pack(expand=True, fill='both', padx=40, pady=30)
            self._widget_refs.add(content_frame)
            
            # Ana başlık
            title_label = tk.Label(
                content_frame,
                text="📊 Karlılık Analizi Dashboard",
                font=('Segoe UI', 24, 'bold'),
                fg='white',
                bg=self.colors['primary']
            )
            title_label.pack(anchor='w')
            self._widget_refs.add(title_label)
            
            # Alt başlık
            product_count = len(self.df) if not self.df.empty else 0
            subtitle_text = f"Toplam {product_count} ürün detaylı analizi"
            
            subtitle_label = tk.Label(
                content_frame,
                text=subtitle_text,
                font=('Segoe UI', 14),
                fg=self.colors.get('primary_light', '#bfdbfe'),
                bg=self.colors['primary']
            )
            subtitle_label.pack(anchor='w', pady=(5, 0))
            self._widget_refs.add(subtitle_label)
            
        except Exception as e:
            self.logger.error(f"Header creation error: {e}")
    
    @lru_cache(maxsize=1)
    def _get_kpi_data(self) -> Dict[str, Any]:
        """KPI verilerini cache ile al"""
        try:
            if self.analiz is not None:
                return self.analiz.get_kpi_summary()
            else:
                return self._get_fallback_kpi_data()
        except Exception as e:
            self.logger.error(f"KPI data retrieval error: {e}")
            return self._get_fallback_kpi_data()
    
    def _get_fallback_kpi_data(self) -> Dict[str, Any]:
        """Fallback KPI verisi hesapla"""
        try:
            if self.df.empty:
                return self._get_empty_kpi_data()
            
            kpi_data = {
                'toplam_kar': 0,
                'en_karli_urun': 'Veri Yok',
                'en_karli_urun_kar': 0,
                'ortalama_kar': 0,
                'toplam_urun': len(self.df),
                'pozitif_kar_urun': 0,
                'negatif_kar_urun': 0,
                'toplam_satis_miktar': 0
            }
            
            # Net Kar sütunu varsa hesapla
            if 'Net Kar' in self.df.columns:
                try:
                    net_kar_series = self.df['Net Kar'].apply(SafeFallbacks.safe_numeric_conversion)
                    valid_kar = net_kar_series.dropna()
                    
                    if not valid_kar.empty:
                        kpi_data['toplam_kar'] = float(valid_kar.sum())
                        kpi_data['ortalama_kar'] = float(valid_kar.mean())
                        kpi_data['pozitif_kar_urun'] = int(len(valid_kar[valid_kar > 0]))
                        kpi_data['negatif_kar_urun'] = int(len(valid_kar[valid_kar < 0]))
                        
                        # En karlı ürün
                        max_idx = valid_kar.idxmax()
                        if pd.notna(max_idx) and max_idx in self.df.index:
                            kpi_data['en_karli_urun_kar'] = float(valid_kar.loc[max_idx])
                            
                            # Stok ismi bul
                            for col in self.df.columns:
                                if 'stok' in col.lower() and 'ismi' in col.lower():
                                    product_name = self.df.loc[max_idx, col]
                                    if pd.notna(product_name):
                                        kpi_data['en_karli_urun'] = str(product_name)[:50]
                                    break
                
                except Exception as e:
                    self.logger.warning(f"Fallback KPI calculation error: {e}")
            
            return kpi_data
            
        except Exception as e:
            self.logger.error(f"Fallback KPI data error: {e}")
            return self._get_empty_kpi_data()
    
    def _get_empty_kpi_data(self) -> Dict[str, Any]:
        """Boş KPI verisi"""
        return {
            'toplam_kar': 0,
            'en_karli_urun': 'Veri Yok',
            'en_karli_urun_kar': 0,
            'ortalama_kar': 0,
            'toplam_urun': 0,
            'pozitif_kar_urun': 0,
            'negatif_kar_urun': 0,
            'toplam_satis_miktar': 0
        }
    
    def _create_kpi_section(self):
        """KPI kartları bölümü oluştur"""
        try:
            if not self._check_widget_exists(self.main_frame):
                raise WidgetError("Main frame not available for KPI section")
            
            # Section başlığı
            self._create_section_title(
                self.main_frame, 
                "🎯 Performans Özeti", 
                "Ana performans metrikleri"
            )
            
            # KPI verilerini al
            kpi_data = self._get_kpi_data()
            
            # KPI kartları container
            kpi_container = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
            kpi_container.pack(fill='x', pady=(0, 40))
            self._widget_refs.add(kpi_container)
            
            # İlk satır KPI kartları
            kpi_row1 = tk.Frame(kpi_container, bg=self.colors['bg_primary'])
            kpi_row1.pack(fill='x', pady=(0, 20))
            self._widget_refs.add(kpi_row1)
            
            # En karlı ürün adını güvenli şekilde kısalt
            en_karli_urun_text = str(kpi_data.get('en_karli_urun', 'Veri Yok'))
            if len(en_karli_urun_text) > 20:
                en_karli_urun_text = en_karli_urun_text[:20] + "..."
            
            # KPI kartlarını oluştur
            self._create_kpi_cards_row1(kpi_row1, kpi_data, en_karli_urun_text)
            
            # İkinci satır KPI kartları
            kpi_row2 = tk.Frame(kpi_container, bg=self.colors['bg_primary'])
            kpi_row2.pack(fill='x')
            self._widget_refs.add(kpi_row2)
            
            self._create_kpi_cards_row2(kpi_row2, kpi_data)
            
            # Grid konfigürasyonu
            for i in range(4):
                kpi_row1.grid_columnconfigure(i, weight=1)
                kpi_row2.grid_columnconfigure(i, weight=1)
                
        except Exception as e:
            self.logger.error(f"KPI section creation error: {e}")
    
    def _create_kpi_cards_row1(self, parent, kpi_data, en_karli_urun_text):
        """İlk satır KPI kartları"""
        try:
            cards_data = [
                ("💰", "Toplam Net Kar", f"₺{kpi_data.get('toplam_kar', 0):,.0f}", self.colors['success']),
                ("🏆", "En Karlı Ürün", en_karli_urun_text, self.colors['primary']),
                ("📈", "Ortalama Kar", f"₺{kpi_data.get('ortalama_kar', 0):,.0f}", self.colors['warning']),
                ("📦", "Toplam Ürün", f"{kpi_data.get('toplam_urun', 0)} adet", self.colors['info'])
            ]
            
            for i, (icon, title, value, color) in enumerate(cards_data):
                self._create_modern_kpi_card(parent, icon, title, value, color, i)
                
        except Exception as e:
            self.logger.error(f"KPI cards row 1 creation error: {e}")
    
    def _create_kpi_cards_row2(self, parent, kpi_data):
        """İkinci satır KPI kartları"""
        try:
            cards_data = [
                ("✅", "Karlı Ürün", f"{kpi_data.get('pozitif_kar_urun', 0)} adet", self.colors['success']),
                ("❌", "Zararlı Ürün", f"{kpi_data.get('negatif_kar_urun', 0)} adet", self.colors['danger']),
                ("🎯", "En Yüksek Kar", f"₺{kpi_data.get('en_karli_urun_kar', 0):,.0f}", self.colors.get('primary_dark', '#8b5cf6')),
                ("📊", "Toplam Satış", f"{kpi_data.get('toplam_satis_miktar', 0):,.0f} adet", self.colors['info'])
            ]
            
            for i, (icon, title, value, color) in enumerate(cards_data):
                self._create_modern_kpi_card(parent, icon, title, value, color, i)
                
        except Exception as e:
            self.logger.error(f"KPI cards row 2 creation error: {e}")
    
    def _create_modern_kpi_card(self, parent, icon, title, value, color, column):
        """Modern KPI kartı oluştur"""
        try:
            if DASHBOARD_COMPONENTS_AVAILABLE:
                DashboardComponents.create_modern_kpi_card(parent, icon, title, value, color, column)
            else:
                self._create_fallback_kpi_card(parent, icon, title, value, color, column)
        except Exception as e:
            self.logger.error(f"KPI card creation error: {e}")
            self._create_fallback_kpi_card(parent, icon, title, value, color, column)
    
    def _create_fallback_kpi_card(self, parent, icon, title, value, color, column):
        """Fallback KPI kartı"""
        try:
            card_container = tk.Frame(parent, bg=self.colors['bg_primary'])
            card_container.grid(row=0, column=column, padx=12, pady=8, sticky='ew')
            self._widget_refs.add(card_container)
            
            card_frame = tk.Frame(card_container, bg=self.colors['bg_secondary'], relief='solid', bd=1)
            card_frame.pack(fill='both', expand=True)
            self._widget_refs.add(card_frame)
            
            inner_frame = tk.Frame(card_frame, bg=self.colors['bg_secondary'])
            inner_frame.pack(fill='both', expand=True, padx=20, pady=15)
            self._widget_refs.add(inner_frame)
            
            # Icon
            icon_label = tk.Label(inner_frame, text=str(icon), font=('Segoe UI', 16), 
                                 fg=color, bg=self.colors['bg_secondary'])
            icon_label.pack()
            self._widget_refs.add(icon_label)
            
            # Title
            title_label = tk.Label(inner_frame, text=str(title), font=('Segoe UI', 10, 'bold'),
                                  fg=self.colors['text_secondary'], bg=self.colors['bg_secondary'])
            title_label.pack(pady=(8, 5))
            self._widget_refs.add(title_label)
            
            # Value
            value_label = tk.Label(inner_frame, text=str(value), font=('Segoe UI', 14, 'bold'),
                                  fg=self.colors['text_primary'], bg=self.colors['bg_secondary'])
            value_label.pack()
            self._widget_refs.add(value_label)
            
        except Exception as e:
            self.logger.error(f"Fallback KPI card creation error: {e}")
    
    def _create_section_title(self, parent, title, subtitle=None):
        """Section başlığı oluştur"""
        try:
            if DASHBOARD_COMPONENTS_AVAILABLE:
                DashboardComponents.create_section_title(parent, title, subtitle)
            else:
                self._create_fallback_section_title(parent, title, subtitle)
        except Exception as e:
            self.logger.error(f"Section title creation error: {e}")
            self._create_fallback_section_title(parent, title, subtitle)
    
    def _create_fallback_section_title(self, parent, title, subtitle=None):
        """Fallback section başlığı"""
        try:
            header_frame = tk.Frame(parent, bg=self.colors['primary'], height=80)
            header_frame.pack(fill='x', pady=(0, 20))
            header_frame.pack_propagate(False)
            self._widget_refs.add(header_frame)
            
            title_label = tk.Label(header_frame, text=title, font=('Segoe UI', 16, 'bold'),
                                  fg='white', bg=self.colors['primary'])
            title_label.pack(expand=True)
            self._widget_refs.add(title_label)
            
            if subtitle:
                subtitle_label = tk.Label(header_frame, text=subtitle, font=('Segoe UI', 12),
                                         fg='#bfdbfe', bg=self.colors['primary'])
                subtitle_label.pack(expand=True)
                self._widget_refs.add(subtitle_label)
                
        except Exception as e:
            self.logger.error(f"Fallback section title creation error: {e}")
    
    def _create_analysis_tabs(self):
        """Modern analiz sekmeleri oluştur"""
        try:
            if not self._check_widget_exists(self.main_frame):
                raise WidgetError("Main frame not available for analysis tabs")
            
            self._create_section_title(
                self.main_frame, 
                "📊 Detaylı Analizler", 
                "Ürün performans analizleri"
            )
            
            # Tab container
            tab_container = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
            tab_container.pack(fill='x', pady=(0, 40))
            self._widget_refs.add(tab_container)
            
            # Tab notebook
            self.analysis_notebook = ttk.Notebook(tab_container)
            self.analysis_notebook.pack(fill='both', expand=True)
            self._widget_refs.add(self.analysis_notebook)
            
            # Tabs oluştur
            self._create_performance_tab()
            self._create_profit_tab()
            self._create_distribution_tab()
            
        except Exception as e:
            self.logger.error(f"Analysis tabs creation error: {e}")
    
    def _create_performance_tab(self):
        """Performans analizi sekmesi"""
        try:
            perf_frame = ttk.Frame(self.analysis_notebook)
            self.analysis_notebook.add(perf_frame, text="🏆 Performans")
            self._widget_refs.add(perf_frame)
            
            main_container = tk.Frame(perf_frame, bg=self.colors['bg_secondary'])
            main_container.pack(fill='both', expand=True, padx=20, pady=20)
            self._widget_refs.add(main_container)
            
            # Top products section
            top_section = tk.Frame(main_container, bg=self.colors['bg_secondary'])
            top_section.pack(fill='both', expand=True, pady=(0, 15))
            self._widget_refs.add(top_section)
            
            # Sol: En karlı ürünler
            left_container = tk.Frame(top_section, bg=self.colors['bg_secondary'])
            left_container.pack(side='left', fill='both', expand=True, padx=(0, 10))
            self._widget_refs.add(left_container)
            
            left_frame = tk.Frame(left_container, bg=self.colors['bg_secondary'], relief='flat')
            left_frame.pack(fill='both', expand=True)
            self._widget_refs.add(left_frame)
            
            # Header
            left_header = tk.Frame(left_frame, bg=self.colors['primary'], height=40)
            left_header.pack(fill='x')
            left_header.pack_propagate(False)
            self._widget_refs.add(left_header)
            
            left_title = tk.Label(
                left_header,
                text="🔥 En Karlı Ürünler (Top 10)",
                font=('Segoe UI', 12, 'bold'),
                fg='white',
                bg=self.colors['primary']
            )
            left_title.pack(expand=True)
            self._widget_refs.add(left_title)
            
            # Sağ: En çok satan ürünler
            right_container = tk.Frame(top_section, bg=self.colors['bg_secondary'])
            right_container.pack(side='right', fill='both', expand=True, padx=(10, 0))
            self._widget_refs.add(right_container)
            
            right_frame = tk.Frame(right_container, bg=self.colors['bg_secondary'], relief='flat')
            right_frame.pack(fill='both', expand=True)
            self._widget_refs.add(right_frame)
            
            # Header
            right_header = tk.Frame(right_frame, bg=self.colors['info'], height=40)
            right_header.pack(fill='x')
            right_header.pack_propagate(False)
            self._widget_refs.add(right_header)
            
            right_title = tk.Label(
                right_header,
                text="📈 En Çok Satan Ürünler (Top 10)",
                font=('Segoe UI', 12, 'bold'),
                fg='white',
                bg=self.colors['info']
            )
            right_title.pack(expand=True)
            self._widget_refs.add(right_title)
            
            # Veri listelerini oluştur
            self._create_product_lists(left_frame, right_frame)
            
        except Exception as e:
            self.logger.error(f"Performance tab creation error: {e}")
    
    def _create_product_lists(self, left_frame, right_frame):
        """Ürün listelerini oluştur"""
        try:
            top_profitable = pd.DataFrame()
            top_selling = pd.DataFrame()
            miktar_col = None
            
            if self.analiz:
                try:
                    top_profitable = self.analiz.get_top_profitable_products(10)
                    top_selling = self.analiz.get_top_selling_products(10)
                    miktar_col = self.analiz.find_miktar_column()
                except Exception as e:
                    self.logger.warning(f"Analysis data retrieval error: {e}")
            else:
                # Fallback analiz
                top_profitable, top_selling, miktar_col = self._get_fallback_product_lists()
            
            # DashboardComponents ile liste oluştur
            if DASHBOARD_COMPONENTS_AVAILABLE:
                try:
                    DashboardComponents.create_modern_product_list(
                        left_frame, top_profitable, 'Net Kar', self.colors['success'], self.analiz
                    )
                    DashboardComponents.create_modern_product_list(
                        right_frame, top_selling, miktar_col if miktar_col else 'Miktar', 
                        self.colors['info'], self.analiz
                    )
                except Exception as e:
                    self.logger.warning(f"DashboardComponents product list error: {e}")
                    self._create_fallback_product_lists(left_frame, right_frame, top_profitable, top_selling, miktar_col)
            else:
                self._create_fallback_product_lists(left_frame, right_frame, top_profitable, top_selling, miktar_col)
                
        except Exception as e:
            self.logger.error(f"Product lists creation error: {e}")
    
    def _get_fallback_product_lists(self):
        """Fallback ürün listeleri"""
        try:
            if self.df.empty:
                return pd.DataFrame(), pd.DataFrame(), None
            
            top_profitable = pd.DataFrame()
            top_selling = pd.DataFrame()
            miktar_col = None
            
            # Net Kar sütunu varsa en karlı ürünleri al
            if 'Net Kar' in self.df.columns:
                try:
                    df_copy = self.df.copy()
                    df_copy['Net Kar'] = df_copy['Net Kar'].apply(SafeFallbacks.safe_numeric_conversion)
                    top_profitable = df_copy.nlargest(10, 'Net Kar')
                except Exception as e:
                    self.logger.warning(f"Top profitable fallback error: {e}")
            
            # Miktar sütunu bul ve en çok satanları al
            for col in self.df.columns:
                if 'miktar' in col.lower() or 'satis' in col.lower():
                    miktar_col = col
                    try:
                        df_copy = self.df.copy()
                        df_copy[col] = df_copy[col].apply(SafeFallbacks.safe_numeric_conversion)
                        top_selling = df_copy.nlargest(10, col)
                        break
                    except Exception as e:
                        self.logger.warning(f"Top selling fallback error: {e}")
            
            return top_profitable, top_selling, miktar_col
            
        except Exception as e:
            self.logger.error(f"Fallback product lists error: {e}")
            return pd.DataFrame(), pd.DataFrame(), None
    
    def _create_fallback_product_lists(self, left_frame, right_frame, top_profitable, top_selling, miktar_col):
        """Fallback ürün listeleri UI"""
        try:
            # Sol taraf - En karlı ürünler
            if not top_profitable.empty:
                self._create_simple_product_list(left_frame, top_profitable, 'Net Kar', 'En Karlı Ürünler')
            else:
                self._create_no_data_label(left_frame, "En karlı ürün verisi bulunamadı")
            
            # Sağ taraf - En çok satanlar
            if not top_selling.empty and miktar_col:
                self._create_simple_product_list(right_frame, top_selling, miktar_col, 'En Çok Satan Ürünler')
            else:
                self._create_no_data_label(right_frame, "Satış miktarı verisi bulunamadı")
                
        except Exception as e:
            self.logger.error(f"Fallback product lists UI error: {e}")
    
    def _create_simple_product_list(self, parent, df, value_column, title):
        """Basit ürün listesi"""
        try:
            # Stok sütunu bul
            stok_col = None
            for col in df.columns:
                if 'stok' in col.lower() and 'ismi' in col.lower():
                    stok_col = col
                    break
            
            if not stok_col and len(df.columns) > 0:
                stok_col = df.columns[0]
            
            if not stok_col:
                self._create_no_data_label(parent, f"{title} - Stok sütunu bulunamadı")
                return
            
            # Liste container
            list_container = tk.Frame(parent, bg=self.colors['bg_secondary'])
            list_container.pack(fill='both', expand=True, padx=15, pady=(0, 15))
            self._widget_refs.add(list_container)
            
            # İlk 5 ürün
            for i, (_, row) in enumerate(df.head(5).iterrows()):
                try:
                    item_frame = tk.Frame(list_container, bg='white', relief='solid', bd=1)
                    item_frame.pack(fill='x', pady=2)
                    self._widget_refs.add(item_frame)
                    
                    # Ürün adı
                    product_name = str(row[stok_col]) if pd.notna(row[stok_col]) else "Bilinmiyor"
                    if len(product_name) > 30:
                        product_name = product_name[:30] + "..."
                    
                    name_label = tk.Label(
                        item_frame, text=f"{i+1}. {product_name}",
                        font=('Segoe UI', 10), fg=self.colors['text_primary'], bg='white'
                    )
                    name_label.pack(side='left', padx=10, pady=5)
                    self._widget_refs.add(name_label)
                    
                    # Değer
                    try:
                        value = SafeFallbacks.safe_numeric_conversion(row[value_column])
                        if 'kar' in value_column.lower():
                            value_text = f"₺{value:,.0f}"
                        else:
                            value_text = f"{value:,.0f}"
                    except:
                        value_text = "N/A"
                    
                    value_label = tk.Label(
                        item_frame, text=value_text,
                        font=('Segoe UI', 10, 'bold'), fg=self.colors['primary'], bg='white'
                    )
                    value_label.pack(side='right', padx=10, pady=5)
                    self._widget_refs.add(value_label)
                    
                except Exception as e:
                    self.logger.warning(f"Product list item error: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Simple product list creation error: {e}")
            self._create_no_data_label(parent, f"{title} - Liste oluşturulamadı")
    
    def _create_no_data_label(self, parent, message):
        """Veri yok etiketi"""
        try:
            no_data_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
            no_data_frame.pack(fill='both', expand=True, padx=30, pady=30)
            self._widget_refs.add(no_data_frame)
            
            no_data_label = tk.Label(
                no_data_frame, text=message,
                font=('Segoe UI', 12), fg=self.colors['text_secondary'], bg=self.colors['bg_secondary']
            )
            no_data_label.pack(expand=True)
            self._widget_refs.add(no_data_label)
            
        except Exception as e:
            self.logger.error(f"No data label creation error: {e}")
    
    def _create_profit_tab(self):
        """Kar analizi sekmesi"""
        try:
            profit_frame = ttk.Frame(self.analysis_notebook)
            self.analysis_notebook.add(profit_frame, text="💰 Kar Analizi")
            self._widget_refs.add(profit_frame)
            
            main_container = tk.Frame(profit_frame, bg=self.colors['bg_secondary'])
            main_container.pack(fill='both', expand=True, padx=20, pady=20)
            self._widget_refs.add(main_container)
            
            # Kar dağılımı
            self._create_profit_distribution_section(main_container)
            
            # Düşük performanslı ürünler
            self._create_low_performance_section(main_container)
            
        except Exception as e:
            self.logger.error(f"Profit tab creation error: {e}")
    
    def _create_profit_distribution_section(self, parent):
        """Kar dağılımı bölümü"""
        try:
            # Kar dağılımı verilerini al
            if self.analiz:
                try:
                    dist_data = self.analiz.get_profit_distribution()
                except Exception as e:
                    self.logger.warning(f"Analysis profit distribution error: {e}")
                    dist_data = self._get_fallback_profit_distribution()
            else:
                dist_data = self._get_fallback_profit_distribution()
            
            # Başlık
            dist_title = tk.Label(
                parent, text="📊 Kar Dağılımı",
                font=('Segoe UI', 16, 'bold'), fg=self.colors['text_primary'], bg=self.colors['bg_secondary']
            )
            dist_title.pack(anchor='w', pady=(0, 20))
            self._widget_refs.add(dist_title)
            
            # Kar dağılım kartları
            dist_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
            dist_frame.pack(fill='x', pady=(0, 20))
            self._widget_refs.add(dist_frame)
            
            self._create_profit_distribution_cards(dist_frame, dist_data)
            
        except Exception as e:
            self.logger.error(f"Profit distribution section error: {e}")
    
    def _get_fallback_profit_distribution(self):
        """Fallback kar dağılımı"""
        try:
            if self.df.empty or 'Net Kar' not in self.df.columns:
                return {'cok_karli': 0, 'orta_karli': 0, 'dusuk_karli': 0, 'zararda': 0}
            
            kar_series = self.df['Net Kar'].apply(SafeFallbacks.safe_numeric_conversion)
            kar_data = kar_series.dropna()
            
            if kar_data.empty:
                return {'cok_karli': 0, 'orta_karli': 0, 'dusuk_karli': 0, 'zararda': 0}
            
            # Zarardaki ürünler
            zararda = len(kar_data[kar_data < 0])
            
            # Pozitif kar değerleri
            pozitif_kar = kar_data[kar_data >= 0]
            
            if pozitif_kar.empty:
                return {'cok_karli': 0, 'orta_karli': 0, 'dusuk_karli': 0, 'zararda': int(zararda)}
            
            if len(pozitif_kar) == 1:
                return {'cok_karli': 1, 'orta_karli': 0, 'dusuk_karli': 0, 'zararda': int(zararda)}
            
            # Quantile hesaplama
            try:
                q33 = pozitif_kar.quantile(0.33)
                q67 = pozitif_kar.quantile(0.67)
                
                dusuk_karli = len(pozitif_kar[pozitif_kar < q33])
                orta_karli = len(pozitif_kar[(pozitif_kar >= q33) & (pozitif_kar < q67)])
                cok_karli = len(pozitif_kar[pozitif_kar >= q67])
                
            except (ValueError, TypeError):
                pozitif_count = len(pozitif_kar)
                cok_karli = pozitif_count // 3
                orta_karli = pozitif_count // 3
                dusuk_karli = pozitif_count - cok_karli - orta_karli
            
            return {
                'cok_karli': int(cok_karli),
                'orta_karli': int(orta_karli),
                'dusuk_karli': int(dusuk_karli),
                'zararda': int(zararda)
            }
            
        except Exception as e:
            self.logger.error(f"Fallback profit distribution error: {e}")
            return {'cok_karli': 0, 'orta_karli': 0, 'dusuk_karli': 0, 'zararda': 0}
    
    def _create_profit_distribution_cards(self, parent, dist_data):
        """Kar dağılım kartları"""
        try:
            profit_colors = [self.colors['success'], self.colors['warning'], 
                           self.colors.get('warning_dark', '#f97316'), self.colors['danger']]
            profit_data = [
                ("📈", "Çok Karlı", dist_data.get('cok_karli', 0)),
                ("⚖️", "Orta Karlı", dist_data.get('orta_karli', 0)),
                ("📉", "Düşük Karlı", dist_data.get('dusuk_karli', 0)),
                ("❌", "Zararda", dist_data.get('zararda', 0))
            ]
            
            for i, ((icon, title, value), color) in enumerate(zip(profit_data, profit_colors)):
                if DASHBOARD_COMPONENTS_AVAILABLE:
                    try:
                        DashboardComponents.create_profit_card(parent, icon, title, value, color, i)
                    except Exception as e:
                        self.logger.warning(f"DashboardComponents profit card error: {e}")
                        self._create_fallback_profit_card(parent, icon, title, value, color, i)
                else:
                    self._create_fallback_profit_card(parent, icon, title, value, color, i)
            
            # Grid konfigürasyonu
            for i in range(4):
                parent.grid_columnconfigure(i, weight=1)
                
        except Exception as e:
            self.logger.error(f"Profit distribution cards error: {e}")
    
    def _create_fallback_profit_card(self, parent, icon, title, value, color, column):
        """Fallback kar kartı"""
        try:
            card_container = tk.Frame(parent, bg=self.colors['bg_secondary'])
            card_container.grid(row=0, column=column, padx=12, pady=8, sticky='ew')
            self._widget_refs.add(card_container)
            
            card_frame = tk.Frame(card_container, bg=color, relief='flat')
            card_frame.pack(fill='both', expand=True)
            self._widget_refs.add(card_frame)
            
            inner_frame = tk.Frame(card_frame, bg=color)
            inner_frame.pack(fill='both', expand=True, padx=20, pady=20)
            self._widget_refs.add(inner_frame)
            
            # Icon
            icon_label = tk.Label(inner_frame, text=str(icon), font=('Segoe UI', 20), fg='white', bg=color)
            icon_label.pack()
            self._widget_refs.add(icon_label)
            
            # Title
            title_label = tk.Label(inner_frame, text=str(title), font=('Segoe UI', 11, 'bold'), fg='white', bg=color)
            title_label.pack(pady=(8, 5))
            self._widget_refs.add(title_label)
            
            # Value
            try:
                value_int = int(value) if value else 0
                value_text = f"{value_int} ürün"
            except (ValueError, TypeError):
                value_text = f"{value} ürün"
            
            value_label = tk.Label(inner_frame, text=value_text, font=('Segoe UI', 14, 'bold'), fg='white', bg=color)
            value_label.pack()
            self._widget_refs.add(value_label)
            
        except Exception as e:
            self.logger.error(f"Fallback profit card creation error: {e}")
    
    def _create_low_performance_section(self, parent):
        """Düşük performans bölümü"""
        try:
            low_perf_container = tk.Frame(parent, bg=self.colors['bg_secondary'])
            low_perf_container.pack(fill='x')
            self._widget_refs.add(low_perf_container)
            
            low_perf_frame = tk.Frame(low_perf_container, bg=self.colors['bg_secondary'], relief='flat')
            low_perf_frame.pack(fill='both', expand=True)
            self._widget_refs.add(low_perf_frame)
            
            # Header
            low_perf_header = tk.Frame(low_perf_frame, bg=self.colors['danger'], height=40)
            low_perf_header.pack(fill='x')
            low_perf_header.pack_propagate(False)
            self._widget_refs.add(low_perf_header)
            
            header_label = tk.Label(
                low_perf_header, text="⚠️ Dikkat Edilmesi Gereken Ürünler",
                font=('Segoe UI', 12, 'bold'), fg='white', bg=self.colors['danger']
            )
            header_label.pack(expand=True)
            self._widget_refs.add(header_label)
            
            # Düşük karlı ürünleri al
            try:
                if self.analiz:
                    low_profit_products = self.analiz.get_low_profit_products(10)
                else:
                    low_profit_products = self._get_fallback_low_profit_products()
                
                if DASHBOARD_COMPONENTS_AVAILABLE:
                    DashboardComponents.create_modern_product_list(
                        low_perf_frame, low_profit_products, 'Net Kar', self.colors['danger'], self.analiz
                    )
                else:
                    if not low_profit_products.empty:
                        self._create_simple_product_list(low_perf_frame, low_profit_products, 'Net Kar', 'Düşük Karlı Ürünler')
                    else:
                        self._create_no_data_label(low_perf_frame, "Düşük karlı ürün verisi bulunamadı")
                        
            except Exception as e:
                self.logger.warning(f"Low performance products error: {e}")
                self._create_no_data_label(low_perf_frame, "Düşük performans verileri yüklenemedi")
                
        except Exception as e:
            self.logger.error(f"Low performance section error: {e}")
    
    def _get_fallback_low_profit_products(self):
        """Fallback düşük karlı ürünler"""
        try:
            if self.df.empty or 'Net Kar' not in self.df.columns:
                return pd.DataFrame()
            
            df_copy = self.df.copy()
            df_copy['Net Kar'] = df_copy['Net Kar'].apply(SafeFallbacks.safe_numeric_conversion)
            return df_copy.nsmallest(10, 'Net Kar')
            
        except Exception as e:
            self.logger.error(f"Fallback low profit products error: {e}")
            return pd.DataFrame()
    
    def _create_distribution_tab(self):
        """Dağılım analizi sekmesi"""
        try:
            dist_frame = ttk.Frame(self.analysis_notebook)
            self.analysis_notebook.add(dist_frame, text="📊 Dağılım")
            self._widget_refs.add(dist_frame)
            
            main_container = tk.Frame(dist_frame, bg=self.colors['bg_secondary'])
            main_container.pack(fill='both', expand=True, padx=20, pady=20)
            self._widget_refs.add(main_container)
            
            # İstatistiksel özet
            self._create_statistical_summary(main_container)
            
        except Exception as e:
            self.logger.error(f"Distribution tab creation error: {e}")
    
    def _create_statistical_summary(self, parent):
        """İstatistiksel özet bölümü"""
        try:
            stats_container = tk.Frame(parent, bg=self.colors['bg_secondary'])
            stats_container.pack(fill='x')
            self._widget_refs.add(stats_container)
            
            stats_frame = tk.Frame(stats_container, bg=self.colors['bg_secondary'], relief='flat')
            stats_frame.pack(fill='both', expand=True)
            self._widget_refs.add(stats_frame)
            
            # Header
            stats_header = tk.Frame(stats_frame, bg=self.colors['primary'], height=40)
            stats_header.pack(fill='x')
            stats_header.pack_propagate(False)
            self._widget_refs.add(stats_header)
            
            header_label = tk.Label(
                stats_header, text="📈 İstatistiksel Özet",
                font=('Segoe UI', 12, 'bold'), fg='white', bg=self.colors['primary']
            )
            header_label.pack(expand=True)
            self._widget_refs.add(header_label)
            
            # İstatistik verilerini al
            try:
                if self.analiz:
                    stats = self.analiz.get_summary_stats()
                else:
                    stats = self._get_fallback_summary_stats()
                
                if stats:
                    self._create_stats_content(stats_frame, stats)
                else:
                    self._create_no_data_label(stats_frame, "İstatistik verisi bulunamadı")
                    
            except Exception as e:
                self.logger.warning(f"Summary stats error: {e}")
                self._create_no_data_label(stats_frame, "İstatistik verileri yüklenemedi")
                
        except Exception as e:
            self.logger.error(f"Statistical summary creation error: {e}")
    
    def _get_fallback_summary_stats(self):
        """Fallback özet istatistikler"""
        try:
            if self.df.empty:
                return {}
            
            stats = {}
            
            # Net Kar istatistikleri
            if 'Net Kar' in self.df.columns:
                try:
                    kar_series = self.df['Net Kar'].apply(SafeFallbacks.safe_numeric_conversion)
                    valid_kar = kar_series.dropna()
                    
                    if not valid_kar.empty:
                        stats.update({
                            'kar_toplam': float(valid_kar.sum()),
                            'kar_ortalama': float(valid_kar.mean()),
                            'kar_medyan': float(valid_kar.median()),
                            'kar_std': float(valid_kar.std()) if len(valid_kar) > 1 else 0.0,
                            'kar_min': float(valid_kar.min()),
                            'kar_max': float(valid_kar.max())
                        })
                except Exception as e:
                    self.logger.warning(f"Net Kar stats error: {e}")
            
            # Birim Kar istatistikleri
            if 'Birim Kar' in self.df.columns:
                try:
                    birim_kar_series = self.df['Birim Kar'].apply(SafeFallbacks.safe_numeric_conversion)
                    valid_birim_kar = birim_kar_series.dropna()
                    
                    if not valid_birim_kar.empty:
                        stats.update({
                            'birim_kar_ortalama': float(valid_birim_kar.mean()),
                            'birim_kar_medyan': float(valid_birim_kar.median())
                        })
                except Exception as e:
                    self.logger.warning(f"Birim Kar stats error: {e}")
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Fallback summary stats error: {e}")
            return {}
    
    def _create_stats_content(self, parent, stats):
        """İstatistik içeriği oluştur"""
        try:
            stats_content = tk.Frame(parent, bg=self.colors['bg_secondary'])
            stats_content.pack(fill='x', padx=20, pady=20)
            self._widget_refs.add(stats_content)
            
            row = 0
            col = 0
            
            for key, value in stats.items():
                if col >= 3:
                    col = 0
                    row += 1
                
                # Stat card container
                stat_container = tk.Frame(stats_content, bg=self.colors['bg_secondary'])
                stat_container.grid(row=row, column=col, padx=8, pady=8, sticky='ew')
                self._widget_refs.add(stat_container)
                
                # Stat card
                stat_card = tk.Frame(stat_container, bg=self.colors.get('input_bg', '#f8fafc'), relief='flat')
                stat_card.pack(fill='both', expand=True)
                self._widget_refs.add(stat_card)
                
                # İç padding
                stat_inner = tk.Frame(stat_card, bg=self.colors.get('input_bg', '#f8fafc'))
                stat_inner.pack(fill='both', expand=True, padx=20, pady=15)
                self._widget_refs.add(stat_inner)
                
                # Başlık
                title_text = str(key).replace('_', ' ').title()
                title_label = tk.Label(
                    stat_inner, text=title_text, font=('Segoe UI', 10, 'bold'),
                    fg=self.colors['text_secondary'], bg=self.colors.get('input_bg', '#f8fafc')
                )
                title_label.pack()
                self._widget_refs.add(title_label)
                
                # Değer
                try:
                    if isinstance(value, float):
                        if 'kar' in str(key).lower():
                            value_text = f"₺{value:,.2f}"
                        else:
                            value_text = f"{value:,.2f}"
                    else:
                        value_text = f"{value:,}"
                except (ValueError, TypeError):
                    value_text = str(value)
                
                value_label = tk.Label(
                    stat_inner, text=value_text, font=('Segoe UI', 14, 'bold'),
                    fg=self.colors['text_primary'], bg=self.colors.get('input_bg', '#f8fafc')
                )
                value_label.pack(pady=(5, 0))
                self._widget_refs.add(value_label)
                
                col += 1
            
            # Grid ağırlıkları
            for i in range(3):
                stats_content.grid_columnconfigure(i, weight=1)
                
        except Exception as e:
            self.logger.error(f"Stats content creation error: {e}")
    
    def _create_search_section(self):
        """Arama bölümü oluştur"""
        try:
            if not self._check_widget_exists(self.main_frame):
                raise WidgetError("Main frame not available for search section")
            
            self._create_section_title(
                self.main_frame, 
                "🔍 Gelişmiş Ürün Arama", 
                "Arama ve filtreleme araçları"
            )
            
            # Arama container
            search_container = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
            search_container.pack(fill='x', pady=(0, 40))
            self._widget_refs.add(search_container)
            
            # Arama frame
            search_frame = tk.Frame(search_container, bg=self.colors['bg_secondary'], relief='flat')
            search_frame.pack(fill='x')
            self._widget_refs.add(search_frame)
            
            # Arama header
            search_header = tk.Frame(search_frame, bg=self.colors['primary'], height=50)
            search_header.pack(fill='x')
            search_header.pack_propagate(False)
            self._widget_refs.add(search_header)
            
            header_label = tk.Label(
                search_header, text="Arama ve Filtreleme",
                font=('Segoe UI', 14, 'bold'), fg='white', bg=self.colors['primary']
            )
            header_label.pack(expand=True)
            self._widget_refs.add(header_label)
            
            # Arama kontrolleri
            self._create_search_controls(search_frame)
            
            # Sonuç alanı
            self.search_result_frame = tk.Frame(search_frame, bg=self.colors['bg_secondary'])
            self.search_result_frame.pack(fill='both', expand=True, padx=30, pady=(0, 30))
            self._widget_refs.add(self.search_result_frame)
            
            # Başlangıç mesajı
            self._show_initial_search_message()
            
        except Exception as e:
            self.logger.error(f"Search section creation error: {e}")
    
    def _create_search_controls(self, parent):
        """Arama kontrolleri oluştur"""
        try:
            controls_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
            controls_frame.pack(fill='x', padx=30, pady=25)
            self._widget_refs.add(controls_frame)
            
            # Arama kutusu satırı
            search_row = tk.Frame(controls_frame, bg=self.colors['bg_secondary'])
            search_row.pack(fill='x', pady=(0, 20))
            self._widget_refs.add(search_row)
            
            # Arama etiketi
            search_label = tk.Label(
                search_row, text="Ürün Adı:", font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text_primary'], bg=self.colors['bg_secondary']
            )
            search_label.pack(side='left')
            self._widget_refs.add(search_label)
            
            # Arama kutusu
            self.search_var = tk.StringVar()
            search_entry_frame = tk.Frame(search_row, bg=self.colors['bg_secondary'])
            search_entry_frame.pack(side='left', padx=(15, 20))
            self._widget_refs.add(search_entry_frame)
            
            search_entry = tk.Entry(
                search_entry_frame, textvariable=self.search_var, font=('Segoe UI', 11),
                bg=self.colors.get('input_bg', '#f8fafc'), fg=self.colors['text_primary'],
                relief='solid', bd=1, width=35, insertbackground=self.colors['primary']
            )
            search_entry.pack(pady=3)
            self._widget_refs.add(search_entry)
            
            # Buton grubu
            button_frame = tk.Frame(search_row, bg=self.colors['bg_secondary'])
            button_frame.pack(side='left')
            self._widget_refs.add(button_frame)
            
            # Arama butonu
            search_btn = self._create_search_button(button_frame, "🔍 Ara", self._search_product, self.colors['primary'])
            search_btn.pack(side='left', padx=(0, 10))
            
            # Temizle butonu
            clear_btn = self._create_search_button(button_frame, "🗑️ Temizle", self._clear_search, self.colors['text_secondary'])
            clear_btn.pack(side='left')
            
            # Enter tuşu ile arama
            search_entry.bind('<Return>', lambda e: self._search_product())
            
            # Hızlı filtreler
            self._create_quick_filters(controls_frame)
            
        except Exception as e:
            self.logger.error(f"Search controls creation error: {e}")
    
    def _create_search_button(self, parent, text, command, bg_color):
        """Arama butonu oluştur"""
        try:
            if UI_COMPONENTS_AVAILABLE:
                return UIComponents.create_modern_button(
                    parent, text=text, command=command, bg_color=bg_color,
                    hover_color=self._get_hover_color(bg_color), padx=25, pady=10
                )
            else:
                return self._create_fallback_button(parent, text, command, bg_color)
        except Exception as e:
            self.logger.warning(f"Search button creation error: {e}")
            return self._create_fallback_button(parent, text, command, bg_color)
    
    def _create_fallback_button(self, parent, text, command, bg_color):
        """Fallback buton"""
        try:
            button = tk.Button(
                parent, text=text, command=command, bg=bg_color, fg='white',
                font=('Segoe UI', 11, 'bold'), relief='flat', bd=0, cursor='hand2', padx=20, pady=8
            )
            self._widget_refs.add(button)
            return button
        except Exception as e:
            self.logger.error(f"Fallback button creation error: {e}")
            return None
    
    def _get_hover_color(self, color):
        """Hover rengi döndür"""
        hover_colors = {
            self.colors['text_secondary']: self.colors.get('text_light', '#4b5563'),
            self.colors['success']: self.colors.get('success_dark', '#059669'),
            self.colors['danger']: self.colors.get('danger_dark', '#dc2626'),
            self.colors['info']: self.colors.get('info_dark', '#0891b2'),
            self.colors['primary']: self.colors.get('primary_dark', '#2563eb')
        }
        return hover_colors.get(color, color)
    
    def _create_quick_filters(self, parent):
        """Hızlı filtreler oluştur"""
        try:
            filter_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
            filter_frame.pack(fill='x')
            self._widget_refs.add(filter_frame)
            
            filter_label = tk.Label(
                filter_frame, text="Hızlı Filtreler:", font=('Segoe UI', 12, 'bold'),
                fg=self.colors['text_primary'], bg=self.colors['bg_secondary']
            )
            filter_label.pack(anchor='w', pady=(0, 10))
            self._widget_refs.add(filter_label)
            
            # Filter buttons
            filter_buttons = tk.Frame(filter_frame, bg=self.colors['bg_secondary'])
            filter_buttons.pack(fill='x')
            self._widget_refs.add(filter_buttons)
            
            filters = [
                ("Tümü", "all", self.colors['text_secondary']),
                ("Karlı", "profitable", self.colors['success']),
                ("Zararlı", "loss", self.colors['danger']),
                ("Yüksek Satış", "high_sales", self.colors['info'])
            ]
            
            for text, filter_type, color in filters:
                btn = self._create_search_button(
                    filter_buttons, text=str(text),
                    command=lambda f=filter_type: self._apply_quick_filter(f),
                    bg_color=color
                )
                if btn:
                    btn.pack(side='left', padx=(0, 12))
                    
        except Exception as e:
            self.logger.error(f"Quick filters creation error: {e}")
    
    def _show_initial_search_message(self):
        """Başlangıç arama mesajı"""
        try:
            if DASHBOARD_COMPONENTS_AVAILABLE:
                DashboardComponents.show_initial_search_message(self.search_result_frame)
            else:
                self._create_fallback_search_message()
        except Exception as e:
            self.logger.warning(f"Initial search message error: {e}")
            self._create_fallback_search_message()
    
    def _create_fallback_search_message(self):
        """Fallback arama mesajı"""
        try:
            msg_container = tk.Frame(self.search_result_frame, bg=self.colors['bg_secondary'])
            msg_container.pack(fill='x', pady=20)
            self._widget_refs.add(msg_container)
            
            msg_frame = tk.Frame(msg_container, bg='#f0f9ff', relief='flat')
            msg_frame.pack(fill='x')
            self._widget_refs.add(msg_frame)
            
            msg_label = tk.Label(
                msg_frame,
                text="💡 Arama yapmak için yukarıdaki kutucuğa ürün adını yazın veya hızlı filtreleri kullanın",
                font=('Segoe UI', 12), fg=self.colors['info'], bg='#f0f9ff'
            )
            msg_label.pack(pady=20)
            self._widget_refs.add(msg_label)
            
        except Exception as e:
            self.logger.error(f"Fallback search message creation error: {e}")
    
    def _search_product(self):
        """Ürün arama işlemi"""
        try:
            search_term = self.search_var.get().strip() if hasattr(self, 'search_var') else ""
            
            # Eski sonuçları temizle
            self._clear_search_results()
            
            if not search_term:
                self._show_search_error("⚠️ Lütfen arama terimi girin")
                return
            
            # Arama yap
            try:
                if self.analiz:
                    results = self.analiz.search_product(search_term)
                else:
                    results = self._fallback_search(search_term)
                
                if results.empty:
                    self._show_search_error(f"❌ '{search_term}' için sonuç bulunamadı")
                    return
                
                # Sonuç başlığı
                self._show_search_results_header(search_term, len(results))
                
                # Sonuç tablosu
                self._display_search_results(results)
                
            except Exception as e:
                self.logger.error(f"Search execution error: {e}")
                self._show_search_error("❌ Arama işlemi sırasında hata oluştu")
                
        except Exception as e:
            self.logger.error(f"Search product error: {e}")
    
    def _fallback_search(self, search_term):
        """Fallback arama"""
        try:
            if self.df.empty:
                return pd.DataFrame()
            
            # Stok sütunu bul
            stok_col = None
            for col in self.df.columns:
                if 'stok' in col.lower() and 'ismi' in col.lower():
                    stok_col = col
                    break
            
            if not stok_col:
                return pd.DataFrame()
            
            # Arama yap
            mask = self.df[stok_col].astype(str).str.contains(search_term, case=False, na=False)
            return self.df[mask].copy()
            
        except Exception as e:
            self.logger.error(f"Fallback search error: {e}")
            return pd.DataFrame()
    
    def _clear_search_results(self):
        """Arama sonuçlarını temizle"""
        try:
            if hasattr(self, 'search_result_frame') and self._check_widget_exists(self.search_result_frame):
                for widget in self.search_result_frame.winfo_children():
                    try:
                        widget.destroy()
                    except tk.TclError:
                        pass
        except Exception as e:
            self.logger.error(f"Clear search results error: {e}")
    
    def _show_search_error(self, message):
        """Arama hatası göster"""
        try:
            error_container = tk.Frame(self.search_result_frame, bg=self.colors['bg_secondary'])
            error_container.pack(fill='x', pady=10)
            self._widget_refs.add(error_container)
            
            error_frame = tk.Frame(error_container, bg='#fef2f2', relief='flat')
            error_frame.pack(fill='x')
            self._widget_refs.add(error_frame)
            
            error_label = tk.Label(
                error_frame, text=message, font=('Segoe UI', 12),
                fg=self.colors['danger'], bg='#fef2f2'
            )
            error_label.pack(pady=15)
            self._widget_refs.add(error_label)
            
        except Exception as e:
            self.logger.error(f"Search error display error: {e}")
    
    def _show_search_results_header(self, search_term, result_count):
        """Arama sonuç başlığı"""
        try:
            result_header = tk.Frame(self.search_result_frame, bg=self.colors['bg_secondary'])
            result_header.pack(fill='x', pady=(0, 20))
            self._widget_refs.add(result_header)
            
            header_label = tk.Label(
                result_header,
                text=f"🎯 '{search_term}' için {result_count} sonuç bulundu:",
                font=('Segoe UI', 14, 'bold'), fg=self.colors['success'], bg=self.colors['bg_secondary']
            )
            header_label.pack(anchor='w')
            self._widget_refs.add(header_label)
            
        except Exception as e:
            self.logger.error(f"Search results header error: {e}")
    
    def _display_search_results(self, results):
        """Arama sonuçlarını göster"""
        try:
            if DASHBOARD_COMPONENTS_AVAILABLE:
                DashboardComponents.display_search_results(self.search_result_frame, results, self.analiz)
            else:
                self._create_fallback_results_table(results)
        except Exception as e:
            self.logger.warning(f"Display search results error: {e}")
            self._create_fallback_results_table(results)
    
    def _create_fallback_results_table(self, results):
        """Fallback sonuç tablosu"""
        try:
            # Basit tablo oluştur
            table_frame = tk.Frame(self.search_result_frame, bg='white', relief='solid', bd=1)
            table_frame.pack(fill='both', expand=True)
            self._widget_refs.add(table_frame)
            
            # İlk 10 sonuç göster
            limited_results = results.head(10)
            
            for i, (_, row) in enumerate(limited_results.iterrows()):
                try:
                    row_frame = tk.Frame(table_frame, bg='white' if i % 2 == 0 else '#f8f9fa')
                    row_frame.pack(fill='x', pady=1)
                    self._widget_refs.add(row_frame)
                    
                    # Ürün adı
                    stok_col = None
                    for col in results.columns:
                        if 'stok' in col.lower() and 'ismi' in col.lower():
                            stok_col = col
                            break
                    
                    if stok_col:
                        product_name = str(row[stok_col]) if pd.notna(row[stok_col]) else "Bilinmiyor"
                        if len(product_name) > 50:
                            product_name = product_name[:50] + "..."
                    else:
                        product_name = "Ürün Adı Bulunamadı"
                    
                    product_label = tk.Label(
                        row_frame, text=f"{i+1}. {product_name}",
                        font=('Segoe UI', 10), fg=self.colors['text_primary'],
                        bg=row_frame['bg'], anchor='w'
                    )
                    product_label.pack(side='left', padx=10, pady=5, fill='x', expand=True)
                    self._widget_refs.add(product_label)
                    
                    # Net Kar (varsa)
                    if 'Net Kar' in row.index:
                        try:
                            kar_value = SafeFallbacks.safe_numeric_conversion(row['Net Kar'])
                            kar_text = f"₺{kar_value:,.2f}"
                            kar_color = self.colors['success'] if kar_value >= 0 else self.colors['danger']
                        except:
                            kar_text = "N/A"
                            kar_color = self.colors['text_light']
                        
                        kar_label = tk.Label(
                            row_frame, text=kar_text, font=('Segoe UI', 10, 'bold'),
                            fg=kar_color, bg=row_frame['bg']
                        )
                        kar_label.pack(side='right', padx=10, pady=5)
                        self._widget_refs.add(kar_label)
                        
                except Exception as e:
                    self.logger.warning(f"Result row creation error: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Fallback results table error: {e}")
    
    def _apply_quick_filter(self, filter_type):
        """Hızlı filtre uygula"""
        try:
            self._clear_search_results()
            
            try:
                if filter_type == "all":
                    results = self.df.copy()
                elif filter_type == "profitable":
                    results = self._filter_profitable_products()
                elif filter_type == "loss":
                    results = self._filter_loss_products()
                elif filter_type == "high_sales":
                    results = self._filter_high_sales_products()
                else:
                    results = pd.DataFrame()
                
                if results.empty:
                    self._show_search_error("❌ Bu filtre için sonuç bulunamadı")
                    return
                
                # Sonuç başlığı
                filter_names = {
                    "all": "Tüm Ürünler",
                    "profitable": "Karlı Ürünler",
                    "loss": "Zararlı Ürünler", 
                    "high_sales": "Yükkes Satışlı Ürünler"
                }
                
                self._show_search_results_header(filter_names.get(filter_type, 'Filtre'), len(results))
                
                # Sonuç tablosu (İlk 50 sonuç)
                self._display_search_results(results.head(50))
                
            except Exception as e:
                self.logger.error(f"Filter execution error: {e}")
                self._show_search_error("❌ Filtreleme işlemi sırasında hata oluştu")
                
        except Exception as e:
            self.logger.error(f"Quick filter error: {e}")
    
    def _filter_profitable_products(self):
        """Karlı ürünleri filtrele"""
        try:
            if 'Net Kar' not in self.df.columns:
                return pd.DataFrame()
            
            df_copy = self.df.copy()
            df_copy['Net Kar'] = df_copy['Net Kar'].apply(SafeFallbacks.safe_numeric_conversion)
            return df_copy[df_copy['Net Kar'] > 0].copy()
            
        except Exception as e:
            self.logger.error(f"Profitable filter error: {e}")
            return pd.DataFrame()
    
    def _filter_loss_products(self):
        """Zararlı ürünleri filtrele"""
        try:
            if 'Net Kar' not in self.df.columns:
                return pd.DataFrame()
            
            df_copy = self.df.copy()
            df_copy['Net Kar'] = df_copy['Net Kar'].apply(SafeFallbacks.safe_numeric_conversion)
            return df_copy[df_copy['Net Kar'] < 0].copy()
            
        except Exception as e:
            self.logger.error(f"Loss filter error: {e}")
            return pd.DataFrame()
    
    def _filter_high_sales_products(self):
        """Yüksek satışlı ürünleri filtrele"""
        try:
            # Miktar sütunu bul
            miktar_col = None
            for col in self.df.columns:
                if 'miktar' in col.lower() or 'satis' in col.lower():
                    miktar_col = col
                    break
            
            if not miktar_col:
                return pd.DataFrame()
            
            df_copy = self.df.copy()
            df_copy[miktar_col] = df_copy[miktar_col].apply(SafeFallbacks.safe_numeric_conversion)
            threshold = df_copy[miktar_col].quantile(0.75)
            
            return df_copy[df_copy[miktar_col] >= threshold].copy()
            
        except Exception as e:
            self.logger.error(f"High sales filter error: {e}")
            return pd.DataFrame()
    
    def _clear_search(self):
        """Arama temizle"""
        try:
            if hasattr(self, 'search_var'):
                self.search_var.set("")
            
            self._clear_search_results()
            self._show_initial_search_message()
            
        except Exception as e:
            self.logger.error(f"Clear search error: {e}")
    
    def cleanup(self):
        """Comprehensive cleanup"""
        if self._cleanup_scheduled:
            return
        
        try:
            self._cleanup_scheduled = True
            self._is_destroyed = True
            
            self.logger.info("Starting AnalyzDashboard cleanup...")
            
            # Execute cleanup functions
            for cleanup_func in self._cleanup_functions:
                try:
                    cleanup_func()
                except Exception as e:
                    self.logger.debug(f"Cleanup function error: {e}")
            
            self._cleanup_functions.clear()
            
            # Clear widget references
            self._clear_all_widget_references()
            
            # Clear weak reference set
            self._widget_refs.clear()
            
            # Clear cache
            self._get_kpi_data.cache_clear()
            
            # Force garbage collection
            gc.collect()
            
            self.logger.info("AnalyzDashboard cleanup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
    
    def _clear_all_widget_references(self):
        """Tüm widget referanslarını temizle"""
        widget_attrs = [
            'main_container', 'dashboard_frame', 'canvas', 'scrollable_frame', 'scrollbar', 'main_frame',
            'analysis_notebook', 'search_result_frame', 'search_var'
        ]
        
        for attr in widget_attrs:
            try:
                setattr(self, attr, None)
            except Exception:
                pass
    
    def __del__(self):
        """Destructor with safety"""
        try:
            if not self._is_destroyed and not self._cleanup_scheduled:
                self.cleanup()
        except Exception:
            pass