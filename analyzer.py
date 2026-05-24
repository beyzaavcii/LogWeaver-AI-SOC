#analyzer.py
import log_processor

# Fonksiyon 1: Hazır Log Dosyası (Toplu Analiz) İçin Korelasyon 
def find_related_logs(main_alert_index: int, all_logs: list[str], window_size: int) -> list[str]:
    """
    Tüm log listesi içinde, belirtilen indeksteki ana alarm ile ilişkili logları bulur.
    Bu fonksiyon 'batch_analyzer.py' tarafından kullanılır.
    """
    main_alert_data = log_processor.parse_snort_log(all_logs[main_alert_index])
    if not main_alert_data:
        return []

    main_src_ip = main_alert_data.get('src_ip')
    main_dst_ip = main_alert_data.get('dst_ip')
    
    related = []
    start_index = max(0, main_alert_index - window_size)
    end_index = min(len(all_logs), main_alert_index + window_size + 1)
    
    for i in range(start_index, end_index):
        if i == main_alert_index:
            continue
        
        log_line = all_logs[i]
        if main_src_ip in log_line or main_dst_ip in log_line:
            related.append(log_line.strip())
            
    return related

# Fonksiyon 2: Gerçek Zamanlı Analiz İçin Korelasyon 
def find_related_logs_in_buffer(main_alert_log: str, log_buffer: object) -> list[str]:
    """
    Kısa süreli hafızada (deque) tutulan loglar içinde ana alarm ile ilişkili olanları bulur.
    Bu fonksiyon 'realtime_analyzer.py' tarafından kullanılır.
    """
    main_alert_data = log_processor.parse_snort_log(main_alert_log)
    if not main_alert_data:
        return []

    main_src_ip = main_alert_data.get('src_ip')
    main_dst_ip = main_alert_data.get('dst_ip')
    
    related = []
    for log_line in log_buffer:
        if log_line == main_alert_log:
            continue
        
        if main_src_ip in log_line or main_dst_ip in log_line:
            related.append(log_line.strip())
            
    return related

# Fonksiyon 3: Ortak Prompt Oluşturucu 
def build_contextual_prompt(template: str, network_context: str, main_alert: dict, related_logs: list[str]) -> str:
    """
    Verilen şablonu, ana alarmı ve ilişkili logları kullanarak LLM için tam ve bağlam açısından zengin bir prompt oluşturur.
    Bu fonksiyon hem 'batch_analyzer.py' hem de 'realtime_analyzer.py' tarafından kullanılır.
    """
    if related_logs:
        formatted_related_events = "\n".join([f"- {log}" for log in related_logs])
    else:
        formatted_related_events = "İlişkili başka olay bulunamadı."

    prompt = template.format(
        network_context=network_context,
        alert_msg=main_alert.get('alert_msg', 'N/A'),
        classification=main_alert.get('classification', 'N/A'),
        priority=main_alert.get('priority', 'N/A'),
        protocol=main_alert.get('protocol', 'N/A'),
        src_ip=main_alert.get('src_ip', 'N/A'),
        src_port=main_alert.get('src_port', 'N/A'),
        dst_ip=main_alert.get('dst_ip', 'N/A'),
        dst_port=main_alert.get('dst_port', 'N/A'),
        related_events=formatted_related_events
    )
    return prompt
