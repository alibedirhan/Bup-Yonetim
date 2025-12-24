# -*- coding: utf-8 -*-
"""
BUP-ALL-IN-ONE Ana Program
Tüm modülleri birleştiren modern arayüz - v3.1
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict
import threading
import tkinter as tk
from datetime import datetime
import urllib.request
import json

# Versiyon
APP_VERSION = "3.3.0"
GITHUB_REPO = "alibedirhan/Bup-Yonetim"

# Path ayarları
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Uygulama genel fix'leri (Tk float/locale + logging + crash hook)
from shared.utils import initialize_app
logger = initialize_app("BUP_MAIN")

import customtkinter as ctk

# Shared modüller
from shared.theme import COLORS, MODULE_COLORS, FONTS, SIZES
from shared.components import show_error

# CTK ayarları
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Windows DPI/scaling bazen float üretip Tk'yi bozabiliyor -> sabitle
try:
    ctk.set_widget_scaling(1.0)
    ctk.set_window_scaling(1.0)
except Exception:
    pass


def check_for_updates():
    """GitHub'dan güncelleme kontrolü"""
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={'User-Agent': 'BUP-Yonetim'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            latest = data.get('tag_name', '').lstrip('v')
            if latest and latest > APP_VERSION:
                return latest, data.get('html_url', '')
    except:
        pass
    return None, None


# =============================================================================
# RENK PALETİ - MODERN TASARIM (HTML Prototipinden)
# =============================================================================

# Light tema renkleri - Profesyonel ve temiz
LIGHT_COLORS = {
    'bg_primary': '#f5f5f7',       # Ana arka plan - açık gri
    'bg_secondary': '#ffffff',      # İkincil arka plan - beyaz
    'bg_header': '#1E3A5F',         # Header - koyu mavi
    'bg_card': '#ffffff',           # Kart arka planı
    'bg_card_hover': '#f8f9fa',     # Kart hover
    'text_primary': '#1d1d1f',      # Ana metin - koyu
    'text_secondary': '#6e6e73',    # İkincil metin
    'text_muted': '#86868b',        # Soluk metin
    'border': '#d2d2d7',            # Border
    'border_light': '#e8e8ed',      # Açık border
    'hover': '#f8f9fa',             # Hover
}

# Dark tema renkleri - Claude tarzı (koyu lacivert/mor tonları)
DARK_COLORS = {
    'bg_primary': '#1a1a2e',        # Ana arka plan - koyu lacivert
    'bg_secondary': '#16213e',      # İkincil arka plan
    'bg_header': '#0f0f23',         # Header - en koyu
    'bg_card': '#252542',           # Kart arka planı
    'bg_card_hover': '#2d2d4a',     # Kart hover
    'text_primary': '#f5f5f7',      # Ana metin - açık (OKUNABILIR!)
    'text_secondary': '#a1a1aa',    # İkincil metin
    'text_muted': '#71717a',        # Soluk metin
    'border': '#3f3f5a',            # Border
    'border_light': '#2a2a42',      # Açık border
    'hover': '#2d2d4a',             # Hover
}

# Aktif renk paleti (varsayılan light)
MODERN_COLORS = {
    # Ana renkler
    'bg_primary': '#f5f5f7',
    'bg_secondary': '#ffffff',
    'bg_header': '#1E3A5F',
    'bg_header_gradient': '#0F2439',
    
    # Modül accent renkleri
    'accent_red': '#EF4444',
    'accent_blue': '#3B82F6',
    'accent_teal': '#14B8A6',
    'accent_orange': '#F97316',
    
    # Metin
    'text_primary': '#1d1d1f',
    'text_secondary': '#6e6e73',
    'text_muted': '#86868b',
    'text_white': '#FFFFFF',
    
    # Diğer
    'border': '#d2d2d7',
    'border_light': '#e8e8ed',
    'shadow': '#00000015',
    'hover': '#f8f9fa',
}


# =============================================================================
# MODERN MODÜL KARTI - Tema Destekli
# =============================================================================

class ModernModuleCard(ctk.CTkFrame):
    """Modern tasarımlı modül kartı - Light/Dark tema destekli"""
    
    def __init__(self, master, title: str, description: str, icon: str, 
                 accent_color: str, features: list, command, **kwargs):
        
        # Boyut ayarları
        kwargs.pop('width', None)
        kwargs.pop('height', None)
        
        super().__init__(
            master,
            fg_color=MODERN_COLORS['bg_secondary'],
            corner_radius=16,
            border_width=1,
            border_color=MODERN_COLORS.get('border_light', MODERN_COLORS['border']),
            **kwargs
        )
        
        self.accent_color = accent_color
        self.command = command
        self.title_text = title
        self.description_text = description
        self.features_list = features
        
        # UI elemanları referansları
        self.title_label = None
        self.desc_label = None
        self.feature_labels = []
        self.icon_frame = None
        
        self._setup_ui(title, description, icon, features)
        self._setup_hover()
    
    def _setup_ui(self, title: str, description: str, icon: str, features: list):
        """UI bileşenlerini oluştur"""
        # Ana container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Üst renkli çizgi (accent bar)
        self.accent_bar = ctk.CTkFrame(
            self.container, 
            fg_color=self.accent_color, 
            height=4, 
            corner_radius=0
        )
        self.accent_bar.pack(fill="x")
        
        # İçerik alanı
        content = ctk.CTkFrame(self.container, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=24)
        
        # İkon alanı
        self.icon_frame = ctk.CTkFrame(
            content,
            fg_color=self._get_icon_bg_color(),
            corner_radius=16,
            width=70,
            height=70
        )
        self.icon_frame.pack(pady=(0, 18))
        self.icon_frame.pack_propagate(False)
        
        # İkon - Segoe UI Emoji font kullan (Windows emoji desteği)
        self.icon_label = ctk.CTkLabel(
            self.icon_frame,
            text=icon,
            font=ctk.CTkFont(family="Segoe UI Emoji", size=32),
            text_color=self.accent_color
        )
        self.icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Başlık
        self.title_label = ctk.CTkLabel(
            content,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=MODERN_COLORS['text_primary']
        )
        self.title_label.pack(pady=(0, 8))
        
        # Açıklama
        self.desc_label = ctk.CTkLabel(
            content,
            text=description,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=MODERN_COLORS['text_secondary'],
            wraplength=220
        )
        self.desc_label.pack(pady=(0, 20))
        
        # Özellikler listesi
        features_frame = ctk.CTkFrame(content, fg_color="transparent")
        features_frame.pack(fill="x", pady=(0, 24))
        
        self.feature_labels = []
        for feature in features:
            feature_row = ctk.CTkFrame(features_frame, fg_color="transparent")
            feature_row.pack(fill="x", pady=6)
            
            check_label = ctk.CTkLabel(
                feature_row,
                text="✓",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.accent_color,
                width=20
            )
            check_label.pack(side="left")
            
            text_label = ctk.CTkLabel(
                feature_row,
                text=feature,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=MODERN_COLORS['text_secondary']
            )
            text_label.pack(side="left")
            
            self.feature_labels.append(text_label)
        
        # Başlat butonu
        self.start_btn = ctk.CTkButton(
            content,
            text="Başlat",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            fg_color=self.accent_color,
            hover_color=self._darken_color(self.accent_color, 0.15),
            corner_radius=12,
            height=48,
            command=self.command
        )
        self.start_btn.pack(fill="x")
    
    def _get_icon_bg_color(self):
        """İkon arka plan rengini hesapla"""
        # Accent rengin %10 opaklığında arka plan
        return self._lighten_color(self.accent_color, 0.9)
    
    def _setup_hover(self):
        """Hover efektleri"""
        def on_enter(e):
            self.configure(border_color=self.accent_color, border_width=2)
        
        def on_leave(e):
            self.configure(
                border_color=MODERN_COLORS.get('border_light', MODERN_COLORS['border']), 
                border_width=1
            )
        
        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)
    
    def update_theme(self, is_dark: bool):
        """Tema değişikliğinde kartı güncelle"""
        colors = DARK_COLORS if is_dark else LIGHT_COLORS
        
        # Kart arka planı
        self.configure(
            fg_color=colors['bg_card'],
            border_color=colors.get('border_light', colors['border'])
        )
        
        # Başlık
        if self.title_label:
            self.title_label.configure(text_color=colors['text_primary'])
        
        # Açıklama
        if self.desc_label:
            self.desc_label.configure(text_color=colors['text_secondary'])
        
        # Özellik metinleri
        for label in self.feature_labels:
            label.configure(text_color=colors['text_secondary'])
        
        # İkon arka planı - dark modda biraz daha belirgin
        if self.icon_frame:
            if is_dark:
                # Dark modda icon background biraz daha görünür
                self.icon_frame.configure(fg_color=self._lighten_color(self.accent_color, 0.85))
            else:
                self.icon_frame.configure(fg_color=self._lighten_color(self.accent_color, 0.9))
    
    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """Rengi açıklaştır"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _darken_color(self, hex_color: str, factor: float) -> str:
        """Rengi koyulaştır"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        return f'#{r:02x}{g:02x}{b:02x}'


