# data_operations.py - Veri İşlemleri ve Analiz Operasyonları Modülü

import pandas as pd
import numpy as np
import json
import os
import tempfile
import gc
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Union, Any
import logging


class DataCleaner:
    """Veri temizleme ve standardizasyon işlemleri"""
    
    @staticmethod
    def turkce_normalize(text: Union[str, float]) -> str:
        """Türkçe karakterleri normalize eder ve metni standartlaştırır"""
        if pd.isna(text):
            return ""
            
        text = str(text).lower().strip()
        replacements = {
            'ı': 'i', 'ì': 'i', 'İ': 'i', 'I': 'i',
            'ş': 's', 'Ş': 's', 'ç': 'c', 'Ç': 'c',
            'ğ': 'g', 'Ğ': 'g', 'ü': 'u', 'Ü': 'u',
            'ö': 'o', 'Ö': 'o'
        }
        for tr_char, en_char in replacements.items():
            text = text.replace(tr_char, en_char)
        return text
    
    @staticmethod
    def clean_numeric(value: Union[str, float, int]) -> float:
        """Sayısal değerleri temizler ve float'a çevirir"""
        if pd.isna(value):
            return 0.0
            
        try:
            if isinstance(value, (int, float)):
                return float(value)
                
            if isinstance(value, str):
                # Para birimi sembollerini kaldır
                value = value.replace('₺', '').replace('TL', '').strip()
                
                # Binlik ayracı ve ondalık ayracı işleme
                if ',' in value and '.' in value:
                    # Hangisi ondalık ayracı belirle
                    if value.rfind(',') > value.rfind('.'):
                        value = value.replace('.', '').replace(',', '.')
                    else:
                        value = value.replace(',', '')
                elif ',' in value:
                    value = value.replace(',', '.')
                
                return float(value)
        except (ValueError, TypeError):
            return 0.0
            
        return 0.0
    
    @staticmethod
    def safe_numeric_conversion(series: pd.Series, default_value: float = 0.0) -> pd.Series:
        """Pandas Series'i güvenli şekilde sayısal değerlere çevirir"""
        try:
            # Önce string'leri temizle
            if series.dtype == 'object':
                cleaned_series = series.apply(DataCleaner.clean_numeric)
                return pd.to_numeric(cleaned_series, errors='coerce').fillna(default_value)
            else:
                return pd.to_numeric(series, errors='coerce').fillna(default_value)
        except Exception:
            return pd.Series([default_value] * len(series), index=series.index)
    
    @staticmethod
    def remove_summary_rows(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
        """TOPLAM, TOTAL gibi özet satırlarını kaldırır"""
        try:
            if column_name not in df.columns:
                return df
            
            # Özet satırları filtrele
            summary_patterns = ['TOPLAM', 'TOTAL', 'GENEL', 'SUM', 'ÖZET']
            mask = ~df[column_name].astype(str).str.upper().str.contains(
                '|'.join(summary_patterns), case=False, na=False
            )
            return df[mask].copy()
        except Exception:
            return df
    
    @staticmethod
    def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Sütun isimlerini standartlaştırır"""
        try:
            new_columns = {}
            for col in df.columns:
                # Satır sonlarını ve fazla boşlukları temizle
                clean_col = str(col).replace('\n', ' ').strip()
                clean_col = ' '.join(clean_col.split())  # Çoklu boşlukları tek boşluk yap
                new_columns[col] = clean_col
            
            return df.rename(columns=new_columns)
        except Exception:
            return df


class DataAnalyzer:
    """Veri analizi ve istatistik hesaplama işlemleri"""
    
    @staticmethod
    def calculate_basic_statistics(df: pd.DataFrame, column_name: str) -> Dict[str, float]:
        """Temel istatistikleri hesaplar"""
        try:
            if column_name not in df.columns:
                return {}
            
            series = DataCleaner.safe_numeric_conversion(df[column_name])
            valid_data = series.dropna()
            
            if valid_data.empty:
                return {}
            
            stats = {
                'count': len(valid_data),
                'sum': float(valid_data.sum()),
                'mean': float(valid_data.mean()),
                'median': float(valid_data.median()),
                'std': float(valid_data.std()) if len(valid_data) > 1 else 0.0,
                'min': float(valid_data.min()),
                'max': float(valid_data.max()),
                'q25': float(valid_data.quantile(0.25)),
                'q75': float(valid_data.quantile(0.75))
            }
            
            return stats
            
        except Exception as e:
            logging.error(f"Statistics calculation error: {e}")
            return {}
    
    @staticmethod
    def calculate_profit_distribution(df: pd.DataFrame, profit_column: str = 'Net Kar') -> Dict[str, int]:
        """Kar dağılımı analizi yapar"""
        try:
            if profit_column not in df.columns:
                return {'cok_karli': 0, 'orta_karli': 0, 'dusuk_karli': 0, 'zararda': 0}
            
            # Numeric conversion
            kar_series = DataCleaner.safe_numeric_conversion(df[profit_column])
            kar_data = kar_series.dropna()
            
            if kar_data.empty:
                return {'cok_karli': 0, 'orta_karli': 0, 'dusuk_karli': 0, 'zararda': 0}
            
            # Zarardaki ürünler
            zararda = len(kar_data[kar_data < 0])
            
            # Pozitif kar değerleri
            pozitif_kar = kar_data[kar_data >= 0]
            
            if pozitif_kar.empty:
                return {'cok_karli': 0, 'orta_karli': 0, 'dusuk_karli': 0, 'zararda': int(zararda)}
            
            if len(pozitif_kar) == 1:
                return {'cok_karli': 1, 'orta_karli': 0, 'dusuk_karli': 0, 'zararda': int(zararda)}
            
            # Quantile hesaplama
            try:
                q33 = pozitif_kar.quantile(0.33)
                q67 = pozitif_kar.quantile(0.67)
                
                dusuk_karli = len(pozitif_kar[pozitif_kar < q33])
                orta_karli = len(pozitif_kar[(pozitif_kar >= q33) & (pozitif_kar < q67)])
                cok_karli = len(pozitif_kar[pozitif_kar >= q67])
                
            except (ValueError, TypeError):
                # Eşit dağıtım
                pozitif_count = len(pozitif_kar)
                cok_karli = pozitif_count // 3
                orta_karli = pozitif_count // 3
                dusuk_karli = pozitif_count - cok_karli - orta_karli
            
            return {
                'cok_karli': int(cok_karli),
                'orta_karli': int(orta_karli),
                'dusuk_karli': int(dusuk_karli),
                'zararda': int(zararda)
            }
            
        except Exception as e:
            logging.error(f"Profit distribution calculation error: {e}")
            return {'cok_karli': 0, 'orta_karli': 0, 'dusuk_karli': 0, 'zararda': 0}
    
    @staticmethod
    def find_column_by_pattern(df: pd.DataFrame, patterns: List[str]) -> Optional[str]:
        """Sütun isimlerinde belirli paternleri arar"""
        try:
            for col in df.columns:
                col_normalized = DataCleaner.turkce_normalize(col)
                for pattern in patterns:
                    if pattern.lower() in col_normalized:
                        return col
            return None
        except Exception:
            return None
    
    @staticmethod
    def get_top_values(df: pd.DataFrame, 
                      sort_column: str, 
                      limit: int = 10, 
                      ascending: bool = False) -> pd.DataFrame:
        """Belirtilen sütuna göre en yüksek/düşük değerleri getirir"""
        try:
            if sort_column not in df.columns or df.empty:
                return pd.DataFrame()
            
            # Numeric conversion
            df_copy = df.copy()
            df_copy[sort_column] = DataCleaner.safe_numeric_conversion(df_copy[sort_column])
            
            # Geçerli değerleri filtrele
            valid_df = df_copy.dropna(subset=[sort_column])
            if valid_df.empty:
                return pd.DataFrame()
            
            # Sırala ve limit uygula
            if ascending:
                result = valid_df.nsmallest(limit, sort_column)
            else:
                result = valid_df.nlargest(limit, sort_column)
            
            return result.reset_index(drop=True)
            
        except Exception as e:
            logging.error(f"Top values calculation error: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def filter_data_by_criteria(df: pd.DataFrame, criteria: Dict[str, Any]) -> pd.DataFrame:
        """Belirtilen kriterlere göre veriyi filtreler"""
        try:
            if df.empty:
                return df
            
            filtered_df = df.copy()
            
            for column, condition in criteria.items():
                if column not in filtered_df.columns:
                    continue
                
                if isinstance(condition, dict):
                    if 'min' in condition:
                        numeric_col = DataCleaner.safe_numeric_conversion(filtered_df[column])
                        filtered_df = filtered_df[numeric_col >= condition['min']]
                    
                    if 'max' in condition:
                        numeric_col = DataCleaner.safe_numeric_conversion(filtered_df[column])
                        filtered_df = filtered_df[numeric_col <= condition['max']]
                    
                    if 'contains' in condition:
                        mask = filtered_df[column].astype(str).str.contains(
                            condition['contains'], case=False, na=False
                        )
                        filtered_df = filtered_df[mask]
                
                elif isinstance(condition, (list, tuple)):
                    filtered_df = filtered_df[filtered_df[column].isin(condition)]
                
                else:
                    filtered_df = filtered_df[filtered_df[column] == condition]
            
            return filtered_df.reset_index(drop=True)
            
        except Exception as e:
            logging.error(f"Data filtering error: {e}")
            return df


class ExcelOperations:
    """Excel dosya işlemleri"""
    
    @staticmethod
    def find_header_row(file_path: Union[str, Path], max_rows: int = 5) -> int:
        """Excel dosyasında uygun header satırını bulur"""
        try:
            for header_row in range(max_rows):
                try:
                    test_df = pd.read_excel(file_path, header=header_row, nrows=5)
                    
                    if test_df.empty:
                        continue
                    
                    # Sütun isimlerini kontrol et
                    column_names = [str(col).lower().strip() for col in test_df.columns]
                    
                    # Kritik sütunları ara
                    has_product = any('stok' in col or 'urun' in col or 'isim' in col 
                                    for col in column_names)
                    has_data = any('satis' in col or 'miktar' in col or 'fiyat' in col or 'tutar' in col 
                                 for col in column_names)
                    
                    if has_product and has_data:
                        return header_row
                        
                except Exception:
                    continue
            
            return 1  # Varsayılan değer
            
        except Exception:
            return 1
    
    @staticmethod
    def export_to_excel(df: pd.DataFrame, 
                       filename: str, 
                       sheet_name: str = 'Data',
                       summary_data: Optional[Dict] = None) -> bool:
        """DataFrame'i Excel dosyasına aktarır"""
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Ana veri
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Özet sayfası (varsa)
                if summary_data:
                    summary_df = pd.DataFrame(list(summary_data.items()), 
                                            columns=['Bilgi', 'Değer'])
                    summary_df.to_excel(writer, sheet_name='Özet', index=False)
            
            return True
            
        except PermissionError:
            logging.error("Excel export permission denied")
            return False
        except Exception as e:
            logging.error(f"Excel export error: {e}")
            return False
    
    @staticmethod
    def read_excel_safe(file_path: Union[str, Path], 
                       header: Optional[int] = None,
                       **kwargs) -> pd.DataFrame:
        """Excel dosyasını güvenli şekilde okur"""
        try:
            if header is None:
                header = ExcelOperations.find_header_row(file_path)
            
            df = pd.read_excel(file_path, header=header, **kwargs)
            
            if df.empty:
                return pd.DataFrame()
            
            # Sütun isimlerini standartlaştır
            df = DataCleaner.standardize_column_names(df)
            
            return df
            
        except Exception as e:
            logging.error(f"Excel read error: {e}")
            return pd.DataFrame()


class JSONOperations:
    """JSON dosya işlemleri"""
    
    @staticmethod
    def read_json_safe(file_path: Union[str, Path]) -> Dict[str, Any]:
        """JSON dosyasını güvenli şekilde okur"""
        try:
            if not os.path.exists(file_path):
                return {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data if isinstance(data, dict) else {}
            
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logging.error(f"JSON read error: {e}")
            return {}
        except Exception as e:
            logging.error(f"JSON read unexpected error: {e}")
            return {}
    
    @staticmethod
    def write_json_safe(data: Dict[str, Any], file_path: Union[str, Path]) -> bool:
        """JSON verisini güvenli şekilde yazar"""
        try:
            # Geçici dosya kullan
            with tempfile.NamedTemporaryFile(
                mode='w', 
                delete=False, 
                encoding='utf-8',
                suffix='.json'
            ) as temp_file:
                json.dump(data, temp_file, ensure_ascii=False, indent=2)
                temp_file_path = temp_file.name
            
            # Atomic replace
            os.replace(temp_file_path, file_path)
            return True
            
        except Exception as e:
            logging.error(f"JSON write error: {e}")
            # Cleanup temp file
            try:
                if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            except:
                pass
            return False
    
    @staticmethod
    def backup_json_file(file_path: Union[str, Path]) -> bool:
        """JSON dosyasının yedeğini alır"""
        try:
            if not os.path.exists(file_path):
                return False
            
            backup_name = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            import shutil
            shutil.copy2(file_path, backup_name)
            return True
            
        except Exception as e:
            logging.error(f"JSON backup error: {e}")
            return False
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_keys: List[str]) -> Tuple[bool, str]:
        """JSON yapısını doğrular"""
        try:
            if not isinstance(data, dict):
                return False, "Veri dictionary formatında değil"
            
            for key in required_keys:
                if key not in data:
                    return False, f"Gerekli alan eksik: {key}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Doğrulama hatası: {e}"


class DataMatcher:
    """Veri eşleştirme işlemleri"""
    
    @staticmethod
    def create_lookup_dictionary(df: pd.DataFrame, 
                                key_column: str, 
                                value_column: str,
                                clean_keys: bool = True) -> Dict[str, Any]:
        """Lookup dictionary oluşturur"""
        try:
            if key_column not in df.columns or value_column not in df.columns:
                return {}
            
            lookup_dict = {}
            
            for _, row in df.iterrows():
                key = row[key_column]
                value = row[value_column]
                
                if pd.isna(key) or pd.isna(value):
                    continue
                
                if clean_keys:
                    key = str(key).strip().upper()
                else:
                    key = str(key)
                
                # Sayısal değeri temizle
                if isinstance(value, str):
                    value = DataCleaner.clean_numeric(value)
                
                if key and value != 0:
                    lookup_dict[key] = value
            
            return lookup_dict
            
        except Exception as e:
            logging.error(f"Lookup dictionary creation error: {e}")
            return {}
    
    @staticmethod
    def match_data(df: pd.DataFrame,
                  match_column: str,
                  lookup_dict: Dict[str, Any],
                  target_column: str,
                  clean_match_keys: bool = True) -> Tuple[int, List[str]]:
        """
        Veri eşleştirme yapar
        
        Returns:
            Tuple[int, List[str]]: (eşleşen_sayısı, eşleşmeyenler)
        """
        try:
            if match_column not in df.columns:
                return 0, []
            
            # Target sütunu yoksa oluştur
            if target_column not in df.columns:
                df[target_column] = 0.0
            
            matched_count = 0
            unmatched = []
            
            for idx, row in df.iterrows():
                match_key = row[match_column]
                
                if pd.isna(match_key):
                    continue
                
                if clean_match_keys:
                    match_key = str(match_key).strip().upper()
                else:
                    match_key = str(match_key)
                
                if match_key in lookup_dict:
                    df.at[idx, target_column] = lookup_dict[match_key]
                    matched_count += 1
                else:
                    unmatched.append(match_key)
            
            return matched_count, unmatched
            
        except Exception as e:
            logging.error(f"Data matching error: {e}")
            return 0, []
    
    @staticmethod
    def fuzzy_match(df: pd.DataFrame,
                   match_column: str,
                   lookup_dict: Dict[str, Any],
                   threshold: float = 0.8) -> Dict[str, str]:
        """
        Bulanık eşleştirme yapar (opsiyonel, difflib kullanarak)
        
        Returns:
            Dict[str, str]: {original_key: matched_key}
        """
        try:
            import difflib
            
            if match_column not in df.columns:
                return {}
            
            fuzzy_matches = {}
            lookup_keys = list(lookup_dict.keys())
            
            for _, row in df.iterrows():
                match_key = row[match_column]
                
                if pd.isna(match_key):
                    continue
                
                match_key = str(match_key).strip().upper()
                
                if match_key not in lookup_dict:
                    # En yakın eşleşmeyi bul
                    matches = difflib.get_close_matches(
                        match_key, lookup_keys, n=1, cutoff=threshold
                    )
                    
                    if matches:
                        fuzzy_matches[match_key] = matches[0]
            
            return fuzzy_matches
            
        except ImportError:
            logging.warning("difflib not available for fuzzy matching")
            return {}
        except Exception as e:
            logging.error(f"Fuzzy matching error: {e}")
            return {}


class DataValidator:
    """Veri doğrulama işlemleri"""
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame, 
                          required_columns: List[str],
                          min_rows: int = 1) -> Tuple[bool, str]:
        """DataFrame'i doğrular"""
        try:
            if df is None:
                return False, "DataFrame None"
            
            if df.empty:
                return False, "DataFrame boş"
            
            if len(df) < min_rows:
                return False, f"En az {min_rows} satır gerekli"
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return False, f"Eksik sütunlar: {', '.join(missing_columns)}"
            
            return True, ""
            
        except Exception as e:
            return False, f"Doğrulama hatası: {e}"
    
    @staticmethod
    def check_data_quality(df: pd.DataFrame, column_name: str) -> Dict[str, Any]:
        """Veri kalitesi analizi"""
        try:
            if column_name not in df.columns:
                return {}
            
            series = df[column_name]
            total_count = len(series)
            
            if total_count == 0:
                return {}
            
            null_count = series.isnull().sum()
            unique_count = series.nunique()
            
            quality_report = {
                'total_count': total_count,
                'null_count': int(null_count),
                'null_percentage': float(null_count / total_count * 100),
                'unique_count': int(unique_count),
                'unique_percentage': float(unique_count / total_count * 100),
                'data_type': str(series.dtype)
            }
            
            # Sayısal sütunlar için ek bilgi
            try:
                numeric_series = pd.to_numeric(series, errors='coerce')
                valid_numeric = numeric_series.dropna()
                
                if not valid_numeric.empty:
                    quality_report.update({
                        'numeric_count': len(valid_numeric),
                        'zero_count': int((valid_numeric == 0).sum()),
                        'negative_count': int((valid_numeric < 0).sum())
                    })
            except:
                pass
            
            return quality_report
            
        except Exception as e:
            logging.error(f"Data quality check error: {e}")
            return {}


# Yardımcı fonksiyonlar
def cleanup_memory():
    """Bellek temizleme"""
    try:
        gc.collect()
    except Exception:
        pass


def setup_logging(level=logging.INFO):
    """Logging kurulumu"""
    try:
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    except Exception:
        pass
