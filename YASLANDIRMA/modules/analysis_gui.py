#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - Analiz GUI Modülü
ARAÇ analizi için kullanıcı arayüzü - Temiz versiyon
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

from tkinter import messagebox, filedialog
import tkinter.ttk as ttk
import logging
from datetime import datetime
from pathlib import Path
import threading
from typing import Dict, List, Optional

# Modül importları
from .analysis import AnalysisEngine
from .assignment import AssignmentManager
from .data_manager import DataManager
from .reports import ReportGenerator
from .visualization import VisualizationEngine
from utils import format_number_display

logger = logging.getLogger(__name__)

class AnalysisGUI:
    def __init__(self, parent, excel_processor):
        self.parent = parent
        self.excel_processor = excel_processor
        
        # Modüller
        self.analysis_engine = AnalysisEngine()
        self.assignment_manager = AssignmentManager()
        self.data_manager = DataManager()
        self.report_generator = ReportGenerator()
        self.visualization_engine = VisualizationEngine()
        
        # Veri
        self.current_analysis_results = {}
        self.current_assignments = {}
        
        # UI değişkenleri
        self.selected_arac = None
        
        # Pencereyi oluştur
        self.create_analysis_window()
    
    def create_analysis_window(self):
        """Analiz penceresini oluştur"""
        try:
            # Ana pencere
            self.window = ctk.CTkToplevel(self.parent)
            self.window.title("ARAÇ Analiz Modülü")
            self.window.geometry("1400x800")
            
            # Pencereyi modal yap
            self.window.transient(self.parent)
            self.window.grab_set()
            
            # Ana container
            main_container = ctk.CTkFrame(self.window)
            main_container.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Üst panel
            self.create_top_panel(main_container)
            
            # Notebook panel
            self.create_notebook_panel(main_container)
            
            # Durum çubuğu
            self.create_status_bar(main_container)
            
            # Pencere kapanış
            self.window.protocol("WM_DELETE_WINDOW", self.on_window_close)
            
            # Pencereyi öne getir
            self.window.lift()
            self.window.focus_force()
            
        except Exception as e:
            logger.error(f"Analiz penceresi oluşturma hatası: {e}")
            messagebox.showerror("Hata", f"Analiz penceresi oluşturulamadı: {e}")
    
    def create_top_panel(self, parent):
        """Üst kontrol paneli"""
        top_frame = ctk.CTkFrame(parent, height=80)
        top_frame.pack(fill="x", padx=5, pady=5)
        top_frame.pack_propagate(False)
        
        # Başlık
        title_label = ctk.CTkLabel(
            top_frame,
            text="🚗 ARAÇ ANALİZ SİSTEMİ",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=20)
        
        # Butonlar
        buttons_frame = ctk.CTkFrame(top_frame)
        buttons_frame.pack(side="right", padx=20, pady=10)
        
        # Analiz başlat butonu
        self.analyze_btn = ctk.CTkButton(
            buttons_frame,
            text="📊 Analiz Başlat",
            command=self.start_analysis,
            fg_color="green",
            height=40
        )
        self.analyze_btn.pack(side="left", padx=5)
        
        # Rapor butonu
        self.report_btn = ctk.CTkButton(
            buttons_frame,
            text="📋 Rapor",
            command=self.generate_reports,
            height=40
        )
        self.report_btn.pack(side="left", padx=5)
    
    def create_notebook_panel(self, parent):
        """Notebook paneli"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Genel Bakış tab'ı
        self.create_overview_tab()
        
        # ARAÇ Detay tab'ı
        self.create_detail_tab()
    
    def create_overview_tab(self):
        """Genel bakış tab'ı"""
        overview_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(overview_frame, text="📈 Genel Bakış")
        
        # Sol panel - ARAÇ listesi
        left_panel = ctk.CTkFrame(overview_frame, width=300)
        left_panel.pack(side="left", fill="y", padx=5, pady=5)
        left_panel.pack_propagate(False)
        
        ctk.CTkLabel(
            left_panel,
            text="ARAÇ Listesi",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Listbox
        self.arac_listbox = ctk.CTkTextbox(left_panel)
        self.arac_listbox.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Sağ panel - İstatistikler
        right_panel = ctk.CTkFrame(overview_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(
            right_panel,
            text="Özet İstatistikler",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # İstatistik kartları
        self.create_statistics_cards(right_panel)
    
    def create_statistics_cards(self, parent):
        """İstatistik kartları"""
        cards_frame = ctk.CTkFrame(parent)
        cards_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # İlk satır
        row1_frame = ctk.CTkFrame(cards_frame)
        row1_frame.pack(fill="x", pady=5)
        
        self.total_arac_card = self.create_stat_card(
            row1_frame, "Toplam ARAÇ", "0", "🚗"
        )
        self.total_arac_card.pack(side="left", fill="x", expand=True, padx=5)
        
        self.total_customer_card = self.create_stat_card(
            row1_frame, "Toplam Müşteri", "0", "👥"
        )
        self.total_customer_card.pack(side="left", fill="x", expand=True, padx=5)
        
        # İkinci satır
        row2_frame = ctk.CTkFrame(cards_frame)
        row2_frame.pack(fill="x", pady=5)
        
        self.total_balance_card = self.create_stat_card(
            row2_frame, "Toplam Bakiye", "0 TL", "💰"
        )
        self.total_balance_card.pack(side="left", fill="x", expand=True, padx=5)
        
        self.open_balance_card = self.create_stat_card(
            row2_frame, "Açık Hesap", "0 TL", "⚠️"
        )
        self.open_balance_card.pack(side="left", fill="x", expand=True, padx=5)
    
    def create_stat_card(self, parent, title, value, icon):
        """İstatistik kartı"""
        card = ctk.CTkFrame(parent, corner_radius=10)
        
        # Icon
        icon_label = ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=24))
        icon_label.pack(pady=(10, 5))
        
        # Başlık
        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold"))
        title_label.pack(pady=2)
        
        # Değer
        value_label = ctk.CTkLabel(
            card, 
            text=value, 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("green", "light green")
        )
        value_label.pack(pady=(2, 10))
        
        # Değer label'ını kart ile ilişkilendir
        card.value_label = value_label
        
        return card
    
    def create_detail_tab(self):
        """ARAÇ detay tab'ı"""
        detail_frame = ctk.CTkFrame(self.notebook)
        self.notebook.add(detail_frame, text="🚗 ARAÇ Detayı")
        
        # Üst panel - ARAÇ seçimi
        top_frame = ctk.CTkFrame(detail_frame, height=60)
        top_frame.pack(fill="x", padx=5, pady=5)
        top_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            top_frame,
            text="ARAÇ Seçin:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=20, pady=20)
        
        # ARAÇ dropdown
        self.arac_dropdown = ctk.CTkComboBox(
            top_frame,
            values=["ARAÇ seçin..."],
            command=self.on_arac_selected,
            width=200
        )
        self.arac_dropdown.pack(side="left", padx=10, pady=20)
        
        # Ana içerik
        content_frame = ctk.CTkFrame(detail_frame)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ARAÇ bilgi paneli
        info_frame = ctk.CTkFrame(content_frame, width=400)
        info_frame.pack(side="left", fill="y", padx=5, pady=5)
        info_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            info_frame,
            text="ARAÇ Bilgileri",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        self.arac_info_text = ctk.CTkTextbox(info_frame)
        self.arac_info_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Müşteri listesi paneli
        customer_frame = ctk.CTkFrame(content_frame)
        customer_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(
            customer_frame,
            text="Müşteri Detayları",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # Treeview
        tree_frame = ctk.CTkFrame(customer_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.customer_tree = ttk.Treeview(tree_frame)
        self.customer_tree.pack(fill="both", expand=True)
    
    def create_status_bar(self, parent):
        """Durum çubuğu"""
        status_frame = ctk.CTkFrame(parent, height=30)
        status_frame.pack(fill="x", side="bottom", padx=5, pady=5)
        status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Hazır",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(status_frame, width=200)
        self.progress_bar.pack(side="right", padx=10, pady=5)
        self.progress_bar.set(0)
    
    def start_analysis(self):
        """Analizi başlat"""
        try:
            if self.excel_processor.processed_df is None:
                messagebox.showerror("Hata", "Önce Excel verisi işlenmelidir!")
                return
            
            self.status_label.configure(text="Analiz başlatılıyor...")
            self.progress_bar.set(0.1)
            self.analyze_btn.configure(state="disabled")
            
            def analysis_thread():
                try:
                    # Veriyi analiz motoruna aktar
                    if not self.analysis_engine.set_data(self.excel_processor.processed_df):
                        raise Exception("Analiz verisi ayarlanamadı")
                    
                    self.window.after(0, lambda: self.progress_bar.set(0.3))
                    self.window.after(0, lambda: self.status_label.configure(text="ARAÇ analizi yapılıyor..."))
                    
                    # Tüm ARAÇ'ları analiz et
                    self.current_analysis_results = self.analysis_engine.analyze_all_aracs()
                    
                    if not self.current_analysis_results:
                        raise Exception("Analiz sonucu alınamadı")
                    
                    self.window.after(0, lambda: self.progress_bar.set(0.8))
                    self.window.after(0, lambda: self.status_label.configure(text="Sonuçlar güncelleniyor..."))
                    
                    # UI'yi güncelle
                    self.window.after(0, self.update_analysis_results)
                    
                    self.window.after(0, lambda: self.progress_bar.set(1.0))
                    self.window.after(0, lambda: self.status_label.configure(text="Analiz tamamlandı"))
                    self.window.after(0, lambda: self.analyze_btn.configure(state="normal"))
                    
                except Exception as e:
                    self.window.after(0, lambda: messagebox.showerror("Analiz Hatası", str(e)))
                    self.window.after(0, lambda: self.status_label.configure(text="Analiz hatası"))
                    self.window.after(0, lambda: self.progress_bar.set(0))
                    self.window.after(0, lambda: self.analyze_btn.configure(state="normal"))
            
            # Thread'i başlat
            thread = threading.Thread(target=analysis_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error(f"Analiz başlatma hatası: {e}")
            messagebox.showerror("Hata", f"Analiz başlatılamadı: {e}")
            self.analyze_btn.configure(state="normal")
    
    def update_analysis_results(self):
        """Analiz sonuçlarını UI'de güncelle"""
        try:
            # İstatistik kartlarını güncelle
            self.update_statistics_cards()
            
            # ARAÇ listbox'ını güncelle
            self.update_arac_listbox()
            
            # ARAÇ dropdown'ını güncelle
            self.refresh_arac_list()
            
            logger.info("Analiz sonuçları UI'de güncellendi")
            
        except Exception as e:
            logger.error(f"UI güncelleme hatası: {e}")
    
    def update_statistics_cards(self):
        """İstatistik kartlarını güncelle"""
        try:
            if not self.current_analysis_results:
                return
            
            # Özet istatistikleri hesapla
            summary = self.analysis_engine.get_summary_statistics()
            
            # Kartları güncelle
            self.total_arac_card.value_label.configure(text=str(summary.get('toplam_arac_sayisi', 0)))
            self.total_customer_card.value_label.configure(text=str(summary.get('toplam_musteri_sayisi', 0)))
            self.total_balance_card.value_label.configure(text=format_number_display(summary.get('toplam_bakiye', 0)) + " TL")
            self.open_balance_card.value_label.configure(text=format_number_display(summary.get('toplam_acik_hesap', 0)) + " TL")
            
        except Exception as e:
            logger.error(f"İstatistik kartı güncelleme hatası: {e}")
    
    def update_arac_listbox(self):
        """ARAÇ listbox'ını güncelle"""
        try:
            self.arac_listbox.delete("1.0", "end")
            
            if not self.current_analysis_results:
                self.arac_listbox.insert("1.0", "Analiz yapılmadı")
                return
            
            # ARAÇ listesi oluştur
            content = "ARAÇ LİSTESİ\n" + "="*30 + "\n\n"
            
            for arac_no, analysis in self.current_analysis_results.items():
                musteri_sayisi = analysis.get('musteri_sayisi', 0)
                toplam_bakiye = format_number_display(analysis.get('toplam_bakiye', 0))
                
                content += f"🚗 ARAÇ {arac_no}\n"
                content += f"   👥 Müşteri: {musteri_sayisi}\n"
                content += f"   💰 Bakiye: {toplam_bakiye} TL\n\n"
            
            self.arac_listbox.insert("1.0", content)
            
        except Exception as e:
            logger.error(f"ARAÇ listbox güncelleme hatası: {e}")
    
    def refresh_arac_list(self):
        """ARAÇ listesini yenile"""
        try:
            arac_list = self.analysis_engine.get_arac_list()
            
            if arac_list:
                self.arac_dropdown.configure(values=arac_list)
            else:
                self.arac_dropdown.configure(values=["ARAÇ bulunamadı"])
                
        except Exception as e:
            logger.error(f"ARAÇ listesi yenileme hatası: {e}")
    
    def on_arac_selected(self, choice):
        """ARAÇ seçildiğinde"""
        try:
            if choice and choice != "ARAÇ seçin..." and choice in self.current_analysis_results:
                self.selected_arac = choice
                self.show_arac_details()
        except Exception as e:
            logger.error(f"ARAÇ seçimi hatası: {e}")
    
    def show_arac_details(self):
        """ARAÇ detaylarını göster"""
        try:
            if not self.selected_arac or self.selected_arac not in self.current_analysis_results:
                messagebox.showwarning("Uyarı", "Lütfen geçerli bir ARAÇ seçin")
                return
            
            analysis = self.current_analysis_results[self.selected_arac]
            
            # ARAÇ bilgileri textbox'ını güncelle
            self.arac_info_text.delete("1.0", "end")
            
            info_content = f"ARAÇ {self.selected_arac} DETAYLARI\n"
            info_content += "="*40 + "\n\n"
            
            # Temel bilgiler
            info_content += f"📊 GENEL BİLGİLER\n"
            info_content += f"Müşteri Sayısı: {analysis.get('musteri_sayisi', 0)}\n"
            info_content += f"Toplam Bakiye: {format_number_display(analysis.get('toplam_bakiye', 0))} TL\n"
            info_content += f"Açık Hesap: {format_number_display(analysis.get('acik_hesap', 0))} TL\n"
            info_content += f"Analiz Tarihi: {analysis.get('analiz_tarihi', 'Bilinmiyor')}\n\n"
            
            # İstatistikler
            stats = analysis.get('istatistikler', {})
            if stats:
                info_content += f"📈 İSTATİSTİKLER\n"
                info_content += f"Ortalama Bakiye: {format_number_display(stats.get('ortalama_bakiye', 0))} TL\n"
                info_content += f"En Yüksek Bakiye: {format_number_display(stats.get('en_yuksek_bakiye', 0))} TL\n"
                info_content += f"En Düşük Bakiye: {format_number_display(stats.get('en_dusuk_bakiye', 0))} TL\n"
                info_content += f"Pozitif Bakiye: {stats.get('bakiye_pozitif_olan', 0)} müşteri\n"
                info_content += f"Negatif Bakiye: {stats.get('bakiye_negatif_olan', 0)} müşteri\n\n"
            
            # Yaşlandırma analizi
            yaslanding = analysis.get('yaslanding_analizi', {})
            if yaslanding:
                info_content += f"⏰ YAŞLANDIRMA ANALİZİ\n"
                total_balance = analysis.get('toplam_bakiye', 0)
                for period, amount in yaslanding.items():
                    percentage = (amount / total_balance * 100) if total_balance > 0 else 0
                    info_content += f"{period}: {format_number_display(amount)} TL ({percentage:.1f}%)\n"
            
            self.arac_info_text.insert("1.0", info_content)
            
            # Müşteri listesini güncelle
            self.update_customer_tree()
            
            # ARAÇ detay tab'ına geç
            self.notebook.select(1)
            
        except Exception as e:
            logger.error(f"ARAÇ detay gösterme hatası: {e}")
            messagebox.showerror("Hata", f"ARAÇ detayları gösterilemedi: {e}")
    
    def update_customer_tree(self):
        """Müşteri tree'sini güncelle"""
        try:
            # Mevcut verileri temizle
            for item in self.customer_tree.get_children():
                self.customer_tree.delete(item)
            
            if not self.selected_arac or self.selected_arac not in self.current_analysis_results:
                return
            
            analysis = self.current_analysis_results[self.selected_arac]
            musteri_detaylari = analysis.get('musteri_detaylari', [])
            
            # Sütunları ayarla
            columns = ["cari_unvan", "toplam_bakiye"]
            
            # Yaşlandırma dönemlerini ekle
            if musteri_detaylari:
                sample_detail = musteri_detaylari[0].get('bakiye_detay', {})
                aging_periods = list(sample_detail.keys())
                columns.extend(aging_periods)
            else:
                aging_periods = []
            
            self.customer_tree["columns"] = columns
            self.customer_tree["show"] = "headings"
            
            # Başlıkları ayarla
            self.customer_tree.heading("cari_unvan", text="Cari Ünvan")
            self.customer_tree.heading("toplam_bakiye", text="Toplam Bakiye")
            
            for period in aging_periods:
                self.customer_tree.heading(period, text=period)
            
            # Sütun genişlikleri
            self.customer_tree.column("cari_unvan", width=250)
            self.customer_tree.column("toplam_bakiye", width=120)
            
            for period in aging_periods:
                self.customer_tree.column(period, width=100)
            
            # Verileri ekle
            for musteri in musteri_detaylari:
                values = [
                    musteri.get('cari_unvan', ''),
                    format_number_display(musteri.get('toplam_bakiye', 0))
                ]
                
                # Yaşlandırma değerlerini ekle
                bakiye_detay = musteri.get('bakiye_detay', {})
                for period in aging_periods:
                    amount = bakiye_detay.get(period, 0)
                    values.append(format_number_display(amount))
                
                self.customer_tree.insert("", "end", values=values)
            
        except Exception as e:
            logger.error(f"Müşteri tree güncelleme hatası: {e}")
    
    def generate_reports(self):
        """Raporları oluştur"""
        try:
            if not self.current_analysis_results:
                messagebox.showwarning("Uyarı", "Önce analiz yapılmalıdır!")
                return
            
            # Dosya kaydetme dialogu
            file_path = filedialog.asksaveasfilename(
                title="Rapor Kaydetme",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
            )
            
            if not file_path:
                return
            
            try:
                # ARAÇ özet raporu oluştur
                summary_report = self.report_generator.generate_arac_summary_report(
                    self.current_analysis_results, 
                    self.current_assignments
                )
                
                if summary_report is not None:
                    if file_path.endswith('.xlsx'):
                        self.report_generator.save_report_to_excel(summary_report, file_path, "ARAÇ Özet")
                    else:
                        summary_report.to_csv(file_path, index=False, encoding='utf-8-sig')
                    
                    messagebox.showinfo("Başarılı", f"Rapor kaydedildi: {file_path}")
                else:
                    messagebox.showerror("Hata", "Rapor oluşturulamadı!")
                    
            except Exception as save_error:
                messagebox.showerror("Hata", f"Rapor kaydetme hatası: {save_error}")
                
        except Exception as e:
            logger.error(f"Rapor oluşturma hatası: {e}")
            messagebox.showerror("Hata", f"Rapor oluşturma hatası: {e}")
    
    def on_window_close(self):
        """Pencere kapanırken"""
        try:
            # Grafikleri temizle
            if hasattr(self, 'visualization_engine'):
                self.visualization_engine.clear_figures()
            
            # Grab'i serbest bırak
            try:
                self.window.grab_release()
            except Exception:
                pass
            
            # Pencereyi kapat
            self.window.destroy()
            
        except Exception as e:
            logger.error(f"Pencere kapanış hatası: {e}")
            try:
                self.window.destroy()
            except Exception:
                pass


def create_analysis_gui(parent, excel_processor):
    """Analiz GUI'sini oluştur"""
    try:
        return AnalysisGUI(parent, excel_processor)
    except Exception as e:
        logger.error(f"Analiz GUI oluşturma hatası: {e}")
        messagebox.showerror("Hata", f"Analiz modülü başlatılamadı: {e}")
        return None