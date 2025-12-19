#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - Veri Yönetim Modülü
JSON veri kaydetme, yükleme ve yönetim sistemi
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import shutil
import os

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, data_directory: str = "data"):
        self.data_dir = Path(data_directory)
        self.data_dir.mkdir(exist_ok=True)
        
        # Dosya yolları
        self.analysis_file = self.data_dir / "analysis_data.json"
        self.assignments_file = self.data_dir / "assignments_data.json"
        self.settings_file = self.data_dir / "settings.json"
        self.backup_dir = self.data_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Cache
        self._cache = {}
        self._cache_timeout = 300  # 5 dakika
        
    def save_analysis_data(self, analysis_results: Dict, metadata: Dict = None) -> bool:
        """
        Analiz verilerini kaydet
        
        Args:
            analysis_results: Analiz sonuçları
            metadata: Ek meta veriler
            
        Returns:
            Boolean: Başarılı/başarısız
        """
        try:
            if not isinstance(analysis_results, dict):
                logger.error("Geçersiz analiz veri formatı")
                return False
            
            # Backup oluştur
            if self.analysis_file.exists():
                self._create_backup(self.analysis_file)
            
            # Kayıt verisi hazırla
            save_data = {
                'version': '1.0',
                'save_date': datetime.now().isoformat(),
                'analysis_results': analysis_results,
                'metadata': metadata or {},
                'data_checksum': self._calculate_checksum(analysis_results)
            }
            
            # JSON'a kaydet
            success = self._save_json(self.analysis_file, save_data)
            
            if success:
                # Cache'i güncelle
                self._update_cache('analysis_data', save_data)
                logger.info(f"Analiz verileri kaydedildi: {len(analysis_results)} ARAÇ")
            
            return success
            
        except Exception as e:
            logger.error(f"Analiz veri kaydetme hatası: {e}")
            return False
    
    def load_analysis_data(self) -> Optional[Dict]:
        """
        Analiz verilerini yükle
        
        Returns:
            Dict: Analiz verileri veya None
        """
        try:
            # Cache'den kontrol et
            cached_data = self._get_from_cache('analysis_data')
            if cached_data:
                return cached_data
            
            if not self.analysis_file.exists():
                logger.info("Analiz veri dosyası bulunamadı")
                return None
            
            # JSON'dan yükle
            data = self._load_json(self.analysis_file)
            if not data:
                return None
            
            # Veri bütünlüğü kontrolü
            if not self._validate_analysis_data(data):
                logger.error("Analiz veri bütünlüğü hatası")
                return None
            
            # Cache'e kaydet
            self._update_cache('analysis_data', data)
            
            logger.info(f"Analiz verileri yüklendi: {len(data.get('analysis_results', {}))} ARAÇ")
            return data
            
        except Exception as e:
            logger.error(f"Analiz veri yükleme hatası: {e}")
            return None
    
    def save_assignments_data(self, assignments: Dict, assignment_history: List = None) -> bool:
        """
        Atama verilerini kaydet
        
        Args:
            assignments: Atama verileri
            assignment_history: Atama geçmişi
            
        Returns:
            Boolean: Başarılı/başarısız
        """
        try:
            if not isinstance(assignments, dict):
                logger.error("Geçersiz atama veri formatı")
                return False
            
            # Backup oluştur
            if self.assignments_file.exists():
                self._create_backup(self.assignments_file)
            
            # Kayıt verisi hazırla
            save_data = {
                'version': '1.0',
                'save_date': datetime.now().isoformat(),
                'assignments': assignments,
                'assignment_history': assignment_history or [],
                'total_assignments': len(assignments),
                'data_checksum': self._calculate_checksum(assignments)
            }
            
            # JSON'a kaydet
            success = self._save_json(self.assignments_file, save_data)
            
            if success:
                # Cache'i güncelle
                self._update_cache('assignments_data', save_data)
                logger.info(f"Atama verileri kaydedildi: {len(assignments)} atama")
            
            return success
            
        except Exception as e:
            logger.error(f"Atama veri kaydetme hatası: {e}")
            return False
    
    def load_assignments_data(self) -> Optional[Dict]:
        """
        Atama verilerini yükle
        
        Returns:
            Dict: Atama verileri veya None
        """
        try:
            # Cache'den kontrol et
            cached_data = self._get_from_cache('assignments_data')
            if cached_data:
                return cached_data
            
            if not self.assignments_file.exists():
                logger.info("Atama veri dosyası bulunamadı")
                return None
            
            # JSON'dan yükle
            data = self._load_json(self.assignments_file)
            if not data:
                return None
            
            # Veri bütünlüğü kontrolü
            if not self._validate_assignments_data(data):
                logger.error("Atama veri bütünlüğü hatası")
                return None
            
            # Cache'e kaydet
            self._update_cache('assignments_data', data)
            
            logger.info(f"Atama verileri yüklendi: {len(data.get('assignments', {}))} atama")
            return data
            
        except Exception as e:
            logger.error(f"Atama veri yükleme hatası: {e}")
            return None
    
    def save_settings(self, settings: Dict) -> bool:
        """
        Ayarları kaydet
        
        Args:
            settings: Ayar verileri
            
        Returns:
            Boolean: Başarılı/başarısız
        """
        try:
            if not isinstance(settings, dict):
                logger.error("Geçersiz ayar veri formatı")
                return False
            
            # Kayıt verisi hazırla
            save_data = {
                'version': '1.0',
                'save_date': datetime.now().isoformat(),
                'settings': settings
            }
            
            # JSON'a kaydet
            success = self._save_json(self.settings_file, save_data)
            
            if success:
                # Cache'i güncelle
                self._update_cache('settings', save_data)
                logger.info("Ayarlar kaydedildi")
            
            return success
            
        except Exception as e:
            logger.error(f"Ayar kaydetme hatası: {e}")
            return False
    
    def load_settings(self) -> Dict:
        """
        Ayarları yükle
        
        Returns:
            Dict: Ayar verileri
        """
        try:
            # Cache'den kontrol et
            cached_data = self._get_from_cache('settings')
            if cached_data:
                return cached_data.get('settings', {})
            
            if not self.settings_file.exists():
                # Varsayılan ayarlar
                default_settings = self._get_default_settings()
                self.save_settings(default_settings)
                return default_settings
            
            # JSON'dan yükle
            data = self._load_json(self.settings_file)
            if not data:
                return self._get_default_settings()
            
            # Cache'e kaydet
            self._update_cache('settings', data)
            
            return data.get('settings', {})
            
        except Exception as e:
            logger.error(f"Ayar yükleme hatası: {e}")
            return self._get_default_settings()
    
    def export_all_data(self, export_path: str) -> bool:
        """
        Tüm verileri export et
        
        Args:
            export_path: Export dosya yolu
            
        Returns:
            Boolean: Başarılı/başarısız
        """
        try:
            export_data = {
                'export_info': {
                    'export_date': datetime.now().isoformat(),
                    'application': 'Excel İşleme Uygulaması',
                    'version': '1.0'
                },
                'analysis_data': self.load_analysis_data(),
                'assignments_data': self.load_assignments_data(),
                'settings': self.load_settings()
            }
            
            # Export dosyasına kaydet
            export_file = Path(export_path)
            success = self._save_json(export_file, export_data)
            
            if success:
                logger.info(f"Tüm veriler export edildi: {export_path}")
            
            return success
            
        except Exception as e:
            logger.error(f"Veri export hatası: {e}")
            return False
    
    def import_all_data(self, import_path: str) -> bool:
        """
        Tüm verileri import et
        
        Args:
            import_path: Import dosya yolu
            
        Returns:
            Boolean: Başarılı/başarısız
        """
        try:
            import_file = Path(import_path)
            
            if not import_file.exists():
                logger.error(f"Import dosyası bulunamadı: {import_path}")
                return False
            
            # JSON'dan yükle
            import_data = self._load_json(import_file)
            if not import_data:
                return False
            
            # Mevcut verileri backup'la
            self._create_full_backup()
            
            success_count = 0
            
            # Analiz verilerini import et
            if 'analysis_data' in import_data and import_data['analysis_data']:
                analysis_data = import_data['analysis_data']
                if 'analysis_results' in analysis_data:
                    if self.save_analysis_data(
                        analysis_data['analysis_results'],
                        analysis_data.get('metadata', {})
                    ):
                        success_count += 1
            
            # Atama verilerini import et
            if 'assignments_data' in import_data and import_data['assignments_data']:
                assignments_data = import_data['assignments_data']
                if 'assignments' in assignments_data:
                    if self.save_assignments_data(
                        assignments_data['assignments'],
                        assignments_data.get('assignment_history', [])
                    ):
                        success_count += 1
            
            # Ayarları import et
            if 'settings' in import_data and import_data['settings']:
                if self.save_settings(import_data['settings']):
                    success_count += 1
            
            logger.info(f"Import tamamlandı: {success_count} veri türü başarılı")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Veri import hatası: {e}")
            return False
    
    def _save_json(self, file_path: Path, data: Any) -> bool:
        """JSON dosyası kaydet"""
        try:
            # Geçici dosyaya yaz
            temp_file = file_path.with_suffix('.tmp')
            
            with temp_file.open('w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            # Atomik dosya değiştirme
            if file_path.exists():
                file_path.unlink()
            temp_file.rename(file_path)
            
            return True
            
        except Exception as e:
            logger.error(f"JSON kaydetme hatası {file_path}: {e}")
            # Geçici dosyayı temizle
            temp_file = file_path.with_suffix('.tmp')
            if temp_file.exists():
                temp_file.unlink()
            return False
    
    def _load_json(self, file_path: Path) -> Optional[Dict]:
        """JSON dosyası yükle"""
        try:
            with file_path.open('r', encoding='utf-8') as f:
                return json.load(f)
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse hatası {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"JSON yükleme hatası {file_path}: {e}")
            return None
    
    def _create_backup(self, file_path: Path):
        """Dosya backup'ı oluştur"""
        try:
            if not file_path.exists():
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_backup_{timestamp}.json"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(file_path, backup_path)
            
            # Eski backup'ları temizle (son 10 tanesini tut)
            self._cleanup_old_backups(file_path.stem)
            
        except Exception as e:
            logger.debug(f"Backup oluşturma hatası: {e}")
    
    def _create_full_backup(self):
        """Tüm verilerin backup'ını oluştur"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            full_backup_dir = self.backup_dir / f"full_backup_{timestamp}"
            full_backup_dir.mkdir(exist_ok=True)
            
            # Tüm veri dosyalarını backup'la
            for file_path in [self.analysis_file, self.assignments_file, self.settings_file]:
                if file_path.exists():
                    shutil.copy2(file_path, full_backup_dir / file_path.name)
            
        except Exception as e:
            logger.debug(f"Full backup oluşturma hatası: {e}")
    
    def _cleanup_old_backups(self, file_stem: str, keep_count: int = 10):
        """Eski backup'ları temizle"""
        try:
            pattern = f"{file_stem}_backup_*.json"
            backup_files = list(self.backup_dir.glob(pattern))
            
            if len(backup_files) > keep_count:
                # Tarihe göre sırala (eski olanlar önce)
                backup_files.sort(key=lambda x: x.stat().st_mtime)
                
                # Fazla olanları sil
                for old_backup in backup_files[:-keep_count]:
                    old_backup.unlink()
                    
        except Exception as e:
            logger.debug(f"Backup temizleme hatası: {e}")
    
    def _calculate_checksum(self, data: Any) -> str:
        """Veri checksum'ı hesapla"""
        try:
            import hashlib
            json_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(json_str.encode()).hexdigest()
        except Exception:
            return ""
    
    def _validate_analysis_data(self, data: Dict) -> bool:
        """Analiz veri bütünlüğünü kontrol et"""
        try:
            required_fields = ['version', 'save_date', 'analysis_results']
            return all(field in data for field in required_fields)
        except Exception:
            return False
    
    def _validate_assignments_data(self, data: Dict) -> bool:
        """Atama veri bütünlüğünü kontrol et"""
        try:
            required_fields = ['version', 'save_date', 'assignments']
            return all(field in data for field in required_fields)
        except Exception:
            return False
    
    def _get_default_settings(self) -> Dict:
        """Varsayılan ayarları getir"""
        return {
            'ui_theme': 'dark',
            'auto_save': True,
            'auto_save_interval': 300,  # 5 dakika
            'backup_enabled': True,
            'max_backup_count': 10,
            'analysis_cache_timeout': 300,
            'default_export_format': 'json',
            'notifications_enabled': True
        }
    
    def _update_cache(self, key: str, data: Any):
        """Cache güncelle"""
        try:
            self._cache[key] = {
                'data': data,
                'timestamp': datetime.now().timestamp()
            }
        except Exception as e:
            logger.debug(f"Cache güncelleme hatası: {e}")
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Cache'den veri al"""
        try:
            if key not in self._cache:
                return None
            
            cache_entry = self._cache[key]
            cache_age = datetime.now().timestamp() - cache_entry['timestamp']
            
            if cache_age > self._cache_timeout:
                # Cache süresi dolmuş
                del self._cache[key]
                return None
            
            return cache_entry['data']
            
        except Exception as e:
            logger.debug(f"Cache okuma hatası: {e}")
            return None
    
    def clear_cache(self):
        """Cache'i temizle"""
        try:
            self._cache.clear()
            logger.info("Cache temizlendi")
        except Exception as e:
            logger.debug(f"Cache temizleme hatası: {e}")
    
    def get_data_info(self) -> Dict:
        """Veri bilgilerini getir"""
        try:
            info = {
                'data_directory': str(self.data_dir),
                'analysis_file_exists': self.analysis_file.exists(),
                'assignments_file_exists': self.assignments_file.exists(),
                'settings_file_exists': self.settings_file.exists(),
                'backup_count': len(list(self.backup_dir.glob('*.json'))),
                'cache_size': len(self._cache)
            }
            
            # Dosya boyutları
            for file_name, file_path in [
                ('analysis_file_size', self.analysis_file),
                ('assignments_file_size', self.assignments_file),
                ('settings_file_size', self.settings_file)
            ]:
                if file_path.exists():
                    info[file_name] = file_path.stat().st_size
                else:
                    info[file_name] = 0
            
            return info
            
        except Exception as e:
            logger.error(f"Veri bilgisi alma hatası: {e}")
            return {}
