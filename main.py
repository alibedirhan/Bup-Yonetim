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
APP_VERSION = "3.2.1"
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
# RENK PALETİ - MODERN TASARIM
# =============================================================================

MODERN_COLORS = {
    # Ana renkler
    'bg_primary': '#F8FAFC',
    'bg_secondary': '#FFFFFF',
    'bg_header': '#1E3A5F',
    'bg_header_gradient': '#0F2439',
    
    # Modül accent renkleri
    'accent_red': '#EF4444',
    'accent_blue': '#3B82F6',
    'accent_teal': '#14B8A6',
    'accent_orange': '#F97316',
    
    # Metin
    'text_primary': '#1E293B',
    'text_secondary': '#64748B',
    'text_muted': '#94A3B8',
    'text_white': '#FFFFFF',
    
    # Diğer
    'border': '#E2E8F0',
    'shadow': '#00000015',
    'hover': '#F1F5F9',
}


# =============================================================================
# MODERN MODÜL KARTI
# =============================================================================

class ModernModuleCard(ctk.CTkFrame):
    """Modern tasarımlı modül kartı"""
    
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
            border_color=MODERN_COLORS['border'],
            **kwargs
        )
        
        self.accent_color = accent_color
        self.command = command
        self._setup_ui(title, description, icon, features)
        self._setup_hover()
    
    def _setup_ui(self, title: str, description: str, icon: str, features: list):
        """UI bileşenlerini oluştur"""
        # Ana container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Üst renkli çizgi
        accent_bar = ctk.CTkFrame(
            container, 
            fg_color=self.accent_color, 
            height=5, 
            corner_radius=3
        )
        accent_bar.pack(fill="x", pady=(0, 20))
        
        # İkon alanı
        icon_frame = ctk.CTkFrame(
            container,
            fg_color=self._lighten_color(self.accent_color, 0.9),
            corner_radius=16,
            width=80,
            height=80
        )
        icon_frame.pack(pady=(0, 20))
        icon_frame.pack_propagate(False)
        
        # İkon - modüle özel
        icons_map = {'💰': '₺', '📊': '📈', '👥': '👤', '📈': '⏰'}
        display_icon = icons_map.get(icon, icon)
        
        ctk.CTkLabel(
            icon_frame,
            text=display_icon,
            font=ctk.CTkFont(size=32),
            text_color=self.accent_color
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Başlık
        ctk.CTkLabel(
            container,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=MODERN_COLORS['text_primary']
        ).pack(pady=(0, 8))
        
        # Açıklama
        ctk.CTkLabel(
            container,
            text=description,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=MODERN_COLORS['text_secondary'],
            wraplength=200
        ).pack(pady=(0, 20))
        
        # Özellikler listesi
        features_frame = ctk.CTkFrame(container, fg_color="transparent")
        features_frame.pack(fill="x", pady=(0, 20))
        
        for feature in features:
            feature_row = ctk.CTkFrame(features_frame, fg_color="transparent")
            feature_row.pack(fill="x", pady=3)
            
            ctk.CTkLabel(
                feature_row,
                text="✓",
                font=ctk.CTkFont(size=12),
                text_color=self.accent_color,
                width=20
            ).pack(side="left")
            
            ctk.CTkLabel(
                feature_row,
                text=feature,
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=MODERN_COLORS['text_secondary']
            ).pack(side="left")
        
        # Başlat butonu
        self.start_btn = ctk.CTkButton(
            container,
            text="Başlat",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=self.accent_color,
            hover_color=self._darken_color(self.accent_color, 0.15),
            corner_radius=25,
            height=45,
            command=self.command
        )
        self.start_btn.pack(fill="x")
    
    def _setup_hover(self):
        """Hover efektleri"""
        def on_enter(e):
            self.configure(border_color=self.accent_color, border_width=2)
        
        def on_leave(e):
            self.configure(border_color=MODERN_COLORS['border'], border_width=1)
        
        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)
    
    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """Rengi açıklaştır"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _darken_color(self, hex_color: str, factor: float) -> str:
        """Rengi koyulaştır"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)
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
        
        # Tema
        self.is_dark_mode = False
        
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
        header = ctk.CTkFrame(
            self,
            fg_color=MODERN_COLORS['bg_header'],
            corner_radius=0,
            height=120
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        
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
            corner_radius=12,
            width=60,
            height=60
        )
        logo_bg.pack(side="left")
        logo_bg.pack_propagate(False)
        
        ctk.CTkLabel(
            logo_bg,
            text="🐔",
            font=ctk.CTkFont(size=28)
        ).place(relx=0.5, rely=0.5, anchor="center")
        
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
        welcome = ctk.CTkFrame(content, fg_color="transparent")
        welcome.pack(fill="x", pady=(0, 30))
        
        ctk.CTkLabel(
            welcome,
            text="👋 Hoş Geldiniz!",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=MODERN_COLORS['text_primary']
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            welcome,
            text="İşletme yönetimi için aşağıdaki modüllerden birini seçerek başlayabilirsiniz.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=MODERN_COLORS['text_secondary']
        ).pack(anchor="w", pady=(8, 0))
        
        # Modül kartları container
        cards_container = ctk.CTkFrame(content, fg_color="transparent")
        cards_container.pack(fill="both", expand=True)
        
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
    
    def _create_footer(self):
        """Footer - Tema ve ayarlar"""
        footer = ctk.CTkFrame(
            self,
            fg_color=MODERN_COLORS['bg_secondary'],
            corner_radius=0,
            height=60,
            border_width=1,
            border_color=MODERN_COLORS['border']
        )
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_propagate(False)
        
        # Sol - Bilgi
        left = ctk.CTkFrame(footer, fg_color="transparent")
        left.pack(side="left", padx=30, fill="y")
        
        info = ctk.CTkFrame(left, fg_color="transparent")
        info.pack(expand=True)
        
        ctk.CTkLabel(
            info,
            text="🐔 Bupiliç v3.1 Modern Edition",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=MODERN_COLORS['text_secondary']
        ).pack(side="left")
        
        ctk.CTkLabel(
            info,
            text="  •  ",
            font=ctk.CTkFont(size=12),
            text_color=MODERN_COLORS['text_muted']
        ).pack(side="left")
        
        ctk.CTkLabel(
            info,
            text="Ali Bedirhan",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=MODERN_COLORS['text_secondary']
        ).pack(side="left")
        
        # Sağ - Butonlar
        right = ctk.CTkFrame(footer, fg_color="transparent")
        right.pack(side="right", padx=30, fill="y")
        
        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.pack(expand=True)
        
        # Tema butonu
        self.theme_btn = ctk.CTkButton(
            btn_frame,
            text="🌙" if not self.is_dark_mode else "☀️",
            width=40,
            height=40,
            corner_radius=20,
            fg_color=MODERN_COLORS['hover'],
            hover_color=MODERN_COLORS['border'],
            text_color=MODERN_COLORS['text_secondary'],
            font=ctk.CTkFont(size=16),
            command=self._toggle_theme
        )
        self.theme_btn.pack(side="left", padx=(0, 10))
        
        # Ayarlar butonu
        ctk.CTkButton(
            btn_frame,
            text="⚙️ Ayarlar",
            width=110,
            height=40,
            corner_radius=20,
            fg_color=MODERN_COLORS['hover'],
            hover_color=MODERN_COLORS['border'],
            text_color=MODERN_COLORS['text_secondary'],
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=self._show_settings
        ).pack(side="left")
    
    # =========================================================================
    # TEMA VE AYARLAR
    # =========================================================================
    
    def _toggle_theme(self):
        """Tema değiştir"""
        self.is_dark_mode = not self.is_dark_mode
        
        if self.is_dark_mode:
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="☀️")
        else:
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="🌙")
    
    def _show_settings(self):
        """Gelişmiş ayarlar penceresi"""
        settings = ctk.CTkToplevel(self)
        settings.title("⚙️ Ayarlar")
        settings.geometry("500x600")
        settings.transient(self)
        
        # Pencereyi ortala
        settings.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 500) // 2
        y = self.winfo_y() + (self.winfo_height() - 600) // 2
        settings.geometry(f"+{x}+{y}")
        
        # grab_set için pencere görünür olana kadar bekle
        def do_grab():
            try:
                settings.grab_set()
            except:
                pass
        settings.after(100, do_grab)
        
        # Ana container - basit frame
        main = ctk.CTkFrame(settings, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Başlık
        ctk.CTkLabel(
            main,
            text="⚙️ Uygulama Ayarları",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            main,
            text="Uygulamanın görünümünü ve davranışını özelleştirin",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#64748B"
        ).pack(anchor="w", pady=(5, 25))
        
        # === GÖRÜNÜM KARTI ===
        appearance_card = ctk.CTkFrame(main, corner_radius=12)
        appearance_card.pack(fill="x", pady=(0, 15))
        
        app_inner = ctk.CTkFrame(appearance_card, fg_color="transparent")
        app_inner.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            app_inner,
            text="🎨 Görünüm",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 15))
        
        # Tema satırı
        theme_row = ctk.CTkFrame(app_inner, fg_color="transparent")
        theme_row.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            theme_row,
            text="Tema:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=120, anchor="w"
        ).pack(side="left")
        
        self.theme_selector = ctk.CTkSegmentedButton(
            theme_row,
            values=["Light", "Dark", "System"],
            command=self._apply_theme,
            font=ctk.CTkFont(size=11)
        )
        self.theme_selector.set("Light" if not self.is_dark_mode else "Dark")
        self.theme_selector.pack(side="right")
        
        # === PROGRAM KARTI ===
        program_card = ctk.CTkFrame(main, corner_radius=12)
        program_card.pack(fill="x", pady=(0, 15))
        
        prog_inner = ctk.CTkFrame(program_card, fg_color="transparent")
        prog_inner.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            prog_inner,
            text="🖥️ Program",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 15))
        
        # Başlangıç modülü
        startup_row = ctk.CTkFrame(prog_inner, fg_color="transparent")
        startup_row.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            startup_row,
            text="Başlangıç Modülü:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=140, anchor="w"
        ).pack(side="left")
        
        ctk.CTkOptionMenu(
            startup_row,
            values=["Ana Menü", "Karlılık Analizi", "İskonto", "Müşteri Takip", "Yaşlandırma"],
            width=180
        ).pack(side="right")
        
        # Son dosyaları hatırla
        remember_row = ctk.CTkFrame(prog_inner, fg_color="transparent")
        remember_row.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            remember_row,
            text="Son dosyaları hatırla:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            width=140, anchor="w"
        ).pack(side="left")
        
        remember_switch = ctk.CTkSwitch(remember_row, text="", width=40)
        remember_switch.select()
        remember_switch.pack(side="right")
        
        # === HAKKINDA KARTI ===
        about_card = ctk.CTkFrame(main, corner_radius=12)
        about_card.pack(fill="x", pady=(0, 15))
        
        about_inner = ctk.CTkFrame(about_card, fg_color="transparent")
        about_inner.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            about_inner,
            text="ℹ️ Hakkında",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 15))
        
        ctk.CTkLabel(
            about_inner,
            text="🐔 Bupiliç İşletme Yönetim Sistemi\n"
                 "Versiyon: 3.1 Modern Edition\n"
                 "Geliştirici: Ali Bedirhan\n"
                 "© 2024-2025",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#64748B",
            justify="left"
        ).pack(anchor="w")
        
        # Kapat butonu
        ctk.CTkButton(
            main,
            text="Kapat",
            width=120,
            height=40,
            corner_radius=20,
            command=settings.destroy
        ).pack(side="bottom", pady=(20, 0))
    
    def _apply_theme(self, theme: str):
        """Tema uygula"""
        ctk.set_appearance_mode(theme.lower())
        self.is_dark_mode = (theme == "Dark")
        self.theme_btn.configure(text="☀️" if self.is_dark_mode else "🌙")
    
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
