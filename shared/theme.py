# -*- coding: utf-8 -*-
"""
BUP-ALL-IN-ONE Ortak Tema Modülü
Tüm alt programlarda tutarlı görünüm için merkezi tema yönetimi
"""

# Windows/Tk: 'bad screen distance "200.0"' benzeri hataları engelle
try:
    from .utils import apply_tk_float_fix, setup_turkish_locale
    apply_tk_float_fix()
    setup_turkish_locale()
except Exception:
    pass

import customtkinter as ctk

from typing import Dict, Any
import platform

# ============================================================================
# GLOBAL RENK PALETİ - TÜM MODÜLLERDE AYNI RENKLER
# ============================================================================

COLORS = {
    # Ana renkler
    'primary': '#1E3A5F',           # Koyu mavi - ana renk
    'primary_light': '#2E5077',     # Açık mavi
    'primary_dark': '#0F2439',      # Daha koyu mavi
    
    # Vurgu renkleri (her modül için farklı ama uyumlu)
    'accent_red': '#E63946',        # İskonto modülü
    'accent_blue': '#457B9D',       # Karlılık modülü  
    'accent_teal': '#2A9D8F',       # Müşteri modülü
    'accent_orange': '#F4A261',     # Yaşlandırma modülü
    
    # Durum renkleri
    'success': '#2ECC71',           # Başarı yeşili
    'warning': '#F39C12',           # Uyarı turuncusu
    'error': '#E74C3C',             # Hata kırmızısı
    'info': '#3498DB',              # Bilgi mavisi
    
    # Arka plan renkleri
    'bg_dark': '#1A1A2E',           # Koyu tema arka plan
    'bg_light': '#F5F7FA',          # Açık tema arka plan
    'bg_card': '#FFFFFF',           # Kart arka planı
    'bg_card_dark': '#16213E',      # Koyu tema kart
    
    # Metin renkleri
    'text_primary': '#2C3E50',      # Ana metin
    'text_secondary': '#7F8C8D',    # İkincil metin
    'text_light': '#FFFFFF',        # Açık metin
    'text_muted': '#95A5A6',        # Soluk metin
    
    # Kenarlık renkleri
    'border': '#E0E6ED',            # Normal kenarlık
    'border_dark': '#34495E',       # Koyu kenarlık
    'border_light': '#ECF0F1',      # Açık kenarlık
    
    # Hover renkleri
    'hover_light': '#EBF5FB',       # Açık hover
    'hover_dark': '#2C3E50',        # Koyu hover
}

# Modül bazlı accent renkleri
MODULE_COLORS = {
    'ISKONTO_HESABI': {
        'accent': COLORS['accent_red'],
        'accent_hover': '#C1121F',
        'gradient_start': '#E63946',
        'gradient_end': '#1E3A5F'
    },
    'KARLILIK_ANALIZI': {
        'accent': COLORS['accent_blue'],
        'accent_hover': '#1D3557',
        'gradient_start': '#457B9D',
        'gradient_end': '#1E3A5F'
    },
    'Musteri_Sayisi_Kontrolu': {
        'accent': COLORS['accent_teal'],
        'accent_hover': '#1D7874',
        'gradient_start': '#2A9D8F',
        'gradient_end': '#1E3A5F'
    },
    'YASLANDIRMA': {
        'accent': COLORS['accent_orange'],
        'accent_hover': '#E76F51',
        'gradient_start': '#F4A261',
        'gradient_end': '#1E3A5F'
    }
}

# ============================================================================
# FONT AYARLARI
# ============================================================================

def get_system_font() -> str:
    """Platform uyumlu font döndür"""
    system = platform.system()
    if system == "Windows":
        return 'Segoe UI'
    elif system == "Darwin":
        return 'SF Pro Display'
    else:
        return 'Ubuntu'

FONT_FAMILY = get_system_font()

FONTS = {
    'title': (FONT_FAMILY, 24, 'bold'),
    'subtitle': (FONT_FAMILY, 18, 'bold'),
    'heading': (FONT_FAMILY, 16, 'bold'),
    'subheading': (FONT_FAMILY, 14, 'bold'),
    'body': (FONT_FAMILY, 12),
    'body_bold': (FONT_FAMILY, 12, 'bold'),
    'small': (FONT_FAMILY, 10),
    'small_bold': (FONT_FAMILY, 10, 'bold'),
    'tiny': (FONT_FAMILY, 9),
    'button': (FONT_FAMILY, 12, 'bold'),
    'button_small': (FONT_FAMILY, 10, 'bold'),
}

# ============================================================================
# BOYUT AYARLARI
# ============================================================================

SIZES = {
    'button_height': 40,
    'button_height_large': 50,
    'button_height_small': 32,
    'entry_height': 40,
    'corner_radius': 8,
    'corner_radius_large': 12,
    'corner_radius_small': 4,
    'padding_small': 5,
    'padding_medium': 10,
    'padding_large': 20,
    'padding_xlarge': 30,
}

# ============================================================================
# TEMA SINIFI
# ============================================================================

