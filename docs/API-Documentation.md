# Data Center Intelligent Site Selection and Energy Optimization System — API Documentation

## Overview

This system provides data center site selection analysis services based on satellite imagery and AI, including land use analysis, energy resource assessment, decision analysis, and more.

## Base Information

- **Base URL**: `http://localhost:8000`
- **API Version**: v1.0.0
- **Data Format**: JSON

## API Endpoints

### 1. Health Check

**GET** `/health`

Check service status.

**Response example:**

```json
{
  "status": "healthy"
}
```

### 2. Location Analysis

**POST** `/analyze/location`

Analyze data center site feasibility for a given location.

**Request body:**

```json
{
  "latitude": 39.9042,
  "longitude": 116.4074,
  "radius": 1000,
  "city_name": "Beijing"
}
```

**Parameter description:**

- `latitude`: Latitude (required)
- `longitude`: Longitude (required)
- `radius`: Search radius in meters (optional, default 1000)
- `city_name`: City name (optional)

**Response example:**

```json
{
  "location": {
    "latitude": 39.9042,
    "longitude": 116.4074
  },
  "land_analysis": {
    "total_area": 1000000,
    "land_use_distribution": {
      "water": 0.05,
      "vegetation": 0.25,
      "bare_land": 0.35,
      "buildings": 0.35
    },
    "suitable_areas": [
      {
        "type": "bare_land",
        "area_ratio": 0.35,
        "suitability_score": 0.7
      }
    ],
    "constraints": ["High building density", "Grid load must be considered"],
    "recommendations": [
      "Recommend selecting suburban bare land areas",
      "Grid capacity must be evaluated"
    ]
  },
  "energy_assessment": {
    "solar_data": {
      "annual_irradiance": 1500,
      "solar_zone": "Zone 2",
      "solar_potential": "moderate"
    },
    "wind_data": {
      "wind_zone": "Wind Zone 3",
      "average_speed": 6.5,
      "wind_potential": "moderate"
    },
    "renewable_potential": {
      "total_renewable_potential": {
        "annual_generation_mwh": 50000
      }
    },
    "storage_assessment": {
      "renewable_coverage": 0.5
    },
    "grid_assessment": {
      "available_capacity": 100,
      "voltage_level": "220kV",
      "grid_stability": "good"
    },
    "recommendations": ["Detailed energy assessment recommended"]
  },
  "decision_recommendation": {
    "overall_score": {
      "score": 75,
      "level": "good"
    },
    "detailed_scores": {
      "land_suitability": { "score": 80, "level": "good" },
      "energy_resources": { "score": 70, "level": "good" },
      "grid_capacity": { "score": 75, "level": "good" },
      "economic_feasibility": { "score": 70, "level": "good" },
      "environmental_impact": { "score": 80, "level": "good" }
    },
    "recommendations": ["This location is suitable for a data center"],
    "risk_assessment": {
      "risk_level": "low",
      "risks": []
    },
    "decision_level": "recommended"
  },
  "heat_utilization": {
    "recoverable_heat_mw": 60,
    "utilization_options": [
      {
        "type": "district_heating",
        "capacity_mw": 60,
        "target_users": "residential areas, schools, hospitals",
        "economic_value": 60000000
      }
    ],
    "economic_benefits": {
      "annual_revenue": 60000000,
      "payback_period": 3,
      "co2_reduction": 262800
    },
    "recommendations": ["District heating system construction recommended"]
  }
}
```

### 3. Batch City Analysis

**POST** `/analyze/cities`

Batch analysis of data center site selection for multiple cities.

**Request body:**

```json
{
  "cities": ["Beijing", "Shenzhen", "Lanzhou"]
}
```

**Response example:**

```json
{
  "cities_analysis": {
    "Beijing": {
      // Beijing analysis result, same format as single location analysis
    },
    "Shenzhen": {
      // Shenzhen analysis result, same format as single location analysis
    },
    "Lanzhou": {
      // Lanzhou analysis result, same format as single location analysis
    }
  }
}
```

### 4. Get Satellite Image

**GET** `/satellite/image/{lat}/{lon}`

Get satellite imagery for a specified location.

**Path parameters:**

- `lat`: Latitude
- `lon`: Longitude

**Query parameters:**

- `zoom`: Zoom level (optional, default 15)

**Response example:**

```json
{
  "image_url": "https://example.com/satellite-image.jpg",
  "metadata": {
    "acquisition_date": "2023-06-15",
    "cloud_cover": 5.2,
    "resolution": "medium"
  }
}
```

### 5. Get Energy Resource Information

**GET** `/energy/resources/{lat}/{lon}`

Get energy resource information for a specified location.

**Path parameters:**

- `lat`: Latitude
- `lon`: Longitude

**Response example:**

```json
{
  "solar": {
    "annual_irradiance": 1500,
    "solar_zone": "Zone 2",
    "solar_potential": "moderate"
  },
  "wind": {
    "wind_zone": "Wind Zone 3",
    "average_speed": 6.5,
    "wind_potential": "moderate"
  },
  "location": {
    "latitude": 39.9042,
    "longitude": 116.4074
  },
  "assessment_date": "2023-12-01T10:00:00"
}
```

## Error Handling

All API endpoints may return the following error responses:

**400 Bad Request**

```json
{
  "detail": "Invalid request parameters"
}
```

**500 Internal Server Error**

```json
{
  "detail": "Internal server error"
}
```

## Usage Examples

### Python Example

```python
import requests

# Analyze Beijing area
response = requests.post('http://localhost:8000/analyze/location', json={
    "latitude": 39.9042,
    "longitude": 116.4074,
    "radius": 1000,
    "city_name": "Beijing"
})

if response.status_code == 200:
    analysis = response.json()
    print(f"Overall score: {analysis['decision_recommendation']['overall_score']['score']}")
    print(f"Decision level: {analysis['decision_recommendation']['decision_level']}")
else:
    print(f"Analysis failed: {response.status_code}")
```

### JavaScript Example

```javascript
// Analyze Shenzhen area
fetch("http://localhost:8000/analyze/location", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    latitude: 22.5431,
    longitude: 114.0579,
    radius: 1000,
    city_name: "Shenzhen",
  }),
})
  .then((response) => response.json())
  .then((data) => {
    console.log(
      "Overall score:",
      data.decision_recommendation.overall_score.score
    );
    console.log("Decision level:", data.decision_recommendation.decision_level);
  })
  .catch((error) => {
    console.error("Analysis failed:", error);
  });
```

## Notes

1. All coordinates use the WGS84 coordinate system
2. Distance unit is meters
3. Time format follows the ISO 8601 standard
4. Scores range from 0 to 100
5. HTTPS is recommended in production environments
6. Please manage API call frequency responsibly to avoid overloading the server
