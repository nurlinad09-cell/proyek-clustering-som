# 1. Gunakan image resmi Python sebagai fondasi (versi slim agar ringan)
FROM python:3.10-slim

# 2. Atur folder kerja utama di dalam komputer virtual server
WORKDIR /app

# 3. Salin file daftar library (requirements.txt) ke dalam server
COPY requirements.txt .

# 4. Install semua library yang ada di dalam requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 5. Salin seluruh file kode backend Anda (main.py, dll) ke dalam server
COPY . .

# 6. Jalankan perintah untuk menyalakan FastAPI menggunakan Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]