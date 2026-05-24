# web_log_analyzer.py
import yaml
from collections import defaultdict
import ui, ai_agent
from log_processor import parse_web_log
import time
import re

def run(log_file_path: str, config: dict):
    ui.print_startup_message(log_file_path, mode='web-batch')
    PROMPT_TEMPLATE = config.get("prompt_template", "")
    NETWORK_CONTEXT = config.get("network_context", "")

    # SOAR Handler'ın okuyacağı config dosyası adı
    CONFIG_FILE_NAME = "config_web.yaml"
    user_sessions = defaultdict(list)
    try:
        with open(log_file_path, 'r') as f:
            for line in f:
                log_data = parse_web_log(line)
                if log_data:
                    user_sessions[log_data['ip_address']].append(line.strip())
    except FileNotFoundError:
        print(f"[HATA] Log dosyası bulunamadı: {log_file_path}")
        return

    print(f"\nToplam {len(user_sessions)} farklı IP adresi için oturum bulundu. Analiz ediliyor...")
    
    for ip, logs in user_sessions.items():
        ui.console.print(f"\n[bold cyan]IP Adresi: {ip} için oturum analiz ediliyor...[/bold cyan]")
        formatted_session = "\n".join(logs)
        prompt = PROMPT_TEMPLATE.format(
            network_context=NETWORK_CONTEXT,
            session_logs=formatted_session
        )
        
        soar_context = {
            "source_ip": ip,
            # SOAR'a kanıt olarak son log satırını veya tüm session özetini gönderebiliriz
            "raw_log": logs[-1],
            "log_type": "Web"    
            
        }
        
        analysis_result = ai_agent.analyze_alert(prompt ,CONFIG_FILE_NAME, soar_context)
        


        # --- LOGDAN GERÇEK ÖNCELİĞİ ÇEKME KODU ---
        # Regex burada log satırındaki [Priority: X] kısmını arar.
        # (\d+) demek: "Buradaki rakam neyse (1, 2 veya 3) onu yakala" demektir.
        priority_match = re.search(r"\[Priority:\s*(\d+)\]", line)
        
        if priority_match:
            # Yakalanan sayıyı (1, 2 ya da 3 fark etmez) alıp değişkene atıyoruz.
            logdaki_sayi = int(priority_match.group(1))
            
            # Ve analiz sonucunun içine yazıyoruz.
            analysis_result["priority"] = logdaki_sayi
        else:
            # Eğer logda Priority yazmıyorsa varsayılan 3 olsun.
            if "priority" not in analysis_result:
                analysis_result["priority"] = 3

        
        ui.display_result(analysis_result, logs[-1])
        
        ui.save_to_dashboard(analysis_result) 
   
      
        # API'yi boğmamak için her işlemden sonra 1 saniye bekle
        time.sleep(1.0) 
      

    
    ui.print_completion_message()
