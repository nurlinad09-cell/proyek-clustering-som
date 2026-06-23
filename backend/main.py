import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import pandas as pd
import numpy as np
from minisom import MiniSom
from geopy.distance import great_circle

app = FastAPI(
    title="API Clustering SOM - Wilayah Sulawesi Tengah",
    description="API untuk merekomendasikan seluruh titik monitoring berdasarkan algoritma Self-Organizing Maps (SOM) dan Non-Maximum Suppression (NMS) tanpa batasan jumlah",
    version="1.0.0"
)

# Mengizinkan CORS agar frontend bisa mengakses API ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Inisialisasi Supabase Client dari Environment Variables Vercel
SUPABASE_URL = os.getenv("https://sbzqjvavhsglqjvixlq.supabase.co")
SUPABASE_KEY = os.getenv("sb_publishable_9DZfFMq_K0J3oliBq7EVvQ_woZN5pyF")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Environment Variables SUPABASE_URL dan SUPABASE_KEY belum diatur!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Nama tabel Supabase Anda
NAMA_TABEL = "dataset_sims_sulteng" 

@app.get("/")
def root():
    return {"status": "running", "message": "API Clustering SOM Sulteng Siap Digunakan!"}

@app.get("/api/cluster")
def get_som_clusters(city: str = Query(..., description="Nama kota/kabupaten di Sulteng, contoh: 'KOTA PALU'")):
    try:
        # 2. Ambil data dari Supabase (Filter: Bukan Fixed Service dan Sesuai Kota yang dipilih)
        response = supabase.table(NAMA_TABEL)\
            .select("CLNT_NAME, SERVICE, FREQ, STN_NAME, SID_LONG, SID_LAT, CITY")\
            .neq("SERVICE", "Fixed Service")\
            .eq("CITY", city.upper())\
            .execute()
            
        data_rows = response.data
        
        if not data_rows or len(data_rows) == 0:
            raise HTTPException(status_code=404, detail=f"Tidak ada data stasiun ditemukan untuk wilayah {city}")
            
        # 3. Konversi hasil query Supabase menjadi Pandas DataFrame
        df_filter = pd.DataFrame(data_rows)
        df_filter = df_filter.dropna(subset=['SID_LAT', 'SID_LONG'])
        
        if len(df_filter) == 0:
            return {"city": city, "total_stations": 0, "recommendations": []}

        coords = df_filter[['SID_LAT', 'SID_LONG']].values
        
        # 4. Inisialisasi & Training Algoritma SOM (Self-Organizing Maps)
        som_size = 5
        som = MiniSom(x=som_size, y=som_size, input_len=2, sigma=1.0, learning_rate=0.5, random_seed=42)
        som.pca_weights_init(coords)
        som.train(coords, num_iteration=500, verbose=False)
        
        centroids = som.get_weights().reshape(-1, 2)
        
        # 5. Hitung Cakupan Stasiun dalam Radius 5 km untuk Setiap Centroid
        recommendation_pool = []
        
        for idx, centroid in enumerate(centroids):
            centroid_lat, centroid_long = centroid[0], centroid[1]
            
            if np.isnan(centroid_lat) or np.isnan(centroid_long):
                continue
                
            covered_stations = []
            
            # Hitung jarak geografis ke setiap stasiun asli
            for _, row in df_filter.iterrows():
                try:
                    dist = great_circle((centroid_lat, centroid_long), (row['SID_LAT'], row['SID_LONG'])).km
                    if dist <= 5.0: # Radius Cakupan 5 Kilometer
                        covered_stations.append({
                            "client_name": row['CLNT_NAME'],
                            "service": row['SERVICE'],
                            "station_name": row['STN_NAME'],
                            "distance_km": round(dist, 2)
                        })
                except Exception:
                    continue
            
            recommendation_pool.append({
                "id_centroid": idx,
                "latitude": float(centroid_lat),
                "longitude": float(centroid_long),
                "coverage_count": len(covered_stations),
                "stations_inside": covered_stations
            })
            
        # 6. Sorting & Jalankan Algoritma NMS (Non-Maximum Suppression)
        # Urutkan berdasarkan titik dengan cakupan stasiun terbanyak
        recommendation_pool.sort(key=lambda x: x['coverage_count'], reverse=True)
        
        final_recommendations = []
        
        for item in recommendation_pool:
            if item['coverage_count'] == 0:
                continue # Abaikan titik kosong
                
            # Cek tumpang tindih (< 5km) dengan titik yang sudah dipilih
            overlap = False
            for selected in final_recommendations:
                dist_between_centroids = great_circle(
                    (item['latitude'], item['longitude']), 
                    (selected['latitude'], selected['longitude'])
                ).km
                if dist_between_centroids < 5.0:
                    overlap = True
                    break
            
            # Jika lolos seleksi NMS, simpan ke rekomendasi final
            if not overlap:
                final_recommendations.append(item)
                
            # --- BAGIAN BATASAN 15 TITIK TELAH DIHAPUS DI SINI ---
                
        # 7. Kembalikan Response Semua Titik dalam Format JSON
        return {
            "status": "success",
            "city": city.upper(),
            "total_available_stations": len(df_filter),
            "total_recommendation_points": len(final_recommendations),
            "recommendations": final_recommendations
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal: {str(e)}")