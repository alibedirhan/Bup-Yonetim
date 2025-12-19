#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - İşleme Motoru
Cari yaşlandırma raporunu işleyen ana mantık
"""

import pandas as pd
import numpy as np
import re
import logging
from pathlib import Path
from copy import deepcopy

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelProcessorError(Exception):
    """Excel işleme için özel hata sınıfı"""
    pass

class ExcelProcessor:
    def __init__(self):
        self.original_df = None
        self.processed_df = None
        self._backup_df = None
        
    def process_excel(self, file_path, progress_callback=None):
        """
        Excel dosyasını işle
        """
        try:
            # 1. Dosyayı oku ve validate et
            if progress_callback:
                progress_callback(0.1, "Dosya okunuyor...")
            
            # Dosya doğrulaması
            if not Path(file_path).exists():
                raise ExcelProcessorError("Dosya bulunamadı")
            
            if not Path(file_path).suffix.lower() in ['.xlsx', '.xls']:
                raise ExcelProcessorError("Geçersiz dosya formatı")
            
            try:
                df = pd.read_excel(file_path, header=None)
            except Exception as e:
                raise ExcelProcessorError(f"Dosya okuma hatası: {str(e)}")
            
            if df.empty:
                raise ExcelProcessorError("Dosya boş")
            
            # Orijinal veriyi sakla
            self.original_df = df.copy()
            self._backup_df = df.copy()
            
            # 2. İlk 2 satırı sil
            if progress_callback:
                progress_callback(0.2, "İlk 2 satır siliniyor...")
            
            if len(df) < 3:
                raise ExcelProcessorError("Dosyada yeterli satır yok")
            
            df = df.iloc[2:].reset_index(drop=True)
            
            # 3. Başlıkları ayarla (3. satır başlık olacak)
            if len(df) == 0:
                raise ExcelProcessorError("Başlık ayarlamak için yeterli veri yok")
            
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
            
            # Boş sütun adlarını düzelt
            new_columns = []
            for i, col in enumerate(df.columns):
                if pd.isna(col) or str(col).strip() == '':
                    new_columns.append(f"Sütun_{i+1}")
                else:
                    new_columns.append(str(col).strip())
            df.columns = new_columns
            
            # 4. Cari Ünvan boş olanları sil
            if progress_callback:
                progress_callback(0.3, "Boş cari ünvanlar temizleniyor...")
            df = self.clean_empty_cari_unvan(df)
            
            # 5. Kategori işleme
            if progress_callback:
                progress_callback(0.4, "Kategoriler işleniyor...")
            df = self.process_categories(df)
            
            # 6. 0-7 Gün sonrası boş satırları sil
            if progress_callback:
                progress_callback(0.5, "Veri olmayan satırlar temizleniyor...")
            df = self.remove_empty_rows_after_07(df)
            
            # 7. Tamamen boş sütunları kaldır
            if progress_callback:
                progress_callback(0.6, "Boş sütunlar kaldırılıyor...")
            df = self.remove_empty_columns(df)
            
            # 8. Diğer Bakiye hesapla - FORMATLAMA YAPMADAN ÖNCE!
            if progress_callback:
                progress_callback(0.7, "Diğer bakiye hesaplanıyor...")
            df = self.calculate_diger_bakiye(df)
            
            # 9. Sayı formatlarını düzenle - EN SON YAPILACAK
            if progress_callback:
                progress_callback(0.9, "Sayı formatları düzenleniyor...")
            df = self.format_all_numbers(df)
            
            if progress_callback:
                progress_callback(1.0, "İşlem tamamlandı!")
            
            self.processed_df = df
            logger.info(f"İşlem başarıyla tamamlandı: {len(df)} satır işlendi")
            return df
            
        except ExcelProcessorError:
            # Excel processor hatalarını aynen fırlat
            raise
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {str(e)}")
            raise ExcelProcessorError(f"İşleme hatası: {str(e)}")
    
    def find_column(self, pattern, columns):
        """Sütun adını güvenli şekilde bul"""
        pattern_lower = pattern.lower()
        
        # Önce tam eşleşme ara
        for col in columns:
            if pattern_lower == str(col).lower():
                return col
        
        # Sonra kısmi eşleşme ara
        for col in columns:
            if pattern_lower in str(col).lower():
                return col
        
        logger.warning(f"'{pattern}' sütunu bulunamadı")
        return None
    
    def clean_empty_cari_unvan(self, df):
        """Cari Ünvan boş olanları temizle"""
        cari_col = self.find_column('Cari Ünvan', df.columns)
        if not cari_col:
            logger.warning("Cari Ünvan sütunu bulunamadı, temizleme atlandı")
            return df
        
        initial_count = len(df)
        
        try:
            df = df[df[cari_col].notna()]
            df = df[df[cari_col].astype(str).str.strip() != '']
            
            removed_count = initial_count - len(df)
            if removed_count > 0:
                logger.info(f"{removed_count} boş cari ünvan satırı silindi")
            
            return df.reset_index(drop=True)
            
        except Exception as e:
            logger.error(f"Cari ünvan temizleme hatası: {e}")
            return df
    
    def process_categories(self, df):
        """Kategori sütununu işle - DÜZELTİLMİŞ VERSİYON"""
        # Kategori sütununu bul
        kategori_col = None
        for col in df.columns:
            if 'kategori' in str(col).lower():
                kategori_col = col
                break
        
        if not kategori_col:
            logger.warning("Kategori sütunu bulunamadı")
            return df
        
        try:
            # Orijinal değerleri backup'la
            original_values = df[kategori_col].copy()
            
            # Yeni değerler listesi
            new_values = []
            for val in df[kategori_col]:
                if pd.isna(val):
                    new_values.append(val)
                else:
                    val_str = str(val)
                    # ARAÇ kelimesi var mı?
                    if 'ARAÇ' in val_str.upper():
                        # DÜZELTME: ARAÇ numarasını güvenli şekilde çıkar
                        arac_num = self.extract_arac_number_safe(val_str)
                        new_values.append(arac_num)
                    else:
                        # ARAÇ yoksa olduğu gibi bırak
                        new_values.append(val_str)
            
            df[kategori_col] = new_values
            
            # Sayısal ve sayısal olmayanları ayır ve sırala
            try:
                # DÜZELTME: Sayısal dönüşümde daha güvenli yöntem
                df['_is_numeric'] = pd.to_numeric(df[kategori_col], errors='coerce').notna()
                df['_numeric_val'] = pd.to_numeric(df[kategori_col], errors='coerce')
                
                # Önce sayısallar (küçükten büyüğe), sonra diğerleri
                df = df.sort_values(
                    by=['_is_numeric', '_numeric_val', kategori_col],
                    ascending=[False, True, True],
                    na_position='last'
                )
                
                # Yardımcı sütunları sil
                df = df.drop(columns=['_is_numeric', '_numeric_val'])
                
            except Exception as sort_error:
                logger.error(f"Kategori sıralama hatası: {sort_error}")
                # Sıralama başarısız olursa orijinal sıralamayı koru
                
            logger.info("Kategori işleme tamamlandı")
            return df.reset_index(drop=True)
            
        except Exception as e:
            logger.error(f"Kategori işleme hatası: {e}")
            # Hata durumunda orijinal değerleri geri yükle
            try:
                df[kategori_col] = original_values
            except:
                pass
            return df

    def extract_arac_number_safe(self, text):
        """
        Metinden ARAÇ numarasını GÜVENLİ şekilde çıkar
        [İZMİR ARAÇ 01] İZMİR ARAÇ 01 → "01" (string olarak)
        """
        import re
        
        if not text or pd.isna(text):
            return "00"
        
        text_str = str(text).upper()
        
        # Pattern 1: [İZMİR ARAÇ XX] formatını ara
        pattern1 = r'\[İZMİR ARAÇ (\d+)\]'
        match1 = re.search(pattern1, text_str)
        
        if match1:
            arac_num = match1.group(1)
            # Baştaki sıfırları koru, 2 haneli yap
            return arac_num.zfill(2)
        
        # Pattern 2: İZMİR ARAÇ XX formatını ara
        pattern2 = r'İZMİR ARAÇ (\d+)'
        match2 = re.search(pattern2, text_str)
        
        if match2:
            arac_num = match2.group(1)
            return arac_num.zfill(2)
        
        # Pattern 3: Sadece sayıları ara
        numbers = re.findall(r'\d+', text_str)
        if numbers:
            return numbers[0].zfill(2)
        
        return "00"  # Varsayılan
    
    def parse_number(self, val):
        """Türkçe sayı formatını güvenli şekilde parse et"""
        if pd.isna(val) or val == '':
            return 0
        
        val_str = str(val).strip()
        if not val_str:
            return 0
        
        try:
            # Nokta ve virgül dönüşümü
            val_str = val_str.replace('.', '')  # Binlik ayracı kaldır
            val_str = val_str.replace(',', '.')  # Ondalık ayracı dönüştür
            
            # Sadece sayılar, nokta ve eksi işareti kalsın
            val_str = re.sub(r'[^\d.-]', '', val_str)
            
            return float(val_str) if val_str else 0
        except (ValueError, TypeError):
            logger.debug(f"Sayı parse edilemedi: {val}")
            return 0
    
    def remove_empty_rows_after_07(self, df):
        """0-7 Gün sonrası veri olmayan satırları sil"""
        try:
            rows_to_keep = []
            
            # Gün sütunlarını bul
            gun_columns = []
            for col in df.columns:
                col_str = str(col)
                if 'gün' in col_str.lower() and '0-7' not in col_str.lower():
                    gun_columns.append(col)
            
            if not gun_columns:
                logger.warning("Gün sütunları bulunamadı")
                return df
            
            initial_count = len(df)
            
            for idx, row in df.iterrows():
                # 0-7 Gün'den sonra veri var mı?
                has_data = False
                for col in gun_columns:
                    val = self.parse_number(row[col])
                    if val != 0:
                        has_data = True
                        break
                
                if has_data:
                    rows_to_keep.append(idx)
            
            if rows_to_keep:
                result_df = df.loc[rows_to_keep].reset_index(drop=True)
                removed_count = initial_count - len(result_df)
                if removed_count > 0:
                    logger.info(f"{removed_count} veri olmayan satır silindi")
                return result_df
            
            return df
            
        except Exception as e:
            logger.error(f"Boş satır silme hatası: {e}")
            return df
    
    def remove_empty_columns(self, df):
        """Tamamen boş sütunları güvenli şekilde kaldır"""
        try:
            cols_to_keep = []
            
            for col in df.columns:
                # Diğer Bakiye her zaman kalsın
                if 'diğer bakiye' in str(col).lower():
                    cols_to_keep.append(col)
                    continue
                
                # Kritik sütunlar (cari, ünvan, kategori) her zaman kalsın
                critical_keywords = ['cari', 'ünvan', 'kategori']
                if any(keyword in str(col).lower() for keyword in critical_keywords):
                    cols_to_keep.append(col)
                    continue
                
                # Gün sütunları için kontrol
                if 'gün' in str(col).lower():
                    has_data = False
                    for val in df[col]:
                        if self.parse_number(val) != 0:
                            has_data = True
                            break
                    if has_data:
                        cols_to_keep.append(col)
                else:
                    # Diğer sütunlar
                    if df[col].notna().any():
                        non_empty = df[col].dropna()
                        if len(non_empty) > 0:
                            # En az bir veri var mı kontrol et
                            has_real_data = False
                            for val in non_empty:
                                val_str = str(val).strip()
                                if val_str and val_str != '0':
                                    has_real_data = True
                                    break
                            if has_real_data:
                                cols_to_keep.append(col)
            
            removed_count = len(df.columns) - len(cols_to_keep)
            if removed_count > 0:
                logger.info(f"{removed_count} boş sütun kaldırıldı")
            
            return df[cols_to_keep]
            
        except Exception as e:
            logger.error(f"Boş sütun kaldırma hatası: {e}")
            return df

    def calculate_diger_bakiye(self, df):
        """Diğer Bakiye hesapla"""
        try:
            # Diğer Bakiye sütunu
            diger_col = None
            for col in df.columns:
                if 'diğer bakiye' in str(col).lower():
                    diger_col = col
                    break
            
            if not diger_col:
                diger_col = 'Diğer Bakiye'
                df[diger_col] = 0
            
            # Toplanacak sütunlar (8-14 ve sonrası)
            sum_cols = []
            target_patterns = ['8-14', '15-21', '22-28', '29-35', 
                              '36-42', '43-49', '50-56', '57-63',
                              '64-70', '71-77', '77+']
            
            for col in df.columns:
                col_str = str(col).lower()
                if 'gün' in col_str and '0-7' not in col_str and 'diğer' not in col_str:
                    # Belirtilen pattern'lardan birini içeriyor mu?
                    if any(pattern in col_str for pattern in target_patterns):
                        sum_cols.append(col)
            
            if not sum_cols:
                logger.warning("Toplanacak gün sütunu bulunamadı")
                return df
            
            # Her satır için topla
            diger_values = []
            for idx in df.index:
                total = 0
                for col in sum_cols:
                    val = df.loc[idx, col]
                    # Eğer değer var ve boş değilse
                    if pd.notna(val) and str(val).strip() != '':
                        num_val = self.parse_number(val)
                        total += num_val
                diger_values.append(total)
            
            # Diğer Bakiye sütununa yaz - FORMATLANMAMIŞ HALİYLE
            df[diger_col] = diger_values
            
            logger.info(f"Diğer Bakiye {len(sum_cols)} sütundan hesaplandı")
            return df
            
        except Exception as e:
            logger.error(f"Diğer Bakiye hesaplama hatası: {e}")
            return df

    def format_all_numbers(self, df):
        """Tüm sayısal sütunları güvenli şekilde formatla"""
        try:
            # DataFrame kopyası oluştur
            formatted_df = df.copy()
            
            for col in formatted_df.columns:
                col_str = str(col).lower()
                # Sayısal sütunlar - DİĞER BAKİYE HARİÇ
                if any(x in col_str for x in ['hesap', 'gün', 'bakiye']) and 'diğer' not in col_str:
                    try:
                        formatted_vals = []
                        for val in formatted_df[col]:
                            formatted_vals.append(self.format_turkish_number(val))
                        formatted_df[col] = formatted_vals
                    except Exception as col_error:
                        logger.error(f"Sütun {col} formatlanırken hata: {col_error}")
                        # Hata durumunda orijinal değerleri koru
                        continue
            
            return formatted_df
            
        except Exception as e:
            logger.error(f"Sayı formatlama hatası: {e}")
            return df
    
    def format_turkish_number(self, val):
        """Sayıyı güvenli şekilde Türkçe formata çevir"""
        if pd.isna(val):
            return ''
        
        try:
            num = self.parse_number(val)
            if num == 0:
                return '0'
            
            # Yuvarlama
            rounded = round(num)
            
            # Binlik ayraç ekle
            formatted = f"{rounded:,}".replace(',', '.')
            
            return formatted
            
        except Exception as e:
            logger.debug(f"Sayı formatlama hatası {val}: {e}")
            return str(val)  # Hata durumunda orijinal değeri döndür
    
    def get_backup_data(self):
        """Backup verisini döndür"""
        return self._backup_df
    
    def restore_from_backup(self):
        """Backup'tan geri yükle"""
        if self._backup_df is not None:
            self.processed_df = self._backup_df.copy()
            logger.info("Veriler backup'tan geri yüklendi")
            return True
        return False