#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - Analiz İşlemleri
ARAÇ analizi ve ilgili işlemler
"""

import sys
from pathlib import Path

# Parent modül path'ini ekle
_current_dir = Path(__file__).parent
_parent_dir = _current_dir.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

import threading
import logging
from tkinter import messagebox
from utils import format_number_display

logger = logging.getLogger(__name__)

class AnalysisOperations:
    """Analiz işlemleri için mixin sınıf"""
    
    def start_analysis(self):
        """ARAÇ analizini başlat - GELİŞTİRİLMİŞ PROGRESS"""
        if not hasattr(self, 'analysis_engine'):
            messagebox.showerror("Hata", "Analiz modülü yüklenmemiş!")
            return
            
        try:
            if self.processed_df is None:
                messagebox.showerror("Hata", "Önce Excel verisi işlenmelidir!")
                return
            
            # UI'yi analiz moduna geçir
            self.set_analysis_mode(True)
            
            def analysis_thread():
                try:
                    # Adım 1: Veri hazırlığı (10%)
                    self.update_progress(0.1, "Veri hazırlanıyor...")
                    
                    if not self.analysis_engine.set_data(self.processed_df):
                        raise Exception("Analiz verisi ayarlanamadı")
                    
                    # Adım 2: ARAÇ listesi çıkarma (20%)
                    self.update_progress(0.2, "ARAÇ numaraları tespit ediliyor...")
                    arac_list = self.analysis_engine.get_arac_list()
                    total_aracs = len(arac_list)
                    
                    if total_aracs == 0:
                        raise Exception("Analiz edilecek ARAÇ bulunamadı")
                    
                    # Adım 3: Her ARAÇ için analiz (20% - 80%)
                    self.current_analysis_results = {}
                    
                    for i, arac_no in enumerate(arac_list):
                        progress = 0.2 + (0.6 * (i / total_aracs))
                        self.update_progress(progress, f"ARAÇ {arac_no} analiz ediliyor... ({i+1}/{total_aracs})")
                        
                        # Tek ARAÇ analizi
                        analysis_result = self.analysis_engine.analyze_single_arac(arac_no)
                        if analysis_result:
                            self.current_analysis_results[str(arac_no)] = analysis_result
                    
                    # Adım 4: Sonuçları kaydetme (90%)
                    self.update_progress(0.9, "Sonuçlar kaydediliyor...")
                    
                    # UI güncelleme
                    self.update_progress(0.95, "Arayüz güncelleniyor...")
                    self.root.after(0, self.update_analysis_results)
                    
                    # Tamamlandı (100%)
                    self.update_progress(1.0, f"Analiz tamamlandı! {total_aracs} ARAÇ analiz edildi")
                    
                    # Analiz modundan çık
                    self.root.after(1000, lambda: self.set_analysis_mode(False))
                    
                    # Analiz tab'ına geç
                    self.root.after(500, lambda: self.notebook.select(1))
                    
                    # Başarı mesajı
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Başarılı", 
                        f"ARAÇ analizi tamamlandı!\n\n"
                        f"• {total_aracs} ARAÇ analiz edildi\n"
                        f"• {sum(r.get('musteri_sayisi', 0) for r in self.current_analysis_results.values())} müşteri\n"
                        f"• Toplam bakiye: {format_number_display(sum(r.get('toplam_bakiye', 0) for r in self.current_analysis_results.values()))} TL"
                    ))
                    
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("Analiz Hatası", str(e)))
                    self.root.after(0, lambda: self.set_analysis_mode(False))
                    logger.error(f"Analiz hatası: {e}")
            
            # Thread'i başlat
            thread = threading.Thread(target=analysis_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error(f"Analiz başlatma hatası: {e}")
            messagebox.showerror("Hata", f"Analiz başlatılamadı: {e}")
            self.set_analysis_mode(False)
    
    def set_analysis_mode(self, analyzing):
        """Analiz moduna geç/çık"""
        def update_ui():
            state = "disabled" if analyzing else "normal"
            
            # Ana butonları disable et
            if self.select_btn:
                self.select_btn.configure(state=state)
            if self.process_btn:
                self.process_btn.configure(state=state)
            if self.save_btn:
                self.save_btn.configure(state=state)
            if hasattr(self, 'restore_btn') and self.restore_btn:
                self.restore_btn.configure(state=state)
            
            # Analiz butonunu özel olarak handle et
            if hasattr(self, 'analyze_btn') and self.analyze_btn:
                if analyzing:
                    self.analyze_btn.configure(text="Analiz Çalışıyor...", state="disabled")
                else:
                    self.analyze_btn.configure(text="Analiz Başlat", state="normal")
            
            # Progress bar'ı göster/gizle
            if self.progress:
                if not analyzing:
                    self.progress.set(0)
        
        self.root.after(0, update_ui)
    
    def update_analysis_results(self):
        """Analiz sonuçlarını UI'de güncelle"""
        if not hasattr(self, 'analysis_engine'):
            return
            
        try:
            # ARAÇ listesini güncelle
            self.refresh_arac_list()
            
            # İstatistik kartlarını güncelle
            self.update_statistics_cards()
            
            # ARAÇ listbox'ını güncelle
            self.update_arac_listbox()
            
            # Analiz status'unu güncelle
            if hasattr(self, 'refresh_reports_arac_list'):
                self.refresh_reports_arac_list()
            
            logger.info("Analiz sonuçları UI'de güncellendi")
            
        except Exception as e:
            logger.error(f"UI güncelleme hatası: {e}")
    
    def update_statistics_cards(self):
        """İstatistik kartlarını güncelle"""
        if not hasattr(self, 'current_analysis_results'):
            return
            
        try:
            if not self.current_analysis_results:
                return
            
            # Özet istatistikleri hesapla
            summary = self.analysis_engine.get_summary_statistics()
            
            # Kartları güncelle
            if hasattr(self, 'total_arac_card'):
                self.total_arac_card.value_label.configure(text=str(summary.get('toplam_arac_sayisi', 0)))
                self.total_customer_card.value_label.configure(text=str(summary.get('toplam_musteri_sayisi', 0)))
                self.total_balance_card.value_label.configure(text=format_number_display(summary.get('toplam_bakiye', 0)) + " TL")
                self.open_balance_card.value_label.configure(text=format_number_display(summary.get('toplam_acik_hesap', 0)) + " TL")
                
                # Atama istatistikleri
                assigned_count = len([arac for arac in self.current_analysis_results.keys() 
                                    if arac in self.current_assignments])
                unassigned_count = len(self.current_analysis_results) - assigned_count
                
                self.assigned_arac_card.value_label.configure(text=str(assigned_count))
                self.unassigned_arac_card.value_label.configure(text=str(unassigned_count))
            
        except Exception as e:
            logger.error(f"İstatistik kartı güncelleme hatası: {e}")
    
    def update_arac_listbox(self):
        """ARAÇ listbox'ını güncelle"""
        if not hasattr(self, 'arac_listbox'):
            return
            
        try:
            self.arac_listbox.delete("1.0", "end")
            
            if not self.current_analysis_results:
                self.arac_listbox.insert("1.0", "Analiz yapılmadı")
                return
            
            # ARAÇ listesi oluştur
            content = "ARAÇ LİSTESİ\n" + "="*30 + "\n\n"
            
            for arac_no, analysis in self.current_analysis_results.items():
                sorumlu = self.current_assignments.get(arac_no, {}).get('sorumlu', 'Atanmamış')
                musteri_sayisi = analysis.get('musteri_sayisi', 0)
                toplam_bakiye = format_number_display(analysis.get('toplam_bakiye', 0))
                
                content += f"ARAÇ {arac_no}\n"
                content += f"   Sorumlu: {sorumlu}\n"
                content += f"   Müşteri: {musteri_sayisi}\n"
                content += f"   Bakiye: {toplam_bakiye} TL\n\n"
            
            self.arac_listbox.insert("1.0", content)
            
        except Exception as e:
            logger.error(f"ARAÇ listbox güncelleme hatası: {e}")
    
    def refresh_arac_list(self):
        """ARAÇ listesini yenile"""
        if not hasattr(self, 'analysis_engine'):
            return
            
        try:
            arac_list = self.analysis_engine.get_arac_list()
            
            # Dropdown'ı güncelle
            if hasattr(self, 'arac_dropdown'):
                if arac_list:
                    self.arac_dropdown.configure(values=arac_list)
                else:
                    self.arac_dropdown.configure(values=["ARAÇ bulunamadı"])
                
        except Exception as e:
            logger.error(f"ARAÇ listesi yenileme hatası: {e}")
    
    def on_arac_selected(self, choice):
        """ARAÇ seçildiğinde"""
        if not hasattr(self, 'current_analysis_results'):
            return
            
        try:
            if choice and choice != "ARAÇ seçin..." and choice in self.current_analysis_results:
                self.selected_arac = choice
                self.show_arac_details()
        except Exception as e:
            logger.error(f"ARAÇ seçimi hatası: {e}")
    
    def show_selected_arac_details(self):
        """Seçili ARAÇ detaylarını göster"""
        if not hasattr(self, 'current_analysis_results'):
            return
            
        try:
            # ARAÇ seçim dialog'u
            if not self.current_analysis_results:
                messagebox.showwarning("Uyarı", "Önce analiz yapılmalıdır!")
                return
            
            arac_list = list(self.current_analysis_results.keys())
            
            # Basit seçim için ilk ARAÇ'ı seç
            if arac_list:
                self.selected_arac = arac_list[0]
                # ARAÇ detay tab'ına geç ve dropdown'ı ayarla
                if self.notebook:
                    self.notebook.select(2)  # ARAÇ Detayı tab'ı
                if hasattr(self, 'arac_dropdown'):
                    self.arac_dropdown.set(self.selected_arac)
                self.show_arac_details()
        except Exception as e:
            logger.error(f"ARAÇ detay gösterme hatası: {e}")
    
    def show_arac_details(self):
        """ARAÇ detaylarını göster"""
        if not hasattr(self, 'current_analysis_results'):
            return
            
        try:
            if not self.selected_arac or self.selected_arac not in self.current_analysis_results:
                messagebox.showwarning("Uyarı", "Lütfen geçerli bir ARAÇ seçin")
                return
            
            analysis = self.current_analysis_results[self.selected_arac]
            
            # ARAÇ bilgileri textbox'ını güncelle
            if hasattr(self, 'arac_info_text'):
                self.arac_info_text.delete("1.0", "end")
                
                info_content = f"ARAÇ {self.selected_arac} DETAYLARI\n"
                info_content += "="*40 + "\n\n"
                
                # Temel bilgiler
                info_content += f"GENEL BİLGİLER\n"
                info_content += f"Müşteri Sayısı: {analysis.get('musteri_sayisi', 0)}\n"
                info_content += f"Toplam Bakiye: {format_number_display(analysis.get('toplam_bakiye', 0))} TL\n"
                info_content += f"Açık Hesap: {format_number_display(analysis.get('acik_hesap', 0))} TL\n"
                info_content += f"Analiz Tarihi: {analysis.get('analiz_tarihi', 'Bilinmiyor')}\n\n"
                
                # İstatistikler
                stats = analysis.get('istatistikler', {})
                if stats:
                    info_content += f"İSTATİSTİKLER\n"
                    info_content += f"Ortalama Bakiye: {format_number_display(stats.get('ortalama_bakiye', 0))} TL\n"
                    info_content += f"En Yüksek Bakiye: {format_number_display(stats.get('en_yuksek_bakiye', 0))} TL\n"
                    info_content += f"En Düşük Bakiye: {format_number_display(stats.get('en_dusuk_bakiye', 0))} TL\n"
                    info_content += f"Pozitif Bakiye: {stats.get('bakiye_pozitif_olan', 0)} müşteri\n"
                    info_content += f"Negatif Bakiye: {stats.get('bakiye_negatif_olan', 0)} müşteri\n\n"
                
                # Yaşlandırma analizi
                yaslanding = analysis.get('yaslanding_analizi', {})
                if yaslanding:
                    info_content += f"YAŞLANDIRMA ANALİZİ\n"
                    total_balance = analysis.get('toplam_bakiye', 0)
                    for period, amount in yaslanding.items():
                        percentage = (amount / total_balance * 100) if total_balance > 0 else 0
                        info_content += f"{period}: {format_number_display(amount)} TL ({percentage:.1f}%)\n"
                    info_content += "\n"
                
                self.arac_info_text.insert("1.0", info_content)
                
                # Müşteri listesini güncelle
                self.update_customer_tree()
            
        except Exception as e:
            logger.error(f"ARAÇ detay gösterme hatası: {e}")
            messagebox.showerror("Hata", f"ARAÇ detayları gösterilemedi: {e}")
    
    def update_customer_tree(self):
        """Müşteri tree'sini güncelle"""
        if not hasattr(self, 'customer_tree'):
            return
            
        try:
            # Mevcut verileri temizle
            for item in self.customer_tree.get_children():
                self.customer_tree.delete(item)
            
            if not self.selected_arac or self.selected_arac not in self.current_analysis_results:
                return
            
            analysis = self.current_analysis_results[self.selected_arac]
            musteri_detaylari = analysis.get('musteri_detaylari', [])
            
            if not musteri_detaylari:
                return
            
            # Sütunları ayarla
            columns = ["cari_unvan", "toplam_bakiye"]
            
            # Yaşlandırma dönemlerini ekle
            sample_detail = musteri_detaylari[0].get('bakiye_detay', {})
            aging_periods = list(sample_detail.keys())
            columns.extend(aging_periods)
            
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
    
    def refresh_analysis(self):
        """Analizi yenile"""
        if not hasattr(self, 'analysis_engine'):
            messagebox.showwarning("Uyarı", "Analiz modülü mevcut değil")
            return
            
        try:
            if self.processed_df is not None:
                self.start_analysis()
            else:
                messagebox.showwarning("Uyarı", "Önce dosya işlenmelidir")
        except Exception as e:
            logger.error(f"Analiz yenileme hatası: {e}")
    
    def save_analysis_data(self):
        """Analiz verilerini kaydet"""
        if not hasattr(self, 'data_manager'):
            messagebox.showwarning("Uyarı", "Analiz modülü mevcut değil")
            return
            
        try:
            if not self.current_analysis_results:
                messagebox.showwarning("Uyarı", "Kaydedilecek analiz verisi yok")
                return
            
            if self.main_status_label:
                self.main_status_label.configure(text="Analiz verileri kaydediliyor...")
            
            # Analiz verilerini kaydet
            from datetime import datetime
            metadata = {
                'save_date': datetime.now().isoformat(),
                'total_aracs': len(self.current_analysis_results),
                'application': 'Excel İşleme Uygulaması - Modüler'
            }
            
            success = self.data_manager.save_analysis_data(self.current_analysis_results, metadata)
            
            if success:
                if self.main_status_label:
                    self.main_status_label.configure(text="Analiz verileri kaydedildi")
                messagebox.showinfo("Başarılı", "Analiz verileri başarıyla kaydedildi")
            else:
                messagebox.showerror("Hata", "Analiz verisi kaydetme başarısız")
                
        except Exception as e:
            logger.error(f"Analiz veri kaydetme hatası: {e}")
            messagebox.showerror("Hata", f"Analiz verisi kaydetme başarısız: {e}")
            if self.main_status_label:
                self.main_status_label.configure(text="Analiz kaydetme hatası")
    
    def load_saved_analysis_data(self):
        """Kaydedilmiş analiz verilerini yükle"""
        if not hasattr(self, 'data_manager'):
            return
            
        try:
            # Analiz verilerini yükle
            analysis_data = self.data_manager.load_analysis_data()
            if analysis_data and 'analysis_results' in analysis_data:
                self.current_analysis_results = analysis_data['analysis_results']
                logger.info("Kaydedilmiş analiz verileri yüklendi")
                
                # UI'yi güncelle
                self.update_analysis_results()
            
            # Atama verilerini yükle
            assignment_data = self.data_manager.load_assignments_data()
            if assignment_data and 'assignments' in assignment_data:
                self.current_assignments = assignment_data['assignments']
                logger.info("Kaydedilmiş atama verileri yüklendi")
            
        except Exception as e:
            logger.error(f"Kaydedilmiş veri yükleme hatası: {e}")