class BupTheme:
    """Merkezi tema yönetim sınıfı"""
    
    def __init__(self, module_name: str = None, appearance_mode: str = "light"):
        """
        Args:
            module_name: Modül adı (MODULE_COLORS'dan accent rengi almak için)
            appearance_mode: 'light' veya 'dark'
        """
        self.module_name = module_name
        self.appearance_mode = appearance_mode
        self._setup_ctk()
        
    def _setup_ctk(self):
        """CustomTkinter temel ayarları"""
        ctk.set_appearance_mode(self.appearance_mode)
        ctk.set_default_color_theme("blue")
    
    @property
    def accent(self) -> str:
        """Modül accent rengini döndür"""
        if self.module_name and self.module_name in MODULE_COLORS:
            return MODULE_COLORS[self.module_name]['accent']
        return COLORS['primary']
    
    @property
    def accent_hover(self) -> str:
        """Modül accent hover rengini döndür"""
        if self.module_name and self.module_name in MODULE_COLORS:
            return MODULE_COLORS[self.module_name]['accent_hover']
        return COLORS['primary_dark']
    
    @property
    def bg(self) -> str:
        """Arka plan rengini döndür"""
        if self.appearance_mode == "dark":
            return COLORS['bg_dark']
        return COLORS['bg_light']
    
    @property
    def bg_card(self) -> str:
        """Kart arka plan rengini döndür"""
        if self.appearance_mode == "dark":
            return COLORS['bg_card_dark']
        return COLORS['bg_card']
    
    @property
    def text(self) -> str:
        """Ana metin rengini döndür"""
        if self.appearance_mode == "dark":
            return COLORS['text_light']
        return COLORS['text_primary']
    
    @property
    def text_secondary(self) -> str:
        """İkincil metin rengini döndür"""
        return COLORS['text_secondary']
    
    def get_button_colors(self, button_type: str = 'primary') -> Dict[str, str]:
        """Buton renklerini döndür"""
        if button_type == 'primary':
            return {
                'fg_color': self.accent,
                'hover_color': self.accent_hover,
                'text_color': COLORS['text_light']
            }
        elif button_type == 'secondary':
            return {
                'fg_color': 'transparent',
                'hover_color': COLORS['hover_light'],
                'text_color': self.accent,
                'border_color': self.accent
            }
        elif button_type == 'success':
            return {
                'fg_color': COLORS['success'],
                'hover_color': '#27AE60',
                'text_color': COLORS['text_light']
            }
        elif button_type == 'danger':
            return {
                'fg_color': COLORS['error'],
                'hover_color': '#C0392B',
                'text_color': COLORS['text_light']
            }
        elif button_type == 'warning':
            return {
                'fg_color': COLORS['warning'],
                'hover_color': '#E67E22',
                'text_color': COLORS['text_light']
            }
        else:
            return {
                'fg_color': COLORS['primary'],
                'hover_color': COLORS['primary_dark'],
                'text_color': COLORS['text_light']
            }


# ============================================================================
# YARDIMCI FONKSİYONLAR
# ============================================================================

def darken_color(hex_color: str, factor: float = 0.2) -> str:
    """Rengi koyulaştır"""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)
    r = int(r * (1 - factor))
    g = int(g * (1 - factor))
    b = int(b * (1 - factor))
    return f'#{r:02x}{g:02x}{b:02x}'

def lighten_color(hex_color: str, factor: float = 0.2) -> str:
    """Rengi açıklaştır"""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:], 16)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return f'#{r:02x}{g:02x}{b:02x}'

def create_gradient_colors(start_color: str, end_color: str, steps: int = 5) -> list:
    """İki renk arasında gradient oluştur"""
    start = start_color.lstrip('#')
    end = end_color.lstrip('#')
    
    r1, g1, b1 = int(start[:2], 16), int(start[2:4], 16), int(start[4:], 16)
    r2, g2, b2 = int(end[:2], 16), int(end[2:4], 16), int(end[4:], 16)
    
    colors = []
    for i in range(steps):
        ratio = i / (steps - 1)
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        colors.append(f'#{r:02x}{g:02x}{b:02x}')
    
    return colors


# ============================================================================
# ORTAK WİDGET STİLLERİ
# ============================================================================

def get_entry_style(theme: BupTheme) -> Dict[str, Any]:
    """Entry widget için stil"""
    return {
        'height': SIZES['entry_height'],
        'corner_radius': SIZES['corner_radius'],
        'border_width': 1,
        'border_color': COLORS['border'],
        'fg_color': theme.bg_card,
        'text_color': theme.text,
        'placeholder_text_color': COLORS['text_muted']
    }

def get_frame_style(theme: BupTheme) -> Dict[str, Any]:
    """Frame widget için stil"""
    return {
        'corner_radius': SIZES['corner_radius'],
        'fg_color': theme.bg_card,
        'border_width': 1,
        'border_color': COLORS['border']
    }

def get_label_style(theme: BupTheme, style: str = 'body') -> Dict[str, Any]:
    """Label widget için stil"""
    return {
        'font': ctk.CTkFont(family=FONTS[style][0], size=FONTS[style][1], 
                           weight='bold' if len(FONTS[style]) > 2 else 'normal'),
        'text_color': theme.text
    }