# =============================================================================
# ANA UYGULAMA
# =============================================================================

class BupilicMainApp(ctk.CTk):
    """Ana uygulama penceresi - Modern tasarım"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Bupiliç İşletme Yönetim Sistemi")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        
        # Program ikonu ayarla
        self._set_app_icon()
        
        # Tema
        self.is_dark_mode = False
        
        # Tavuk animasyonu için
        self.animating = False
        
        # Ayarlar penceresi referansı
        self._settings_window = None
        
        # Modül pencereleri
        self.module_windows: Dict[str, ctk.CTkToplevel] = {}
        
        # Grid yapılandırması
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # UI oluştur
        self._setup_ui()
        
        # Kapatma protokolü
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        logger.info("Ana uygulama başlatıldı")
    
    def _set_app_icon(self):
        """Program ikonunu ayarla"""
        try:
            icon_path = BASE_DIR / "assets" / "bupilic.ico"
            if icon_path.exists():
                self.iconbitmap(str(icon_path))
                logger.info("Program ikonu ayarlandı")
            else:
                # PNG ile dene (Linux/Mac için)
                png_path = BASE_DIR / "assets" / "bupilic.png"
                if png_path.exists():
                    from PIL import Image, ImageTk
                    img = Image.open(png_path)
                    photo = ImageTk.PhotoImage(img)
                    self.iconphoto(True, photo)
                    self._icon_photo = photo  # Referansı tut
                    logger.info("Program ikonu (PNG) ayarlandı")
        except Exception as e:
            logger.warning(f"İkon ayarlanamadı: {e}")
    
    def _setup_ui(self):
        """Tüm UI bileşenlerini oluştur"""
        self.configure(fg_color=MODERN_COLORS['bg_primary'])
        
        self._create_header()
        self._create_main_content()
        self._create_footer()
        
        # Güncelleme kontrolü (arka planda)
        threading.Thread(target=self._check_updates_async, daemon=True).start()
    
    def _check_updates_async(self):
        """Arka planda güncelleme kontrolü"""
        latest, url = check_for_updates()
        if latest:
            self.after(1000, lambda: self._show_update_dialog(latest, url))
    
    def _show_update_dialog(self, version: str, url: str):
        """Güncelleme bildirimi göster"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Güncelleme Mevcut")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.after(100, dialog.grab_set)
        
        ctk.CTkLabel(
            dialog,
            text=f"🎉 Yeni sürüm mevcut: v{version}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(30, 10))
        
        ctk.CTkLabel(
            dialog,
            text=f"Mevcut sürüm: v{APP_VERSION}",
            font=ctk.CTkFont(size=12),
            text_color="#64748B"
        ).pack(pady=(0, 20))
        
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(
            btn_frame, text="İndir", width=100,
            command=lambda: [__import__('webbrowser').open(url), dialog.destroy()]
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame, text="Sonra", width=100,
            fg_color="#E2E8F0", text_color="#64748B", hover_color="#CBD5E1",
            command=dialog.destroy
        ).pack(side="left", padx=5)
    
    def _create_header(self):
        """Modern header - gradient ve logo ile"""
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color=MODERN_COLORS['bg_header'],
            corner_radius=0,
            height=120
        )
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_propagate(False)
        
        # Header için kısa referans
        header = self.header_frame
        
        # Header içeriği
        content = ctk.CTkFrame(header, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40)
        
        # Sol taraf - Logo ve başlık
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(side="left", fill="y", pady=20)
        
        # Logo container
        logo_bg = ctk.CTkFrame(
            left,
            fg_color="#2D4A6F",
            corner_radius=14,
            width=60,
            height=60
        )
        logo_bg.pack(side="left")
        logo_bg.pack_propagate(False)
        
        # Logo ikonu - Segoe UI Emoji font (Windows emoji desteği)
        self.logo_label = ctk.CTkLabel(
            logo_bg,
            text="🐔",
            font=ctk.CTkFont(family="Segoe UI Emoji", size=32),
            text_color="#FFFFFF"
        )
        self.logo_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Başlık metinleri
        title_frame = ctk.CTkFrame(left, fg_color="transparent")
        title_frame.pack(side="left", padx=(20, 0))
        
        ctk.CTkLabel(
            title_frame,
            text="Bupiliç",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=MODERN_COLORS['text_white']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            title_frame,
            text="İşletme Yönetim Sistemi",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#94A3B8"
        ).pack(anchor="w")
        
        # Sağ taraf - Menü ve bilgiler
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.pack(side="right", fill="y", pady=25)
        
        # Tarih/Saat
        self.time_label = ctk.CTkLabel(
            right,
            text=datetime.now().strftime("%d %B %Y"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#94A3B8"
        )
        self.time_label.pack(anchor="e")
        
        # Versiyon badge
        version_badge = ctk.CTkFrame(right, fg_color="#2D4A6F", corner_radius=8)
        version_badge.pack(anchor="e", pady=(8, 0))
        
        ctk.CTkLabel(
            version_badge,
            text="  v3.1  ",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#B8C9E0"
        ).pack(padx=6, pady=3)
    
    def _create_main_content(self):
        """Ana içerik - Hoşgeldin ve modül kartları"""
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=50, pady=30)
        
        # Hoşgeldin bölümü
        self.welcome_frame = ctk.CTkFrame(content, fg_color="transparent")
        self.welcome_frame.pack(fill="x", pady=(0, 30))
        
        self.welcome_title = ctk.CTkLabel(
            self.welcome_frame,
            text="👋 Hoş Geldiniz!",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=MODERN_COLORS['text_primary']
        )
        self.welcome_title.pack(anchor="w")
        
        self.welcome_subtitle = ctk.CTkLabel(
            self.welcome_frame,
            text="İşletme yönetimi için aşağıdaki modüllerden birini seçerek başlayabilirsiniz.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=MODERN_COLORS['text_secondary']
        )
        self.welcome_subtitle.pack(anchor="w", pady=(8, 0))
        
        # Modül kartları container
        self.cards_frame = ctk.CTkFrame(content, fg_color="transparent")
        self.cards_frame.pack(fill="both", expand=True)
        
        # Kısa referans
        cards_container = self.cards_frame
        
        # 4 sütun grid
        for i in range(4):
            cards_container.grid_columnconfigure(i, weight=1, uniform="cards")
        
        # Modül tanımları
        modules = [
            {
                'title': 'İskonto Hesaplama',
                'description': 'PDF fiyat listelerinden otomatik iskonto hesaplama',
                'icon': '💰',
                'accent': MODERN_COLORS['accent_red'],
                'features': ['Çoklu PDF desteği', 'Kategori bazlı iskonto', 'Excel/PDF export'],
                'command': self._open_iskonto
            },
            {
                'title': 'Karlılık Analizi',
                'description': 'Detaylı şube ve ürün karlılık raporları',
                'icon': '📊',
                'accent': MODERN_COLORS['accent_blue'],
                'features': ['Şube karşılaştırma', 'Zaman analizi', 'Dashboard görünümü'],
                'command': self._open_karlilik
            },
            {
                'title': 'Müşteri Takip',
                'description': 'Müşteri kayıp/kazanç analizi ve kontrolü',
                'icon': '👥',
                'accent': MODERN_COLORS['accent_teal'],
                'features': ['Dönem karşılaştırma', 'Kayıp müşteri tespiti', 'Trend analizi'],
                'command': self._open_musteri
            },
            {
                'title': 'Yaşlandırma',
                'description': 'Cari hesap yaşlandırma ve takip sistemi',
                'icon': '📈',
                'accent': MODERN_COLORS['accent_orange'],
                'features': ['Otomatik yaşlandırma', 'Sorumlu atama', 'Detaylı raporlar'],
                'command': self._open_yaslandirma
            }
        ]
        
        # Kartları oluştur ve listede sakla
        self.module_cards = []
        for i, module in enumerate(modules):
            card = ModernModuleCard(
                cards_container,
                title=module['title'],
                description=module['description'],
                icon=module['icon'],
                accent_color=module['accent'],
                features=module['features'],
                command=module['command']
            )
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.module_cards.append(card)
    
    def _create_footer(self):
        """Footer - Tema ve ayarlar"""
        self.footer_frame = ctk.CTkFrame(
            self,
            fg_color=MODERN_COLORS['bg_secondary'],
            corner_radius=0,
            height=60,
            border_width=1,
            border_color=MODERN_COLORS['border']
        )
        self.footer_frame.grid(row=2, column=0, sticky="ew")
        self.footer_frame.grid_propagate(False)
        
        # Kısa referans
        footer = self.footer_frame
        
        # Sol - Bilgi
        left = ctk.CTkFrame(footer, fg_color="transparent")
        left.pack(side="left", padx=30, fill="y")
        
        info = ctk.CTkFrame(left, fg_color="transparent")
        info.pack(expand=True)
        
        self.footer_text = ctk.CTkLabel(
            info,
            text=f"🐔 Bupiliç v{APP_VERSION} Modern Edition",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=MODERN_COLORS['text_secondary']
        )
        self.footer_text.pack(side="left")
        
        self.footer_separator = ctk.CTkLabel(
            info,
            text="  •  ",
            font=ctk.CTkFont(size=12),
            text_color=MODERN_COLORS['text_muted']
        )
        self.footer_separator.pack(side="left")
        
        self.footer_author = ctk.CTkLabel(
            info,
            text="Ali Bedirhan",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=MODERN_COLORS['text_secondary']
        )
        self.footer_author.pack(side="left")
        
        # Sağ - Butonlar
        right = ctk.CTkFrame(footer, fg_color="transparent")
        right.pack(side="right", padx=30, fill="y")
        
        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.pack(expand=True)
        
        # Tema butonu - Tavuk animasyonlu
        self.theme_btn = ctk.CTkButton(
            btn_frame,
            text="🐔",  # Tavuk ikonu - Gündüz
            width=48,
            height=48,
            corner_radius=24,
            fg_color=MODERN_COLORS['hover'],
            hover_color=MODERN_COLORS['border'],
            text_color=MODERN_COLORS['text_secondary'],
            border_width=1,
            border_color=MODERN_COLORS['border'],
            font=ctk.CTkFont(size=20),
            command=self._toggle_theme_with_animation
        )
        self.theme_btn.pack(side="left", padx=(0, 12))
        
        # Ayarlar butonu
        self.settings_btn = ctk.CTkButton(
            btn_frame,
            text="⚙️ Ayarlar",
            width=110,
            height=48,
            corner_radius=24,
            fg_color=MODERN_COLORS['hover'],
            hover_color=MODERN_COLORS['border'],
            text_color=MODERN_COLORS['text_secondary'],
            border_width=1,
            border_color=MODERN_COLORS['border'],
            font=ctk.CTkFont(family="Segoe UI", size=13),
            command=self._open_settings_safe
        )
        self.settings_btn.pack(side="left")
    
    # =========================================================================
    # TEMA DEĞİŞTİRME - SADECE ANA EKRAN (Modüller etkilenmiyor)
    # =========================================================================
    
    def _toggle_theme_with_animation(self):
        """Tema değiştir - Tavuk animasyonlu"""
        if self.animating:
            return
        
        self.animating = True
        self.theme_btn.configure(state="disabled")
        self._run_chicken_animation(0)
    
    def _run_chicken_animation(self, step: int):
        """Tavuk animasyonu - 8 frame"""
        frames = ["🐔", "🐓", "🥚", "🐣", "🐤", "🐥", "🐔", "🐓"]
        
        if step < len(frames):
            try:
                self.theme_btn.configure(text=frames[step])
                self.after(60, lambda: self._run_chicken_animation(step + 1))
            except:
                self._apply_main_theme()
        else:
            self._apply_main_theme()
    
    def _apply_main_theme(self):
        """Ana ekrana tema uygula - Modüller ETKİLENMİYOR"""
        try:
            self.is_dark_mode = not self.is_dark_mode
            self._update_main_ui_colors()
            
            # İkon güncelle
            icon = "🌜" if self.is_dark_mode else "🐔"
            self.theme_btn.configure(text=icon, state="normal")
            
            logger.info(f"Ana ekran teması: {'dark' if self.is_dark_mode else 'light'}")
            
        except Exception as e:
            logger.error(f"Tema değiştirme hatası: {e}")
        finally:
            self.animating = False
            self.theme_btn.configure(state="normal")
    
    def _update_main_ui_colors(self):
        """Ana ekran renklerini güncelle - Claude tarzı dark tema"""
        if self.is_dark_mode:
            colors = DARK_COLORS
        else:
            colors = LIGHT_COLORS
        
        # Ana pencere
        self.configure(fg_color=colors['bg_primary'])
        
        # Header güncelle
        if hasattr(self, 'header_frame'):
            self.header_frame.configure(fg_color=colors['bg_header'])
        
        # Hoşgeldin bölümü
        if hasattr(self, 'welcome_frame'):
            self.welcome_frame.configure(fg_color="transparent")
        if hasattr(self, 'welcome_title'):
            # Dark modda turuncu daha parlak, light modda normal
            title_color = "#f59e0b" if self.is_dark_mode else "#F97316"
            self.welcome_title.configure(text_color=title_color)
        if hasattr(self, 'welcome_subtitle'):
            self.welcome_subtitle.configure(text_color=colors['text_secondary'])
        
        # Kartlar container
        if hasattr(self, 'cards_frame'):
            self.cards_frame.configure(fg_color="transparent")
        
        # Modül kartlarını güncelle
        if hasattr(self, 'module_cards'):
            for card in self.module_cards:
                card.update_theme(self.is_dark_mode)
        
        # Footer güncelle
        if hasattr(self, 'footer_frame'):
            self.footer_frame.configure(
                fg_color=colors['bg_secondary'],
                border_color=colors.get('border_light', colors['border'])
            )
        if hasattr(self, 'footer_text'):
            self.footer_text.configure(text_color=colors['text_secondary'])
        if hasattr(self, 'footer_separator'):
            self.footer_separator.configure(text_color=colors['text_muted'])
        if hasattr(self, 'footer_author'):
            self.footer_author.configure(text_color=colors['text_secondary'])
        
        # Tema ve Ayarlar butonları
        if hasattr(self, 'theme_btn'):
            self.theme_btn.configure(
                fg_color=colors['bg_card'] if self.is_dark_mode else colors['hover'],
                hover_color=colors['hover'] if self.is_dark_mode else colors['border'],
                text_color=colors['text_primary'],
                border_color=colors['border'],
                border_width=1
            )
        if hasattr(self, 'settings_btn'):
            self.settings_btn.configure(
                fg_color=colors['bg_card'] if self.is_dark_mode else colors['hover'],
                hover_color=colors['hover'] if self.is_dark_mode else colors['border'],
                text_color=colors['text_secondary'],
                border_color=colors['border'],
                border_width=1
            )
    
    def _apply_theme_direct(self, theme: str):
        """Tema uygula - Ayarlar penceresinden (sadece ana ekran)"""
        try:
            self.is_dark_mode = (theme == "Dark")
            self._update_main_ui_colors()
            
            # Ana buton ikonunu güncelle
            self.theme_btn.configure(text="🌜" if self.is_dark_mode else "🐔")
            
            # Ayarlar penceresini kapat ve yeniden aç (tema uyumu için)
            if hasattr(self, '_settings_window') and self._settings_window is not None:
                try:
                    if self._settings_window.winfo_exists():
                        self._settings_window.destroy()
                        self._settings_window = None
                        # Kısa gecikme ile yeniden aç
                        self.after(100, self._create_settings_window)
                except:
                    pass
            
            logger.info(f"Tema uygulandı: {theme}")
            
        except Exception as e:
            logger.error(f"Tema uygulama hatası: {e}")
    
    # =========================================================================
    # AYARLAR PENCERESİ - DONMA SORUNUNU ÇÖZEN VERSİYON
    # =========================================================================
    
    def _open_settings_safe(self):
        """Ayarlar penceresini güvenli şekilde aç"""
        # Zaten açık mı kontrol et
        if hasattr(self, '_settings_window') and self._settings_window is not None:
            try:
                if self._settings_window.winfo_exists():
                    self._settings_window.focus_force()
                    self._settings_window.lift()
                    return
            except:
                pass
        
        # Yeni pencere oluştur
        self._create_settings_window()
    
    def _create_settings_window(self):
        """Ayarlar penceresini oluştur - grab_set KULLANMADAN"""
        self._settings_window = ctk.CTkToplevel(self)
        settings = self._settings_window
        
        settings.title("⚙️ Ayarlar")
        settings.geometry("500x550")
        settings.resizable(False, False)
        
        # Pencereyi ortala
        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 500) // 2
        y = self.winfo_y() + (self.winfo_height() - 550) // 2
        settings.geometry(f"500x550+{x}+{y}")
        
        # transient - ana pencereyle ilişkilendir
        settings.transient(self)
        
        # Kapanma işlemi
        def close_settings():
            try:
                self._settings_window = None
                settings.destroy()
            except:
                pass
        
        settings.protocol("WM_DELETE_WINDOW", close_settings)
        
        # ÖNEMLİ: grab_set KULLANMIYORUZ - donmaya neden oluyor!
        # Bunun yerine focus ve lift kullanıyoruz
        settings.focus_force()
        settings.lift()
        
        # === UI İÇERİĞİ ===
        # Tema renklerini al
        colors = DARK_COLORS if self.is_dark_mode else LIGHT_COLORS
        
        # Ana pencere arka planı
        settings.configure(fg_color=colors['bg_primary'])
        
        main = ctk.CTkFrame(settings, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Başlık
        ctk.CTkLabel(
            main,
            text="⚙️ Uygulama Ayarları",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=colors['text_primary']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            main,
            text="Uygulamanın görünümünü ve davranışını özelleştirin",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=colors['text_secondary']
        ).pack(anchor="w", pady=(5, 25))
        
        # === GÖRÜNÜM KARTI ===
        appearance_card = ctk.CTkFrame(
            main, 
            corner_radius=12,
            fg_color=colors['bg_card'],
            border_width=1,
            border_color=colors['border_light']
        )
        appearance_card.pack(fill="x", pady=(0, 15))
        
        app_inner = ctk.CTkFrame(appearance_card, fg_color="transparent")
        app_inner.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            app_inner,
            text="🎨 Görünüm",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=colors['text_primary']
        ).pack(anchor="w", pady=(0, 15))
        
        # Tema satırı
        theme_row = ctk.CTkFrame(app_inner, fg_color="transparent")
        theme_row.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            theme_row,
            text="Tema:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=colors['text_secondary'],
            width=120, anchor="w"
        ).pack(side="left")
        
        # Mevcut temayı belirle
        current_theme = "Dark" if self.is_dark_mode else "Light"
        
        theme_selector = ctk.CTkSegmentedButton(
            theme_row,
            values=["Light", "Dark"],
            command=self._apply_theme_direct,
            font=ctk.CTkFont(size=12),
            corner_radius=8
        )
        theme_selector.set(current_theme)
        theme_selector.pack(side="right")
        
        # === PROGRAM KARTI ===
        program_card = ctk.CTkFrame(
            main, 
            corner_radius=12,
            fg_color=colors['bg_card'],
            border_width=1,
            border_color=colors['border_light']
        )
        program_card.pack(fill="x", pady=(0, 15))
        
        prog_inner = ctk.CTkFrame(program_card, fg_color="transparent")
        prog_inner.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            prog_inner,
            text="🖥️ Program",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=colors['text_primary']
        ).pack(anchor="w", pady=(0, 15))
        
        # Versiyon bilgisi
        version_row = ctk.CTkFrame(prog_inner, fg_color="transparent")
        version_row.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            version_row,
            text="Versiyon:",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=colors['text_secondary'],
            width=120, anchor="w"
        ).pack(side="left")
        
        ctk.CTkLabel(
            version_row,
            text=f"v{APP_VERSION}",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="#3B82F6"
        ).pack(side="right")
        
        # === HAKKINDA KARTI ===
        about_card = ctk.CTkFrame(
            main, 
            corner_radius=12,
            fg_color=colors['bg_card'],
            border_width=1,
            border_color=colors['border_light']
        )
        about_card.pack(fill="x", pady=(0, 15))
        
        about_inner = ctk.CTkFrame(about_card, fg_color="transparent")
        about_inner.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            about_inner,
            text="ℹ️ Hakkında",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=colors['text_primary']
        ).pack(anchor="w", pady=(0, 15))
        
        ctk.CTkLabel(
            about_inner,
            text=f"🐔 Bupiliç İşletme Yönetim Sistemi\n"
                 f"Versiyon: {APP_VERSION}\n"
                 f"Geliştirici: Ali Bedirhan\n"
                 f"© 2024-2025",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=colors['text_secondary'],
            justify="left"
        ).pack(anchor="w")
        
        # Kapat butonu
        ctk.CTkButton(
            main,
            text="Kapat",
            width=120,
            height=44,
            corner_radius=22,
            fg_color=colors['bg_card'] if self.is_dark_mode else colors['hover'],
            hover_color=colors['hover'] if self.is_dark_mode else colors['border'],
            text_color=colors['text_primary'],
            border_width=1,
            border_color=colors['border'],
            command=close_settings
        ).pack(side="bottom", pady=(20, 0))
    
    # =========================================================================
    # MODÜL AÇMA
    # =========================================================================
    
    def _open_iskonto(self):
        """İskonto modülünü aç"""
        self._open_module("ISKONTO_HESABI", "İskonto Hesaplama")
    
    def _open_karlilik(self):
        """Karlılık modülünü aç"""
        self._open_module("KARLILIK_ANALIZI", "Karlılık Analizi")
    
    def _open_musteri(self):
        """Müşteri modülünü aç"""
        self._open_module("Musteri_Sayisi_Kontrolu", "Müşteri Takip")
    
    def _open_yaslandirma(self):
        """Yaşlandırma modülünü aç"""
        self._open_module("YASLANDIRMA", "Yaşlandırma")
    
    def _open_module(self, module_name: str, display_name: str):
        """Modül penceresini aç"""
        # Zaten açık mı kontrol et
        if module_name in self.module_windows:
            window = self.module_windows[module_name]
            try:
                if window.winfo_exists():
                    window.focus()
                    window.lift()
                    return
            except:
                pass
            del self.module_windows[module_name]
        
        try:
            if module_name == "ISKONTO_HESABI":
                window = ctk.CTkToplevel(self)
                window.title(f"Bupiliç - {display_name}")
                window.geometry("1200x800")
                window.minsize(1000, 700)
                
                from ISKONTO_HESABI.ui import IskontoHesabiApp
                app = IskontoHesabiApp(window)
                app.pack(fill="both", expand=True)
                
                self.module_windows[module_name] = window
                self._setup_window_close(window, module_name)
            
            elif module_name == "Musteri_Sayisi_Kontrolu":
                window = ctk.CTkToplevel(self)
                window.title(f"Bupiliç - {display_name}")
                window.geometry("1200x800")
                window.minsize(1000, 700)
                
                musteri_path = BASE_DIR / "Musteri_Sayisi_Kontrolu"
                if str(musteri_path) not in sys.path:
                    sys.path.insert(0, str(musteri_path))
                
                from Musteri_Sayisi_Kontrolu.main import ExcelComparisonLogic
                from Musteri_Sayisi_Kontrolu.ui_modern import MusteriTakipApp
                
                app_logic = ExcelComparisonLogic()
                app = MusteriTakipApp(window, app_logic)
                app.pack(fill="both", expand=True)
                
                self.module_windows[module_name] = window
                self._setup_window_close(window, module_name)
            
            elif module_name == "KARLILIK_ANALIZI":
                self._open_karlilik_legacy(display_name)
                return
            
            elif module_name == "YASLANDIRMA":
                window = ctk.CTkToplevel(self)
                window.title(f"Bupiliç - {display_name}")
                window.geometry("1400x900")
                window.minsize(1200, 800)
                
                yaslandirma_path = BASE_DIR / "YASLANDIRMA"
                for p in [yaslandirma_path, yaslandirma_path / "gui", yaslandirma_path / "modules"]:
                    if str(p) not in sys.path:
                        sys.path.insert(0, str(p))
                
                from YASLANDIRMA.ui_modern import YaslandirmaApp
                
                app = YaslandirmaApp(window)
                app.pack(fill="both", expand=True)
                
                self.module_windows[module_name] = window
                self._setup_window_close(window, module_name)
            
            logger.info(f"{module_name} modülü açıldı")
            
        except Exception as e:
            logger.error(f"Modül hatası: {e}", exc_info=True)
            show_error("Hata", f"{display_name} açılırken hata oluştu:\n{str(e)}")
    
    def _open_karlilik_legacy(self, display_name: str):
        """Karlılık modülünü CTK ile aç"""
        try:
            window = ctk.CTkToplevel(self)
            window.title(f"Bupiliç - {display_name}")
            window.geometry("1400x900")
            window.minsize(1200, 800)
            
            karlilik_path = BASE_DIR / "KARLILIK_ANALIZI"
            if str(karlilik_path) not in sys.path:
                sys.path.insert(0, str(karlilik_path))
            
            from KARLILIK_ANALIZI.ui_ctk import KarlilikApp
            
            app = KarlilikApp(window)
            app.pack(fill="both", expand=True)
            
            self.module_windows["KARLILIK_ANALIZI"] = window
            self._setup_window_close(window, "KARLILIK_ANALIZI")
            
            logger.info("KARLILIK_ANALIZI (legacy) modülü açıldı")
            
        except Exception as e:
            logger.error(f"Karlılık legacy hatası: {e}", exc_info=True)
            show_error("Hata", f"{display_name} açılırken hata oluştu:\n{str(e)}")
    
    def _setup_window_close(self, window, module_name: str):
        """Pencere kapatma protokolü"""
        def on_close():
            if module_name in self.module_windows:
                del self.module_windows[module_name]
            try:
                window.destroy()
            except:
                pass
        
        window.protocol("WM_DELETE_WINDOW", on_close)
    
    def _on_closing(self):
        """Uygulama kapatılırken"""
        for module_name, window in list(self.module_windows.items()):
            try:
                if window.winfo_exists():
                    window.destroy()
            except:
                pass
        
        self.module_windows.clear()
        logger.info("Ana uygulama kapatılıyor")
        self.quit()
        self.destroy()


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Ana fonksiyon"""
    app = BupilicMainApp()
    app.mainloop()


if __name__ == "__main__":
    main()
