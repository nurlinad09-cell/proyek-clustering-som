import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import axios from 'axios';

// Peta dirender secara dinamis agar tidak error di server-side (Next.js)
const Map = dynamic(
  () => import('../components/MapComponent'), 
  { ssr: false }
);

export default function Dashboard() {
  const [wilayah, setWilayah] = useState('Semua');
  const [points, setPoints] = useState([]);

  // Mengambil data dari Backend FastAPI
  useEffect(() => {
    const fetchData = async () => {
      const url = wilayah === 'Semua' 
        ? 'http://localhost:8000/api/points' 
        : `http://localhost:8000/api/points?wilayah=${wilayah}`;
      const res = await axios.get(url);
      setPoints(res.data.data);
    };
    fetchData();
  }, [wilayah]);

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar Kiri */}
      <div className="w-1/4 bg-white p-6 shadow-lg z-10">
        <h1 className="text-2xl font-bold mb-6 text-blue-800">Monitoring Cluster</h1>
        <label className="block text-gray-700 font-semibold mb-2">Pilih Wilayah:</label>
        <select 
          className="w-full p-2 border rounded"
          value={wilayah} 
          onChange={(e) => setWilayah(e.target.value)}
        >
          <option value="Semua">Semua Wilayah</option>
          <option value="Palu">Palu</option>
          <option value="Donggala">Donggala</option>
          {/* Tambahkan wilayah lain sesuai dataset */}
        </select>

        <div className="mt-8">
          <h3 className="font-semibold text-gray-700">Ringkasan:</h3>
          <p className="text-sm text-gray-600">Total Titik: {points.length}</p>
        </div>
      </div>

      {/* Konten Utama (Peta) */}
      <div className="w-3/4 relative">
        {/* Komponen Peta yang menampilkan marker berdasarkan state 'points' */}
        <Map points={points} /> 
      </div>
    </div>
  );
}