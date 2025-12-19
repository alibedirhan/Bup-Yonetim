# -*- coding: utf-8 -*-
"""
BUP-ALL-IN-ONE Ortak UI Bileşenleri
Tüm modüllerde kullanılan ortak widget'lar ve UI fonksiyonları
"""

import customtkinter as ctk
from typing import Callable, Optional, List, Dict, Any
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from .theme import (
    COLORS, FONTS, SIZES, BupTheme, 
    darken_color, lighten_color, MODULE_COLORS
)


# ============================================================================
# MODERN HEADER COMPONENT
# ============================================================================

class ModernHeader(ctk.CTkFrame):
    """Tüm modüllerde kullanılan modern header"""
    
    def __init__(
        self,
        master,
        title: str,
        subtitle: str = "",
        module_name: str = None,
        show_back_button: bool = False,
        back_callback: Callable = None,
        **kwargs
    ):
        # Modül rengini al
        accent = COLORS['primary']
        if module_name and module_name in MODULE_COLORS:
            accent = MODULE_COLORS[module_name]['accent']
        
        super().__init__(master, fg_color=accent, corner_radius=0, **kwargs)
        
        self.grid_columnconfigure(1, weight=1)
        
        # Geri butonu
        if show_back_button and back_callback:
            back_btn = ctk.CTkButton(
                self,
                text="← Geri",
                width=80,
                height=32,
                fg_color="transparent",
                hover_color=darken_color(accent, 0.2),
                text_color=COLORS['text_light'],
                font=ctk.CTkFont(family=FONTS['small'][0], size=FONTS['small'][1]),
                command=back_callback
            )
            back_btn.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Başlık container
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=1, pady=20)
        
        # Ana başlık
        title_label = ctk.CTkLabel(
            title_frame,
            text=title,
            font=ctk.CTkFont(family=FONTS['title'][0], size=FONTS['title'][1], weight='bold'),
            text_color=COLORS['text_light']
        )
        title_label.pack()
        
        # Alt başlık
        if subtitle:
            subtitle_label = ctk.CTkLabel(
                title_frame,
                text=subtitle,
                font=ctk.CTkFont(family=FONTS['body'][0], size=FONTS['body'][1]),
                text_color=lighten_color(accent, 0.4)
            )
            subtitle_label.pack(pady=(5, 0))


# ============================================================================
# MODERN CARD COMPONENT
# ============================================================================

class ModernCard(ctk.CTkFrame):
    """Modern kart bileşeni"""
    
    def __init__(
        self,
        master,
        title: str = "",
        icon: str = "",
        **kwargs
    ):
        # Varsayılan stil
        default_kwargs = {
            'fg_color': COLORS['bg_card'],
            'corner_radius': SIZES['corner_radius_large'],
            'border_width': 1,
            'border_color': COLORS['border']
        }
        default_kwargs.update(kwargs)
        
        super().__init__(master, **default_kwargs)
        
        self.content_frame = self
        
        # Başlık varsa
        if title or icon:
            header = ctk.CTkFrame(self, fg_color="transparent")
            header.pack(fill="x", padx=SIZES['padding_large'], pady=(SIZES['padding_large'], SIZES['padding_medium']))
            
            header_text = f"{icon} {title}".strip()
            title_label = ctk.CTkLabel(
                header,
                text=header_text,
                font=ctk.CTkFont(family=FONTS['subheading'][0], size=FONTS['subheading'][1], weight='bold'),
                text_color=COLORS['text_primary']
            )
            title_label.pack(anchor="w")
            
            # Ayırıcı çizgi
            separator = ctk.CTkFrame(self, height=1, fg_color=COLORS['border'])
            separator.pack(fill="x", padx=SIZES['padding_large'])
            
            # İçerik frame
            self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.content_frame.pack(fill="both", expand=True, padx=SIZES['padding_large'], pady=SIZES['padding_large'])


# ============================================================================
# MODERN BUTTON
# ============================================================================

