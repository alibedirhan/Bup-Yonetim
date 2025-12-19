# -*- coding: utf-8 -*-
"""
ISKONTO_HESABI - Export Manager Modülü
Excel ve PDF dışa aktarma işlemleri
"""

import os
from datetime import datetime
import pandas as pd
from fpdf import FPDF
from tkinter import filedialog
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Shared modül import
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.utils import (
    setup_logging, get_exports_dir, safe_turkish_text,
    get_clean_filename, get_timestamp, get_date_display
)
from shared.components import show_success, show_error, show_warning

logger = setup_logging("ISKONTO_EXPORT")


class SafePDF(FPDF):
    """Güvenli UTF-8 destekli PDF sınıfı"""
    
    def __init__(self):
        super().__init__()
        self.font_loaded = False
        self._load_fonts()
    
    def _load_fonts(self):
        """Fontları güvenli şekilde yükle"""
        try:
            self.set_font('Helvetica', '', 12)
            
            windows_paths = [
                'C:/Windows/Fonts/arial.ttf',
                'C:/Windows/Fonts/arialbd.ttf'
            ]
            
            linux_paths = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
            ]
            
            paths_to_try = [(windows_paths[0], windows_paths[1])]
            for i in range(0, len(linux_paths), 2):
                if i+1 < len(linux_paths):
                    paths_to_try.append((linux_paths[i], linux_paths[i+1]))
            
            for normal_path, bold_path in paths_to_try:
                try:
                    if Path(normal_path).exists() and Path(bold_path).exists():
                        self.add_font('Arial', '', normal_path, uni=True)
                        self.add_font('Arial', 'B', bold_path, uni=True)
                        self.font_loaded = True
                        break
                except Exception:
                    continue
                    
        except Exception as e:
            logger.warning(f"Font yükleme başarısız: {e}")
    
    def set_font(self, family, style='', size=0):
        """Güvenli font ayarlama"""
        try:
            if self.font_loaded and family == 'Arial':
                super().set_font('Arial', style, size)
            else:
                super().set_font('Helvetica', style, size)
        except Exception:
            try:
                super().set_font('Helvetica', '', 12)
            except:
                pass
    
    def header(self):
        pass
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Sayfa {self.page_no()}', 0, 0, 'C')


