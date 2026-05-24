#ai_agent.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import soar_handler 


# .env dosyasındaki değişkenleri yükle
load_dotenv()

# OpenAI istemcisini başlat
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_alert(prompt: str, config_path: str = None, extra_data: dict = None) -> dict:
    """
    Hazırlanan prompt'u GPT-4o API'sine gönderir, yanıtı alır ve SOAR sürecini tetikler.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful cybersecurity analyst assistant designed to output JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},  # GPT-4o'nun JSON modunu kullan
        )
        # 1. LLM Yanıtını Al
        analysis_json = json.loads(response.choices[0].message.content)
        
        # 2. SOAR İçin Gerekli Ek Bilgileri (IP, Ham Log) Yanıta Ekle
        # LLM sadece analiz yapar, IP adresini her zaman JSON içinde vermeyebilir.
        # Biz elimizdeki kesin veriyi buraya ekliyoruz.
        if extra_data:
            analysis_json.update(extra_data)

        # 3. SOAR İşleyicisini Tetikle
        # Sonucu ve config dosyasının yolunu gönderiyoruz
        if config_path:
            soar_handler.send_to_soar(analysis_json, config_path)

        return analysis_json
    
    except Exception as e:
        print(f"[AI Agent] Hata: {e}")
        return {"error": str(e)}
