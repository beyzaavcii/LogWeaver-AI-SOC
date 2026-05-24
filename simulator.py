#simulator.py
import time
import random
import sys

# Log dosyasının doğru yolu
LOG_FILE = "logs/alert_fast"

# RASTGELE IP VE PORT ÜRETİCİLERİ 
def get_random_ip():
    return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"

def get_random_port():
    return random.randint(1024, 65535)


ATTACK_TYPES = [
    {
        "name": "SQL Injection",
        "template": "[**] [1:2001219:18] ET WEB_SERVER SQL Injection Attempt [**] [Classification: Web Application Attack] [Priority: 1] {{TCP}} {src_ip}:{src_port} -> {dst_ip}:80",
        "weight": 0.15
    },
    {
        "name": "SSH Brute Force",
        "template": "[**] [1:2001220:1] ET SCAN Potential SSH Brute Force [**] [Classification: Attempted Information Leak] [Priority: 2] {{TCP}} {src_ip}:{src_port} -> {dst_ip}:22",
        "weight": 0.15
    },
    {
        "name": "XSS (Cross Site Scripting)",
        "template": "[**] [1:2001221:5] ET WEB_SERVER Possible XSS Attempt in URI [**] [Classification: Web Application Attack] [Priority: 2] {{TCP}} {src_ip}:{src_port} -> {dst_ip}:443",
        "weight": 0.10
    },
    {
        "name": "Malware C&C Communication",
        "template": "[**] [1:2018311:2] ET MALWARE Win32/Trojan Downloader Checkin [**] [Classification: A Network Trojan was detected] [Priority: 1] {{TCP}} {dst_ip}:445 -> {src_ip}:{src_port}",
        "weight": 0.05
    },
    {
        "name": "Nmap Port Scan",
        "template": "[**] [1:2000537:8] ET SCAN Nmap Scripting Engine User-Agent Detected [**] [Classification: Attempted Information Leak] [Priority: 3] {{TCP}} {src_ip}:{src_port} -> {dst_ip}:80",
        "weight": 0.10
    },
    {
        "name": "Normal Trafik (Gürültü)",
        "template": "[**] [1:1000001:1] ICMP Ping [**] [Classification: Misc activity] [Priority: 3] {{ICMP}} {src_ip} -> {dst_ip}",
        "weight": 0.45
    }
]

# Sabit Hedef
MY_SERVER_IP = "192.168.1.50"

print("--- SNORT SİMÜLATÖRÜ (TARİHSİZ MOD) BAŞLATILDI ---")
print(f"Hedef Sistem: {LOG_FILE}")

# Dosya yoksa oluştur
try:
    with open(LOG_FILE, "a") as f:
        pass
except FileNotFoundError:
    print(f"HATA: {LOG_FILE} yolu bulunamadı.")
    sys.exit(1)

while True:
    scenario = random.choices(ATTACK_TYPES, weights=[s["weight"] for s in ATTACK_TYPES], k=1)[0]
    
    # Dinamik verileri doldur
    log_message = scenario["template"].format(
        src_ip=get_random_ip(),
        src_port=get_random_port(),
        dst_ip=MY_SERVER_IP
    )
    
    
    # Tarih eklemiyoruz. Sadece log mesajı + yeni satır karakteri.
    full_log_entry = f"{log_message}\n"

    try:
        with open(LOG_FILE, "a") as f:
            f.write(full_log_entry)
            f.flush()
    except Exception as e:
        print(f"Yazma Hatası: {e}")

    # Ekrana basarken bilgi olsun diye (Dosyaya yazılmaz)
    if "Priority: 3" in full_log_entry:
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(1)
    else:
        print(f"\n\n[!!!] KRİTİK LOG DOSYAYA YAZILDI ({scenario['name']})")
        print(f"      Log: {log_message[:80]}...") 
        print("      AI Analizi bekleniyor... (30sn bekleme)")
        time.sleep(30)