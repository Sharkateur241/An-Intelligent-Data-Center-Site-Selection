import React, { useState, useRef, useEffect } from "react";
import "./App.css";
import { ConfigProvider, theme as antTheme } from "antd";
import EnergyAssessment from "./components/EnergyAssessment";
import DecisionAnalysis from "./components/DecisionAnalysis";
import AnalysisResults from "./components/AnalysisResults";
import GeographicPanel from "./components/GeographicPanel";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const pinIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

interface AnalysisResult {
  location: { latitude: number; longitude: number };
  land_analysis: Record<string, any>;
  energy_assessment: Record<string, any>;
  decision_recommendation: Record<string, any>;
  heat_utilization: Record<string, any>;
  geographic_environment: Record<string, any>;
  power_supply_analysis: Record<string, any>;
  energy_storage_analysis: Record<string, any>;
  promethee_mcgp_analysis: Record<string, any>;
  ai_multimodal_analysis?: Record<string, any> | null;
  ai_energy_analysis?: Record<string, any> | null;
  ai_power_supply_analysis?: Record<string, any> | null;
  ai_energy_storage_analysis?: Record<string, any> | null;
  ai_decision_analysis?: Record<string, any> | null;
}

interface LocationRecommendation {
  latitude: number;
  longitude: number;
  distance_km: number;
  suitability_score: number;
  solar_zone?: string;
  wind_zone?: string;
  water?: string;
  hazards?: string[];
  rationale?: string;
}

interface LocationRecommendationResponse {
  recommended_location: LocationRecommendation;
  candidates: LocationRecommendation[];
}

interface ClickedLocation {
  lat: number;
  lng: number;
  name?: string;
}

function MapClickHandler({
  onLocationSelect,
}: {
  onLocationSelect: (lat: number, lng: number) => void;
}) {
  useMapEvents({
    click(e) {
      onLocationSelect(
        parseFloat(e.latlng.lat.toFixed(6)),
        parseFloat(e.latlng.lng.toFixed(6))
      );
    },
  });
  return null;
}