class ModernButton(ctk.CTkButton):
    """Modern stil buton"""
    
    def __init__(
        self,
        master,
        text: str,
        command: Callable = None,
        button_type: str = 'primary',
        module_name: str = None,
        icon: str = "",
        size: str = 'normal',
        **kwargs
    ):
        # Boyut ayarları
        height = SIZES['button_height']
        font_key = 'button'
        
        if size == 'large':
            height = SIZES['button_height_large']
        elif size == 'small':
            height = SIZES['button_height_small']
            font_key = 'button_small'
        
        # Renk ayarları
        if button_type == 'primary' and module_name and module_name in MODULE_COLORS:
            fg_color = MODULE_COLORS[module_name]['accent']
            hover_color = MODULE_COLORS[module_name]['accent_hover']
            text_color = COLORS['text_light']
        elif button_type == 'primary':
            fg_color = COLORS['primary']
            hover_color = COLORS['primary_dark']
            text_color = COLORS['text_light']
        elif button_type == 'success':
            fg_color = COLORS['success']
            hover_color = darken_color(COLORS['success'], 0.2)
            text_color = COLORS['text_light']
        elif button_type == 'danger':
            fg_color = COLORS['error']
            hover_color = darken_color(COLORS['error'], 0.2)
            text_color = COLORS['text_light']
        elif button_type == 'warning':
            fg_color = COLORS['warning']
            hover_color = darken_color(COLORS['warning'], 0.2)
            text_color = COLORS['text_light']
        elif button_type == 'secondary':
            fg_color = "transparent"
            hover_color = COLORS['hover_light']
            text_color = COLORS['text_primary']
        else:
            fg_color = COLORS['primary']
            hover_color = COLORS['primary_dark']
            text_color = COLORS['text_light']
        
        # Buton metni
        button_text = f"{icon} {text}".strip() if icon else text
        
        # Varsayılan kwargs
        default_kwargs = {
            'text': button_text,
            'command': command,
            'height': height,
            'corner_radius': SIZES['corner_radius'],
            'fg_color': fg_color,
            'hover_color': hover_color,
            'text_color': text_color,
            'font': ctk.CTkFont(family=FONTS[font_key][0], size=FONTS[font_key][1], weight='bold')
        }
        default_kwargs.update(kwargs)
        
        super().__init__(master, **default_kwargs)


# ============================================================================
# FILE SELECTOR COMPONENT
# ============================================================================

class FileSelector(ctk.CTkFrame):
    """Dosya seçim bileşeni"""
    
    def __init__(
        self,
        master,
        label: str,
        filetypes: List[tuple] = None,
        module_name: str = None,
        on_file_selected: Callable = None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.filetypes = filetypes or [("Tüm dosyalar", "*.*")]
        self.on_file_selected = on_file_selected
        self.module_name = module_name
        self.selected_path = ctk.StringVar()
        
        # Label
        label_widget = ctk.CTkLabel(
            self,
            text=label,
            font=ctk.CTkFont(family=FONTS['body_bold'][0], size=FONTS['body_bold'][1], weight='bold'),
            text_color=COLORS['text_primary']
        )
        label_widget.pack(anchor="w", pady=(0, 5))
        
        # Dosya seçim frame
        select_frame = ctk.CTkFrame(self, fg_color="transparent")
        select_frame.pack(fill="x")
        select_frame.grid_columnconfigure(0, weight=1)
        
        # Path entry
        self.path_entry = ctk.CTkEntry(
            select_frame,
            textvariable=self.selected_path,
            height=SIZES['entry_height'],
            corner_radius=SIZES['corner_radius'],
            border_width=1,
            border_color=COLORS['border'],
            fg_color=COLORS['bg_card'],
            text_color=COLORS['text_primary'],
            placeholder_text="Dosya seçilmedi...",
            state="readonly"
        )
        self.path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # Seç butonu
        self.select_btn = ModernButton(
            select_frame,
            text="📁 Seç",
            command=self._select_file,
            module_name=module_name,
            size='small',
            width=100
        )
        self.select_btn.grid(row=0, column=1)
    
    def _select_file(self):
        """Dosya seçim dialogu aç"""
        file_path = filedialog.askopenfilename(
            title="Dosya Seç",
            filetypes=self.filetypes
        )
        
        if file_path:
            self.selected_path.set(file_path)
            if self.on_file_selected:
                self.on_file_selected(file_path)
    
    def get_path(self) -> str:
        """Seçili dosya yolunu döndür"""
        return self.selected_path.get()
    
    def set_path(self, path: str):
        """Dosya yolunu ayarla"""
        self.selected_path.set(path)
    
    def clear(self):
        """Seçimi temizle"""
        self.selected_path.set("")


# ============================================================================
# PROGRESS INDICATOR
# ============================================================================

class ProgressIndicator(ctk.CTkFrame):
    """İlerleme göstergesi"""
    
    def __init__(self, master, module_name: str = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.module_name = module_name
        accent = COLORS['primary']
        if module_name and module_name in MODULE_COLORS:
            accent = MODULE_COLORS[module_name]['accent']
        
        # Durum metni
        self.status_label = ctk.CTkLabel(
            self,
            text="Hazır",
            font=ctk.CTkFont(family=FONTS['small'][0], size=FONTS['small'][1]),
            text_color=COLORS['text_secondary']
        )
        self.status_label.pack(anchor="w", pady=(0, 5))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self,
            height=8,
            corner_radius=4,
            progress_color=accent,
            fg_color=COLORS['border']
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
    
    def set_progress(self, value: float, status: str = ""):
        """İlerleme değerini ayarla (0-1 arası)"""
        self.progress_bar.set(min(1, max(0, value)))
        if status:
            self.status_label.configure(text=status)
    
    def reset(self):
        """Sıfırla"""
        self.progress_bar.set(0)
        self.status_label.configure(text="Hazır")
    
    def set_indeterminate(self, status: str = "İşlem devam ediyor..."):
        """Belirsiz mod"""
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        self.status_label.configure(text=status)
    
    def stop_indeterminate(self):
        """Belirsiz modu durdur"""
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")


# ============================================================================
# STAT CARD COMPONENT
# ============================================================================

class StatCard(ctk.CTkFrame):
    """İstatistik kartı"""
    
    def __init__(
        self,
        master,
        title: str,
        value: str,
        icon: str = "",
        accent_color: str = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLORS['bg_card'],
            corner_radius=SIZES['corner_radius'],
            border_width=1,
            border_color=COLORS['border'],
            **kwargs
        )
        
        accent = accent_color or COLORS['primary']
        
        # İkon
        if icon:
            icon_label = ctk.CTkLabel(
                self,
                text=icon,
                font=ctk.CTkFont(size=32),
                text_color=accent
            )
            icon_label.pack(pady=(SIZES['padding_large'], SIZES['padding_small']))
        
        # Değer
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(family=FONTS['subtitle'][0], size=FONTS['subtitle'][1], weight='bold'),
            text_color=accent
        )
        self.value_label.pack(pady=(SIZES['padding_small'], 0))
        
        # Başlık
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(family=FONTS['small'][0], size=FONTS['small'][1]),
            text_color=COLORS['text_secondary']
        )
        title_label.pack(pady=(0, SIZES['padding_large']))
    
    def set_value(self, value: str):
        """Değeri güncelle"""
        self.value_label.configure(text=value)


