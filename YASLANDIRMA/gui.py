#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - GUI Modülü (Modülerleştirilmiş)
Modern ve profesyonel kullanıcı arayüzü - Temiz versiyon
"""

# Modüler GUI sınıfını import et
from gui.main_gui import ExcelProcessorGUI

# Geriye uyumluluk için eski imports
import logging
logger = logging.getLogger(__name__)

# Ana sınıfı dışa aktar
__all__ = ['ExcelProcessorGUI']

def run():
    """GUI'yi başlat"""
    try:
        app = ExcelProcessorGUI()
        app.run()
    except Exception as e:
        logger.error(f"GUI başlatma hatası: {e}")
        raise

if __name__ == "__main__":
    run()