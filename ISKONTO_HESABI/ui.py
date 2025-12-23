# -*- coding: utf-8 -*-
"""
ISKONTO_HESABI - Modern CustomTkinter UI
Çoklu PDF desteği ile iskonto hesaplama arayüzü
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

from tkinter import filedialog
import threading
from datetime import datetime
import pdfplumber
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Shared modül import
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.theme import COLORS, MODULE_COLORS, FONTS, SIZES, BupTheme
from shared.utils import setup_logging, get_clean_filename
from shared.components import (
    ModernHeader, ModernCard, ModernButton, StatCard,
    ProgressIndicator, ModernTabView, ScrollableFrame,
    show_success, show_error, show_warning, ask_yes_no
)

from .pdf_processor import PDFProcessor
from .export_manager import ExportManager

logger = setup_logging("ISKONTO_UI")

# Modül renkleri
MODULE_NAME = "ISKONTO_HESABI"
ACCENT = MODULE_COLORS[MODULE_NAME]['accent']
ACCENT_HOVER = MODULE_COLORS[MODULE_NAME]['accent_hover']


class IskontoHesabiApp(ctk.CTkFrame):
    """İskonto Hesabı Ana Uygulama"""
    
    def __init__(self, master, standalone: bool = False):
        super().__init__(master, fg_color=COLORS['bg_light'])
        
        self.standalone = standalone
        self.master = master
        
        # Veri yapıları
        self.pdf_processors: List[PDFProcessor] = []
        self.pdf_files: List[Dict] = []
        self.current_data_all: Dict = {}
        self.max_pdf_count = 3
        self.pdf_loaded = False
        
        # Export manager
        self.export_manager = ExportManager()
        
        # İskonto değişkenleri
        self.discount_vars: Dict[str, ctk.DoubleVar] = {}
        
        # Kategori listesi
        self.categories = [
            ('Bütün Piliç Ürünleri', '🐔'),
            ('Kanat Ürünleri', '🍗'),
            ('But Ürünleri', '🍖'),
            ('Göğüs Ürünleri', '🥩'),
            ('Sakatat Ürünleri', '🫀'),
            ('Yan Ürünler', '📦')
        ]
        
        # UI oluştur
        self._setup_ui()
        
        logger.info("İskonto Hesabı UI başlatıldı")
    
    def _setup_ui(self):
        """Ana UI yapısını oluştur"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header = ModernHeader(
            self,
            title="🚀 İskonto Hesaplayıcı",
            subtitle="PDF fiyat listelerinizi kolayca işleyin (Maks. 3 PDF)",
            module_name=MODULE_NAME
        )
        header.grid(row=0, column=0, sticky="ew")
        
        # Tab view
        self.tabview = ModernTabView(self, module_name=MODULE_NAME)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        # Tabları oluştur
        self.tabview.add("📄 PDF Yükle")
        self.tabview.add("💰 İskonto Ayarla")
        self.tabview.add("📊 Önizleme")
        self.tabview.add("📈 İstatistikler")
        
        # Tab içeriklerini oluştur
        self._create_pdf_tab()
        self._create_discount_tab()
        self._create_preview_tab()
        self._create_stats_tab()
        
        # Alt kontrol paneli
        self._create_control_panel()
    
    def _create_pdf_tab(self):
        """PDF yükleme tabı"""
        tab = self.tabview.tab("📄 PDF Yükle")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Başlık
        title = ctk.CTkLabel(
            tab,
            text="PDF Dosyalarını Seçin",
            font=ctk.CTkFont(family=FONTS['heading'][0], size=FONTS['heading'][1], weight='bold'),
            text_color=COLORS['text_primary']
        )
        title.grid(row=0, column=0, pady=(20, 10))
        
        # PDF listesi frame
        list_frame = ctk.CTkFrame(tab, fg_color=COLORS['bg_card'], corner_radius=SIZES['corner_radius'])
        list_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=10)
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # PDF listesi container
        self.pdf_list_frame = ctk.CTkScrollableFrame(
            list_frame,
            fg_color="transparent",
            height=200
        )
        self.pdf_list_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.pdf_list_frame.grid_columnconfigure(0, weight=1)
        
        # Boş liste mesajı
        self.empty_label = ctk.CTkLabel(
            self.pdf_list_frame,
            text="Henüz PDF yüklenmedi\n\nAşağıdaki butona tıklayarak PDF dosyalarını seçin",
            font=ctk.CTkFont(family=FONTS['body'][0], size=FONTS['body'][1]),
            text_color=COLORS['text_secondary']
        )
        self.empty_label.grid(row=0, column=0, pady=40)
        
        # Butonlar frame
        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=20)
        
        # PDF Seç butonu
        self.select_btn = ModernButton(
            btn_frame,
            text="PDF Seç (Maks. 3)",
            icon="📁",
            command=self._select_pdfs,
            module_name=MODULE_NAME,
            size='large',
            width=200
        )
        self.select_btn.pack(side="left", padx=10)
        
        # Temizle butonu
        self.clear_btn = ModernButton(
            btn_frame,
            text="Temizle",
            icon="🗑️",
            command=self._clear_pdfs,
            button_type='danger',
            size='large',
            width=150
        )
        self.clear_btn.pack(side="left", padx=10)
        self.clear_btn.configure(state="disabled")
        
        # Desteklenen formatlar bilgisi
        info_frame = ctk.CTkFrame(tab, fg_color=COLORS['hover_light'], corner_radius=SIZES['corner_radius'])
        info_frame.grid(row=3, column=0, pady=(0, 20), padx=40, sticky="ew")
        
        info_text = "✓ Normal Fiyat Listesi   ✓ Gramajlı/Soslu Ürünler   ✓ Dondurulmuş Ürünler"
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(family=FONTS['small'][0], size=FONTS['small'][1]),
            text_color=COLORS['success']
        )
        info_label.pack(pady=10)
    
    def _create_discount_tab(self):
        """İskonto ayarları tabı"""
        tab = self.tabview.tab("💰 İskonto Ayarla")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(
            tab, 
            fg_color="transparent",
            scrollbar_button_color=COLORS['border'],
            scrollbar_button_hover_color=ACCENT
        )
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Başlık
        title = ctk.CTkLabel(
            scroll_frame,
            text="İskonto Oranlarını Ayarlayın",
            font=ctk.CTkFont(family=FONTS['heading'][0], size=FONTS['heading'][1], weight='bold'),
            text_color=COLORS['text_primary']
        )
        title.grid(row=0, column=0, pady=(10, 5))
        
        # Not
        note = ctk.CTkLabel(
            scroll_frame,
            text="Not: Belirlenen iskonto oranları tüm yüklenen PDF dosyalarına uygulanacaktır.",
            font=ctk.CTkFont(family=FONTS['small'][0], size=FONTS['small'][1]),
            text_color=COLORS['warning']
        )
        note.grid(row=1, column=0, pady=(0, 10))
        
        # Hızlı ayar butonları
        quick_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        quick_frame.grid(row=2, column=0, pady=10)
        
        ctk.CTkLabel(
            quick_frame,
            text="Hızlı Ayar:",
            font=ctk.CTkFont(family=FONTS['body'][0], size=FONTS['body'][1]),
            text_color=COLORS['text_primary']
        ).pack(side="left", padx=(0, 15))
        
        for value in [5, 10, 15, 20]:
            btn = ctk.CTkButton(
                quick_frame,
                text=f"Tümü %{value}",
                width=85,
                height=32,
                fg_color=COLORS['bg_card'],
                hover_color=COLORS['hover_light'],
                text_color=COLORS['text_primary'],
                border_width=1,
                border_color=COLORS['border'],
                font=ctk.CTkFont(family=FONTS['small'][0], size=FONTS['small'][1], weight='bold'),
                command=lambda v=value: self._set_all_discounts(v)
            )
            btn.pack(side="left", padx=3)
        
        # Sıfırla butonu - beyaz yazı için daha koyu kırmızı
        reset_btn = ctk.CTkButton(
            quick_frame,
            text="Sıfırla",
            width=80,
            height=32,
            fg_color="#C0392B",  # Daha koyu kırmızı
            hover_color="#A93226",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family=FONTS['small'][0], size=FONTS['small'][1], weight='bold'),
            command=lambda: self._set_all_discounts(0)
        )
        reset_btn.pack(side="left", padx=(15, 0))
        
        # Kategori kartları
        categories_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        categories_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        categories_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.category_cards = {}
        
        for i, (category, icon) in enumerate(self.categories):
            row = i // 2
            col = i % 2
            
            card = ctk.CTkFrame(
                categories_frame,
                fg_color=COLORS['bg_card'],
                corner_radius=SIZES['corner_radius'],
                border_width=1,
                border_color=COLORS['border']
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="ew")
            
            # Header
            header = ctk.CTkFrame(card, fg_color="transparent")
            header.pack(fill="x", padx=12, pady=(12, 8))
            
            ctk.CTkLabel(
                header,
                text=f"{icon} {category}",
                font=ctk.CTkFont(family=FONTS['body_bold'][0], size=FONTS['body_bold'][1], weight='bold'),
                text_color=COLORS['text_primary']
            ).pack(side="left")
            
            # Ürün sayısı etiketi
            count_label = ctk.CTkLabel(
                header,
                text="(0 ürün)",
                font=ctk.CTkFont(family=FONTS['small'][0], size=FONTS['small'][1]),
                text_color=COLORS['text_secondary']
            )
            count_label.pack(side="left", padx=(10, 0))
            
            # İskonto girişi
            input_frame = ctk.CTkFrame(card, fg_color="transparent")
            input_frame.pack(fill="x", padx=12, pady=(0, 12))
            
            ctk.CTkLabel(
                input_frame,
                text="İskonto %:",
                font=ctk.CTkFont(family=FONTS['small'][0], size=FONTS['small'][1]),
                text_color=COLORS['text_secondary']
            ).pack(side="left")
            
            var = ctk.DoubleVar(value=0.0)
            entry = ctk.CTkEntry(
                input_frame,
                textvariable=var,
                width=80,
                height=32,
                corner_radius=SIZES['corner_radius_small'],
                border_width=1,
                border_color=COLORS['border']
            )
            entry.pack(side="right")
            
            self.discount_vars[category] = var
            self.category_cards[category] = {
                'card': card,
                'count_label': count_label,
                'entry': entry
            }
        
        # Hesapla butonu - alt kısımda
        calc_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        calc_frame.grid(row=4, column=0, pady=(10, 20))
        
        calc_btn = ctk.CTkButton(
            calc_frame,
            text="🔄 Önizleme Oluştur",
            width=200,
            height=40,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#FFFFFF",
            font=ctk.CTkFont(family=FONTS['body'][0], size=14, weight='bold'),
            command=self._preview_data
        )
        calc_btn.pack()
    
    def _create_preview_tab(self):
        """Önizleme tabı"""
        tab = self.tabview.tab("📊 Önizleme")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(tab, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="Fiyat Listesi Önizleme",
            font=ctk.CTkFont(family=FONTS['heading'][0], size=FONTS['heading'][1], weight='bold'),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        ModernButton(
            header_frame,
            text="Yenile",
            icon="🔄",
            command=self._preview_data,
            module_name=MODULE_NAME,
            size='small',
            width=100
        ).pack(side="right")
        
        # Önizleme alanı
        self.preview_text = ctk.CTkTextbox(
            tab,
            font=ctk.CTkFont(family="Consolas", size=10),
            fg_color=COLORS['bg_card'],
            text_color=COLORS['text_primary'],
            corner_radius=SIZES['corner_radius'],
            border_width=1,
            border_color=COLORS['border']
        )
        self.preview_text.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        
        # Hoşgeldin mesajı
        self._show_welcome_message()
    
    def _create_stats_tab(self):
        """İstatistikler tabı"""
        tab = self.tabview.tab("📈 İstatistikler")
        tab.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Başlık
        title = ctk.CTkLabel(
            tab,
            text="İstatistikler ve Özet",
            font=ctk.CTkFont(family=FONTS['heading'][0], size=FONTS['heading'][1], weight='bold'),
            text_color=COLORS['text_primary']
        )
        title.grid(row=0, column=0, columnspan=3, pady=(20, 30))
        
        # Stat kartları
        stats_info = [
            ('pdf_count', 'Yüklenen PDF', '📄', '0'),
            ('product_count', 'Toplam Ürün', '📦', '0'),
            ('category_count', 'Kategori', '📊', '0'),
            ('avg_discount', 'Ort. İskonto', '💰', '%0'),
            ('total_discount', 'Toplam İskonto', '💵', '0 ₺'),
            ('total_records', 'Toplam Kayıt', '💾', '0')
        ]
        
        self.stat_cards = {}
        
        for i, (key, title_text, icon, value) in enumerate(stats_info):
            row = i // 3 + 1
            col = i % 3
            
            card = StatCard(
                tab,
                title=title_text,
                value=value,
                icon=icon,
                accent_color=ACCENT
            )
            card.grid(row=row, column=col, padx=15, pady=15, sticky="ew")
            self.stat_cards[key] = card
    
    def _create_control_panel(self):
        """Alt kontrol paneli"""
        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        control_frame.grid_columnconfigure(0, weight=1)
        
        # Progress indicator
        self.progress = ProgressIndicator(control_frame, module_name=MODULE_NAME)
        self.progress.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Butonlar
        btn_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="e")
        
        # Excel butonu - koyu yeşil, beyaz yazı
        self.excel_btn = ctk.CTkButton(
            btn_frame,
            text="📊 Excel'e Aktar",
            width=150,
            height=40,
            corner_radius=8,
            fg_color="#27AE60",  # Koyu yeşil
            hover_color="#219A52",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight='bold'),
            command=lambda: self._export_data('excel')
        )
        self.excel_btn.pack(side="left", padx=5)
        self.excel_btn.configure(state="disabled")
        
        # PDF butonu - koyu kırmızı, beyaz yazı
        self.pdf_btn = ctk.CTkButton(
            btn_frame,
            text="📄 PDF'e Aktar",
            width=150,
            height=40,
            corner_radius=8,
            fg_color="#C0392B",  # Koyu kırmızı
            hover_color="#A93226",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight='bold'),
            command=lambda: self._export_data('pdf')
        )
        self.pdf_btn.pack(side="left", padx=5)
        self.pdf_btn.configure(state="disabled")
        
        # Her ikisi butonu - modül accent rengi
        self.both_btn = ctk.CTkButton(
            btn_frame,
            text="📊📄 Her İkisi",
            width=150,
            height=40,
            corner_radius=8,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight='bold'),
            command=lambda: self._export_data('both')
        )
        self.both_btn.pack(side="left", padx=5)
        self.both_btn.configure(state="disabled")
    
    def _show_welcome_message(self):
        """Hoşgeldin mesajı"""
        self.preview_text.delete("1.0", "end")
        welcome = """
╔════════════════════════════════════════════════════════════════╗
║           BUPİLİÇ İSKONTOLU FİYAT HESAPLAYICI                 ║
╚════════════════════════════════════════════════════════════════╝

KULLANIM ADIMLARI:
─────────────────
1. PDF sekmesinden fiyat listesi PDF'lerini seçin (Maks. 3 adet)
2. İskonto sekmesinden oranları ayarlayın
3. Önizleme sekmesinden sonuçları kontrol edin
4. Excel veya PDF olarak dışa aktarın

ÖZELLİKLER:
──────────
✓ Çoklu PDF desteği (1-3 adet)
✓ Her PDF için ayrı önizleme
✓ Excel'de her PDF için ayrı sheet
✓ PDF'lerde otomatik isimlendirme
✓ %1 KDV hesaplaması

Başlamak için "PDF Yükle" sekmesine gidin...
"""
        self.preview_text.insert("1.0", welcome)
    
    def _select_pdfs(self):
        """PDF seçimi"""
        if len(self.pdf_files) >= self.max_pdf_count:
            show_warning("Uyarı", f"Maksimum {self.max_pdf_count} PDF yükleyebilirsiniz!")
            return
        
        remaining = self.max_pdf_count - len(self.pdf_files)
        
        file_paths = filedialog.askopenfilenames(
            title=f"PDF Dosyaları Seç (Maks. {remaining} adet)",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_paths:
            if len(file_paths) + len(self.pdf_files) > self.max_pdf_count:
                show_warning("Uyarı", f"Maksimum {self.max_pdf_count} PDF! İlk {remaining} dosya yüklenecek.")
                file_paths = file_paths[:remaining]
            
            self.progress.set_indeterminate(f"{len(file_paths)} PDF işleniyor...")
            
            thread = threading.Thread(target=self._process_pdfs, args=(file_paths,))
            thread.daemon = True
            thread.start()
    
    def _process_pdfs(self, file_paths):
        """PDF'leri işle (thread)"""
        try:
            success_count = 0
            
            for file_path in file_paths:
                pdf_type = self._determine_pdf_type(file_path)
                processor = PDFProcessor()
                success = processor.extract_data_from_pdf(file_path, pdf_type)
                
                if success:
                    pdf_info = {
                        'path': file_path,
                        'name': os.path.basename(file_path),
                        'type': pdf_type,
                        'processor': processor,
                        'product_count': processor.get_product_count()
                    }
                    
                    self.pdf_files.append(pdf_info)
                    self.pdf_processors.append(processor)
                    success_count += 1
                    logger.info(f"PDF yüklendi: {pdf_info['name']} - {pdf_info['product_count']} ürün")
            
            self.after(0, lambda: self._after_pdf_processing(success_count))
            
        except Exception as e:
            logger.error(f"PDF işleme hatası: {e}")
            self.after(0, lambda: self._show_error(f"PDF işleme hatası: {str(e)}"))
    
    def _determine_pdf_type(self, file_path: str) -> str:
        """PDF tipini belirle"""
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages[:2]:
                    text += (page.extract_text() or "").lower()
                
                if 'dondurulmuş' in text or 'don.' in text:
                    return 'dondurulmus'
                elif 'gramaj' in text or 'soslu' in text:
                    return 'gramaj'
                else:
                    return 'normal'
        except:
            return 'normal'
    
    def _after_pdf_processing(self, success_count: int):
        """PDF işleme sonrası"""
        self.progress.reset()
        
        if success_count > 0:
            self.pdf_loaded = True
            self._update_pdf_list()
            self._update_category_counts()
            self._update_statistics()
            
            self.clear_btn.configure(state="normal")
            self.tabview.set("💰 İskonto Ayarla")
            
            total_products = sum(pdf['product_count'] for pdf in self.pdf_files)
            show_success("Başarılı", 
                        f"{success_count} PDF yüklendi!\n"
                        f"Toplam {total_products} ürün bulundu.")
        else:
            show_error("Hata", "PDF'ler işlenirken hata oluştu!")
    
    def _update_pdf_list(self):
        """PDF listesini güncelle"""
        # Mevcut widget'ları temizle
        for widget in self.pdf_list_frame.winfo_children():
            widget.destroy()
        
        if not self.pdf_files:
            self.empty_label = ctk.CTkLabel(
                self.pdf_list_frame,
                text="Henüz PDF yüklenmedi",
                font=ctk.CTkFont(family=FONTS['body'][0], size=FONTS['body'][1]),
                text_color=COLORS['text_secondary']
            )
            self.empty_label.grid(row=0, column=0, pady=40)
            return
        
        for i, pdf_info in enumerate(self.pdf_files):
            pdf_frame = ctk.CTkFrame(
                self.pdf_list_frame,
                fg_color=COLORS['bg_card'],
                corner_radius=SIZES['corner_radius_small'],
                border_width=1,
                border_color=COLORS['border']
            )
            pdf_frame.grid(row=i, column=0, sticky="ew", pady=5, padx=5)
            pdf_frame.grid_columnconfigure(1, weight=1)
            
            # Numara
            ctk.CTkLabel(
                pdf_frame,
                text=f"{i+1}.",
                font=ctk.CTkFont(family=FONTS['body_bold'][0], size=FONTS['body_bold'][1], weight='bold'),
                text_color=ACCENT,
                width=30
            ).grid(row=0, column=0, padx=(10, 5), pady=10)
            
            # Dosya adı
            ctk.CTkLabel(
                pdf_frame,
                text=pdf_info['name'],
                font=ctk.CTkFont(family=FONTS['body'][0], size=FONTS['body'][1]),
                text_color=COLORS['text_primary']
            ).grid(row=0, column=1, sticky="w", padx=5, pady=10)
            
            # Detaylar
            type_names = {'normal': 'Normal', 'dondurulmus': 'Dondurulmuş', 'gramaj': 'Gramajlı'}
            details = f"({type_names.get(pdf_info['type'], 'Normal')} - {pdf_info['product_count']} ürün)"
            
            ctk.CTkLabel(
                pdf_frame,
                text=details,
                font=ctk.CTkFont(family=FONTS['small'][0], size=FONTS['small'][1]),
                text_color=COLORS['text_secondary']
            ).grid(row=0, column=2, padx=10, pady=10)
            
            # Durum
            ctk.CTkLabel(
                pdf_frame,
                text="✓",
                font=ctk.CTkFont(size=16),
                text_color=COLORS['success'],
                width=30
            ).grid(row=0, column=3, padx=(5, 10), pady=10)
    
    def _update_category_counts(self):
        """Kategori sayılarını güncelle"""
        total_counts = {}
        
        for pdf_info in self.pdf_files:
            processor = pdf_info['processor']
            for category, products in processor.categories.items():
                if category not in total_counts:
                    total_counts[category] = 0
                total_counts[category] += len(products)
        
        for category, info in self.category_cards.items():
            count = total_counts.get(category, 0)
            info['count_label'].configure(text=f"({count} ürün)")
    
    def _clear_pdfs(self):
        """PDF'leri temizle"""
        if ask_yes_no("Onay", "Tüm PDF'leri temizlemek istiyor musunuz?"):
            self.pdf_files = []
            self.pdf_processors = []
            self.current_data_all = {}
            self.pdf_loaded = False
            
            self._update_pdf_list()
            self._update_category_counts()
            self._update_statistics()
            
            self.clear_btn.configure(state="disabled")
            self.excel_btn.configure(state="disabled")
            self.pdf_btn.configure(state="disabled")
            self.both_btn.configure(state="disabled")
            
            self._show_welcome_message()
    
    def _set_all_discounts(self, value: float):
        """Tüm iskontoları ayarla"""
        for var in self.discount_vars.values():
            var.set(value)
        
        if self.pdf_loaded:
            self._preview_data()
    
    def _preview_data(self):
        """Önizleme oluştur"""
        if not self.pdf_loaded or not self.pdf_files:
            show_warning("Uyarı", "Önce PDF dosyaları yükleyin!")
            return
        
        try:
            discount_rates = {}
            for category, var in self.discount_vars.items():
                rate = var.get()
                if rate < 0 or rate > 100:
                    show_warning("Uyarı", f"{category} için iskonto 0-100 arasında olmalı!")
                    return
                discount_rates[category] = rate
            
            self.current_data_all = {}
            
            for pdf_info in self.pdf_files:
                processor = pdf_info['processor']
                discounted = processor.apply_discounts(discount_rates)
                
                if discounted:
                    self.current_data_all[pdf_info['name']] = {
                        'data': discounted,
                        'type': pdf_info['type'],
                        'path': pdf_info['path']
                    }
            
            if not self.current_data_all:
                show_warning("Uyarı", "İşlenecek veri bulunamadı!")
                return
            
            self._update_preview()
            self._update_statistics()
            
            self.excel_btn.configure(state="normal")
            self.pdf_btn.configure(state="normal")
            self.both_btn.configure(state="normal")
            
            self.tabview.set("📊 Önizleme")
            
        except Exception as e:
            logger.error(f"Önizleme hatası: {e}")
            show_error("Hata", f"Önizleme hatası: {str(e)}")
    
    def _update_preview(self):
        """Önizleme metnini güncelle"""
        self.preview_text.delete("1.0", "end")
        
        text = "BUPİLİÇ İSKONTOLU FİYAT LİSTELERİ\n"
        text += "=" * 100 + "\n"
        text += f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        text += f"PDF Sayısı: {len(self.pdf_files)}\n\n"
        
        grand_total_products = 0
        grand_total_discount = 0
        
        for pdf_idx, (pdf_name, pdf_data) in enumerate(self.current_data_all.items(), 1):
            text += f"\n{'#'*100}\n"
            text += f"PDF {pdf_idx}: {pdf_name}\n"
            text += f"{'#'*100}\n\n"
            
            pdf_total = 0
            pdf_discount = 0
            
            for category, products in pdf_data['data'].items():
                if not products:
                    continue
                
                rate = self.discount_vars[category].get()
                
                text += f"{'='*100}\n"
                text += f"{category.upper()} - %{rate:.1f} İSKONTO ({len(products)} ÜRÜN)\n"
                text += f"{'='*100}\n"
                
                text += f"{'ÜRÜN ADI':<50} {'ORJ.':>12} {'İSK.':>12} {'FARK':>12}\n"
                text += "-" * 100 + "\n"
                
                cat_discount = 0
                for product in products[:10]:  # İlk 10 ürün
                    name = product['name'][:47] + "..." if len(product['name']) > 47 else product['name']
                    orig = product.get('original_price_with_vat', 0)
                    disc = product['price_with_vat']
                    diff = orig - disc
                    cat_discount += diff
                    
                    text += f"{name:<50} {orig:>12.2f} {disc:>12.2f} {diff:>12.2f}\n"
                
                if len(products) > 10:
                    text += f"... ve {len(products) - 10} ürün daha\n"
                
                text += f"\nKategori İskonto: {cat_discount:.2f} TL\n\n"
                
                pdf_total += len(products)
                pdf_discount += cat_discount
            
            text += f"{'─'*100}\n"
            text += f"PDF ÖZET: Ürün: {pdf_total} | İskonto: {pdf_discount:.2f} TL\n"
            
            grand_total_products += pdf_total
            grand_total_discount += pdf_discount
        
        text += f"\n{'='*100}\n"
        text += "GENEL ÖZET\n"
        text += f"{'='*100}\n"
        text += f"Toplam PDF: {len(self.pdf_files)}\n"
        text += f"Toplam Ürün: {grand_total_products}\n"
        text += f"Toplam İskonto: {grand_total_discount:.2f} TL\n"
        
        self.preview_text.insert("1.0", text)
    
    def _update_statistics(self):
        """İstatistikleri güncelle"""
        if self.current_data_all:
            total_products = 0
            total_categories = set()
            total_discount = 0
            rates = []
            
            for pdf_data in self.current_data_all.values():
                for category, products in pdf_data['data'].items():
                    if products:
                        total_categories.add(category)
                        total_products += len(products)
                        
                        rate = self.discount_vars[category].get()
                        if rate not in rates:
                            rates.append(rate)
                        
                        for product in products:
                            orig = product.get('original_price_with_vat', 0)
                            disc = product['price_with_vat']
                            total_discount += (orig - disc)
            
            avg_discount = sum(rates) / len(rates) if rates else 0
            
            self.stat_cards['pdf_count'].set_value(str(len(self.pdf_files)))
            self.stat_cards['product_count'].set_value(str(total_products))
            self.stat_cards['category_count'].set_value(str(len(total_categories)))
            self.stat_cards['avg_discount'].set_value(f"%{avg_discount:.1f}")
            self.stat_cards['total_discount'].set_value(f"{total_discount:.2f} ₺")
            self.stat_cards['total_records'].set_value(str(total_products))
        else:
            self.stat_cards['pdf_count'].set_value(str(len(self.pdf_files)))
            self.stat_cards['product_count'].set_value("0")
            self.stat_cards['category_count'].set_value("0")
            self.stat_cards['avg_discount'].set_value("%0")
            self.stat_cards['total_discount'].set_value("0 ₺")
            self.stat_cards['total_records'].set_value("0")
    
    def _export_data(self, export_type: str):
        """Veriyi dışa aktar"""
        if not self.current_data_all:
            show_warning("Uyarı", "Önce önizleme yapın!")
            return
        
        try:
            if export_type == 'excel':
                self.export_manager.export_to_excel_multi(self.current_data_all, self.discount_vars)
            elif export_type == 'pdf':
                self.export_manager.export_to_pdf_multi(self.current_data_all, self.discount_vars)
            elif export_type == 'both':
                self.export_manager.export_to_excel_multi(self.current_data_all, self.discount_vars)
                self.export_manager.export_to_pdf_multi(self.current_data_all, self.discount_vars)
        except Exception as e:
            logger.error(f"Dışa aktarma hatası: {e}")
            show_error("Hata", f"Dışa aktarma hatası: {str(e)}")
    
    def _show_error(self, message: str):
        """Hata göster"""
        self.progress.reset()
        show_error("Hata", message)


def main():
    """Standalone çalıştırma"""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    root.title("Bupiliç İskonto Hesaplayıcı")
    root.geometry("1200x800")
    root.minsize(1000, 700)
    
    app = IskontoHesabiApp(root, standalone=True)
    app.pack(fill="both", expand=True)
    
    root.mainloop()


if __name__ == "__main__":
    main()