# ============================================================================
# MESSAGE DIALOGS
# ============================================================================

def show_success(title: str, message: str):
    """Başarı mesajı göster"""
    messagebox.showinfo(title, message)

def show_error(title: str, message: str):
    """Hata mesajı göster"""
    messagebox.showerror(title, message)

def show_warning(title: str, message: str):
    """Uyarı mesajı göster"""
    messagebox.showwarning(title, message)

def show_info(title: str, message: str):
    """Bilgi mesajı göster"""
    messagebox.showinfo(title, message)

def ask_yes_no(title: str, message: str) -> bool:
    """Evet/Hayır sorusu"""
    return messagebox.askyesno(title, message)

def ask_ok_cancel(title: str, message: str) -> bool:
    """Tamam/İptal sorusu"""
    return messagebox.askokcancel(title, message)


# ============================================================================
# SCROLLABLE FRAME
# ============================================================================

class ScrollableFrame(ctk.CTkScrollableFrame):
    """Kaydırılabilir frame"""
    
    def __init__(self, master, **kwargs):
        default_kwargs = {
            'fg_color': "transparent",
            'corner_radius': 0
        }
        default_kwargs.update(kwargs)
        super().__init__(master, **default_kwargs)


# ============================================================================
# TAB VIEW
# ============================================================================

class ModernTabView(ctk.CTkTabview):
    """Modern sekme görünümü"""
    
    def __init__(self, master, module_name: str = None, **kwargs):
        accent = COLORS['primary']
        if module_name and module_name in MODULE_COLORS:
            accent = MODULE_COLORS[module_name]['accent']
        
        default_kwargs = {
            'fg_color': COLORS['bg_card'],
            'segmented_button_fg_color': COLORS['border'],
            'segmented_button_selected_color': accent,
            'segmented_button_selected_hover_color': darken_color(accent, 0.1),
            'segmented_button_unselected_color': COLORS['bg_card'],
            'segmented_button_unselected_hover_color': COLORS['hover_light'],
            'corner_radius': SIZES['corner_radius_large'],
            'border_width': 1,
            'border_color': COLORS['border']
        }
        default_kwargs.update(kwargs)
        
        super().__init__(master, **default_kwargs)


# ============================================================================
# TOOLTIP
# ============================================================================

class ToolTip:
    """Tooltip sınıfı"""
    
    def __init__(self, widget, text: str, delay: int = 500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.after_id = None
        
        self.widget.bind("<Enter>", self._schedule_show)
        self.widget.bind("<Leave>", self._hide)
        self.widget.bind("<Button>", self._hide)
    
    def _schedule_show(self, event=None):
        self.after_id = self.widget.after(self.delay, self._show)
    
    def _show(self):
        if self.tooltip_window:
            return
        
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="#FFFFD0",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
            padx=5,
            pady=2
        )
        label.pack()
    
    def _hide(self, event=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def add_tooltip(widget, text: str) -> ToolTip:
    """Widget'a tooltip ekle"""
    return ToolTip(widget, text)
