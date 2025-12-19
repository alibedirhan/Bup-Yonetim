#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - UI Yardımcı Sınıflar
ToolTip, ProgressManager ve diğer yardımcı sınıflar
"""

import tkinter as tk
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

import queue
import time
import logging

logger = logging.getLogger(__name__)

class ToolTip:
    """
    Tooltip widget'ı için sınıf
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        # Mouse event'leri bind et
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event=None):
        """Mouse üzerine geldiğinde"""
        self.show_tooltip()
    
    def on_leave(self, event=None):
        """Mouse çıktığında"""
        self.hide_tooltip()
    
    def show_tooltip(self):
        """Tooltip'i göster"""
        if self.tooltip_window or not self.text:
            return
        
        x, y, cx, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Tooltip penceresi oluştur
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Tooltip içeriği
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            justify='left',
            background="#ffffe0",
            relief='solid',
            borderwidth=1,
            font=("tahoma", "8", "normal"),
            wraplength=300
        )
        label.pack(ipadx=1)
    
    def hide_tooltip(self):
        """Tooltip'i gizle"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

def add_tooltip(widget, text):
    """Widget'a tooltip ekle - Kolaylık fonksiyonu"""
    return ToolTip(widget, text)

class ProgressManager:
    """Gelişmiş progress bar yönetimi"""
    
    def __init__(self, progress_bar, status_label):
        self.progress_bar = progress_bar
        self.status_label = status_label
        self.current_task = None
        self.is_running = False
        
    def start_task(self, task_name: str, total_steps: int = 100):
        """Görev başlat"""
        self.current_task = task_name
        self.total_steps = total_steps
        self.current_step = 0
        self.is_running = True
        self.progress_bar.set(0)
        self.status_label.configure(text=f"{task_name} başlatılıyor...")
        
    def update_progress(self, step: int, message: str = ""):
        """Progress güncelle"""
        if not self.is_running:
            return
            
        self.current_step = step
        progress_value = min(step / self.total_steps, 1.0)
        self.progress_bar.set(progress_value)
        
        if message:
            self.status_label.configure(text=f"{self.current_task}: {message}")
        else:
            percentage = int(progress_value * 100)
            self.status_label.configure(text=f"{self.current_task} - %{percentage}")
            
    def finish_task(self, success_message: str = "Tamamlandı"):
        """Görevi bitir"""
        self.is_running = False
        self.progress_bar.set(1.0)
        self.status_label.configure(text=success_message)
        
    def error_task(self, error_message: str):
        """Hata durumu"""
        self.is_running = False
        self.progress_bar.set(0)
        self.status_label.configure(text=f"Hata: {error_message}")