function ScoreRing({ score, label }: { score: number; label: string }) {
  const [animated, setAnimated] = useState(false);
  const r = 54;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(Math.max(score, 0), 100) / 100;
  const color = score >= 80 ? "#22d3a5" : score >= 60 ? "#f59e0b" : "#ef4444";

  useEffect(() => {
    const t = setTimeout(() => setAnimated(true), 60);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="score-ring-wrap">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle
          cx="70"
          cy="70"
          r={r}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth="10"
        />
        <circle
          cx="70"
          cy="70"
          r={r}
          fill="none"
          stroke={color}
          strokeWidth="10"
          strokeDasharray={circ}
          strokeDashoffset={animated ? circ * (1 - pct) : circ}
          strokeLinecap="round"
          transform="rotate(-90 70 70)"
          className="ring-progress"
        />
        <text
          x="70"
          y="66"
          textAnchor="middle"
          className="ring-score"
          fill={color}
        >
          {Math.round(score)}
        </text>
        <text
          x="70"
          y="84"
          textAnchor="middle"
          className="ring-label"
          fill="rgba(255,255,255,0.4)"
        >
          {label}
        </text>
      </svg>
    </div>
  );
}

function DataSection({
  icon,
  title,
  data,
  accent,
  maxRows,
}: {
  icon: string;
  title: string;
  data: Record<string, any> | null | undefined;
  accent?: string;
  maxRows?: number;
}) {
  const [expanded, setExpanded] = useState(false);

  if (!data || typeof data !== "object") return null;
  const flat = Object.entries(data).filter(
    ([, v]) => v !== null && v !== undefined && typeof v !== "object"
  );
  if (flat.length === 0) return null;
  const visibleRows =
    maxRows && !expanded ? flat.slice(0, maxRows) : flat;
  const hiddenCount = maxRows ? Math.max(flat.length - maxRows, 0) : 0;

  return (
    <div className="ds-card" style={{ "--accent": accent || "#22d3a5" } as any}>
      <div className="ds-head">
        <span className="ds-icon">{icon}</span>
        <span className="ds-title">{title}</span>
      </div>
      <div className="ds-grid">
        {visibleRows.map(([k, v]) => (
          <div key={k} className="ds-row">
            <span className="ds-key">{k.replace(/_/g, " ")}</span>
            <span className="ds-val">{String(v)}</span>
          </div>
        ))}
      </div>
      {hiddenCount > 0 && (
        <button className="ds-toggle" onClick={() => setExpanded(!expanded)}>
          {expanded
            ? "Show less"
            : `Show more (${hiddenCount} hidden)`}
        </button>
      )}
    </div>
  );
}

function AICard({
  icon,
  title,
  data,
}: {
  icon: string;
  title: string;
  data: Record<string, any> | null | undefined;
}) {
  const [open, setOpen] = useState(false);
  if (!data) return null;
  const text =
    data.analysis ||
    data.summary ||
    data.recommendation ||
    data.content ||
    data.error ||
    (typeof data === "string" ? data : null);
  if (!text) return null;

  return (
    <div
      className={`ai-card ${open ? "open" : ""}`}
      onClick={() => setOpen((o) => !o)}
    >
      <div className="ai-card-head">
        <span className="ai-icon">{icon}</span>
        <span className="ai-title">{title}</span>
        <span className="ai-chevron">{open ? "▴" : "▾"}</span>
      </div>
      {open && <div className="ai-body">{String(text)}</div>}
    </div>
  );
}

function Verdict({ score }: { score: number }) {
  if (score >= 80)
    return <span className="verdict verdict-green">✦ Excellent Site</span>;
  if (score >= 65)
    return <span className="verdict verdict-amber">◈ Good Candidate</span>;
  return <span className="verdict verdict-red">⚠ Needs Review</span>;
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
  const [progress, setProgress] = useState(0);
  const [recommendation, setRecommendation] =
    useState<LocationRecommendationResponse | null>(null);
  const [recLoading, setRecLoading] = useState(false);
  const [recError, setRecError] = useState<string | null>(null);
  const [showSticky, setShowSticky] = useState(false);
  const [activeDetailTab, setActiveDetailTab] = useState<'overview' | 'energy' | 'decision' | 'ai'>('overview');
  const markerRef = useRef<L.Marker | null>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  const scorePanelRef = useRef<HTMLDivElement>(null);
  const recAbortRef = useRef<AbortController | null>(null);

  const handleLocationSelect = (lat: number, lng: number, name?: string) => {
    setLatitude(lat.toString());
    setLongitude(lng.toString());
    setClickedLocation({ lat, lng, name });
    setError("");
    setResult(null);
  };

  useEffect(() => {
    if (loading) {
      setProgress(0);
      const steps = [8, 20, 35, 50, 65, 78, 88, 95];
      let i = 0;
      const iv = setInterval(() => {
        if (i < steps.length) {
          setProgress(steps[i]);
          i++;
        } else clearInterval(iv);
      }, 1800);
      return () => clearInterval(iv);
    }
  }, [loading]);

  useEffect(() => {
    if (result && resultsRef.current) {
      setTimeout(
        () =>
          resultsRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          }),
        100
      );
    }
  }, [result]);

  useEffect(() => {
    if (!result) return;
    const score = computeOverallScore(result);
    if (score !== null && score < 50) {
      fetchRecommendation(result.location.latitude, result.location.longitude);
    } else {
      setRecommendation(null);
      setRecError(null);
    }
  }, [result]);

  useEffect(() => {
    if (!result || !scorePanelRef.current) return;
    const observer = new IntersectionObserver(
      ([entry]) => setShowSticky(!entry.isIntersecting),
      { threshold: 0, rootMargin: "-58px 0px 0px 0px" }
    );
    observer.observe(scorePanelRef.current);
    return () => observer.disconnect();
  }, [result]);

  const geoLocate = () => {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = parseFloat(pos.coords.latitude.toFixed(6));
        const lng = parseFloat(pos.coords.longitude.toFixed(6));
        handleLocationSelect(lat, lng);
      },
      () => setError("Geolocation denied or unavailable.")
    );
  };

  const startAnalysis = async () => {
    const lat = Number(latitude);
    const lon = Number(longitude);
    const rad = Number(radius);
    if (!latitude || !longitude) {
      setError("Select a location on the map or enter coordinates.");
      return;
    }
    if (isNaN(lat) || lat < -90 || lat > 90) {
      setError("Latitude must be between -90 and 90.");
      return;
    }
    if (isNaN(lon) || lon < -180 || lon > 180) {
      setError("Longitude must be between -180 and 180.");
      return;
    }
    if (isNaN(rad) || rad <= 0) {
      setError("Radius must be a positive number.");
      return;
    }
    setError("");
    setResult(null);
    setRecommendation(null);
    setRecError(null);
    setRecLoading(false);
    setLoading(true);
    try {
      const response = await fetch("/analyze/location", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          latitude: Number(latitude),
          longitude: Number(longitude),
          radius: Number(radius),
          city_name: clickedLocation?.name || null,
        }),
      });
      if (!response.ok) {
        const detail = await response.text();
        throw new Error(`Server ${response.status}: ${detail}`);
      }
      const data: AnalysisResult = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(`Connection failed: ${err.message}`);
    } finally {
      setLoading(false);
      setProgress(100);
    }
  };

  const fetchRecommendation = async (lat: number, lon: number) => {
    if (recAbortRef.current) recAbortRef.current.abort();
    const controller = new AbortController();
    recAbortRef.current = controller;
    setRecLoading(true);
    setRecError(null);
    try {
      const resp = await fetch("/recommend/location", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          latitude: lat,
          longitude: lon,
          search_radius_km: 100,
          samples: 14,
        }),
        signal: controller.signal,
      });
      if (!resp.ok) {
        const t = await resp.text();
        throw new Error(t || `Server ${resp.status}`);
      }
      const data: LocationRecommendationResponse = await resp.json();
      setRecommendation(data);
    } catch (err: any) {
      if (err.name === "AbortError") return;
      setRecError(err.message);
    } finally {
      setRecLoading(false);
    }
  };

  const overallScore =
    result?.promethee_mcgp_analysis?.overall_score ??
    result?.decision_recommendation?.overall_score ??
    null;
  const energyScore =
    result?.energy_assessment?.renewable_score ??
    result?.energy_assessment?.solar_score ??
    null;
  const powerScore =
    result?.power_supply_analysis?.grid_reliability ??
    result?.power_supply_analysis?.score ??
    null;

  const STEPS = [
    "Satellite fetch",
    "Land analysis",
    "Energy model",
    "Power grid",
    "AI reasoning",
    "PROMETHEE",
    "Final scoring",
  ];

  const computeOverallScore = (res: AnalysisResult | null) => {
    if (!res) return null;
    return (
      res.promethee_mcgp_analysis?.overall_score ??
      res.decision_recommendation?.overall_score ??
      null
    );
  };

  const locationRecommendation = React.useMemo(() => {
    if (!result) return null;

    const promText =
      (typeof result.promethee_mcgp_analysis?.recommendations === "string"
        ? result.promethee_mcgp_analysis.recommendations
        : null) ||
      (Array.isArray(
        (result.promethee_mcgp_analysis as any)?.recommendation?.recommendations
      )
        ? (result.promethee_mcgp_analysis as any).recommendation.recommendations.join(
            "；"
          )
        : (result.promethee_mcgp_analysis as any)?.recommendation
            ?.recommendations) ||
      (result.promethee_mcgp_analysis as any)?.recommendation;

    const decisionText =
      (Array.isArray((result.decision_recommendation as any)?.recommendations)
        ? (result.decision_recommendation as any).recommendations.join("；")
        : (result.decision_recommendation as any)?.recommendation) ||
      (typeof (result.ai_decision_analysis as any)?.analysis === "string"
        ? (result.ai_decision_analysis as any).analysis
        : null);

    return promText || decisionText || null;
  }, [result]);

  return (
    <div className="app">
      <nav className="nav">
        <div className="nav-logo">
          <div className="logo-mark">⬡</div>
          <div className="logo-text">
            <span className="logo-primary">IDCSS</span>
            <span className="logo-sub">
              Intelligent Data-Center Site Selection
            </span>
          </div>
        </div>
        <div className="nav-status">
          <span className="status-pip" />
          Backend Online
        </div>
      </nav>

      <header className="hero">
        <div className="hero-noise" />
        <div className="hero-glow" />
        <div className="hero-inner">
          <div className="hero-chip">IDCSS Platform · v2.0</div>
          <h1 className="hero-h1">
            Intelligent Data Center Site Selection &amp; Energy Optimisation
            <br />Based on <em>Google Earth Engine</em> and <em>AI Technology</em>
          </h1>
          <p className="hero-sub">
            Satellite imagery × Google Earth Engine × AI-powered
            multi-dimensional scoring
          </p>
        </div>
      </header>

      <main className="main">
        <div className="map-row">
          <section className="panel map-panel">
            <div className="panel-head">
              <span className="panel-icon">◎</span>
              <span className="panel-title">Select Location</span>
              <span className="panel-hint">Click anywhere on the map</span>
            </div>
            <div className="map-box">
              <MapContainer
                center={[20, 10]}
                zoom={2}
                scrollWheelZoom
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
                    icon={pinIcon}
                    ref={markerRef}
                  >
                    <Popup>
                      <div className="popup-box">
                        <div className="popup-coord">
                          {clickedLocation.lat}°, {clickedLocation.lng}°
                        </div>
                        <button
                          className="popup-btn"
                          onClick={() =>
                            handleLocationSelect(
                              clickedLocation.lat,
                              clickedLocation.lng
                            )
                          }
                        >
                          Confirm location
                        </button>
                      </div>
                    </Popup>
                  </Marker>
                )}
              </MapContainer>
              <button className="map-geo-btn" onClick={geoLocate} title="Use my location">
                ⊕ My Location
              </button>
            </div>
            {clickedLocation && (
              <div className="coord-bar">
                <span className="coord-label">📍 Selected</span>
                <code className="coord-code">
                  {Math.abs(clickedLocation.lat)}° {clickedLocation.lat >= 0 ? "N" : "S"} &nbsp;/&nbsp; {Math.abs(clickedLocation.lng)}° {clickedLocation.lng >= 0 ? "E" : "W"}
                </code>
              </div>
            )}
          </section>

          <section className="panel params-panel">
            <div className="panel-head">
              <span className="panel-icon">⊞</span>
              <span className="panel-title">Parameters</span>
            </div>
            <div className="params-grid">
              <div className="field">
                <label className="field-label">Latitude</label>
                <input
                  className="field-input"
                  type="number"
                  placeholder="e.g. 48.8566"
                  value={latitude}
                  onChange={(e) => setLatitude(e.target.value)}
                />
              </div>
              <div className="field">
                <label className="field-label">Longitude</label>
                <input
                  className="field-input"
                  type="number"
                  placeholder="e.g. 2.3522"
                  value={longitude}
                  onChange={(e) => setLongitude(e.target.value)}
                />
              </div>
              <div className="field">
                <label className="field-label">Analysis Radius</label>
                <select
                  className="field-input"
                  value={radius}
                  onChange={(e) => setRadius(e.target.value)}
                >
                  <option value="500">500 m</option>
                  <option value="1000">1 000 m</option>
                  <option value="2000">2 000 m</option>
                  <option value="5000">5 000 m</option>
                </select>
              </div>
            </div>
            <button
              className="run-btn"
              onClick={startAnalysis}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="btn-spinner" /> Running analysis…
                </>
              ) : (
                <>Run AI Analysis →</>
              )}
            </button>
            {error && <div className="err-box">⚠ {error}</div>}
          </section>
        </div>

        {loading && (
          <section className="panel load-panel">
            <div className="load-head">Analyzing site…</div>
            <div className="load-bar-track">
              <div
                className="load-bar-fill"
                style={{ width: `${progress}%` }}
              />
            </div>
            <div className="load-steps">
              {STEPS.map((s, i) => {
                const threshold = ((i + 1) / STEPS.length) * 100;
                const done = progress >= threshold;
                const active = !done && progress >= (i / STEPS.length) * 100;
                return (
                  <div
                    key={s}
                    className={`load-step ${
                      done ? "done" : active ? "active" : ""
                    }`}
                  >
                    <span className="step-dot" />
                    <span>{s}</span>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {result && (
          <div ref={resultsRef} className="results-root">
            <section className="panel score-panel" ref={scorePanelRef}>
              <div className="score-left">
                <div className="score-loc">
                  <span>◎</span>
                  {result.location.latitude}°,&nbsp;{result.location.longitude}°
                </div>
                {overallScore !== null && (
                  <Verdict score={Number(overallScore)} />
                )}
                <h2 className="score-headline">Analysis Complete</h2>
                <p className="score-sub">
                  Multi-criteria evaluation across{" "}
                  {
                    Object.keys(result).filter(
                      (k) => !k.startsWith("ai_") && k !== "location"
                    ).length
                  }{" "}
                  dimensions using satellite data and AI reasoning.
                </p>
              </div>
              <div className="score-rings">
                {overallScore !== null && (
                  <ScoreRing score={Number(overallScore)} label="Overall" />
                )}
                {energyScore !== null && (
                  <ScoreRing score={Number(energyScore)} label="Energy" />
                )}
                {powerScore !== null && (
                  <ScoreRing score={Number(powerScore)} label="Power" />
                )}
              </div>
            </section>

            {locationRecommendation && (
              <section className="panel rec-panel">
                <div className="rec-head">
                  <div className="rec-chip">AI Recommendation</div>
                  {overallScore !== null && (
                    <Verdict score={Number(overallScore)} />
                  )}
                </div>
                <div className="rec-body">
                  <div className="rec-icon">🧭</div>
                  <div className="rec-text">
                    <p>{String(locationRecommendation)}</p>
                  </div>
                </div>
                <div className="rec-meta">
                  <span className="rec-pill">PROMETHEE · Decision AI</span>
                  <span className="rec-pill">
                    Radius {radius} m · Lat {latitude || result.location.latitude}
                    ° · Lon {longitude || result.location.longitude}°
                  </span>
                </div>
              </section>
            )}

            {overallScore !== null && overallScore < 50 && (
              <section className="panel alt-panel">
                <div className="panel-head">
                  <span className="panel-icon">🧭</span>
                  <span className="panel-title">Nearby Recommended Location</span>
                  <span className="panel-hint">Auto-search within 100 km</span>
                </div>
                {recLoading && (
                  <div className="alt-body">Searching for better nearby sites…</div>
                )}
                {recError && (
                  <div className="err-box">⚠ Recommendation failed: {recError}</div>
                )}
                {recommendation && (
                  <div className="alt-body">
                    <div className="alt-row">
                      <div>
                        <div className="alt-label">Best candidate</div>
                        <div className="alt-coord">
                          {recommendation.recommended_location.latitude.toFixed(
                            4
                          )}
                          °,{" "}
                          {recommendation.recommended_location.longitude.toFixed(
                            4
                          )}
                          °
                        </div>
                      </div>
                      <div className="alt-score">
                        Score {recommendation.recommended_location.suitability_score}
                      </div>
                    </div>
                    <div className="alt-meta">
                      <span>
                        Distance {recommendation.recommended_location.distance_km} km
                      </span>
                      {recommendation.recommended_location.solar_zone && (
                        <span>
                          Solar {recommendation.recommended_location.solar_zone}
                        </span>
                      )}
                      {recommendation.recommended_location.wind_zone && (
                        <span>
                          Wind {recommendation.recommended_location.wind_zone}
                        </span>
                      )}
                      {recommendation.recommended_location.water && (
                        <span>
                          Water {recommendation.recommended_location.water}
                        </span>
                      )}
                    </div>
                    {recommendation.recommended_location.rationale && (
                      <p className="alt-rationale">
                        {recommendation.recommended_location.rationale}
                      </p>
                    )}
                    <button
                      className="run-btn ghost"
                      onClick={() =>
                        handleLocationSelect(
                          recommendation.recommended_location.latitude,
                          recommendation.recommended_location.longitude
                        )
                      }
                    >
                      Use this location →
                    </button>
                  </div>
                )}
              </section>
            )}

            <div className="data-grid">
              <div className="ds-card" style={{ "--accent": "#22d3a5", gridColumn: "1 / -1" } as any}>
                <div className="ds-head">
                  <span className="ds-icon">🌍</span>
                  <span className="ds-title">Geographic Environment</span>
                </div>
                <GeographicPanel data={result.geographic_environment} />
              </div>
              <DataSection
                icon="🏗"
                title="Land Analysis"
                data={result.land_analysis}
                accent="#38bdf8"
              />
              <DataSection
                icon="⚡"
                title="Energy Assessment"
                data={result.energy_assessment}
                accent="#f59e0b"
              />
              <DataSection
                icon="🔌"
                title="Power Supply"
                data={result.power_supply_analysis}
                accent="#a78bfa"
              />
              <DataSection
                icon="🔋"
                title="Energy Storage"
                data={result.energy_storage_analysis}
                accent="#34d399"
              />
              <DataSection
                icon="♻️"
                title="Heat Utilization"
                data={result.heat_utilization}
                accent="#fb7185"
              />
              <DataSection
                icon="📐"
                title="PROMETHEE–MCGP"
                data={result.promethee_mcgp_analysis}
                accent="#22d3a5"
              />
              <DataSection
                icon="✅"
                title="Decision Recommendation"
                data={result.decision_recommendation}
                accent="#4ade80"
              />
            </div>

            <ConfigProvider theme={{ algorithm: antTheme.darkAlgorithm }}>
              <section className="panel detail-panel">
                <div className="result-tabs">
                  {(["overview", "energy", "decision", "ai"] as const).map((tab) => {
                    const labels: Record<string, string> = {
                      overview: "📊 Overview",
                      energy: "⚡ Energy",
                      decision: "📐 Decision",
                      ai: "🧠 AI Reasoning",
                    };
                    return (
                      <button
                        key={tab}
                        className={`result-tab${activeDetailTab === tab ? " active" : ""}`}
                        onClick={() => setActiveDetailTab(tab)}
                      >
                        {labels[tab]}
                      </button>
                    );
                  })}
                </div>
                <div className="tab-content">
                  {activeDetailTab === "overview" && <AnalysisResults data={result} />}
                  {activeDetailTab === "energy" && <EnergyAssessment data={result} />}
                  {activeDetailTab === "decision" && <DecisionAnalysis data={result} />}
                  {activeDetailTab === "ai" && (
                    <div className="ai-list">
                      <AICard icon="🛰" title="Multimodal Analysis" data={result.ai_multimodal_analysis} />
                      <AICard icon="⚡" title="Energy AI Analysis" data={result.ai_energy_analysis} />
                      <AICard icon="🔌" title="Power Supply AI" data={result.ai_power_supply_analysis} />
                      <AICard icon="🔋" title="Energy Storage AI" data={result.ai_energy_storage_analysis} />
                      <AICard icon="🧠" title="Decision AI" data={result.ai_decision_analysis} />
                    </div>
                  )}
                </div>
              </section>
            </ConfigProvider>
          </div>
        )}
      </main>

      {result && overallScore !== null && (
        <div className={`sticky-bar${showSticky ? " visible" : ""}`}>
          <span className="sticky-loc">
            {result.location.latitude.toFixed(4)}°, {result.location.longitude.toFixed(4)}°
          </span>
          <div className="sticky-score">
            <span
              className="sticky-score-val"
              style={{
                color: Number(overallScore) >= 80 ? "#22d3a5" : Number(overallScore) >= 65 ? "#f59e0b" : "#ef4444",
              }}
            >
              {Math.round(Number(overallScore))}
            </span>
            <span className="sticky-score-label">/ 100</span>
          </div>
          <Verdict score={Number(overallScore)} />
          <span className="sticky-spacer" />
          <span className="sticky-scroll-hint">↑ scroll up for details</span>
        </div>
      )}

      <footer className="foot">
        © 2026 IDCSS — Graduation Thesis Essongue Iperot Loice 2026
        &nbsp;·&nbsp; Google Earth Engine + OpenAI
      </footer>
    </div>
  );
}
