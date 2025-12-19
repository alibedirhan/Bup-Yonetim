import os
import sys
import time

print("=" * 50)
print(f"🚀 Starting {os.path.basename(os.path.dirname(__file__))}")
print("=" * 50)

# FROZEN DURUMU İÇİN KRİTİK AYAR
if getattr(sys, 'frozen', False):
    print("❄️ Frozen mode detected")
    
    # 1. MEIPASS yolunu al
    base_path = sys._MEIPASS
    print(f"📦 MEIPASS: {base_path}")
    
    # 2. Programın kendi yolunu bul
    current_dir_name = os.path.basename(os.path.dirname(__file__))
    source_program_path = os.path.join(base_path, current_dir_name)
    
    # 3. Hedef yol (ana EXE ile aynı dizin)
    target_base_path = os.path.dirname(sys.executable)
    target_program_path = os.path.join(target_base_path, current_dir_name)
    
    print(f"🎯 Source: {source_program_path}")
    print(f"🎯 Target: {target_program_path}")
    
    # 4. Eğer hedefte yoksa KOPYALA
    if not os.path.exists(target_program_path):
        print("📋 Copying program files...")
        import shutil
        
        try:
            shutil.copytree(source_program_path, target_program_path)
            print("✅ Copy successful")
        except Exception as e:
            print(f"❌ Copy failed: {e}")
    
    # 5. Çalışma dizinini AYNI SEVİYEDE olacak şekilde ayarla
    os.chdir(target_program_path)
    
else:
    # Normal mod
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

print(f"📂 Working directory: {os.getcwd()}")
print(f"📄 Files here: {os.listdir('.')}")
print("=" * 50)
time.sleep(1)  # Debug için bekle

# GERİ KALAN KODLARINIZ BURADAN SONRA GELMELİ

# Windows/Tk: 'bad screen distance "200.0"' benzeri hataları engelle
import os as _os, sys as _sys

def _ensure_project_root():
    cur = _os.path.abspath(_os.path.dirname(__file__))
    for _ in range(6):
        if _os.path.isdir(_os.path.join(cur, "shared")):
            if cur not in _sys.path:
                _sys.path.insert(0, cur)
            return
        parent = _os.path.dirname(cur)
        if parent == cur:
            return
        cur = parent

try:
    _ensure_project_root()
    from shared.utils import apply_tk_float_fix as _apply_tk_float_fix, setup_turkish_locale as _setup_turkish_locale
    _apply_tk_float_fix()
    _setup_turkish_locale()
except Exception:
    pass

import customtkinter as ctk

# CustomTkinter DPI/scaling bazen float üretebiliyor -> sabitle
try:
    ctk.set_widget_scaling(1.0)
    ctk.set_window_scaling(1.0)
except Exception:
    pass

import sys
import os

class Program:
    def __init__(self, title):
        self.root = ctk.CTk()
        self.root.title(title)
        self.root.geometry("600x400")
        
        # Ana frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Başlık
        title_label = ctk.CTkLabel(main_frame, text=title, 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        # İçerik
        info_label = ctk.CTkLabel(main_frame, 
                                 text="Bu modül henüz geliştirilme aşamasındadır.",
                                 font=ctk.CTkFont(size=14))
        info_label.pack(pady=10)
        
        # Kapat butonu
        close_btn = ctk.CTkButton(main_frame, text="Kapat", 
                                 command=self.root.quit,
                                 width=200, height=40)
        close_btn.pack(pady=30)
    
    def run(self):
        self.root.mainloop()

def main():
    from YASLANDIRMA.gui.main_gui import ExcelProcessorGUI
    app = ExcelProcessorGUI()
    app.run()

def run_program():
    main()

if __name__ == "__main__":
    main()
