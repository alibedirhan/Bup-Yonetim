# ui_components.py - Genel UI Bileşenleri Modülü

import tkinter as tk
from tkinter import ttk
import platform
import weakref
from typing import Optional, Callable, Dict, Any, List, Tuple


class UIComponents:
    """Genel kullanım UI bileşenleri ve yardımcı fonksiyonlar"""
    
    # Tema renkleri
    DEFAULT_COLORS = {
        'bg_primary': '#f8fafc',
        'bg_secondary': '#ffffff', 
        'bg_accent': '#e2e8f0',
        'primary': '#3b82f6',
        'primary_dark': '#2563eb',
        'success': '#10b981',
        'warning': '#f59e0b',
        'danger': '#ef4444',
        'info': '#06b6d4',
        'text_primary': '#1f2937',
        'text_secondary': '#6b7280',
        'text_light': '#9ca3af',
        'border': '#e5e7eb',
        'shadow': '#f3f4f6'
    }
    
    @staticmethod
    def create_labeled_entry(parent: tk.Widget, 
                           label_text: str, 
                           width: int = 30,
                           entry_var: Optional[tk.StringVar] = None,
                           label_font: Tuple[str, int, str] = ('Segoe UI', 11, 'bold'),
                           entry_font: Tuple[str, int] = ('Segoe UI', 11),
                           colors: Optional[Dict] = None) -> Tuple[tk.Label, tk.Entry]:
        """
        Etiketli giriş kutusu oluşturur
        
        Returns:
            Tuple[tk.Label, tk.Entry]: Label ve Entry widget'ları
        """
        if colors is None:
            colors = UIComponents.DEFAULT_COLORS
            
        try:
            # Container frame
            container = tk.Frame(parent, bg=colors['bg_secondary'])
            container.pack(fill='x', pady=5)
            
            # Label
            label = tk.Label(
                container,
                text=label_text,
                font=label_font,
                fg=colors['text_primary'],
                bg=colors['bg_secondary']
            )
            label.pack(anchor='w', pady=(0, 5))
            
            # Entry
            entry = tk.Entry(
                container,
                textvariable=entry_var,
                font=entry_font,
                width=width,
                bg='#f8fafc',
                fg=colors['text_primary'],
                relief='solid',
                bd=1,
                insertbackground=colors['primary']
            )
            entry.pack(fill='x')
            
            return label, entry
            
        except Exception as e:
            print(f"Labeled entry creation error: {e}")
            # Fallback basit entry
            simple_entry = tk.Entry(parent, width=width)
            simple_entry.pack()
            return None, simple_entry
    
    @staticmethod
    def create_progress_frame(parent: tk.Widget,
                            colors: Optional[Dict] = None) -> Tuple[tk.Frame, ttk.Progressbar, tk.Label]:
        """
        İlerleme çubuğu frame'i oluşturur
        
        Returns:
            Tuple[tk.Frame, ttk.Progressbar, tk.Label]: Frame, progressbar ve status label
        """
        if colors is None:
            colors = UIComponents.DEFAULT_COLORS
            
        try:
            # Progress container
            progress_frame = tk.Frame(parent, bg=colors['bg_secondary'])
            progress_frame.pack(fill='x', pady=10)
            
            # Progress bar
            progress_bar = ttk.Progressbar(
                progress_frame,
                mode='determinate',
                length=400
            )
            progress_bar.pack(pady=(0, 5))
            
            # Status label
            status_label = tk.Label(
                progress_frame,
                text="Hazır...",
                font=('Segoe UI', 10),
                fg=colors['text_secondary'],
                bg=colors['bg_secondary']
            )
            status_label.pack()
            
            return progress_frame, progress_bar, status_label
            
        except Exception as e:
            print(f"Progress frame creation error: {e}")
            return None, None, None
    
    @staticmethod
    def create_scrollable_frame(parent: tk.Widget,
                              colors: Optional[Dict] = None,
                              setup_mouse_wheel: bool = True) -> Tuple[tk.Canvas, tk.Frame, ttk.Scrollbar]:
        """
        Kaydırılabilir frame oluşturur
        
        Returns:
            Tuple[tk.Canvas, tk.Frame, ttk.Scrollbar]: Canvas, scrollable frame ve scrollbar
        """
        if colors is None:
            colors = UIComponents.DEFAULT_COLORS
            
        try:
            # Canvas
            canvas = tk.Canvas(
                parent,
                bg=colors['bg_primary'],
                highlightthickness=0,
                bd=0,
                relief='flat'
            )
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(
                parent,
                orient="vertical",
                command=canvas.yview
            )
            
            # Scrollable frame
            scrollable_frame = tk.Frame(canvas, bg=colors['bg_primary'])
            
            # Scroll region güncelleme fonksiyonu
            def configure_scroll_region(event=None):
                try:
                    if canvas.winfo_exists():
                        canvas.configure(scrollregion=canvas.bbox("all"))
                except tk.TclError:
                    pass
            
            # Canvas genişlik güncelleme
            def configure_canvas_width(event=None):
                try:
                    if canvas.winfo_exists():
                        canvas_width = canvas.winfo_width()
                        if canvas_width > 1:
                            canvas.itemconfig(canvas_window, width=canvas_width)
                except (tk.TclError, AttributeError):
                    pass
            
            # Event binding
            scrollable_frame.bind("<Configure>", configure_scroll_region)
            canvas.bind('<Configure>', configure_canvas_width)
            
            # Canvas window oluştur
            canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Mouse wheel setup
            if setup_mouse_wheel:
                UIComponents.setup_mouse_wheel_scroll(canvas, scrollable_frame)
            
            # Pack widgets
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            return canvas, scrollable_frame, scrollbar
            
        except Exception as e:
            print(f"Scrollable frame creation error: {e}")
            # Fallback frame
            fallback_frame = tk.Frame(parent, bg=colors.get('bg_primary', 'white'))
            fallback_frame.pack(fill='both', expand=True)
            return None, fallback_frame, None
    
    @staticmethod
    def setup_mouse_wheel_scroll(canvas: tk.Canvas, 
                               scrollable_frame: tk.Frame,
                               cleanup_functions: Optional[List] = None) -> List[Callable]:
        """
        Mouse wheel scroll kurulumu
        
        Returns:
            List[Callable]: Cleanup fonksiyonları listesi
        """
        try:
            os_platform = platform.system()
            cleanup_funcs = []
            
            def on_mouse_wheel(event):
                try:
                    if not canvas.winfo_exists():
                        return "break"
                    
                    delta = 0
                    if os_platform == "Windows":
                        delta = -1 * int(event.delta / 120)
                    elif os_platform == "Darwin":
                        delta = -1 * int(event.delta)
                    else:
                        if event.num == 4:
                            delta = -1
                        elif event.num == 5:
                            delta = 1
                        else:
                            return "break"
                    
                    canvas.yview_scroll(delta, "units")
                    return "break"
                    
                except (AttributeError, tk.TclError, ValueError, TypeError):
                    return "break"
            
            def bind_mousewheel():
                try:
                    if os_platform == "Windows":
                        canvas.bind("<MouseWheel>", on_mouse_wheel)
                        scrollable_frame.bind("<MouseWheel>", on_mouse_wheel)
                    elif os_platform == "Darwin":
                        canvas.bind("<MouseWheel>", on_mouse_wheel)
                        scrollable_frame.bind("<MouseWheel>", on_mouse_wheel)
                    else:
                        canvas.bind("<Button-4>", on_mouse_wheel)
                        canvas.bind("<Button-5>", on_mouse_wheel)
                        scrollable_frame.bind("<Button-4>", on_mouse_wheel)
                        scrollable_frame.bind("<Button-5>", on_mouse_wheel)
                except tk.TclError:
                    pass
            
            def unbind_mousewheel():
                try:
                    if os_platform in ["Windows", "Darwin"]:
                        canvas.unbind("<MouseWheel>")
                        scrollable_frame.unbind("<MouseWheel>")
                    else:
                        canvas.unbind("<Button-4>")
                        canvas.unbind("<Button-5>")
                        scrollable_frame.unbind("<Button-4>")
                        scrollable_frame.unbind("<Button-5>")
                except tk.TclError:
                    pass
            
            def on_canvas_enter(event):
                bind_mousewheel()
            
            def on_canvas_leave(event):
                unbind_mousewheel()
            
            # Mouse enter/leave events
            canvas.bind('<Enter>', on_canvas_enter)
            canvas.bind('<Leave>', on_canvas_leave)
            
            cleanup_funcs = [unbind_mousewheel]
            
            if cleanup_functions is not None:
                cleanup_functions.extend(cleanup_funcs)
            
            return cleanup_funcs
            
        except Exception as e:
            print(f"Mouse wheel setup error: {e}")
            return []
    
    @staticmethod
    def create_modern_button(parent: tk.Widget,
                           text: str,
                           command: Callable,
                           bg_color: str,
                           fg_color: str = 'white',
                           font: Tuple[str, int, str] = ('Segoe UI', 11, 'bold'),
                           padx: int = 20,
                           pady: int = 10,
                           hover_color: Optional[str] = None,
                           **kwargs) -> tk.Button:
        """
        Modern buton oluşturur
        
        Returns:
            tk.Button: Oluşturulan buton widget'ı
        """
        try:
            button = tk.Button(
                parent,
                text=text,
                command=command,
                bg=bg_color,
                fg=fg_color,
                font=font,
                relief='flat',
                bd=0,
                cursor='hand2',
                padx=padx,
                pady=pady,
                **kwargs
            )
            
            # Hover efekti ekle
            if hover_color:
                UIComponents.create_button_hover_effect(button, bg_color, hover_color)
            
            return button
            
        except Exception as e:
            print(f"Modern button creation error: {e}")
            # Fallback button
            return tk.Button(parent, text=text, command=command)
    
    @staticmethod
    def create_button_hover_effect(button: tk.Button, 
                                 normal_color: str, 
                                 hover_color: str) -> None:
        """Buton hover efekti oluşturur"""
        try:
            def on_enter(e):
                try:
                    if button.winfo_exists():
                        button.config(bg=hover_color)
                except tk.TclError:
                    pass
                    
            def on_leave(e):
                try:
                    if button.winfo_exists():
                        button.config(bg=normal_color)
                except tk.TclError:
                    pass
                    
            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)
            
        except Exception as e:
            print(f"Button hover effect error: {e}")
    
    @staticmethod
    def create_section_header(parent: tk.Widget,
                            title: str,
                            subtitle: Optional[str] = None,
                            bg_color: Optional[str] = None,
                            colors: Optional[Dict] = None) -> tk.Frame:
        """
        Bölüm başlığı oluşturur
        
        Returns:
            tk.Frame: Başlık frame'i
        """
        if colors is None:
            colors = UIComponents.DEFAULT_COLORS
        if bg_color is None:
            bg_color = colors['primary']
            
        try:
            header_frame = tk.Frame(parent, bg=bg_color, height=80)
            header_frame.pack(fill='x', pady=(0, 20))
            header_frame.pack_propagate(False)
            
            # Ana başlık
            title_label = tk.Label(
                header_frame,
                text=title,
                font=('Segoe UI', 18, 'bold'),
                fg='white',
                bg=bg_color
            )
            title_label.pack(expand=True)
            
            # Alt başlık (varsa)
            if subtitle:
                subtitle_label = tk.Label(
                    header_frame,
                    text=subtitle,
                    font=('Segoe UI', 12),
                    fg='#bfdbfe',
                    bg=bg_color
                )
                subtitle_label.pack(expand=True)
            
            return header_frame
            
        except Exception as e:
            print(f"Section header creation error: {e}")
            return tk.Frame(parent)
    
    @staticmethod
    def create_file_selector(parent: tk.Widget,
                           label_text: str,
                           file_types: List[Tuple[str, str]] = None,
                           button_color: str = None,
                           colors: Optional[Dict] = None) -> Tuple[tk.Frame, tk.Label, tk.StringVar, Callable]:
        """
        Dosya seçici widget'ı oluşturur
        
        Returns:
            Tuple[tk.Frame, tk.Label, tk.StringVar, Callable]: Container, display label, path variable, select function
        """
        if colors is None:
            colors = UIComponents.DEFAULT_COLORS
        if button_color is None:
            button_color = colors['primary']
        if file_types is None:
            file_types = [("Excel dosyaları", "*.xlsx *.xls"), ("Tüm dosyalar", "*.*")]
            
        try:
            from tkinter import filedialog
            import os
            
            # Container
            container = tk.Frame(parent, bg=colors['bg_secondary'])
            container.pack(fill='x', pady=10)
            
            # Label
            tk.Label(
                container,
                text=label_text,
                font=('Segoe UI', 11, 'bold'),
                fg=colors['text_primary'],
                bg=colors['bg_secondary']
            ).pack(anchor='w', pady=(0, 5))
            
            # File display area
            file_frame = tk.Frame(container, bg=colors['bg_secondary'])
            file_frame.pack(fill='x')
            
            # Display label
            display_label = tk.Label(
                file_frame,
                text="Henüz dosya seçilmedi...",
                font=('Segoe UI', 10),
                fg=colors['text_secondary'],
                bg='#f8f9fa',
                relief='solid',
                bd=1,
                anchor='w',
                padx=10,
                pady=8
            )
            display_label.pack(side='left', fill='x', expand=True, padx=(0, 10))
            
            # Path variable
            path_var = tk.StringVar()
            
            # Select function
            def select_file():
                try:
                    filename = filedialog.askopenfilename(
                        title=f"{label_text} Seçin",
                        filetypes=file_types
                    )
                    
                    if filename and os.path.exists(filename):
                        path_var.set(filename)
                        display_label.config(
                            text=f"✅ {os.path.basename(filename)}",
                            fg=colors['success']
                        )
                    
                except Exception as e:
                    print(f"File selection error: {e}")
            
            # Select button
            select_button = UIComponents.create_modern_button(
                file_frame,
                text="📂 Dosya Seç",
                command=select_file,
                bg_color=button_color,
                hover_color=colors.get('primary_dark', button_color)
            )
            select_button.pack(side='right')
            
            return container, display_label, path_var, select_file
            
        except Exception as e:
            print(f"File selector creation error: {e}")
            return tk.Frame(parent), None, tk.StringVar(), lambda: None
    
    @staticmethod
    def create_info_card(parent: tk.Widget,
                        icon: str,
                        title: str,
                        value: str,
                        bg_color: str,
                        colors: Optional[Dict] = None) -> tk.Frame:
        """
        Bilgi kartı oluşturur
        
        Returns:
            tk.Frame: Kart frame'i
        """
        if colors is None:
            colors = UIComponents.DEFAULT_COLORS
            
        try:
            # Card container
            card_container = tk.Frame(parent, bg=colors['bg_primary'])
            card_container.pack(side='left', fill='both', expand=True, padx=10, pady=5)
            
            # Card frame
            card_frame = tk.Frame(card_container, bg=colors['bg_secondary'], relief='flat')
            card_frame.pack(fill='both', expand=True)
            
            # İç container
            inner_frame = tk.Frame(card_frame, bg=colors['bg_secondary'])
            inner_frame.pack(fill='both', expand=True, padx=20, pady=15)
            
            # Icon container
            icon_container = tk.Frame(inner_frame, bg=bg_color, width=40, height=40)
            icon_container.pack(anchor='w')
            icon_container.pack_propagate(False)
            
            # Icon
            icon_label = tk.Label(
                icon_container,
                text=icon,
                font=('Segoe UI', 16),
                fg='white',
                bg=bg_color
            )
            icon_label.place(relx=0.5, rely=0.5, anchor='center')
            
            # Title
            title_label = tk.Label(
                inner_frame,
                text=title,
                font=('Segoe UI', 10, 'bold'),
                fg=colors['text_secondary'],
                bg=colors['bg_secondary']
            )
            title_label.pack(anchor='w', pady=(10, 5))
            
            # Value
            value_label = tk.Label(
                inner_frame,
                text=value,
                font=('Segoe UI', 14, 'bold'),
                fg=colors['text_primary'],
                bg=colors['bg_secondary']
            )
            value_label.pack(anchor='w')
            
            return card_container
            
        except Exception as e:
            print(f"Info card creation error: {e}")
            return tk.Frame(parent)
    
    @staticmethod
    def create_shadow_effect(parent: tk.Widget, 
                           widget: tk.Widget, 
                           offset: int = 2,
                           shadow_color: str = '#f3f4f6') -> Optional[tk.Frame]:
        """Gölge efekti oluşturur"""
        try:
            if not parent or not widget:
                return None
            if not parent.winfo_exists() or not widget.winfo_exists():
                return None
                
            shadow = tk.Frame(parent, bg=shadow_color, height=offset, relief='flat')
            shadow.place(in_=widget, x=offset, y=offset, relwidth=1, relheight=1)
            widget.lift()
            return shadow
            
        except tk.TclError:
            return None
        except Exception:
            return None
    
    @staticmethod
    def apply_theme(widget: tk.Widget, theme_name: str = 'default') -> None:
        """Widget'a tema uygular"""
        try:
            if theme_name == 'dark':
                dark_colors = {
                    'bg': '#2d3748',
                    'fg': '#f7fafc',
                    'select_bg': '#4a5568',
                    'select_fg': '#f7fafc'
                }
                
                if hasattr(widget, 'config'):
                    widget.config(
                        bg=dark_colors['bg'],
                        fg=dark_colors['fg']
                    )
            
        except Exception as e:
            print(f"Theme application error: {e}")


