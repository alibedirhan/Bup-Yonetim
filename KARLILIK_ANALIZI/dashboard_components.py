# dashboard_components.py - Dashboard UI Bileşenleri - Refactored Versiyon

import tkinter as tk
from tkinter import ttk
import pandas as pd

# Frozen mode için import düzeltmesi
try:
    from .ui_components import UIComponents
    from .themes import get_colors, get_color
    from .data_operations import DataCleaner, DataAnalyzer
except ImportError:
    try:
        from KARLILIK_ANALIZI.ui_components import UIComponents
        from KARLILIK_ANALIZI.themes import get_colors, get_color
        from KARLILIK_ANALIZI.data_operations import DataCleaner, DataAnalyzer
    except ImportError:
        from ui_components import UIComponents
        from themes import get_colors, get_color
        from data_operations import DataCleaner, DataAnalyzer


class DashboardComponents:
    """Dashboard'a özel UI bileşenlerini içeren sınıf"""
    
    # Backward compatibility için renk paleti - artık themes.py'den alınıyor
    @property
    def COLORS(self):
        """Dinamik renk paleti - themes.py'den alır"""
        return get_colors()
    
    @staticmethod
    def create_shadow_effect(parent, widget, offset=2):
        """Soft shadow efekti oluştur - ui_components.py delegasyonu"""
        try:
            return UIComponents.create_shadow_effect(parent, widget, offset, get_color('shadow'))
        except Exception:
            return None
    
    @staticmethod
    def create_modern_kpi_card(parent, icon, title, value, color, column):
        """Modern KPI kartı - Soft tasarım"""
        if not parent:
            return
            
        colors = get_colors()
        
        try:
            # Ana card container
            card_container = tk.Frame(parent, bg=colors['bg_primary'])
            card_container.grid(row=0, column=column, padx=12, pady=8, sticky='ew')
            
            # Card frame
            card_frame = tk.Frame(card_container, bg=colors['bg_secondary'], relief='flat')
            card_frame.pack(fill='both', expand=True)
            
            # İç padding frame
            inner_frame = tk.Frame(card_frame, bg=colors['bg_secondary'])
            inner_frame.pack(fill='both', expand=True, padx=24, pady=20)
            
            # Icon container
            icon_container = tk.Frame(inner_frame, bg=color, width=50, height=50)
            icon_container.pack(anchor='w')
            icon_container.pack_propagate(False)
            
            # Icon
            icon_label = tk.Label(
                icon_container,
                text=str(icon),
                font=('Segoe UI', 18),
                fg='white',
                bg=color
            )
            icon_label.place(relx=0.5, rely=0.5, anchor='center')
            
            # Title
            title_label = tk.Label(
                inner_frame,
                text=str(title),
                font=('Segoe UI', 11, 'bold'),
                fg=colors['text_secondary'],
                bg=colors['bg_secondary']
            )
            title_label.pack(anchor='w', pady=(15, 5))
            
            # Value
            value_label = tk.Label(
                inner_frame,
                text=str(value),
                font=('Segoe UI', 16, 'bold'),
                fg=colors['text_primary'],
                bg=colors['bg_secondary']
            )
            value_label.pack(anchor='w')
            
            # Soft shadow efekti
            DashboardComponents.create_shadow_effect(card_container, card_frame, 3)
            
            # Hover efekti - Güvenli
            def create_hover_effect():
                def on_enter(e):
                    try:
                        if card_frame.winfo_exists():
                            card_frame.config(bg='#f1f5f9')
                            inner_frame.config(bg='#f1f5f9')
                            title_label.config(bg='#f1f5f9')
                            value_label.config(bg='#f1f5f9')
                    except tk.TclError:
                        pass
                
                def on_leave(e):
                    try:
                        if card_frame.winfo_exists():
                            card_frame.config(bg=colors['bg_secondary'])
                            inner_frame.config(bg=colors['bg_secondary'])
                            title_label.config(bg=colors['bg_secondary'])
                            value_label.config(bg=colors['bg_secondary'])
                    except tk.TclError:
                        pass
                
                widgets = [card_frame, inner_frame, title_label, value_label]
                for widget in widgets:
                    try:
                        if widget.winfo_exists():
                            widget.bind("<Enter>", on_enter)
                            widget.bind("<Leave>", on_leave)
                    except tk.TclError:
                        pass
            
            create_hover_effect()
            
        except Exception as e:
            print(f"KPI card oluşturma hatası: {e}")
    
    @staticmethod
    def create_section_title(parent, title, subtitle=None):
        """Modern section başlığı - ui_components.py delegasyonu"""
        try:
            return UIComponents.create_section_header(parent, title, subtitle)
        except Exception as e:
            print(f"Section title oluşturma hatası: {e}")
    
    @staticmethod
    def create_profit_card(parent, icon, title, value, color, column):
        """Modern kar kartı"""
        if not parent:
            return
            
        colors = get_colors()
        
        try:
            # Card container
            card_container = tk.Frame(parent, bg=colors['bg_secondary'])
            card_container.grid(row=0, column=column, padx=12, pady=8, sticky='ew')
            
            # Card frame
            card_frame = tk.Frame(card_container, bg=color, relief='flat')
            card_frame.pack(fill='both', expand=True)
            
            # İç container
            inner_frame = tk.Frame(card_frame, bg=color)
            inner_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Icon
            icon_label = tk.Label(
                inner_frame,
                text=str(icon),
                font=('Segoe UI', 24),
                fg='white',
                bg=color
            )
            icon_label.pack()
            
            # Title
            title_label = tk.Label(
                inner_frame,
                text=str(title),
                font=('Segoe UI', 11, 'bold'),
                fg='white',
                bg=color
            )
            title_label.pack(pady=(8, 5))
            
            # Value - Güvenli formatlama
            try:
                value_int = int(value) if value else 0
                value_text = f"{value_int} ürün"
            except (ValueError, TypeError):
                value_text = f"{value} ürün"
                
            value_label = tk.Label(
                inner_frame,
                text=value_text,
                font=('Segoe UI', 16, 'bold'),
                fg='white',
                bg=color
            )
            value_label.pack()
            
            # Shadow efekti
            DashboardComponents.create_shadow_effect(card_container, card_frame, 3)
            
        except Exception as e:
            print(f"Profit card oluşturma hatası: {e}")
    
    @staticmethod
    def create_modern_product_list(parent, df, value_column, color, analiz=None):
        """Modern ürün listesi - data_operations.py ile entegre"""
        if not parent:
            return
            
        colors = get_colors()
        
        try:
            if df is None or df.empty:
                no_data_frame = tk.Frame(parent, bg=colors['bg_secondary'])
                no_data_frame.pack(fill='both', expand=True, padx=30, pady=30)
                
                tk.Label(
                    no_data_frame,
                    text="📋 Gösterilecek veri bulunamadı",
                    font=('Segoe UI', 12),
                    fg=colors['text_secondary'],
                    bg=colors['bg_secondary']
                ).pack(expand=True)
                return
            
            # Liste container
            list_container = tk.Frame(parent, bg=colors['bg_secondary'])
            list_container.pack(fill='both', expand=True, padx=15, pady=(0, 15))
            
            # Scrollable list - ui_components.py kullan
            canvas, scrollable_frame, scrollbar = UIComponents.create_scrollable_frame(
                list_container, colors, setup_mouse_wheel=True
            )
            
            # Stok sütunu bul - data_operations.py kullan
            stok_col = None
            try:
                if analiz and hasattr(analiz, 'find_stok_column'):
                    stok_col = analiz.find_stok_column()
                    
                if not stok_col or stok_col not in df.columns:
                    # DataAnalyzer kullanarak bul
                    stok_patterns = ['stok ismi', 'stok isim', 'stok kodu', 'ürün adı', 'urun adi']
                    stok_col = DataAnalyzer.find_column_by_pattern(df, stok_patterns)
                    
                if not stok_col and len(df.columns) > 0:
                    stok_col = df.columns[0]
                        
            except Exception as e:
                print(f"Stok sütunu bulma hatası: {e}")
                stok_col = df.columns[0] if len(df.columns) > 0 else None
            
            if not stok_col or not value_column or value_column not in df.columns:
                error_label = tk.Label(
                    scrollable_frame, 
                    text="Sütun bilgisi bulunamadı", 
                    bg=colors['bg_secondary'],
                    fg=colors['text_secondary']
                )
                error_label.pack(pady=20)
                return
            
            # Liste öğeleri - Güvenli (maksimum 8 öğe)
            try:
                df_limited = df.head(8)
                for i, (idx, row) in enumerate(df_limited.iterrows(), 1):
                    # Item container
                    item_container = tk.Frame(scrollable_frame, bg=colors['bg_secondary'])
                    item_container.pack(fill='x', pady=2, padx=3)
                    
                    # Item frame
                    item_frame = tk.Frame(item_container, bg=colors['bg_secondary'], relief='flat')
                    item_frame.pack(fill='x')
                    
                    # İç container
                    inner_item = tk.Frame(item_frame, bg=colors['bg_secondary'])
                    inner_item.pack(fill='x', padx=15, pady=8)
                    
                    # Rank container
                    rank_container = tk.Frame(inner_item, bg=color, width=30, height=30)
                    rank_container.pack(side='left')
                    rank_container.pack_propagate(False)
                    
                    # Rank number
                    rank_label = tk.Label(
                        rank_container,
                        text=str(i),
                        font=('Segoe UI', 10, 'bold'),
                        fg='white',
                        bg=color
                    )
                    rank_label.place(relx=0.5, rely=0.5, anchor='center')
                    
                    # Ürün bilgileri
                    info_frame = tk.Frame(inner_item, bg=colors['bg_secondary'])
                    info_frame.pack(side='left', fill='x', expand=True, padx=(12, 0))
                    
                    # Ürün adı - Güvenli
                    try:
                        product_name = str(row[stok_col]) if pd.notna(row[stok_col]) else "Bilinmiyor"
                        if len(product_name) > 30:
                            product_name = product_name[:30] + "..."
                    except (KeyError, TypeError):
                        product_name = "Veri Hatası"
                    
                    name_label = tk.Label(
                        info_frame,
                        text=product_name,
                        font=('Segoe UI', 10, 'bold'),
                        fg=colors['text_primary'],
                        bg=colors['bg_secondary'],
                        anchor='w'
                    )
                    name_label.pack(fill='x')
                    
                    # Değer bilgisi - data_operations.py kullan
                    try:
                        value = row[value_column]
                        if pd.notna(value):
                            if 'Kar' in value_column:
                                value_num = DataCleaner.clean_numeric(value)
                                value_text = f"₺{value_num:,.2f}"
                                value_color = colors['success'] if value_num >= 0 else colors['danger']
                            else:
                                value_num = DataCleaner.clean_numeric(value)
                                value_text = f"{value_num:,.0f} adet"
                                value_color = color
                        else:
                            value_text = "N/A"
                            value_color = colors['text_light']
                    except (ValueError, TypeError, KeyError):
                        value_text = "N/A"
                        value_color = colors['text_light']
                    
                    value_label = tk.Label(
                        info_frame,
                        text=value_text,
                        font=('Segoe UI', 9),
                        fg=value_color,
                        bg=colors['bg_secondary'],
                        anchor='w'
                    )
                    value_label.pack(fill='x', pady=(2, 0))
                    
                    # Shadow efekti
                    DashboardComponents.create_shadow_effect(item_container, item_frame, 1)
                    
                    # Hover efekti - UIComponents delegasyonu
                    def create_hover_handlers(widgets_to_hover):
                        def on_enter(e):
                            try:
                                for widget in widgets_to_hover:
                                    if widget.winfo_exists():
                                        widget.config(bg=colors['bg_hover'])
                            except tk.TclError:
                                pass
                        
                        def on_leave(e):
                            try:
                                for widget in widgets_to_hover:
                                    if widget.winfo_exists():
                                        widget.config(bg=colors['bg_secondary'])
                            except tk.TclError:
                                pass
                        
                        return on_enter, on_leave
                    
                    hover_widgets = [item_frame, inner_item, info_frame, name_label, value_label]
                    on_enter_func, on_leave_func = create_hover_handlers(hover_widgets)
                    
                    try:
                        item_frame.bind("<Enter>", on_enter_func)
                        item_frame.bind("<Leave>", on_leave_func)
                    except tk.TclError:
                        pass
                        
            except Exception as e:
                print(f"Liste oluşturma hatası: {e}")
                error_label = tk.Label(
                    scrollable_frame, 
                    text=f"Liste oluşturma hatası: {str(e)}", 
                    bg=colors['bg_secondary'],
                    fg=colors['danger']
                )
                error_label.pack(pady=20)
            
        except Exception as e:
            print(f"Product list oluşturma hatası: {e}")
    
    @staticmethod
    def display_search_results(parent, results, analiz=None):
        """Modern sonuç tablosu - data_operations.py ile entegre"""
        if not parent:
            return
            
        colors = get_colors()
        
        try:
            if results is None or results.empty:
                tk.Label(
                    parent,
                    text="Sonuç bulunamadı",
                    font=('Segoe UI', 12),
                    fg=colors['danger'],
                    bg=colors['bg_secondary']
                ).pack(pady=10)
                return
                
            # Tablo container
            table_container = tk.Frame(parent, bg=colors['bg_secondary'])
            table_container.pack(fill='both', expand=True, pady=10)
            
            # Tablo frame
            table_frame = tk.Frame(table_container, bg=colors['bg_secondary'], relief='flat')
            table_frame.pack(fill='both', expand=True)
            
            # Shadow efekti
            DashboardComponents.create_shadow_effect(table_container, table_frame, 3)
            
            # Tablo header
            table_header = tk.Frame(table_frame, bg=colors['primary'], height=50)
            table_header.pack(fill='x')
            table_header.pack_propagate(False)
            
            tk.Label(
                table_header,
                text="📊 Sonuç Tablosu",
                font=('Segoe UI', 14, 'bold'),
                fg='white',
                bg=colors['primary']
            ).pack(expand=True)
            
            # Canvas ve scrollbar - ui_components.py kullan
            canvas_frame = tk.Frame(table_frame, bg=colors['bg_secondary'])
            canvas_frame.pack(fill='both', expand=True, padx=15, pady=15)
            
            table_canvas, table_scrollable_frame, table_scrollbar = UIComponents.create_scrollable_frame(
                canvas_frame, colors, setup_mouse_wheel=True
            )
            
            # Başlık satırı
            header_row = tk.Frame(table_scrollable_frame, bg=colors['primary'])
            header_row.pack(fill='x', pady=(0, 5))
            
            headers = ['#', 'Ürün Adı', 'Net Kar', 'Birim Kar', 'Miktar', 'Ort. Satış Fiyatı', 'Fiyat']
            header_widths = [50, 250, 100, 100, 80, 120, 100]
            
            # Grid sistemi ile sabit sütunlar
            for i in range(len(headers)):
                header_row.grid_columnconfigure(i, weight=0, minsize=header_widths[i])
            
            for i, header in enumerate(headers):
                header_label = tk.Label(
                    header_row,
                    text=header,
                    font=('Segoe UI', 10, 'bold'),
                    fg='white',
                    bg=colors['primary'],
                    anchor='center',
                    justify='center',
                    width=header_widths[i]//8
                )
                header_label.grid(row=0, column=i, sticky='ew', padx=1, pady=6, ipadx=5)
            
            # Sütun bilgilerini bul - data_operations.py kullan
            stok_col = None
            miktar_col = None
            
            try:
                if analiz and hasattr(analiz, 'find_stok_column'):
                    stok_col = analiz.find_stok_column()
                if analiz and hasattr(analiz, 'find_miktar_column'):
                    miktar_col = analiz.find_miktar_column()
                
                if not stok_col:
                    stok_patterns = ['stok ismi', 'stok isim', 'ürün adı', 'urun adi']
                    stok_col = DataAnalyzer.find_column_by_pattern(results, stok_patterns)
                    if not stok_col and len(results.columns) > 0:
                        stok_col = results.columns[0]
                        
                if not miktar_col:
                    miktar_patterns = ['miktar', 'satis miktar', 'satış miktar']
                    miktar_col = DataAnalyzer.find_column_by_pattern(results, miktar_patterns)
                            
            except Exception as e:
                print(f"Sütun bulma hatası: {e}")
                stok_col = results.columns[0] if len(results.columns) > 0 else None
                miktar_col = None
            
            # Veri satırları - Güvenli (maksimum 20 satır)
            try:
                limited_results = results.head(20)
                for idx, (_, row) in enumerate(limited_results.iterrows()):
                    row_bg = colors['bg_secondary'] if idx % 2 == 0 else colors.get('bg_hover', '#f8fafc')
                    
                    data_row = tk.Frame(table_scrollable_frame, bg=row_bg)
                    data_row.pack(fill='x', pady=1)
                    
                    # Grid konfigürasyonu
                    for i in range(len(headers)):
                        data_row.grid_columnconfigure(i, weight=0, minsize=header_widths[i])
                    
                    # Sıra numarası
                    sira_label = tk.Label(
                        data_row,
                        text=str(idx + 1),
                        font=('Segoe UI', 10),
                        fg=colors['text_primary'],
                        bg=row_bg,
                        anchor='center',
                        width=header_widths[0]//8
                    )
                    sira_label.grid(row=0, column=0, sticky='ew', padx=1, pady=3, ipadx=5)
                    
                    # Ürün adı - Güvenli
                    try:
                        if stok_col and stok_col in row.index:
                            product_name = str(row[stok_col]) if pd.notna(row[stok_col]) else "Bilinmiyor"
                        else:
                            product_name = "Veri Yok"
                        
                        max_chars = 28
                        if len(product_name) > max_chars:
                            product_name = product_name[:max_chars-3] + "..."
                            
                    except (KeyError, TypeError):
                        product_name = "Hata"
                        
                    urun_label = tk.Label(
                        data_row,
                        text=product_name,
                        font=('Segoe UI', 10),
                        fg=colors['text_primary'],
                        bg=row_bg,
                        anchor='w',
                        width=header_widths[1]//8
                    )
                    urun_label.grid(row=0, column=1, sticky='ew', padx=1, pady=3, ipadx=5)
                    
                    # Net kar - data_operations.py kullan
                    try:
                        net_kar = row.get('Net Kar', 0)
                        if pd.notna(net_kar) and str(net_kar) != '':
                            net_kar_value = DataCleaner.clean_numeric(net_kar)
                            if abs(net_kar_value) >= 1000:
                                net_kar_text = f"₺{net_kar_value/1000:.1f}K"
                            else:
                                net_kar_text = f"₺{net_kar_value:.0f}"
                            net_kar_color = colors['success'] if net_kar_value >= 0 else colors['danger']
                        else:
                            net_kar_text = "N/A"
                            net_kar_color = colors['text_light']
                    except (ValueError, TypeError, KeyError):
                        net_kar_text = "N/A"
                        net_kar_color = colors['text_light']
                    
                    netkar_label = tk.Label(
                        data_row,
                        text=net_kar_text,
                        font=('Segoe UI', 10, 'bold'),
                        fg=net_kar_color,
                        bg=row_bg,
                        anchor='center',
                        width=header_widths[2]//8
                    )
                    netkar_label.grid(row=0, column=2, sticky='ew', padx=1, pady=3, ipadx=5)
                    
                    # Birim kar - data_operations.py kullan
                    try:
                        birim_kar = row.get('Birim Kar', 0)
                        if pd.notna(birim_kar) and str(birim_kar) != '':
                            birim_kar_value = DataCleaner.clean_numeric(birim_kar)
                            if abs(birim_kar_value) >= 100:
                                birim_kar_text = f"₺{birim_kar_value:.0f}"
                            else:
                                birim_kar_text = f"₺{birim_kar_value:.1f}"
                            birim_kar_color = colors['success'] if birim_kar_value >= 0 else colors['danger']
                        else:
                            birim_kar_text = "N/A"
                            birim_kar_color = colors['text_light']
                    except (ValueError, TypeError, KeyError):
                        birim_kar_text = "N/A"
                        birim_kar_color = colors['text_light']
                    
                    birimkar_label = tk.Label(
                        data_row,
                        text=birim_kar_text,
                        font=('Segoe UI', 10),
                        fg=birim_kar_color,
                        bg=row_bg,
                        anchor='center',
                        width=header_widths[3]//8
                    )
                    birimkar_label.grid(row=0, column=3, sticky='ew', padx=1, pady=3, ipadx=5)
                    
                    # Miktar - data_operations.py kullan
                    try:
                        if miktar_col and miktar_col in row.index:
                            miktar = row[miktar_col]
                            if pd.notna(miktar) and str(miktar) != '':
                                miktar_value = DataCleaner.clean_numeric(miktar)
                                if miktar_value >= 1000:
                                    miktar_text = f"{miktar_value/1000:.1f}K"
                                else:
                                    miktar_text = f"{miktar_value:.0f}"
                            else:
                                miktar_text = "N/A"
                        else:
                            miktar_text = "N/A"
                    except (ValueError, TypeError, KeyError):
                        miktar_text = "N/A"
                        
                    miktar_label = tk.Label(
                        data_row,
                        text=miktar_text,
                        font=('Segoe UI', 10),
                        fg=colors['info'],
                        bg=row_bg,
                        anchor='center',
                        width=header_widths[4]//8
                    )
                    miktar_label.grid(row=0, column=4, sticky='ew', padx=1, pady=3, ipadx=5)
                    
                    # Ort. Satış Fiyatı - data_operations.py kullan
                    try:
                        ort_satis_fiyat = None
                        possible_columns = ['Ort.Satış Fiyat', 'Ort.Satış\nFiyat', 'Ort Satış Fiyat', 'Ortalama Satış Fiyat']
                        
                        for col in possible_columns:
                            if col in row.index:
                                ort_satis_fiyat = row[col]
                                break
                        
                        if ort_satis_fiyat is not None and pd.notna(ort_satis_fiyat) and str(ort_satis_fiyat) != '':
                            fiyat_value = DataCleaner.clean_numeric(ort_satis_fiyat)
                            if fiyat_value >= 1000:
                                ort_satis_text = f"₺{fiyat_value:,.0f}"
                            else:
                                ort_satis_text = f"₺{fiyat_value:.2f}"
                            ort_satis_color = colors['success']
                        else:
                            ort_satis_text = "Bilgi yok"
                            ort_satis_color = colors['text_light']
                            
                    except (ValueError, TypeError, KeyError):
                        ort_satis_text = "Bilgi yok"
                        ort_satis_color = colors['text_light']
                    
                    ort_satis_label = tk.Label(
                        data_row,
                        text=ort_satis_text,
                        font=('Segoe UI', 10, 'bold'),
                        fg=ort_satis_color,
                        bg=row_bg,
                        anchor='center',
                        width=header_widths[5]//8
                    )
                    ort_satis_label.grid(row=0, column=5, sticky='ew', padx=1, pady=3, ipadx=5)
                    
                    # Fiyat (Birim Maliyet) - data_operations.py kullan
                    try:
                        birim_maliyet = row.get('Birim Maliyet', None)
                        
                        if pd.notna(birim_maliyet) and str(birim_maliyet) != '' and DataCleaner.clean_numeric(birim_maliyet) > 0:
                            fiyat_value = DataCleaner.clean_numeric(birim_maliyet)
                            if fiyat_value >= 1000:
                                fiyat_text = f"₺{fiyat_value:,.0f}"
                            else:
                                fiyat_text = f"₺{fiyat_value:.2f}"
                            fiyat_color = colors['primary']
                        else:
                            fiyat_text = "N/A"
                            fiyat_color = colors['text_light']
                                
                    except (ValueError, TypeError, KeyError):
                        fiyat_text = "N/A"
                        fiyat_color = colors['text_light']
                    
                    fiyat_label = tk.Label(
                        data_row,
                        text=fiyat_text,
                        font=('Segoe UI', 10, 'bold'),
                        fg=fiyat_color,
                        bg=row_bg,
                        anchor='center',
                        width=header_widths[6]//8
                    )
                    fiyat_label.grid(row=0, column=6, sticky='ew', padx=1, pady=3, ipadx=5)
                    
                    # Hover efekti - UIComponents delegasyonu
                    def create_row_hover(widgets_list, original_bg):
                        def on_enter(e):
                            try:
                                hover_color = colors.get('bg_hover', '#e2e8f0')
                                data_row.config(bg=hover_color)
                                for widget in widgets_list:
                                    if widget.winfo_exists():
                                        widget.config(bg=hover_color)
                            except tk.TclError:
                                pass
                        
                        def on_leave(e):
                            try:
                                data_row.config(bg=original_bg)
                                for widget in widgets_list:
                                    if widget.winfo_exists():
                                        widget.config(bg=original_bg)
                            except tk.TclError:
                                pass
                        
                        return on_enter, on_leave
                    
                    row_widgets = [sira_label, urun_label, netkar_label, birimkar_label, 
                                  miktar_label, ort_satis_label, fiyat_label]
                    on_enter_row, on_leave_row = create_row_hover(row_widgets, row_bg)
                    
                    try:
                        data_row.bind("<Enter>", on_enter_row)
                        data_row.bind("<Leave>", on_leave_row)
                    except tk.TclError:
                        pass
                        
            except Exception as e:
                print(f"Tablo satır oluşturma hatası: {e}")
                error_label = tk.Label(
                    table_scrollable_frame, 
                    text=f"Tablo oluşturma hatası: {str(e)}", 
                    bg=colors['bg_secondary'],
                    fg=colors['danger']
                )
                error_label.pack(pady=20)
            
            # Sonuç sayısı bilgisi
            if len(results) > 20:
                info_container = tk.Frame(parent, bg=colors['bg_secondary'])
                info_container.pack(fill='x', pady=15)
                
                info_frame = tk.Frame(info_container, bg='#f0f9ff', relief='flat')
                info_frame.pack(fill='x')
                
                tk.Label(
                    info_frame,
                    text=f"📄 İlk 20 sonuç gösteriliyor. Toplam {len(results)} sonuç bulundu.",
                    font=('Segoe UI', 11),
                    fg=colors['info'],
                    bg='#f0f9ff'
                ).pack(pady=12)
                
                DashboardComponents.create_shadow_effect(info_container, info_frame, 2)
                
        except Exception as e:
            print(f"Search results display hatası: {e}")
    
    @staticmethod
    def show_initial_search_message(parent):
        """Başlangıç arama mesajı - ui_components.py delegasyonu"""
        if not parent:
            return
            
        colors = get_colors()
        
        try:
            msg_container = tk.Frame(parent, bg=colors['bg_secondary'])
            msg_container.pack(fill='x', pady=20)
            
            msg_frame = tk.Frame(msg_container, bg='#f0f9ff', relief='flat')
            msg_frame.pack(fill='x')
            
            tk.Label(
                msg_frame,
                text="💡 Arama yapmak için yukarıdaki kutucuğa ürün adını yazın veya hızlı filtreleri kullanın",
                font=('Segoe UI', 12),
                fg=colors['info'],
                bg='#f0f9ff'
            ).pack(pady=20)
            
            # Shadow efekti
            DashboardComponents.create_shadow_effect(msg_container, msg_frame, 2)
            
        except Exception as e:
            print(f"Initial search message hatası: {e}")
    
    @staticmethod
    def create_button_hover(button, normal_color, hover_color):
        """Buton hover efekti oluştur - ui_components.py delegasyonu"""
        try:
            UIComponents.create_button_hover_effect(button, normal_color, hover_color)
        except Exception as e:
            print(f"Button hover effect hatası: {e}")