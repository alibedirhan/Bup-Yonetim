#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - Modules Package
Analiz modüllerini içeren paket
"""

# Modül versiyonu
__version__ = "1.0.0"

# Ana modülleri import et
try:
    from .analysis import AnalysisEngine
    from .assignment import AssignmentManager
    from .data_manager import DataManager
    from .reports import ReportGenerator
    from .visualization import VisualizationEngine
    from .analysis_gui import AnalysisGUI, create_analysis_gui
    
    # Import edilebilen modüller
    __all__ = [
        'AnalysisEngine',
        'AssignmentManager', 
        'DataManager',
        'ReportGenerator',
        'VisualizationEngine',
        'AnalysisGUI',
        'create_analysis_gui'
    ]
    
    # Modül durumu
    MODULES_LOADED = True
    
except ImportError as e:
    print(f"Analiz modülleri yüklenirken hata: {e}")
    MODULES_LOADED = False
    __all__ = []
