# themes.py - Tema ve Renk Yönetimi Modülü

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Tuple, Any, List
from enum import Enum
import platform


class ThemeType(Enum):
    """Tema türleri"""
    LIGHT = "light"
    DARK = "dark"
    BLUE = "blue"
    GREEN = "green"
    CUSTOM = "custom"


class ColorPalette:
    """Renk paleti sınıfı"""
    
    def __init__(self, name: str, colors: Dict[str, str]):
        self.name = name
        self.colors = colors
    
    def get(self, key: str, default: str = "#ffffff") -> str:
        """Renk değeri döndürür"""
        return self.colors.get(key, default)
    
    def set(self, key: str, value: str) -> None:
        """Renk değeri ayarlar"""
        self.colors[key] = value
    
    def update(self, new_colors: Dict[str, str]) -> None:
        """Renk paletini günceller"""
        self.colors.update(new_colors)


class ThemeManager:
    """Tema yönetim sınıfı"""
    
    # Önceden tanımlı temalar
    PREDEFINED_THEMES = {
        ThemeType.LIGHT: {
            'bg_primary': '#f8fafc',
            'bg_secondary': '#ffffff', 
            'bg_accent': '#e2e8f0',
            'bg_hover': '#f1f5f9',
            'primary': '#3b82f6',
            'primary_dark': '#2563eb',
            'primary_light': '#93c5fd',
            'success': '#10b981',
            'success_dark': '#059669',
            'success_light': '#6ee7b7',
            'warning': '#f59e0b',
            'warning_dark': '#d97706',
            'warning_light': '#fbbf24',
            'danger': '#ef4444',
            'danger_dark': '#dc2626',
            'danger_light': '#f87171',
            'info': '#06b6d4',
            'info_dark': '#0891b2',
            'info_light': '#67e8f9',
            'text_primary': '#1f2937',
            'text_secondary': '#6b7280',
            'text_light': '#9ca3af',
            'text_muted': '#d1d5db',
            'border': '#e5e7eb',
            'border_light': '#f3f4f6',
            'shadow': '#f3f4f6',
            'shadow_dark': '#e5e7eb',
            'card_bg': '#ffffff',
            'input_bg': '#f8fafc',
            'button_bg': '#f9fafb',
            'header_bg': '#ffffff',
            'sidebar_bg': '#f9fafb'
        },
        
        ThemeType.DARK: {
            'bg_primary': '#1a202c',
            'bg_secondary': '#2d3748', 
            'bg_accent': '#4a5568',
            'bg_hover': '#2d3748',
            'primary': '#4299e1',
            'primary_dark': '#3182ce',
            'primary_light': '#63b3ed',
            'success': '#48bb78',
            'success_dark': '#38a169',
            'success_light': '#68d391',
            'warning': '#ed8936',
            'warning_dark': '#dd6b20',
            'warning_light': '#f6ad55',
            'danger': '#f56565',
            'danger_dark': '#e53e3e',
            'danger_light': '#fc8181',
            'info': '#4fd1c7',
            'info_dark': '#38b2ac',
            'info_light': '#81e6d9',
            'text_primary': '#f7fafc',
            'text_secondary': '#cbd5e0',
            'text_light': '#a0aec0',
            'text_muted': '#718096',
            'border': '#4a5568',
            'border_light': '#2d3748',
            'shadow': '#171923',
            'shadow_dark': '#0f1214',
            'card_bg': '#2d3748',
            'input_bg': '#4a5568',
            'button_bg': '#4a5568',
            'header_bg': '#2d3748',
            'sidebar_bg': '#1a202c'
        },
        
        ThemeType.BLUE: {
            'bg_primary': '#eff6ff',
            'bg_secondary': '#ffffff', 
            'bg_accent': '#dbeafe',
            'bg_hover': '#f0f9ff',
            'primary': '#2563eb',
            'primary_dark': '#1d4ed8',
            'primary_light': '#60a5fa',
            'success': '#059669',
            'success_dark': '#047857',
            'success_light': '#34d399',
            'warning': '#d97706',
            'warning_dark': '#b45309',
            'warning_light': '#fbbf24',
            'danger': '#dc2626',
            'danger_dark': '#b91c1c',
            'danger_light': '#f87171',
            'info': '#0891b2',
            'info_dark': '#0e7490',
            'info_light': '#22d3ee',
            'text_primary': '#1e3a8a',
            'text_secondary': '#1e40af',
            'text_light': '#3b82f6',
            'text_muted': '#93c5fd',
            'border': '#bfdbfe',
            'border_light': '#dbeafe',
            'shadow': '#e0e7ff',
            'shadow_dark': '#c7d2fe',
            'card_bg': '#ffffff',
            'input_bg': '#f8fafc',
            'button_bg': '#f0f9ff',
            'header_bg': '#1e40af',
            'sidebar_bg': '#eff6ff'
        },
        
        ThemeType.GREEN: {
            'bg_primary': '#f0fdf4',
            'bg_secondary': '#ffffff', 
            'bg_accent': '#dcfce7',
            'bg_hover': '#f0fdf4',
            'primary': '#16a34a',
            'primary_dark': '#15803d',
            'primary_light': '#4ade80',
            'success': '#10b981',
            'success_dark': '#059669',
            'success_light': '#6ee7b7',
            'warning': '#f59e0b',
            'warning_dark': '#d97706',
            'warning_light': '#fbbf24',
            'danger': '#ef4444',
            'danger_dark': '#dc2626',
            'danger_light': '#f87171',
            'info': '#06b6d4',
            'info_dark': '#0891b2',
            'info_light': '#67e8f9',
            'text_primary': '#14532d',
            'text_secondary': '#166534',
            'text_light': '#16a34a',
            'text_muted': '#86efac',
            'border': '#bbf7d0',
            'border_light': '#dcfce7',
            'shadow': '#ecfdf5',
            'shadow_dark': '#d1fae5',
            'card_bg': '#ffffff',
            'input_bg': '#f8fafc',
            'button_bg': '#f0fdf4',
            'header_bg': '#166534',
            'sidebar_bg': '#f0fdf4'
        }
    }
    
    def __init__(self, initial_theme: ThemeType = ThemeType.LIGHT):
        self.current_theme = initial_theme
        self.current_palette = ColorPalette(
            initial_theme.value,
            self.PREDEFINED_THEMES[initial_theme].copy()
        )
        self.custom_palettes: Dict[str, ColorPalette] = {}
        self._style_configured = False
        
    def get_palette(self, theme_type: Optional[ThemeType] = None) -> ColorPalette:
        """Belirtilen tema paletini döndürür"""
        if theme_type is None:
            return self.current_palette
        
        if theme_type in self.PREDEFINED_THEMES:
            return ColorPalette(
                theme_type.value,
                self.PREDEFINED_THEMES[theme_type].copy()
            )
        
        return self.current_palette
    
    def set_theme(self, theme_type: ThemeType) -> bool:
        """Tema değiştirir"""
        try:
            if theme_type in self.PREDEFINED_THEMES:
                self.current_theme = theme_type
                self.current_palette = ColorPalette(
                    theme_type.value,
                    self.PREDEFINED_THEMES[theme_type].copy()
                )
                return True
            return False
        except Exception:
            return False
    
    def create_custom_palette(self, name: str, base_theme: ThemeType, 
                            overrides: Dict[str, str]) -> bool:
        """Özel renk paleti oluşturur"""
        try:
            if base_theme not in self.PREDEFINED_THEMES:
                return False
            
            base_colors = self.PREDEFINED_THEMES[base_theme].copy()
            base_colors.update(overrides)
            
            self.custom_palettes[name] = ColorPalette(name, base_colors)
            return True
        except Exception:
            return False
    
    def apply_custom_palette(self, name: str) -> bool:
        """Özel paleti uygular"""
        try:
            if name in self.custom_palettes:
                self.current_palette = self.custom_palettes[name]
                self.current_theme = ThemeType.CUSTOM
                return True
            return False
        except Exception:
            return False
    
    def get_color(self, key: str, default: str = "#ffffff") -> str:
        """Geçerli temadan renk döndürür"""
        return self.current_palette.get(key, default)
    
    def get_colors(self) -> Dict[str, str]:
        """Tüm renkleri döndürür"""
        return self.current_palette.colors.copy()


