import React, { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMapEvents,
} from "react-leaflet";
import { Card, Typography, Button, Space } from "antd";
import { EnvironmentOutlined } from "@ant-design/icons";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const { Title, Text } = Typography;

// Fix default Leaflet marker icon issue
delete (L.Icon.Default.prototype as any)._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

interface MapComponentProps {
  onLocationSelect: (lat: number, lng: number) => void;
  selectedLocation: { lat: number; lng: number } | null;
}

// Component to handle map click events
const MapClickHandler: React.FC<{
  onLocationSelect: (lat: number, lng: number) => void;
}> = ({ onLocationSelect }) => {
  useMapEvents({
    click: (e) => {
      const { lat, lng } = e.latlng;
      onLocationSelect(lat, lng);
    },
  });

  return null;
};

const MapComponent: React.FC<MapComponentProps> = ({
  onLocationSelect,
  selectedLocation,
}) => {
  // Default world view
  const [mapCenter, setMapCenter] = useState<[number, number]>([20, 0]);
  const [mapZoom, setMapZoom] = useState(2);

  // Update map when a location is selected
  useEffect(() => {
    if (selectedLocation) {
      setMapCenter([selectedLocation.lat, selectedLocation.lng]);
      setMapZoom(12);
    }
  }, [selectedLocation]);

  // Get user current location
  const handleGetCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          onLocationSelect(latitude, longitude);
        },
        (error) => {
          console.error("Failed to get location:", error);
        }
      );
    } else {
      console.error("Geolocation is not supported by this browser.");
    }
  };

  return (
    <Card title="Map Location Selection" className="map-container">
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Button
            type="primary"
            icon={<EnvironmentOutlined />}
            onClick={handleGetCurrentLocation}
          >
            Use Current Location
          </Button>

          <Text type="secondary">
            Click on the map to select a location or use the button to detect
            your current position.
          </Text>
        </Space>
      </div>

      <div style={{ height: "500px", width: "100%" }}>
        <MapContainer
          center={mapCenter}
          zoom={mapZoom}
          style={{ height: "100%", width: "100%" }}
        >
          {/* OpenStreetMap base layer */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Satellite imagery layer */}
          <TileLayer
            attribution='&copy; <a href="https://www.esri.com/">Esri</a>'
            url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            opacity={0.7}
          />

          <MapClickHandler onLocationSelect={onLocationSelect} />

          {selectedLocation && (
            <Marker position={[selectedLocation.lat, selectedLocation.lng]}>
              <Popup>
                <div>
                  <Title level={5}>Selected Location</Title>

                  <Text>Latitude: {selectedLocation.lat.toFixed(6)}</Text>
                  <br />

                  <Text>Longitude: {selectedLocation.lng.toFixed(6)}</Text>
                </div>
              </Popup>
            </Marker>
          )}
        </MapContainer>
      </div>

      {selectedLocation && (
        <div
          style={{
            marginTop: 16,
            padding: 12,
            background: "#f6ffed",
            borderRadius: 4,
          }}
        >
          <Text strong>Selected Coordinates:</Text>
          <br />

          <Text>Latitude: {selectedLocation.lat.toFixed(6)}</Text>
          <br />

          <Text>Longitude: {selectedLocation.lng.toFixed(6)}</Text>
        </div>
      )}
    </Card>
  );
};

export default MapComponent;
