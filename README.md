# 🚀 Data Center Intelligent Site Selection & Energy Optimization

An AI- and Google Earth Engine–powered system for data center siting and energy resource assessment. Combines satellite remote sensing, multimodal AI analysis, and multi-criteria decision methods.

## ✨ Key Features

- 🌍 **Satellite imagery analysis** — High-resolution GEE imagery with AI analysis
- ⚡ **Energy resource assessment** — Solar, wind, and hydro potential
- 🏭 **Waste-heat utilization analysis** — Data center heat recovery potential
- 🌿 **Geographic environment analysis** — Elevation, rivers, forests, climate factors
- 🔋 **Power supply analysis** — Tech/economic evaluation of supply schemes
- 💾 **Energy storage layout** — Optimized storage system planning
- 🎯 **Intelligent decision analysis** — PROMETHEE-MCGP multi-criteria scoring
- 🤖 **Multimodal AI analysis** — Combined image/text/data reasoning
- 📊 **Interactive map** — Leaflet-based visualization

## 🛠️ Tech Stack

### Backend
- **FastAPI 0.104.1** — high-performance web framework
- **Google Earth Engine** — satellite data processing
- **Python 3.8+** — core language
- **Pydantic 2.5.0** — data validation
- **Uvicorn** — ASGI server
- **OpenCV** — image processing
- **scikit-learn** — machine learning
- **NumPy & Pandas** — data handling

### Frontend
- **React 18**
- **TypeScript**
- **Ant Design 5.27.4**
- **Leaflet**
- **Recharts**

## 📋 System Requirements

- **Python 3.8+** (3.9+ recommended)
- **Node.js 16+** (18+ recommended)
- **Google Earth Engine account** (required)
- **8GB+ RAM** (recommended)
- **Stable internet** (for GEE)
- **Windows/Linux/Mac** (WSL supported)

## 🚀 Quick Start

### Option 1: One-click (recommended)

Double-click `start.bat`.

It will:
- Set proxy (if configured)
- Build the frontend
- Start the backend
- Show access URLs

### Option 2: Full setup

#### 1️⃣ Install dependencies
```cmd
# Windows
install_all.bat

# Linux/Mac
chmod +x install_all.sh
./install_all.sh

# Or manual
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
```

#### 2️⃣ Configure environment
```cmd
cp env.example .env
# Edit .env:
# - OPENAI_API_KEY
# - GEE_PROJECT_ID
# - proxy settings if needed
```

#### 3️⃣ GEE authentication (required)
```cmd
python setup_gee_auth.py
```
The system must use Google Earth Engine data. See [GEE_SETUP_GUIDE.md](GEE_SETUP_GUIDE.md) for details.

#### 4️⃣ Start the system
```cmd
# Option 1
start.bat

# Option 2
python start_system.py
```

### 🌐 Access
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API docs**: http://localhost:8000/docs

## 📖 Documentation

- [GEE Setup Guide](docs/GEE认证指南.md)
- [API Docs](docs/API文档.md)
- [User Guide](docs/使用指南.md)
- [GEE Real Data Guide](GEE真实数据配置指南.md)

## 🔧 Configuration Notes

### GEE auth
Required steps:
1. Register a GEE account
2. Create a Google Cloud project
3. Enable Earth Engine API
4. Run the auth script

See the GEE setup guide above.

### Environment variables
Create `.env` (optional):
```env
GEE_PROJECT_ID=your-project-id
DEBUG=False
```

## 📊 System Structure

```
├── backend/                    # Backend services
│   ├── main.py                 # FastAPI app
│   └── services/               # Service layer
│       ├── satellite_service.py           # Satellite imagery service
│       ├── image_analysis.py              # Image analysis
│       ├── energy_assessment.py           # Energy assessment
│       ├── energy_ai_analysis.py          # Energy AI analysis
│       ├── power_supply_analysis.py       # Power supply analysis
│       ├── power_supply_ai_analysis.py    # Power supply AI
│       ├── energy_storage_analysis.py     # Storage layout analysis
│       ├── energy_storage_ai_analysis.py  # Storage AI
│       ├── decision_analysis.py           # Decision analysis
│       ├── decision_ai_analysis.py        # Decision AI
│       ├── promethee_mcgp_analysis.py     # PROMETHEE decisioning
│       ├── multimodal_analysis.py         # Multimodal analysis
├── frontend/                  # Frontend app
│   ├── src/                  # React source
│   │   ├── App.tsx           # Main app
│   │   └── components/       # Components
│   │       ├── MapComponent.tsx      # Map
│   │       ├── EnergyAssessment.tsx  # Energy assessment
│   │       ├── DecisionAnalysis.tsx  # Decision analysis
│   │       └── AnalysisResults.tsx   # Results
│   └── build/                # Build output
├── docs/                     # Docs
├── notebooks/                # Jupyter samples
└── scripts/                  # Startup scripts
    ├── start.bat             # One-click start
    ├── install_all.bat       # One-click install
    └── setup_gee_auth.py     # GEE auth
```

## 🌟 Core Capabilities

### 🌍 Satellite imagery
- Landsat 8/9 and Sentinel-2
- Cloud filtering and quality optimization
- Multiple data-source fallbacks
- 20 km coverage radius
- AI image recognition and analysis

### ⚡ Energy assessment
- AI-based solar irradiance estimation
- AI wind resource assessment
- Hydropower potential
- Renewable coverage calculation
- Multimodal data fusion

### 🔋 Power & storage
- Tech-economic evaluation of supply schemes
- Storage system layout optimization
- AI-driven cost-benefit analysis
- Renewable integration schemes

### 🎯 Decision analysis
- PROMETHEE multi-criteria method
- AI-enhanced decision support
- Economic and natural factor evaluation
- Integrated scoring and ranking

### 🤖 AI features
- Multimodal AI (image + text + data)
- Intelligent image recognition
- Automated decision support
- Predictive analysis

## 🚨 Troubleshooting

### Common issues

1. **GEE auth failure**
   ```cmd
   python setup_gee_auth.py
   ```

2. **Dependency install failure**
   ```cmd
   install_all.bat
   ```

3. **Network problems**
   - Check proxy settings
   - Ensure access to Google services

4. **Port in use**
   - Backend: 8000
   - Frontend: 3000

### System checks
```cmd
# Backend status
python check_backend_status.py

# Network check
python check_network.py
```

## 📝 Changelog

### v1.0.0 (current)
- ✅ Integrated Google Earth Engine
- ✅ Multimodal AI analysis
- ✅ Interactive map UI
- ✅ Full API docs
- ✅ One-click start scripts

## 🤝 Contributing

Issues and PRs are welcome!
