# -*- coding: utf-8 -*-
"""
BUP-ALL-IN-ONE Shared Modülü
Tüm alt programlarda kullanılan ortak bileşenler
"""

from .theme import (
    COLORS,
    MODULE_COLORS,
    FONTS,
    SIZES,
    BupTheme,
    darken_color,
    lighten_color,
    create_gradient_colors,
    get_entry_style,
    get_frame_style,
    get_label_style
)

from .utils import (
    is_frozen,
    get_base_path,
    get_app_dir,
    get_data_dir,
    get_logs_dir,
    get_exports_dir,
    get_resource_path,
    setup_logging,
    setup_turkish_locale,
    safe_turkish_text,
    apply_tk_float_fix,
    get_clean_filename,
    format_file_size,
    format_number,
    format_currency,
    get_timestamp,
    get_date_display,
    get_date_short,
    check_dependencies,
    get_system_info,
    initialize_app
)

from .components import (
    ModernHeader,
    ModernCard,
    ModernButton,
    FileSelector,
    ProgressIndicator,
    StatCard,
    ScrollableFrame,
    ModernTabView,
    ToolTip,
    add_tooltip,
    show_success,
    show_error,
    show_warning,
    ask_yes_no,
    ask_ok_cancel
)

__all__ = [
    # Theme
    'COLORS', 'MODULE_COLORS', 'FONTS', 'SIZES', 'BupTheme',
    'darken_color', 'lighten_color', 'create_gradient_colors',
    'get_entry_style', 'get_frame_style', 'get_label_style',
    
    # Utils
    'is_frozen', 'get_base_path', 'get_app_dir', 'get_data_dir',
    'get_logs_dir', 'get_exports_dir', 'get_resource_path',
    'setup_logging', 'setup_turkish_locale', 'safe_turkish_text',
    'apply_tk_float_fix', 'get_clean_filename', 'format_file_size',
    'format_number', 'format_currency', 'get_timestamp',
    'get_date_display', 'get_date_short', 'check_dependencies',
    'get_system_info', 'initialize_app',
    
    # Components
    'ModernHeader', 'ModernCard', 'ModernButton', 'FileSelector',
    'ProgressIndicator', 'StatCard', 'ScrollableFrame', 'ModernTabView',
    'ToolTip', 'add_tooltip', 'show_success', 'show_error',
    'show_warning', 'ask_yes_no', 'ask_ok_cancel'
]
