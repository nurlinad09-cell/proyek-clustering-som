import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Perbaikan bug icon Leaflet yang sering hilang saat di-build di Next.js
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

export default function MapComponent({ points }) {
  // Koordinat default berpusat di Sulawesi Tengah (sekitar Palu)
  const centerPosition = [-0.9006, 119.8780]; 

  return (
    <MapContainer center={centerPosition} zoom={8} style={{ height: '100%', width: '100%' }}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      
      {/* Melakukan looping untuk merender marker berdasarkan koordinat dari backend */}
      {points && points.map((point, index) => (
        <Marker key={index} position={[point.latitude, point.longitude]}>
          <Popup>
            <div className="text-gray-800">
              <strong className="text-blue-700">Titik Rekomendasi #{index + 1}</strong><br />
              <strong>Latitude:</strong> {point.latitude}<br />
              <strong>Longitude:</strong> {point.longitude}<br />
              <strong>Cakupan Titik:</strong> {point.coverage_count || 0}
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}