class ExportManager:
    """Excel ve PDF dışa aktarma yöneticisi"""
    
    def __init__(self):
        self.exports_dir = get_exports_dir()
        self._setup_directories()
    
    def _setup_directories(self):
        """Gerekli dizinleri oluştur"""
        (self.exports_dir / "excel").mkdir(parents=True, exist_ok=True)
        (self.exports_dir / "pdf").mkdir(parents=True, exist_ok=True)
        logger.info(f"Export dizinleri hazır: {self.exports_dir}")
    
    def export_to_excel_multi(self, all_pdf_data: Dict, discount_vars: Dict):
        """Çoklu PDF'i Excel'e aktar"""
        try:
            if not all_pdf_data:
                show_warning("Uyarı", "Dışa aktarılacak veri bulunamadı!")
                return
            
            timestamp = get_timestamp()
            initial_filename = f"Bupilic_Iskontolu_Fiyat_Listeleri_{timestamp}.xlsx"
            
            file_path = filedialog.asksaveasfilename(
                title="Excel olarak kaydet",
                defaultextension=".xlsx",
                initialfile=initial_filename,
                initialdir=str(self.exports_dir / "excel"),
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                summary_data = self._create_multi_summary(all_pdf_data, discount_vars)
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='OZET', index=False)
                
                for sheet_idx, (pdf_name, pdf_data) in enumerate(all_pdf_data.items(), 1):
                    clean_name = get_clean_filename(pdf_name, max_length=25)
                    sheet_name = f"{sheet_idx}_{clean_name}"[:31]
                    
                    sheet_data = []
                    
                    for category, products in pdf_data['data'].items():
                        if not products:
                            continue
                        
                        discount_rate = discount_vars[category].get()
                        
                        sheet_data.append({
                            'Kategori': category,
                            'Ürün Adı': f'%{discount_rate:.1f} İSKONTO',
                            'Orj. KDV Hariç': '',
                            'Orj. KDV Dahil': '',
                            'İsk. KDV Hariç': '',
                            'İsk. KDV Dahil': '',
                            'İskonto %': discount_rate,
                            'İskonto TL': ''
                        })
                        
                        for product in products:
                            iskonto = product.get('original_price_with_vat', 0) - product['price_with_vat']
                            
                            sheet_data.append({
                                'Kategori': category,
                                'Ürün Adı': product['name'],
                                'Orj. KDV Hariç': product.get('original_price_without_vat', 0),
                                'Orj. KDV Dahil': product.get('original_price_with_vat', 0),
                                'İsk. KDV Hariç': product['price_without_vat'],
                                'İsk. KDV Dahil': product['price_with_vat'],
                                'İskonto %': discount_rate,
                                'İskonto TL': round(iskonto, 2)
                            })
                        
                        if sheet_data:
                            sheet_data.append({col: '' for col in sheet_data[0].keys()})
                    
                    if sheet_data:
                        df = pd.DataFrame(sheet_data)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        self._format_excel_sheet(writer, sheet_name)
            
            logger.info(f"Excel kaydedildi: {file_path}")
            show_success("Başarılı", f"Excel dosyası kaydedildi:\n{file_path}")
            
        except PermissionError:
            show_error("Hata", "Dosya başka bir program tarafından kullanılıyor.")
        except Exception as e:
            logger.error(f"Excel hatası: {e}")
            show_error("Hata", f"Excel kaydetme hatası: {str(e)}")
    
    def export_to_pdf_multi(self, all_pdf_data: Dict, discount_vars: Dict):
        """Her PDF için ayrı iskontolu PDF oluştur"""
        try:
            if not all_pdf_data:
                show_warning("Uyarı", "Dışa aktarılacak veri bulunamadı!")
                return
            
            save_dir = filedialog.askdirectory(
                title="PDF klasörü seçin",
                initialdir=str(self.exports_dir / "pdf")
            )
            
            if not save_dir:
                return
            
            saved_files = []
            current_date = datetime.now().strftime("%d.%m.%Y")
            
            for pdf_name, pdf_data in all_pdf_data.items():
                clean_name = get_clean_filename(pdf_name)
                output_filename = f"{clean_name}_Iskontolu_{current_date}.pdf"
                file_path = os.path.join(save_dir, output_filename)
                
                pdf = SafePDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                
                pdf.add_page()
                self._add_cover_page(pdf, pdf_name, pdf_data['data'], discount_vars)
                
                pdf.add_page()
                self._add_summary_page(pdf, pdf_data['data'], discount_vars)
                
                for category, products in pdf_data['data'].items():
                    if not products:
                        continue
                    
                    discount_rate = discount_vars[category].get()
                    pdf.add_page()
                    safe_cat = safe_turkish_text(category)
                    self._add_category_page(pdf, safe_cat, products, discount_rate)
                
                pdf.output(file_path)
                saved_files.append(output_filename)
                logger.info(f"PDF kaydedildi: {file_path}")
            
            if saved_files:
                show_success("Başarılı", f"{len(saved_files)} PDF dosyası kaydedildi.")
            
        except Exception as e:
            logger.error(f"PDF hatası: {e}")
            show_error("Hata", f"PDF kaydetme hatası: {str(e)}")
    
    def _create_multi_summary(self, all_pdf_data: Dict, discount_vars: Dict) -> List[Dict]:
        """Özet verisi oluştur"""
        summary = []
        
        for pdf_name, pdf_data in all_pdf_data.items():
            pdf_summary = {
                'PDF Dosyası': pdf_name,
                'Kategori': 0,
                'Ürün': 0,
                'Toplam Orijinal': 0,
                'Toplam İskontolu': 0,
                'Toplam İskonto': 0
            }
            
            for category, products in pdf_data['data'].items():
                if products:
                    pdf_summary['Kategori'] += 1
                    pdf_summary['Ürün'] += len(products)
                    
                    for product in products:
                        pdf_summary['Toplam Orijinal'] += product.get('original_price_with_vat', 0)
                        pdf_summary['Toplam İskontolu'] += product['price_with_vat']
                        pdf_summary['Toplam İskonto'] += (
                            product.get('original_price_with_vat', 0) - product['price_with_vat']
                        )
            
            for key in ['Toplam Orijinal', 'Toplam İskontolu', 'Toplam İskonto']:
                pdf_summary[key] = round(pdf_summary[key], 2)
            
            summary.append(pdf_summary)
        
        return summary
    
    def _format_excel_sheet(self, writer, sheet_name: str):
        """Excel formatla"""
        try:
            worksheet = writer.sheets[sheet_name]
            widths = {'A': 25, 'B': 50, 'C': 15, 'D': 15, 'E': 15, 'F': 15, 'G': 12, 'H': 15}
            for col, width in widths.items():
                worksheet.column_dimensions[col].width = width
        except Exception as e:
            logger.warning(f"Format hatası: {e}")
    
    def _add_cover_page(self, pdf, pdf_name: str, data: Dict, discount_vars: Dict):
        """Kapak sayfası"""
        pdf.set_font("Arial", 'B', 24)
        pdf.ln(50)
        pdf.cell(0, 15, "BUPILIC", 0, 1, 'C')
        pdf.set_font("Arial", '', 18)
        pdf.cell(0, 10, "ISKONTOLU FIYAT LISTESI", 0, 1, 'C')
        
        pdf.ln(20)
        pdf.set_font("Arial", '', 14)
        pdf.cell(0, 10, safe_turkish_text(get_clean_filename(pdf_name)), 0, 1, 'C')
        
        pdf.ln(10)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Tarih: {get_date_display()}", 0, 1, 'C')
        
        pdf.ln(30)
        total = sum(len(p) for p in data.values() if p)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, f"Toplam Urun: {total}", 0, 1, 'C')
    
    def _add_summary_page(self, pdf, data: Dict, discount_vars: Dict):
        """Özet sayfası"""
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "OZET", 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(60, 8, "Kategori", 1, 0, 'C')
        pdf.cell(25, 8, "Urun", 1, 0, 'C')
        pdf.cell(25, 8, "Iskonto %", 1, 0, 'C')
        pdf.cell(35, 8, "Iskonto TL", 1, 1, 'C')
        
        pdf.set_font("Arial", '', 9)
        total_products = 0
        total_discount = 0
        
        for category, products in data.items():
            if products:
                count = len(products)
                rate = discount_vars[category].get()
                discount = sum(p.get('original_price_with_vat', 0) - p['price_with_vat'] for p in products)
                
                safe_cat = safe_turkish_text(category)[:30]
                pdf.cell(60, 7, safe_cat, 1, 0, 'L')
                pdf.cell(25, 7, str(count), 1, 0, 'C')
                pdf.cell(25, 7, f"{rate:.1f}", 1, 0, 'C')
                pdf.cell(35, 7, f"{discount:.2f}", 1, 1, 'R')
                
                total_products += count
                total_discount += discount
        
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(60, 8, "TOPLAM", 1, 0, 'L')
        pdf.cell(25, 8, str(total_products), 1, 0, 'C')
        pdf.cell(25, 8, "-", 1, 0, 'C')
        pdf.cell(35, 8, f"{total_discount:.2f}", 1, 1, 'R')
    
    def _add_category_page(self, pdf, category: str, products: List[Dict], discount_rate: float):
        """Kategori sayfası"""
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"{category} - %{discount_rate:.1f} Iskonto", 0, 1, 'C')
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(70, 7, "Urun", 1, 0, 'C')
        pdf.cell(30, 7, "Orijinal", 1, 0, 'C')
        pdf.cell(30, 7, "Iskontolu", 1, 0, 'C')
        pdf.cell(25, 7, "Kazanc", 1, 1, 'C')
        
        pdf.set_font("Arial", '', 8)
        for product in products:
            name = safe_turkish_text(product['name'])[:35]
            orig = product.get('original_price_with_vat', 0)
            disc = product['price_with_vat']
            save = orig - disc
            
            pdf.cell(70, 6, name, 1, 0, 'L')
            pdf.cell(30, 6, f"{orig:.2f}", 1, 0, 'R')
            pdf.cell(30, 6, f"{disc:.2f}", 1, 0, 'R')
            pdf.cell(25, 6, f"{save:.2f}", 1, 1, 'R')
    
    # Geriye uyumluluk
    def export_to_excel(self, data, discount_vars):
        all_data = {"Fiyat_Listesi": {"data": data, "type": "normal", "path": ""}}
        self.export_to_excel_multi(all_data, discount_vars)
    
    def export_to_pdf(self, data, discount_vars):
        all_data = {"Fiyat_Listesi": {"data": data, "type": "normal", "path": ""}}
        self.export_to_pdf_multi(all_data, discount_vars)
