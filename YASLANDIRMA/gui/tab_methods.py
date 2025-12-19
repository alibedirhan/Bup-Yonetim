#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - Tab İşlemleri
Tab'larla ilgili tüm metodlar
"""

import sys
from pathlib import Path

# Parent modül path'ini ekle
_current_dir = Path(__file__).parent
_parent_dir = _current_dir.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

import customtkinter as ctk
from tkinter import messagebox
import tkinter.ttk as ttk
import pandas as pd
import logging
from datetime import datetime
from utils import format_number_display, format_turkish_number

logger = logging.getLogger(__name__)

class TabMethods:
    """Tab işlemleri için mixin sınıf"""
    
    def create_preview_panel(self, parent):
        """Önizleme panelini oluştur"""
        right_frame = ctk.CTkFrame(parent)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Başlık
        preview_title = ctk.CTkLabel(
            right_frame,
            text="Veri Önizleme",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        preview_title.pack(pady=10)
        
        # Treeview için frame
        tree_frame = ctk.CTkFrame(right_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbarlar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Grid yerleşimi
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Treeview stil
        self.setup_treeview_style()
    
    def on_assignment_arac_selected(self, choice):
        """Atama için ARAÇ seçildiğinde"""
        if not hasattr(self, 'current_analysis_results'):
            return
            
        try:
            if choice and choice != "ARAÇ seçin..." and choice in self.current_analysis_results:
                # Mevcut atamayı forma yükle
                assignment = self.current_assignments.get(choice, {})
                
                if assignment:
                    self.personnel_name_entry.delete(0, "end")
                    self.personnel_name_entry.insert(0, assignment.get('sorumlu', ''))
                    
                    self.personnel_email_entry.delete(0, "end")
                    self.personnel_email_entry.insert(0, assignment.get('email', ''))
                    
                    self.personnel_phone_entry.delete(0, "end")
                    self.personnel_phone_entry.insert(0, assignment.get('telefon', ''))
                    
                    self.personnel_department_entry.delete(0, "end")
                    self.personnel_department_entry.insert(0, assignment.get('departman', ''))
                    
                    self.personnel_notes_textbox.delete("1.0", "end")
                    self.personnel_notes_textbox.insert("1.0", assignment.get('notlar', ''))
                else:
                    # Formu temizle
                    self.clear_assignment_form()
                    
        except Exception as e:
            logger.error(f"Atama ARAÇ seçimi hatası: {e}")
    
    def clear_assignment_form(self):
        """Atama formunu temizle"""
        try:
            self.personnel_name_entry.delete(0, "end")
            self.personnel_email_entry.delete(0, "end")
            self.personnel_phone_entry.delete(0, "end")
            self.personnel_department_entry.delete(0, "end")
            self.personnel_notes_textbox.delete("1.0", "end")
        except Exception as e:
            logger.debug(f"Form temizleme hatası: {e}")
    
    def assign_personnel(self):
        """Personel atama işlemi"""
        if not hasattr(self, 'assignment_manager'):
            return
            
        try:
            selected_arac = self.assignment_arac_dropdown.get()
            
            if not selected_arac or selected_arac == "ARAÇ seçin...":
                messagebox.showwarning("Uyarı", "Lütfen bir ARAÇ seçin")
                return
            
            personnel_name = self.personnel_name_entry.get().strip()
            if not personnel_name:
                messagebox.showwarning("Uyarı", "Sorumlu adı zorunludur")
                return
            
            # Atama bilgilerini topla
            assignment_info = {
                'sorumlu': personnel_name,
                'email': self.personnel_email_entry.get().strip(),
                'telefon': self.personnel_phone_entry.get().strip(),
                'departman': self.personnel_department_entry.get().strip(),
                'notlar': self.personnel_notes_textbox.get("1.0", "end").strip()
            }
            
            # Atamayı gerçekleştir
            success = self.assignment_manager.assign_personnel(selected_arac, assignment_info)
            
            if success:
                # Yerel listeyi güncelle
                self.current_assignments[selected_arac] = assignment_info
                
                # UI'yi güncelle
                self.update_assignment_tree()
                self.update_statistics_cards()
                
                messagebox.showinfo("Başarılı", f"ARAÇ {selected_arac} → {personnel_name} atandı")
                
                # Verileri kaydet
                self.save_assignment_data()
            else:
                messagebox.showerror("Hata", "Atama işlemi başarısız")
                
        except Exception as e:
            logger.error(f"Personel atama hatası: {e}")
            messagebox.showerror("Hata", f"Atama hatası: {e}")
    
    def remove_assignment(self):
        """Atamayı kaldır"""
        if not hasattr(self, 'assignment_manager'):
            return
            
        try:
            selected_arac = self.assignment_arac_dropdown.get()
            
            if not selected_arac or selected_arac == "ARAÇ seçin...":
                messagebox.showwarning("Uyarı", "Lütfen bir ARAÇ seçin")
                return
            
            if selected_arac not in self.current_assignments:
                messagebox.showwarning("Uyarı", "Bu ARAÇ için atama bulunmuyor")
                return
            
            # Onay al
            confirm = messagebox.askyesno(
                "Onay", 
                f"ARAÇ {selected_arac} atamasını kaldırmak istediğinizden emin misiniz?"
            )
            
            if confirm:
                # Atamayı kaldır
                success = self.assignment_manager.remove_assignment(selected_arac, "Kullanıcı tarafından kaldırıldı")
                
                if success:
                    # Yerel listeden çıkar
                    if selected_arac in self.current_assignments:
                        del self.current_assignments[selected_arac]
                    
                    # Formu temizle
                    self.clear_assignment_form()
                    
                    # UI'yi güncelle
                    self.update_assignment_tree()
                    self.update_statistics_cards()
                    
                    messagebox.showinfo("Başarılı", f"ARAÇ {selected_arac} ataması kaldırıldı")
                    
                    # Verileri kaydet
                    self.save_assignment_data()
                else:
                    messagebox.showerror("Hata", "Atama kaldırma işlemi başarısız")
                    
        except Exception as e:
            logger.error(f"Atama kaldırma hatası: {e}")
            messagebox.showerror("Hata", f"Atama kaldırma hatası: {e}")
    
    def update_assignment_tree(self):
        """Atama tree'sini güncelle - İYİLEŞTİRİLMİŞ"""
        if not hasattr(self, 'assignment_tree'):
            return
            
        try:
            # Mevcut verileri temizle
            for item in self.assignment_tree.get_children():
                self.assignment_tree.delete(item)
            
            # Atamaları ekle
            assignment_count = 0
            for arac_no, assignment in self.current_assignments.items():
                # Tarih formatını düzelt
                atama_tarihi = assignment.get('atama_tarihi', '')
                if atama_tarihi and 'T' in atama_tarihi:
                    atama_tarihi = atama_tarihi.split('T')[0]
                
                values = (
                    arac_no,
                    assignment.get('sorumlu', ''),
                    assignment.get('email', ''),
                    assignment.get('telefon', ''),
                    assignment.get('departman', ''),
                    atama_tarihi
                )
                self.assignment_tree.insert("", "end", values=values)
                assignment_count += 1
            
            # Atama sayısını güncelle
            if hasattr(self, 'assignment_count_label'):
                self.assignment_count_label.configure(
                    text=f"({assignment_count} atama)",
                    text_color="green" if assignment_count > 0 else "gray"
                )
            
            # ARAÇ dropdown'ını güncelle
            if hasattr(self, 'assignment_arac_dropdown') and hasattr(self, 'analysis_engine'):
                arac_list = self.analysis_engine.get_arac_list()
                if arac_list:
                    self.assignment_arac_dropdown.configure(values=["ARAÇ seçin..."] + arac_list)
                    
            logger.info(f"Atama tree güncellendi: {assignment_count} kayıt")
                
        except Exception as e:
            logger.error(f"Atama tree güncelleme hatası: {e}")
    
    def on_assignment_tree_select(self, event):
        """Atama tree'sinde seçim yapıldığında"""
        try:
            if not hasattr(self, 'assignment_tree'):
                return
                
            selection = self.assignment_tree.selection()
            if selection:
                item = self.assignment_tree.item(selection[0])
                values = item['values']
                
                if values and len(values) > 0:
                    arac_no = values[0]
                    # ARAÇ dropdown'ını güncelle
                    self.assignment_arac_dropdown.set(str(arac_no))
                    # Formu doldur
                    self.on_assignment_arac_selected(str(arac_no))
                    
        except Exception as e:
            logger.error(f"Atama tree seçim hatası: {e}")
    
    def save_assignment_data(self):
        """Atama verilerini kaydet"""
        if not hasattr(self, 'assignment_manager') or not hasattr(self, 'data_manager'):
            return
            
        try:
            assignment_history = self.assignment_manager.get_assignment_history()
            success = self.data_manager.save_assignments_data(
                self.current_assignments, 
                assignment_history
            )
            
            if success:
                logger.info("Atama verileri kaydedildi")
            else:
                logger.warning("Atama verileri kaydetme başarısız")
                
        except Exception as e:
            logger.error(f"Atama veri kaydetme hatası: {e}")
    
    def on_report_all_arac_toggle(self):
        """Tüm ARAÇ seçimi değiştiğinde"""
        try:
            if self.report_all_arac_var.get():
                # Tüm ARAÇ'lar seçili, checkboxları gizle
                for widget in self.arac_selection_frame.winfo_children():
                    widget.destroy()
            else:
                # Bireysel seçim, checkboxları göster
                self.create_arac_selection_checkboxes()
        except Exception as e:
            logger.error(f"ARAÇ seçim toggle hatası: {e}")
    
    def create_arac_selection_checkboxes(self):
        """ARAÇ seçim checkboxlarını oluştur"""
        try:
            if not hasattr(self, 'analysis_engine'):
                return
                
            # Mevcut widgetları temizle
            for widget in self.arac_selection_frame.winfo_children():
                widget.destroy()
            
            # ARAÇ listesini al
            arac_list = self.analysis_engine.get_arac_list()
            
            if not arac_list:
                ctk.CTkLabel(
                    self.arac_selection_frame,
                    text="ARAÇ listesi yok"
                ).pack(pady=5)
                return
            
            # Checkbox'lar için scrollable frame
            scrollable_frame = ctk.CTkScrollableFrame(self.arac_selection_frame)
            scrollable_frame.pack(fill="both", expand=True)
            
            self.arac_checkboxes = {}
            
            for arac_no in arac_list:
                var = ctk.BooleanVar()
                checkbox = ctk.CTkCheckBox(
                    scrollable_frame,
                    text=f"ARAÇ {arac_no}",
                    variable=var
                )
                checkbox.pack(anchor="w", pady=1)
                self.arac_checkboxes[arac_no] = var
                
        except Exception as e:
            logger.error(f"ARAÇ checkbox oluşturma hatası: {e}")
    
    def get_selected_aracs_for_report(self):
        """Rapor için seçili ARAÇ'ları al"""
        try:
            if self.report_all_arac_var.get():
                # Tüm ARAÇ'lar
                return self.analysis_engine.get_arac_list()
            else:
                # Seçili ARAÇ'lar
                selected = []
                if hasattr(self, 'arac_checkboxes'):
                    for arac_no, var in self.arac_checkboxes.items():
                        if var.get():
                            selected.append(arac_no)
                return selected
        except Exception as e:
            logger.error(f"Seçili ARAÇ alma hatası: {e}")
            return []
    
    def generate_report(self):
        """Rapor oluştur"""
        if not hasattr(self, 'report_generator'):
            messagebox.showerror("Hata", "Analiz modülü mevcut değil")
            return
            
        try:
            if not self.current_analysis_results:
                messagebox.showwarning("Uyarı", "Önce analiz yapılmalıdır")
                return
            
            report_type = self.report_type_var.get()
            selected_aracs = self.get_selected_aracs_for_report()
            
            if not selected_aracs:
                messagebox.showwarning("Uyarı", "Hiç ARAÇ seçilmedi")
                return
            
            self.report_status_label.configure(text="Rapor oluşturuluyor...")
            self.generate_report_btn.configure(state="disabled")
            
            # Rapor türüne göre oluştur
            report_df = None
            
            if report_type == "arac_summary":
                report_df = self.report_generator.generate_arac_summary_report(
                    self.current_analysis_results, 
                    self.current_assignments
                )
                
            elif report_type == "detailed_analysis":
                report_df = self.report_generator.generate_detailed_analysis_report(
                    self.current_analysis_results
                )
                
            elif report_type == "assignment_report":
                report_df = self.report_generator.generate_assignment_report(
                    self.current_assignments
                )
                
            elif report_type == "aging_analysis":
                report_df = self.report_generator.generate_aging_analysis_report(
                    self.current_analysis_results
                )
                
            elif report_type == "comparison_report":
                report_df = self.report_generator.generate_comparison_report(
                    self.current_analysis_results,
                    selected_aracs
                )
            
            if report_df is not None and not report_df.empty:
                # Raporu önizlemede göster
                self.display_report_preview(report_df)
                self.current_report_df = report_df
                self.report_status_label.configure(text=f"Rapor oluşturuldu: {len(report_df)} kayıt")
                self.export_report_btn.configure(state="normal")
            else:
                self.report_status_label.configure(text="Rapor oluşturulamadı")
                messagebox.showerror("Hata", "Rapor oluşturulamadı")
                
            self.generate_report_btn.configure(state="normal")
            
        except Exception as e:
            logger.error(f"Rapor oluşturma hatası: {e}")
            messagebox.showerror("Hata", f"Rapor oluşturma hatası: {e}")
            self.report_status_label.configure(text="Rapor oluşturma hatası")
            self.generate_report_btn.configure(state="normal")
    
    def display_report_preview(self, df):
        """Raporu önizlemede göster"""
        try:
            # Mevcut verileri temizle
            for item in self.report_tree.get_children():
                self.report_tree.delete(item)
            
            if df.empty:
                return
            
            # Sütunları ayarla
            columns = list(df.columns)
            self.report_tree["columns"] = columns
            self.report_tree["show"] = "headings"
            
            # Başlıkları ayarla
            for col in columns:
                self.report_tree.heading(col, text=str(col))
                # Sütun genişliği
                if "ARAÇ" in str(col):
                    width = 80
                elif "Ünvan" in str(col) or "Sorumlu" in str(col):
                    width = 200
                elif "Bakiye" in str(col) or "Tutar" in str(col):
                    width = 120
                else:
                    width = 100
                self.report_tree.column(col, width=width)
            
            # Verileri ekle (sadece ilk 1000 satır performans için)
            max_rows = min(len(df), 1000)
            for idx in range(max_rows):
                row = df.iloc[idx]
                values = [str(val) if pd.notna(val) else "" for val in row]
                self.report_tree.insert("", "end", values=values)
            
            if len(df) > 1000:
                self.report_status_label.configure(
                    text=f"İlk 1000 satır gösteriliyor (Toplam: {len(df)})"
                )
                
        except Exception as e:
            logger.error(f"Rapor önizleme hatası: {e}")
    
    def export_report(self):
        """Raporu Excel'e aktar"""
        try:
            if not hasattr(self, 'current_report_df') or self.current_report_df is None:
                messagebox.showwarning("Uyarı", "Aktarılacak rapor yok")
                return
            
            # Dosya kaydetme dialogu
            from tkinter import filedialog
            
            report_type_names = {
                "arac_summary": "ARAÇ_Özet",
                "detailed_analysis": "Detaylı_Analiz",
                "assignment_report": "Atama_Raporu",
                "aging_analysis": "Yaşlandırma_Analizi",
                "comparison_report": "Karşılaştırma"
            }
            
            report_name = report_type_names.get(self.report_type_var.get(), "Rapor")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"{report_name}_{timestamp}.xlsx"
            
            file_path = filedialog.asksaveasfilename(
                title="Raporu Kaydet",
                defaultextension=".xlsx",
                initialfile=default_name,
                filetypes=[
                    ("Excel files", "*.xlsx"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            try:
                if file_path.endswith('.xlsx'):
                    # Excel formatında kaydet
                    success = self.report_generator.save_report_to_excel(
                        self.current_report_df, 
                        file_path, 
                        report_name
                    )
                else:
                    # CSV formatında kaydet
                    self.current_report_df.to_csv(file_path, index=False, encoding='utf-8-sig')
                    success = True
                
                if success:
                    messagebox.showinfo("Başarılı", f"Rapor kaydedildi:\n{file_path}")
                else:
                    messagebox.showerror("Hata", "Rapor kaydedilemedi")
                    
            except Exception as save_error:
                messagebox.showerror("Hata", f"Kaydetme hatası: {save_error}")
                
        except Exception as e:
            logger.error(f"Rapor export hatası: {e}")
            messagebox.showerror("Hata", f"Export hatası: {e}")
    
    def on_chart_type_change(self, choice):
        """Grafik türü değiştiğinde"""
        try:
            # ARAÇ dropdown'ını güncelle
            arac_list = ["Tüm ARAÇ'lar"]
            
            if hasattr(self, 'analysis_engine'):
                self.refresh_reports_arac_list()
            
            self.chart_arac_dropdown.configure(values=arac_list)
            
        except Exception as e:
            logger.error(f"Grafik türü değiştirme hatası: {e}")
    
    def refresh_reports_arac_list(self):
        """Reports tab'ındaki ARAÇ listesini yenile"""
        try:
            if not hasattr(self, 'analysis_engine'):
                return
                
            # Eğer "Tüm ARAÇ'lar" seçili değilse, checkbox'ları göster
            if hasattr(self, 'report_all_arac_var') and not self.report_all_arac_var.get():
                self.create_arac_selection_checkboxes()
                
        except Exception as e:
            logger.error(f"Reports ARAÇ listesi yenileme hatası: {e}")
    
    def create_chart(self):
        """Grafik oluştur"""
        if not hasattr(self, 'visualization_engine'):
            messagebox.showerror("Hata", "Analiz modülü mevcut değil")
            return
            
        try:
            if not self.current_analysis_results:
                messagebox.showwarning("Uyarı", "Önce analiz yapılmalıdır")
                return
            
            chart_type = self.chart_type_var.get()
            selected_arac = self.chart_arac_dropdown.get()
            
            # Mevcut grafik widget'larını temizle
            self.clear_chart_display()
            
            # Grafik türüne göre oluştur
            figure = None
            
            if chart_type == "ARAÇ Özet Grafiği":
                figure = self.visualization_engine.create_arac_summary_chart(
                    self.current_analysis_results
                )
                
            elif chart_type == "Yaşlandırma Analizi":
                figure = self.visualization_engine.create_aging_analysis_chart(
                    self.current_analysis_results
                )
                
            elif chart_type == "ARAÇ Karşılaştırma":
                # Seçili ARAÇ'ları al
                arac_list = None
                if selected_arac != "Tüm ARAÇ'lar":
                    arac_list = [selected_arac]
                
                figure = self.visualization_engine.create_comparison_chart(
                    self.current_analysis_results,
                    arac_list
                )
                
            elif chart_type == "İş Yükü Dağılımı":
                figure = self.visualization_engine.create_workload_distribution_chart(
                    self.current_assignments
                )
            
            if figure is not None:
                # Grafik gösterimini güncelle
                self.display_chart(figure)
                self.current_chart_figure = figure
                self.save_chart_btn.configure(state="normal")
            else:
                messagebox.showerror("Hata", "Grafik oluşturulamadı")
                
        except Exception as e:
            logger.error(f"Grafik oluşturma hatası: {e}")
            messagebox.showerror("Hata", f"Grafik oluşturma hatası: {e}")
    
    def clear_chart_display(self):
        """Grafik gösterim alanını temizle"""
        try:
            # Mevcut widget'ları temizle
            for widget in self.chart_display_frame.winfo_children():
                widget.destroy()
        except Exception as e:
            logger.error(f"Grafik temizleme hatası: {e}")
    
    def display_chart(self, figure):
        """Grafiği gösterim alanında göster"""
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
            import tkinter as tk
            
            # Canvas oluştur
            canvas = FigureCanvasTkAgg(figure, self.chart_display_frame)
            canvas.draw()
            
            # Canvas widget'ını yerleştir
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(fill="both", expand=True)
            
            # Toolbar ekle (zoom, pan vb. için)
            toolbar_frame = ctk.CTkFrame(self.chart_display_frame)
            toolbar_frame.pack(fill="x", side="bottom")
            
            # Toolbar için tkinter Frame kullan (CustomTkinter uyumlu değil)
            toolbar_tk_frame = tk.Frame(toolbar_frame)
            toolbar_tk_frame.pack()
            
            toolbar = NavigationToolbar2Tk(canvas, toolbar_tk_frame)
            toolbar.update()
            
            logger.info("Grafik başarıyla gösterildi")
            
        except Exception as e:
            logger.error(f"Grafik gösterme hatası: {e}")
            # Hata durumunda mesaj göster
            error_label = ctk.CTkLabel(
                self.chart_display_frame,
                text=f"Grafik gösterme hatası: {str(e)}",
                text_color="red"
            )
            error_label.pack(expand=True)
    
    def save_chart(self):
        """Grafiği kaydet"""
        try:
            if not hasattr(self, 'current_chart_figure') or self.current_chart_figure is None:
                messagebox.showwarning("Uyarı", "Kaydedilecek grafik yok")
                return
            
            # Dosya kaydetme dialogu
            from tkinter import filedialog
            
            chart_type_names = {
                "ARAÇ Özet Grafiği": "ARAÇ_Özet",
                "Yaşlandırma Analizi": "Yaşlandırma_Analizi",
                "ARAÇ Karşılaştırma": "ARAÇ_Karşılaştırma",
                "İş Yükü Dağılımı": "İş_Yükü_Dağılımı"
            }
            
            chart_name = chart_type_names.get(self.chart_type_var.get(), "Grafik")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"{chart_name}_{timestamp}.png"
            
            file_path = filedialog.asksaveasfilename(
                title="Grafiği Kaydet",
                defaultextension=".png",
                initialfile=default_name,
                filetypes=[
                    ("PNG files", "*.png"),
                    ("PDF files", "*.pdf"),
                    ("SVG files", "*.svg"),
                    ("JPEG files", "*.jpg"),
                    ("All files", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            try:
                # DPI ayarla
                dpi = 300 if file_path.endswith('.pdf') else 150
                
                success = self.visualization_engine.save_chart(
                    self.current_chart_figure,
                    file_path,
                    dpi=dpi
                )
                
                if success:
                    messagebox.showinfo("Başarılı", f"Grafik kaydedildi:\n{file_path}")
                else:
                    messagebox.showerror("Hata", "Grafik kaydedilemedi")
                    
            except Exception as save_error:
                messagebox.showerror("Hata", f"Kaydetme hatası: {save_error}")
                
        except Exception as e:
            logger.error(f"Grafik kaydetme hatası: {e}")
            messagebox.showerror("Hata", f"Grafik kaydetme hatası: {e}")
    
    def refresh_charts_data(self):
        """Grafik verilerini yenile"""
        try:
            if not hasattr(self, 'analysis_engine'):
                return
                
            # ARAÇ dropdown'ını güncelle
            arac_list = ["Tüm ARAÇ'lar"]
            
            if hasattr(self, 'analysis_engine'):
                available_aracs = self.analysis_engine.get_arac_list()
                arac_list.extend(available_aracs)
            
            if hasattr(self, 'chart_arac_dropdown'):
                self.chart_arac_dropdown.configure(values=arac_list)
            
        except Exception as e:
            logger.error(f"Grafik veri yenileme hatası: {e}")
    
    def update_all_tabs(self):
        """Tüm tab'ların verilerini güncelle"""
        try:
            if not hasattr(self, 'analysis_engine'):
                return
                
            # Assignment tab güncelle
            if hasattr(self, 'assignment_arac_dropdown'):
                arac_list = self.analysis_engine.get_arac_list()
                if arac_list:
                    self.assignment_arac_dropdown.configure(values=arac_list)
            
            if hasattr(self, 'update_assignment_tree'):
                self.update_assignment_tree()
            
            # Reports tab güncelle
            if hasattr(self, 'create_arac_selection_checkboxes') and not self.report_all_arac_var.get():
                self.create_arac_selection_checkboxes()
            
            # Charts tab güncelle
            if hasattr(self, 'refresh_charts_data'):
                self.refresh_charts_data()
            
            logger.info("Tüm tab'lar güncellendi")
            
        except Exception as e:
            logger.error(f"Tab güncelleme hatası: {e}")