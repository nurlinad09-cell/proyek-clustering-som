from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os

app = FastAPI()

# Mengizinkan Frontend (React/Next.js) mengakses API ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Ganti dengan URL Vercel nanti
    allow_methods=["*"],
    allow_headers=["*"],
)


# Konfigurasi Supabase
SUPABASE_URL = "https://sbzqjvavhsglqjvixlq.supabase.co"
SUPABASE_KEY = "sb_publishable_9DZfFMq_K0J3oliBq7EVvQ_woZN5pyF"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
def read_root():
    return {"message": "API Monitoring SOM Aktif"}

# Endpoint untuk mengambil data titik monitoring berdasarkan wilayah
@app.get("/api/points")
def get_points(wilayah: str = None):
    query = supabase.table("monitoring_points").select("*")
    if wilayah:
        query = query.eq("wilayah", wilayah)

    response = query.execute()
    return {"data": response.data}