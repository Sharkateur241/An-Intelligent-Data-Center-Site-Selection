import React, { useState } from "react";

interface GeographicPanelProps {
  data: Record<string, any> | null | undefined;
}

const FIELD_LABELS: Record<string, string> = {
  elevation: "Elevation",
  terrain_type: "Terrain Type",
  climate_zone: "Climate Zone",
  forest_coverage: "Forest Coverage",
  slope: "Slope",
  aspect: "Aspect",
  soil_type: "Soil Type",
  seismic_zone: "Seismic Zone",
  flood_risk: "Flood Risk",
  land_cover: "Land Cover",
};

export default function GeographicPanel({ data }: GeographicPanelProps) {
  const [imgError, setImgError] = useState(false);

  if (!data || typeof data !== "object") return null;

  const imageUrl: string | undefined =
    data.satellite_image_url || data.image_url || data.url;

  const metadata: Record<string, any> | undefined =
    data.satellite_image_metadata || data.metadata;

  const naturalHazards: string[] | undefined =
    Array.isArray(data.natural_hazards) ? data.natural_hazards : undefined;

  const waterResources: Record<string, any> | undefined =
    data.water_resources && typeof data.water_resources === "object"
      ? data.water_resources
      : undefined;

  // Scalar fields to display in the info grid
  const infoFields = Object.entries(data).filter(([k, v]) => {
    if (
      [
        "satellite_image_url",
        "image_url",
        "url",
        "satellite_image_metadata",
        "metadata",
        "natural_hazards",
        "water_resources",
      ].includes(k)
    )
      return false;
    return v !== null && v !== undefined && typeof v !== "object";
  });

  return (
    <div className="geo-panel">
      {/* Satellite image */}
      <div className="geo-image-wrap">
        {imageUrl && !imgError ? (
          <img
            src={imageUrl}
            alt="Satellite imagery"
            className="geo-image"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="geo-image-placeholder">
            <span className="geo-placeholder-icon">🛰</span>
            <span className="geo-placeholder-text">
              {imgError ? "Image failed to load" : "No satellite image available"}
            </span>
          </div>
        )}
        {metadata && (
          <div className="geo-image-caption">
            {metadata.acquisition_date && (
              <span>📅 {metadata.acquisition_date}</span>
            )}
            {metadata.cloud_cover !== undefined && (
              <span>☁ Cloud cover: {Number(metadata.cloud_cover).toFixed(1)}%</span>
            )}
            {metadata.source && <span>📡 {metadata.source}</span>}
            {metadata.resolution && <span>🔍 {metadata.resolution}</span>}
          </div>
        )}
      </div>

      {/* Info grid */}
      {infoFields.length > 0 && (
        <div className="geo-info-grid">
          {infoFields.map(([k, v]) => (
            <div key={k} className="geo-info-item">
              <span className="geo-info-label">
                {FIELD_LABELS[k] || k.replace(/_/g, " ")}
              </span>
              <span className="geo-info-value">
                {typeof v === "number"
                  ? k.includes("coverage") || k.includes("ratio")
                    ? `${(v * 100).toFixed(1)}%`
                    : k.includes("elevation") || k.includes("slope")
                    ? `${v} m`
                    : String(v)
                  : String(v)}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Natural hazards */}
      {naturalHazards && naturalHazards.length > 0 && (
        <div className="geo-hazards">
          <span className="geo-section-label">⚠ Natural Hazards</span>
          <div className="geo-tags">
            {naturalHazards.map((h) => (
              <span key={h} className="geo-tag geo-tag-warn">
                {h}
              </span>
            ))}
          </div>
        </div>
      )}

      {naturalHazards && naturalHazards.length === 0 && (
        <div className="geo-hazards">
          <span className="geo-section-label">✅ Natural Hazards</span>
          <span className="geo-tag geo-tag-ok">None detected</span>
        </div>
      )}

      {/* Water resources */}
      {waterResources && Object.keys(waterResources).length > 0 && (
        <div className="geo-water">
          <span className="geo-section-label">💧 Water Resources</span>
          <div className="geo-info-grid">
            {Object.entries(waterResources)
              .filter(([, v]) => v !== null && v !== undefined && typeof v !== "object")
              .map(([k, v]) => (
                <div key={k} className="geo-info-item">
                  <span className="geo-info-label">{k.replace(/_/g, " ")}</span>
                  <span className="geo-info-value">{String(v)}</span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
