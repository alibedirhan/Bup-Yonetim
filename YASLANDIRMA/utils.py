#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - Yardımcı Fonksiyonlar (GELİŞTİRİLMİŞ)
Sayı formatı dönüşümleri ve diğer yardımcı işlemler
"""

import re
import math
import logging
import pandas as pd
import numpy as np
from typing import Union, Any, Optional

logger = logging.getLogger(__name__)

def parse_turkish_number(value: Any) -> float:
    """
    Türkçe sayı formatını Python float'a güvenli şekilde çevir
    Tüm edge case'leri handle eder
    
    Args:
        value: String, sayısal değer veya herhangi bir tip
        
    Returns:
        Float değer, hata durumunda 0.0
    """
    # Boş değer kontrolü
    if value is None or value == '':
        return 0.0
    
    # NaN kontrolü
    if isinstance(value, float) and math.isnan(value):
        return 0.0
    
    # Zaten sayısal ise direkt dönüştür
    if isinstance(value, (int, float)) and not math.isnan(value if isinstance(value, float) else 0):
        return float(value)
    
    # String'e çevir
    try:
        value_str = str(value).strip()
    except Exception as e:
        logger.debug(f"String çevirme hatası '{value}': {e}")
        return 0.0
    
    # Boş veya özel değerler
    if not value_str or value_str.lower() in ['nan', 'none', 'null', '-', '']:
        return 0.0
    
    try:
        # Negatif işaret kontrolü
        is_negative = False
        
        # Parantez içindeki negatif sayılar: (1.234,56)
        if value_str.startswith('(') and value_str.endswith(')'):
            is_negative = True
            value_str = value_str[1:-1].strip()
        # Normal negatif işaret: -1.234,56
        elif value_str.startswith('-'):
            is_negative = True
            value_str = value_str[1:].strip()
        
        # Para birimi sembolleri ve diğer karakterleri temizle
        # ₺, TL, $, €, £ gibi sembolleri kaldır
        currency_symbols = ['₺', 'TL', '$', '€', '£', '¥', '₽']
        for symbol in currency_symbols:
            value_str = value_str.replace(symbol, '')
        
        value_str = value_str.strip()
        
        # Nokta ve virgül işleme - Türkçe format
        if ',' in value_str and '.' in value_str:
            # Her ikisi de varsa: 1.234.567,89 formatı
            # Son virgülden sonra en fazla 2 rakam olmalı (ondalık)
            parts = value_str.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2 and parts[1].isdigit():
                # Ondalıklı kısım geçerli, noktaları kaldır
                integer_part = parts[0].replace('.', '')
                decimal_part = parts[1]
                value_str = f"{integer_part}.{decimal_part}"
            else:
                # Geçersiz format, tüm nokta ve virgülleri kaldır
                value_str = re.sub(r'[,.]', '', value_str)
        elif ',' in value_str:
            # Sadece virgül var
            parts = value_str.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2 and parts[1].isdigit():
                # Ondalıklı: 1234,56 → 1234.56
                value_str = value_str.replace(',', '.')
            else:
                # Binlik ayıraç: 1,234,567 → 1234567
                value_str = value_str.replace(',', '')
        elif '.' in value_str:
            # Sadece nokta var
            parts = value_str.split('.')
            if len(parts) == 2 and len(parts[1]) <= 2 and parts[1].isdigit():
                # Ondalıklı gibi görünüyor: 1234.56
                pass
            elif len(parts) > 2:
                # Binlik ayıraç: 1.234.567 → 1234567
                value_str = value_str.replace('.', '')
            # Tek nokta varsa olduğu gibi bırak
        
        # Sadece rakamlar, nokta ve eksi işareti kalsın
        cleaned = re.sub(r'[^\d.-]', '', value_str)
        
        if not cleaned or cleaned in ['-', '.', '-.']:
            return 0.0
        
        # Float'a çevir
        result = float(cleaned)
        
        # Negatif işaret uygula
        if is_negative:
            result = -result
        
        # Çok büyük sayıları filtrele (hata olabilir)
        if abs(result) > 1e15:
            logger.warning(f"Çok büyük sayı tespit edildi: {result}")
            return 0.0
        
        return result
        
    except (ValueError, TypeError, OverflowError) as e:
        logger.debug(f"Sayı parse edilemedi '{value}': {e}")
        return 0.0

def format_turkish_number(value: Any) -> str:
    """
    Sayıyı Türkçe formata çevir ve yuvarla
    1234567.89 → 1.234.568
    
    Args:
        value: Herhangi bir değer
        
    Returns:
        Formatlanmış string
    """
    if value is None:
        return ""
    
    # NaN kontrolü
    if isinstance(value, float) and math.isnan(value):
        return ""
    
    # Float'a çevir
    try:
        num_value = parse_turkish_number(value)
    except Exception:
        return str(value)
    
    if num_value == 0:
        return "0"
    
    try:
        # Yuvarlama kuralı: 0.5 ve üstü yukarı
        rounded_value = round(num_value)
        
        # Binlik ayraç ekle
        formatted = format_with_thousand_separator(rounded_value)
        
        return formatted
        
    except Exception as e:
        logger.debug(f"Sayı formatlama hatası '{value}': {e}")
        return str(value)

def format_with_thousand_separator(value: Union[int, float]) -> str:
    """
    Sayıya binlik ayraç ekle (Türkçe format)
    1234567 → 1.234.567
    
    Args:
        value: Sayısal değer
        
    Returns:
        Noktalı format
    """
    if value == 0:
        return "0"
    
    try:
        # Negatif kontrolü
        is_negative = value < 0
        value = abs(value)
        
        # Integer'a çevir
        int_value = int(value)
        
        # Python'un format özelliğini kullan
        formatted = f"{int_value:,}".replace(',', '.')
        
        # Negatif ise ekle
        if is_negative:
            formatted = '-' + formatted
        
        return formatted
        
    except Exception as e:
        logger.debug(f"Binlik ayraç ekleme hatası '{value}': {e}")
        return str(value)

def format_number_display(value: Any) -> str:
    """
    GUI'de gösterim için sayıyı güvenli şekilde formatla
    
    Args:
        value: Herhangi bir değer
        
    Returns:
        Gösterim için formatlanmış string
    """
    if value is None or value == '':
        return ""
    
    # NaN kontrolü
    if isinstance(value, float) and math.isnan(value):
        return ""
    
    # Sayısal değil ise olduğu gibi döndür
    try:
        parsed = parse_turkish_number(value)
        if parsed == 0 and str(value).strip() not in ['0', '0.0', '0,0']:
            # Sayı parse edilemedi ama 0 değil, orijinal değeri döndür
            return str(value)
    except Exception:
        return str(value)
    
    # Türkçe formata çevir
    return format_turkish_number(parsed)

def is_numeric_column(column_name: str) -> bool:
    """
    Sütunun sayısal olup olmadığını kontrol et
    
    Args:
        column_name: Sütun adı
        
    Returns:
        Boolean
    """
    if not column_name:
        return False
    
    numeric_keywords = ['hesap', 'gün', 'gun', 'bakiye', 'tutar', 'toplam', 'total', 'amount']
    column_str = str(column_name).lower()
    
    return any(keyword in column_str for keyword in numeric_keywords)

def clean_string(value: Any) -> str:
    """
    String değeri temizle ve normalize et
    
    Args:
        value: Herhangi bir değer
        
    Returns:
        Temizlenmiş string
    """
    if value is None:
        return ""
    
    try:
        # String'e çevir ve temizle
        cleaned = str(value).strip()
        
        # Çoklu boşlukları tek boşluğa çevir
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Baş ve sondaki özel karakterleri temizle
        cleaned = cleaned.strip(' \t\n\r\f\v-_')
        
        return cleaned
        
    except Exception as e:
        logger.debug(f"String temizleme hatası '{value}': {e}")
        return str(value) if value is not None else ""

def extract_numbers_from_text(text: str) -> list:
    """
    Metinden tüm sayıları güvenli şekilde çıkar
    
    Args:
        text: Metin
        
    Returns:
        Sayıların listesi
    """
    if not text:
        return []
    
    try:
        # Regex ile tüm sayıları bul
        numbers = re.findall(r'\b\d+\b', str(text))
        
        # String'den integer'a çevir
        return [int(num) for num in numbers if num.isdigit()]
        
    except Exception as e:
        logger.debug(f"Sayı çıkarma hatası '{text}': {e}")
        return []

def extract_arac_number_from_text(text: str) -> Optional[int]:
    """
    Metinden ARAÇ numarasını çıkar
    Özel olarak ARAÇ formatları için optimize edilmiş
    
    Args:
        text: ARAÇ formatını içeren metin
        
    Returns:
        ARAÇ numarası veya None
    """
    if not text:
        return None
    
    try:
        text_upper = str(text).strip().upper()
        
        # ARAÇ pattern'leri sırasıyla dene
        patterns = [
            r'\[İZMİR ARAÇ (\d+)\]',        # [İZMİR ARAÇ 06]
            r'İZMİR ARAÇ (\d+)',            # İZMİR ARAÇ 06
            r'ARAÇ (\d+)',                  # ARAÇ 06
            r'(\d+)\s*ARAÇ',                # 06 ARAÇ
            r'^(\d+)$',                     # Sadece sayı
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text_upper)
            if matches:
                try:
                    arac_num = int(matches[0])
                    if 0 < arac_num < 100:  # Geçerli ARAÇ numarası aralığı
                        return arac_num
                except ValueError:
                    continue
        
        return None
        
    except Exception as e:
        logger.debug(f"ARAÇ numarası çıkarma hatası '{text}': {e}")
        return None

def get_category_sort_key(value: Any) -> tuple:
    """
    Kategori sıralama anahtarı oluştur
    Sayısal değerler önce, sonra alfabetik
    
    Args:
        value: Kategori değeri
        
    Returns:
        Sıralama tuple'ı (priority, sort_value)
    """
    if pd.isna(value):
        return (2, "")  # NaN değerler en sona
    
    try:
        # Sayısal mı kontrol et
        num_val = int(value)
        return (0, num_val)  # Sayısal değerler önce
    except (ValueError, TypeError):
        return (1, str(value).lower())  # String değerler sonra, küçük harfe çevir

def validate_excel_file(file_path: str) -> tuple:
    """
    Excel dosyasının geçerliliğini kontrol et
    
    Args:
        file_path: Dosya yolu
        
    Returns:
        (Boolean, Error message veya None)
    """
    try:
        from pathlib import Path
        
        path = Path(file_path)
        
        # Dosya var mı?
        if not path.exists():
            return False, "Dosya bulunamadı"
        
        # Excel dosyası mı?
        if path.suffix.lower() not in ['.xlsx', '.xls']:
            return False, "Geçersiz dosya formatı. Excel dosyası (.xlsx veya .xls) seçin."
        
        # Dosya boyutu kontrolü (maksimum 100MB)
        file_size = path.stat().st_size
        if file_size > 100 * 1024 * 1024:  # 100MB
            return False, "Dosya çok büyük (maksimum 100MB)"
        
        # Dosya okunabilir mi?
        try:
            pd.read_excel(file_path, nrows=1)
        except Exception as e:
            return False, f"Dosya okunamadı: {str(e)}"
        
        return True, None
        
    except Exception as e:
        logger.error(f"Dosya doğrulama hatası: {e}")
        return False, f"Doğrulama hatası: {str(e)}"

def get_column_data_type(series: pd.Series) -> str:
    """
    Pandas Series'in veri tipini belirle
    
    Args:
        series: Pandas Series
        
    Returns:
        'numeric', 'text', 'mixed', 'date', veya 'empty'
    """
    try:
        # Boş değerleri çıkar
        non_null = series.dropna()
        
        if len(non_null) == 0:
            return 'empty'
        
        # Tarih mi kontrol et
        try:
            pd.to_datetime(non_null.head(10), errors='raise')
            return 'date'
        except (ValueError, TypeError):
            pass
        
        # Numeric mi kontrol et
        numeric_count = 0
        for value in non_null.head(20):  # İlk 20 değeri test et
            if parse_turkish_number(value) != 0 or str(value).strip() in ['0', '0.0', '0,0']:
                numeric_count += 1
        
        if numeric_count / min(len(non_null), 20) > 0.8:  # %80'i sayısal ise
            return 'numeric'
        
        # Text mi kontrol et
        if non_null.apply(lambda x: isinstance(x, str)).all():
            return 'text'
        
        return 'mixed'
        
    except Exception as e:
        logger.debug(f"Veri tipi belirleme hatası: {e}")
        return 'mixed'

def calculate_statistics(df: pd.DataFrame) -> dict:
    """
    DataFrame için güvenli istatistikler hesapla
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        İstatistik dictionary
    """
    try:
        stats = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'numeric_columns': 0,
            'text_columns': 0,
            'date_columns': 0,
            'empty_columns': 0,
            'empty_cells': 0,
            'total_cells': len(df) * len(df.columns) if len(df) > 0 else 0
        }
        
        # Her sütun için tip kontrolü
        for col in df.columns:
            try:
                col_type = get_column_data_type(df[col])
                if col_type == 'numeric':
                    stats['numeric_columns'] += 1
                elif col_type == 'text':
                    stats['text_columns'] += 1
                elif col_type == 'date':
                    stats['date_columns'] += 1
                elif col_type == 'empty':
                    stats['empty_columns'] += 1
            except Exception as e:
                logger.debug(f"Sütun {col} analiz hatası: {e}")
        
        # Boş hücre sayısı
        try:
            stats['empty_cells'] = int(df.isna().sum().sum())
        except Exception:
            stats['empty_cells'] = 0
        
        # Doluluk oranı
        if stats['total_cells'] > 0:
            stats['fill_rate'] = round(100 * (1 - stats['empty_cells'] / stats['total_cells']), 2)
        else:
            stats['fill_rate'] = 0.0
        
        # Bellek kullanımı
        try:
            stats['memory_usage_mb'] = round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        except Exception:
            stats['memory_usage_mb'] = 0.0
        
        return stats
        
    except Exception as e:
        logger.error(f"İstatistik hesaplama hatası: {e}")
        return {
            'row_count': 0,
            'column_count': 0,
            'numeric_columns': 0,
            'text_columns': 0,
            'date_columns': 0,
            'empty_columns': 0,
            'empty_cells': 0,
            'total_cells': 0,
            'fill_rate': 0.0,
            'memory_usage_mb': 0.0
        }

def safe_excel_read(file_path: str, **kwargs) -> Optional[pd.DataFrame]:
    """
    Excel dosyasını güvenli şekilde oku
    
    Args:
        file_path: Dosya yolu
        **kwargs: pandas.read_excel parametreleri
        
    Returns:
        DataFrame veya None
    """
    try:
        # Dosya kontrolü
        is_valid, error_msg = validate_excel_file(file_path)
        if not is_valid:
            logger.error(f"Excel dosyası geçersiz: {error_msg}")
            return None
        
        # Dosyayı oku
        df = pd.read_excel(file_path, **kwargs)
        
        if df.empty:
            logger.warning("Excel dosyası boş")
            return None
        
        logger.info(f"Excel dosyası başarıyla okundu: {len(df)} satır, {len(df.columns)} sütun")
        return df
        
    except Exception as e:
        logger.error(f"Excel okuma hatası: {e}")
        return None

def safe_excel_write(df: pd.DataFrame, file_path: str, **kwargs) -> bool:
    """
    DataFrame'i güvenli şekilde Excel'e yaz
    
    Args:
        df: Pandas DataFrame
        file_path: Dosya yolu
        **kwargs: pandas.to_excel parametreleri
        
    Returns:
        Boolean (başarılı/başarısız)
    """
    try:
        from pathlib import Path
        
        if df is None or df.empty:
            logger.error("Yazılacak DataFrame boş")
            return False
        
        # Dosya yolu kontrolü
        path = Path(file_path)
        
        # Dizin yoksa oluştur
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Dosya yazma
        df.to_excel(file_path, **kwargs)
        logger.info(f"DataFrame başarıyla Excel'e yazıldı: {file_path}")
        
        return True
        
    except PermissionError:
        logger.error(f"Dosya yazma izni yok: {file_path}")
        return False
    except Exception as e:
        logger.error(f"Excel yazma hatası: {e}")
        return False

def format_file_size(size_bytes: int) -> str:
    """
    Dosya boyutunu insan okunabilir formata çevir
    
    Args:
        size_bytes: Byte cinsinden boyut
        
    Returns:
        Formatlanmış string (örn: "1.5 MB")
    """
    try:
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        i = min(i, len(size_names) - 1)  # Maksimum indeks kontrolü
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        
        return f"{s} {size_names[i]}"
        
    except Exception as e:
        logger.debug(f"Dosya boyutu formatlama hatası: {e}")
        return f"{size_bytes} B"

def memory_usage_mb() -> Optional[float]:
    """
    Mevcut bellek kullanımını MB cinsinden döndür
    
    Returns:
        Bellek kullanımı (MB) veya None
    """
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        return round(memory_mb, 2)
        
    except ImportError:
        # psutil yüklü değilse
        return None
    except Exception as e:
        logger.debug(f"Bellek kullanımı alınamadı: {e}")
        return None

def backup_file(file_path: str, backup_suffix: str = "_backup") -> Optional[str]:
    """
    Dosyanın backup'ını oluştur
    
    Args:
        file_path: Orijinal dosya yolu
        backup_suffix: Backup dosyası için ek
        
    Returns:
        Backup dosya yolu veya None
    """
    try:
        from pathlib import Path
        import shutil
        from datetime import datetime
        
        original_path = Path(file_path)
        
        if not original_path.exists():
            logger.warning(f"Backup oluşturulamadı, dosya yok: {file_path}")
            return None
        
        # Backup dosya adı oluştur
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{original_path.stem}{backup_suffix}_{timestamp}{original_path.suffix}"
        backup_path = original_path.parent / backup_name
        
        # Backup oluştur
        shutil.copy2(original_path, backup_path)
        logger.info(f"Backup oluşturuldu: {backup_path}")
        
        return str(backup_path)
        
    except Exception as e:
        logger.error(f"Backup oluşturma hatası: {e}")
        return None

def cleanup_temp_files(directory: str, pattern: str = "temp_*", max_age_hours: int = 24) -> int:
    """
    Geçici dosyaları temizle
    
    Args:
        directory: Temizlenecek dizin
        pattern: Dosya pattern'i
        max_age_hours: Maksimum yaş (saat)
        
    Returns:
        Temizlenen dosya sayısı
    """
    try:
        from pathlib import Path
        import time
        
        directory = Path(directory)
        if not directory.exists():
            return 0
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        cleaned_count = 0
        
        # Pattern'e uyan dosyaları bul
        for file_path in directory.glob(pattern):
            try:
                file_age = current_time - file_path.stat().st_mtime
                
                if file_age > max_age_seconds:
                    file_path.unlink()
                    cleaned_count += 1
                    logger.debug(f"Geçici dosya silindi: {file_path}")
                    
            except Exception as e:
                logger.debug(f"Dosya silme hatası {file_path}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"{cleaned_count} geçici dosya temizlendi")
        
        return cleaned_count
        
    except Exception as e:
        logger.error(f"Geçici dosya temizleme hatası: {e}")
        return 0

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Güvenli bölme işlemi
    
    Args:
        numerator: Bölünen
        denominator: Bölen
        default: Sıfıra bölme durumunda dönülecek değer
        
    Returns:
        Bölme sonucu veya default değer
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except Exception:
        return default

def normalize_text(text: str) -> str:
    """
    Metni normalize et (Türkçe karakterler, büyük/küçük harf)
    
    Args:
        text: Normalleştirilecek metin
        
    Returns:
        Normalize edilmiş metin
    """
    if not text:
        return ""
    
    try:
        # Türkçe karakterleri ASCII'ye çevir
        turkish_chars = {
            'ç': 'c', 'Ç': 'C',
            'ğ': 'g', 'Ğ': 'G', 
            'ı': 'i', 'I': 'I',
            'İ': 'I', 'i': 'i',
            'ö': 'o', 'Ö': 'O',
            'ş': 's', 'Ş': 'S',
            'ü': 'u', 'Ü': 'U'
        }
        
        normalized = str(text).strip()
        
        # Türkçe karakterleri değiştir
        for tr_char, en_char in turkish_chars.items():
            normalized = normalized.replace(tr_char, en_char)
        
        # Küçük harfe çevir
        normalized = normalized.lower()
        
        # Özel karakterleri temizle
        normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
        
        # Çoklu boşlukları tek boşluğa çevir
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
        
    except Exception as e:
        logger.debug(f"Metin normalize etme hatası: {e}")
        return str(text).lower().strip()

def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Metni belirtilen uzunlukta kes
    
    Args:
        text: Kesilecek metin
        max_length: Maksimum uzunluk
        suffix: Kesim sonrası eklenecek ek
        
    Returns:
        Kesilmiş metin
    """
    if not text or len(text) <= max_length:
        return str(text) if text else ""
    
    return text[:max_length - len(suffix)] + suffix

def find_similar_strings(target: str, candidates: list, threshold: float = 0.8) -> list:
    """
    Benzer stringleri bul (basit similarity)
    
    Args:
        target: Hedef string
        candidates: Aday stringler
        threshold: Benzerlik eşiği (0-1)
        
    Returns:
        Benzer stringlerin listesi
    """
    if not target or not candidates:
        return []
    
    try:
        target_normalized = normalize_text(target)
        similar = []
        
        for candidate in candidates:
            if not candidate:
                continue
                
            candidate_normalized = normalize_text(str(candidate))
            
            # Basit benzerlik: ortak kelime sayısı
            target_words = set(target_normalized.split())
            candidate_words = set(candidate_normalized.split())
            
            if not target_words or not candidate_words:
                continue
            
            intersection = len(target_words.intersection(candidate_words))
            union = len(target_words.union(candidate_words))
            
            similarity = intersection / union if union > 0 else 0
            
            if similarity >= threshold:
                similar.append(candidate)
        
        return similar
        
    except Exception as e:
        logger.debug(f"String benzerlik arama hatası: {e}")
        return []