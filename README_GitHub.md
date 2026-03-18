# Data Center Intelligent Site Selection and Energy Optimization System

A data center site selection system based on Google Earth Engine satellite imagery and AI, integrated with the PROMETHEE-MCGP decision-making method.

## 🚀 Quick Start

### Requirements

- Python 3.8+
- Node.js 16+
- **Google Earth Engine account (required)**

### Installation Steps

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/data-center-location-analysis.git
cd data-center-location-analysis
```

2. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

3. **Install frontend dependencies**

```bash
cd frontend
npm install
npm run build
cd ..
```

4. **Configure GEE (required)**

```bash
python setup_gee_auth.py
```

5. **Start the system**

```bash
python start_system.py
```

6. **Access the system**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📊 Features

- 🌍 **GEE Satellite Image Analysis** - Based on high-resolution satellite data from Google Earth Engine
- 🏗️ **Land Use Analysis** - Intelligent vacant land identification and land suitability assessment
- ⚡ **Power Supply Analysis** - Evaluation of renewable energy sources including solar, wind, and hydropower
- 🔋 **Energy Storage Layout Analysis** - Optimization of multiple energy storage technology solutions
- 🔥 **Waste Heat Utilization** - Northern district heating and southern industrial heat applications
- 📈 **PROMETHEE-MCGP Decision Making** - Scientific multi-criteria decision analysis

## 🔧 Configuration

### GEE Configuration (required)

⚠️ **Important: This system must use GEE data!**

1. Visit https://earthengine.google.com/
2. Register a Google account and apply for GEE access
3. Create a Google Cloud project
4. Enable the Earth Engine API
5. Run `python setup_gee_auth.py` to complete authentication

### Environment Variables

Create a `.env` file (optional):

```
GEE_PROJECT_ID=your-project-id
GEE_SERVICE_ACCOUNT=your-service-account
```

## 📚 User Guide

1. Enter latitude/longitude coordinates or select a city
2. The system automatically analyzes:
   - Land use conditions
   - Energy resource assessment
   - Power supply recommendations
   - Energy storage layout analysis
   - Waste heat utilization options
   - Comprehensive decision score

## 🛠️ Development Notes

### Project Structure

```
├── backend/                 # Backend API service
│   ├── services/           # Analysis service modules
│   └── main.py            # FastAPI application
├── frontend/              # Frontend React application
│   ├── src/               # Source code
│   └── build/             # Build files
└── docs/                  # Documentation
```

### API Endpoints

- `POST /analyze/location` - Location analysis
- `POST /analyze/cities` - City comparison analysis
- `GET /satellite/image/{lat}/{lon}` - Retrieve satellite image
