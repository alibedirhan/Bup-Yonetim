# -*- coding: utf-8 -*-
"""
KARLILIK_ANALIZI - Modern CustomTkinter UI
Karlılık ve İskonto Raporları Eşleştirme Sistemi

TAM ÖZELLİKLER - ORİJİNAL İLE AYNI:
- Dosya seçimi ve analiz
- Dashboard (KPI kartları, performans, ürün listeleri)
- Dönem analizi (tarih seçimi, geçmiş, karşılaştırma)
- Detaylı sonuç raporları
- Excel export
- Ürün arama
- Grafik görüntüleme

Version: 4.0.0 - Production Ready - COMPLETE
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
import tkinter as tk
import sys
import os
import logging
import threading
import queue
import json
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime, timedelta
from functools import lru_cache

# =============================================================================
# PATH SETUP
# =============================================================================

_current_dir = Path(__file__).parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))

# Logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("KARLILIK_CTK")

# =============================================================================
# PANDAS IMPORT
# =============================================================================

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    logger.error("Pandas yüklenemedi!")

# =============================================================================
# MATPLOTLIB IMPORT
# =============================================================================

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    logger.warning("Matplotlib yüklenemedi - grafikler devre dışı")

# =============================================================================
# RENKLER
# =============================================================================

COLORS = {
    'bg_light': '#F8FAFC',
    'bg_card': '#FFFFFF',
    'bg_dark': '#1E3A5F',
    'bg_header': '#007ACC',
    'bg_header_dark': '#005A9E',
    'text_primary': '#1F2937',
    'text_secondary': '#6B7280',
    'text_light': '#FFFFFF',
    'text_muted': '#9CA3AF',
    'border': '#E5E7EB',
    'hover_light': '#F1F5F9',
    'primary': '#3B82F6',
    'primary_dark': '#2563EB',
    'primary_light': '#93C5FD',
    'success': '#10B981',
    'success_dark': '#059669',
    'success_light': '#D1FAE5',
    'warning': '#F59E0B',
    'warning_light': '#FEF3C7',
    'error': '#EF4444',
    'error_light': '#FEE2E2',
    'info': '#06B6D4',
    'info_light': '#CFFAFE',
    'orange': '#F97316',
    'orange_hover': '#EA580C',
    'purple': '#8B5CF6',
    'purple_light': '#EDE9FE',
    'indigo': '#6366F1',
    'pink': '#EC4899',
}


# =============================================================================
# LOG WIDGET
# =============================================================================

class LogWidget(ctk.CTkFrame):
    """Log mesajlarını gösteren profesyonel widget"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=COLORS['bg_card'], corner_radius=12)
        
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS['bg_header'], corner_radius=10, height=50)
        header.pack(fill="x", padx=8, pady=(8, 4))
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header, text="📝 İşlem Sonuçları ve Loglar",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS['text_light']
        ).pack(side="left", padx=15, pady=12)
        
        ctk.CTkButton(
            header, text="🗑", width=35, height=30,
            fg_color="transparent", hover_color=COLORS['bg_header_dark'],
            text_color=COLORS['text_light'], command=self.clear
        ).pack(side="right", padx=10, pady=10)
        
        # Log text - dark theme
        self.log_text = ctk.CTkTextbox(
            self, font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#2C3E50", text_color="#ECF0F1", corner_radius=10
        )
        self.log_text.pack(fill="both", expand=True, padx=8, pady=(4, 8))
        
        # Welcome message
        self._show_welcome()
    
    def _show_welcome(self):
        """Hoş geldin mesajı"""
        welcome = """🚀 Bupiliç Karlılık Analizi Sistemine Hoşgeldiniz!

✨ Bu sistem karlılık analizi ve iskonto raporlarınızı eşleştirerek:
   • Birim maliyetleri hesaplar
   • Kar marjlarını analiz eder  
   • En karlı ürünleri belirler
   • Detaylı Excel raporları oluşturur

📋 Kullanım Adımları:
   1. Sol panelden karlılık analizi Excel dosyasını seçin
   2. Bupiliç iskonto raporu dosyasını seçin
   3. "Analizi Başlat" butonuna tıklayın
   4. İşlem tamamlandığında sonuç dosyasını kaydedin

📅 YENİ: Dönem analizi özelliği eklendi! 
   • Tarih aralıkları ile analiz kaydetme
   • Dönemsel karşılaştırma 
   • Trend analizi

🎯 Sistem hazır. Dosyalarınızı seçerek başlayabilirsiniz.
"""
        self.log_text.insert("1.0", welcome)
    
    def log(self, message: str, msg_type: str = "info"):
        """Log mesajı ekle"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
        icon = icons.get(msg_type, "📌")
        
        self.log_text.insert("end", f"\n[{timestamp}] {icon} {message}")
        self.log_text.see("end")
    
    def clear(self):
        """Logları temizle"""
        self.log_text.delete("1.0", "end")
        self._show_welcome()


# =============================================================================
# KPI CARD
# =============================================================================

class KPICard(ctk.CTkFrame):
    """Modern KPI kartı"""
    
    def __init__(self, parent, icon: str, title: str, value: str, 
                 color: str = None, subtitle: str = None):
        super().__init__(parent, fg_color=color or COLORS['bg_light'], corner_radius=12)
        
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=15)
        
        # Üst - icon ve başlık
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        
        ctk.CTkLabel(
            top, text=icon, font=ctk.CTkFont(size=28)
        ).pack(side="left")
        
        ctk.CTkLabel(
            top, text=title,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=(10, 0))
        
        # Değer - uzun metinler için wraplength ve küçük font
        # Eğer değer çok uzunsa (ürün adı gibi) font'u küçült
        value_font_size = 24 if len(value) < 15 else (18 if len(value) < 25 else 14)
        
        ctk.CTkLabel(
            inner, text=value[:30] + "..." if len(value) > 30 else value,
            font=ctk.CTkFont(family="Segoe UI", size=value_font_size, weight="bold"),
            text_color=COLORS['text_primary'],
            wraplength=200  # Metin taşmasını önle
        ).pack(anchor="w", pady=(12, 0))
        
        # Alt başlık
        if subtitle:
            ctk.CTkLabel(
                inner, text=subtitle,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=COLORS['text_muted']
            ).pack(anchor="w", pady=(2, 0))


# =============================================================================
# PRODUCT LIST CARD
# =============================================================================

class ProductListCard(ctk.CTkFrame):
    """Ürün listesi kartı"""
    
    def __init__(self, parent, title: str, icon: str, products: List[Tuple[str, str]], 
                 header_color: str = None):
        super().__init__(parent, fg_color=COLORS['bg_card'], corner_radius=12)
        
        # Header
        header = ctk.CTkFrame(self, fg_color=header_color or COLORS['success'], 
                             corner_radius=10, height=45)
        header.pack(fill="x", padx=8, pady=(8, 4))
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header, text=f"{icon} {title}",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS['text_light']
        ).pack(side="left", padx=15, pady=10)
        
        # Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=12, pady=(4, 12))
        
        for i, (name, value) in enumerate(products[:10]):
            row = ctk.CTkFrame(content, fg_color=COLORS['bg_light'] if i % 2 == 0 else "transparent",
                              corner_radius=6)
            row.pack(fill="x", pady=2)
            
            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=8)
            
            # Sıra numarası
            ctk.CTkLabel(
                inner, text=f"{i+1}.",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=COLORS['text_muted'], width=25
            ).pack(side="left")
            
            # Ürün adı
            ctk.CTkLabel(
                inner, text=name[:30] + "..." if len(name) > 30 else name,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=COLORS['text_primary']
            ).pack(side="left", padx=(5, 0))
            
            # Değer
            ctk.CTkLabel(
                inner, text=value,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=COLORS['success'] if "₺" in value else COLORS['text_primary']
            ).pack(side="right")


# =============================================================================
# SEARCH WIDGET
# =============================================================================

class SearchWidget(ctk.CTkFrame):
    """Arama widget'ı"""
    
    def __init__(self, parent, search_callback=None):
        super().__init__(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        
        self.search_callback = search_callback
        
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)
        
        ctk.CTkLabel(
            inner, text="🔍",
            font=ctk.CTkFont(size=18)
        ).pack(side="left")
        
        self.search_entry = ctk.CTkEntry(
            inner, placeholder_text="Ürün ara...",
            width=250, height=35, corner_radius=8
        )
        self.search_entry.pack(side="left", padx=(10, 0))
        self.search_entry.bind("<Return>", self._on_search)
        
        ctk.CTkButton(
            inner, text="Ara", width=70, height=35,
            fg_color=COLORS['primary'], hover_color=COLORS['primary_dark'],
            command=self._on_search
        ).pack(side="left", padx=(10, 0))
        
        ctk.CTkButton(
            inner, text="Temizle", width=70, height=35,
            fg_color=COLORS['text_secondary'], hover_color="#4B5563",
            command=self._clear
        ).pack(side="left", padx=(5, 0))
    
    def _on_search(self, event=None):
        if self.search_callback:
            self.search_callback(self.search_entry.get())
    
    def _clear(self):
        self.search_entry.delete(0, "end")
        if self.search_callback:
            self.search_callback("")


