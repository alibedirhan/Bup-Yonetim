# veri_analizi.py - Düzeltilmiş ve Refactored Versiyon

import pandas as pd
import numpy as np

# Frozen mode için import düzeltmesi
try:
    from .data_operations import DataCleaner, DataAnalyzer, DataValidator
    from .themes import get_colors, get_color
except ImportError:
    try:
        from KARLILIK_ANALIZI.data_operations import DataCleaner, DataAnalyzer, DataValidator
        from KARLILIK_ANALIZI.themes import get_colors, get_color
    except ImportError:
        from data_operations import DataCleaner, DataAnalyzer, DataValidator
        from themes import get_colors, get_color


class VeriAnalizi:
    def __init__(self, df):
        """
        Karlılık analizi sonuçlarını analiz eden sınıf - Refactored
        
        Args:
            df: Pandas DataFrame - Karlılık analizi sonuç verisi
        """
        if df is None or df.empty:
            self.original_df = pd.DataFrame()
            self.df = pd.DataFrame()
        else:
            # Deep copy ile güvenli kopyalama
            self.original_df = df.copy(deep=True)
            self.df = self.original_df.copy(deep=True)
        
        # Cache için
        self._stok_column_cache = None
        self._miktar_column_cache = None
        
        # Tema renkleri - themes.py'den al
        self.colors = get_colors()
        
        self.clean_data()
    
    def clean_data(self):
        """Veriyi analiz için temizle - data_operations.py entegreli"""
        if self.df.empty:
            return
            
        try:
            # Sayısal sütunları temizle - DataCleaner kullan
            numeric_columns = ['Birim Maliyet', 'Birim Kar', 'Net Kar']
            for col in numeric_columns:
                if col in self.df.columns:
                    try:
                        # DataCleaner.safe_numeric_conversion kullan
                        self.df[col] = DataCleaner.safe_numeric_conversion(self.df[col], default_value=0.0)
                    except (KeyError, ValueError, TypeError):
                        # Hata durumunda sütunu 0 ile doldur
                        self.df[col] = 0.0
            
            # Miktar sütununu bul ve temizle - DataAnalyzer kullan
            miktar_col = self.find_miktar_column()
            if miktar_col and miktar_col in self.df.columns:
                try:
                    self.df[miktar_col] = DataCleaner.safe_numeric_conversion(self.df[miktar_col], default_value=0.0)
                except (KeyError, ValueError, TypeError):
                    pass
                        
        except Exception:
            pass
    
    def get_kpi_summary(self):
        """Temel KPI özetini döndür - data_operations.py entegreli"""
        if self.df.empty:
            return self._get_empty_kpi()
        
        try:
            # DataFrame doğrulama - DataValidator kullan
            is_valid, error_msg = DataValidator.validate_dataframe(
                self.df, 
                required_columns=['Net Kar'], 
                min_rows=1
            )
            
            if not is_valid:
                return self._get_empty_kpi()
            
            # Güvenli kar hesaplama - DataCleaner kullan
            net_kar_col = 'Net Kar'
            kar_series = DataCleaner.safe_numeric_conversion(self.df[net_kar_col])
            valid_kar_series = kar_series.dropna()
            
            # Toplam kar
            toplam_kar = float(valid_kar_series.sum()) if not valid_kar_series.empty else 0.0
            
            # En karlı ürün - DataAnalyzer kullan
            en_karli_urun = 'Veri Yok'
            en_karli_urun_kar = 0.0
            
            if not valid_kar_series.empty and len(self.df) > 0:
                try:
                    max_kar_idx = valid_kar_series.idxmax()
                    if pd.notna(max_kar_idx) and max_kar_idx in self.df.index:
                        # Stok ismi sütununu bul - DataAnalyzer kullan
                        stok_col = self.find_stok_column()
                        if stok_col and stok_col in self.df.columns:
                            product_name = self.df.loc[max_kar_idx, stok_col]
                            en_karli_urun = str(product_name) if pd.notna(product_name) else "Bilinmiyor"
                            en_karli_urun_kar = float(valid_kar_series.loc[max_kar_idx])
                except (KeyError, IndexError, ValueError, TypeError):
                    pass
            
            # Ortalama kar
            ortalama_kar = float(valid_kar_series.mean()) if not valid_kar_series.empty else 0.0
            
            # Ürün sayıları - güvenli hesaplama
            toplam_urun = len(self.df)
            try:
                pozitif_kar_urun = len(valid_kar_series[valid_kar_series > 0])
                negatif_kar_urun = len(valid_kar_series[valid_kar_series < 0])
            except (KeyError, TypeError):
                pozitif_kar_urun = 0
                negatif_kar_urun = 0
            
            # Toplam satış miktarı - DataAnalyzer kullan
            toplam_satis_miktar = 0.0
            miktar_col = self.find_miktar_column()
            if miktar_col and miktar_col in self.df.columns:
                try:
                    miktar_series = DataCleaner.safe_numeric_conversion(self.df[miktar_col])
                    valid_miktar = miktar_series.dropna()
                    toplam_satis_miktar = float(valid_miktar.sum()) if not valid_miktar.empty else 0.0
                except (KeyError, TypeError, ValueError):
                    toplam_satis_miktar = 0.0
            
            return {
                'toplam_kar': round(toplam_kar, 2),
                'en_karli_urun': en_karli_urun,
                'en_karli_urun_kar': round(en_karli_urun_kar, 2),
                'ortalama_kar': round(ortalama_kar, 2),
                'toplam_urun': int(toplam_urun),
                'pozitif_kar_urun': int(pozitif_kar_urun),
                'negatif_kar_urun': int(negatif_kar_urun),
                'toplam_satis_miktar': round(toplam_satis_miktar, 0)
            }
            
        except Exception:
            return self._get_empty_kpi()
    
    def _get_empty_kpi(self):
        """Boş KPI yapısı döndür"""
        return {
            'toplam_kar': 0,
            'en_karli_urun': 'Veri Yok',
            'en_karli_urun_kar': 0,
            'ortalama_kar': 0,
            'toplam_urun': 0,
            'pozitif_kar_urun': 0,
            'negatif_kar_urun': 0,
            'toplam_satis_miktar': 0
        }
    
    def find_stok_column(self):
        """Stok ismi sütununu bul - data_operations.py entegreli"""
        if self._stok_column_cache is not None:
            return self._stok_column_cache
            
        if self.df.empty:
            return None
            
        # DataAnalyzer kullanarak bul
        stok_patterns = [
            'stok ismi', 'stok isim', 'stok kodu', 'stok kod',
            'ürün adı', 'urun adi', 'ürün', 'urun'
        ]
        
        stok_col = DataAnalyzer.find_column_by_pattern(self.df, stok_patterns)
        
        # Alternatif: İlk sütunu kullan
        if not stok_col and len(self.df.columns) > 0:
            stok_col = self.df.columns[0]
            
        self._stok_column_cache = stok_col
        return stok_col
    
    def find_miktar_column(self):
        """Satış miktar sütununu bul - data_operations.py entegreli"""
        if self._miktar_column_cache is not None:
            return self._miktar_column_cache
            
        if self.df.empty:
            return None
            
        # Önce tam eşleşme ara
        possible_names = ['Satış Miktar', 'Satış\nMiktar', 'Satis Miktar', 'Miktar']
        for col in self.df.columns:
            if col in possible_names:
                self._miktar_column_cache = col
                return col
        
        # DataAnalyzer kullanarak pattern arama
        miktar_patterns = ['miktar', 'satis miktar', 'satış miktar']
        miktar_col = DataAnalyzer.find_column_by_pattern(self.df, miktar_patterns)
        
        self._miktar_column_cache = miktar_col
        return miktar_col
    
    def get_top_profitable_products(self, limit=10):
        """En karlı ürünleri döndür - data_operations.py entegreli"""
        if self.df.empty or 'Net Kar' not in self.df.columns:
            return pd.DataFrame()
        
        try:
            stok_col = self.find_stok_column()
            if not stok_col or stok_col not in self.df.columns:
                return pd.DataFrame()
            
            # DataAnalyzer kullanarak en yüksek değerleri al
            top_df = DataAnalyzer.get_top_values(
                self.df, 
                sort_column='Net Kar', 
                limit=limit, 
                ascending=False
            )
            
            if top_df.empty:
                return pd.DataFrame()
            
            # Sadece gerekli sütunları al
            result_cols = [stok_col, 'Net Kar']
            if 'Birim Kar' in top_df.columns:
                result_cols.append('Birim Kar')
            
            # Miktar sütununu bul ve ekle
            miktar_col = self.find_miktar_column()
            if miktar_col and miktar_col in top_df.columns:
                result_cols.append(miktar_col)
            
            available_cols = [col for col in result_cols if col in top_df.columns]
            if not available_cols:
                return pd.DataFrame()
                
            return top_df[available_cols].reset_index(drop=True)
            
        except Exception:
            return pd.DataFrame()
    
    def get_top_selling_products(self, limit=10):
        """En çok satan ürünleri döndür - data_operations.py entegreli"""
        if self.df.empty:
            return pd.DataFrame()
        
        try:
            miktar_col = self.find_miktar_column()
            stok_col = self.find_stok_column()
            
            if not miktar_col or not stok_col or miktar_col not in self.df.columns or stok_col not in self.df.columns:
                return pd.DataFrame()
            
            # DataAnalyzer kullanarak en yüksek değerleri al
            top_df = DataAnalyzer.get_top_values(
                self.df, 
                sort_column=miktar_col, 
                limit=limit, 
                ascending=False
            )
            
            if top_df.empty:
                return pd.DataFrame()
            
            # Gerekli sütunları al
            result_cols = [stok_col, miktar_col]
            if 'Net Kar' in top_df.columns:
                result_cols.append('Net Kar')
            if 'Birim Kar' in top_df.columns:
                result_cols.append('Birim Kar')
            
            available_cols = [col for col in result_cols if col in top_df.columns]
            if not available_cols:
                return pd.DataFrame()
                
            return top_df[available_cols].reset_index(drop=True)
            
        except Exception:
            return pd.DataFrame()
    
    def get_low_profit_products(self, limit=10):
        """En düşük karlı ürünleri döndür - data_operations.py entegreli"""
        if self.df.empty or 'Net Kar' not in self.df.columns:
            return pd.DataFrame()
        
        try:
            stok_col = self.find_stok_column()
            if not stok_col or stok_col not in self.df.columns:
                return pd.DataFrame()
            
            # DataAnalyzer kullanarak en düşük değerleri al
            low_df = DataAnalyzer.get_top_values(
                self.df, 
                sort_column='Net Kar', 
                limit=limit, 
                ascending=True
            )
            
            if low_df.empty:
                return pd.DataFrame()
            
            # Gerekli sütunları al
            result_cols = [stok_col, 'Net Kar']
            if 'Birim Kar' in low_df.columns:
                result_cols.append('Birim Kar')
            
            miktar_col = self.find_miktar_column()
            if miktar_col and miktar_col in low_df.columns:
                result_cols.append(miktar_col)
            
            available_cols = [col for col in result_cols if col in low_df.columns]
            if not available_cols:
                return pd.DataFrame()
                
            return low_df[available_cols].reset_index(drop=True)
            
        except Exception:
            return pd.DataFrame()
    
    def get_profit_distribution(self):
        """Kar dağılımı analizi - data_operations.py delegasyonu"""
        try:
            # DataAnalyzer kullanarak kar dağılımını hesapla
            return DataAnalyzer.calculate_profit_distribution(self.df, 'Net Kar')
        except Exception:
            return {
                'cok_karli': 0,
                'orta_karli': 0,
                'dusuk_karli': 0,
                'zararda': 0
            }
    
    def search_product(self, search_term):
        """Ürün arama - data_operations.py entegreli"""
        if self.df.empty or not search_term:
            return pd.DataFrame()
        
        try:
            stok_col = self.find_stok_column()
            if not stok_col or stok_col not in self.df.columns:
                return pd.DataFrame()
            
            # DataAnalyzer kullanarak filtreleme yap
            criteria = {stok_col: {'contains': search_term}}
            result = DataAnalyzer.filter_data_by_criteria(self.df, criteria)
            
            return result.reset_index(drop=True) if not result.empty else pd.DataFrame()
            
        except Exception:
            return pd.DataFrame()
    
    def get_summary_stats(self):
        """Özet istatistikler - data_operations.py entegreli"""
        if self.df.empty:
            return {}
        
        try:
            stats = {}
            
            # Net Kar istatistikleri - DataAnalyzer kullan
            if 'Net Kar' in self.df.columns:
                try:
                    net_kar_stats = DataAnalyzer.calculate_basic_statistics(self.df, 'Net Kar')
                    # Anahtar isimlerini uygun şekilde düzenle
                    for key, value in net_kar_stats.items():
                        if key == 'sum':
                            stats['kar_toplam'] = value
                        elif key == 'mean':
                            stats['kar_ortalama'] = value
                        elif key == 'median':
                            stats['kar_medyan'] = value
                        elif key == 'std':
                            stats['kar_std'] = value
                except (ValueError, TypeError):
                    pass
            
            # Birim Kar istatistikleri - DataAnalyzer kullan
            if 'Birim Kar' in self.df.columns:
                try:
                    birim_kar_stats = DataAnalyzer.calculate_basic_statistics(self.df, 'Birim Kar')
                    # Anahtar isimlerini uygun şekilde düzenle
                    for key, value in birim_kar_stats.items():
                        if key == 'mean':
                            stats['birim_kar_ortalama'] = value
                        elif key == 'median':
                            stats['birim_kar_medyan'] = value
                except (ValueError, TypeError):
                    pass
            
            # Miktar istatistikleri - DataAnalyzer kullan
            miktar_col = self.find_miktar_column()
            if miktar_col and miktar_col in self.df.columns:
                try:
                    miktar_stats = DataAnalyzer.calculate_basic_statistics(self.df, miktar_col)
                    # Anahtar isimlerini uygun şekilde düzenle
                    for key, value in miktar_stats.items():
                        if key == 'sum':
                            stats['miktar_toplam'] = value
                        elif key == 'mean':
                            stats['miktar_ortalama'] = value
                except (ValueError, TypeError):
                    pass
            
            return stats
            
        except Exception:
            return {}