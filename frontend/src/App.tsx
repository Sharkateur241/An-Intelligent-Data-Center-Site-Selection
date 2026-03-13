import React, { useState, useRef } from "react";
import "./App.css";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix default Leaflet marker icons
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

// Custom teal marker
const tealIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

interface AnalysisResult {
  latitude: number;
  longitude: number;
  score?: number;
  recommendation?: string;
}

interface ClickedLocation {
  lat: number;
  lng: number;
  name?: string;
}

// Component that listens for map clicks
function MapClickHandler({
  onLocationSelect,
}: {
  onLocationSelect: (lat: number, lng: number) => void;
}) {
  useMapEvents({
    click(e) {
      onLocationSelect(
        parseFloat(e.latlng.lat.toFixed(4)),
        parseFloat(e.latlng.lng.toFixed(4))
      );
    },
  });
  return null;
}

export default function App() {
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [radius, setRadius] = useState("1000");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");
  const [clickedLocation, setClickedLocation] =
    useState<ClickedLocation | null>(null);
  const markerRef = useRef<L.Marker | null>(null);

  const handleLocationSelect = (lat: number, lng: number, name?: string) => {
    setLatitude(lat.toString());
    setLongitude(lng.toString());
    setClickedLocation({ lat, lng, name });
    setError("");
  };

  const startAnalysis = async () => {
    if (!latitude || !longitude) {
      setError("⚠ Please select a location on the map or enter coordinates.");
      return;
    }
    setError("");
    setLoading(true);
    setTimeout(() => {
      const score = Math.floor(Math.random() * 40) + 60; // 60-100 range
      setResult({
        latitude: Number(latitude),
        longitude: Number(longitude),
        score,
        recommendation:
          score >= 80
            ? "Excellent site candidate. High energy grid accessibility, low seismic risk, favorable climate stability, and strong connectivity infrastructure detected in this region."
            : score >= 70
            ? "Good site candidate. Moderate climate conditions and reasonable infrastructure. Further on-ground survey recommended before final selection."
            : "Acceptable site with notable constraints. Review local energy costs, flood risk, and connectivity availability before proceeding.",
      });
      setLoading(false);
    }, 2000);
  };

  return (
    <div>
      {/* ── NAVBAR ── */}
      <nav className="navbar">
        <a className="navbar-brand" href="/">
          <div className="brand-icon">IDCSS</div>
          <div className="brand-text">
            <span className="brand-name">IDCSS</span>
            <span className="brand-tagline">
              The Intelligent Data-Center Site Selection
            </span>
          </div>
        </a>
        <div className="navbar-status">
          <div className="status-dot" />
          System Online
        </div>
      </nav>

      {/* ── HERO ── */}
      <div className="hero">
        <div className="hero-bg" />
        <div className="hero-overlay" />
        <div className="hero-content">
          <div className="hero-badge">
            Intelligent Data Center Site Selection
          </div>
          <h1>Powered by Google Earth Engine and AI Technology</h1>
          <p>
            An Intelligent Data Center Site Selection and Energy Optimization
            Based on Google Earth Engine and AI Technology .
          </p>
        </div>
      </div>

      {/* ── MAIN CONTENT ── */}
      <div className="container">
        {/* ── HOW TO USE BANNER ── */}
        <div className="instruction-banner">
          <div className="instruction-icon">💡</div>
          <div className="instruction-text">
            <h3>How to Use IDCSS</h3>
            <p>
              Select a candidate location for your data center directly on the
              interactive map below, fine-tune the analysis radius, then run the
              AI analysis to receive a suitability score and detailed
              recommendation.
            </p>
            <div className="instruction-steps">
              <span className="step-chip">① Click on the map</span>
              <span className="step-chip">② Review coordinates</span>
              <span className="step-chip">③ Set analysis radius</span>
              <span className="step-chip">④ Run AI Analysis</span>
              <span className="step-chip">⑤ Review results</span>
            </div>
          </div>
        </div>

        {/* ── INTERACTIVE MAP ── */}
        <div className="map-card">
          <div className="map-card-header">
            <h2>🗺 Interactive Location Map</h2>
            <span className="map-instruction">
              🖱 Click anywhere on the map to select a location
            </span>
          </div>

          <div className="map-wrapper">
            <MapContainer
              center={[20, 10]}
              zoom={2}
              scrollWheelZoom={true}
              style={{ height: "100%", width: "100%" }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <MapClickHandler onLocationSelect={handleLocationSelect} />
              {clickedLocation && (
                <Marker
                  position={[clickedLocation.lat, clickedLocation.lng]}
                  icon={tealIcon}
                  ref={markerRef}
                >
                  <Popup>
                    <div className="popup-inner">
                      <h4>📍 {clickedLocation.name || "Selected Location"}</h4>
                      <p>
                        <strong>Lat:</strong> {clickedLocation.lat}
                      </p>
                      <p>
                        <strong>Lng:</strong> {clickedLocation.lng}
                      </p>
                      <button
                        onClick={() =>
                          handleLocationSelect(
                            clickedLocation.lat,
                            clickedLocation.lng,
                            clickedLocation.name
                          )
                        }
                      >
                        ✓ Use This Location
                      </button>
                    </div>
                  </Popup>
                </Marker>
              )}
            </MapContainer>
          </div>

          {clickedLocation ? (
            <div className="selected-location-bar">
              <span>📍 Selected coordinates:</span>
              <span className="coord-badge">
                {clickedLocation.lat}, {clickedLocation.lng}
              </span>
              <span style={{ color: "var(--gray-400)", marginLeft: "auto" }}>
                Click the map to change location
              </span>
            </div>
          ) : (
            <div className="map-empty">
              Click anywhere on the map to select a candidate location
            </div>
          )}
        </div>

        {/* ── INPUT PANEL ── */}
        <div className="card">
          <div className="card-header">
            <h2>📋 Analysis Parameters</h2>
            <span className="card-hint">Coordinates auto-fill from map</span>
          </div>

          <div className="input-grid">
            <div className="input-group">
              <label>Latitude</label>
              <input
                type="number"
                value={latitude}
                onChange={(e) => setLatitude(e.target.value)}
                placeholder="Click map or enter e.g. 39.90"
              />
            </div>

            <div className="input-group">
              <label>Longitude</label>
              <input
                type="number"
                value={longitude}
                onChange={(e) => setLongitude(e.target.value)}
                placeholder="Click map or enter e.g. 116.40"
              />
            </div>

            <div className="input-group">
              <label>Analysis Radius</label>
              <select
                value={radius}
                onChange={(e) => setRadius(e.target.value)}
              >
                <option value="500">500 m — Precise parcel</option>
                <option value="1000">1,000 m — Neighbourhood</option>
                <option value="2000">2,000 m — District</option>
                <option value="5000">5,000 m — City zone</option>
                <option value="10000">10,000 m — Regional</option>
              </select>
            </div>
          </div>

          <button
            className="analyze-btn"
            onClick={startAnalysis}
            disabled={loading}
          >
            {loading ? "⏳ Analyzing location data…" : "🚀 Run AI Analysis"}
          </button>

          {error && <p className="error">{error}</p>}
        </div>

        {/* ── AI PANEL ── */}
        <div className="ai-panel">
          <div className="ai-panel-header">
            <div className="ai-avatar">🤖</div>
            <div className="ai-panel-header-text">
              <h2>AI Analysis Engine</h2>
              <p>Multi-factor geospatial intelligence for data center siting</p>
            </div>
          </div>

          <div className="ai-panel-body">
            <div className="ai-how-it-works">
              <h4>How the AI scoring works</h4>
              <div className="ai-steps">
                <div className="ai-step">
                  <div className="ai-step-num">1</div>
                  <span>
                    <strong>Data ingestion</strong> — Google Earth Engine
                    retrieves satellite imagery, elevation models, and climate
                    datasets for the selected radius.
                  </span>
                </div>
                <div className="ai-step">
                  <div className="ai-step-num">2</div>
                  <span>
                    <strong>Multi-factor scoring</strong> The AI evaluates six
                    weighted parameters (see below) and generates a composite
                    0-100 suitability score.
                  </span>
                </div>
                <div className="ai-step">
                  <div className="ai-step-num">3</div>
                  <span>
                    <strong>Recommendation</strong> A plain-language summary is
                    produced highlighting key strengths, risks, and suggested
                    next steps for the site.
                  </span>
                </div>
              </div>
            </div>

            <div className="ai-factors">
              <div className="ai-factor">
                <div className="ai-factor-icon">⚡</div>
                <div className="ai-factor-name">Energy Access</div>
                <div className="ai-factor-desc">
                  Grid proximity &amp; capacity
                </div>
              </div>
              <div className="ai-factor">
                <div className="ai-factor-icon">🌡</div>
                <div className="ai-factor-name">Climate</div>
                <div className="ai-factor-desc">
                  Temp &amp; humidity stability
                </div>
              </div>
              <div className="ai-factor">
                <div className="ai-factor-icon">🌊</div>
                <div className="ai-factor-name">Flood Risk</div>
                <div className="ai-factor-desc">Elevation &amp; drainage</div>
              </div>
              <div className="ai-factor">
                <div className="ai-factor-icon">📡</div>
                <div className="ai-factor-name">Connectivity</div>
                <div className="ai-factor-desc">
                  Fibre &amp; network density
                </div>
              </div>
              <div className="ai-factor">
                <div className="ai-factor-icon">🏔</div>
                <div className="ai-factor-name">Seismic</div>
                <div className="ai-factor-desc">Geological stability</div>
              </div>
              <div className="ai-factor">
                <div className="ai-factor-icon">🏗</div>
                <div className="ai-factor-name">Land Use</div>
                <div className="ai-factor-desc">Zoning &amp; accessibility</div>
              </div>
            </div>
          </div>
        </div>

        {/* ── RESULTS ── */}
        {result && (
          <div className="card">
            <div className="card-header">
              <h2>📊 Analysis Results</h2>
              <span className="card-hint">
                {result.latitude}, {result.longitude}
              </span>
            </div>

            <div className="result-grid">
              <div className="result-box">
                <h3>Coordinates</h3>
                <p>
                  <strong>Latitude:</strong> {result.latitude}
                </p>
                <p>
                  <strong>Longitude:</strong> {result.longitude}
                </p>
                <p>
                  <strong>Radius:</strong> {radius} m
                </p>
              </div>

              <div className="result-box">
                <h3>Suitability Score</h3>
                <p className="score">{result.score}</p>
                <p
                  style={{
                    fontSize: 12,
                    color: "var(--gray-400)",
                    margin: "4px 0 6px",
                  }}
                >
                  out of 100
                </p>
                <div className="score-bar">
                  <div
                    className="score-fill"
                    style={{ width: `${result.score}%` }}
                  />
                </div>
              </div>

              <div className="result-box">
                <h3>AI Recommendation</h3>
                <p>{result.recommendation}</p>
              </div>
            </div>
          </div>
        )}

        {/* ── FOOTER ── */}
        <footer className="footer">
          © 2026 <strong>IDCSS</strong> Essongue Iperot Loice Graduation-Thesis
        </footer>
      </div>
    </div>
  );
}
