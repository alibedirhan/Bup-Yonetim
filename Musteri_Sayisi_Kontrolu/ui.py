#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Modern Excel Karşılaştırma UI Modülü
Türkçe karakter desteği ve cross-platform uyumluluk ile geliştirilmiştir.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
import sys
import platform
import logging
from pathlib import Path
from typing import Optional, Dict, List, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from main import ExcelComparisonLogic

# Constants
SUPPORTED_EXTENSIONS = ['.xlsx', '.xls']
WINDOW_MIN_SIZE = (850, 600)
DIALOG_SIZE = (900, 650)


class ModernExcelComparisonUI:
    """Modern Excel karşılaştırma kullanıcı arayüzü"""
    
    def __init__(self, root: tk.Tk, app_logic: 'ExcelComparisonLogic'):
        self.root = root
        self.app_logic = app_logic
        
        # Drag & Drop desteği kontrolü
        self.has_dnd = self._check_dnd_support()
        
        # UI bileşenleri
        self.result_tree: Optional[ttk.Treeview] = None
        self.status_var: Optional[tk.StringVar] = None
        self.progress: Optional[ttk.Progressbar] = None
        self.compare_btn: Optional[ttk.Button] = None
        self.save_excel = tk.BooleanVar(value=True)
        self.save_image = tk.BooleanVar(value=False)
        
        # Tema ve arayüz kurulumu
        self._setup_modern_theme()
        self._setup_main_window()
        self._create_modern_interface()
        
    def _check_dnd_support(self) -> bool:
        """Drag & Drop desteğini güvenli şekilde kontrol et"""
        try:
            import tkinterdnd2
            from tkinterdnd2 import DND_FILES, TkinterDnD
            return True
        except (ImportError, AttributeError, OSError):
            return False
        
    def _setup_modern_theme(self) -> None:
        """Modern tema ve renkler"""
        self.colors = {
            'primary': '#2563eb',
            'primary_hover': '#1d4ed8',
            'secondary': '#64748b',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'background': '#f8fafc',
            'card': '#ffffff',
            'border': '#e2e8f0',
            'text': '#1e293b',
            'text_light': '#64748b',
            'entry_normal': '#ffffff',
            'entry_hover': '#f0f9ff',
            'entry_drop': '#e0f2fe'
        }
        
        # Platform uyumlu font
        self.font_family = self._get_system_font()
        
        # TTK stilleri yapılandır
        self._configure_modern_styles()
        
    def _get_system_font(self) -> str:
        """Platform uyumlu font seç"""
        system = platform.system()
        if system == "Windows":
            return 'Segoe UI'
        elif system == "Darwin":  # macOS
            return 'SF Pro Display'
        else:  # Linux ve diğerleri
            return 'DejaVu Sans'
        
    def _configure_modern_styles(self) -> None:
        """Modern stil konfigürasyonları"""
        style = ttk.Style()
        
        # Mevcut temalar arasından en uygun olanı seç
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        
        # Özel stil tanımlamaları
        font_config = (self.font_family, 9)
        
        # Button stilleri
        style.configure('Modern.TButton', font=font_config, padding=(20, 12), relief='flat', borderwidth=0)
        style.configure('Accent.TButton', font=(self.font_family, 9, 'bold'), padding=(25, 15), relief='flat', borderwidth=0)
        style.configure('Secondary.TButton', font=font_config, padding=(20, 12), relief='flat', borderwidth=1)
        style.configure('Small.TButton', font=font_config, padding=(12, 8), relief='flat', borderwidth=1)
        
        # Diğer bileşenler
        style.configure('Small.TCheckbutton', font=font_config, padding=(0, 3))
        style.configure('Modern.TLabelframe', relief='flat', borderwidth=1, padding=20)
        style.configure('Modern.TLabelframe.Label', font=(self.font_family, 9, 'bold'), padding=(0, 5))
        style.configure('Modern.TEntry', font=font_config, padding=10, relief='flat', borderwidth=1)
        style.configure('DragDrop.TEntry', font=font_config, padding=8, relief='solid', borderwidth=2)
        style.configure('Modern.TCheckbutton', font=font_config, padding=(0, 5))
        style.configure('Modern.TRadiobutton', font=font_config, padding=(0, 3))
        
    def _setup_main_window(self) -> None:
        """Ana pencere ayarları"""
        self.root.title("CAL - Excel Karşılaştırma")
        self.root.geometry(f"{DIALOG_SIZE[0]}x{DIALOG_SIZE[1]}")
        self.root.minsize(*WINDOW_MIN_SIZE)
        
        # Pencereyi ortala
        self._center_window()
        
        # Arka plan rengi
        self.root.configure(bg=self.colors['background'])
        
        # Pencere kapatma protokolü
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # İkon ayarla (varsa)
        self._set_window_icon()
            
    def _set_window_icon(self) -> None:
        """Pencere ikonu ayarla"""
        try:
            icon_files = ['icon.ico', 'app.ico', 'excel.ico']
            for icon_file in icon_files:
                if Path(icon_file).exists():
                    self.root.iconbitmap(icon_file)
                    break
        except (tk.TclError, FileNotFoundError, OSError):
            # İkon bulunamazsa sessizce geç
            pass
            
    def _on_closing(self) -> None:
        """Pencere kapatılırken çalışır"""
        # Aktif thread'ler varsa uyar
        active_threads = threading.active_count()
        if active_threads > 1:  # Ana thread + aktif thread'ler
            result = messagebox.askyesno(
                "Çıkış", 
                "İşlem devam ediyor. Çıkmak istediğinizden emin misiniz?"
            )
            if not result:
                return
        
        try:
            self.root.quit()
            self.root.destroy()
        except:
            # Hata durumunda zorla kapat
            sys.exit(0)
            
    def _center_window(self) -> None:
        """Pencereyi ekranın ortasına yerleştir"""
        try:
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f'{width}x{height}+{x}+{y}')
        except:
            # Merkeze alma başarısızsa varsayılan konumu koru
            pass
        
    def _create_modern_interface(self) -> None:
        """Modern arayüz bileşenlerini oluştur"""
        # Ana konteyner
        main_container = tk.Frame(self.root, bg=self.colors['background'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        
        # Özel başlık bölümü oluştur
        self._create_custom_header(main_container)
        
        # İçerik container'ı
        content_frame = tk.Frame(main_container, bg=self.colors['background'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Sol panel (Dosya seçimi ve seçenekler)
        left_panel = tk.Frame(content_frame, bg=self.colors['background'])
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Sağ panel (Sonuçlar)
        right_panel = tk.Frame(content_frame, bg=self.colors['background'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Panelleri oluştur
        self._create_left_panel(left_panel)
        self._create_right_panel(right_panel)
        
    def _create_custom_header(self, parent: tk.Frame) -> None:
        """Özel başlık bölümü oluştur"""
        header_frame = tk.Frame(parent, bg=self.colors['card'], height=50, relief='solid', bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        header_frame.pack_propagate(False)
        
        # Orta - Excel Karşılaştırma
        center_frame = tk.Frame(header_frame, bg=self.colors['card'])
        center_frame.pack(expand=True, fill=tk.BOTH)
        
        title_label = tk.Label(
            center_frame,
            text="Excel Karşılaştırma",
            font=(self.font_family, 14, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        )
        title_label.pack(expand=True)
        
    def _create_left_panel(self, parent: tk.Frame) -> None:
        """Sol panel (Dosya seçimi ve seçenekler)"""
        # Sol panel için sabit genişlik ayarla
        parent.config(width=380)
        parent.pack_propagate(False)
        
        # Dosya seçimi kartı
        self._create_file_selection_card(parent)
        
        # Minimal boşluk
        tk.Frame(parent, bg=self.colors['background'], height=2).pack()
        
        # Seçenekler kartı
        self._create_options_card(parent)
        
        # Minimal boşluk
        tk.Frame(parent, bg=self.colors['background'], height=2).pack()
        
        # İşlem butonları
        self._create_action_buttons(parent)
        
    def _create_file_selection_card(self, parent: tk.Frame) -> None:
        """Dosya seçimi kartı"""
        card_frame = tk.Frame(parent, bg=self.colors['card'], relief='solid', bd=1)
        card_frame.pack(fill=tk.X, pady=2)
        
        # Kart başlığı
        header = tk.Label(
            card_frame,
            text="📁 Dosya Seçimi",
            font=(self.font_family, 9, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text'],
            pady=4
        )
        header.pack(anchor=tk.W, padx=12)
        
        # Dosya seçimi içeriği
        content_frame = tk.Frame(card_frame, bg=self.colors['card'])
        content_frame.pack(fill=tk.X, padx=8, pady=(0, 6))
        
        # Eski dosya
        self._create_dragdrop_file_input(
            content_frame,
            "Eski Tarihli Excel",
            self.app_logic.file1_path,
            self._browse_file1,
            "📄"
        )
        
        # Yeni dosya
        self._create_dragdrop_file_input(
            content_frame,
            "Yeni Tarihli Excel",
            self.app_logic.file2_path,
            self._browse_file2,
            "📄"
        )
        
        # Çıktı dosyası (sadece gösterim)
        self._create_display_input(
            content_frame,
            "Sonuç Dosyası",
            self.app_logic.output_path,
            "💾"
        )
        
    def _create_dragdrop_file_input(self, parent: tk.Frame, label_text: str, text_var: tk.StringVar, browse_command: Callable, icon: str) -> tk.Entry:
        """Drag & Drop destekli dosya input grubu"""
        # Ana container
        container = tk.Frame(parent, bg=self.colors['card'])
        container.pack(fill=tk.X, pady=(0, 4))
        
        # Label
        label = tk.Label(
            container,
            text=f"{icon} {label_text}",
            font=(self.font_family, 9, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        )
        label.pack(anchor=tk.W, pady=(0, 1))
        
        # İpucu metni
        hint_text = "Sürükle veya Gözat" if self.has_dnd else "Gözat ile Seç"
        hint_label = tk.Label(
            container,
            text=hint_text,
            font=(self.font_family, 8, 'italic'),
            bg=self.colors['card'],
            fg=self.colors['text_light']
        )
        hint_label.pack(anchor=tk.W, pady=(0, 1))
        
        # Input ve buton frame
        input_frame = tk.Frame(container, bg=self.colors['card'])
        input_frame.pack(fill=tk.X)
        
        # Entry
        entry = ttk.Entry(
            input_frame,
            textvariable=text_var,
            font=(self.font_family, 9),
            style='DragDrop.TEntry'
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        
        # Gözat butonu
        browse_btn = ttk.Button(
            input_frame,
            text="Gözat",
            command=browse_command,
            style='Small.TButton'
        )
        browse_btn.pack(side=tk.RIGHT)
        
        # Drag & Drop fonksiyonalitesi ekle
        if self.has_dnd:
            self._setup_drag_drop_for_entry(entry, text_var, browse_command)
        else:
            # Double-click ile dosya seçimi
            entry.bind('<Double-Button-1>', lambda e: browse_command())
        
        return entry
    
    def _setup_drag_drop_for_entry(self, entry_widget: ttk.Entry, text_var: tk.StringVar, browse_command: Callable) -> None:
        """Entry widget'ına drag & drop fonksiyonalitesi ekle"""
        if not self.has_dnd:
            return
            
        try:
            from tkinterdnd2 import DND_FILES
            
            def on_drop(event):
                try:
                    files = self.root.tk.splitlist(event.data)
                    if files:
                        file_path = files[0]
                        
                        if self._validate_dropped_file(file_path):
                            text_var.set(file_path)
                            self._show_entry_success(entry_widget)
                            
                            # Eğer file1 ise output filename'i güncelle
                            if text_var == self.app_logic.file1_path:
                                self.app_logic.update_output_filename(file_path)
                        else:
                            self._show_entry_error(entry_widget)
                except Exception as e:
                    logging.error(f"Drop işlemi hatası: {e}")
                    self._show_entry_error(entry_widget)
            
            def on_drag_enter(event):
                self._set_entry_bg(entry_widget, self.colors['entry_hover'])
            
            def on_drag_leave(event):
                self._set_entry_bg(entry_widget, self.colors['entry_normal'])
            
            # Event'leri bağla
            entry_widget.drop_target_register(DND_FILES)
            entry_widget.dnd_bind('<<Drop>>', on_drop)
            entry_widget.dnd_bind('<<DragEnter>>', on_drag_enter)
            entry_widget.dnd_bind('<<DragLeave>>', on_drag_leave)
            
        except (ImportError, AttributeError, OSError):
            # tkinterdnd2 yoksa double-click ile dosya seçimi
            entry_widget.bind('<Double-Button-1>', lambda e: browse_command())
    
    def _set_entry_bg(self, entry_widget: ttk.Entry, color: str) -> None:
        """Entry widget'ının arka plan rengini değiştir"""
        try:
            style = ttk.Style()
            style.configure('DragDrop.TEntry', fieldbackground=color)
        except Exception:
            pass
    
    def _show_entry_success(self, entry_widget: ttk.Entry) -> None:
        """Entry için başarı visual feedback"""
        try:
            self._set_entry_bg(entry_widget, self.colors['success'])
            self.root.after(500, lambda: self._set_entry_bg(entry_widget, self.colors['entry_normal']))
        except Exception:
            pass
    
    def _show_entry_error(self, entry_widget: ttk.Entry) -> None:
        """Entry için hata visual feedback"""
        try:
            self._set_entry_bg(entry_widget, self.colors['danger'])
            self.root.after(800, lambda: self._set_entry_bg(entry_widget, self.colors['entry_normal']))
        except Exception:
            pass
    
    def _validate_dropped_file(self, file_path: str) -> bool:
        """Sürüklenen dosyayı doğrula"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                self.root.after(0, lambda: self.show_error("Hata", "Dosya bulunamadı!"))
                return False
                
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                self.root.after(0, lambda: self.show_error("Hata", f"Geçersiz dosya formatı!\nDesteklenen formatlar: {', '.join(SUPPORTED_EXTENSIONS)}"))
                return False
                
            return True
            
        except Exception as e:
            self.root.after(0, lambda: self.show_error("Hata", f"Dosya kontrolü hatası: {e}"))
            return False
        
    def _create_display_input(self, parent: tk.Frame, label_text: str, text_var: tk.StringVar, icon: str) -> tk.Entry:
        """Sadece gösterim amaçlı dosya input grubu"""
        container = tk.Frame(parent, bg=self.colors['card'])
        container.pack(fill=tk.X, pady=(0, 4))
        
        # Label
        label = tk.Label(
            container,
            text=f"{icon} {label_text}",
            font=(self.font_family, 9, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        )
        label.pack(anchor=tk.W, pady=(0, 1))
        
        # İpucu metni
        hint_label = tk.Label(
            container,
            text="Otomatik oluşturulur",
            font=(self.font_family, 8, 'italic'),
            bg=self.colors['card'],
            fg=self.colors['text_light']
        )
        hint_label.pack(anchor=tk.W, pady=(0, 1))
        
        # Entry
        entry = ttk.Entry(
            container,
            textvariable=text_var,
            font=(self.font_family, 9),
            style='Modern.TEntry',
            state='readonly'
        )
        entry.pack(fill=tk.X)
        
        return entry
        
    def _create_options_card(self, parent: tk.Frame) -> None:
        """Seçenekler kartı"""
        card_frame = tk.Frame(parent, bg=self.colors['card'], relief='solid', bd=1)
        card_frame.pack(fill=tk.X, pady=2)
        
        # Kart başlığı
        header = tk.Label(
            card_frame,
            text="⚙️ Seçenekler",
            font=(self.font_family, 9, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text'],
            pady=4
        )
        header.pack(anchor=tk.W, padx=12)
        
        # Seçenekler içeriği
        content_frame = tk.Frame(card_frame, bg=self.colors['card'])
        content_frame.pack(fill=tk.X, padx=8, pady=(0, 6))
        
        # Büyük/küçük harf seçeneği
        case_check = ttk.Checkbutton(
            content_frame,
            text="Büyük/Küçük Harf Duyarlı",
            variable=self.app_logic.case_sensitive,
            style='Small.TCheckbutton'
        )
        case_check.pack(anchor=tk.W, pady=2)
        
        # Kaydetme formatı
        tk.Label(
            content_frame,
            text="💾 Kaydetme Formatı:",
            font=(self.font_family, 9, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(anchor=tk.W, pady=(6, 2))
        
        # Format seçenekleri
        format_frame = tk.Frame(content_frame, bg=self.colors['card'])
        format_frame.pack(anchor=tk.W, padx=6)
        
        # Excel checkbox
        ttk.Checkbutton(
            format_frame,
            text="Excel (.xlsx)",
            variable=self.save_excel,
            style='Small.TCheckbutton'
        ).pack(anchor=tk.W, pady=1)
        
        # Resim checkbox
        ttk.Checkbutton(
            format_frame,
            text="Resim (.png)",
            variable=self.save_image,
            style='Small.TCheckbutton'
        ).pack(anchor=tk.W, pady=1)
        
    def _create_action_buttons(self, parent: tk.Frame) -> None:
        """İşlem butonları"""
        button_frame = tk.Frame(parent, bg=self.colors['background'])
        button_frame.pack(fill=tk.X, pady=6)
        
        # Progress bar (başlangıçta gizli)
        self.progress = ttk.Progressbar(
            button_frame,
            mode='indeterminate',
            length=350
        )
        
        # Karşılaştır butonu (Ana buton)
        self.compare_btn = ttk.Button(
            button_frame,
            text="▶ Karşılaştır",
            command=self._safe_compare_files,
            style='Accent.TButton'
        )
        self.compare_btn.pack(fill=tk.X, pady=(0, 6))
        
        # Araç-Plasiyer Ayarları butonu
        settings_btn = ttk.Button(
            button_frame,
            text="🚛 Araç-Plasiyer Ayarları",
            command=self._edit_vehicle_settings,
            style='Small.TButton'
        )
        settings_btn.pack(fill=tk.X, pady=(0, 6))
        
        # Temizle butonu
        clear_btn = ttk.Button(
            button_frame,
            text="🗑 Temizle",
            command=self.app_logic.clear_results,
            style='Small.TButton'
        )
        clear_btn.pack(fill=tk.X)
    
    def _edit_vehicle_settings(self) -> None:
        """Araç-plasiyer ayarları düzenleme"""
        try:
            self.app_logic.edit_vehicle_drivers()
        except Exception as e:
            logging.error(f"Vehicle settings error: {e}")
            self.show_error("Hata", f"Ayarlar açılamadı: {e}")
        
    def _safe_compare_files(self) -> None:
        """Güvenli dosya karşılaştırma"""
        try:
            # Input validation
            file1 = self.app_logic.file1_path.get()
            file2 = self.app_logic.file2_path.get()
            
            if not file1 or not file2:
                self.show_error("Hata", "Lütfen her iki Excel dosyasını da seçin!")
                return
            
            # File validation
            for file_path, desc in [(file1, "Eski tarihli"), (file2, "Yeni tarihli")]:
                is_valid, error_msg = self._validate_file_selection(file_path, desc)
                if not is_valid:
                    self.show_error("Dosya Seçim Hatası", error_msg)
                    return
            
            # UI durumunu değiştir
            self.compare_btn.configure(text="⏳ İşleniyor...", state='disabled')
            
            # Progress bar'ı göster
            self.progress.pack(fill=tk.X, pady=5)
            self.progress.start(10)
            
            # UI güncellemesi
            self.root.update()
            
            # Karşılaştırmayı başlat
            self.app_logic.compare_files()
            
        except Exception as e:
            logging.error(f"Compare files error: {e}")
            self.show_error("Hata", f"Karşılaştırma başlatılamadı: {e}")
            self.reset_ui()
    
    def reset_ui(self) -> None:
        """UI'ı sıfırla"""
        try:
            # Progress bar'ı durdur ve gizle
            if self.progress:
                self.progress.stop()
                self.progress.pack_forget()
            
            # Buton durumunu eski haline getir
            if self.compare_btn:
                self.compare_btn.configure(text="▶ Karşılaştır", state='normal')
        except Exception as e:
            logging.error(f"UI reset error: {e}")
        
    def _create_right_panel(self, parent: tk.Frame) -> None:
        """Sağ panel (Sonuçlar)"""
        # Sonuçlar kartı
        card_frame = tk.Frame(parent, bg=self.colors['card'], relief='solid', bd=1)
        card_frame.pack(fill=tk.BOTH, expand=True, pady=2)
        
        # Kart başlığı
        header_frame = tk.Frame(card_frame, bg=self.colors['card'])
        header_frame.pack(fill=tk.X, padx=12, pady=6)
        
        tk.Label(
            header_frame,
            text="📊 Sonuçlar",
            font=(self.font_family, 9, 'bold'),
            bg=self.colors['card'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        # Sonuç tablosu frame
        table_frame = tk.Frame(card_frame, bg=self.colors['card'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        
        # Treeview ve scrollbar
        tree_frame = tk.Frame(table_frame, bg=self.colors['card'])
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        columns = ("no", "unvan")
        self.result_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=12
        )
        
        # Başlıkları ayarla
        self.result_tree.heading("no", text="#")
        self.result_tree.heading("unvan", text="Cari Ünvan")
        
        # Sütun genişlikleri
        self.result_tree.column("no", width=50, anchor=tk.CENTER)
        self.result_tree.column("unvan", width=350)
        
        self.result_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.result_tree.yview)
        
        # Durum bilgisi
        status_frame = tk.Frame(card_frame, bg=self.colors['card'])
        status_frame.pack(fill=tk.X, padx=12, pady=(0, 8))
        
        self.status_var = tk.StringVar(value="Henüz karşılaştırma yapılmadı.")
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=(self.font_family, 8, 'italic'),
            bg=self.colors['card'],
            fg=self.colors['text_light'],
            wraplength=350
        )
        status_label.pack(anchor=tk.W)
    
    def _validate_file_selection(self, file_path: str, file_type: str) -> tuple[bool, str]:
        """Dosya seçimini doğrula"""
        if not file_path:
            return False, f"Lütfen {file_type} dosyasını seçin!"
            
        path = Path(file_path)
        
        if not path.exists():
            return False, f"{file_type} dosyası bulunamadı!"
            
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return False, f"Geçersiz dosya formatı! Desteklenen formatlar: {', '.join(SUPPORTED_EXTENSIONS)}"
        
        # Dosya boyutu kontrolü
        try:
            file_size_mb = path.stat().st_size / (1024 * 1024)
            if file_size_mb > 100:  # 100MB limit
                return False, f"Dosya boyutu çok büyük ({file_size_mb:.1f}MB). Maximum 100MB destekleniyor."
        except Exception as e:
            return False, f"Dosya boyutu kontrolü hatası: {e}"
            
        return True, ""
        
    def _browse_file1(self) -> None:
        """Eski Excel dosyasını seç"""
        try:
            file_path = filedialog.askopenfilename(
                title="Eski Tarihli Excel Dosyasını Seç",
                filetypes=[
                    ("Excel Dosyaları", "*.xlsx *.xls"), 
                    ("Excel 2007-2019", "*.xlsx"),
                    ("Excel 97-2003", "*.xls"),
                    ("Tüm Dosyalar", "*.*")
                ],
                initialdir=str(Path.home())
            )
            
            if file_path:
                is_valid, error_msg = self._validate_file_selection(file_path, "Eski tarihli Excel")
                
                if is_valid:
                    self.app_logic.file1_path.set(file_path)
                    self.app_logic.update_output_filename(file_path)
                else:
                    self.show_error("Dosya Seçim Hatası", error_msg)
        except Exception as e:
            logging.error(f"File1 browse error: {e}")
            self.show_error("Hata", f"Dosya seçim hatası: {e}")
            
    def _browse_file2(self) -> None:
        """Yeni Excel dosyasını seç"""
        try:
            file_path = filedialog.askopenfilename(
                title="Yeni Tarihli Excel Dosyasını Seç",
                filetypes=[
                    ("Excel Dosyaları", "*.xlsx *.xls"), 
                    ("Excel 2007-2019", "*.xlsx"),
                    ("Excel 97-2003", "*.xls"),
                    ("Tüm Dosyalar", "*.*")
                ],
                initialdir=str(Path.home())
            )
            
            if file_path:
                is_valid, error_msg = self._validate_file_selection(file_path, "Yeni tarihli Excel")
                
                if is_valid:
                    self.app_logic.file2_path.set(file_path)
                else:
                    self.show_error("Dosya Seçim Hatası", error_msg)
        except Exception as e:
            logging.error(f"File2 browse error: {e}")
            self.show_error("Hata", f"Dosya seçim hatası: {e}")
            
    def update_results(self, results: List[str], status_text: str) -> None:
        """Sonuçları güncelle - Thread-safe"""
        def _update():
            try:
                if self.result_tree:
                    # Mevcut sonuçları temizle
                    for item in self.result_tree.get_children():
                        self.result_tree.delete(item)
                        
                    # Yeni sonuçları ekle
                    for i, unvan in enumerate(results, 1):
                        # Çok uzun ünvanları kısalt
                        display_unvan = unvan if len(str(unvan)) <= 50 else str(unvan)[:47] + "..."
                        self.result_tree.insert("", tk.END, values=(i, display_unvan))
                        
                    # Durum metnini güncelle
                    if self.status_var:
                        self.status_var.set(status_text)
                    
                    # UI'ı sıfırla
                    self.reset_ui()
                
            except Exception as e:
                logging.error(f"UI güncelleme hatası: {e}")
        
        # Ana thread'de çalıştır
        self.root.after(0, _update)
        
    def clear_results(self) -> None:
        """Sonuçları temizle"""
        try:
            if self.result_tree:
                for item in self.result_tree.get_children():
                    self.result_tree.delete(item)
            if self.status_var:
                self.status_var.set("Henüz karşılaştırma yapılmadı.")
        except Exception as e:
            logging.error(f"Sonuç temizleme hatası: {e}")
        
    def show_info(self, title: str, message: str) -> None:
        """Bilgi mesajı göster - Thread-safe"""
        def _show():
            try:
                messagebox.showinfo(title, message)
            except Exception as e:
                logging.error(f"Info dialog hatası: {e}")
        self.root.after(0, _show)
        
    def show_error(self, title: str, message: str) -> None:
        """Hata mesajı göster - Thread-safe"""
        def _show():
            try:
                messagebox.showerror(title, message)
            except Exception as e:
                logging.error(f"Error dialog hatası: {e}")
        self.root.after(0, _show)
        
    def show_warning(self, title: str, message: str) -> None:
        """Uyarı mesajı göster - Thread-safe"""
        def _show():
            try:
                messagebox.showwarning(title, message)
            except Exception as e:
                logging.error(f"Warning dialog hatası: {e}")
        self.root.after(0, _show)