class StyleManager:
    """TTK stil yöneticisi"""
    
    def __init__(self, theme_manager: ThemeManager):
        self.theme_manager = theme_manager
        self.style = None
        self._setup_style()
    
    def _setup_style(self) -> None:
        """TTK stilini kurur"""
        try:
            self.style = ttk.Style()
            
            # Platform uyumlu tema seçimi
            available_themes = self.style.theme_names()
            if 'clam' in available_themes:
                self.style.theme_use('clam')
            elif 'vista' in available_themes:
                self.style.theme_use('vista')
            elif 'default' in available_themes:
                self.style.theme_use('default')
                
        except Exception:
            pass
    
    def configure_modern_styles(self) -> None:
        """Modern stilleri yapılandırır"""
        if not self.style:
            return
            
        try:
            colors = self.theme_manager.get_colors()
            
            # Modern Button
            self.style.configure(
                'Modern.TButton',
                font=('Segoe UI', 11),
                relief='flat',
                borderwidth=0,
                focuscolor='none',
                background=colors.get('primary'),
                foreground='white'
            )
            
            self.style.map('Modern.TButton',
                         background=[
                             ('active', colors.get('primary_dark')),
                             ('pressed', colors.get('primary_dark'))
                         ])
            
            # Modern Progressbar
            self.style.configure(
                'Modern.Horizontal.TProgressbar',
                background=colors.get('primary'),
                troughcolor=colors.get('border'),
                borderwidth=0,
                lightcolor=colors.get('primary'),
                darkcolor=colors.get('primary_dark')
            )
            
            # Modern Frame
            self.style.configure(
                'Modern.TFrame',
                background=colors.get('bg_secondary'),
                relief='flat',
                borderwidth=1
            )
            
            # Modern Notebook
            self.style.configure(
                'Modern.TNotebook',
                background=colors.get('bg_primary'),
                borderwidth=0
            )
            
            self.style.configure(
                'Modern.TNotebook.Tab',
                background=colors.get('bg_accent'),
                foreground=colors.get('text_primary'),
                padding=[12, 8],
                font=('Segoe UI', 10)
            )
            
            self.style.map('Modern.TNotebook.Tab',
                         background=[
                             ('selected', colors.get('primary')),
                             ('active', colors.get('bg_hover'))
                         ],
                         foreground=[
                             ('selected', 'white'),
                             ('active', colors.get('text_primary'))
                         ])
            
            # Modern Entry
            self.style.configure(
                'Modern.TEntry',
                fieldbackground=colors.get('input_bg'),
                background=colors.get('input_bg'),
                foreground=colors.get('text_primary'),
                borderwidth=1,
                relief='solid'
            )
            
            # Modern Combobox
            self.style.configure(
                'Modern.TCombobox',
                fieldbackground=colors.get('input_bg'),
                background=colors.get('input_bg'),
                foreground=colors.get('text_primary'),
                borderwidth=1,
                arrowcolor=colors.get('text_secondary')
            )
            
            # Modern Treeview
            self.style.configure(
                'Modern.Treeview',
                background=colors.get('bg_secondary'),
                foreground=colors.get('text_primary'),
                fieldbackground=colors.get('bg_secondary'),
                borderwidth=0
            )
            
            self.style.configure(
                'Modern.Treeview.Heading',
                background=colors.get('primary'),
                foreground='white',
                font=('Segoe UI', 10, 'bold')
            )
            
        except Exception as e:
            print(f"Style configuration error: {e}")
    
    def apply_theme_to_widget(self, widget: tk.Widget, widget_type: str = 'default') -> None:
        """Widget'a tema uygular"""
        try:
            colors = self.theme_manager.get_colors()
            
            if widget_type == 'frame':
                widget.config(bg=colors.get('bg_secondary'))
            elif widget_type == 'label':
                widget.config(
                    bg=colors.get('bg_secondary'),
                    fg=colors.get('text_primary')
                )
            elif widget_type == 'button':
                widget.config(
                    bg=colors.get('primary'),
                    fg='white',
                    relief='flat',
                    bd=0
                )
            elif widget_type == 'entry':
                widget.config(
                    bg=colors.get('input_bg'),
                    fg=colors.get('text_primary'),
                    relief='solid',
                    bd=1
                )
            elif widget_type == 'text':
                widget.config(
                    bg=colors.get('bg_secondary'),
                    fg=colors.get('text_primary'),
                    relief='flat'
                )
            elif widget_type == 'canvas':
                widget.config(
                    bg=colors.get('bg_primary'),
                    highlightthickness=0
                )
                
        except Exception:
            pass


