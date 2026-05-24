# 1. Temel İmaj: Python 3.11'in hafif bir sürümünü kullanıyoruz
FROM python:3.11-slim

# 2. Çalışma Dizinini Ayarla: Konteyner içinde /app diye bir klasörde çalışacağız
WORKDIR /app

# 3. Bağımlılıkları Yükle:
# Önce sadece requirements.txt'yi kopyalıyoruz ki Docker "cache" özelliğini kullanabilsin.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Kaynak Kodları Kopyala:
# Mevcut klasördeki (.) her şeyi konteynerin içine (.) kopyala.
# (.dockerignore dosyası sayesinde .venv ve gereksiz loglar kopyalanmayacak)
COPY . .

# 5. Log Klasörü Oluştur (Eğer yoksa garanti olsun)
RUN mkdir -p logs

# 6. Başlangıç Komutu:
# Konteyner başladığında varsayılan olarak ne yapsın?
# Biz bunu docker-compose ile ezeceğiz ama varsayılan bir komut durabilir.
CMD ["python", "main.py", "--help"]