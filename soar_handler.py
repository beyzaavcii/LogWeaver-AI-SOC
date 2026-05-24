#soar_handler.py
import requests
import yaml
import urllib3

# Localhost sertifika uyarısını gizle
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_config(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except:
        return None

def send_to_soar(llm_result, config_path):
    config = load_config(config_path)
    if not config or not config.get('soar', {}).get('enabled', False):
        return

    # Sadece True Positive ise gönder
    detection = llm_result.get('tespit', 'Bilinmiyor')
    if "true positive" not in detection.lower():
        return

    # 1. IP Adresini Sağlamlaştır (Snort için source_ip, Web için client_ip, yoksa ip)
    saldirgan_ip = llm_result.get('source_ip') or llm_result.get('client_ip') or llm_result.get('ip') or '0.0.0.0'

    # 2. Payload'ı Oluştur (log_type bilgisini de ekledik)
    payload = {
        "ip": saldirgan_ip,
        "reason": llm_result.get('aciklama', 'AI Tespiti'),
        "log_type": llm_result.get('log_type', 'Bilinmiyor'), 
        "severity": "High",
        "timestamp": llm_result.get('timestamp', 'N/A')
    }

    try:
        print(f"\n [SOAR Handler] Kritik tehdit! Shuffle/n8n'e iletiliyor...")
        requests.post(
            config['soar']['webhook_url'], 
            json=payload, 
            timeout=5, 
            verify=False 
        )
        print(f"   ✅ [SOAR Handler] İletildi.")
    except Exception as e:
        print(f"   ❌ [SOAR Handler] Bağlantı Hatası: {e}")