#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - Sorumlu Atama Modülü
ARAÇ'lara sorumlu atama ve yönetim sistemi
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)

class AssignmentManager:
    def __init__(self):
        self.assignments = {}  # arac_no -> assignment_data
        self.personnel_list = []  # Personel listesi
        self.assignment_history = []  # Atama geçmişi
    
    def load_assignments(self, assignments_data: Dict) -> bool:
        """
        Atama verilerini yükle
        
        Args:
            assignments_data: JSON'dan gelen atama verileri
            
        Returns:
            Boolean: Başarılı/başarısız
        """
        try:
            if not isinstance(assignments_data, dict):
                logger.error("Geçersiz atama veri formatı")
                return False
            
            self.assignments = assignments_data.copy()
            logger.info(f"{len(self.assignments)} atama yüklendi")
            return True
            
        except Exception as e:
            logger.error(f"Atama yükleme hatası: {e}")
            return False
    
    def assign_personnel(self, arac_no: str, personnel_info: Dict) -> bool:
        """
        ARAÇ'a personel ata
        
        Args:
            arac_no: ARAÇ numarası
            personnel_info: Personel bilgileri
            
        Returns:
            Boolean: Başarılı/başarısız
        """
        try:
            # Input validation
            if not arac_no or not isinstance(personnel_info, dict):
                logger.error("Geçersiz atama parametreleri")
                return False
            
            # Personel bilgilerini validate et
            validated_info = self._validate_personnel_info(personnel_info)
            if not validated_info:
                return False
            
            # Mevcut atamayı geçmişe kaydet
            if arac_no in self.assignments:
                self._add_to_history(arac_no, self.assignments[arac_no], 'değiştirildi')
            
            # Yeni atama
            assignment_data = {
                'arac_no': str(arac_no),
                'sorumlu': validated_info['sorumlu'],
                'email': validated_info.get('email', ''),
                'telefon': validated_info.get('telefon', ''),
                'departman': validated_info.get('departman', ''),
                'atama_tarihi': datetime.now().isoformat(),
                'notlar': validated_info.get('notlar', ''),
                'durum': 'aktif',
                'son_guncelleme': datetime.now().isoformat()
            }
            
            self.assignments[str(arac_no)] = assignment_data
            
            # Geçmişe kaydet
            self._add_to_history(arac_no, assignment_data, 'atandı')
            
            # Personel listesini güncelle
            self._update_personnel_list(validated_info['sorumlu'])
            
            logger.info(f"ARAÇ {arac_no} -> {validated_info['sorumlu']} atandı")
            return True
            
        except Exception as e:
            logger.error(f"Personel atama hatası: {e}")
            return False
    
    def remove_assignment(self, arac_no: str, reason: str = '') -> bool:
        """
        ARAÇ atamasını kaldır
        
        Args:
            arac_no: ARAÇ numarası
            reason: Kaldırma nedeni
            
        Returns:
            Boolean: Başarılı/başarısız
        """
        try:
            arac_str = str(arac_no)
            
            if arac_str not in self.assignments:
                logger.warning(f"ARAÇ {arac_no} için atama bulunamadı")
                return False
            
            # Geçmişe kaydet
            removed_assignment = self.assignments[arac_str].copy()
            removed_assignment['kaldirilma_nedeni'] = reason
            removed_assignment['kaldirilma_tarihi'] = datetime.now().isoformat()
            
            self._add_to_history(arac_no, removed_assignment, 'kaldırıldı')
            
            # Atamayı sil
            del self.assignments[arac_str]
            
            logger.info(f"ARAÇ {arac_no} ataması kaldırıldı: {reason}")
            return True
            
        except Exception as e:
            logger.error(f"Atama kaldırma hatası: {e}")
            return False
    
    def update_assignment(self, arac_no: str, update_data: Dict) -> bool:
        """
        Mevcut atamayı güncelle
        
        Args:
            arac_no: ARAÇ numarası
            update_data: Güncellenecek veriler
            
        Returns:
            Boolean: Başarılı/başarısız
        """
        try:
            arac_str = str(arac_no)
            
            if arac_str not in self.assignments:
                logger.error(f"ARAÇ {arac_no} için atama bulunamadı")
                return False
            
            # Mevcut veriyi backup'la
            old_assignment = self.assignments[arac_str].copy()
            
            # Güncelleme verilerini validate et
            current_assignment = self.assignments[arac_str]
            
            # Güvenli güncelleme
            updateable_fields = ['sorumlu', 'email', 'telefon', 'departman', 'notlar', 'durum']
            
            for field, value in update_data.items():
                if field in updateable_fields:
                    if field == 'sorumlu' and value:
                        # Sorumlu değişiyorsa validate et
                        if not self._validate_name(value):
                            logger.error(f"Geçersiz sorumlu adı: {value}")
                            continue
                        self._update_personnel_list(value)
                    elif field == 'email' and value:
                        if not self._validate_email(value):
                            logger.error(f"Geçersiz email: {value}")
                            continue
                    elif field == 'telefon' and value:
                        if not self._validate_phone(value):
                            logger.error(f"Geçersiz telefon: {value}")
                            continue
                    
                    current_assignment[field] = str(value).strip()
            
            # Son güncelleme tarihini ayarla
            current_assignment['son_guncelleme'] = datetime.now().isoformat()
            
            # Geçmişe kaydet
            self._add_to_history(arac_no, old_assignment, 'güncellendi')
            
            logger.info(f"ARAÇ {arac_no} ataması güncellendi")
            return True
            
        except Exception as e:
            logger.error(f"Atama güncelleme hatası: {e}")
            return False
    
    def get_assignment(self, arac_no: str) -> Optional[Dict]:
        """
        ARAÇ atamasını getir
        
        Args:
            arac_no: ARAÇ numarası
            
        Returns:
            Dict: Atama bilgileri veya None
        """
        try:
            arac_str = str(arac_no)
            
            if arac_str in self.assignments:
                return self.assignments[arac_str].copy()
            else:
                return None
                
        except Exception as e:
            logger.error(f"Atama getirme hatası: {e}")
            return None
    
    def get_all_assignments(self) -> Dict:
        """Tüm atamaları getir"""
        try:
            return self.assignments.copy()
        except Exception as e:
            logger.error(f"Tüm atama getirme hatası: {e}")
            return {}
    
    def get_assignments_by_personnel(self, personnel_name: str) -> List[Dict]:
        """
        Belirli personelin atamalarını getir
        
        Args:
            personnel_name: Personel adı
            
        Returns:
            List[Dict]: Atama listesi
        """
        try:
            personnel_assignments = []
            
            for assignment in self.assignments.values():
                if assignment.get('sorumlu', '').lower() == personnel_name.lower():
                    personnel_assignments.append(assignment.copy())
            
            return personnel_assignments
            
        except Exception as e:
            logger.error(f"Personel atama getirme hatası: {e}")
            return []
    
    def get_personnel_list(self) -> List[str]:
        """Personel listesini getir"""
        try:
            return self.personnel_list.copy()
        except Exception as e:
            logger.error(f"Personel listesi getirme hatası: {e}")
            return []
    
    def get_assignment_history(self, arac_no: str = None) -> List[Dict]:
        """
        Atama geçmişini getir
        
        Args:
            arac_no: ARAÇ numarası (opsiyonel, tümü için None)
            
        Returns:
            List[Dict]: Geçmiş kayıtları
        """
        try:
            if arac_no is None:
                return self.assignment_history.copy()
            else:
                arac_str = str(arac_no)
                arac_history = [
                    record for record in self.assignment_history
                    if record.get('arac_no') == arac_str
                ]
                return arac_history
                
        except Exception as e:
            logger.error(f"Atama geçmişi getirme hatası: {e}")
            return []
    
    def get_workload_distribution(self) -> Dict:
        """
        İş yükü dağılımını hesapla
        
        Returns:
            Dict: Personel bazlı iş yükü
        """
        try:
            workload = {}
            
            for assignment in self.assignments.values():
                personnel = assignment.get('sorumlu', 'Atanmamış')
                
                if personnel not in workload:
                    workload[personnel] = {
                        'arac_sayisi': 0,
                        'arac_listesi': [],
                        'aktif_atamalar': 0,
                        'pasif_atamalar': 0
                    }
                
                workload[personnel]['arac_sayisi'] += 1
                workload[personnel]['arac_listesi'].append(assignment['arac_no'])
                
                if assignment.get('durum', 'aktif') == 'aktif':
                    workload[personnel]['aktif_atamalar'] += 1
                else:
                    workload[personnel]['pasif_atamalar'] += 1
            
            return workload
            
        except Exception as e:
            logger.error(f"İş yükü hesaplama hatası: {e}")
            return {}
    
    def _validate_personnel_info(self, personnel_info: Dict) -> Optional[Dict]:
        """Personel bilgilerini validate et"""
        try:
            # Zorunlu alanlar
            if 'sorumlu' not in personnel_info or not personnel_info['sorumlu']:
                logger.error("Sorumlu adı zorunlu")
                return None
            
            validated = {
                'sorumlu': str(personnel_info['sorumlu']).strip()
            }
            
            # Ad validation
            if not self._validate_name(validated['sorumlu']):
                logger.error(f"Geçersiz sorumlu adı: {validated['sorumlu']}")
                return None
            
            # Opsiyonel alanlar
            if 'email' in personnel_info and personnel_info['email']:
                email = str(personnel_info['email']).strip()
                if self._validate_email(email):
                    validated['email'] = email
                else:
                    logger.warning(f"Geçersiz email formatı: {email}")
            
            if 'telefon' in personnel_info and personnel_info['telefon']:
                phone = str(personnel_info['telefon']).strip()
                if self._validate_phone(phone):
                    validated['telefon'] = phone
                else:
                    logger.warning(f"Geçersiz telefon formatı: {phone}")
            
            # Diğer opsiyonel alanlar
            for field in ['departman', 'notlar']:
                if field in personnel_info and personnel_info[field]:
                    validated[field] = str(personnel_info[field]).strip()
            
            return validated
            
        except Exception as e:
            logger.error(f"Personel bilgi validation hatası: {e}")
            return None
    
    def _validate_name(self, name: str) -> bool:
        """Ad validasyonu"""
        try:
            if not name or len(name.strip()) < 2:
                return False
            
            # Sadece harf, boşluk ve Türkçe karakterler
            name_pattern = r'^[a-zA-ZçğıöşüÇĞIİÖŞÜ\s]+$'
            return bool(re.match(name_pattern, name.strip()))
            
        except Exception:
            return False
    
    def _validate_email(self, email: str) -> bool:
        """Email validasyonu"""
        try:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(email_pattern, email.strip()))
        except Exception:
            return False
    
    def _validate_phone(self, phone: str) -> bool:
        """Telefon validasyonu"""
        try:
            # Türkiye telefon formatları
            phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
            
            patterns = [
                r'^0[5][0-9]{9}$',  # 0555 123 45 67
                r'^90[5][0-9]{9}$',  # 90555 123 45 67
                r'^[5][0-9]{9}$',   # 555 123 45 67
                r'^0[2-4][0-9]{8}$'  # Sabit hat
            ]
            
            return any(re.match(pattern, phone_clean) for pattern in patterns)
            
        except Exception:
            return False
    
    def _update_personnel_list(self, personnel_name: str):
        """Personel listesini güncelle"""
        try:
            if personnel_name and personnel_name not in self.personnel_list:
                self.personnel_list.append(personnel_name)
                self.personnel_list.sort()
        except Exception as e:
            logger.debug(f"Personel listesi güncelleme hatası: {e}")
    
    def _add_to_history(self, arac_no: str, assignment_data: Dict, action: str):
        """Geçmişe kayıt ekle"""
        try:
            history_record = {
                'arac_no': str(arac_no),
                'action': action,
                'timestamp': datetime.now().isoformat(),
                'assignment_data': assignment_data.copy()
            }
            
            self.assignment_history.append(history_record)
            
            # Geçmişi sınırla (son 1000 kayıt)
            if len(self.assignment_history) > 1000:
                self.assignment_history = self.assignment_history[-1000:]
                
        except Exception as e:
            logger.debug(f"Geçmiş kayıt ekleme hatası: {e}")
    
    def get_statistics(self) -> Dict:
        """Atama istatistikleri"""
        try:
            total_assignments = len(self.assignments)
            active_assignments = len([
                a for a in self.assignments.values() 
                if a.get('durum', 'aktif') == 'aktif'
            ])
            
            workload = self.get_workload_distribution()
            personnel_count = len(workload)
            
            # En çok atanan personel
            max_workload_personnel = None
            max_workload_count = 0
            
            for personnel, data in workload.items():
                if data['arac_sayisi'] > max_workload_count:
                    max_workload_count = data['arac_sayisi']
                    max_workload_personnel = personnel
            
            stats = {
                'toplam_atama': total_assignments,
                'aktif_atama': active_assignments,
                'pasif_atama': total_assignments - active_assignments,
                'personel_sayisi': personnel_count,
                'ortalama_arac_per_personel': total_assignments / personnel_count if personnel_count > 0 else 0,
                'en_cok_atanan_personel': max_workload_personnel,
                'en_yuksek_is_yuku': max_workload_count,
                'gecmis_kayit_sayisi': len(self.assignment_history)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Atama istatistik hatası: {e}")
            return {}
    
    def search_assignments(self, search_term: str) -> List[Dict]:
        """
        Atamalarda arama yap
        
        Args:
            search_term: Arama terimi
            
        Returns:
            List[Dict]: Bulunan atamalar
        """
        try:
            if not search_term:
                return []
            
            search_term_lower = search_term.lower()
            results = []
            
            for assignment in self.assignments.values():
                # Arama alanları
                search_fields = [
                    assignment.get('arac_no', ''),
                    assignment.get('sorumlu', ''),
                    assignment.get('email', ''),
                    assignment.get('telefon', ''),
                    assignment.get('departman', ''),
                    assignment.get('notlar', '')
                ]
                
                # Herhangi bir alanda eşleşme var mı?
                if any(search_term_lower in str(field).lower() for field in search_fields):
                    results.append(assignment.copy())
            
            return results
            
        except Exception as e:
            logger.error(f"Atama arama hatası: {e}")
            return []
    
    def export_assignments(self) -> Dict:
        """
        Atamaları export için hazırla
        
        Returns:
            Dict: Export verisi
        """
        try:
            export_data = {
                'export_date': datetime.now().isoformat(),
                'total_assignments': len(self.assignments),
                'assignments': self.assignments.copy(),
                'personnel_list': self.personnel_list.copy(),
                'statistics': self.get_statistics()
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Atama export hatası: {e}")
            return {}
    
    def import_assignments(self, import_data: Dict) -> bool:
        """
        Atamaları import et
        
        Args:
            import_data: Import verisi
            
        Returns:
            Boolean: Başarılı/başarısız
        """
        try:
            if not isinstance(import_data, dict):
                logger.error("Geçersiz import veri formatı")
                return False
            
            # Mevcut veriyi backup'la
            backup_assignments = self.assignments.copy()
            backup_personnel = self.personnel_list.copy()
            
            try:
                # Import verisini yükle
                if 'assignments' in import_data:
                    self.assignments = import_data['assignments'].copy()
                
                if 'personnel_list' in import_data:
                    self.personnel_list = import_data['personnel_list'].copy()
                
                logger.info(f"Import başarılı: {len(self.assignments)} atama yüklendi")
                return True
                
            except Exception as import_error:
                # Hata durumunda geri yükle
                self.assignments = backup_assignments
                self.personnel_list = backup_personnel
                raise import_error
                
        except Exception as e:
            logger.error(f"Atama import hatası: {e}")
            return False