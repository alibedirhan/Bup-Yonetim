#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - Görselleştirme Modülü
Analiz sonuçları için grafik ve chart oluşturma sistemi
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd
import numpy as np

# Frozen mode için import düzeltmesi
try:
    from ..utils import format_turkish_number
except ImportError:
    try:
        from YASLANDIRMA.utils import format_turkish_number
    except ImportError:
        from utils import format_turkish_number

logger = logging.getLogger(__name__)

# Türkçe font ve stil ayarları
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
sns.set_palette("husl")

class VisualizationEngine:
    def __init__(self):
        self.figure_size = (12, 8)
        self.color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                             '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        self.current_figures = {}
    
    def create_arac_summary_chart(self, analysis_results: Dict) -> Optional[plt.Figure]:
        """
        ARAÇ özet grafiği oluştur
        
        Args:
            analysis_results: Analiz sonuçları
            
        Returns:
            matplotlib.Figure: Grafik figürü
        """
        try:
            if not analysis_results:
                logger.error("Grafik için analiz verisi bulunamadı")
                return None
            
            # Veri hazırlama
            arac_nos = []
            musteri_sayilari = []
            bakiyeler = []
            
            for arac_no, analysis in analysis_results.items():
                arac_nos.append(f"ARAÇ {arac_no}")
                musteri_sayilari.append(analysis.get('musteri_sayisi', 0))
                bakiyeler.append(analysis.get('toplam_bakiye', 0))
            
            # Figure oluştur
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figure_size)
            fig.suptitle('ARAÇ Özet Analizi', fontsize=16, fontweight='bold')
            
            # Müşteri sayıları bar chart
            bars1 = ax1.bar(arac_nos, musteri_sayilari, color=self.color_palette[0], alpha=0.7)
            ax1.set_title('ARAÇ Başına Müşteri Sayısı')
            ax1.set_ylabel('Müşteri Sayısı')
            ax1.tick_params(axis='x', rotation=45)
            
            # Bar üzerine değer yazma
            for bar, value in zip(bars1, musteri_sayilari):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{value}', ha='center', va='bottom')
            
            # Bakiye miktarları bar chart
            bars2 = ax2.bar(arac_nos, bakiyeler, color=self.color_palette[1], alpha=0.7)
            ax2.set_title('ARAÇ Başına Toplam Bakiye')
            ax2.set_ylabel('Bakiye (TL)')
            ax2.set_xlabel('ARAÇ No')
            ax2.tick_params(axis='x', rotation=45)
            
            # Y ekseni formatı (büyük sayılar için)
            ax2.yaxis.set_major_formatter(plt.FuncFormatter(self._format_currency))
            
            # Bar üzerine değer yazma
            for bar, value in zip(bars2, bakiyeler):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + max(bakiyeler) * 0.01,
                        format_turkish_number(value), ha='center', va='bottom', 
                        fontsize=8, rotation=45)
            
            plt.tight_layout()
            
            self.current_figures['arac_summary'] = fig
            logger.info("ARAÇ özet grafiği oluşturuldu")
            return fig
            
        except Exception as e:
            logger.error(f"ARAÇ özet grafiği oluşturma hatası: {e}")
            return None
    
    def create_aging_analysis_chart(self, analysis_results: Dict) -> Optional[plt.Figure]:
        """
        Yaşlandırma analizi grafiği oluştur
        
        Args:
            analysis_results: Analiz sonuçları
            
        Returns:
            matplotlib.Figure: Grafik figürü
        """
        try:
            if not analysis_results:
                logger.error("Yaşlandırma grafiği için analiz verisi bulunamadı")
                return None
            
            # Toplam yaşlandırma verisi hesapla
            total_aging = {}
            total_balance = 0
            
            for analysis in analysis_results.values():
                yaslanding_analizi = analysis.get('yaslanding_analizi', {})
                for period, amount in yaslanding_analizi.items():
                    if period not in total_aging:
                        total_aging[period] = 0
                    total_aging[period] += amount
                    total_balance += amount
            
            if not total_aging:
                logger.warning("Yaşlandırma verisi bulunamadı")
                return None
            
            # Veri sıralama
            periods = list(total_aging.keys())
            amounts = list(total_aging.values())
            percentages = [amount/total_balance*100 if total_balance > 0 else 0 for amount in amounts]
            
            # Figure oluştur
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            fig.suptitle('Yaşlandırma Analizi', fontsize=16, fontweight='bold')
            
            # Pie chart
            wedges, texts, autotexts = ax1.pie(amounts, labels=periods, autopct='%1.1f%%',
                                              colors=self.color_palette[:len(periods)],
                                              startangle=90)
            ax1.set_title('Yaşlandırma Dağılımı (%)')
            
            # Bar chart
            bars = ax2.bar(periods, amounts, color=self.color_palette[:len(periods)], alpha=0.7)
            ax2.set_title('Yaşlandırma Miktarları')
            ax2.set_ylabel('Bakiye (TL)')
            ax2.set_xlabel('Yaşlandırma Dönemi')
            ax2.tick_params(axis='x', rotation=45)
            ax2.yaxis.set_major_formatter(plt.FuncFormatter(self._format_currency))
            
            # Bar üzerine değer yazma
            for bar, amount in zip(bars, amounts):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + max(amounts) * 0.01,
                        format_turkish_number(amount), ha='center', va='bottom',
                        fontsize=8, rotation=45)
            
            plt.tight_layout()
            
            self.current_figures['aging_analysis'] = fig
            logger.info("Yaşlandırma analizi grafiği oluşturuldu")
            return fig
            
        except Exception as e:
            logger.error(f"Yaşlandırma analizi grafiği oluşturma hatası: {e}")
            return None
    
    def create_comparison_chart(self, analysis_results: Dict, arac_list: List[str] = None) -> Optional[plt.Figure]:
        """
        ARAÇ karşılaştırma grafiği oluştur
        
        Args:
            analysis_results: Analiz sonuçları
            arac_list: Karşılaştırılacak ARAÇ listesi
            
        Returns:
            matplotlib.Figure: Grafik figürü
        """
        try:
            if not analysis_results:
                logger.error("Karşılaştırma grafiği için analiz verisi bulunamadı")
                return None
            
            # ARAÇ listesi kontrolü
            if not arac_list:
                arac_list = list(analysis_results.keys())[:10]  # En fazla 10 ARAÇ
            else:
                arac_list = arac_list[:10]  # Sınırla
            
            # Veri hazırlama
            arac_labels = []
            musteri_sayilari = []
            bakiyeler = []
            acik_hesaplar = []
            
            for arac_no in arac_list:
                if arac_no in analysis_results:
                    analysis = analysis_results[arac_no]
                    arac_labels.append(f"ARAÇ {arac_no}")
                    musteri_sayilari.append(analysis.get('musteri_sayisi', 0))
                    bakiyeler.append(analysis.get('toplam_bakiye', 0))
                    acik_hesaplar.append(analysis.get('acik_hesap', 0))
            
            if not arac_labels:
                logger.warning("Karşılaştırma için veri bulunamadı")
                return None
            
            # Figure oluştur
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('ARAÇ Karşılaştırma Analizi', fontsize=16, fontweight='bold')
            
            # 1. Müşteri sayıları
            bars1 = ax1.bar(arac_labels, musteri_sayilari, color=self.color_palette[0], alpha=0.7)
            ax1.set_title('Müşteri Sayıları')
            ax1.set_ylabel('Müşteri Sayısı')
            ax1.tick_params(axis='x', rotation=45)
            self._add_value_labels(ax1, bars1, musteri_sayilari)
            
            # 2. Toplam bakiyeler
            bars2 = ax2.bar(arac_labels, bakiyeler, color=self.color_palette[1], alpha=0.7)
            ax2.set_title('Toplam Bakiyeler')
            ax2.set_ylabel('Bakiye (TL)')
            ax2.tick_params(axis='x', rotation=45)
            ax2.yaxis.set_major_formatter(plt.FuncFormatter(self._format_currency))
            self._add_value_labels(ax2, bars2, bakiyeler, format_values=True)
            
            # 3. Açık hesaplar
            bars3 = ax3.bar(arac_labels, acik_hesaplar, color=self.color_palette[2], alpha=0.7)
            ax3.set_title('Açık Hesaplar')
            ax3.set_ylabel('Açık Hesap (TL)')
            ax3.set_xlabel('ARAÇ No')
            ax3.tick_params(axis='x', rotation=45)
            ax3.yaxis.set_major_formatter(plt.FuncFormatter(self._format_currency))
            self._add_value_labels(ax3, bars3, acik_hesaplar, format_values=True)
            
            # 4. Müşteri başına ortalama bakiye
            ortalama_bakiyeler = [b/m if m > 0 else 0 for b, m in zip(bakiyeler, musteri_sayilari)]
            bars4 = ax4.bar(arac_labels, ortalama_bakiyeler, color=self.color_palette[3], alpha=0.7)
            ax4.set_title('Müşteri Başına Ortalama Bakiye')
            ax4.set_ylabel('Ortalama Bakiye (TL)')
            ax4.set_xlabel('ARAÇ No')
            ax4.tick_params(axis='x', rotation=45)
            ax4.yaxis.set_major_formatter(plt.FuncFormatter(self._format_currency))
            self._add_value_labels(ax4, bars4, ortalama_bakiyeler, format_values=True)
            
            plt.tight_layout()
            
            self.current_figures['comparison'] = fig
            logger.info(f"ARAÇ karşılaştırma grafiği oluşturuldu: {len(arac_labels)} ARAÇ")
            return fig
            
        except Exception as e:
            logger.error(f"Karşılaştırma grafiği oluşturma hatası: {e}")
            return None
    
    def create_workload_distribution_chart(self, assignments: Dict) -> Optional[plt.Figure]:
        """
        İş yükü dağılımı grafiği oluştur
        
        Args:
            assignments: Atama verileri
            
        Returns:
            matplotlib.Figure: Grafik figürü
        """
        try:
            if not assignments:
                logger.error("İş yükü grafiği için atama verisi bulunamadı")
                return None
            
            # İş yükü hesaplama
            workload = {}
            for assignment in assignments.values():
                personnel = assignment.get('sorumlu', 'Atanmamış')
                if personnel not in workload:
                    workload[personnel] = 0
                workload[personnel] += 1
            
            if not workload:
                logger.warning("İş yükü verisi bulunamadı")
                return None
            
            # Veri sıralama
            sorted_workload = sorted(workload.items(), key=lambda x: x[1], reverse=True)
            personnel_names = [item[0] for item in sorted_workload]
            arac_counts = [item[1] for item in sorted_workload]
            
            # Figure oluştur
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            fig.suptitle('İş Yükü Dağılımı', fontsize=16, fontweight='bold')
            
            # Bar chart
            bars = ax1.barh(personnel_names, arac_counts, color=self.color_palette[:len(personnel_names)])
            ax1.set_title('Personel Başına ARAÇ Sayısı')
            ax1.set_xlabel('ARAÇ Sayısı')
            ax1.set_ylabel('Personel')
            
            # Bar üzerine değer yazma
            for bar, value in zip(bars, arac_counts):
                width = bar.get_width()
                ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                        f'{value}', ha='left', va='center')
            
            # Pie chart
            wedges, texts, autotexts = ax2.pie(arac_counts, labels=personnel_names, 
                                              autopct='%1.1f%%', colors=self.color_palette[:len(personnel_names)],
                                              startangle=90)
            ax2.set_title('İş Yükü Oranları')
            
            plt.tight_layout()
            
            self.current_figures['workload'] = fig
            logger.info(f"İş yükü dağılımı grafiği oluşturuldu: {len(personnel_names)} personel")
            return fig
            
        except Exception as e:
            logger.error(f"İş yükü dağılımı grafiği oluşturma hatası: {e}")
            return None
    
    def create_trend_analysis_chart(self, historical_data: List[Dict]) -> Optional[plt.Figure]:
        """
        Trend analizi grafiği oluştur
        
        Args:
            historical_data: Geçmiş analiz verileri
            
        Returns:
            matplotlib.Figure: Grafik figürü
        """
        try:
            if not historical_data or len(historical_data) < 2:
                logger.error("Trend analizi için yeterli geçmiş veri yok")
                return None
            
            # Veri hazırlama
            dates = []
            total_balances = []
            total_customers = []
            
            for data in historical_data:
                try:
                    date_str = data.get('analiz_tarihi', '')
                    if date_str:
                        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        dates.append(date)
                        
                        # Toplam değerleri hesapla
                        analysis_results = data.get('analysis_results', {})
                        total_balance = sum(analysis.get('toplam_bakiye', 0) for analysis in analysis_results.values())
                        total_customer = sum(analysis.get('musteri_sayisi', 0) for analysis in analysis_results.values())
                        
                        total_balances.append(total_balance)
                        total_customers.append(total_customer)
                except Exception as e:
                    logger.debug(f"Trend veri işleme hatası: {e}")
                    continue
            
            if len(dates) < 2:
                logger.warning("Trend analizi için yeterli geçerli veri yok")
                return None
            
            # Figure oluştur
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.figure_size)
            fig.suptitle('Trend Analizi', fontsize=16, fontweight='bold')
            
            # Bakiye trendi
            ax1.plot(dates, total_balances, marker='o', linewidth=2, color=self.color_palette[0])
            ax1.set_title('Toplam Bakiye Trendi')
            ax1.set_ylabel('Toplam Bakiye (TL)')
            ax1.grid(True, alpha=0.3)
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(self._format_currency))
            
            # Müşteri sayısı trendi
            ax2.plot(dates, total_customers, marker='s', linewidth=2, color=self.color_palette[1])
            ax2.set_title('Toplam Müşteri Sayısı Trendi')
            ax2.set_ylabel('Müşteri Sayısı')
            ax2.set_xlabel('Tarih')
            ax2.grid(True, alpha=0.3)
            
            # Tarih formatı
            fig.autofmt_xdate()
            
            plt.tight_layout()
            
            self.current_figures['trend'] = fig
            logger.info(f"Trend analizi grafiği oluşturuldu: {len(dates)} veri noktası")
            return fig
            
        except Exception as e:
            logger.error(f"Trend analizi grafiği oluşturma hatası: {e}")
            return None
    
    def create_performance_heatmap(self, analysis_results: Dict) -> Optional[plt.Figure]:
        """
        Performans heatmap'i oluştur
        
        Args:
            analysis_results: Analiz sonuçları
            
        Returns:
            matplotlib.Figure: Grafik figürü
        """
        try:
            if not analysis_results:
                logger.error("Heatmap için analiz verisi bulunamadı")
                return None
            
            # Veri matrisi hazırlama
            arac_list = list(analysis_results.keys())
            
            # Metrikler
            metrics = ['Müşteri Sayısı', 'Toplam Bakiye', 'Açık Hesap', 'Ortalama Bakiye']
            
            # Veri matrisi
            data_matrix = []
            
            for arac_no in arac_list:
                analysis = analysis_results[arac_no]
                stats = analysis.get('istatistikler', {})
                
                row = [
                    analysis.get('musteri_sayisi', 0),
                    analysis.get('toplam_bakiye', 0),
                    analysis.get('acik_hesap', 0),
                    stats.get('ortalama_bakiye', 0)
                ]
                data_matrix.append(row)
            
            # Normalizasyon (0-1 arasında)
            data_array = np.array(data_matrix)
            normalized_data = np.zeros_like(data_array, dtype=float)
            
            for i in range(data_array.shape[1]):
                col = data_array[:, i]
                col_min, col_max = col.min(), col.max()
                if col_max > col_min:
                    normalized_data[:, i] = (col - col_min) / (col_max - col_min)
                else:
                    normalized_data[:, i] = 0
            
            # Figure oluştur
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Heatmap
            im = ax.imshow(normalized_data, cmap='RdYlBu_r', aspect='auto')
            
            # Eksen etiketleri
            ax.set_xticks(range(len(metrics)))
            ax.set_xticklabels(metrics)
            ax.set_yticks(range(len(arac_list)))
            ax.set_yticklabels([f"ARAÇ {arac}" for arac in arac_list])
            
            # Başlık
            ax.set_title('ARAÇ Performans Heatmap', fontsize=16, fontweight='bold')
            
            # Colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Normalize Edilmiş Değer (0-1)', rotation=270, labelpad=15)
            
            # Değer yazma
            for i in range(len(arac_list)):
                for j in range(len(metrics)):
                    text = ax.text(j, i, f'{normalized_data[i, j]:.2f}',
                                 ha="center", va="center", color="black", fontsize=8)
            
            plt.tight_layout()
            
            self.current_figures['heatmap'] = fig
            logger.info("Performans heatmap'i oluşturuldu")
            return fig
            
        except Exception as e:
            logger.error(f"Performans heatmap oluşturma hatası: {e}")
            return None
    
    def save_chart(self, figure: plt.Figure, file_path: str, dpi: int = 300) -> bool:
        """
        Grafiği dosyaya kaydet
        
        Args:
            figure: Matplotlib figure
            file_path: Kayıt yolu
            dpi: Çözünürlük
            
        Returns:
            Boolean: Başarılı/başarısız
        """
        try:
            if figure is None:
                logger.error("Kaydedilecek grafik yok")
                return False
            
            figure.savefig(file_path, dpi=dpi, bbox_inches='tight', 
                          facecolor='white', edgecolor='none')
            
            logger.info(f"Grafik kaydedildi: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Grafik kaydetme hatası: {e}")
            return False
    
    def save_all_charts(self, directory_path: str, dpi: int = 300) -> int:
        """
        Tüm grafikleri kaydet
        
        Args:
            directory_path: Kayıt dizini
            dpi: Çözünürlük
            
        Returns:
            int: Kaydedilen grafik sayısı
        """
        try:
            from pathlib import Path
            
            directory = Path(directory_path)
            directory.mkdir(exist_ok=True)
            
            saved_count = 0
            
            for chart_name, figure in self.current_figures.items():
                if figure is not None:
                    file_path = directory / f"{chart_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    if self.save_chart(figure, str(file_path), dpi):
                        saved_count += 1
            
            logger.info(f"{saved_count} grafik kaydedildi: {directory_path}")
            return saved_count
            
        except Exception as e:
            logger.error(f"Tüm grafik kaydetme hatası: {e}")
            return 0
    
    def clear_figures(self):
        """Tüm figürleri temizle"""
        try:
            for figure in self.current_figures.values():
                if figure is not None:
                    plt.close(figure)
            
            self.current_figures.clear()
            logger.info("Tüm figürler temizlendi")
            
        except Exception as e:
            logger.error(f"Figür temizleme hatası: {e}")
    
    def get_figure(self, chart_name: str) -> Optional[plt.Figure]:
        """Belirli bir figürü getir"""
        return self.current_figures.get(chart_name)
    
    def _format_currency(self, x, pos):
        """Para birimi formatı"""
        if x >= 1e6:
            return f'{x/1e6:.1f}M'
        elif x >= 1e3:
            return f'{x/1e3:.1f}K'
        else:
            return f'{x:.0f}'
    
    def _add_value_labels(self, ax, bars, values, format_values=False):
        """Bar grafiklerine değer etiketleri ekle"""
        try:
            for bar, value in zip(bars, values):
                height = bar.get_height()
                if format_values:
                    label = format_turkish_number(value)
                else:
                    label = str(value)
                
                ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.01,
                       label, ha='center', va='bottom', fontsize=8)
        except Exception as e:
            logger.debug(f"Değer etiketi ekleme hatası: {e}")
    
    def create_custom_chart(self, data: Dict, chart_type: str, title: str = "Özel Grafik") -> Optional[plt.Figure]:
        """
        Özel grafik oluştur
        
        Args:
            data: Grafik verisi
            chart_type: Grafik türü ('bar', 'pie', 'line', 'scatter')
            title: Grafik başlığı
            
        Returns:
            matplotlib.Figure: Grafik figürü
        """
        try:
            if not data:
                logger.error("Özel grafik için veri yok")
                return None
            
            fig, ax = plt.subplots(figsize=self.figure_size)
            
            if chart_type == 'bar':
                bars = ax.bar(data.keys(), data.values(), color=self.color_palette[:len(data)])
                self._add_value_labels(ax, bars, list(data.values()))
                ax.set_ylabel('Değer')
                
            elif chart_type == 'pie':
                wedges, texts, autotexts = ax.pie(data.values(), labels=data.keys(), 
                                                 autopct='%1.1f%%', colors=self.color_palette[:len(data)])
                
            elif chart_type == 'line':
                ax.plot(list(data.keys()), list(data.values()), marker='o', linewidth=2)
                ax.set_ylabel('Değer')
                ax.grid(True, alpha=0.3)
                
            elif chart_type == 'scatter':
                x_values = range(len(data))
                y_values = list(data.values())
                ax.scatter(x_values, y_values, color=self.color_palette[0], s=100, alpha=0.7)
                ax.set_xticks(x_values)
                ax.set_xticklabels(data.keys())
                ax.set_ylabel('Değer')
                
            else:
                logger.error(f"Desteklenmeyen grafik türü: {chart_type}")
                plt.close(fig)
                return None
            
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel('Kategori')
            
            plt.tight_layout()
            
            chart_key = f"custom_{chart_type}_{datetime.now().strftime('%H%M%S')}"
            self.current_figures[chart_key] = fig
            
            logger.info(f"Özel {chart_type} grafiği oluşturuldu")
            return fig
            
        except Exception as e:
            logger.error(f"Özel grafik oluşturma hatası: {e}")
            return None