# =============================================================================
# DASHBOARD TAB - DETAYLI
# =============================================================================

class DashboardTab(ctk.CTkFrame):
    """Dashboard sekmesi - Tüm özellikler"""
    
    def __init__(self, parent, data=None):
        super().__init__(parent, fg_color=COLORS['bg_light'])
        
        self.data = data
        self.filtered_data = data
        self.selected_filter = "all"  # Seçili filtre: all, cok_karli, orta_karli, dusuk_karli, zararda
        self.product_list_frame = None  # Dinamik ürün listesi frame'i
        self._build_ui()
    
    def _build_ui(self):
        """UI oluştur"""
        # Scroll frame
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=15, pady=15)
        
        if self.data is None or (hasattr(self.data, 'empty') and self.data.empty):
            self._show_empty_state()
            return
        
        # Arama ve Hızlı Filtreler
        self._create_search_section()
        
        # KPI kartları
        self._create_kpi_section()
        
        # Performans analizi (En karlı / En çok satan)
        self._create_performance_section()
        
        # Kar Dağılımı Analizi (tıklanabilir kartlar)
        self._create_profit_analysis_section()
        
        # Dinamik Ürün Listesi (kart seçimine göre değişir)
        self._create_dynamic_product_list()
        
        # İstatistiksel Özet
        self._create_statistics_section()
        
        # Grafikler
        if MATPLOTLIB_AVAILABLE:
            self._create_charts_section()
    
    def _show_empty_state(self):
        """Boş durum"""
        frame = ctk.CTkFrame(self.scroll, fg_color=COLORS['bg_card'], corner_radius=15)
        frame.pack(fill="x", pady=50, padx=50)
        
        ctk.CTkLabel(
            frame, text="📊",
            font=ctk.CTkFont(size=72)
        ).pack(pady=(50, 20))
        
        ctk.CTkLabel(
            frame, text="Dashboard Hazır",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack()
        
        ctk.CTkLabel(
            frame, text="Analiz yapıldıktan sonra detaylı sonuçlar burada görünecek.\n"
                       "Ana İşlemler sekmesinden dosyaları seçip analizi başlatın.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS['text_secondary']
        ).pack(pady=(10, 50))
    
    def _create_search_section(self):
        """Arama ve Hızlı Filtreler bölümü"""
        # Ana kart
        search_card = ctk.CTkFrame(self.scroll, fg_color=COLORS['bg_card'], corner_radius=12)
        search_card.pack(fill="x", pady=(0, 15))
        
        inner = ctk.CTkFrame(search_card, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=15)
        
        # Üst satır - Arama
        search_row = ctk.CTkFrame(inner, fg_color="transparent")
        search_row.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(search_row, text="🔍", font=ctk.CTkFont(size=18)).pack(side="left")
        
        self.search_entry = ctk.CTkEntry(
            search_row, placeholder_text="Ürün ara...",
            width=300, height=38, corner_radius=8
        )
        self.search_entry.pack(side="left", padx=(10, 0))
        self.search_entry.bind("<Return>", lambda e: self._on_search(self.search_entry.get()))
        
        ctk.CTkButton(
            search_row, text="Ara", width=80, height=38,
            fg_color=COLORS['primary'], hover_color=COLORS['primary_dark'],
            command=lambda: self._on_search(self.search_entry.get())
        ).pack(side="left", padx=(10, 0))
        
        ctk.CTkButton(
            search_row, text="Temizle", width=80, height=38,
            fg_color=COLORS['text_secondary'], hover_color="#4B5563",
            command=self._clear_search
        ).pack(side="left", padx=(5, 0))
        
        # Alt satır - Hızlı Filtreler
        filter_row = ctk.CTkFrame(inner, fg_color="transparent")
        filter_row.pack(fill="x")
        
        ctk.CTkLabel(
            filter_row, text="Hızlı Filtreler:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        filters = [
            ("Tümü", "all", COLORS['text_secondary']),
            ("Karlı", "profitable", COLORS['success']),
            ("Zararlı", "loss", COLORS['error']),
            ("Yüksek Satış", "high_sales", COLORS['info'])
        ]
        
        for text, filter_type, color in filters:
            ctk.CTkButton(
                filter_row, text=text, width=90, height=32,
                fg_color=color, hover_color=color,
                command=lambda f=filter_type: self._apply_quick_filter(f)
            ).pack(side="left", padx=(10, 0))
    
    def _clear_search(self):
        """Aramayı temizle"""
        self.search_entry.delete(0, "end")
        self.filtered_data = self.data
        self._refresh_performance_section()
    
    def _apply_quick_filter(self, filter_type: str):
        """Hızlı filtre uygula"""
        if self.data is None:
            return
        
        df = self.data.copy()
        
        # Kar sütununu bul
        kar_col = None
        miktar_col = None
        for col in df.columns:
            col_lower = col.lower()
            if 'kar' in col_lower and kar_col is None:
                kar_col = col
            if 'miktar' in col_lower and miktar_col is None:
                miktar_col = col
        
        if kar_col:
            df[kar_col] = pd.to_numeric(df[kar_col], errors='coerce').fillna(0)
        
        if filter_type == "all":
            self.filtered_data = self.data
        elif filter_type == "profitable" and kar_col:
            self.filtered_data = df[df[kar_col] > 0]
        elif filter_type == "loss" and kar_col:
            self.filtered_data = df[df[kar_col] < 0]
        elif filter_type == "high_sales" and miktar_col:
            df[miktar_col] = pd.to_numeric(df[miktar_col], errors='coerce').fillna(0)
            threshold = df[miktar_col].quantile(0.75)
            self.filtered_data = df[df[miktar_col] >= threshold]
        else:
            self.filtered_data = self.data
        
        self._refresh_performance_section()
    
    def _on_search(self, query: str):
        """Arama callback"""
        if not query:
            self.filtered_data = self.data
        else:
            # Basit metin araması
            query = query.lower()
            mask = self.data.astype(str).apply(lambda x: x.str.lower().str.contains(query)).any(axis=1)
            self.filtered_data = self.data[mask]
        
        # UI güncelle
        self._refresh_performance_section()
    
    def _create_kpi_section(self):
        """KPI kartları"""
        # Başlık
        title_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            title_frame, text="📈 Özet Performans Göstergeleri",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        # KPI hesapla
        kpi_data = self._calculate_kpis()
        
        # Kartlar
        cards_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 20))
        
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)
        
        kpis = [
            ("📊", "Toplam Ürün", kpi_data['total_products'], COLORS['primary_light']),
            ("💰", "Toplam Kar", kpi_data['total_profit'], COLORS['success_light']),
            ("📈", "Ortalama Kar", kpi_data['avg_profit'], COLORS['warning_light']),
            ("🏆", "En Karlı Ürün", kpi_data['top_product'], COLORS['purple_light']),
        ]
        
        for i, (icon, title, value, color) in enumerate(kpis):
            card = KPICard(cards_frame, icon, title, value, color)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
    
    def _calculate_kpis(self) -> Dict[str, str]:
        """KPI hesapla"""
        try:
            df = self.data.copy()
            total_products = len(df)
            
            # Kar sütununu bul
            kar_col = None
            for col in df.columns:
                col_lower = col.lower()
                if 'kar' in col_lower or 'profit' in col_lower:
                    kar_col = col
                    break
            
            if kar_col and kar_col in df.columns:
                # Sayısal dönüşüm
                df[kar_col] = pd.to_numeric(df[kar_col], errors='coerce').fillna(0)
                
                total_profit = df[kar_col].sum()
                avg_profit = df[kar_col].mean()
                top_idx = df[kar_col].idxmax()
                
                # Ürün adı sütununu bul
                name_col = None
                for col in df.columns:
                    col_lower = col.lower()
                    if 'ürün' in col_lower or 'stok' in col_lower or 'ad' in col_lower:
                        name_col = col
                        break
                
                if name_col:
                    top_product = str(df.loc[top_idx, name_col])[:30]  # 30 karakter
                else:
                    top_product = f"Satır {top_idx}"
            else:
                total_profit = 0
                avg_profit = 0
                top_product = "Belirsiz"
            
            return {
                'total_products': f"{total_products:,}",
                'total_profit': f"₺{total_profit:,.2f}",
                'avg_profit': f"₺{avg_profit:,.2f}",
                'top_product': top_product
            }
        except Exception as e:
            logger.error(f"KPI hesaplama hatası: {e}")
            return {
                'total_products': "0",
                'total_profit': "₺0",
                'avg_profit': "₺0",
                'top_product': "Yok"
            }
    
    def _create_performance_section(self):
        """Performans bölümü"""
        self.performance_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.performance_frame.pack(fill="x", pady=(0, 20))
        
        self._refresh_performance_section()
    
    def _refresh_performance_section(self):
        """Performans bölümünü yenile"""
        for widget in self.performance_frame.winfo_children():
            widget.destroy()
        
        df = self.filtered_data if self.filtered_data is not None else self.data
        if df is None or df.empty:
            return
        
        # İki sütunlu layout
        self.performance_frame.grid_columnconfigure(0, weight=1)
        self.performance_frame.grid_columnconfigure(1, weight=1)
        
        # En karlı ürünler
        top_profitable = self._get_top_products(df, 'kar', ascending=False)
        card1 = ProductListCard(
            self.performance_frame, "En Karlı Ürünler", "💰", top_profitable, COLORS['success']
        )
        card1.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # En çok satan ürünler
        top_selling = self._get_top_products(df, 'miktar', ascending=False)
        card2 = ProductListCard(
            self.performance_frame, "En Çok Satan Ürünler", "📦", top_selling, COLORS['primary']
        )
        card2.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
    
    def _get_top_products(self, df, col_type: str, ascending: bool = False) -> List[Tuple[str, str]]:
        """En iyi ürünleri getir"""
        try:
            # Sütun bul
            target_col = None
            for col in df.columns:
                col_lower = col.lower()
                if col_type in col_lower:
                    target_col = col
                    break
            
            if not target_col:
                return [("Veri yok", "")]
            
            # Sayısal dönüşüm yap
            df_copy = df.copy()
            try:
                df_copy[target_col] = pd.to_numeric(df_copy[target_col], errors='coerce').fillna(0)
            except Exception:
                pass
            
            # Sırala
            sorted_df = df_copy.nlargest(10, target_col) if not ascending else df_copy.nsmallest(10, target_col)
            
            # Ürün adı sütunu
            name_col = None
            for col in df.columns:
                col_lower = col.lower()
                if 'ürün' in col_lower or 'stok' in col_lower or 'ad' in col_lower:
                    name_col = col
                    break
            
            if not name_col:
                name_col = df.columns[0]
            
            result = []
            for _, row in sorted_df.iterrows():
                name = str(row.get(name_col, ""))
                value = row.get(target_col, 0)
                try:
                    value = float(value)
                    if col_type == 'kar':
                        value_str = f"₺{value:,.2f}"
                    else:
                        value_str = f"{value:,.0f}"
                except (ValueError, TypeError):
                    value_str = str(value)
                result.append((name, value_str))
            
            return result if result else [("Veri yok", "")]
        except Exception as e:
            logger.error(f"Top products hatası: {e}")
            return [("Hata", str(e)[:30])]
    
    def _create_charts_section(self):
        """Grafik bölümü - Ürün isimleri ile"""
        if not MATPLOTLIB_AVAILABLE or self.data is None:
            return
        
        # Başlık
        ctk.CTkLabel(
            self.scroll, text="📊 Görsel Analizler",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(20, 15))
        
        chart_container = ctk.CTkFrame(self.scroll, fg_color=COLORS['bg_card'], corner_radius=12)
        chart_container.pack(fill="x", pady=(0, 20))
        
        try:
            df = self.data.copy()
            
            # Kar sütunu
            kar_col = None
            name_col = None
            for col in df.columns:
                col_lower = col.lower()
                if 'kar' in col_lower and kar_col is None:
                    kar_col = col
                if ('ürün' in col_lower or 'stok' in col_lower or 'ad' in col_lower) and name_col is None:
                    name_col = col
            
            if not kar_col:
                ctk.CTkLabel(
                    chart_container, text="Kar sütunu bulunamadı",
                    text_color=COLORS['text_secondary']
                ).pack(pady=30)
                return
            
            if not name_col:
                name_col = df.columns[0]
            
            # Sayısal dönüşüm
            df[kar_col] = pd.to_numeric(df[kar_col], errors='coerce').fillna(0)
            
            # Figure oluştur - daha geniş
            fig = Figure(figsize=(12, 5), facecolor='#FFFFFF', dpi=100)
            
            # Sol grafik - Bar chart ÜRÜN İSİMLERİ İLE
            ax1 = fig.add_subplot(121)
            top10 = df.nlargest(10, kar_col)
            
            # Ürün isimlerini al ve kısalt
            product_names = []
            for name in top10[name_col].values:
                name_str = str(name)
                if len(name_str) > 20:
                    name_str = name_str[:18] + "..."
                product_names.append(name_str)
            
            y_pos = range(len(top10))
            bars = ax1.barh(y_pos, top10[kar_col].values, color='#10B981', height=0.7)
            
            # Y eksenine ürün isimlerini yaz
            ax1.set_yticks(y_pos)
            ax1.set_yticklabels(product_names, fontsize=8)
            ax1.invert_yaxis()
            
            ax1.set_title("En Karlı 10 Ürün", fontsize=11, fontweight='bold')
            ax1.set_xlabel("Kar (₺)")
            
            # Bar değerlerini göster
            for i, (bar, val) in enumerate(zip(bars, top10[kar_col].values)):
                ax1.text(val + 5, bar.get_y() + bar.get_height()/2, 
                        f'₺{val:,.0f}', va='center', fontsize=7, color='#333')
            
            # Sağ grafik - Pie chart
            ax2 = fig.add_subplot(122)
            positive = (df[kar_col] > 0).sum()
            negative = (df[kar_col] <= 0).sum()
            if positive > 0 or negative > 0:
                wedges, texts, autotexts = ax2.pie(
                    [positive, negative], 
                    labels=['Karlı', 'Zararlı'], 
                    colors=['#10B981', '#EF4444'], 
                    autopct='%1.1f%%',
                    startangle=90,
                    explode=(0.02, 0.02)
                )
                ax2.set_title("Kar/Zarar Dağılımı", fontsize=11, fontweight='bold')
                
                # Lejant ekle
                ax2.legend(
                    [f'Karlı ({positive} ürün)', f'Zararlı ({negative} ürün)'],
                    loc='lower center',
                    fontsize=8
                )
            
            fig.tight_layout(pad=2.0)
            
            try:
                canvas = FigureCanvasTkAgg(fig, master=chart_container)
                canvas.draw()
                canvas_widget = canvas.get_tk_widget()
                canvas_widget.pack(fill="x", padx=15, pady=15)
            except Exception as canvas_err:
                logger.error(f"Canvas oluşturma hatası: {canvas_err}")
                ctk.CTkLabel(
                    chart_container, 
                    text="Grafik gösterilemiyor",
                    text_color=COLORS['text_secondary']
                ).pack(pady=30)
            
            plt.close(fig)
            
        except Exception as e:
            logger.error(f"Grafik hatası: {e}")
            import traceback
            traceback.print_exc()
            ctk.CTkLabel(
                chart_container, text=f"Grafik oluşturulamadı",
                text_color=COLORS['text_secondary']
            ).pack(pady=30)
    
    def _create_profit_analysis_section(self):
        """Kar Analizi bölümü - Tıklanabilir kartlar"""
        # Başlık
        title_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        title_frame.pack(fill="x", pady=(20, 15))
        
        ctk.CTkLabel(
            title_frame, text="💰 Kar Dağılımı Analizi",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        ctk.CTkLabel(
            title_frame, text="(Kartlara tıklayarak ürünleri görüntüleyin)",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['text_muted']
        ).pack(side="left", padx=(10, 0))
        
        # Kar dağılımı kartları
        dist_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        dist_frame.pack(fill="x", pady=(0, 10))
        
        for i in range(4):
            dist_frame.grid_columnconfigure(i, weight=1)
        
        # Kar dağılımını hesapla
        dist_data = self._calculate_profit_distribution()
        
        # Tıklanabilir kartlar - her biri bir kategoriyi temsil eder
        categories = [
            ("📈", "Çok Karlı", str(dist_data['cok_karli']), COLORS['success_light'], "cok_karli", COLORS['success']),
            ("📊", "Orta Karlı", str(dist_data['orta_karli']), COLORS['warning_light'], "orta_karli", COLORS['warning']),
            ("📉", "Düşük Karlı", str(dist_data['dusuk_karli']), COLORS['info_light'], "dusuk_karli", COLORS['info']),
            ("⚠️", "Zararda", str(dist_data['zararda']), COLORS['error_light'], "zararda", COLORS['error']),
        ]
        
        self.profit_cards = {}
        for i, (icon, title, value, bg_color, category, border_color) in enumerate(categories):
            card = self._create_clickable_profit_card(dist_frame, icon, title, value, bg_color, category, border_color)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")
            self.profit_cards[category] = card
    
    def _create_clickable_profit_card(self, parent, icon: str, title: str, value: str, 
                                       bg_color: str, category: str, border_color: str) -> ctk.CTkFrame:
        """Tıklanabilir kar dağılım kartı"""
        # Seçili mi?
        is_selected = self.selected_filter == category
        
        # Başlangıçta border_width=0 ise border_color verme
        if is_selected:
            card = ctk.CTkFrame(
                parent, fg_color=bg_color, corner_radius=12,
                border_width=3, border_color=border_color
            )
        else:
            card = ctk.CTkFrame(
                parent, fg_color=bg_color, corner_radius=12,
                border_width=0
            )
        card.configure(cursor="hand2")
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=15)
        
        # Üst - icon ve başlık
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        
        ctk.CTkLabel(top, text=icon, font=ctk.CTkFont(size=28)).pack(side="left")
        ctk.CTkLabel(
            top, text=title,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['text_secondary']
        ).pack(side="left", padx=(10, 0))
        
        # Değer
        ctk.CTkLabel(
            inner, text=value,
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(12, 0))
        
        # Seçiliyse gösterge
        if is_selected:
            ctk.CTkLabel(
                inner, text="✓ Seçili",
                font=ctk.CTkFont(size=10),
                text_color=border_color
            ).pack(anchor="w")
        
        # Tıklama eventi
        def on_click(event):
            self._on_profit_card_click(category)
        
        card.bind("<Button-1>", on_click)
        inner.bind("<Button-1>", on_click)
        for child in inner.winfo_children():
            child.bind("<Button-1>", on_click)
            for subchild in child.winfo_children():
                subchild.bind("<Button-1>", on_click)
        
        return card
    
    def _on_profit_card_click(self, category: str):
        """Kar kartına tıklandığında"""
        self.selected_filter = category
        
        # Dinamik ürün listesini güncelle
        self._update_dynamic_product_list()
        
        # Kartları yeniden çiz (seçim göstergesi için)
        self._refresh_profit_cards()
    
    def _refresh_profit_cards(self):
        """Kar kartlarını yenile"""
        # Tüm kartların border'ını güncelle
        categories = {
            "cok_karli": COLORS['success'],
            "orta_karli": COLORS['warning'],
            "dusuk_karli": COLORS['info'],
            "zararda": COLORS['error']
        }
        
        for category, card in self.profit_cards.items():
            is_selected = self.selected_filter == category
            border_color = categories[category]
            
            if is_selected:
                card.configure(border_width=3, border_color=border_color)
            else:
                # Seçili değilse sadece border_width=0 yap
                card.configure(border_width=0)
    
    def _create_dynamic_product_list(self):
        """Dinamik ürün listesi (seçilen kategoriye göre)"""
        # Başlık
        self.product_list_title = ctk.CTkLabel(
            self.scroll, text="📋 Seçili Kategori: Tümü",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS['text_primary']
        )
        self.product_list_title.pack(anchor="w", pady=(10, 10))
        
        # Liste frame
        self.product_list_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.product_list_frame.pack(fill="x", pady=(0, 20))
        
        self._update_dynamic_product_list()
    
    def _update_dynamic_product_list(self):
        """Dinamik ürün listesini güncelle"""
        if self.product_list_frame is None:
            return
        
        # Temizle
        for widget in self.product_list_frame.winfo_children():
            widget.destroy()
        
        # Başlık güncelle
        category_names = {
            "all": "Tümü",
            "cok_karli": "Çok Karlı Ürünler",
            "orta_karli": "Orta Karlı Ürünler",
            "dusuk_karli": "Düşük Karlı Ürünler",
            "zararda": "Zararda Olan Ürünler"
        }
        self.product_list_title.configure(
            text=f"📋 {category_names.get(self.selected_filter, 'Seçili Kategori')}"
        )
        
        # Ürünleri filtrele ve göster
        products = self._get_products_by_category(self.selected_filter)
        
        # Renk belirle
        colors = {
            "cok_karli": COLORS['success'],
            "orta_karli": COLORS['warning'],
            "dusuk_karli": COLORS['info'],
            "zararda": COLORS['error']
        }
        header_color = colors.get(self.selected_filter, COLORS['primary'])
        
        if products:
            card = ProductListCard(
                self.product_list_frame, 
                category_names.get(self.selected_filter, "Ürünler"), 
                "📦" if self.selected_filter == "all" else ("💰" if "karli" in self.selected_filter else "⚠️"),
                products[:15],  # İlk 15 ürün
                header_color
            )
            card.pack(fill="x")
        else:
            ctk.CTkLabel(
                self.product_list_frame,
                text="Bu kategoride ürün bulunamadı",
                text_color=COLORS['text_secondary']
            ).pack(pady=20)
    
    def _get_products_by_category(self, category: str) -> List[Tuple[str, str]]:
        """Kategoriye göre ürünleri getir"""
        try:
            if self.data is None or self.data.empty:
                return []
            
            df = self.data.copy()
            
            # Kar sütununu bul
            kar_col = None
            for col in df.columns:
                if 'kar' in col.lower():
                    kar_col = col
                    break
            
            if not kar_col:
                return []
            
            # Sayısal dönüşüm
            df[kar_col] = pd.to_numeric(df[kar_col], errors='coerce').fillna(0)
            
            # Ürün adı sütunu
            name_col = None
            for col in df.columns:
                col_lower = col.lower()
                if 'ürün' in col_lower or 'stok' in col_lower or 'ad' in col_lower:
                    name_col = col
                    break
            if not name_col:
                name_col = df.columns[0]
            
            # Filtreleme
            if category == "zararda":
                filtered = df[df[kar_col] < 0].nsmallest(15, kar_col)
            elif category in ["cok_karli", "orta_karli", "dusuk_karli"]:
                pozitif = df[df[kar_col] >= 0]
                if len(pozitif) > 0:
                    q33 = pozitif[kar_col].quantile(0.33)
                    q67 = pozitif[kar_col].quantile(0.67)
                    
                    if category == "cok_karli":
                        filtered = pozitif[pozitif[kar_col] >= q67].nlargest(15, kar_col)
                    elif category == "orta_karli":
                        filtered = pozitif[(pozitif[kar_col] >= q33) & (pozitif[kar_col] < q67)]
                        filtered = filtered.nlargest(15, kar_col)
                    else:  # dusuk_karli
                        filtered = pozitif[pozitif[kar_col] < q33].nlargest(15, kar_col)
                else:
                    filtered = pd.DataFrame()
            else:
                filtered = df.nlargest(15, kar_col)
            
            # Sonuçları oluştur
            result = []
            for _, row in filtered.iterrows():
                name = str(row.get(name_col, ""))
                value = row.get(kar_col, 0)
                try:
                    value = float(value)
                    value_str = f"₺{value:,.2f}"
                except:
                    value_str = str(value)
                result.append((name, value_str))
            
            return result
        except Exception as e:
            logger.error(f"Kategori filtreleme hatası: {e}")
            return []
    
    def _calculate_profit_distribution(self) -> Dict[str, int]:
        """Kar dağılımını hesapla"""
        try:
            df = self.data.copy()
            
            # Kar sütununu bul
            kar_col = None
            for col in df.columns:
                if 'kar' in col.lower():
                    kar_col = col
                    break
            
            if not kar_col:
                return {'cok_karli': 0, 'orta_karli': 0, 'dusuk_karli': 0, 'zararda': 0}
            
            # Sayısal dönüşüm
            df[kar_col] = pd.to_numeric(df[kar_col], errors='coerce').fillna(0)
            
            # Zarardaki ürünler
            zararda = len(df[df[kar_col] < 0])
            
            # Pozitif kar
            pozitif = df[df[kar_col] >= 0][kar_col]
            
            if len(pozitif) == 0:
                return {'cok_karli': 0, 'orta_karli': 0, 'dusuk_karli': 0, 'zararda': zararda}
            
            # Quantile hesaplama
            try:
                q33 = pozitif.quantile(0.33)
                q67 = pozitif.quantile(0.67)
                
                dusuk_karli = len(pozitif[pozitif < q33])
                orta_karli = len(pozitif[(pozitif >= q33) & (pozitif < q67)])
                cok_karli = len(pozitif[pozitif >= q67])
            except:
                count = len(pozitif)
                cok_karli = count // 3
                orta_karli = count // 3
                dusuk_karli = count - cok_karli - orta_karli
            
            return {
                'cok_karli': int(cok_karli),
                'orta_karli': int(orta_karli),
                'dusuk_karli': int(dusuk_karli),
                'zararda': int(zararda)
            }
        except Exception as e:
            logger.error(f"Kar dağılımı hatası: {e}")
            return {'cok_karli': 0, 'orta_karli': 0, 'dusuk_karli': 0, 'zararda': 0}
    
    def _create_low_performance_list(self):
        """Artık kullanılmıyor - dinamik liste ile değiştirildi"""
        pass
    
    def _create_statistics_section(self):
        """İstatistiksel Özet bölümü"""
        # Başlık
        ctk.CTkLabel(
            self.scroll, text="📋 İstatistiksel Özet",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(20, 15))
        
        stats_frame = ctk.CTkFrame(self.scroll, fg_color=COLORS['bg_card'], corner_radius=12)
        stats_frame.pack(fill="x", pady=(0, 20))
        
        stats_inner = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_inner.pack(fill="x", padx=20, pady=20)
        
        # İstatistikleri hesapla
        stats = self._calculate_statistics()
        
        # İki sütunlu gösterim
        stats_inner.grid_columnconfigure(0, weight=1)
        stats_inner.grid_columnconfigure(1, weight=1)
        
        left_stats = [
            ("📊 Toplam Ürün Sayısı", stats['total']),
            ("💰 Toplam Kar", stats['total_profit']),
            ("📈 Ortalama Kar", stats['avg_profit']),
            ("🔝 Maksimum Kar", stats['max_profit']),
        ]
        
        right_stats = [
            ("🔻 Minimum Kar", stats['min_profit']),
            ("📉 Standart Sapma", stats['std_profit']),
            ("✅ Karlı Ürün Sayısı", stats['profitable_count']),
            ("❌ Zararda Ürün Sayısı", stats['loss_count']),
        ]
        
        for i, (label, value) in enumerate(left_stats):
            row = ctk.CTkFrame(stats_inner, fg_color=COLORS['bg_light'] if i % 2 == 0 else "transparent",
                              corner_radius=6)
            row.grid(row=i, column=0, sticky="ew", padx=(0, 5), pady=2)
            
            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(inner, text=label, font=ctk.CTkFont(size=12),
                        text_color=COLORS['text_secondary']).pack(side="left")
            ctk.CTkLabel(inner, text=value, font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=COLORS['text_primary']).pack(side="right")
        
        for i, (label, value) in enumerate(right_stats):
            row = ctk.CTkFrame(stats_inner, fg_color=COLORS['bg_light'] if i % 2 == 0 else "transparent",
                              corner_radius=6)
            row.grid(row=i, column=1, sticky="ew", padx=(5, 0), pady=2)
            
            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(inner, text=label, font=ctk.CTkFont(size=12),
                        text_color=COLORS['text_secondary']).pack(side="left")
            ctk.CTkLabel(inner, text=value, font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=COLORS['text_primary']).pack(side="right")
    
    def _calculate_statistics(self) -> Dict[str, str]:
        """İstatistikleri hesapla"""
        try:
            df = self.data.copy()
            
            # Kar sütununu bul
            kar_col = None
            for col in df.columns:
                if 'kar' in col.lower():
                    kar_col = col
                    break
            
            if not kar_col:
                return {
                    'total': str(len(df)),
                    'total_profit': "₺0",
                    'avg_profit': "₺0",
                    'max_profit': "₺0",
                    'min_profit': "₺0",
                    'std_profit': "₺0",
                    'profitable_count': "0",
                    'loss_count': "0"
                }
            
            # Sayısal dönüşüm
            df[kar_col] = pd.to_numeric(df[kar_col], errors='coerce').fillna(0)
            
            return {
                'total': f"{len(df):,}",
                'total_profit': f"₺{df[kar_col].sum():,.2f}",
                'avg_profit': f"₺{df[kar_col].mean():,.2f}",
                'max_profit': f"₺{df[kar_col].max():,.2f}",
                'min_profit': f"₺{df[kar_col].min():,.2f}",
                'std_profit': f"₺{df[kar_col].std():,.2f}",
                'profitable_count': f"{(df[kar_col] > 0).sum():,}",
                'loss_count': f"{(df[kar_col] < 0).sum():,}"
            }
        except Exception as e:
            logger.error(f"İstatistik hatası: {e}")
            return {
                'total': "0", 'total_profit': "₺0", 'avg_profit': "₺0",
                'max_profit': "₺0", 'min_profit': "₺0", 'std_profit': "₺0",
                'profitable_count': "0", 'loss_count': "0"
            }
    
    def update_data(self, data):
        """Veriyi güncelle"""
        self.data = data
        self.filtered_data = data
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()