class ThreadedAnalysis:
    """Thread'li analiz sistemi"""
    
    def __init__(self, gui_instance):
        self.gui = gui_instance
        self.progress_manager = ProgressManager(
            gui_instance.progress_bar, 
            gui_instance.status_label
        )
        self.message_queue = queue.Queue()
        
    def start_analysis_threaded(self):
        """Analizi thread'de başlat"""
        if not hasattr(self.gui, 'excel_processor') or self.gui.excel_processor.processed_df is None:
            from tkinter import messagebox
            messagebox.showerror("Hata", "Önce Excel verisi işlenmelidir!")
            return
            
        # UI elementlerini devre dışı bırak
        self.gui.analyze_btn.configure(state="disabled")
        if hasattr(self.gui, 'load_excel_btn'):
            self.gui.load_excel_btn.configure(state="disabled")
        
        # Thread başlat
        import threading
        analysis_thread = threading.Thread(
            target=self._analysis_worker, 
            daemon=True
        )
        analysis_thread.start()
        
        # Message queue'yu kontrol et
        self.gui.root.after(100, self._check_message_queue)
        
    def _analysis_worker(self):
        """Analiz worker thread'i"""
        try:
            # 1. Veri hazırlama
            self._send_progress(10, "Veri hazırlanıyor...")
            time.sleep(0.1)
            
            if not self.gui.analysis_engine.set_data(self.gui.excel_processor.processed_df):
                raise Exception("Analiz verisi ayarlanamadı")
                
            # 2. ARAÇ listesi çıkarma
            self._send_progress(20, "ARAÇ listesi hazırlanıyor...")
            arac_list = self.gui.analysis_engine._extract_arac_numbers()
            
            if not arac_list:
                raise Exception("Geçerli ARAÇ numarası bulunamadı")
                
            # 3. ARAÇ'ları tek tek analiz et
            total_aracs = len(arac_list)
            
            for i, arac_no in enumerate(arac_list):
                progress = 20 + (i * 60 / total_aracs)
                self._send_progress(progress, f"ARAÇ {arac_no} analiz ediliyor...")
                
                # Analiz yap
                result = self.gui.analysis_engine._analyze_single_arac_internal(arac_no)
                if result:
                    self.gui.current_analysis_results[str(arac_no)] = result
                    
                time.sleep(0.05)  # Progress görünürlüğü için
                
            # 4. Sonuçları tamamla
            self._send_progress(85, "Sonuçlar hazırlanıyor...")
            self.gui.analysis_engine.analysis_results = self.gui.current_analysis_results
            
            # 5. UI güncellemesi için sinyal gönder
            self._send_progress(95, "Arayüz güncelleniyor...")
            self._send_message("UPDATE_UI")
            
            # 6. Başarı
            self._send_progress(100, f"Analiz tamamlandı - {total_aracs} ARAÇ")
            self._send_message("ANALYSIS_COMPLETE")
            
        except Exception as e:
            self._send_message(("ERROR", str(e)))
            
    def _send_progress(self, value: float, message: str):
        """Progress güncelleme mesajı gönder"""
        self.message_queue.put(("PROGRESS", value, message))
        
    def _send_message(self, message):
        """Genel mesaj gönder"""
        self.message_queue.put(message)
        
    def _check_message_queue(self):
        """Message queue'yu kontrol et"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                
                if isinstance(message, tuple):
                    if message[0] == "PROGRESS":
                        _, value, text = message
                        self.progress_manager.update_progress(value, text)
                    elif message[0] == "ERROR":
                        _, error_text = message
                        self.progress_manager.error_task(error_text)
                        from tkinter import messagebox
                        messagebox.showerror("Analiz Hatası", error_text)
                        self._enable_buttons()
                        return
                        
                elif message == "UPDATE_UI":
                    self.gui.update_analysis_results()
                    
                elif message == "ANALYSIS_COMPLETE":
                    self.progress_manager.finish_task("Analiz başarıyla tamamlandı")
                    self._enable_buttons()
                    return
                    
        except queue.Empty:
            pass
            
        # Devam et
        self.gui.root.after(100, self._check_message_queue)
        
    def _enable_buttons(self):
        """Butonları tekrar aktif et"""
        self.gui.analyze_btn.configure(state="normal")
        if hasattr(self.gui, 'load_excel_btn'):
            self.gui.load_excel_btn.configure(state="normal")

def show_help_dialog(parent):
    """Yardım dialog'unu göster"""
    try:
        help_window = ctk.CTkToplevel(parent)
        help_window.title("Kullanım Kılavuzu")
        help_window.geometry("700x600")
        help_window.transient(parent)
        
        # Scrollable text
        textbox = ctk.CTkTextbox(help_window)
        textbox.pack(fill="both", expand=True, padx=20, pady=20)
        
        help_content = """ ... (uzun kullanım kılavuzu içeriği burada) ... """
        textbox.insert("1.0", help_content)
        textbox.configure(state="disabled") 
        
    except Exception as e:
        logger.error(f"Yardım penceresi açma hatası: {e}")

