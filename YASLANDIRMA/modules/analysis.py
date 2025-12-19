#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - Analiz Modülü (DÜZELTİLMİŞ)
ARAÇ bazlı analiz ve hesaplama motoru - Temiz versiyon
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union, Any
import re
from utils import parse_turkish_number

logger = logging.getLogger(__name__)

class AnalysisEngine:
    def __init__(self):
        self.current_data = None
        self.analysis_results = {}
        self.last_analysis_date = None
        self.arac_column_name = None
        self.cari_column_name = None
        self.bakiye_columns = []
        self._validation_cache = {}
    
    def set_data(self, df: pd.DataFrame) -> bool:
        """Analiz için veri setini ayarla"""
        try:
            if df is None or df.empty:
                logger.error("Analiz için boş veri seti")
                return False
            
            self.current_data = self._optimize_dataframe(df.copy())
            self.last_analysis_date = datetime.now()
            
            # Sütun adlarını tespit et
            self.arac_column_name = self._find_arac_column()
            self.cari_column_name = self._find_cari_column()
            self.bakiye_columns = self._find_bakiye_columns()
            
            if not self.arac_column_name:
                logger.error("ARAÇ kategori sütunu bulunamadı")
                return False
                
            if not self.cari_column_name:
                logger.warning("Cari ünvan sütunu bulunamadı")
                self.cari_column_name = self._find_first_text_column()
                if not self.cari_column_name:
                    logger.error("Cari ünvan sütunu bulunamadı")
                    return False
                
            if not self.bakiye_columns:
                logger.error("Bakiye sütunları bulunamadı")
                return False
            
            logger.info(f"Analiz veri seti ayarlandı: {len(df)} satır")
            logger.info(f"ARAÇ sütunu: {self.arac_column_name}")
            logger.info(f"Cari sütunu: {self.cari_column_name}")
            logger.info(f"Bakiye sütunları: {self.bakiye_columns}")
            
            self._validation_cache.clear()
            return True
            
        except Exception as e:
            logger.error(f"Veri seti ayarlama hatası: {e}")
            return False
    
    def _optimize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame bellek kullanımını optimize et"""
        try:
            for col in df.select_dtypes(include=[np.number]).columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            for col in df.select_dtypes(include=['object']).columns:
                if df[col].nunique() / len(df) < 0.5:
                    df[col] = df[col].astype('category')
            
            return df
        except Exception as e:
            logger.warning(f"DataFrame optimizasyon hatası: {e}")
            return df
    
    def analyze_all_aracs(self) -> Dict:
        """Tüm ARAÇ'ları analiz et"""
        try:
            if self.current_data is None:
                raise ValueError("Analiz için veri seti ayarlanmamış")
            
            if not self.arac_column_name:
                raise ValueError("ARAÇ sütunu tespit edilemedi")
            
            arac_numbers = self._extract_arac_numbers()
            
            if not arac_numbers:
                logger.warning("Geçerli ARAÇ numarası bulunamadı")
                return {}
            
            logger.info(f"Analiz edilecek ARAÇ numaraları: {sorted(arac_numbers)}")
            
            results = {}
            total_aracs = len(arac_numbers)
            
            for i, arac_no in enumerate(arac_numbers):
                try:
                    arac_analysis = self._analyze_single_arac_internal(arac_no)
                    if arac_analysis:
                        results[str(arac_no)] = arac_analysis
                        logger.info(f"ARAÇ {arac_no} analizi tamamlandı ({i+1}/{total_aracs}): {arac_analysis['musteri_sayisi']} müşteri")
                    else:
                        logger.warning(f"ARAÇ {arac_no} analizi başarısız")
                except Exception as arac_error:
                    logger.error(f"ARAÇ {arac_no} analiz hatası: {arac_error}")
                    continue
            
            self.analysis_results = results
            logger.info(f"Toplam {len(results)} ARAÇ analiz edildi")
            return results
            
        except Exception as e:
            logger.error(f"ARAÇ analizi hatası: {e}")
            return {}
    
    def analyze_single_arac(self, arac_no: Union[str, int]) -> Optional[Dict]:
        """Tek ARAÇ analizi (Public method)"""
        try:
            if self.current_data is None:
                raise ValueError("Analiz için veri seti ayarlanmamış")
            
            try:
                arac_int = int(arac_no) if isinstance(arac_no, str) else arac_no
            except (ValueError, TypeError):
                logger.error(f"Geçersiz ARAÇ numarası: {arac_no}")
                return None
                
            return self._analyze_single_arac_internal(arac_int)
            
        except Exception as e:
            logger.error(f"ARAÇ {arac_no} analizi hatası: {e}")
            return None
    
    def _find_arac_column(self) -> Optional[str]:
        """ARAÇ kategori sütununu bul - GELİŞTİRİLMİŞ"""
        try:
            possible_names = [
                'Cari Kategori 3',
                'cari kategori 3', 
                'Kategori 3',
                'kategori 3',
                'ARAÇ',
                'Arac',
                'arac',
                'Cari Grubu 3',
                'cari grubu 3'
            ]
            
            # Önce tam eşleşme ara
            for col in self.current_data.columns:
                col_str = str(col).strip()
                if col_str in possible_names:
                    logger.info(f"ARAÇ sütunu bulundu (tam eşleşme): {col_str}")
                    return col_str
            
            # Sonra kısmi eşleşme ara
            for col in self.current_data.columns:
                col_str = str(col).strip()
                col_lower = col_str.lower()
                
                if ('kategori' in col_lower and '3' in col_lower):
                    logger.info(f"ARAÇ sütunu bulundu (kategori 3 eşleşme): {col_str}")
                    return col_str
                elif ('grup' in col_lower and '3' in col_lower):
                    logger.info(f"ARAÇ sütunu bulundu (grup 3 eşleşme): {col_str}")
                    return col_str
            
            # Son olarak araç kelimesi içeren sütunları ara
            for col in self.current_data.columns:
                col_str = str(col).lower()
                if 'araç' in col_str or 'arac' in col_str:
                    logger.info(f"ARAÇ sütunu bulundu (araç içeren): {col}")
                    return col
            
            logger.error("ARAÇ sütunu bulunamadı")
            return None
            
        except Exception as e:
            logger.error(f"ARAÇ sütunu bulma hatası: {e}")
            return None
    
    def _find_first_text_column(self) -> Optional[str]:
        """İlk metin sütununu bul"""
        try:
            for col in self.current_data.columns:
                if self.current_data[col].dtype == 'object' or pd.api.types.is_string_dtype(self.current_data[col]):
                    if not self.current_data[col].isna().all():
                        logger.info(f"Metin sütunu bulundu: {col}")
                        return col
            return None
        except Exception as e:
            logger.error(f"Metin sütunu bulma hatası: {e}")
            return None
    
    def _find_cari_column(self) -> Optional[str]:
        """Cari Ünvan sütununu bul"""
        try:
            # Önce kesin eşleşmeler
            for col in self.current_data.columns:
                col_str = str(col).lower()
                if 'cari' in col_str and ('ünvan' in col_str or 'unvan' in col_str):
                    return col
            
            # Sonra alternatif isimler
            for col in self.current_data.columns:
                col_str = str(col).lower()
                if 'müşteri' in col_str or 'musteri' in col_str:
                    return col
                elif 'firma' in col_str or 'şirket' in col_str or 'sirket' in col_str:
                    return col
                elif 'isim' in col_str or 'ad' in col_str or 'name' in col_str:
                    return col
                    
            logger.warning("Cari ünvan sütunu bulunamadı")
            return None
            
        except Exception as e:
            logger.error(f"Cari sütunu bulma hatası: {e}")
            return None
    
    def _find_bakiye_columns(self) -> List[str]:
        """Bakiye/Gün sütunlarını bul - GELİŞTİRİLMİŞ"""
        try:
            bakiye_cols = []
            
            for col in self.current_data.columns:
                col_str = str(col).lower()
                
                aging_periods = [
                    'açık hesap', 'acik hesap',
                    '0-7', '8-14', '15-21', '22-28', '29-35', 
                    '36-42', '43-49', '50-56', '57-63', '64-70', 
                    '71-77', '77+',
                    'diğer bakiye', 'diger bakiye',
                    'toplam', 'genel toplam'
                ]
                
                if any(period in col_str for period in aging_periods):
                    bakiye_cols.append(col)
                elif 'gün' in col_str or 'gun' in col_str:
                    bakiye_cols.append(col)
                elif 'bakiye' in col_str or 'bakiyesi' in col_str:
                    bakiye_cols.append(col)
                elif 'tutar' in col_str or 'meblağ' in col_str or 'meblag' in col_str:
                    bakiye_cols.append(col)
            
            bakiye_cols.sort(key=self._sort_aging_columns)
            
            logger.info(f"Bulunan bakiye sütunları: {bakiye_cols}")
            return bakiye_cols
            
        except Exception as e:
            logger.error(f"Bakiye sütunları bulma hatası: {e}")
            return []
    
    def _sort_aging_columns(self, column_name: str) -> int:
        """Yaşlandırma sütunlarını sıralama için key fonksiyonu"""
        try:
            col_str = str(column_name).lower()
            
            aging_order = [
                'açık hesap', 'acik hesap',
                '0-7', '8-14', '15-21', '22-28', '29-35', 
                '36-42', '43-49', '50-56', '57-63', '64-70', 
                '71-77', '77+',
                'diğer bakiye', 'diger bakiye',
                'toplam', 'genel toplam'
            ]
            
            for i, period in enumerate(aging_order):
                if period in col_str:
                    return i
                    
            return 999
            
        except Exception:
            return 999
    
    def _extract_arac_numbers(self) -> List[int]:
        """ARAÇ numaralarını çıkar - TAM DÜZELTİLMİŞ"""
        try:
            if not self.arac_column_name:
                return []
            
            arac_column = self.current_data[self.arac_column_name]
            arac_numbers = set()
            
            unique_values = arac_column.unique()
            logger.info(f"ARAÇ sütunundaki unique değerler: {[str(v) for v in unique_values if pd.notna(v)]}")
            
            # Geliştirilmiş regex pattern'ler
            patterns = [
                r'\[İZMİR ARAÇ (\d+)\]',        # [İZMİR ARAÇ 06] formatı
                r'İZMİR ARAÇ (\d+)',            # İZMİR ARAÇ 06 formatı
                r'ARAÇ (\d+)',                  # ARAÇ 06 formatı
                r'(\d+)\s*ARAÇ',                # 06 ARAÇ formatı
                r'^(\d+)$',                     # Sadece sayı formatı
                r'(\d+)(?:\s|$)',               # Sayı + boşluk veya satır sonu
            ]
            
            for value in unique_values:
                if pd.isna(value):
                    continue
                    
                str_value = str(value).strip().upper()
                
                # Özel kategorileri atla
                skip_keywords = ['İZMİR ŞUBE DEPO', 'DEPO', 'MERKEZ', 'GENEL', 'KESİMHANE']
                if any(keyword in str_value for keyword in skip_keywords):
                    logger.debug(f"Özel kategori atlandı: {str_value}")
                    continue
                
                # Önce doğrudan sayı olup olmadığını kontrol et
                try:
                    direct_num = int(str_value)
                    if 0 < direct_num < 100:
                        arac_numbers.add(direct_num)
                        logger.debug(f"Doğrudan ARAÇ numarası bulundu: {str_value} → {direct_num}")
                        continue
                except ValueError:
                    pass
                
                # Regex pattern'ler ile eşleştirme
                found = False
                for pattern in patterns:
                    try:
                        matches = re.findall(pattern, str_value)
                        for match in matches:
                            try:
                                arac_num = int(match)
                                if 0 < arac_num < 100:
                                    arac_numbers.add(arac_num)
                                    logger.debug(f"ARAÇ numarası bulundu: {str_value} → {arac_num}")
                                    found = True
                                    break
                            except ValueError:
                                continue
                        if found:
                            break
                    except Exception as pattern_error:
                        logger.debug(f"Pattern hatası {pattern}: {pattern_error}")
                        continue
            
            result = sorted(list(arac_numbers))
            logger.info(f"Çıkarılan ARAÇ numaraları: {result}")
            return result
            
        except Exception as e:
            logger.error(f"ARAÇ numarası çıkarma hatası: {e}")
            return []
    
    def _get_arac_data(self, arac_no: int) -> pd.DataFrame:
        """Belirli ARAÇ numarasına ait verileri filtrele - DÜZELTME"""
        try:
            if not self.arac_column_name:
                logger.error("ARAÇ sütunu belirlenmemiş")
                return pd.DataFrame()
            
            arac_column = self.current_data[self.arac_column_name]
            
            # ARAÇ numarasını string olarak hazırla (01, 04 vs formatında)
            arac_str_padded = f"{arac_no:02d}"  # 1 -> "01", 11 -> "11"
            arac_str_normal = str(arac_no)      # 1 -> "1", 11 -> "11"
            
            # Doğrudan eşleşme için mask oluştur
            mask = pd.Series([False] * len(arac_column))
            
            for idx, value in enumerate(arac_column):
                if pd.notna(value):
                    value_str = str(value).strip()
                    
                    # TAM EŞLEŞTİRME kontrolü - sadece bu ARAÇ numarası olmalı
                    # Örnek: "01" == "01" ✓, "11" != "01" ✓
                    if value_str == arac_str_padded or value_str == arac_str_normal:
                        mask.iloc[idx] = True
                        continue
                    
                    # Format içinde tam eşleştirme (köşeli parantez veya ARAÇ kelimesi ile)
                    # Daha katı kontrol: sayıdan önce ve sonra sayı olmamalı
                    import re
                    
                    # Patterns - word boundary (\b) kullanarak kesin eşleştirme
                    patterns = [
                        rf'\[İZMİR ARAÇ {arac_str_padded}\]',     # [İZMİR ARAÇ 01]
                        rf'\[İZMİR ARAÇ {arac_str_normal}\]',     # [İZMİR ARAÇ 1]
                        rf'\bİZMİR ARAÇ {arac_str_padded}\b',     # İZMİR ARAÇ 01
                        rf'\bİZMİR ARAÇ {arac_str_normal}\b',     # İZMİR ARAÇ 1
                        rf'\bARAÇ {arac_str_padded}\b',           # ARAÇ 01
                        rf'\bARAÇ {arac_str_normal}\b',           # ARAÇ 1
                        rf'^{arac_str_padded}$',                  # Sadece 01
                        rf'^{arac_str_normal}$',                  # Sadece 1
                    ]
                    
                    value_upper = value_str.upper()
                    for pattern in patterns:
                        if re.search(pattern, value_upper):
                            mask.iloc[idx] = True
                            break
            
            filtered_data = self.current_data[mask].copy()
            
            if not filtered_data.empty:
                logger.info(f"ARAÇ {arac_no} için {len(filtered_data)} kayıt bulundu")
                # Debug: hangi değerler eşleşti
                matched_values = arac_column[mask].unique()
                logger.debug(f"ARAÇ {arac_no} için eşleşen değerler: {matched_values}")
            else:
                logger.warning(f"ARAÇ {arac_no} için kayıt bulunamadı")
                # Debug: tüm değerleri logla
                all_values = arac_column.unique()
                logger.debug(f"Mevcut tüm ARAÇ değerleri: {[str(v) for v in all_values if pd.notna(v)]}")
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"ARAÇ {arac_no} veri alma hatası: {e}")
            return pd.DataFrame()
    
    def _analyze_single_arac_internal(self, arac_no: int) -> Optional[Dict]:
        """Tek ARAÇ için detaylı analiz - DÜZELTİLMİŞ"""
        try:
            arac_data = self._get_arac_data(arac_no)
            
            if arac_data.empty:
                logger.warning(f"ARAÇ {arac_no} için veri bulunamadı")
                return None
            
            logger.info(f"ARAÇ {arac_no} analizi başlatıldı: {len(arac_data)} kayıt")
            
            analysis = {
                'arac_no': str(arac_no),
                'analiz_tarihi': self.last_analysis_date.isoformat(),
                'musteri_sayisi': len(arac_data),
                'toplam_bakiye': 0.0,
                'acik_hesap': 0.0,
                'yaslanding_analizi': {},
                'musteri_detaylari': [],
                'istatistikler': {}
            }
            
            toplam_bakiye = 0.0
            acik_hesap = 0.0
            yaslanding_data = {}
            bakiye_list = []
            
            for idx, row in arac_data.iterrows():
                try:
                    musteri_unvan = str(row[self.cari_column_name]) if pd.notna(row[self.cari_column_name]) else f"Müşteri_{idx}"
                    musteri_info = {
                        'cari_unvan': musteri_unvan,
                        'bakiye_detay': {},
                        'toplam_bakiye': 0.0
                    }
                    
                    musteri_toplam = 0.0
                    musteri_acik = 0.0
                    
                    for col in self.bakiye_columns:
                        try:
                            raw_value = row[col]
                            bakiye_value = 0.0
                            
                            if pd.notna(raw_value):
                                bakiye_value = parse_turkish_number(raw_value)
                            
                            yaslanding_kategori = self._get_yaslanding_category(col)
                            musteri_info['bakiye_detay'][yaslanding_kategori] = bakiye_value
                            
                            if yaslanding_kategori not in yaslanding_data:
                                yaslanding_data[yaslanding_kategori] = 0.0
                            yaslanding_data[yaslanding_kategori] += bakiye_value
                            
                            col_lower = str(col).lower()
                            if 'açık hesap' in col_lower or 'acik hesap' in col_lower:
                                musteri_acik += bakiye_value
                                acik_hesap += bakiye_value
                            
                            musteri_toplam += bakiye_value
                                
                        except Exception as bakiye_error:
                            logger.debug(f"Bakiye hesaplama hatası {col}: {bakiye_error}")
                            continue
                    
                    musteri_info['toplam_bakiye'] = musteri_toplam
                    analysis['musteri_detaylari'].append(musteri_info)
                    
                    toplam_bakiye += musteri_toplam
                    bakiye_list.append(musteri_toplam)
                    
                except Exception as musteri_error:
                    logger.debug(f"Müşteri analiz hatası (satır {idx}): {musteri_error}")
                    continue
            
            analysis['toplam_bakiye'] = toplam_bakiye
            analysis['acik_hesap'] = acik_hesap
            analysis['yaslanding_analizi'] = yaslanding_data
            
            if bakiye_list:
                analysis['istatistikler'] = self._calculate_statistics(bakiye_list, toplam_bakiye)
            
            logger.info(f"ARAÇ {arac_no} analizi tamamlandı: {len(arac_data)} müşteri, Toplam bakiye = {toplam_bakiye:.2f}")
            return analysis
            
        except Exception as e:
            logger.error(f"ARAÇ {arac_no} detay analizi hatası: {e}")
            return None
    
    def _get_yaslanding_category(self, column_name: str) -> str:
        """Sütun adından yaşlandırma kategorisini çıkar"""
        try:
            col_str = str(column_name).lower()
            
            category_mapping = {
                'açık hesap': 'Açık Hesap',
                'acik hesap': 'Açık Hesap',
                '0-7': '0-7 Gün',
                '8-14': '8-14 Gün',
                '15-21': '15-21 Gün',
                '22-28': '22-28 Gün',
                '29-35': '29-35 Gün',
                '36-42': '36-42 Gün',
                '43-49': '43-49 Gün',
                '50-56': '50-56 Gün',
                '57-63': '57-63 Gün',
                '64-70': '64-70 Gün',
                '71-77': '71-77 Gün',
                '77+': '77+ Gün',
                'diğer bakiye': 'Diğer Bakiye',
                'diger bakiye': 'Diğer Bakiye',
                'toplam': 'Toplam',
                'genel toplam': 'Genel Toplam'
            }
            
            for pattern, category in category_mapping.items():
                if pattern in col_str:
                    return category
            
            return col_str
            
        except Exception as e:
            logger.debug(f"Yaşlandırma kategorisi belirleme hatası: {e}")
            return 'Diğer'
    
    def _calculate_statistics(self, bakiye_list: List[float], toplam_bakiye: float) -> Dict:
        """İstatistikleri hesapla"""
        try:
            if not bakiye_list:
                return {}
            
            bakiyeler = np.array(bakiye_list)
            
            stats = {
                'ortalama_bakiye': float(np.mean(bakiyeler)),
                'en_yuksek_bakiye': float(np.max(bakiyeler)),
                'en_dusuk_bakiye': float(np.min(bakiyeler)),
                'medyan_bakiye': float(np.median(bakiyeler)),
                'standart_sapma': float(np.std(bakiyeler)),
                'bakiye_0_olan': int(np.sum(bakiyeler == 0)),
                'bakiye_pozitif_olan': int(np.sum(bakiyeler > 0)),
                'bakiye_negatif_olan': int(np.sum(bakiyeler < 0)),
                'varyans': float(np.var(bakiyeler)),
                'bakiye_araliklari': self._calculate_bakiye_ranges(bakiyeler)
            }
            
            if len(bakiyeler) > 1:
                for percentile in [25, 50, 75, 90, 95]:
                    stats[f'percentile_{percentile}'] = float(np.percentile(bakiyeler, percentile))
            
            return stats
            
        except Exception as e:
            logger.error(f"İstatistik hesaplama hatası: {e}")
            return {}
    
    def _calculate_bakiye_ranges(self, bakiyeler: np.array) -> Dict:
        """Bakiye aralıklarını hesapla"""
        try:
            if len(bakiyeler) == 0:
                return {}
            
            ranges = {
                '0-100': 0,
                '100-500': 0,
                '500-1000': 0,
                '1000-5000': 0,
                '5000-10000': 0,
                '10000+': 0
            }
            
            for bakiye in bakiyeler:
                if bakiye <= 100:
                    ranges['0-100'] += 1
                elif bakiye <= 500:
                    ranges['100-500'] += 1
                elif bakiye <= 1000:
                    ranges['500-1000'] += 1
                elif bakiye <= 5000:
                    ranges['1000-5000'] += 1
                elif bakiye <= 10000:
                    ranges['5000-10000'] += 1
                else:
                    ranges['10000+'] += 1
            
            return ranges
            
        except Exception as e:
            logger.debug(f"Bakiye aralığı hesaplama hatası: {e}")
            return {}
    
    def get_arac_list(self) -> List[str]:
        """Mevcut ARAÇ listesini döndür"""
        try:
            if self.current_data is None:
                return []
            
            arac_numbers = self._extract_arac_numbers()
            return [str(num) for num in arac_numbers]
            
        except Exception as e:
            logger.error(f"ARAÇ listesi alma hatası: {e}")
            return []
    
    def get_summary_statistics(self) -> Dict:
        """Genel özet istatistikleri"""
        try:
            if not self.analysis_results:
                return {
                    'toplam_arac_sayisi': 0,
                    'toplam_musteri_sayisi': 0,
                    'toplam_bakiye': 0.0,
                    'toplam_acik_hesap': 0.0,
                    'ortalama_musteri_per_arac': 0.0,
                    'ortalama_bakiye_per_arac': 0.0,
                    'analiz_tarihi': None
                }
            
            total_aracs = len(self.analysis_results)
            total_customers = sum(
                result.get('musteri_sayisi', 0) 
                for result in self.analysis_results.values()
            )
            total_balance = sum(
                result.get('toplam_bakiye', 0.0) 
                for result in self.analysis_results.values()
            )
            total_open_balance = sum(
                result.get('acik_hesap', 0.0) 
                for result in self.analysis_results.values()
            )
            
            return {
                'toplam_arac_sayisi': total_aracs,
                'toplam_musteri_sayisi': total_customers,
                'toplam_bakiye': total_balance,
                'toplam_acik_hesap': total_open_balance,
                'ortalama_musteri_per_arac': total_customers / total_aracs if total_aracs > 0 else 0.0,
                'ortalama_bakiye_per_arac': total_balance / total_aracs if total_aracs > 0 else 0.0,
                'analiz_tarihi': self.last_analysis_date.isoformat() if self.last_analysis_date else None
            }
            
        except Exception as e:
            logger.error(f"Özet istatistik hatası: {e}")
            return {}
    
    def compare_aracs(self, arac_list: List[str]) -> Dict:
        """ARAÇ'ları karşılaştır"""
        try:
            if not self.analysis_results or not arac_list:
                return {}
            
            comparison = {
                'arac_listesi': arac_list,
                'karsilastirma': {},
                'siralamalar': {}
            }
            
            valid_comparisons = {}
            
            for arac in arac_list:
                if arac in self.analysis_results:
                    result = self.analysis_results[arac]
                    valid_comparisons[arac] = {
                        'musteri_sayisi': result.get('musteri_sayisi', 0),
                        'toplam_bakiye': result.get('toplam_bakiye', 0.0),
                        'acik_hesap': result.get('acik_hesap', 0.0),
                        'ortalama_bakiye': result.get('istatistikler', {}).get('ortalama_bakiye', 0.0)
                    }
            
            comparison['karsilastirma'] = valid_comparisons
            
            if valid_comparisons:
                comparison['siralamalar']['musteri_sayisi'] = sorted(
                    valid_comparisons.items(),
                    key=lambda x: x[1]['musteri_sayisi'],
                    reverse=True
                )
                
                comparison['siralamalar']['toplam_bakiye'] = sorted(
                    valid_comparisons.items(),
                    key=lambda x: x[1]['toplam_bakiye'],
                    reverse=True
                )
            
            return comparison
            
        except Exception as e:
            logger.error(f"ARAÇ karşılaştırma hatası: {e}")
            return {}
    
    def get_aging_analysis(self, arac_no: str = None) -> Dict:
        """Yaşlandırma analizi"""
        try:
            if not self.analysis_results:
                return {}
            
            if arac_no:
                arac_key = str(arac_no)
                if arac_key in self.analysis_results:
                    return self.analysis_results[arac_key].get('yaslanding_analizi', {})
                else:
                    logger.warning(f"ARAÇ {arac_no} analiz sonuçlarında bulunamadı")
                    return {}
            else:
                total_aging = {}
                for result in self.analysis_results.values():
                    yaslanding_analizi = result.get('yaslanding_analizi', {})
                    for period, amount in yaslanding_analizi.items():
                        if period not in total_aging:
                            total_aging[period] = 0.0
                        total_aging[period] += amount
                
                return total_aging
                
        except Exception as e:
            logger.error(f"Yaşlandırma analizi hatası: {e}")
            return {}
    
    def validate_analysis_data(self) -> Dict:
        """Analiz verilerinin doğruluğunu kontrol et"""
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': [],
                'summary': {}
            }
            
            if self.current_data is None:
                validation_result['valid'] = False
                validation_result['errors'].append("Veri seti yüklenmemiş")
                return validation_result
            
            if not self.arac_column_name:
                validation_result['errors'].append("ARAÇ sütunu bulunamadı")
            
            if not self.cari_column_name:
                validation_result['warnings'].append("Cari ünvan sütunu bulunamadı")
            
            if not self.bakiye_columns:
                validation_result['errors'].append("Bakiye sütunları bulunamadı")
            
            if self.arac_column_name:
                arac_numbers = self._extract_arac_numbers()
                validation_result['summary']['valid_arac_count'] = len(arac_numbers)
                validation_result['summary']['arac_numbers'] = arac_numbers
                
                if len(arac_numbers) == 0:
                    validation_result['warnings'].append("Geçerli ARAÇ numarası bulunamadı")
                
                sample_values = self.current_data[self.arac_column_name].unique()[:5]
                validation_result['summary']['sample_arac_values'] = [str(v) for v in sample_values if pd.notna(v)]
            
            if self.bakiye_columns:
                validation_result['summary']['bakiye_column_count'] = len(self.bakiye_columns)
                
                sample_bakiye_values = {}
                for col in self.bakiye_columns[:5]:
                    sample_values = self.current_data[col].dropna().head(3).tolist()
                    sample_bakiye_values[col] = sample_values
                validation_result['summary']['sample_bakiye_values'] = sample_bakiye_values
            
            if validation_result['errors']:
                validation_result['valid'] = False
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Veri doğrulama hatası: {e}")
            return {
                'valid': False,
                'errors': [f"Doğrulama hatası: {e}"],
                'warnings': [],
                'summary': {}
            }
    
    def clear_cache(self):
        """Cache'i temizle"""
        self._validation_cache.clear()
        logger.info("Analiz cache'i temizlendi")
    
    def get_data_info(self) -> Dict:
        """Veri seti hakkında bilgi al"""
        try:
            if self.current_data is None:
                return {'status': 'no_data'}
            
            info = {
                'status': 'loaded',
                'row_count': len(self.current_data),
                'column_count': len(self.current_data.columns),
                'columns': list(self.current_data.columns),
                'memory_usage': self.current_data.memory_usage(deep=True).sum(),
                'arac_column': self.arac_column_name,
                'cari_column': self.cari_column_name,
                'bakiye_columns': self.bakiye_columns,
                'analysis_results_count': len(self.analysis_results)
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Veri bilgisi alma hatası: {e}")
            return {'status': 'error', 'error': str(e)}