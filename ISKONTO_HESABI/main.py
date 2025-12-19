# -*- coding: utf-8 -*-
"""
ISKONTO_HESABI - Ana Giriş Noktası
"""

import sys
from pathlib import Path

# Shared modül path'i ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.utils import initialize_app

# Logger başlat
logger = initialize_app("ISKONTO_HESABI")

def main():
    """Ana fonksiyon"""
    try:
        from .ui import main as run_ui
        run_ui()
    except ImportError:
        # Doğrudan çalıştırma durumu
        from ui import main as run_ui
        run_ui()

if __name__ == "__main__":
    main()
