#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - Dosya İşlemleri
Dosya okuma, yazma ve işleme metodları
"""

import sys
from pathlib import Path

# Parent modül path'ini ekle
_current_dir = Path(__file__).parent
_parent_dir = _current_dir.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

import pandas as pd
import threading
import logging
from tkinter import messagebox, filedialog
from utils import format_number_display

logger = logging.getLogger(__name__)

class FileOperations:
    """Dosya işlemleri için mixin sınıf"""
    
    def select_file(self):
        """Dosya seçme işlemi"""
        try:
            file_path = filedialog.askopenfilename(
                title="Excel Dosyası Seçin",
                filetypes=[
                    ("Excel Files", "*.xlsx *.xls"),
                    ("All Files", "*.*")
                ]
            )
            
            if file_path:
                # Dosya doğrulaması
                path = Path(file_path)
                if not path.exists():
                    messagebox.showerror("Hata", "Dosya bulunamadı")
                    return
                
                if path.suffix.lower() not in ['.xlsx', '.xls']:
                    messagebox.showerror("Hata", "Lütfen geçerli bir Excel dosyası seçin")
                    return
                
                self.file_path = path
                self.file_label.configure(text=self.file_path.name)
                self.process_btn.configure(state="normal")
                if self.main_status_label:
                    self.main_status_label.configure(text="Dosya yüklendi, işleme hazır")
                
                # Orijinal veriyi göster
                try:
                    df = pd.read_excel(self.file_path)
                    self.display_dataframe(df)
                    self.update_stats(df, "Orijinal")
                except Exception as e:
                    logger.error(f"Dosya önizleme hatası: {e}")
                    messagebox.showerror("Hata", f"Dosya okunamadı: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Dosya seçme hatası: {e}")
            messagebox.showerror("Hata", f"Dosya seçme işlemi başarısız: {str(e)}")
    
    def process_file(self):
        """Dosya işleme - GELİŞTİRİLMİŞ PROGRESS"""
        if not self.file_path:
            messagebox.showerror("Hata", "Lütfen önce bir dosya seçin")
            return
        
        # Processing moduna geç
        self.set_processing_mode(True)
        
        def process_thread():
            try:
                # Progress callback
                def update_progress_callback(value, status):
                    self.update_progress(value, status)
                
                # İşle
                self.processed_df = self.processor.process_excel(
                    self.file_path,
                    progress_callback=update_progress_callback
                )
                
                # Sonuçları göster
                self.root.after(0, self.on_process_complete)
                
            except Exception as e:
                logger.error(f"İşleme hatası: {e}")
                self.root.after(0, lambda: messagebox.showerror("İşleme Hatası", str(e)))
                self.root.after(0, self.on_process_error)
        
        thread = threading.Thread(target=process_thread, daemon=True)
        thread.start()
    
    def set_processing_mode(self, processing):
        """Processing moduna geç/çık"""
        def update_ui():
            state = "disabled" if processing else "normal"
            
            # Butonları kontrol et
            if self.select_btn:
                self.select_btn.configure(state=state)
            if self.save_btn:
                self.save_btn.configure(state=state)
            if hasattr(self, 'restore_btn') and self.restore_btn:
                self.restore_btn.configure(state=state)
            
            # Process butonunu özel handle et
            if self.process_btn:
                if processing:
                    self.process_btn.configure(text="İşleniyor...", state="disabled")
                else:
                    self.process_btn.configure(text="İşleme Başla", state="normal")
        
        self.root.after(0, update_ui)
    
    def on_process_complete(self):
        """İşlem tamamlandığında"""
        try:
            if self.progress:
                self.progress.set(1)
            if self.main_status_label:
                self.main_status_label.configure(text="İşlem tamamlandı!")
            
            self.set_processing_mode(False)
            
            if self.preview_btn:
                self.preview_btn.configure(state="normal")
            if self.save_btn:
                self.save_btn.configure(state="normal")
            if hasattr(self, 'restore_btn') and self.restore_btn:
                self.restore_btn.configure(state="normal")
            
            # Analiz modülü butonunu aktif et
            if hasattr(self, 'analyze_btn') and self.analyze_btn:
                self.analyze_btn.configure(state="normal")
                if hasattr(self, 'analysis_indicator') and self.analysis_indicator:
                    self.analysis_indicator.configure(text="Analiz: Veri Hazır")
            
            # Otomatik önizleme
            self.preview_processed()
            
            # Başarı mesajı
            success_msg = "Excel dosyası başarıyla işlendi!"
            if hasattr(self, 'analyze_btn'):
                success_msg += "\n\n'Analiz Başlat' butonu ile ARAÇ analizi yapabilirsiniz."
            
            messagebox.showinfo("Başarılı", success_msg)
            
        except Exception as e:
            logger.error(f"İşlem tamamlama hatası: {e}")
    
    def on_process_error(self):
        """İşlem hatası durumunda"""
        self.set_processing_mode(False)
        if self.progress:
            self.progress.set(0)
        if self.main_status_label:
            self.main_status_label.configure(text="Hata oluştu")
        if hasattr(self, 'analyze_btn') and self.analyze_btn:
            self.analyze_btn.configure(state="disabled")
            if hasattr(self, 'analysis_indicator') and self.analysis_indicator:
                self.analysis_indicator.configure(text="Analiz: Hata", text_color="red")
    
    def preview_processed(self):
        """İşlenmiş veriyi göster"""
        try:
            if self.processed_df is not None:
                self.display_dataframe(self.processed_df)
                self.update_stats(self.processed_df, "İşlenmiş")
            else:
                messagebox.showwarning("Uyarı", "Henüz işlenmiş veri yok")
        except Exception as e:
            logger.error(f"Önizleme hatası: {e}")
            messagebox.showerror("Hata", f"Önizleme gösterilemedi: {str(e)}")
    
    def save_file(self):
        """İşlenmiş dosyayı kaydet"""
        if self.processed_df is None:
            messagebox.showwarning("Uyarı", "Kaydedilecek işlenmiş veri yok")
            return
        
        try:
            # Varsayılan dosya adı
            default_name = f"{self.file_path.stem}_islenmis.xlsx"
            
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=default_name,
                filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
            )
            
            if save_path:
                try:
                    self.processed_df.to_excel(save_path, index=False)
                    
                    success_msg = f"Dosya kaydedildi:\n{save_path}"
                    if hasattr(self, 'analyze_btn'):
                        success_msg += f"\n\nİpucu: ARAÇ analizi bu veri üzerinde çalışır!"
                    
                    messagebox.showinfo("Başarılı", success_msg)
                    logger.info(f"Dosya başarıyla kaydedildi: {save_path}")
                    
                except PermissionError:
                    messagebox.showerror("Hata", "Dosya açık olabilir. Lütfen dosyayı kapatıp tekrar deneyin.")
                except Exception as save_error:
                    logger.error(f"Dosya kaydetme hatası: {save_error}")
                    messagebox.showerror("Kayıt Hatası", f"Dosya kaydedilemedi: {str(save_error)}")
                    
        except Exception as e:
            logger.error(f"Kaydetme işlemi hatası: {e}")
            messagebox.showerror("Hata", f"Kaydetme işlemi başarısız: {str(e)}")
    
    def restore_backup(self):
        """Backup'tan geri yükle"""
        try:
            if self.processor.restore_from_backup():
                self.processed_df = self.processor.get_backup_data()
                if self.processed_df is not None:
                    self.display_dataframe(self.processed_df)
                    self.update_stats(self.processed_df, "Geri Yüklenen")
                    messagebox.showinfo("Başarılı", "Veriler orijinal haline geri yüklendi")
                else:
                    messagebox.showwarning("Uyarı", "Geri yüklenecek backup bulunamadı")
            else:
                messagebox.showwarning("Uyarı", "Geri yüklenecek backup bulunamadı")
        except Exception as e:
            logger.error(f"Geri yükleme hatası: {e}")
            messagebox.showerror("Hata", f"Geri yükleme başarısız: {str(e)}")
    
    def display_dataframe(self, df):
        """DataFrame'i Treeview'da güvenli şekilde göster"""
        try:
            if not self.tree:
                return
                
            # Mevcut veriyi temizle
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            if df.empty:
                return
            
            # Sütunları ayarla
            self.tree["columns"] = list(df.columns)
            self.tree["show"] = "headings"
            
            # Sütun başlıkları
            for col in df.columns:
                self.tree.heading(col, text=str(col))
                # Sütun genişliği
                if "Cari Ünvan" in str(col):
                    width = 250
                elif any(x in str(col) for x in ["Cari Kategori 3", "Kategori"]):
                    width = 120
                else:
                    width = 100
                self.tree.column(col, width=width, minwidth=50)
            
            # Veriyi ekle (sadece ilk 1000 satır performans için)
            max_rows = min(len(df), 1000)
            for idx in range(max_rows):
                row = df.iloc[idx]
                values = []
                for val in row:
                    if pd.isna(val):
                        values.append("")
                    elif isinstance(val, (int, float)):
                        values.append(format_number_display(val))
                    else:
                        values.append(str(val))
                self.tree.insert("", "end", values=values)
            
            if len(df) > 1000 and self.main_status_label:
                self.main_status_label.configure(text=f"İlk 1000 satır gösteriliyor (Toplam: {len(df)})")
                
        except Exception as e:
            logger.error(f"DataFrame görüntüleme hatası: {e}")
            messagebox.showerror("Hata", f"Veri görüntülenemedi: {str(e)}")
    
    def update_stats(self, df, label):
        """İstatistikleri güvenli şekilde güncelle"""
        try:
            if not self.stats_label:
                return
                
            stats_text = f"{label} Veri:\n"
            stats_text += f"Satır: {len(df)}\n"
            stats_text += f"Sütun: {len(df.columns)}\n"
            
            # Kategori dağılımı
            kategori_cols = [col for col in df.columns if 'kategori' in str(col).lower()]
            
            if kategori_cols:
                col_name = kategori_cols[0]  # İlk kategori sütununu al
                kategori_col = df[col_name]
                
                # Sayısal kategoriler (ARAÇ'lar)
                try:
                    numeric_cats = kategori_col[pd.to_numeric(kategori_col, errors='coerce').notna()]
                    if not numeric_cats.empty:
                        stats_text += f"ARAÇ Sayısı: {len(numeric_cats)}\n"
                        
                        # En büyük ve en küçük ARAÇ numarası
                        numeric_values = pd.to_numeric(numeric_cats, errors='coerce')
                        stats_text += f"   Min ARAÇ: {int(numeric_values.min())}\n"
                        stats_text += f"   Max ARAÇ: {int(numeric_values.max())}\n"
                    
                    # Diğer kategoriler
                    non_numeric = kategori_col[pd.to_numeric(kategori_col, errors='coerce').isna()]
                    if not non_numeric.empty:
                        stats_text += f"Diğer Kategori: {len(non_numeric)}\n"
                        
                except Exception as cat_error:
                    logger.debug(f"Kategori analizi hatası: {cat_error}")
            
            # Bakiye sütunları analizi (eğer işlenmiş veriyse)
            if label == "İşlenmiş":
                bakiye_cols = [col for col in df.columns if 'gün' in str(col).lower() or 'bakiye' in str(col).lower()]
                if bakiye_cols:
                    stats_text += f"Bakiye Sütunu: {len(bakiye_cols)}\n"
            
            # Analiz modülü durumu
            if hasattr(self, 'analyze_btn') and label == "İşlenmiş":
                stats_text += f"\nAnaliz Hazır\n"
                stats_text += f"ARAÇ Analizi mevcut!"
            elif not hasattr(self, 'analyze_btn'):
                stats_text += f"\nAnaliz Modülü\nYüklenemedi"
            
            self.stats_label.configure(text=stats_text)
            
        except Exception as e:
            logger.error(f"İstatistik güncelleme hatası: {e}")
            if self.stats_label:
                self.stats_label.configure(text=f"{label} Veri:\nHata oluştu")
    
    def update_progress(self, value, status):
        """Progress ve status güncelle - Thread safe"""
        def update_ui():
            if self.progress:
                self.progress.set(value)
            if self.main_status_label:
                self.main_status_label.configure(text=status)
            if hasattr(self, 'analysis_indicator'):
                if value >= 1.0:
                    self.analysis_indicator.configure(text="Analiz: Tamamlandı", text_color="green")
                elif value > 0:
                    self.analysis_indicator.configure(text="Analiz: Çalışıyor...", text_color="orange")
        
        # Thread-safe UI güncellemesi
        self.root.after(0, update_ui)