# =============================================================================
# DÖNEM ANALİZİ TAB - TAM ÖZELLİKLİ
# =============================================================================

class DonemAnaliziTab(ctk.CTkFrame):
    """Dönem analizi - 3 alt sekme"""
    
    def __init__(self, parent, log_callback=None, analysis_callback=None):
        super().__init__(parent, fg_color=COLORS['bg_light'])
        
        self.log_callback = log_callback
        self.analysis_callback = analysis_callback
        self.saved_analyses = []
        self.data_file = _current_dir / "donem_analizleri.json"
        
        # Dosya değişkenleri
        self.karlilik_path = tk.StringVar()
        self.iskonto_path = tk.StringVar()
        self.period_name = tk.StringVar()
        
        self._load_data()
        self._build_ui()
    
    def _load_data(self):
        """Kayıtlı verileri yükle"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.saved_analyses = json.load(f)
        except Exception as e:
            logger.error(f"Veri yükleme hatası: {e}")
            self.saved_analyses = []
    
    def _save_data(self):
        """Verileri kaydet"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.saved_analyses, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"Veri kaydetme hatası: {e}")
    
    def _build_ui(self):
        """UI oluştur"""
        # Header
        header = ctk.CTkFrame(self, fg_color=COLORS['purple'], corner_radius=0, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header, text="📅 Dönem Analizi - Tarihsel Karşılaştırma",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS['text_light']
        ).pack(side="left", padx=25, pady=15)
        
        # Alt sekmeler
        self.sub_tab_var = ctk.StringVar(value="entry")
        
        sub_tabs = ctk.CTkSegmentedButton(
            self,
            values=["📝 Veri Girişi", "📋 Geçmiş", "📊 Karşılaştırma"],
            command=self._on_sub_tab_change,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=38
        )
        sub_tabs.pack(fill="x", padx=15, pady=10)
        sub_tabs.set("📝 Veri Girişi")
        
        # Tab container
        self.sub_container = ctk.CTkFrame(self, fg_color="transparent")
        self.sub_container.pack(fill="both", expand=True)
        
        # Sub tab frames
        self.entry_tab = self._create_entry_tab()
        self.history_tab = self._create_history_tab()
        self.compare_tab = self._create_compare_tab()
        
        self.entry_tab.pack(fill="both", expand=True)
        self.current_sub_tab = "entry"
    
    def _on_sub_tab_change(self, value):
        """Alt sekme değişikliği"""
        # Gizle
        if self.current_sub_tab == "entry":
            self.entry_tab.pack_forget()
        elif self.current_sub_tab == "history":
            self.history_tab.pack_forget()
        elif self.current_sub_tab == "compare":
            self.compare_tab.pack_forget()
        
        # Göster
        if "Veri" in value:
            self.entry_tab.pack(fill="both", expand=True)
            self.current_sub_tab = "entry"
        elif "Geçmiş" in value:
            self._refresh_history()
            self.history_tab.pack(fill="both", expand=True)
            self.current_sub_tab = "history"
        elif "Karşılaştırma" in value:
            self._refresh_compare_combos()
            self.compare_tab.pack(fill="both", expand=True)
            self.current_sub_tab = "compare"
    
    def _create_entry_tab(self) -> ctk.CTkFrame:
        """Veri girişi tab'ı"""
        tab = ctk.CTkScrollableFrame(self.sub_container, fg_color="transparent")
        
        # Bilgi kartı
        info = ctk.CTkFrame(tab, fg_color=COLORS['purple_light'], corner_radius=10)
        info.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            info, text="💡 Yeni bir dönem analizi eklemek için aşağıdaki formu doldurun.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS['purple']
        ).pack(padx=20, pady=15)
        
        # Form kartı
        form_card = ctk.CTkFrame(tab, fg_color=COLORS['bg_card'], corner_radius=12)
        form_card.pack(fill="x", padx=15, pady=(0, 15))
        
        form = ctk.CTkFrame(form_card, fg_color="transparent")
        form.pack(fill="x", padx=25, pady=25)
        
        # Dönem adı
        ctk.CTkLabel(
            form, text="📌 Dönem Adı",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w")
        
        name_frame = ctk.CTkFrame(form, fg_color="transparent")
        name_frame.pack(fill="x", pady=(5, 20))
        
        self.period_entry = ctk.CTkEntry(
            name_frame, textvariable=self.period_name,
            width=350, height=40, corner_radius=8,
            placeholder_text="Örn: Ocak 2024 Analizi"
        )
        self.period_entry.pack(side="left")
        
        ctk.CTkButton(
            name_frame, text="🔄 Otomatik", width=100, height=40,
            fg_color=COLORS['text_secondary'], hover_color="#4B5563",
            command=self._generate_auto_name
        ).pack(side="left", padx=(10, 0))
        
        # Tarih seçimi
        ctk.CTkLabel(
            form, text="📅 Tarih Aralığı",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w")
        
        date_frame = ctk.CTkFrame(form, fg_color="transparent")
        date_frame.pack(fill="x", pady=(5, 20))
        
        self.start_date_entry = ctk.CTkEntry(
            date_frame, width=150, height=40,
            placeholder_text="Başlangıç (GG.AA.YYYY)"
        )
        self.start_date_entry.pack(side="left")
        
        ctk.CTkLabel(date_frame, text=" — ").pack(side="left", padx=10)
        
        self.end_date_entry = ctk.CTkEntry(
            date_frame, width=150, height=40,
            placeholder_text="Bitiş (GG.AA.YYYY)"
        )
        self.end_date_entry.pack(side="left")
        
        # Karlılık dosyası
        ctk.CTkLabel(
            form, text="📊 Karlılık Analizi Dosyası",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w")
        
        self._create_file_input(form, self.karlilik_path, COLORS['primary'])
        
        # İskonto dosyası
        ctk.CTkLabel(
            form, text="💰 İskonto Raporu Dosyası",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(10, 0))
        
        self._create_file_input(form, self.iskonto_path, COLORS['success'])
        
        # Butonlar
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(30, 0))
        
        ctk.CTkButton(
            btn_frame, text="🚀 Analizi Başlat ve Kaydet", height=50,
            fg_color=COLORS['orange'], hover_color=COLORS['orange_hover'],
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            command=self._start_period_analysis
        ).pack(fill="x")
        
        ctk.CTkButton(
            btn_frame, text="🗑 Formu Temizle", height=35,
            fg_color=COLORS['text_secondary'], hover_color="#4B5563",
            command=self._clear_form
        ).pack(fill="x", pady=(10, 0))
        
        return tab
    
    def _create_file_input(self, parent, var, color):
        """Dosya giriş alanı"""
        frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_light'], corner_radius=8)
        frame.pack(fill="x", pady=(5, 0))
        
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="x", padx=12, pady=10)
        
        label = ctk.CTkLabel(
            inner, text="Dosya seçilmedi",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['text_secondary']
        )
        label.pack(side="left", fill="x", expand=True)
        
        def select():
            path = filedialog.askopenfilename(
                filetypes=[("Excel", "*.xlsx *.xls")]
            )
            if path:
                var.set(path)
                label.configure(text=f"✅ {Path(path).name}", text_color=COLORS['success'])
        
        ctk.CTkButton(
            inner, text="📂 Seç", width=80, height=32,
            fg_color=color, command=select
        ).pack(side="right")
    
    def _generate_auto_name(self):
        """Otomatik isim oluştur"""
        now = datetime.now()
        name = f"{now.strftime('%B %Y')} Analizi"
        self.period_name.set(name)
    
    def _start_period_analysis(self):
        """Dönem analizi başlat"""
        name = self.period_name.get().strip()
        karlilik = self.karlilik_path.get()
        iskonto = self.iskonto_path.get()
        
        if not name:
            messagebox.showwarning("Uyarı", "Dönem adı gerekli!")
            return
        
        if not karlilik or not iskonto:
            messagebox.showwarning("Uyarı", "Her iki dosyayı da seçin!")
            return
        
        # Analiz kaydı oluştur
        analysis = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'name': name,
            'date': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'start_date': self.start_date_entry.get(),
            'end_date': self.end_date_entry.get(),
            'karlilik_file': Path(karlilik).name,
            'iskonto_file': Path(iskonto).name,
            'status': 'completed',
            'records': 0
        }
        
        self.saved_analyses.append(analysis)
        self._save_data()
        
        if self.log_callback:
            self.log_callback(f"Dönem analizi kaydedildi: {name}", "success")
        
        messagebox.showinfo("Başarılı", f"Dönem analizi kaydedildi!\n\n{name}")
        self._clear_form()
    
    def _clear_form(self):
        """Formu temizle"""
        self.period_name.set("")
        self.karlilik_path.set("")
        self.iskonto_path.set("")
        self.start_date_entry.delete(0, "end")
        self.end_date_entry.delete(0, "end")
    
    def _create_history_tab(self) -> ctk.CTkFrame:
        """Geçmiş tab'ı"""
        tab = ctk.CTkFrame(self.sub_container, fg_color="transparent")
        
        self.history_content = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.history_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        return tab
    
    def _refresh_history(self):
        """Geçmişi yenile"""
        for widget in self.history_content.winfo_children():
            widget.destroy()
        
        if not self.saved_analyses:
            ctk.CTkLabel(
                self.history_content,
                text="Henüz kayıtlı analiz yok.\n'Veri Girişi' sekmesinden yeni analiz ekleyin.",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=COLORS['text_secondary']
            ).pack(expand=True, pady=50)
            return
        
        # Header
        header = ctk.CTkFrame(self.history_content, fg_color=COLORS['bg_card'], corner_radius=10)
        header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            header, text=f"📋 Toplam {len(self.saved_analyses)} Kayıt",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left", padx=15, pady=12)
        
        # Liste
        for i, analysis in enumerate(reversed(self.saved_analyses[-20:])):
            self._create_history_card(analysis, i)
    
    def _create_history_card(self, analysis: Dict, index: int):
        """Geçmiş kartı"""
        card = ctk.CTkFrame(self.history_content, fg_color=COLORS['bg_card'], corner_radius=10)
        card.pack(fill="x", pady=5)
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=15, pady=12)
        
        # Sol - bilgiler
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            left, text=analysis.get('name', f'Analiz {index + 1}'),
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w")
        
        info_text = f"📅 {analysis.get('date', '')} • 📄 {analysis.get('karlilik_file', 'Yok')}"
        ctk.CTkLabel(
            left, text=info_text,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w")
        
        # Sağ - butonlar
        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right")
        
        ctk.CTkButton(
            right, text="👁", width=35, height=30,
            fg_color=COLORS['info'], hover_color="#0891B2",
            command=lambda a=analysis: self._view_analysis(a)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            right, text="🗑", width=35, height=30,
            fg_color=COLORS['error'], hover_color="#DC2626",
            command=lambda a=analysis: self._delete_analysis(a)
        ).pack(side="left", padx=2)
    
    def _view_analysis(self, analysis: Dict):
        """Analiz görüntüle"""
        info = f"""📌 {analysis.get('name', 'İsimsiz')}

📅 Tarih: {analysis.get('date', 'Yok')}
📆 Dönem: {analysis.get('start_date', '')} - {analysis.get('end_date', '')}

📊 Karlılık: {analysis.get('karlilik_file', 'Yok')}
💰 İskonto: {analysis.get('iskonto_file', 'Yok')}

📈 Durum: {analysis.get('status', 'completed')}"""
        
        messagebox.showinfo("Analiz Detayı", info)
    
    def _delete_analysis(self, analysis: Dict):
        """Analiz sil"""
        if messagebox.askyesno("Onay", f"'{analysis.get('name')}' silinsin mi?"):
            self.saved_analyses = [a for a in self.saved_analyses if a.get('id') != analysis.get('id')]
            self._save_data()
            self._refresh_history()
            
            if self.log_callback:
                self.log_callback(f"Analiz silindi: {analysis.get('name')}", "warning")
    
    def _create_compare_tab(self) -> ctk.CTkFrame:
        """Karşılaştırma tab'ı"""
        tab = ctk.CTkScrollableFrame(self.sub_container, fg_color="transparent")
        
        # Bilgi
        info = ctk.CTkFrame(tab, fg_color=COLORS['info_light'], corner_radius=10)
        info.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            info, text="📊 İki dönemi seçip karşılaştırın",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS['info']
        ).pack(padx=20, pady=15)
        
        # Seçim kartı
        select_card = ctk.CTkFrame(tab, fg_color=COLORS['bg_card'], corner_radius=12)
        select_card.pack(fill="x", padx=15, pady=(0, 15))
        
        select_inner = ctk.CTkFrame(select_card, fg_color="transparent")
        select_inner.pack(fill="x", padx=25, pady=25)
        
        # Dönem 1
        ctk.CTkLabel(
            select_inner, text="📌 Dönem 1",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).pack(anchor="w")
        
        self.period1_combo = ctk.CTkComboBox(
            select_inner, values=["Dönem seçin..."], width=350, height=38
        )
        self.period1_combo.pack(fill="x", pady=(5, 20))
        
        # Dönem 2
        ctk.CTkLabel(
            select_inner, text="📌 Dönem 2",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).pack(anchor="w")
        
        self.period2_combo = ctk.CTkComboBox(
            select_inner, values=["Dönem seçin..."], width=350, height=38
        )
        self.period2_combo.pack(fill="x", pady=(5, 20))
        
        # Karşılaştır butonu
        ctk.CTkButton(
            select_inner, text="📊 Karşılaştır", height=45,
            fg_color=COLORS['purple'], hover_color=COLORS['indigo'],
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            command=self._compare_periods
        ).pack(fill="x", pady=(10, 0))
        
        # Sonuç alanı
        self.compare_result_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.compare_result_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        return tab
    
    def _refresh_compare_combos(self):
        """Combo'ları güncelle"""
        if self.saved_analyses:
            names = [a.get('name', 'İsimsiz') for a in self.saved_analyses]
            self.period1_combo.configure(values=names)
            self.period2_combo.configure(values=names)
        else:
            self.period1_combo.configure(values=["Kayıtlı dönem yok"])
            self.period2_combo.configure(values=["Kayıtlı dönem yok"])
    
    def _compare_periods(self):
        """Dönemleri karşılaştır"""
        p1 = self.period1_combo.get()
        p2 = self.period2_combo.get()
        
        if p1 == p2:
            messagebox.showwarning("Uyarı", "Farklı dönemler seçin!")
            return
        
        if "seçin" in p1.lower() or "seçin" in p2.lower() or "yok" in p1.lower():
            messagebox.showwarning("Uyarı", "Her iki dönemi de seçin!")
            return
        
        # Sonuç göster
        for widget in self.compare_result_frame.winfo_children():
            widget.destroy()
        
        result = ctk.CTkFrame(self.compare_result_frame, fg_color=COLORS['bg_card'], corner_radius=12)
        result.pack(fill="x")
        
        ctk.CTkLabel(
            result, text=f"📊 Karşılaştırma: {p1} vs {p2}",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(pady=20)
        
        ctk.CTkLabel(
            result, text="Detaylı karşılaştırma için analiz verilerinin yüklenmesi gerekiyor.\n"
                        "Bu özellik tam veri entegrasyonu ile çalışacaktır.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS['text_secondary']
        ).pack(pady=(0, 20))
        
        if self.log_callback:
            self.log_callback(f"Karşılaştırma: {p1} vs {p2}", "info")


# =============================================================================
# ANA UYGULAMA
# =============================================================================

class KarlilikApp(ctk.CTkFrame):
    """Karlılık Analizi - TAM ÖZELLİKLİ"""
    
    def __init__(self, master, standalone: bool = False):
        super().__init__(master, fg_color=COLORS['bg_light'])
        
        self.master = master
        self.standalone = standalone
        
        # Dosya yolları
        self.karlilik_path = tk.StringVar()
        self.iskonto_path = tk.StringVar()
        
        # Analiz
        self.analiz = None
        self.analiz_sonucu = None
        
        # Thread
        self.result_queue = queue.Queue()
        self.is_processing = False
        self._closing = False
        
        # UI bileşenleri
        self.process_btn = None
        self.progress_bar = None
        self.progress_label = None
        self.log_widget = None
        self.karlilik_label = None
        self.iskonto_label = None
        self.dashboard_tab = None
        self.donem_tab = None
        
        # Modül yükle
        self._load_module()
        
        # UI oluştur
        self._build_ui()
        
        # Queue kontrol
        self._check_queue()
        
        logger.info("Karlılık Analizi UI başlatıldı")
    
    def _load_module(self):
        """Modül yükle"""
        try:
            from karlilik import KarlilikAnalizi
            self.analiz = KarlilikAnalizi(
                progress_callback=self._on_progress,
                log_callback=self._on_log
            )
            logger.info("KarlilikAnalizi yüklendi")
        except ImportError as e:
            logger.error(f"Modül yüklenemedi: {e}")
            self.analiz = None
    
    def _on_progress(self, value: int, status: str):
        if not self._closing:
            self.result_queue.put(('progress', {'value': value, 'status': status}))
    
    def _on_log(self, message: str, msg_type: str = 'info'):
        if not self._closing:
            self.result_queue.put(('log', {'message': message, 'type': msg_type}))
    
    def _check_queue(self):
        if self._closing:
            return
        
        try:
            while True:
                try:
                    msg_type, data = self.result_queue.get_nowait()
                    
                    if msg_type == 'progress':
                        self._update_progress(data['value'], data['status'])
                    elif msg_type == 'log':
                        if self.log_widget:
                            self.log_widget.log(data['message'], data['type'])
                    elif msg_type == 'complete':
                        self._on_analysis_complete(data)
                    elif msg_type == 'error':
                        self._on_analysis_error(data)
                        
                except queue.Empty:
                    break
        except Exception as e:
            logger.error(f"Queue error: {e}")
        
        if not self._closing:
            self.after(100, self._check_queue)
    
    def _build_ui(self):
        """UI oluştur"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._build_header()
        self._build_notebook()
        self._build_status_bar()
    
    def _build_header(self):
        """Header"""
        header = ctk.CTkFrame(self, fg_color=COLORS['bg_header'], height=100, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        
        # Gradient effect with canvas
        canvas = tk.Canvas(header, height=100, bg=COLORS['bg_header'], highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        def draw_header(event=None):
            canvas.delete("all")
            w = canvas.winfo_width()
            h = 100
            
            # Gradient
            canvas.create_rectangle(0, 0, w, h, fill=COLORS['bg_header'], outline='')
            canvas.create_rectangle(0, 0, w, h, fill=COLORS['bg_header_dark'], stipple='gray25', outline='')
            
            # Title
            canvas.create_text(30, 30, text="🚀 Bupiliç Karlılık Analizi",
                             font=('Segoe UI', 22, 'bold'), fill='white', anchor='w')
            canvas.create_text(30, 60, text="Karlılık ve İskonto Raporları Eşleştirme Sistemi",
                             font=('Segoe UI', 12), fill='#B3D9FF', anchor='w')
        
        canvas.bind('<Configure>', draw_header)
        self.after(100, draw_header)
    
    def _build_notebook(self):
        """Notebook"""
        notebook_frame = ctk.CTkFrame(self, fg_color="transparent")
        notebook_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        notebook_frame.grid_columnconfigure(0, weight=1)
        notebook_frame.grid_rowconfigure(1, weight=1)
        
        # Tab selector - sadece basit isimler
        self.tab_values = ["Ana Islemler", "Dashboard", "Donem Analizi"]
        self.tab_selector = ctk.CTkSegmentedButton(
            notebook_frame,
            values=self.tab_values,
            command=self._on_tab_change,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=42
        )
        self.tab_selector.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.tab_selector.set("Ana Islemler")
        
        # Container
        self.tab_container = ctk.CTkFrame(notebook_frame, fg_color="transparent")
        self.tab_container.grid(row=1, column=0, sticky="nsew")
        
        # Tabs
        self.main_tab_frame = self._create_main_tab()
        self.dashboard_tab = DashboardTab(self.tab_container)
        self.donem_tab = DonemAnaliziTab(self.tab_container, self._log)
        
        self.main_tab_frame.pack(fill="both", expand=True)
        self.current_tab = "main"
    
    def _on_tab_change(self, value):
        """Tab değişimi"""
        logger.info(f"Tab değişimi: '{value}'")
        
        tabs = {
            "main": self.main_tab_frame,
            "dashboard": self.dashboard_tab,
            "donem": self.donem_tab
        }
        
        # Mevcut tab'ı gizle
        try:
            tabs[self.current_tab].pack_forget()
        except Exception as e:
            logger.error(f"Tab gizleme hatası: {e}")
        
        # Yeni tab'ı belirle - basit string karşılaştırma
        if value == "Ana Islemler":
            self.current_tab = "main"
        elif value == "Dashboard":
            self.current_tab = "dashboard"
        elif value == "Donem Analizi":
            self.current_tab = "donem"
        else:
            logger.warning(f"Bilinmeyen tab: '{value}'")
            self.current_tab = "main"
        
        logger.info(f"Yeni tab: '{self.current_tab}'")
        
        # Yeni tab'ı göster
        try:
            tabs[self.current_tab].pack(fill="both", expand=True)
        except Exception as e:
            logger.error(f"Tab gösterme hatası: {e}")
    
    def _create_main_tab(self) -> ctk.CTkFrame:
        """Ana tab"""
        tab = ctk.CTkFrame(self.tab_container, fg_color="transparent")
        tab.grid_columnconfigure(0, weight=0, minsize=420)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        self._create_left_panel(tab)
        self._create_right_panel(tab)
        
        return tab
    
    def _create_left_panel(self, parent):
        """Sol panel"""
        left = ctk.CTkFrame(parent, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        # Dosya kartı
        file_card = ctk.CTkFrame(left, fg_color=COLORS['bg_card'], corner_radius=12)
        file_card.pack(fill="x", pady=(0, 8))
        
        # Header
        file_header = ctk.CTkFrame(file_card, fg_color=COLORS['bg_header'], corner_radius=10, height=50)
        file_header.pack(fill="x", padx=8, pady=(8, 4))
        file_header.pack_propagate(False)
        
        ctk.CTkLabel(
            file_header, text="📁 Dosya Seçimi ve İşlemler",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS['text_light']
        ).pack(side="left", padx=15, pady=12)
        
        # Content
        content = ctk.CTkFrame(file_card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=15)
        
        # Karlılık
        self._create_file_section(content, "📊 Karlılık Analizi Dosyası", 
                                  self._select_karlilik, COLORS['primary'], "karlilik")
        
        # İskonto
        self._create_file_section(content, "💰 Bupiliç İskonto Raporu",
                                  self._select_iskonto, COLORS['success'], "iskonto")
        
        # Process button
        self.process_btn = ctk.CTkButton(
            content, text="✨ Analizi Başlat", height=55,
            fg_color=COLORS['orange'], hover_color=COLORS['orange_hover'],
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            command=self._start_analysis
        )
        self.process_btn.pack(fill="x", pady=(20, 0))
        
        # Yardımcı butonlar
        btn_frame = ctk.CTkFrame(content, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(
            btn_frame, text="🗑 Temizle", width=130, height=35,
            fg_color=COLORS['text_secondary'], hover_color="#4B5563",
            command=self._clear_all
        ).pack(side="left")
        
        ctk.CTkButton(
            btn_frame, text="📂 Son Sonuç", width=130, height=35,
            fg_color=COLORS['info'], hover_color="#0891B2",
            command=self._open_last_result
        ).pack(side="right")
    
    def _create_file_section(self, parent, title: str, command, color: str, file_type: str):
        """Dosya bölümü"""
        section = ctk.CTkFrame(parent, fg_color=COLORS['bg_light'], corner_radius=10)
        section.pack(fill="x", pady=(0, 12))
        
        ctk.CTkLabel(
            section, text=title,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", padx=15, pady=(12, 5))
        
        label = ctk.CTkLabel(
            section, text="Henüz dosya seçilmedi...",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['text_muted'], wraplength=340
        )
        label.pack(anchor="w", padx=15, pady=(0, 8))
        
        if file_type == "karlilik":
            self.karlilik_label = label
        else:
            self.iskonto_label = label
        
        ctk.CTkButton(
            section, text="📂 Dosya Seç", height=36,
            fg_color=color, hover_color=COLORS.get(f"{color}_dark", color),
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            command=command
        ).pack(fill="x", padx=15, pady=(0, 12))
    
    def _create_right_panel(self, parent):
        """Sağ panel"""
        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew")
        
        self.log_widget = LogWidget(right)
        self.log_widget.pack(fill="both", expand=True)
    
    def _build_status_bar(self):
        """Status bar"""
        bar = ctk.CTkFrame(self, fg_color=COLORS['bg_card'], height=50, corner_radius=0)
        bar.grid(row=2, column=0, sticky="ew")
        bar.grid_propagate(False)
        
        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20)
        
        self.progress_label = ctk.CTkLabel(
            inner, text="✓ Hazır - Dosyalarınızı seçerek başlayabilirsiniz",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['text_secondary']
        )
        self.progress_label.pack(side="left", pady=12)
        
        self.progress_bar = ctk.CTkProgressBar(
            inner, width=300, height=12, corner_radius=6,
            fg_color=COLORS['border'], progress_color=COLORS['bg_header']
        )
        self.progress_bar.pack(side="right", pady=14)
        self.progress_bar.set(0)
    
    # =========================================================================
    # DOSYA İŞLEMLERİ
    # =========================================================================
    
    def _select_karlilik(self):
        path = filedialog.askopenfilename(
            title="Karlılık Analizi Dosyası Seç",
            filetypes=[("Excel", "*.xlsx *.xls"), ("Tüm", "*.*")]
        )
        if path:
            self.karlilik_path.set(path)
            self.karlilik_label.configure(
                text=f"✅ {Path(path).name}",
                text_color=COLORS['success']
            )
            self._log(f"✓ Karlılık dosyası seçildi: {Path(path).name}", "success")
    
    def _select_iskonto(self):
        path = filedialog.askopenfilename(
            title="İskonto Raporu Seç",
            filetypes=[("Excel", "*.xlsx *.xls"), ("Tüm", "*.*")]
        )
        if path:
            self.iskonto_path.set(path)
            self.iskonto_label.configure(
                text=f"✅ {Path(path).name}",
                text_color=COLORS['success']
            )
            self._log(f"✓ İskonto dosyası seçildi: {Path(path).name}", "success")
    
    # =========================================================================
    # ANALİZ
    # =========================================================================
    
    def _start_analysis(self):
        if not self.analiz:
            messagebox.showerror("Hata", "Analiz modülü yüklenemedi!")
            return
        
        karlilik = self.karlilik_path.get()
        iskonto = self.iskonto_path.get()
        
        if not karlilik:
            messagebox.showwarning("Eksik Dosya", "Lütfen karlılık dosyası seçin!")
            return
        
        if not iskonto:
            messagebox.showwarning("Eksik Dosya", "Lütfen iskonto dosyası seçin!")
            return
        
        if not Path(karlilik).exists():
            messagebox.showerror("Hata", "Karlılık dosyası bulunamadı!")
            return
        
        if not Path(iskonto).exists():
            messagebox.showerror("Hata", "İskonto dosyası bulunamadı!")
            return
        
        self.is_processing = True
        self.process_btn.configure(state="disabled", text="⏳ İşlem Devam Ediyor...")
        self.progress_bar.set(0)
        self._log("Analiz başlatılıyor...", "info")
        
        def analysis_thread():
            try:
                result = self.analiz.analyze(karlilik, iskonto)
                
                if result is not None and not result.empty:
                    self.result_queue.put(('complete', result))
                else:
                    self.result_queue.put(('error', "Analiz sonucu boş döndü"))
                    
            except Exception as e:
                logger.error(f"Analiz hatası: {e}")
                self.result_queue.put(('error', str(e)))
        
        threading.Thread(target=analysis_thread, daemon=True).start()
    
    def _update_progress(self, value: int, status: str):
        if self.progress_bar:
            self.progress_bar.set(value / 100)
        if self.progress_label:
            self.progress_label.configure(text=f"İlerleme %{value}: {status}")
    
    def _on_analysis_complete(self, result):
        self.is_processing = False
        self.analiz_sonucu = result
        
        self.process_btn.configure(state="normal", text="✨ Analizi Başlat")
        self.progress_bar.set(1)
        self.progress_label.configure(text="✓ Analiz tamamlandı!")
        
        self._log("✓ Karlılık analizi başarıyla tamamlandı!", "success")
        self._log(f"📊 {len(result)} ürün analiz edildi", "info")
        
        # Dashboard güncelle
        self.dashboard_tab.update_data(result)
        
        # Başarı mesajı
        messagebox.showinfo(
            "Başarılı! 🎉",
            f"Karlılık analizi tamamlandı!\n\n"
            f"📊 {len(result)} ürün analiz edildi.\n\n"
            f"📊 Dashboard sekmesinde detaylı analizi görebilirsiniz."
        )
    
    def _on_analysis_error(self, error_msg: str):
        self.is_processing = False
        self.process_btn.configure(state="normal", text="✨ Analizi Başlat")
        self.progress_bar.set(0)
        self.progress_label.configure(text="❌ Hata oluştu")
        
        self._log(f"Hata: {error_msg}", "error")
        messagebox.showerror("Analiz Hatası", f"Analiz sırasında hata oluştu:\n{error_msg}")
    
    # =========================================================================
    # YARDIMCI
    # =========================================================================
    
    def _log(self, message: str, msg_type: str = "info"):
        if self.log_widget:
            self.log_widget.log(message, msg_type)
    
    def _clear_all(self):
        self.karlilik_path.set("")
        self.iskonto_path.set("")
        self.karlilik_label.configure(text="Henüz dosya seçilmedi...", text_color=COLORS['text_muted'])
        self.iskonto_label.configure(text="Henüz dosya seçilmedi...", text_color=COLORS['text_muted'])
        self.progress_bar.set(0)
        self.progress_label.configure(text="✓ Hazır")
        self.log_widget.clear()
        self._log("Tüm alanlar temizlendi", "info")
    
    def _open_last_result(self):
        try:
            xlsx_files = list(Path.cwd().glob("karlilik_*.xlsx")) + list(Path.cwd().glob("*_result*.xlsx"))
            if xlsx_files:
                latest = max(xlsx_files, key=lambda p: p.stat().st_mtime)
                import subprocess
                import platform
                
                if platform.system() == "Windows":
                    subprocess.Popen(['start', '', str(latest)], shell=True)
                elif platform.system() == "Darwin":
                    subprocess.Popen(['open', str(latest)])
                else:
                    subprocess.Popen(['xdg-open', str(latest)])
                
                self._log(f"Açıldı: {latest.name}", "success")
            else:
                messagebox.showinfo("Bilgi", "Kayıtlı sonuç bulunamadı!")
        except Exception as e:
            self._log(f"Dosya açma hatası: {e}", "error")
    
    def on_closing(self):
        self._closing = True


# =============================================================================
# STANDALONE
# =============================================================================

def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("Bupiliç - Karlılık Analizi")
    root.geometry("1400x900")
    root.minsize(1200, 800)
    
    app = KarlilikApp(root, standalone=True)
    app.pack(fill="both", expand=True)
    
    root.protocol("WM_DELETE_WINDOW", lambda: (app.on_closing(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