def show_about_dialog(parent):
    """Hakkında dialog'unu göster"""
    try:
        about_window = ctk.CTkToplevel(parent)
        about_window.title("Hakkında")
        about_window.geometry("500x400")
        
        about_window.transient(parent)
        about_window.after(100, lambda: about_window.grab_set())
        about_window.focus()
        
        content_frame = ctk.CTkFrame(about_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            content_frame,
            text="Excel Cari Yaşlandırma İşleyici",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=10)
        
        version_label = ctk.CTkLabel(
            content_frame,
            text="Versiyon 2.0 - Modüler Yapı",
            font=ctk.CTkFont(size=14)
        )
        version_label.pack(pady=5)
        
        description = """ ... (uygulama açıklaması burada) ... """
        desc_label = ctk.CTkLabel(
            content_frame,
            text=description,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        desc_label.pack(pady=10, padx=20)
        
        close_btn = ctk.CTkButton(
            content_frame,
            text="Kapat",
            command=about_window.destroy,
            width=100
        )
        close_btn.pack(pady=20)
        
    except Exception as e:
        logger.error(f"Hakkında penceresi açma hatası: {e}")

def show_quick_help(gui_instance):
    """Hızlı yardım penceresi"""
    help_window = ctk.CTkToplevel(gui_instance.root)
    help_window.title("Hızlı Yardım")
    help_window.geometry("600x400")
    help_window.transient(gui_instance.root)
    help_window.grab_set()
    
    # İçerik
    content_frame = ctk.CTkScrollableFrame(help_window)
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    help_content = """
🚀 HIZLI BAŞLANGIÇ REHBERİ

1️⃣ DOSYA İŞLEME:
   • "Dosya Seç" → Excel dosyanızı seçin
   • "İşleme Başla" → Veriyi temizleyin
   • İşlem tamamlandığında otomatik önizleme gösterilir

2️⃣ ARAÇ ANALİZİ:
   • "Analiz Başlat" → ARAÇ bazlı analiz yapın
   • "Analiz Genel Bakış" tab'ında özet görün
   • "ARAÇ Detayı" tab'ında tek ARAÇ analizi

3️⃣ SORUMLU ATAMA:
   • "Sorumlu Atama" tab'ına gidin
   • ARAÇ seçin, personel bilgilerini girin
   • "Sorumlu Ata" butonuna tıklayın

4️⃣ RAPOR OLUŞTURMA:
   • "Raporlar" tab'ında rapor türü seçin
   • ARAÇ seçimi yapın (tümü veya seçili)
   • "Rapor Oluştur" → "Excel'e Aktar"

5️⃣ GRAFİKLER:
   • "Grafikler" tab'ında grafik türü seçin
   • "Grafik Oluştur" → görsel analiz
   • "Grafiği Kaydet" ile PNG/PDF olarak kaydet

💡 İPUÇLARI:
   • Excel dosyası kapalı olmalı
   • Büyük dosyalar biraz zaman alabilir
   • Tüm veriler otomatik kaydedilir
   • Progress bar'ları takip edin
    """
    
    ctk.CTkLabel(
        content_frame,
        text=help_content,
        font=ctk.CTkFont(size=12),
        justify="left"
    ).pack(pady=10)
    
    # Kapat butonu
    ctk.CTkButton(
        help_window,
        text="Kapat",
        command=help_window.destroy,
        width=100
    ).pack(pady=10)

def show_keyboard_shortcuts(gui_instance):
    """Klavye kısayolları penceresi"""
    shortcuts_window = ctk.CTkToplevel(gui_instance.root)
    shortcuts_window.title("Klavye Kısayolları")
    shortcuts_window.geometry("500x300")
    shortcuts_window.transient(gui_instance.root)
    shortcuts_window.grab_set()
    
    # İçerik
    content_frame = ctk.CTkFrame(shortcuts_window)
    content_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    shortcuts_content = """
⌨️ KLAVYE KISAYOLLARI

Ctrl + O          Dosya Seç
Ctrl + S          Kaydet
F5                İşlemeyi Yenile
Ctrl + A          Analiz Başlat
Ctrl + R          Rapor Oluştur
Ctrl + G          Grafik Oluştur

F1                Bu Yardım
Ctrl + H          Hızlı Yardım
Esc               İptal / Kapat

Tab Geçişleri:
Ctrl + 1          Dosya İşleme
Ctrl + 2          Analiz Genel Bakış
Ctrl + 3          ARAÇ Detayı
Ctrl + 4          Sorumlu Atama
Ctrl + 5          Raporlar
Ctrl + 6          Grafikler
    """
    
    ctk.CTkLabel(
        content_frame,
        text=shortcuts_content,
        font=ctk.CTkFont(size=12, family="monospace"),
        justify="left"
    ).pack(expand=True)