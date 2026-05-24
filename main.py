#main.py
import argparse
import os
import sys
import yaml
from dotenv import load_dotenv
from rich.console import Console

# Modülleri içe aktar
import batch_analyzer
import realtime_analyzer
import web_log_analyzer

import os

def initialize_dashboard_file(current_mode):
    """
    Dashboard dosyasını yönetir:
    - Eğer önceki çalıştırma modu ile şimdiki aynıysa: Dosyayı KORU (Append).
    - Eğer mod değiştiyse: Dosyayı SİL (Wipe/Reset).
    """
    data_file = "dashboard_data.json"
    state_file = ".last_run_mode" # Son çalıştırılan modu burada saklayacağız (Gizli dosya)

    last_mode = ""
    
    # 1. Son çalışma modunu öğren
    if os.path.exists(state_file):
        with open(state_file, "r") as f:
            last_mode = f.read().strip()

    # 2. Karşılaştır ve Karar Ver
    if current_mode != last_mode:
        print(f">>> [INFO] Mod değişikliği algılandı ({last_mode} -> {current_mode}). Dashboard temizleniyor...")
        # Dosyayı sıfırla ("w" modu)
        with open(data_file, "w", encoding="utf-8") as f:
            pass 
    else:
        print(f">>> [INFO] Aynı mod ({current_mode}) algılandı. Dashboard verileri korunuyor...")

    # 3. Yeni modu hafızaya kaydet
    with open(state_file, "w") as f:
        f.write(current_mode)

# Konsol çıktısı için
console = Console()

# .env dosyasından API anahtarlarını yükle
load_dotenv()

def load_config(config_path):
    """YAML yapılandırma dosyasını yükler."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        console.print(f"[bold red]Hata:[/bold red] Config dosyası bulunamadı: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        console.print(f"[bold red]Hata:[/bold red] YAML okuma hatası: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="LogWeaver AI - Güvenlik Log Analiz Sistemi")
    
    # Argümanlar: Mod ve Log Dosyası
    parser.add_argument("mode", choices=["snort-batch", "snort-realtime", "web-batch"], help="Çalışma modu")
    parser.add_argument("log_file", help="Analiz edilecek log dosyasının yolu (örn: logs/test_alerts.log)")
    
    args = parser.parse_args()
    
    initialize_dashboard_file(args.mode)
    

    # API Anahtarı Kontrolü
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]HATA:[/bold red] OPENAI_API_KEY bulunamadı! Lütfen .env dosyasını kontrol edin.")
        sys.exit(1)

    
    # Artık sadece modüllerin (batch_analyzer vb.) kendi UI çıktıları görünecek.

    # Moda göre doğru analizciyi ve config dosyasını seç
    if args.mode == "snort-batch":
        config = load_config("config_batch_test.yaml")
        config['snort_log_path'] = args.log_file
        batch_analyzer.run(args.log_file, config)

    elif args.mode == "snort-realtime":
        config = load_config("config_realtime_lab.yaml")
        config['log_file_path'] = args.log_file
        realtime_analyzer.run(args.log_file, config)

    elif args.mode == "web-batch":
        config = load_config("config_web.yaml")
        config['log_file_path'] = args.log_file
        web_log_analyzer.run(args.log_file, config)
    
    else:
        console.print("[bold red]Geçersiz mod seçimi![/bold red]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Program kullanıcı tarafından durduruldu.[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Beklenmeyen bir hata oluştu:[/bold red] {e}")
        # Hata ayıklamak istersen aşağıdaki satırları açabiliriz:
        # import traceback
        # traceback.print_exc()