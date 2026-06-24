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
      const baseUrl = 'https://nurlina-apiclusteringsom.hf.space'; 
       // 🛠️ 2. Ubah variabel url agar menggunakan baseUrl di atas
      const url = wilayah === 'Semua' 
      ? `${baseUrl}/api/cluster` 
      : `${baseUrl}/api/cluster?wilayah=${wilayah}`;
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
          className="w-full p-2 border rounded bg-white text-gray-800"
          value={wilayah} 
          onChange={(e) => setWilayah(e.target.value)}
        >
          <option value="Semua">Semua Wilayah</option>
          <option value="BANGGAI">BANGGAI</option>
          <option value="BANGGAI KEPULAUAN">BANGGAI KEPULAUAN</option>
          <option value="BANGGAI LAUT">BANGGAI LAUT</option>
          <option value="BUOL">BUOL</option>
          <option value="DONGGALA">DONGGALA</option>
          <option value="KOTA PALU">KOTA PALU</option>
          <option value="MOROWALI">MOROWALI</option>
          <option value="MOROWALI UTARA">MOROWALI UTARA</option>
          <option value="PARIGI MOUTONG">PARIGI MOUTONG</option>
          <option value="POSO">POSO</option>
          <option value="SIGI">SIGI</option>
          <option value="TOJO UNA-UNA">TOJO UNA-UNA</option>
          <option value="TOLI TOLI">TOLI TOLI</option>
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