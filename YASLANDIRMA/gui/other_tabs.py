#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - Diğer Tab'lar (DÜZELTİLMİŞ)
Assignment, Reports ve Charts tab'ları - Atama görüntüleme düzeltmesi
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

import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def create_assignment_tab(notebook, gui_instance):
    """Sorumlu Atama tab'ı oluştur - DÜZELTİLMİŞ"""
    try:
        assignment_frame = ctk.CTkFrame(notebook)
        notebook.add(assignment_frame, text="Sorumlu Atama")
        
        # Üst kontrol paneli
        control_frame = ctk.CTkFrame(assignment_frame, height=80)
        control_frame.pack(fill="x", padx=5, pady=5)
        control_frame.pack_propagate(False)
        
        # Sol taraf - ARAÇ seçimi
        left_control = ctk.CTkFrame(control_frame)
        left_control.pack(side="left", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(
            left_control,
            text="ARAÇ:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=5)
        
        gui_instance.assignment_arac_dropdown = ctk.CTkComboBox(
            left_control,
            values=["ARAÇ seçin..."],
            command=gui_instance.on_assignment_arac_selected,
            width=150
        )
        gui_instance.assignment_arac_dropdown.pack(side="left", padx=5)
        
        # Sağ taraf - İşlem butonları
        right_control = ctk.CTkFrame(control_frame)
        right_control.pack(side="right", fill="y", padx=10, pady=10)
        
        gui_instance.assign_btn = ctk.CTkButton(
            right_control,
            text="Sorumlu Ata",
            command=gui_instance.assign_personnel,
            fg_color="green",
            height=30
        )
        gui_instance.assign_btn.pack(side="left", padx=5)
        
        gui_instance.remove_assignment_btn = ctk.CTkButton(
            right_control,
            text="Atamayı Kaldır",
            command=gui_instance.remove_assignment,
            fg_color="red",
            height=30
        )
        gui_instance.remove_assignment_btn.pack(side="left", padx=5)
        
        # Atamaları yenile butonu - YENİ
        refresh_assignments_btn = ctk.CTkButton(
            right_control,
            text="Listeyi Yenile",
            command=lambda: refresh_assignment_list(gui_instance),
            fg_color="blue",
            height=30
        )
        refresh_assignments_btn.pack(side="left", padx=5)
        
        # Ana içerik alanı
        content_frame = ctk.CTkFrame(assignment_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Sol panel - Atama formu
        form_frame = ctk.CTkFrame(content_frame, width=400)
        form_frame.pack(side="left", fill="y", padx=5, pady=5)
        form_frame.pack_propagate(False)
        
        # Form başlığı
        ctk.CTkLabel(
            form_frame,
            text="Sorumlu Atama Formu",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Form alanları
        form_content = ctk.CTkFrame(form_frame)
        form_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Form elemanları oluştur
        create_assignment_form(form_content, gui_instance)
        
        # Sağ panel - Atama listesi
        create_assignment_list_panel(content_frame, gui_instance)
        
        # İlk yüklemede mevcut atamaları göster - YENİ
        gui_instance.root.after(100, lambda: load_and_display_assignments(gui_instance))
        
        logger.info("Sorumlu atama tab'ı oluşturuldu")
        return assignment_frame
        
    except Exception as e:
        logger.error(f"Sorumlu atama tab'ı oluşturma hatası: {e}")
        return None

def create_assignment_form(parent, gui_instance):
    """Atama formu elemanlarını oluştur"""
    # Sorumlu adı
    ctk.CTkLabel(parent, text="Sorumlu Adı:").pack(anchor="w", pady=(10, 2))
    gui_instance.personnel_name_entry = ctk.CTkEntry(parent, placeholder_text="Ad Soyad")
    gui_instance.personnel_name_entry.pack(fill="x", pady=(0, 10))
    
    # Email
    ctk.CTkLabel(parent, text="Email:").pack(anchor="w", pady=(0, 2))
    gui_instance.personnel_email_entry = ctk.CTkEntry(parent, placeholder_text="email@example.com")
    gui_instance.personnel_email_entry.pack(fill="x", pady=(0, 10))
    
    # Telefon
    ctk.CTkLabel(parent, text="Telefon:").pack(anchor="w", pady=(0, 2))
    gui_instance.personnel_phone_entry = ctk.CTkEntry(parent, placeholder_text="0555 123 45 67")
    gui_instance.personnel_phone_entry.pack(fill="x", pady=(0, 10))
    
    # Departman
    ctk.CTkLabel(parent, text="Departman:").pack(anchor="w", pady=(0, 2))
    gui_instance.personnel_department_entry = ctk.CTkEntry(parent, placeholder_text="Satış, Pazarlama vb.")
    gui_instance.personnel_department_entry.pack(fill="x", pady=(0, 10))
    
    # Notlar
    ctk.CTkLabel(parent, text="Notlar:").pack(anchor="w", pady=(0, 2))
    gui_instance.personnel_notes_textbox = ctk.CTkTextbox(parent, height=80)
    gui_instance.personnel_notes_textbox.pack(fill="x", pady=(0, 10))

def create_assignment_list_panel(parent, gui_instance):
    """Atama listesi panelini oluştur"""
    list_frame = ctk.CTkFrame(parent)
    list_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
    
    # Liste başlığı ve durum etiketi
    header_frame = ctk.CTkFrame(list_frame)
    header_frame.pack(fill="x", pady=5)
    
    ctk.CTkLabel(
        header_frame,
        text="Mevcut Atamalar",
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(side="left", pady=5)
    
    # Atama sayısı etiketi - YENİ
    gui_instance.assignment_count_label = ctk.CTkLabel(
        header_frame,
        text="(0 atama)",
        font=ctk.CTkFont(size=12),
        text_color="gray"
    )
    gui_instance.assignment_count_label.pack(side="left", padx=10, pady=5)
    
    # Treeview frame
    tree_frame = ctk.CTkFrame(list_frame)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Scrollbarlar
    v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
    h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
    
    # Assignment Treeview
    gui_instance.assignment_tree = ttk.Treeview(
        tree_frame,
        yscrollcommand=v_scrollbar.set,
        xscrollcommand=h_scrollbar.set
    )
    
    v_scrollbar.config(command=gui_instance.assignment_tree.yview)
    h_scrollbar.config(command=gui_instance.assignment_tree.xview)
    
    # Grid yerleşimi
    gui_instance.assignment_tree.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")
    
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)
    
    # Treeview sütunları
    gui_instance.assignment_tree["columns"] = ("arac_no", "sorumlu", "email", "telefon", "departman", "tarih")
    gui_instance.assignment_tree["show"] = "headings"
    
    # Başlıklar
    gui_instance.assignment_tree.heading("arac_no", text="ARAÇ No")
    gui_instance.assignment_tree.heading("sorumlu", text="Sorumlu")
    gui_instance.assignment_tree.heading("email", text="Email")
    gui_instance.assignment_tree.heading("telefon", text="Telefon")
    gui_instance.assignment_tree.heading("departman", text="Departman")
    gui_instance.assignment_tree.heading("tarih", text="Atama Tarihi")
    
    # Sütun genişlikleri
    gui_instance.assignment_tree.column("arac_no", width=80)
    gui_instance.assignment_tree.column("sorumlu", width=150)
    gui_instance.assignment_tree.column("email", width=200)
    gui_instance.assignment_tree.column("telefon", width=120)
    gui_instance.assignment_tree.column("departman", width=120)
    gui_instance.assignment_tree.column("tarih", width=120)
    
    # Event binding
    gui_instance.assignment_tree.bind("<<TreeviewSelect>>", gui_instance.on_assignment_tree_select)

def load_and_display_assignments(gui_instance):
    """Kaydedilmiş atamaları yükle ve göster - YENİ"""
    try:
        # Data manager varsa verileri yükle
        if hasattr(gui_instance, 'data_manager'):
            # Atama verilerini yükle
            assignment_data = gui_instance.data_manager.load_assignments_data()
            
            if assignment_data and 'assignments' in assignment_data:
                gui_instance.current_assignments = assignment_data['assignments']
                logger.info(f"JSON'dan {len(gui_instance.current_assignments)} atama yüklendi")
                
                # Assignment manager'a da yükle
                if hasattr(gui_instance, 'assignment_manager'):
                    gui_instance.assignment_manager.load_assignments(gui_instance.current_assignments)
                
                # Tree'yi güncelle
                update_assignment_tree_display(gui_instance)
            else:
                logger.info("Kaydedilmiş atama verisi bulunamadı")
                gui_instance.current_assignments = {}
        
        # ARAÇ listesini güncelle (eğer analiz sonuçları varsa)
        if hasattr(gui_instance, 'current_analysis_results') and gui_instance.current_analysis_results:
            update_arac_dropdown(gui_instance)
            
    except Exception as e:
        logger.error(f"Atama verileri yükleme hatası: {e}")
        gui_instance.current_assignments = {}

def update_assignment_tree_display(gui_instance):
    """Atama tree'sini güncelle - İYİLEŞTİRİLMİŞ"""
    try:
        # Mevcut verileri temizle
        for item in gui_instance.assignment_tree.get_children():
            gui_instance.assignment_tree.delete(item)
        
        # Atamaları ekle
        assignment_count = 0
        for arac_no, assignment in gui_instance.current_assignments.items():
            # Tarih formatını düzelt
            atama_tarihi = assignment.get('atama_tarihi', '')
            if atama_tarihi and 'T' in atama_tarihi:
                atama_tarihi = atama_tarihi.split('T')[0]
            
            values = (
                arac_no,
                assignment.get('sorumlu', ''),
                assignment.get('email', ''),
                assignment.get('telefon', ''),
                assignment.get('departman', ''),
                atama_tarihi
            )
            gui_instance.assignment_tree.insert("", "end", values=values)
            assignment_count += 1
        
        # Atama sayısını güncelle
        if hasattr(gui_instance, 'assignment_count_label'):
            gui_instance.assignment_count_label.configure(
                text=f"({assignment_count} atama)",
                text_color="green" if assignment_count > 0 else "gray"
            )
        
        logger.info(f"Atama tree güncellendi: {assignment_count} kayıt")
        
    except Exception as e:
        logger.error(f"Atama tree güncelleme hatası: {e}")

def update_arac_dropdown(gui_instance):
    """ARAÇ dropdown listesini güncelle - YENİ"""
    try:
        if hasattr(gui_instance, 'analysis_engine'):
            arac_list = gui_instance.analysis_engine.get_arac_list()
            if arac_list:
                gui_instance.assignment_arac_dropdown.configure(values=["ARAÇ seçin..."] + arac_list)
                logger.info(f"ARAÇ dropdown güncellendi: {len(arac_list)} ARAÇ")
    except Exception as e:
        logger.error(f"ARAÇ dropdown güncelleme hatası: {e}")

def refresh_assignment_list(gui_instance):
    """Atama listesini yenile - YENİ"""
    try:
        # Verileri yeniden yükle
        load_and_display_assignments(gui_instance)
        
        # İstatistikleri güncelle
        if hasattr(gui_instance, 'update_statistics_cards'):
            gui_instance.update_statistics_cards()
        
        messagebox.showinfo("Başarılı", "Atama listesi yenilendi")
        
    except Exception as e:
        logger.error(f"Liste yenileme hatası: {e}")
        messagebox.showerror("Hata", f"Liste yenileme hatası: {e}")

# Diğer tab fonksiyonları aynı kalıyor...
def create_reports_tab(notebook, gui_instance):
    """Raporlar tab'ını oluştur"""
    try:
        reports_frame = ctk.CTkFrame(notebook)
        notebook.add(reports_frame, text="Raporlar")
        
        # Üst kontrol paneli
        control_frame = ctk.CTkFrame(reports_frame, height=100)
        control_frame.pack(fill="x", padx=5, pady=5)
        control_frame.pack_propagate(False)
        
        # Sol taraf - Rapor türü seçimi
        left_control = ctk.CTkFrame(control_frame)
        left_control.pack(side="left", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(
            left_control,
            text="Rapor Türü:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=2)
        
        gui_instance.report_type_var = ctk.StringVar(value="arac_summary")
        
        report_types = [
            ("ARAÇ Özet Raporu", "arac_summary"),
            ("Detaylı Analiz Raporu", "detailed_analysis"),
            ("Atama Raporu", "assignment_report"),
            ("Yaşlandırma Analizi", "aging_analysis"),
            ("Karşılaştırma Raporu", "comparison_report")
        ]
        
        for text, value in report_types:
            radio = ctk.CTkRadioButton(
                left_control,
                text=text,
                variable=gui_instance.report_type_var,
                value=value
            )
            radio.pack(anchor="w", pady=1)
        
        # Orta - ARAÇ seçimi
        middle_control = ctk.CTkFrame(control_frame)
        middle_control.pack(side="left", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(
            middle_control,
            text="ARAÇ Seçimi:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=2)
        
        gui_instance.report_all_arac_var = ctk.BooleanVar(value=True)
        
        all_arac_check = ctk.CTkCheckBox(
            middle_control,
            text="Tüm ARAÇ'lar",
            variable=gui_instance.report_all_arac_var,
            command=gui_instance.on_report_all_arac_toggle
        )
        all_arac_check.pack(anchor="w", pady=2)
        
        # Çoklu ARAÇ seçimi için frame
        gui_instance.arac_selection_frame = ctk.CTkFrame(middle_control)
        gui_instance.arac_selection_frame.pack(fill="both", expand=True, pady=5)
        
        # Sağ taraf - İşlem butonları
        right_control = ctk.CTkFrame(control_frame)
        right_control.pack(side="right", fill="y", padx=10, pady=10)
        
        gui_instance.generate_report_btn = ctk.CTkButton(
            right_control,
            text="Rapor Oluştur",
            command=gui_instance.generate_report,
            fg_color="green",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        gui_instance.generate_report_btn.pack(pady=5)
        
        gui_instance.export_report_btn = ctk.CTkButton(
            right_control,
            text="Excel'e Aktar",
            command=gui_instance.export_report,
            height=35,
            state="disabled"
        )
        gui_instance.export_report_btn.pack(pady=5)
        
        # Ana içerik alanı
        content_frame = ctk.CTkFrame(reports_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Rapor önizleme alanı
        create_report_preview_panel(content_frame, gui_instance)
        
        logger.info("Raporlar tab'ı oluşturuldu")
        return reports_frame
        
    except Exception as e:
        logger.error(f"Raporlar tab'ı oluşturma hatası: {e}")
        return None

def create_report_preview_panel(parent, gui_instance):
    """Rapor önizleme panelini oluştur"""
    preview_frame = ctk.CTkFrame(parent)
    preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Önizleme başlığı
    ctk.CTkLabel(
        preview_frame,
        text="Rapor Önizleme",
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=10)
    
    # Treeview frame
    tree_frame = ctk.CTkFrame(preview_frame)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Scrollbarlar
    v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
    h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
    
    # Report Treeview
    gui_instance.report_tree = ttk.Treeview(
        tree_frame,
        yscrollcommand=v_scrollbar.set,
        xscrollcommand=h_scrollbar.set
    )
    
    v_scrollbar.config(command=gui_instance.report_tree.yview)
    h_scrollbar.config(command=gui_instance.report_tree.xview)
    
    # Grid yerleşimi
    gui_instance.report_tree.grid(row=0, column=0, sticky="nsew")
    v_scrollbar.grid(row=0, column=1, sticky="ns")
    h_scrollbar.grid(row=1, column=0, sticky="ew")
    
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)
    
    # Rapor durum etiketi
    gui_instance.report_status_label = ctk.CTkLabel(
        preview_frame,
        text="Rapor oluşturmak için 'Rapor Oluştur' butonuna tıklayın",
        font=ctk.CTkFont(size=12)
    )
    gui_instance.report_status_label.pack(pady=5)

def create_charts_tab(notebook, gui_instance):
    """Grafikler tab'ını oluştur"""
    try:
        charts_frame = ctk.CTkFrame(notebook)
        notebook.add(charts_frame, text="Grafikler")
        
        # Üst kontrol paneli
        control_frame = ctk.CTkFrame(charts_frame, height=80)
        control_frame.pack(fill="x", padx=5, pady=5)
        control_frame.pack_propagate(False)
        
        # Sol taraf - Grafik türü seçimi
        left_control = ctk.CTkFrame(control_frame)
        left_control.pack(side="left", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(
            left_control,
            text="Grafik Türü:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        gui_instance.chart_type_var = ctk.StringVar(value="arac_summary")
        
        chart_dropdown = ctk.CTkComboBox(
            left_control,
            values=[
                "ARAÇ Özet Grafiği",
                "Yaşlandırma Analizi",
                "ARAÇ Karşılaştırma", 
                "İş Yükü Dağılımı"
            ],
            variable=gui_instance.chart_type_var,
            command=gui_instance.on_chart_type_change
        )
        chart_dropdown.pack(pady=5)
        
        # Orta - ARAÇ seçimi
        middle_control = ctk.CTkFrame(control_frame)
        middle_control.pack(side="left", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(
            middle_control,
            text="ARAÇ Seçimi:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w")
        
        gui_instance.chart_arac_dropdown = ctk.CTkComboBox(
            middle_control,
            values=["Tüm ARAÇ'lar"],
            width=150
        )
        gui_instance.chart_arac_dropdown.pack(pady=5)
        
        # Sağ taraf - İşlem butonları
        right_control = ctk.CTkFrame(control_frame)
        right_control.pack(side="right", fill="y", padx=10, pady=10)
        
        gui_instance.create_chart_btn = ctk.CTkButton(
            right_control,
            text="Grafik Oluştur",
            command=gui_instance.create_chart,
            fg_color="green",
            height=35
        )
        gui_instance.create_chart_btn.pack(side="left", padx=5)
        
        gui_instance.save_chart_btn = ctk.CTkButton(
            right_control,
            text="Grafiği Kaydet",
            command=gui_instance.save_chart,
            height=35,
            state="disabled"
        )
        gui_instance.save_chart_btn.pack(side="left", padx=5)
        
        # Ana içerik alanı
        content_frame = ctk.CTkFrame(charts_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Grafik gösterim alanı
        gui_instance.chart_display_frame = ctk.CTkFrame(content_frame)
        gui_instance.chart_display_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Başlangıç mesajı
        gui_instance.chart_placeholder_label = ctk.CTkLabel(
            gui_instance.chart_display_frame,
            text="Grafik oluşturmak için yukarıdaki seçenekleri kullanın",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        gui_instance.chart_placeholder_label.pack(expand=True)
        
        logger.info("Grafikler tab'ı oluşturuldu")
        return charts_frame
        
    except Exception as e:
        logger.error(f"Grafikler tab'ı oluşturma hatası: {e}")
        return None