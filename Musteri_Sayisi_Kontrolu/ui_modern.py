# -*- coding: utf-8 -*-
"""
Musteri_Sayisi_Kontrolu - Modern CustomTkinter UI
Excel karşılaştırma uygulaması için production-ready arayüz

Author: BUP Development Team
Version: 2.0.0 - Production Ready
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter.ttk as ttk
import tkinter as tk
import json
import sys
from pathlib import Path
from typing import Optional, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from main import ExcelComparisonLogic

# =============================================================================
# PATH SETUP
# =============================================================================

_current_dir = Path(__file__).parent
_parent_dir = _current_dir.parent

if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

# =============================================================================
# RENKLER VE SABITLER - YERLEŞIK TANIMLAR (HATA ÖNLEME)
# =============================================================================

# Tüm renkler burada tanımlı - shared modüle bağımlılık yok
COLORS = {
    'bg_light': '#F5F7FA',
    'bg_card': '#FFFFFF',
    'text_primary': '#2C3E50',
    'text_secondary': '#7F8C8D',
    'text_light': '#FFFFFF',
    'border': '#E0E6ED',
    'hover_light': '#EBF5FB',
    'success': '#2ECC71',
    'warning': '#F39C12',
    'error': '#E74C3C',
    'info': '#3498DB',
    'gray_600': '#4B5563',  # Örnek veri butonu için
}

# Modül accent renkleri
ACCENT = '#2A9D8F'  # Teal
ACCENT_HOVER = '#238B7E'
ACCENT_LIGHT = '#E0F2F1'

# Desteklenen dosya uzantıları
SUPPORTED_EXTENSIONS = ['.xlsx', '.xls']

# Logger setup
try:
    from shared.utils import setup_logging
    logger = setup_logging("MUSTERI_UI")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("MUSTERI_UI")


# =============================================================================
# ARAÇ-PLASİYER DIALOG
# =============================================================================

class VehicleDriverDialog(ctk.CTkToplevel):
    """
    Araç-Plasiyer Eşleştirme Dialog'u
    
    Özellikler:
    - 20 araç için plasiyer girişi
    - Örnek veri yükleme
    - JSON config kaydetme
    - Modal pencere (grab_set)
    """
    
    def __init__(self, parent, existing_data: Optional[Dict[str, str]] = None):
        super().__init__(parent)
        
        # Veri
        self.existing_data = existing_data or {}
        self.result: Optional[Dict[str, str]] = None
        self.entries: Dict[str, ctk.CTkEntry] = {}
        self._is_closing = False
        
        # Pencere ayarları
        self.title("Araç-Plasiyer Eşleştirmesi")
        self.geometry("550x650")
        self.resizable(False, False)
        
        # Transient ayarı (parent penceresine bağlı)
        try:
            self.transient(parent)
        except tk.TclError:
            pass
        
        # Ortala
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - 550) // 2
        y = (screen_h - 650) // 2
        self.geometry(f"550x650+{x}+{y}")
        
        # UI oluştur
        self._build_ui()
        
        # Kapanma protokolü
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Modal yap (gecikmeli)
        self.after(200, self._make_modal)
    
    def _make_modal(self):
        """Pencereyi modal yap"""
        if self._is_closing:
            return
        try:
            if self.winfo_exists() and self.winfo_viewable():
                self.grab_set()
                self.focus_force()
        except tk.TclError:
            # Pencere henüz hazır değil, tekrar dene
            self.after(100, self._make_modal)
    
    def _build_ui(self):
        """UI bileşenlerini oluştur"""
        # Ana container
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Başlık
        ctk.CTkLabel(
            main,
            text="🚛 Araç-Plasiyer Eşleştirmesi",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(pady=(0, 5))
        
        # Alt başlık
        ctk.CTkLabel(
            main,
            text="Her araç numarası için plasiyer adını girin",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=COLORS['text_secondary']
        ).pack(pady=(0, 15))
        
        # Scrollable alan
        scroll = ctk.CTkScrollableFrame(
            main,
            fg_color=COLORS['bg_card'],
            corner_radius=8,
            height=400
        )
        scroll.pack(fill="both", expand=True, pady=(0, 15))
        
        # Araç girişleri (01-20)
        for i in range(1, 21):
            num = f"{i:02d}"
            self._create_entry_row(scroll, num)
        
        # Butonlar
        self._create_buttons(main)
    
    def _create_entry_row(self, parent, vehicle_num: str):
        """Tek bir araç satırı oluştur"""
        row = ctk.CTkFrame(parent, fg_color="transparent", height=40)
        row.pack(fill="x", padx=10, pady=3)
        row.pack_propagate(False)
        
        # Label
        ctk.CTkLabel(
            row,
            text=f"Araç {vehicle_num}:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS['text_primary'],
            width=90
        ).pack(side="left", padx=(0, 10))
        
        # Entry
        entry = ctk.CTkEntry(
            row,
            placeholder_text="Plasiyer adı...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=32,
            corner_radius=6
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Mevcut veri varsa doldur
        if vehicle_num in self.existing_data:
            entry.insert(0, self.existing_data[vehicle_num])
        
        self.entries[vehicle_num] = entry
    
    def _create_buttons(self, parent):
        """Alt butonları oluştur"""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent", height=45)
        btn_frame.pack(fill="x")
        btn_frame.pack_propagate(False)
        
        # Örnek Veri butonu
        ctk.CTkButton(
            btn_frame,
            text="📋 Örnek Veri",
            width=120,
            height=38,
            corner_radius=8,
            fg_color=COLORS['gray_600'],
            hover_color="#374151",
            command=self._load_sample
        ).pack(side="left")
        
        # İptal butonu
        ctk.CTkButton(
            btn_frame,
            text="İptal",
            width=90,
            height=38,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS['border'],
            text_color=COLORS['text_primary'],
            hover_color=COLORS['hover_light'],
            command=self._on_close
        ).pack(side="right", padx=(10, 0))
        
        # Kaydet butonu
        ctk.CTkButton(
            btn_frame,
            text="✓ Kaydet",
            width=100,
            height=38,
            corner_radius=8,
            fg_color=COLORS['success'],
            hover_color="#27AE60",
            command=self._save
        ).pack(side="right")
    
    def _load_sample(self):
        """Örnek verileri yükle"""
        samples = {
            "01": "Ahmet ALTILI",
            "02": "Erhan AYDOĞDU",
            "04": "Soner TANAY",
            "05": "Süleyman TANAY",
            "06": "Hakan YILMAZ"
        }
        for num, name in samples.items():
            if num in self.entries:
                self.entries[num].delete(0, "end")
                self.entries[num].insert(0, name)
    
    def _save(self):
        """Verileri kaydet"""
        # Verileri topla
        data = {}
        for num, entry in self.entries.items():
            val = entry.get().strip()
            if val:
                data[num] = val
        
        if not data:
            messagebox.showwarning(
                "Uyarı",
                "En az bir araç-plasiyer eşleştirmesi yapmalısınız!",
                parent=self
            )
            return
        
        # JSON'a kaydet
        try:
            config_path = Path.cwd() / 'config.json'
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump({"vehicle_drivers": data}, f, indent=4, ensure_ascii=False)
            
            self.result = data
            messagebox.showinfo(
                "Başarılı",
                f"{len(data)} araç-plasiyer eşleştirmesi kaydedildi!",
                parent=self
            )
            self._close_window()
            
        except Exception as e:
            logger.error(f"Config kaydetme hatası: {e}")
            messagebox.showerror("Hata", f"Kaydetme hatası: {e}", parent=self)
    
    def _on_close(self):
        """Pencere kapatıldığında"""
        self.result = None
        self._close_window()
    
    def _close_window(self):
        """Pencereyi güvenli şekilde kapat"""
        if self._is_closing:
            return
        self._is_closing = True
        
        try:
            self.grab_release()
        except tk.TclError:
            pass
        
        self.destroy()
    
    def get_result(self) -> Optional[Dict[str, str]]:
        """Dialog sonucunu döndür (blocking)"""
        self.wait_window()
        return self.result


# =============================================================================
# ANA UYGULAMA
# =============================================================================

class MusteriTakipApp(ctk.CTkFrame):
    """
    Müşteri Takip Ana Uygulaması
    
    Özellikler:
    - İki Excel dosyası karşılaştırma
    - Sonuçları Excel/PNG olarak kaydetme
    - Araç-plasiyer eşleştirme
    - Modern CustomTkinter arayüz
    """
    
    def __init__(self, master, app_logic: 'ExcelComparisonLogic', standalone: bool = False):
        super().__init__(master, fg_color=COLORS['bg_light'])
        
        self.master = master
        self.app_logic = app_logic
        self.standalone = standalone
        
        # Kaydetme seçenekleri - Tkinter BooleanVar (güvenilir)
        self.save_excel = tk.BooleanVar(value=True)
        self.save_image = tk.BooleanVar(value=False)
        
        # Widget referansları
        self.result_tree: Optional[ttk.Treeview] = None
        self.status_var: Optional[tk.StringVar] = None
        self.compare_btn: Optional[ctk.CTkButton] = None
        self.progress_bar: Optional[ctk.CTkProgressBar] = None
        self.progress_label: Optional[ctk.CTkLabel] = None
        self.result_count_label: Optional[ctk.CTkLabel] = None
        
        # UI oluştur
        self._build_ui()
        
        # Logic'e UI referansı ver
        self.app_logic.ui = self
        
        logger.info("Müşteri Takip UI başlatıldı")
    
    # =========================================================================
    # UI OLUŞTURMA
    # =========================================================================
    
    def _build_ui(self):
        """Ana UI yapısını oluştur"""
        # Grid yapılandırma
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # İçerik alanı genişlesin
        
        # 1. Header
        self._build_header()
        
        # 2. İçerik (sol + sağ panel)
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 10))
        content.grid_columnconfigure(0, weight=0, minsize=350)  # Sol panel
        content.grid_columnconfigure(1, weight=1)  # Sağ panel
        content.grid_rowconfigure(0, weight=1)
        
        self._build_left_panel(content)
        self._build_right_panel(content)
        
        # 3. Alt panel (progress bar)
        self._build_bottom_panel()
    
    def _build_header(self):
        """Header bölümü"""
        header = ctk.CTkFrame(self, fg_color=ACCENT, height=80, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        
        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=30)
        
        ctk.CTkLabel(
            inner,
            text="👥 Müşteri Takip",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=COLORS['text_light']
        ).pack(pady=(15, 2))
        
        ctk.CTkLabel(
            inner,
            text="Excel dosyalarını karşılaştırarak müşteri kayıp/kazanç analizi yapın",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=ACCENT_LIGHT
        ).pack()
    
    def _build_left_panel(self, parent):
        """Sol panel - dosya seçimi, seçenekler, butonlar"""
        left = ctk.CTkFrame(parent, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        # Dosya Seçimi Kartı
        self._build_file_card(left)
        
        # Seçenekler Kartı
        self._build_options_card(left)
        
        # Aksiyon Butonları
        self._build_action_buttons(left)
    
    def _build_file_card(self, parent):
        """Dosya seçimi kartı"""
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        card.pack(fill="x", pady=(0, 10))
        
        # Başlık
        ctk.CTkLabel(
            card,
            text="📁 Dosya Seçimi",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", padx=15, pady=(12, 8))
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=(0, 12))
        
        # Dosya inputları
        self._build_file_row(content, "📄 Eski Tarihli Excel", 
                            self.app_logic.file1_path, self._browse_old)
        self._build_file_row(content, "📄 Yeni Tarihli Excel",
                            self.app_logic.file2_path, self._browse_new)
        self._build_output_row(content, "💾 Sonuç Dosyası",
                              self.app_logic.output_path)
    
    def _build_file_row(self, parent, label: str, var, command):
        """Dosya seçim satırı"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            container,
            text=label,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 3))
        
        row = ctk.CTkFrame(container, fg_color="transparent")
        row.pack(fill="x")
        
        ctk.CTkEntry(
            row,
            textvariable=var,
            placeholder_text="Dosya seçin...",
            height=36,
            corner_radius=6,
            border_width=1,
            border_color=COLORS['border']
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))
        
        ctk.CTkButton(
            row,
            text="Gözat",
            width=70,
            height=36,
            corner_radius=6,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            command=command
        ).pack(side="right")
    
    def _build_output_row(self, parent, label: str, var):
        """Çıktı dosyası gösterimi"""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            container,
            text=label,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 2))
        
        ctk.CTkLabel(
            container,
            text="Otomatik oluşturulur",
            font=ctk.CTkFont(family="Segoe UI", size=9),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0, 3))
        
        ctk.CTkEntry(
            container,
            textvariable=var,
            height=36,
            corner_radius=6,
            border_width=1,
            border_color=COLORS['border'],
            state="disabled"
        ).pack(fill="x")
    
    def _build_options_card(self, parent):
        """Seçenekler kartı"""
        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        card.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            card,
            text="⚙️ Seçenekler",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", padx=15, pady=(12, 8))
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=15, pady=(0, 12))
        
        # Büyük/küçük harf duyarlı
        ctk.CTkCheckBox(
            content,
            text="Büyük/Küçük Harf Duyarlı",
            variable=self.app_logic.case_sensitive,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=4,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER
        ).pack(anchor="w", pady=(0, 8))
        
        # Kaydetme formatı başlık
        ctk.CTkLabel(
            content,
            text="💾 Kaydetme Formatı:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(anchor="w", pady=(5, 5))
        
        # Excel checkbox
        ctk.CTkCheckBox(
            content,
            text="Excel (.xlsx)",
            variable=self.save_excel,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=4,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER
        ).pack(anchor="w", padx=(15, 0), pady=2)
        
        # Resim checkbox
        ctk.CTkCheckBox(
            content,
            text="Resim (.png)",
            variable=self.save_image,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=4,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER
        ).pack(anchor="w", padx=(15, 0), pady=2)
    
    def _build_action_buttons(self, parent):
        """Aksiyon butonları"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(5, 0))
        
        # Ana buton - Karşılaştır
        self.compare_btn = ctk.CTkButton(
            frame,
            text="▶ Karşılaştır",
            height=45,
            corner_radius=8,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            command=self._on_compare
        )
        self.compare_btn.pack(fill="x", pady=(0, 8))
        
        # Araç-Plasiyer Ayarları
        ctk.CTkButton(
            frame,
            text="🚛 Araç-Plasiyer Ayarları",
            height=38,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=ACCENT,
            text_color=ACCENT,
            hover_color=COLORS['hover_light'],
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=self._on_settings
        ).pack(fill="x", pady=(0, 8))
        
        # Temizle
        ctk.CTkButton(
            frame,
            text="🗑 Temizle",
            height=38,
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=COLORS['border'],
            text_color=COLORS['text_secondary'],
            hover_color=COLORS['hover_light'],
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=self._on_clear
        ).pack(fill="x")
    
    def _build_right_panel(self, parent):
        """Sağ panel - sonuçlar tablosu"""
        right = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'], corner_radius=10)
        right.grid(row=0, column=1, sticky="nsew")
        
        # Başlık satırı
        header = ctk.CTkFrame(right, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(12, 8))
        
        ctk.CTkLabel(
            header,
            text="📊 Karşılaştırma Sonuçları",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        self.result_count_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['text_secondary']
        )
        self.result_count_label.pack(side="right")
        
        # Tablo alanı
        table_frame = ctk.CTkFrame(right, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        # Treeview stili
        style = ttk.Style()
        style.configure(
            "Musteri.Treeview",
            background=COLORS['bg_card'],
            foreground=COLORS['text_primary'],
            fieldbackground=COLORS['bg_card'],
            rowheight=28
        )
        style.configure(
            "Musteri.Treeview.Heading",
            font=('Segoe UI', 10, 'bold')
        )
        
        # Treeview
        columns = ("no", "unvan")
        self.result_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Musteri.Treeview"
        )
        self.result_tree.heading("no", text="#")
        self.result_tree.heading("unvan", text="Cari Ünvan (Eski dosyada var, yeni dosyada yok)")
        self.result_tree.column("no", width=50, anchor="center", stretch=False)
        self.result_tree.column("unvan", width=400, anchor="w")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        
        self.result_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Durum satırı
        status_frame = ctk.CTkFrame(right, fg_color="transparent")
        status_frame.pack(fill="x", padx=15, pady=(0, 12))
        
        self.status_var = tk.StringVar(value="Henüz karşılaştırma yapılmadı.")
        ctk.CTkLabel(
            status_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w")
    
    def _build_bottom_panel(self):
        """Alt panel - progress bar"""
        bottom = ctk.CTkFrame(self, fg_color="transparent", height=50)
        bottom.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 15))
        bottom.grid_propagate(False)
        
        self.progress_label = ctk.CTkLabel(
            bottom,
            text="Hazır",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=COLORS['text_secondary']
        )
        self.progress_label.pack(anchor="w", pady=(5, 3))
        
        self.progress_bar = ctk.CTkProgressBar(
            bottom,
            height=8,
            corner_radius=4,
            fg_color=COLORS['border'],
            progress_color=ACCENT
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
    
    # =========================================================================
    # BUTON KOMUTLARI
    # =========================================================================
    
    def _browse_old(self):
        """Eski dosya seç"""
        path = filedialog.askopenfilename(
            title="Eski Tarihli Excel Dosyasını Seç",
            filetypes=[("Excel Dosyaları", "*.xlsx *.xls"), ("Tüm Dosyalar", "*.*")]
        )
        if path:
            valid, msg = self._validate_file(path)
            if valid:
                self.app_logic.file1_path.set(path)
                self.app_logic.update_output_filename(path)
                self._set_status(f"Eski dosya: {Path(path).name}")
            else:
                messagebox.showerror("Dosya Hatası", msg)
    
    def _browse_new(self):
        """Yeni dosya seç"""
        path = filedialog.askopenfilename(
            title="Yeni Tarihli Excel Dosyasını Seç",
            filetypes=[("Excel Dosyaları", "*.xlsx *.xls"), ("Tüm Dosyalar", "*.*")]
        )
        if path:
            valid, msg = self._validate_file(path)
            if valid:
                self.app_logic.file2_path.set(path)
                self._set_status(f"Yeni dosya: {Path(path).name}")
            else:
                messagebox.showerror("Dosya Hatası", msg)
    
    def _validate_file(self, path: str) -> tuple:
        """Dosya doğrulama"""
        p = Path(path)
        
        if not p.exists():
            return False, "Dosya bulunamadı!"
        
        if p.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return False, f"Geçersiz format!\nDesteklenen: {', '.join(SUPPORTED_EXTENSIONS)}"
        
        try:
            size_mb = p.stat().st_size / (1024 * 1024)
            if size_mb > 100:
                return False, f"Dosya çok büyük ({size_mb:.1f}MB). Max: 100MB"
        except:
            pass
        
        return True, ""
    
    def _on_compare(self):
        """Karşılaştır butonu"""
        # Dosya kontrolleri
        file1 = self.app_logic.file1_path.get()
        file2 = self.app_logic.file2_path.get()
        
        if not file1:
            messagebox.showerror("Hata", "Lütfen eski tarihli Excel dosyasını seçin!")
            return
        
        if not file2:
            messagebox.showerror("Hata", "Lütfen yeni tarihli Excel dosyasını seçin!")
            return
        
        # Dosya doğrulama
        for fp, desc in [(file1, "Eski"), (file2, "Yeni")]:
            valid, msg = self._validate_file(fp)
            if not valid:
                messagebox.showerror("Dosya Hatası", f"{desc} dosya: {msg}")
                return
        
        # Format kontrolü
        if not self.save_excel.get() and not self.save_image.get():
            messagebox.showwarning("Uyarı", "Lütfen en az bir kaydetme formatı seçin!")
            return
        
        # UI güncelle
        self.compare_btn.configure(state="disabled", text="⏳ İşleniyor...")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Dosyalar karşılaştırılıyor...")
        
        # İşlemi başlat
        self.app_logic.compare_files()
    
    def _on_settings(self):
        """Araç-Plasiyer ayarları"""
        try:
            dialog = VehicleDriverDialog(self.master, self.app_logic.vehicle_drivers)
            result = dialog.get_result()
            
            if result:
                self.app_logic.vehicle_drivers = result
                self._set_status(f"Araç-plasiyer eşleştirmesi güncellendi ({len(result)} kayıt)")
        except Exception as e:
            logger.error(f"Settings dialog error: {e}")
            messagebox.showerror("Hata", f"Ayarlar açılamadı: {e}")
    
    def _on_clear(self):
        """Temizle butonu"""
        # Dosya yollarını temizle
        self.app_logic.file1_path.set("")
        self.app_logic.file2_path.set("")
        self.app_logic.output_path.set("")
        
        # Tabloyu temizle
        if self.result_tree:
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)
        
        # Durumu sıfırla
        self.status_var.set("Henüz karşılaştırma yapılmadı.")
        self.result_count_label.configure(text="")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Hazır")
    
    def _set_status(self, msg: str):
        """Durum mesajını güncelle"""
        if self.status_var:
            self.status_var.set(msg)
    
    # =========================================================================
    # LOGIC TARAFINDAN ÇAĞRILAN METODLAR
    # =========================================================================
    
    def clear_results(self):
        """Sonuçları temizle (Logic çağırır)"""
        def _do():
            try:
                if self.result_tree:
                    for item in self.result_tree.get_children():
                        self.result_tree.delete(item)
                if self.result_count_label:
                    self.result_count_label.configure(text="")
                if self.status_var:
                    self.status_var.set("İşlem devam ediyor...")
            except Exception as e:
                logger.error(f"clear_results error: {e}")
        
        self.after(0, _do)
    
    def update_results(self, results: List[str], status_text: str):
        """Sonuçları güncelle (Logic çağırır)"""
        def _do():
            try:
                # Temizle
                if self.result_tree:
                    for item in self.result_tree.get_children():
                        self.result_tree.delete(item)
                    
                    # Ekle
                    for i, unvan in enumerate(results, 1):
                        display = str(unvan)[:67] + "..." if len(str(unvan)) > 70 else str(unvan)
                        self.result_tree.insert("", "end", values=(i, display))
                
                # Güncelle
                if self.result_count_label:
                    self.result_count_label.configure(text=f"{len(results)} kayıt bulundu")
                if self.status_var:
                    self.status_var.set(status_text)
                
                # UI sıfırla
                self.reset_ui()
                
            except Exception as e:
                logger.error(f"update_results error: {e}")
        
        self.after(0, _do)
    
    def reset_ui(self):
        """UI'ı normal duruma getir (Logic çağırır)"""
        try:
            if self.progress_bar:
                self.progress_bar.set(1)
            if self.progress_label:
                self.progress_label.configure(text="Tamamlandı")
            if self.compare_btn:
                self.compare_btn.configure(state="normal", text="▶ Karşılaştır")
        except Exception as e:
            logger.error(f"reset_ui error: {e}")
    
    def show_error(self, title: str, message: str):
        """Hata mesajı göster (Logic çağırır)"""
        def _show():
            messagebox.showerror(title, message)
            self.reset_ui()
        self.after(0, _show)
    
    def show_warning(self, title: str, message: str):
        """Uyarı mesajı göster (Logic çağırır)"""
        self.after(0, lambda: messagebox.showwarning(title, message))
    
    def show_info(self, title: str, message: str):
        """Bilgi mesajı göster (Logic çağırır)"""
        self.after(0, lambda: messagebox.showinfo(title, message))
    
    @property
    def root(self):
        """Eski UI uyumluluğu için"""
        return self.master


# =============================================================================
# STANDALONE ÇALIŞTIRMA
# =============================================================================

def main():
    """Standalone çalıştırma (test için)"""
    from main import ExcelComparisonLogic
    
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("Bupiliç Müşteri Takip")
    root.geometry("1200x800")
    root.minsize(1000, 700)
    
    app_logic = ExcelComparisonLogic()
    app = MusteriTakipApp(root, app_logic, standalone=True)
    app.pack(fill="both", expand=True)
    
    root.mainloop()


if __name__ == "__main__":
    main()
