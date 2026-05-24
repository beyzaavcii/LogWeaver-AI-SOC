#log_processor.py
import re


def parse_snort_log(log_line: str) -> dict | None:
    """
    Standart bir Snort log satırını ayrıştırır.
    """
    pattern = re.compile(
        r"\[\*\*\] \[\d+:\d+:\d+\] (?P<alert_msg>.+?) \[\*\*\] "
        r"\[Classification: (?P<classification>.+?)\] "
        r"\[Priority: (?P<priority>\d+?)\] "
        r"{(?P<protocol>\w+)} (?P<src_ip>[\d\.]+):(?P<src_port>\d+) -> (?P<dst_ip>[\d\.]+):(?P<dst_port>\d+)"
    )
    match = pattern.search(log_line)
    if match:
        return match.groupdict()
        
 
def parse_web_log(log_line: str) -> dict | None:
    """
    Standart bir web sunucusu access.log satırını ayrıştırır.
    """
    # Örnek: 192.168.145.150 - - [17/Aug/2025:10:30:01 +0300] "GET /index.html HTTP/1.1" 200 1573
    pattern = re.compile(
        r'(?P<ip_address>\S+) \S+ \S+ \[(?P<timestamp>.*?)\] '
        r'"(?P<method>\S+) (?P<uri>\S+) (?P<protocol>.*?)" '
        r'(?P<status_code>\d{3}) (?P<response_size>\S+)'
    )
    match = pattern.search(log_line)
    if match:
        return match.groupdict()

        
       
    return None
