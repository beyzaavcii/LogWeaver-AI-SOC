#batch_analyzer.py
import yaml
from tqdm import tqdm
import analyzer, ui, ai_agent, log_processor
import time
import re

def run(log_file_path: str, config: dict):
    ui.print_startup_message(log_file_path, mode='snort-batch')
    PROMPT_TEMPLATE = config.get("prompt_template", "")
    NETWORK_CONTEXT = config.get("network_context", "")
    CORRELATION_WINDOW = config.get("correlation_window", 10)
    CONFIG_FILE_NAME = "config_batch_test.yaml"
    try:
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            all_log_lines = f.readlines()
    except FileNotFoundError:
        print(f"[HATA] Log dosyası bulunamadı: {log_file_path}")
        return

    alerts_to_process = []
    for index, line in enumerate(all_log_lines):
        alert_data = log_processor.parse_snort_log(line)
        if alert_data and int(alert_data.get('priority', 99)) <= 2:
            alerts_to_process.append((index, line, alert_data))

    ui.print_summary(len(all_log_lines), len(alerts_to_process))
    if not alerts_to_process: return

    for index, line, alert_data in tqdm(alerts_to_process, desc="Alarmlar Analiz Ediliyor", unit=" alarm"):
        # 1. prompt oluşturma
        related_logs = analyzer.find_related_logs(index, all_log_lines, CORRELATION_WINDOW)
        prompt = analyzer.build_contextual_prompt(
            template=PROMPT_TEMPLATE, network_context=NETWORK_CONTEXT,
            main_alert=alert_data, related_logs=related_logs
        )
        # 2. SOAR için ek verileri hazırla 
        # log_processor zaten bize src_ip'yi veriyor
        soar_context = {
            "source_ip": alert_data.get('src_ip', 'Bilinmiyor'),
            "raw_log": line.strip(),
            "log_type": "Snort"  
        }

        # 3. AI Agent'ı Yeni Parametrelerle Çağır
        # Artık prompt'un yanına config dosya yolunu ve IP bilgisini de veriyoruz
        analysis_result = ai_agent.analyze_alert(prompt, CONFIG_FILE_NAME, soar_context)
       

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

        ui.display_result(analysis_result, line)

       
        ui.save_to_dashboard(analysis_result) 
      
        # API'yi boğmamak için her işlemden sonra 1 saniye bekle
        time.sleep(1.0) 
  

    ui.print_completion_message()
