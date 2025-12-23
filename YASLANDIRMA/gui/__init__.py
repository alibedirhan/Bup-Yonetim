#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel İşleme Uygulaması - GUI Package
Modüler GUI yapısını destekleyen paket
"""

import sys
from pathlib import Path

# Modül dizinini path'e ekle
_current_dir = Path(__file__).parent
_parent_dir = _current_dir.parent
if str(_current_dir) not in sys.path:
    sys.path.insert(0, str(_current_dir))
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

# Frozen mode için import düzeltmeleri
try:
    from .main_gui import ExcelProcessorGUI
    from .file_tab import create_file_processing_tab
    from .analysis_tabs import create_analysis_overview_tab, create_arac_detail_tab  
    from .other_tabs import create_assignment_tab, create_reports_tab, create_charts_tab
    from .ui_helpers import (
        ToolTip,
        add_tooltip,
        ProgressManager,
        ThreadedAnalysis,
        show_help_dialog,
        show_about_dialog,
        show_quick_help,
        show_keyboard_shortcuts
    )
except ImportError:
    try:
        from YASLANDIRMA.gui.main_gui import ExcelProcessorGUI
        from YASLANDIRMA.gui.file_tab import create_file_processing_tab
        from YASLANDIRMA.gui.analysis_tabs import create_analysis_overview_tab, create_arac_detail_tab  
        from YASLANDIRMA.gui.other_tabs import create_assignment_tab, create_reports_tab, create_charts_tab
        from YASLANDIRMA.gui.ui_helpers import (
            ToolTip,
            add_tooltip,
            ProgressManager,
            ThreadedAnalysis,
            show_help_dialog,
            show_about_dialog,
            show_quick_help,
            show_keyboard_shortcuts
        )
    except ImportError:
        from main_gui import ExcelProcessorGUI
        from file_tab import create_file_processing_tab
        from analysis_tabs import create_analysis_overview_tab, create_arac_detail_tab  
        from other_tabs import create_assignment_tab, create_reports_tab, create_charts_tab
        from ui_helpers import (
            ToolTip,
            add_tooltip,
            ProgressManager,
            ThreadedAnalysis,
            show_help_dialog,
            show_about_dialog,
            show_quick_help,
            show_keyboard_shortcuts
        )

# Export edilecek sınıf ve fonksiyonlar
__all__ = [
    # Ana sınıf
    'ExcelProcessorGUI',
    
    # Tab oluşturucular
    'create_file_processing_tab',
    'create_analysis_overview_tab',
    'create_arac_detail_tab',
    'create_assignment_tab',
    'create_reports_tab',
    'create_charts_tab',
    
    # Yardımcı sınıflar
    'ToolTip',
    'add_tooltip',
    'ProgressManager',
    'ThreadedAnalysis',
    
    # Dialog fonksiyonları
    'show_help_dialog',
    'show_about_dialog',
    'show_quick_help',
    'show_keyboard_shortcuts'
]

__version__ = "2.0.0-modular"