class ThemePresets:
    """Önceden tanımlı tema ayarları"""
    
    @staticmethod
    def get_business_theme() -> Dict[str, str]:
        """İş tema renkleri"""
        return {
            'bg_primary': '#f8f9fa',
            'bg_secondary': '#ffffff',
            'primary': '#004085',
            'success': '#28a745',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'info': '#17a2b8',
            'text_primary': '#212529',
            'text_secondary': '#6c757d'
        }
    
    @staticmethod
    def get_modern_theme() -> Dict[str, str]:
        """Modern tema renkleri"""
        return {
            'bg_primary': '#fafafa',
            'bg_secondary': '#ffffff',
            'primary': '#6366f1',
            'success': '#10b981',
            'warning': '#f59e0b',
            'danger': '#ef4444',
            'info': '#06b6d4',
            'text_primary': '#111827',
            'text_secondary': '#6b7280'
        }
    
    @staticmethod
    def get_minimal_theme() -> Dict[str, str]:
        """Minimal tema renkleri"""
        return {
            'bg_primary': '#ffffff',
            'bg_secondary': '#ffffff',
            'primary': '#000000',
            'success': '#22c55e',
            'warning': '#eab308',
            'danger': '#ef4444',
            'info': '#3b82f6',
            'text_primary': '#000000',
            'text_secondary': '#666666'
        }


