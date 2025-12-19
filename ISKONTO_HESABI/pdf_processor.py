# -*- coding: utf-8 -*-
"""
ISKONTO_HESABI - PDF İşleyici Modülü
PDF fiyat listelerinden veri çıkarma ve işleme
"""

import pdfplumber
import re
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path
import sys
import os

# Shared modül import
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.utils import setup_logging, get_logs_dir

logger = setup_logging("ISKONTO_PDF")


class PDFProcessor:
    """PDF fiyat listesi işleyici"""
    
    def __init__(self):
        self.categories = {
            'Bütün Piliç Ürünleri': [],
            'Kanat Ürünleri': [],
            'But Ürünleri': [],
            'Göğüs Ürünleri': [],
            'Sakatat Ürünleri': [],
            'Yan Ürünler': []
        }
        self.raw_data = []
        self.processed_codes = set()
        self.pdf_files = {}
        
        # Performans için regex pattern'leri önceden derle
        self.code_pattern = re.compile(r'^(D?[A-Z]{2,4}\d{3}(?:\.\d{2})?(?:\.\d{1,2})?(?:\-\d)?)\s*$')
        self.price_pattern = re.compile(r'(\d{2,3}[,\.]\d{2})')
    
    def extract_data_from_pdf(self, pdf_path: str, pdf_type: str = "normal") -> bool:
        """PDF'den veri çıkarır"""
        try:
            logger.info(f"PDF işleniyor: {pdf_path}, Tip: {pdf_type}")
            self.clear_data()
            
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    logger.info(f"Sayfa {page_num + 1} işleniyor...")
                    
                    # Önce tabloları dene
                    tables = page.extract_tables()
                    if tables:
                        logger.info(f"Sayfa {page_num + 1}'de {len(tables)} tablo bulundu")
                        self._process_tables(tables, pdf_type, page_num + 1)
                    else:
                        # Fallback: Metin bazlı çıkarma
                        self._process_text(page, pdf_type, page_num + 1)
                
                self._print_results()
                return True
                
        except FileNotFoundError:
            logger.error(f"PDF dosyası bulunamadı: {pdf_path}")
            return False
        except PermissionError:
            logger.error(f"PDF dosyasına erişim izni yok: {pdf_path}")
            return False
        except Exception as e:
            logger.error(f"PDF işleme hatası: {type(e).__name__}: {e}", exc_info=True)
            return False
    
    def _process_tables(self, tables: List, pdf_type: str, page_num: int):
        """Tabloları işle"""
        for table_idx, table in enumerate(tables):
            if not table:
                continue
            for row_idx, row in enumerate(table):
                if row and any(cell for cell in row if cell):
                    self._parse_table_row(row, pdf_type, page_num, f"Tablo-{table_idx}-Satır-{row_idx}")
    
    def _process_text(self, page, pdf_type: str, page_num: int):
        """Metin bazlı işleme"""
        text = page.extract_text()
        if text:
            logger.info(f"Sayfa {page_num}'de metin işleniyor...")
            for line_idx, line in enumerate(text.split('\n')):
                if line.strip():
                    self._parse_text_line(line, pdf_type, page_num, line_idx)
    
    def _parse_table_row(self, row: List, pdf_type: str, page_num: int, row_info: str):
        """Tablo satırını parse eder"""
        if not row or len(row) < 3:
            return
        
        for i in range(min(3, len(row))):
            if not row[i]:
                continue
                
            cell = str(row[i]).strip()
            match = self.code_pattern.match(cell)
            
            if match:
                product_code = match.group(1).strip()
                category = self._determine_category_by_position(product_code, row_info, page_num)
                
                if not category:
                    logger.debug(f"KATEGORİ BULUNAMADI: {product_code}")
                    continue
                
                duplicate_key = f"{product_code}-{category}"
                if duplicate_key in self.processed_codes:
                    logger.debug(f"DUPLİKASYON: {product_code} {category}'de zaten işlendi")
                    continue
                
                product_name = self._extract_product_name(row, i, pdf_type)
                price_without_vat, price_with_vat = self._extract_prices_from_row(row, i + 2)
                
                if product_name and price_without_vat and price_with_vat:
                    kdv_rate = (price_with_vat / price_without_vat - 1) * 100
                    if not (0.5 <= kdv_rate <= 1.5):
                        logger.warning(f"Anormal KDV oranı {kdv_rate:.2f}% - {product_code}")
                    
                    product = {
                        'code': product_code,
                        'name': self._clean_product_name(product_name),
                        'price_without_vat': price_without_vat,
                        'price_with_vat': price_with_vat,
                        'category': category
                    }
                    
                    self.categories[category].append(product)
                    self.processed_codes.add(duplicate_key)
                    logger.info(f"✓ [{pdf_type} - {category}] {product['name']}: {price_without_vat:.2f} / {price_with_vat:.2f}")
                    break
    
    def _extract_product_name(self, row: List, code_index: int, pdf_type: str) -> str:
        """Ürün adını çıkar"""
        if code_index + 1 < len(row) and row[code_index + 1]:
            product_name = str(row[code_index + 1]).strip()
            
            if pdf_type == "dondurulmus":
                product_name = product_name.replace("DON.", "DONDURULMUŞ")
            
            return product_name
        return ""
    
    def _extract_prices_from_row(self, row: List, start_index: int) -> Tuple[Optional[float], Optional[float]]:
        """Satırdan fiyatları çıkar"""
        prices = []
        
        for j in range(start_index, len(row)):
            if row[j]:
                cell_value = str(row[j]).strip()
                
                if '%' in cell_value or 'fark' in cell_value.lower():
                    continue
                
                price = self._extract_price_from_text(cell_value)
                if price and 5 <= price <= 2000:
                    prices.append(price)
        
        if len(prices) < 2:
            return None, None
        
        price_without_vat = prices[-2] if len(prices) >= 2 else prices[0]
        price_with_vat = prices[-1]
        
        if price_without_vat > price_with_vat:
            price_without_vat, price_with_vat = price_with_vat, price_without_vat
        
        return price_without_vat, price_with_vat
    
    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """Metinden fiyat çıkar"""
        try:
            clean = text.strip().replace(',', '.')
            clean = re.sub(r'[^\d.]', '', clean)
            if clean:
                return float(clean)
        except:
            pass
        return None
    
    def _determine_category_by_position(self, product_code: str, row_info: str, page_num: int) -> Optional[str]:
        """PDF'deki konuma ve ürün koduna göre kategori belirler"""
        table_match = re.search(r'Tablo-(\d+)', row_info)
        if table_match:
            table_num = int(table_match.group(1))
            
            table_category_map = {
                0: 'Bütün Piliç Ürünleri',
                1: 'Bütün Piliç Ürünleri',
                2: 'Kanat Ürünleri',
                3: 'Kanat Ürünleri',
                4: 'But Ürünleri',
                5: 'But Ürünleri',
                6: 'Göğüs Ürünleri',
                7: 'Göğüs Ürünleri',
                8: 'Sakatat Ürünleri',
                9: 'Sakatat Ürünleri',
                10: 'Yan Ürünler',
                11: 'Yan Ürünler',
            }
            
            if table_num in table_category_map:
                return table_category_map[table_num]
        
        return self._determine_category_by_code(product_code)
    
    def _determine_category_by_code(self, product_code: str) -> Optional[str]:
        """Ürün koduna göre kategori belirler"""
        code_upper = product_code.upper()
        
        # Bütün piliç
        if code_upper.startswith(('BP', 'BPD', 'TP', 'TPD')):
            return 'Bütün Piliç Ürünleri'
        
        # Kanat
        if code_upper.startswith(('KN', 'KND', 'DKN')):
            return 'Kanat Ürünleri'
        
        # But
        if code_upper.startswith(('BT', 'BTD', 'DBT', 'PLK', 'PLO')):
            return 'But Ürünleri'
        
        # Göğüs
        if code_upper.startswith(('GS', 'GSD', 'DGS', 'BFE', 'STK')):
            return 'Göğüs Ürünleri'
        
        # Sakatat
        if code_upper.startswith(('SK', 'SKD', 'CG', 'YRK', 'TLK')):
            return 'Sakatat Ürünleri'
        
        # Yan ürünler
        if code_upper.startswith(('YN', 'SOS', 'MRN', 'MARN')):
            return 'Yan Ürünler'
        
        return None
    
    def _clean_product_name(self, name: str) -> str:
        """Ürün adını temizle"""
        if not name:
            return ""
        
        name = re.sub(r'\s+', ' ', name)
        name = name.strip()
        name = re.sub(r'^[\d\.\-\s]+', '', name)
        
        return name
    
    def _parse_text_line(self, line: str, pdf_type: str, page_num: int, line_idx: int):
        """Metin satırını parse et"""
        code_matches = list(self.code_pattern.finditer(line))
        
        for match in code_matches:
            product_code = match.group(1).strip()
            category = self._determine_category_by_code(product_code)
            
            if not category:
                continue
            
            duplicate_key = f"{product_code}-{category}"
            if duplicate_key in self.processed_codes:
                continue
            
            start_pos = match.end()
            remaining = line[start_pos:].strip()
            
            price_matches = self.price_pattern.findall(remaining)
            prices = []
            
            for price_str in price_matches[-2:]:
                if '%' not in price_str:
                    price = self._extract_price_from_text(price_str)
                    if price and 10 <= price <= 2000:
                        prices.append(price)
            
            if len(prices) < 2:
                continue
            
            price_without_vat, price_with_vat = prices[0], prices[1]
            
            product_name = remaining
            for price_str in price_matches:
                product_name = product_name.replace(price_str, '')
            
            product_name = re.sub(r'%.*?\d+[,\.]\d{2}', '', product_name)
            product_name = self._clean_product_name(product_name)
            
            if pdf_type == "dondurulmus" and "DON." in product_name:
                product_name = product_name.replace("DON.", "DONDURULMUŞ")
            
            if product_name and len(product_name) > 3:
                product = {
                    'code': product_code,
                    'name': product_name,
                    'price_without_vat': price_without_vat,
                    'price_with_vat': price_with_vat,
                    'category': category
                }
                
                self.categories[category].append(product)
                self.processed_codes.add(duplicate_key)
                logger.info(f"✓ [{pdf_type} - {category}] [{product_code}] {product['name']}")
    
    def _print_results(self):
        """Sonuçları yazdır"""
        print("\n" + "="*80)
        print("PARSE EDİLEN ÜRÜNLER:")
        print("="*80)
        total = 0
        for cat_name, products in self.categories.items():
            count = len(products)
            total += count
            if count > 0:
                print(f"\n✓ {cat_name}: {count} ürün")
                print("-" * 60)
                for idx, product in enumerate(products[:5], 1):
                    print(f"  {idx:2d}. [{product['code']}] {product['name']}: {product['price_without_vat']:.2f} / {product['price_with_vat']:.2f} TL")
                if len(products) > 5:
                    print(f"  ... ve {len(products) - 5} ürün daha")
            else:
                print(f"\n✗ {cat_name}: 0 ürün")
        
        print(f"\n{'='*80}")
        print(f"TOPLAM: {total} ürün bulundu")
        print(f"{'='*80}")
        
        if total == 0:
            logger.warning("HİÇ ÜRÜN BULUNAMADI! PDF formatını kontrol edin.")
        else:
            logger.info(f"BAŞARILI: Toplam {total} benzersiz ürün işlendi")
    
    def apply_discounts(self, discount_rates: Dict[str, float]) -> Dict:
        """İskonto oranlarını uygular - %1 KDV ile"""
        discounted_data = {}
        
        for category, products in self.categories.items():
            if not products:
                continue
                
            discount_rate = discount_rates.get(category, 0.0)
            discount_multiplier = 1 - (discount_rate / 100)
            
            discounted_products = []
            for product in products:
                discounted_without_vat = round(product['price_without_vat'] * discount_multiplier, 2)
                kdv_multiplier = 1.01  # %1 KDV
                discounted_with_vat = round(discounted_without_vat * kdv_multiplier, 2)
                
                discounted_product = {
                    'name': product['name'],
                    'price_without_vat': discounted_without_vat,
                    'price_with_vat': discounted_with_vat,
                    'original_price_without_vat': product['price_without_vat'],
                    'original_price_with_vat': product['price_with_vat']
                }
                discounted_products.append(discounted_product)
            
            if discounted_products:
                discounted_data[category] = discounted_products
        
        return discounted_data
    
    def get_categories(self) -> List[str]:
        """Mevcut kategorileri döner"""
        return list(self.categories.keys())
    
    def get_product_count(self) -> int:
        """Toplam ürün sayısını döner"""
        return sum(len(products) for products in self.categories.values())
    
    def clear_data(self):
        """Verileri temizler"""
        for category in self.categories:
            self.categories[category] = []
        self.processed_codes.clear()
    
    def determine_pdf_type(self, pdf_path: str) -> str:
        """PDF tipini belirler"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages[:2]:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text.lower()
                
                if 'dondurulmuş' in text or 'don.' in text:
                    return 'dondurulmus'
                elif 'gramaj' in text or 'soslu' in text:
                    return 'gramaj'
                else:
                    return 'normal'
        except Exception as e:
            logger.warning(f"PDF tipi belirlenemedi: {e}")
            return 'normal'
