#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - Analiz Tab'ları
Analiz genel bakış ve ARAÇ detay tab'ları
"""

import sys
from pathlib import Path

# Parent modül path'ini ekle
_current_dir = Path(__file__).parent
_parent_dir = _current_dir.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

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

import tkinter.ttk as ttk
import logging
from utils import format_number_display

logger = logging.getLogger(__name__)

def create_analysis_overview_tab(notebook, gui_instance):
    """Analiz genel bakış tab'ını oluştur"""
    try:
        overview_frame = ctk.CTkFrame(notebook)
        notebook.add(overview_frame, text="Analiz Genel Bakış")
        
        # Üst kontrol paneli
        control_frame = ctk.CTkFrame(overview_frame, height=80)
        control_frame.pack(fill="x", padx=5, pady=5)
        control_frame.pack_propagate(False)
        
        # Analiz durumu
        status_frame = ctk.CTkFrame(control_frame)
        status_frame.pack(side="left", fill="y", padx=10, pady=10)
        
        gui_instance.analysis_status_label = ctk.CTkLabel(
            status_frame,
            text="Analiz Durumu: Bekleniyor",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        gui_instance.analysis_status_label.pack(pady=10)
        
        # Analiz butonları
        buttons_frame = ctk.CTkFrame(control_frame)
        buttons_frame.pack(side="right", fill="y", padx=10, pady=10)
        
        refresh_analysis_btn = ctk.CTkButton(
            buttons_frame,
            text="Analizi Yenile",
            command=gui_instance.refresh_analysis,
            height=30
        )
        refresh_analysis_btn.pack(side="left", padx=5)
        
        save_analysis_btn = ctk.CTkButton(
            buttons_frame,
            text="Analizi Kaydet",
            command=gui_instance.save_analysis_data,
            height=30
        )
        save_analysis_btn.pack(side="left", padx=5)
        
        # Ana içerik alanı
        content_frame = ctk.CTkFrame(overview_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Sol panel - ARAÇ listesi
        left_panel = ctk.CTkFrame(content_frame, width=300)
        left_panel.pack(side="left", fill="y", padx=5, pady=5)
        left_panel.pack_propagate(False)
        
        # ARAÇ listesi başlık
        ctk.CTkLabel(
            left_panel,
            text="ARAÇ Listesi",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # ARAÇ listbox frame
        listbox_frame = ctk.CTkFrame(left_panel)
        listbox_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollbar ve Listbox
        gui_instance.arac_listbox = ctk.CTkTextbox(listbox_frame)
        gui_instance.arac_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ARAÇ seçim butonu
        gui_instance.select_arac_btn = ctk.CTkButton(
            left_panel,
            text="Detayları Göster",
            command=gui_instance.show_selected_arac_details
        )
        gui_instance.select_arac_btn.pack(pady=10)
        
        # Sağ panel - Özet bilgiler
        right_panel = ctk.CTkFrame(content_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Özet başlık
        ctk.CTkLabel(
            right_panel,
            text="Özet İstatistikler",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # İstatistik kartları
        create_statistics_cards(right_panel, gui_instance)
        
        logger.info("Analiz genel bakış tab'ı oluşturuldu")
        return overview_frame
        
    except Exception as e:
        logger.error(f"Analiz genel bakış tab'ı oluşturma hatası: {e}")
        return None

def create_statistics_cards(parent, gui_instance):
    """İstatistik kartlarını oluştur"""
    try:
        # Kartlar için frame
        cards_frame = ctk.CTkFrame(parent)
        cards_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # İlk satır
        row1_frame = ctk.CTkFrame(cards_frame)
        row1_frame.pack(fill="x", pady=5)
        
        # Toplam ARAÇ sayısı
        gui_instance.total_arac_card = create_stat_card(
            row1_frame, "Toplam ARAÇ", "0", "🚗"
        )
        gui_instance.total_arac_card.pack(side="left", fill="x", expand=True, padx=5)
        
        # Toplam müşteri sayısı
        gui_instance.total_customer_card = create_stat_card(
            row1_frame, "Toplam Müşteri", "0", "👥"
        )
        gui_instance.total_customer_card.pack(side="left", fill="x", expand=True, padx=5)
        
        # İkinci satır
        row2_frame = ctk.CTkFrame(cards_frame)
        row2_frame.pack(fill="x", pady=5)
        
        # Toplam bakiye
        gui_instance.total_balance_card = create_stat_card(
            row2_frame, "Toplam Bakiye", "0 TL", "💰"
        )
        gui_instance.total_balance_card.pack(side="left", fill="x", expand=True, padx=5)
        
        # Açık hesap
        gui_instance.open_balance_card = create_stat_card(
            row2_frame, "Açık Hesap", "0 TL", "⚠️"
        )
        gui_instance.open_balance_card.pack(side="left", fill="x", expand=True, padx=5)
        
        # Üçüncü satır
        row3_frame = ctk.CTkFrame(cards_frame)
        row3_frame.pack(fill="x", pady=5)
        
        # Atanmış ARAÇ sayısı
        gui_instance.assigned_arac_card = create_stat_card(
            row3_frame, "Atanmış ARAÇ", "0", "✅"
        )
        gui_instance.assigned_arac_card.pack(side="left", fill="x", expand=True, padx=5)
        
        # Atanmamış ARAÇ sayısı
        gui_instance.unassigned_arac_card = create_stat_card(
            row3_frame, "Atanmamış ARAÇ", "0", "❌"
        )
        gui_instance.unassigned_arac_card.pack(side="left", fill="x", expand=True, padx=5)
        
    except Exception as e:
        logger.error(f"İstatistik kartları oluşturma hatası: {e}")

def create_stat_card(parent, title, value, icon):
    """İstatistik kartı oluştur"""
    card = ctk.CTkFrame(parent, corner_radius=10)
    
    # Icon
    icon_label = ctk.CTkLabel(
        card,
        text=icon,
        font=ctk.CTkFont(size=24)
    )
    icon_label.pack(pady=(10, 5))
    
    # Başlık
    title_label = ctk.CTkLabel(
        card,
        text=title,
        font=ctk.CTkFont(size=14, weight="bold")
    )
    title_label.pack(pady=2)
    
    # Değer
    value_label = ctk.CTkLabel(
        card,
        text=value,
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color=("green", "light green")
    )
    value_label.pack(pady=(2, 10))
    
    # Değer label'ını kart ile ilişkilendir
    card.value_label = value_label
    
    return card

def create_arac_detail_tab(notebook, gui_instance):
    """ARAÇ detay tab'ını oluştur"""
    try:
        detail_frame = ctk.CTkFrame(notebook)
        notebook.add(detail_frame, text="ARAÇ Detayı")
        
        # Üst panel - ARAÇ seçimi
        top_frame = ctk.CTkFrame(detail_frame, height=60)
        top_frame.pack(fill="x", padx=5, pady=5)
        top_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            top_frame,
            text="ARAÇ Seçin:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=20, pady=20)
        
        # ARAÇ dropdown
        gui_instance.arac_dropdown = ctk.CTkComboBox(
            top_frame,
            values=["ARAÇ seçin..."],
            command=gui_instance.on_arac_selected,
            width=200
        )
        gui_instance.arac_dropdown.pack(side="left", padx=10, pady=20)
        
        # Yenile butonu
        refresh_btn = ctk.CTkButton(
            top_frame,
            text="Yenile",
            command=gui_instance.refresh_arac_list,
            width=100
        )
        refresh_btn.pack(side="left", padx=10, pady=20)
        
        # Ana içerik frame
        content_frame = ctk.CTkFrame(detail_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Sol panel - ARAÇ bilgileri
        create_arac_info_panel(content_frame, gui_instance)
        
        # Sağ panel - Müşteri listesi
        create_customer_list_panel(content_frame, gui_instance)
        
        logger.info("ARAÇ detay tab'ı oluşturuldu")
        return detail_frame
        
    except Exception as e:
        logger.error(f"ARAÇ detay tab'ı oluşturma hatası: {e}")
        return None

def create_arac_info_panel(parent, gui_instance):
    """ARAÇ bilgi panelini oluştur"""
    info_frame = ctk.CTkFrame(parent, width=400)
    info_frame.pack(side="left", fill="y", padx=5, pady=5)
    info_frame.pack_propagate(False)
    
    # Başlık
    ctk.CTkLabel(
        info_frame,
        text="ARAÇ Bilgileri",
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=10)
    
    # Bilgi alanları
    gui_instance.arac_info_text = ctk.CTkTextbox(info_frame)
    gui_instance.arac_info_text.pack(fill="both", expand=True, padx=10, pady=10)

def create_customer_list_panel(parent, gui_instance):
    """Müşteri listesi panelini oluştur"""
    customer_frame = ctk.CTkFrame(parent)
    customer_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
    
    # Başlık
    ctk.CTkLabel(
        customer_frame,
        text="Müşteri Detayları",
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=10)
    
    # Treeview frame
    tree_frame = ctk.CTkFrame(customer_frame)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Scrollbarlar
    v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
    h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
    
    # Treeview
    gui_instance.customer_tree = ttk.Treeview(
        tree_frame,
        yscrollcommand=v_scrollbar.set,
        xscrollcommand=h_scrollbar.set
    )
    
    v_scrollbar.config(command=gui_instance.customer_tree.yview)
    h_scrollbar.config(command=gui_instance.customer_tree.xview)
    
    # Grid yerleşimi
    gui_instance.customer_tree.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")
    
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)
