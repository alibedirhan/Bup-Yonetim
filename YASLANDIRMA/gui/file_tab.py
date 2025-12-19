#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - Dosya İşleme Tab'ı
Dosya seçme, işleme ve önizleme işlemleri
"""

import customtkinter as ctk
import tkinter.ttk as ttk
import logging

logger = logging.getLogger(__name__)

def create_file_processing_tab(notebook, gui_instance):
    """
    Dosya işleme tab'ını oluştur
    
    Args:
        notebook: Ana notebook widget'ı
        gui_instance: ExcelProcessorGUI sınıfının instance'ı
    
    Returns:
        Frame: Oluşturulan tab frame'i
    """
    try:
        # Ana frame
        file_frame = ctk.CTkFrame(notebook)
        notebook.add(file_frame, text="Dosya İşleme")
        
        # Sol panel (kontroller)
        left_frame = ctk.CTkFrame(file_frame, width=350)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Dosya bilgileri
        file_info_frame = ctk.CTkFrame(left_frame)
        file_info_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            file_info_frame, 
            text="Seçili Dosya:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=5)
        
        gui_instance.file_label = ctk.CTkLabel(
            file_info_frame,
            text="Dosya seçilmedi",
            fg_color=("gray70", "gray30"),
            corner_radius=6,
            height=30
        )
        gui_instance.file_label.pack(fill="x", pady=5)
        
        # İstatistikler bölümü
        gui_instance.stats_frame = ctk.CTkFrame(left_frame)
        gui_instance.stats_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            gui_instance.stats_frame,
            text="Veri İstatistikleri",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        gui_instance.stats_label = ctk.CTkLabel(
            gui_instance.stats_frame,
            text="Dosya yüklenmedi",
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        gui_instance.stats_label.pack(pady=5)
        
        # İşlem kontrolleri
        controls_frame = ctk.CTkFrame(left_frame)
        controls_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            controls_frame,
            text="İşlem Kontrolleri",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Önizleme butonu
        gui_instance.preview_btn = ctk.CTkButton(
            controls_frame,
            text="Önizleme",
            command=gui_instance.preview_processed,
            state="disabled",
            height=35
        )
        gui_instance.preview_btn.pack(fill="x", pady=5)
        
        # Geri Yükle butonu
        gui_instance.restore_btn = ctk.CTkButton(
            controls_frame,
            text="Geri Yükle",
            command=gui_instance.restore_backup,
            state="disabled",
            fg_color="orange",
            hover_color="dark orange",
            height=35
        )
        gui_instance.restore_btn.pack(fill="x", pady=5)
        
        # Progress bar
        progress_frame = ctk.CTkFrame(left_frame)
        progress_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            progress_frame,
            text="İşlem Durumu",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        gui_instance.progress = ctk.CTkProgressBar(progress_frame)
        gui_instance.progress.pack(fill="x", padx=10, pady=5)
        gui_instance.progress.set(0)
        
        gui_instance.status_label = ctk.CTkLabel(
            progress_frame,
            text="Hazır",
            font=ctk.CTkFont(size=12)
        )
        gui_instance.status_label.pack(pady=5)
        
        # Sağ panel (Önizleme) - create_preview_panel metodunu çağır
        gui_instance.create_preview_panel(file_frame)
        
        logger.info("Dosya işleme tab'ı oluşturuldu")
        return file_frame
        
    except Exception as e:
        logger.error(f"Dosya işleme tab'ı oluşturma hatası: {e}")
        return None