class FontManager:
    """Font yönetimi"""
    
    DEFAULT_FONTS = {
        'default': ('Segoe UI', 11),
        'heading': ('Segoe UI', 16, 'bold'),
        'subheading': ('Segoe UI', 14, 'bold'),
        'body': ('Segoe UI', 11),
        'small': ('Segoe UI', 10),
        'code': ('Consolas', 10),
        'button': ('Segoe UI', 11, 'bold')
    }
    
    def __init__(self):
        self.current_fonts = self.DEFAULT_FONTS.copy()
        self._setup_platform_fonts()
    
    def _setup_platform_fonts(self) -> None:
        """Platform uyumlu fontları ayarlar"""
        try:
            system = platform.system()
            
            if system == "Darwin":  # macOS
                self.current_fonts.update({
                    'default': ('SF Pro Display', 11),
                    'heading': ('SF Pro Display', 16, 'bold'),
                    'subheading': ('SF Pro Display', 14, 'bold'),
                    'body': ('SF Pro Display', 11),
                    'small': ('SF Pro Display', 10),
                    'code': ('Monaco', 10),
                    'button': ('SF Pro Display', 11, 'bold')
                })
            elif system == "Linux":
                self.current_fonts.update({
                    'default': ('Ubuntu', 11),
                    'heading': ('Ubuntu', 16, 'bold'),
                    'subheading': ('Ubuntu', 14, 'bold'),
                    'body': ('Ubuntu', 11),
                    'small': ('Ubuntu', 10),
                    'code': ('Ubuntu Mono', 10),
                    'button': ('Ubuntu', 11, 'bold')
                })
                
        except Exception:
            pass
    
    def get_font(self, font_type: str) -> Tuple[str, int, str]:
        """Font döndürür"""
        font = self.current_fonts.get(font_type, self.current_fonts['default'])
        if len(font) == 2:
            return (font[0], font[1], 'normal')
        return font
    
    def set_font(self, font_type: str, font_tuple: Tuple[str, int, str]) -> None:
        """Font ayarlar"""
        self.current_fonts[font_type] = font_tuple


# Global tema yöneticisi
_global_theme_manager = None
_global_style_manager = None
_global_font_manager = None


def get_theme_manager() -> ThemeManager:
    """Global tema yöneticisini döndürür"""
    global _global_theme_manager
    if _global_theme_manager is None:
        _global_theme_manager = ThemeManager()
    return _global_theme_manager


def get_style_manager() -> StyleManager:
    """Global stil yöneticisini döndürür"""
    global _global_style_manager, _global_theme_manager
    if _global_style_manager is None:
        if _global_theme_manager is None:
            _global_theme_manager = ThemeManager()
        _global_style_manager = StyleManager(_global_theme_manager)
    return _global_style_manager


def get_font_manager() -> FontManager:
    """Global font yöneticisini döndürür"""
    global _global_font_manager
    if _global_font_manager is None:
        _global_font_manager = FontManager()
    return _global_font_manager


def apply_theme_to_app(root: tk.Tk, theme_type: ThemeType = ThemeType.LIGHT) -> None:
    """Uygulamaya tema uygular"""
    try:
        theme_manager = get_theme_manager()
        style_manager = get_style_manager()
        
        theme_manager.set_theme(theme_type)
        style_manager.configure_modern_styles()
        
        # Root pencere arka planı
        colors = theme_manager.get_colors()
        root.configure(bg=colors.get('bg_primary'))
        
    except Exception as e:
        print(f"Theme application error: {e}")


def get_colors() -> Dict[str, str]:
    """Geçerli tema renklerini döndürür"""
    return get_theme_manager().get_colors()


def get_color(key: str, default: str = "#ffffff") -> str:
    """Belirli rengi döndürür"""
    return get_theme_manager().get_color(key, default)