class UIValidator:
    """UI girdi doğrulama yardımcıları"""
    
    @staticmethod
    def validate_numeric_entry(entry_value: str, 
                             min_value: Optional[float] = None,
                             max_value: Optional[float] = None) -> Tuple[bool, str]:
        """
        Sayısal girdi doğrulama
        
        Returns:
            Tuple[bool, str]: (geçerli_mi, hata_mesajı)
        """
        try:
            if not entry_value.strip():
                return False, "Değer boş olamaz"
            
            value = float(entry_value)
            
            if min_value is not None and value < min_value:
                return False, f"Değer {min_value}'den küçük olamaz"
            
            if max_value is not None and value > max_value:
                return False, f"Değer {max_value}'den büyük olamaz"
            
            return True, ""
            
        except ValueError:
            return False, "Geçerli bir sayı girin"
        except Exception as e:
            return False, f"Doğrulama hatası: {e}"
    
    @staticmethod
    def validate_file_path(file_path: str, 
                          allowed_extensions: Optional[List[str]] = None) -> Tuple[bool, str]:
        """
        Dosya yolu doğrulama
        
        Returns:
            Tuple[bool, str]: (geçerli_mi, hata_mesajı)
        """
        try:
            import os
            
            if not file_path.strip():
                return False, "Dosya yolu boş olamaz"
            
            if not os.path.exists(file_path):
                return False, "Dosya bulunamadı"
            
            if not os.path.isfile(file_path):
                return False, "Seçilen yol bir dosya değil"
            
            if allowed_extensions:
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in allowed_extensions:
                    return False, f"İzin verilen uzantılar: {', '.join(allowed_extensions)}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Doğrulama hatası: {e}"
