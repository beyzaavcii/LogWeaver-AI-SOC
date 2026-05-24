#mock_firewall.py
from flask import Flask, request, jsonify
import time
from datetime import datetime

app = Flask(__name__)

print("\n" + "="*60)
print("  SANAL GÜVENLİK DUVARI (vFirewall) BAŞLATILDI  ")
print("   >> Port: 5001 Dinleniyor...")
print("   >> Beklenen: Shuffle SOAR'dan gelecek engelleme emri.")
print("="*60 + "\n")

@app.route('/api/block_ip', methods=['POST'])
def block_ip():
    data = request.json
    target_ip = data.get('ip', 'Bilinmiyor')
    reason = data.get('reason', 'Belirtilmemiş')

    print(f"⚡ [FIREWALL UYARISI] {datetime.now().strftime('%H:%M:%S')} - Emir Alındı!")
    print(f"  İŞLEM: IP Engelleme (BLOCK)")
    print(f"  HEDEF: {target_ip}")
    print(f"  SEBEP: {reason}")
    
    print("   ⚙️  Kural uygulanıyor...", end='', flush=True)
    time.sleep(1)
    print(" [TAMAM]")
    print(f"   ✅ SONUÇ: {target_ip} trafiği kesildi.\n")

    return jsonify({"status": "blocked", "ip": target_ip}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)