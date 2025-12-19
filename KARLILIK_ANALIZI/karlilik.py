# karlilik.py - Profesyonel Karlılık Analiz Modülü

import pandas as pd
import numpy as np
import os
import tempfile
import gc
from tkinter import simpledialog, filedialog, messagebox
from typing import Optional, Tuple, Dict, List, Union, Callable
from pathlib import Path


class KarlilikAnalizi:
    """Excel tabanlı karlılık analizleri yapan ana sınıf"""

    def __init__(self, 
                 progress_callback: Optional[Callable[[int, str], None]] = None,
                 log_callback: Optional[Callable[[str, str], None]] = None):
        """
        Args:
            progress_callback: (value: int, status: str) -> None
            log_callback: (message: str, msg_type: str) -> None
        """
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self._temp_files = []

    #region Yardımcı Metodlar
    def _update_progress(self, value: int, status: str) -> None:
        """İlerleme durumunu günceller"""
        if self.progress_callback:
            try:
                self.progress_callback(value, status)
            except Exception as e:
                self._log_message(f"Progress callback error: {str(e)}", 'error')

    def _log_message(self, message: str, msg_type: str = 'info') -> None:
        """Log mesajı gönderir"""
        if self.log_callback:
            try:
                self.log_callback(message, msg_type)
            except Exception as e:
                print(f"Log callback error: {str(e)}")

    @staticmethod
    def _turkce_normalize(text: Union[str, float]) -> str:
        """Türkçe karakterleri normalize eder ve metni standartlaştırır"""
        if pd.isna(text):
            return ""
            
        text = str(text).lower().strip()
        replacements = {
            'ı': 'i', 'i̇': 'i', 'İ': 'i', 'I': 'i',
            'ş': 's', 'Ş': 's', 'ç': 'c', 'Ç': 'c',
            'ğ': 'g', 'Ğ': 'g', 'ü': 'u', 'Ü': 'u',
            'ö': 'o', 'Ö': 'o'
        }
        for tr_char, en_char in replacements.items():
            text = text.replace(tr_char, en_char)
        return text

    @staticmethod
    def _clean_numeric(value: Union[str, float, int]) -> float:
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
        except (ValueError, TypeError) as e:
            return 0.0
            
        return 0.0
    #endregion

    #region Dosya İşlemleri
    def find_header_row(self, file_path: Union[str, Path]) -> int:
        """Excel dosyasında uygun header satırını bulur"""
        for header_row in range(5):  # 0-4 arası satırları kontrol et
            try:
                test_df = pd.read_excel(file_path, header=header_row, nrows=5)
                
                if test_df.empty:
                    continue
                    
                self._log_message(f"Header {header_row} test ediliyor...")
                
                sutun_isimleri = [str(col).lower().strip() for col in test_df.columns]
                
                # Kritik sütunları kontrol et
                has_stok_ismi = any('stok' in sutun and ('ismi' in sutun or 'isim' in sutun or 'kodu' in sutun) 
                                  for sutun in sutun_isimleri)
                has_satis = any('satış' in sutun or 'satis' in sutun for sutun in sutun_isimleri)
                has_miktar = any('miktar' in sutun for sutun in sutun_isimleri)
                has_fiyat = any('fiyat' in sutun for sutun in sutun_isimleri)
                has_tutar = any('tutar' in sutun for sutun in sutun_isimleri)
                
                veri_sutunu_sayisi = sum([has_satis, has_miktar, has_fiyat, has_tutar])
                if has_stok_ismi and veri_sutunu_sayisi >= 2:
                    self._log_message(f"✓ Header satırı {header_row} olarak belirlendi!")
                    return header_row
                    
            except Exception as e:
                self._log_message(f"Header {header_row} hatası: {str(e)}")
                continue
        
        self._log_message("Uygun header bulunamadı, varsayılan olarak header=1 kullanılıyor...")
        return 1  # Varsayılan değer

    def find_stok_column(self, df: pd.DataFrame) -> Optional[str]:
        """DataFrame'de stok sütununu bulur"""
        stok_ismi_col = None
        
        # Önce "stok ismi" ara
        for col in df.columns:
            col_clean = self._turkce_normalize(col)
            if 'stok' in col_clean and ('ismi' in col_clean or 'isim' in col_clean):
                stok_ismi_col = col
                break
        
        # Bulamazsa "stok kodu" ara        
        if not stok_ismi_col:
            for col in df.columns:
                col_clean = self._turkce_normalize(col)
                if 'stok' in col_clean and 'kodu' in col_clean:
                    stok_ismi_col = col
                    break
        
        # Manuel seçim gerekirse
        if not stok_ismi_col:
            self._log_message("Stok sütunu otomatik bulunamadı, manuel seçim gerekli...", 'warning')
            
            columns = list(df.columns)
            sutun_secenekleri = "\n".join([f"{i}: {col}" for i, col in enumerate(columns)])
            
            try:
                secim_str = simpledialog.askstring(
                    "Sütun Seçimi",
                    f"Hangi sütun stok ismi/kodu?\n\n{sutun_secenekleri}\n\nSütun numarasını girin (0-{len(columns)-1}):"
                )
                
                if secim_str is None:
                    self._log_message("✗ Stok sütunu seçilmedi, işlem iptal ediliyor", 'error')
                    return None
                
                secim_index = int(secim_str)
                if 0 <= secim_index < len(columns):
                    stok_ismi_col = columns[secim_index]
                else:
                    self._log_message("✗ Geçersiz sütun numarası", 'error')
                    return None
            except ValueError:
                self._log_message("✗ Geçersiz giriş", 'error')
                return None
        
        return stok_ismi_col

    def find_iskonto_columns(self, df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
        """İskonto dosyasından fiyat ve stok sütunlarını bulur"""
        columns = df.columns.tolist()
        
        # Fiyat sütunu bul
        fiyat_col = None
        for col in columns:
            col_str = self._turkce_normalize(col)
            if 'fiyat' in col_str and 'liste' not in col_str:
                fiyat_col = col
                break
        
        # İskonto stok sütunu bul
        iskonto_stok_col = None
        for col in columns:
            col_clean = self._turkce_normalize(col)
            if 'stok' in col_clean and ('isim' in col_clean or 'ismi' in col_clean):
                iskonto_stok_col = col
                break
        
        # Manuel seçimler
        if not fiyat_col:
            self._log_message("Fiyat sütunu manuel seçim gerekli...", 'warning')
            sutun_secenekleri = "\n".join([f"{i}: {col}" for i, col in enumerate(columns)])
            
            try:
                secim_str = simpledialog.askstring(
                    "Fiyat Sütunu Seçimi",
                    f"Hangi sütun fiyat bilgisi?\n\n{sutun_secenekleri}\n\nSütun numarasını girin:"
                )
                
                if secim_str is None:
                    return None, None
                
                secim_index = int(secim_str)
                if 0 <= secim_index < len(columns):
                    fiyat_col = columns[secim_index]
            except ValueError:
                return None, None
        
        if not iskonto_stok_col:
            self._log_message("İskonto stok sütunu manuel seçim gerekli...", 'warning')
            sutun_secenekleri = "\n".join([f"{i}: {col}" for i, col in enumerate(columns)])
            
            try:
                secim_str = simpledialog.askstring(
                    "Stok İsmi Sütunu Seçimi",
                    f"Hangi sütun stok ismi?\n\n{sutun_secenekleri}\n\nSütun numarasını girin:"
                )
                
                if secim_str is None:
                    return None, None
                
                secim_index = int(secim_str)
                if 0 <= secim_index < len(columns):
                    iskonto_stok_col = columns[secim_index]
            except ValueError:
                return None, None
        
        return fiyat_col, iskonto_stok_col
    #endregion

    #region Fiyat Eşleştirme
    def create_price_dictionary(self, 
                              iskonto_df: pd.DataFrame, 
                              iskonto_stok_col: str, 
                              fiyat_col: str) -> Dict[str, float]:
        """İskonto dosyasından fiyat sözlüğü oluşturur"""
        fiyat_dict = {}
        baslik_sayisi = 0
        
        try:
            for idx, row in iskonto_df.iterrows():
                stok_adi = row[iskonto_stok_col]
                tarih = row.get('Tarih', '')
                depo = row.get('Depo', '')
                fiyat = row[fiyat_col]
                
                stok_bos = pd.isna(stok_adi) or str(stok_adi).lower() == 'nan'
                tarih_bos = pd.isna(tarih) or str(tarih).lower() == 'nan'
                
                if stok_bos and tarih_bos:
                    gercek_stok_adi = str(depo).strip()
                    
                    # Depo adı kontrolleri
                    if (gercek_stok_adi and 
                        gercek_stok_adi.lower() != 'nan' and
                        not any(term in gercek_stok_adi.upper() for term in ['BÖLGE', 'MERKEZ', 'DEPO', 'ŞUBE']) and
                        self._clean_numeric(fiyat) > 0 and
                        gercek_stok_adi not in fiyat_dict):
                        
                        fiyat_dict[gercek_stok_adi] = round(self._clean_numeric(fiyat), 2)
                        baslik_sayisi += 1
                        
                        if baslik_sayisi <= 5:
                            self._log_message(f"Fiyat eşleşmesi: {gercek_stok_adi} → {fiyat}")
        
        except Exception as e:
            self._log_message(f"Fiyat işleme hatası: {str(e)}", 'error')
        
        return fiyat_dict

    def match_prices(self, 
                    karlilik_df: pd.DataFrame, 
                    stok_ismi_col: str, 
                    fiyat_dict: Dict[str, float]) -> Tuple[int, List[str]]:
        """Fiyatları eşleştirir ve sonuçları döndürür"""
        eslesen_sayisi = 0
        eslesmeyenler = []
        
        # Birim Maliyet sütunu yoksa oluştur
        if 'Birim Maliyet' not in karlilik_df.columns:
            karlilik_df['Birim Maliyet'] = 0.0
        
        for idx, row in karlilik_df.iterrows():
            stok_adi = row[stok_ismi_col]
            
            if pd.isna(stok_adi):
                continue
                
            stok_adi = str(stok_adi).strip().upper()
            
            if stok_adi in fiyat_dict:
                karlilik_df.at[idx, 'Birim Maliyet'] = fiyat_dict[stok_adi]
                eslesen_sayisi += 1
            else:
                eslesmeyenler.append(stok_adi)
        
        return eslesen_sayisi, eslesmeyenler
    #endregion

    #region Kar Hesaplamaları
    def calculate_profits(self, karlilik_df: pd.DataFrame) -> None:
        """Kar hesaplamalarını yapar ve DataFrame'i günceller"""
        # Birim Kar hesaplama
        ort_satis_fiyat_col = None
        for col in karlilik_df.columns:
            col_str = self._turkce_normalize(col)
            if 'ort' in col_str and 'satis' in col_str and 'fiyat' in col_str:
                ort_satis_fiyat_col = col
                break
        
        # Alternatif sütun isimleri
        if not ort_satis_fiyat_col:
            alternatif_fiyat_sutunlari = ['Ort.Satış\nFiyat', 'Ort Satış Fiyat', 'Ortalama Fiyat']
            for alt_col in alternatif_fiyat_sutunlari:
                if alt_col in karlilik_df.columns:
                    ort_satis_fiyat_col = alt_col
                    break
        
        if ort_satis_fiyat_col and ort_satis_fiyat_col in karlilik_df.columns:
            # Numeric conversion
            for idx in karlilik_df.index:
                karlilik_df.at[idx, ort_satis_fiyat_col] = self._clean_numeric(karlilik_df.at[idx, ort_satis_fiyat_col])
            
            karlilik_df['Birim Kar'] = karlilik_df[ort_satis_fiyat_col] - karlilik_df['Birim Maliyet']
            self._log_message("✓ Birim Kar hesaplandı")
        else:
            karlilik_df['Birim Kar'] = 0.0
            self._log_message("Ort.Satış Fiyat sütunu bulunamadı", 'warning')
        
        # Net Kar hesaplama
        satis_miktar_col = None
        for col in karlilik_df.columns:
            col_str = self._turkce_normalize(col)
            if 'satis' in col_str and 'miktar' in col_str:
                satis_miktar_col = col
                break
        
        if not satis_miktar_col:
            alternatif_miktar_sutunlari = ['Satış\nMiktar', 'Satis Miktar', 'Miktar']
            for alt_col in alternatif_miktar_sutunlari:
                if alt_col in karlilik_df.columns:
                    satis_miktar_col = alt_col
                    break
        
        if satis_miktar_col and satis_miktar_col in karlilik_df.columns:
            # Numeric conversion
            for idx in karlilik_df.index:
                karlilik_df.at[idx, satis_miktar_col] = self._clean_numeric(karlilik_df.at[idx, satis_miktar_col])
            
            karlilik_df['Net Kar'] = karlilik_df['Birim Kar'] * karlilik_df[satis_miktar_col]
            self._log_message("✓ Net Kar hesaplandı")
        else:
            karlilik_df['Net Kar'] = 0.0
            self._log_message("Satış Miktar sütunu bulunamadı", 'warning')
    #endregion

    #region Sonuç Hazırlama
    def prepare_result_dataframe(self, 
                               karlilik_df: pd.DataFrame, 
                               stok_ismi_col: str) -> pd.DataFrame:
        """Sonuç DataFrame'ini hazırlar - TÜM ürünleri dahil eder"""
        # Sütun seçimi
        istenen_sutunlar = []
        
        if stok_ismi_col and stok_ismi_col in karlilik_df.columns:
            istenen_sutunlar.append(stok_ismi_col)
        
        # Standart sütunlar
        diger_sutunlar = ['Satış Miktar', 'Ort.Satış Fiyat', 'Satış Tutar', 
                         'Birim Maliyet', 'Birim Kar', 'Net Kar']
        
        for sutun in diger_sutunlar:
            if sutun in karlilik_df.columns:
                istenen_sutunlar.append(sutun)
        
        # Alternatif sütun isimleri
        alternatif_sutunlar = {
            'Satış Miktar': ['Satış\nMiktar', 'Satis Miktar', 'Miktar'],
            'Ort.Satış Fiyat': ['Ort.Satış\nFiyat', 'Ort Satış Fiyat', 'Ortalama Fiyat'],
            'Satış Tutar': ['Satış\nTutar', 'Satis Tutar', 'Tutar'],
            'Birim Maliyet': ['Birim\nMaliyet', 'Maliyet'],
            'Birim Kar': ['Birim\nKar', 'Kar'],
            'Net Kar': ['Net\nKar', 'Toplam Kar']
        }
        
        for standart_isim, alternatifler in alternatif_sutunlar.items():
            if standart_isim not in istenen_sutunlar:
                for alt_isim in alternatifler:
                    if alt_isim in karlilik_df.columns:
                        istenen_sutunlar.append(alt_isim)
                        break
        
        # TÜM ÜRÜNLER DAHİL EDİLİR - filtreleme yapılmaz
        try:
            sonuc_df = karlilik_df[istenen_sutunlar].copy()
        except KeyError as e:
            self._log_message(f"Sütun hatası: {str(e)}, mevcut sütunlar kullanılacak", 'warning')
            # Mevcut sütunlardan sadece var olanları al
            mevcut_sutunlar = [col for col in istenen_sutunlar if col in karlilik_df.columns]
            sonuc_df = karlilik_df[mevcut_sutunlar].copy() if mevcut_sutunlar else karlilik_df.copy()
        
        # Sıralama
        if 'Net Kar' in sonuc_df.columns and 'Birim Kar' in sonuc_df.columns:
            sonuc_df = sonuc_df.sort_values(['Net Kar', 'Birim Kar'], ascending=[False, False])
            self._log_message("✓ Veriler Net Kar'a göre sıralandı")
        elif 'Birim Kar' in sonuc_df.columns:
            sonuc_df = sonuc_df.sort_values('Birim Kar', ascending=False)
            self._log_message("✓ Veriler Birim Kar'a göre sıralandı")
        
        self._log_message(f"✓ Sonuç DataFrame'i hazırlandı: {len(sonuc_df)} ürün")
        
        return sonuc_df

    def save_results(self, 
                    sonuc_df: pd.DataFrame, 
                    eslesen_sayisi: int, 
                    eslesmeyenler: List[str]) -> bool:
        """Sonuçları Excel dosyası olarak kaydeder"""
        try:
            output_path = filedialog.asksaveasfilename(
                title="Karlılık Analizi Sonuçlarını Kaydet",
                defaultextension=".xlsx",
                filetypes=[("Excel dosyaları", "*.xlsx"), ("Tüm dosyalar", "*.*")]
            )
            
            if not output_path:
                self._log_message("Dosya kaydetme iptal edildi", 'warning')
                return False
            
            # Güvenli özet hesaplama
            total_net_kar = sonuc_df['Net Kar'].sum() if 'Net Kar' in sonuc_df.columns else 0
            
            avg_birim_maliyet = 0
            if 'Birim Maliyet' in sonuc_df.columns:
                maliyet_data = sonuc_df[sonuc_df['Birim Maliyet'] > 0]['Birim Maliyet']
                avg_birim_maliyet = maliyet_data.mean() if len(maliyet_data) > 0 else 0
            
            avg_birim_kar = 0
            if 'Birim Kar' in sonuc_df.columns:
                kar_data = sonuc_df['Birim Kar']
                avg_birim_kar = kar_data.mean() if len(kar_data) > 0 else 0
            
            doluluk_orani = (eslesen_sayisi / len(sonuc_df)) * 100 if len(sonuc_df) > 0 else 0
            
            # Excel kaydetme
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                sonuc_df.to_excel(writer, sheet_name='Karlılık Analizi', index=False)
                
                # Özet sayfası
                ozet_data = {
                    'Bilgi': ['Toplam Stok Sayısı', 'Eşleşen Stok Sayısı', 'Eşleşmeyen Stok Sayısı', 
                              'Doluluk Oranı (%)', 'Ortalama Birim Maliyet', 'Ortalama Birim Kar', 'Toplam Net Kar'],
                    'Değer': [
                        len(sonuc_df),
                        eslesen_sayisi,
                        len(sonuc_df) - eslesen_sayisi,
                        f"{doluluk_orani:.1f}",
                        f"{avg_birim_maliyet:.2f}",
                        f"{avg_birim_kar:.2f}",
                        f"{total_net_kar:.2f}"
                    ]
                }
                ozet_df = pd.DataFrame(ozet_data)
                ozet_df.to_excel(writer, sheet_name='Özet', index=False)
            
            self._log_message(f"✓ Sonuçlar kaydedildi: {os.path.basename(output_path)}")
            self._log_message(f"📊 Özet: {eslesen_sayisi} eşleşen / {len(eslesmeyenler)} eşleşmeyen")
            self._log_message(f"📈 Doluluk Oranı: %{doluluk_orani:.1f}")
            
            return True
        
        except PermissionError:
            self._log_message("✗ Dosya yazma izni reddedildi. Dosya açık olabilir.", 'error')
            return False
        except Exception as e:
            self._log_message(f"Excel kaydetme hatası: {str(e)}", 'error')
            return False
    #endregion

    #region Ana Analiz Fonksiyonu
    def analyze(self, 
               karlilik_path: Union[str, Path], 
               iskonto_path: Union[str, Path]) -> Optional[pd.DataFrame]:
        """Ana analiz fonksiyonu - DataFrame döndürür"""
        try:
            self._update_progress(15, "İskonto raporu yükleniyor...")
            
            # İskonto raporunu oku
            iskonto_df = pd.read_excel(iskonto_path)
            
            if iskonto_df.empty:
                self._log_message("✗ İskonto raporu dosyası boş!", 'error')
                return None
                
            self._log_message(f"✓ İskonto Raporu: {len(iskonto_df)} satır yüklendi")
            
            self._update_progress(25, "Karlılık analizi dosyası işleniyor...")
            
            # Karlılık Analizi dosyasını oku - header bul
            header_row = self.find_header_row(karlilik_path)
            karlilik_df = pd.read_excel(karlilik_path, header=header_row)
                
            if karlilik_df.empty:
                self._log_message("✗ Karlılık Analizi dosyası boş veya okunamadı!", 'error')
                return None
                
            self._log_message("✓ Karlılık Analizi dosyası başarıyla yüklendi")
            
            self._update_progress(40, "Sütunlar analiz ediliyor...")
            
            # Stok sütunu bul
            stok_ismi_col = self.find_stok_column(karlilik_df)
            if not stok_ismi_col:
                return None
            
            self._log_message(f"✓ Stok sütunu: {stok_ismi_col}")
            
            # İskonto dosyası sütunları
            fiyat_col, iskonto_stok_col = self.find_iskonto_columns(iskonto_df)
            if not fiyat_col or not iskonto_stok_col:
                return None
            
            self._log_message(f"✓ Bulunan sütunlar: Stok={stok_ismi_col}, Fiyat={fiyat_col}")
            
            # Sütun kontrolleri
            if stok_ismi_col not in karlilik_df.columns:
                self._log_message("✗ Stok sütunu bulunamadı!", 'error')
                return None
            if iskonto_stok_col not in iskonto_df.columns:
                self._log_message("✗ İskonto stok sütunu bulunamadı!", 'error')
                return None
            if fiyat_col not in iskonto_df.columns:
                self._log_message("✗ Fiyat sütunu bulunamadı!", 'error')
                return None
            
            self._update_progress(60, "Veriler temizleniyor...")
            
            # Birim Maliyet sütunu ekle
            if 'Birim Maliyet' not in karlilik_df.columns:
                karlilik_df['Birim Maliyet'] = 0.0
            
            # Veri temizleme
            karlilik_df = karlilik_df[karlilik_df[stok_ismi_col].notna()].copy()
            iskonto_df = iskonto_df[iskonto_df[iskonto_stok_col].notna()].copy()
            
            if karlilik_df.empty or iskonto_df.empty:
                self._log_message("✗ Veriler temizleme sonrası boş kaldı!", 'error')
                return None
            
            # String temizleme
            karlilik_df[stok_ismi_col] = karlilik_df[stok_ismi_col].astype(str).str.strip().str.upper()
            iskonto_df[iskonto_stok_col] = iskonto_df[iskonto_stok_col].astype(str).str.strip().str.upper()
            
            # TOPLAM satırlarını kaldır
            karlilik_df = karlilik_df[~karlilik_df[stok_ismi_col].str.contains('TOPLAM|TOTAL|GENEL', case=False, na=False)].copy()
            iskonto_df = iskonto_df[~iskonto_df[iskonto_stok_col].str.contains('TOPLAM|TOTAL|GENEL', case=False, na=False)].copy()
            
            self._update_progress(70, "Fiyat bilgileri işleniyor...")
            
            # Fiyat sütunu temizleme
            for idx in iskonto_df.index:
                iskonto_df.at[idx, fiyat_col] = self._clean_numeric(iskonto_df.at[idx, fiyat_col])
            
            # CSV işleme (bazı format sorunları için)
            try:
                with tempfile.NamedTemporaryFile(mode='w+', suffix='.csv', delete=False, encoding='utf-8') as temp_file:
                    csv_path = temp_file.name
                    self._temp_files.append(csv_path)
                
                temp_df = pd.read_excel(iskonto_path)
                temp_df.to_csv(csv_path, index=False, encoding='utf-8')
                csv_df = pd.read_csv(csv_path, encoding='utf-8')
                iskonto_df = csv_df.copy()
                
                del temp_df, csv_df
                gc.collect()
                
            except Exception as e:
                self._log_message(f"CSV çevirme hatası: {str(e)}", 'warning')
            
            self._update_progress(80, "Fiyat eşleştirme yapılıyor...")
            
            # Fiyat dictionary oluştur
            fiyat_dict = self.create_price_dictionary(iskonto_df, iskonto_stok_col, fiyat_col)
            self._log_message(f"✓ {len(fiyat_dict)} stok için fiyat bilgisi alındı")
            
            self._update_progress(85, "Stok eşleştirme yapılıyor...")
            
            # Eşleştirme işlemi
            eslesen_sayisi, eslesmeyenler = self.match_prices(karlilik_df, stok_ismi_col, fiyat_dict)
            
            # Birim Maliyet temizleme
            for idx in karlilik_df.index:
                karlilik_df.at[idx, 'Birim Maliyet'] = self._clean_numeric(karlilik_df.at[idx, 'Birim Maliyet'])
            
            self._update_progress(90, "Kar hesaplamaları yapılıyor...")
            
            # Kar hesaplamalarını yap
            self.calculate_profits(karlilik_df)
            
            self._log_message(f"✓ Eşleştirme tamamlandı: {eslesen_sayisi} eşleşen, {len(eslesmeyenler)} eşleşmeyen")
            
            self._update_progress(95, "Sonuçlar kaydediliyor...")
            
            # Sonuç dataframe'ini hazırla
            sonuc_df = self.prepare_result_dataframe(karlilik_df, stok_ismi_col)
            
            # Dosya kaydetme
            save_result = self.save_results(sonuc_df, eslesen_sayisi, eslesmeyenler)
            
            # Başarılı kayıt sonrası DataFrame'i döndür
            if save_result:
                return sonuc_df
            else:
                return None
                
        except Exception as e:
            self._log_message(f"✗ HATA: {str(e)}", 'error')
            return None
        finally:
            # Temizlik
            self._cleanup_temp_files()
            gc.collect()
    
    def _cleanup_temp_files(self) -> None:
        """Geçici dosyaları temizler"""
        for temp_file in self._temp_files:
            try:
                if temp_file and os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception as e:
                self._log_message(f"Geçici dosya silme hatası: {str(e)}", 'warning')
        
        self._temp_files.clear()
    
    def process_files(self, karlilik_path: str, iskonto_path: str) -> Optional[Dict]:
        """
        Ana işlem fonksiyonu - UI'dan çağrılır
        
        Returns:
            Dict: {'dataframe': DataFrame, 'matched_count': int, ...} veya None
        """
        try:
            result_df = self.analyze(karlilik_path, iskonto_path)
            
            if result_df is not None and not result_df.empty:
                # Eşleşen sayısını hesapla
                matched = len(result_df[result_df['Birim Maliyet'] > 0]) if 'Birim Maliyet' in result_df.columns else 0
                
                return {
                    'dataframe': result_df,
                    'matched_count': matched,
                    'total_count': len(result_df),
                    'success': True
                }
            else:
                return None
                
        except Exception as e:
            self._log_message(f"process_files hatası: {str(e)}", 'error')
            return None
    #endregion