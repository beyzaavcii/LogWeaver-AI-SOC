# realtime_analyzer.py
import yaml
import time
from collections import deque
import analyzer, ui, ai_agent, log_processor
import re

def follow(thefile):
    """Bir dosyanın sonuna eklenen satırları canlı olarak okur (tail -f benzeri)."""
    thefile.seek(0, 2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

def run(log_file_path: str, config: dict):
    # Log yolunu config'den değil, parametreden alıyoruz (main.py zaten veriyor)
    LOG_FILE_PATH = log_file_path
    PROMPT_TEMPLATE = config.get("prompt_template", "")
    NETWORK_CONTEXT = config.get("network_context", "")
    CORRELATION_WINDOW = config.get("correlation_window", 100)
    
    # SOAR Handler'ın okuyacağı config dosyası adı (String olarak)
    CONFIG_FILE_NAME = "config_realtime_lab.yaml"

    # ui.print_startup_message'ı doğru parametrelerle çağırıyoruz.
    ui.print_startup_message(LOG_FILE_PATH, mode='snort-realtime')
    log_buffer = deque(maxlen=CORRELATION_WINDOW)

    try:
        with open(LOG_FILE_PATH, 'r') as logfile:
            loglines = follow(logfile)
            for log_line in loglines:
    
                # Eğer satırın içinde düz yazı olarak "Priority: 3" geçiyorsa
                # Hiçbir şey sorma, direkt sonraki satıra geç (continue).
               

                if "Priority: 3" in log_line:
                    continue
                
                log_buffer.append(log_line)
                alert_data = log_processor.parse_snort_log(log_line)
           
                
                
                if alert_data and int(alert_data.get('priority', 99)) <= 2:
                    ui.console.print(f"\n[bold yellow on black]Snort Alarmı Algılandı! Analiz ediliyor...[/bold yellow on black]")
                    
                    related_logs = analyzer.find_related_logs_in_buffer(log_line, log_buffer)
                    prompt = analyzer.build_contextual_prompt(
                        template=PROMPT_TEMPLATE, network_context=NETWORK_CONTEXT,
                        main_alert=alert_data, related_logs=related_logs
                    )

                    soar_context = {
                        "source_ip": alert_data.get('src_ip', 'Bilinmiyor'),
                        "raw_log": log_line.strip(),
                        "log_type": "Snort"  
                    }
                    
                    # ai_agent'a ek parametreleri de gönderiyoruz
                    analysis_result = ai_agent.analyze_alert(prompt, CONFIG_FILE_NAME, soar_context)
                    


                    # --- LOGDAN GERÇEK ÖNCELİĞİ ÇEKME KODU ---
                    # Regex burada log satırındaki [Priority: X] kısmını arar.
                     # (\d+) demek: "Buradaki rakam neyse (1, 2 veya 3) onu yakala" demektir.
                    priority_match = re.search(r"\[Priority:\s*(\d+)\]", log_line)
        
                    if priority_match:
                      # Yakalanan sayıyı (1, 2 ya da 3 fark etmez) alıp değişkene atıyoruz.
                     logdaki_sayi = int(priority_match.group(1))
            
                     # Ve analiz sonucunun içine yazıyoruz.
                     analysis_result["priority"] = logdaki_sayi
                    else:
                     # Eğer logda Priority yazmıyorsa varsayılan 3 olsun.
                     if "priority" not in analysis_result:
                        analysis_result["priority"] = 3

                        

                    ui.display_result(analysis_result, log_line)

                   
                    ui.save_to_dashboard(analysis_result) 
                    
                    
    except KeyboardInterrupt:
        ui.print_completion_message()
    except Exception as e:
        if isinstance(e, PermissionError):
             ui.console.print(f"\n[bold red]HATA: Log dosyasına erişim izni yok.[/bold red]\n[bold cyan]İpucu: Script'i 'sudo' ile ve doğru venv yoluyla çalıştırdığınızdan emin olun.[/bold cyan]")
        else:
            ui.console.print(f"\n[bold red]Beklenmedik bir hata oluştu: {e}[/bold red]")
