# Google Earth Engine Authentication Configuration Guide

## Overview

This guide will help you configure a Google Earth Engine (GEE) non-commercial account to use real satellite data in the data center site selection system.

## Prerequisites

1. **Google account**: A Google account is required
2. **GEE account**: A registered Google Earth Engine non-commercial account
3. **Network connection**: Able to access Google services
4. **Python environment**: Python 3.8+ installed

## Quick Setup

### Method 1: Use the automatic configuration script (recommended)

```bash
# Run the authentication configuration script
python setup_gee_auth.py
```

The script will automatically:

1. Check the current GEE status
2. Open the browser for authentication
3. Complete initialization configuration
4. Test the connection

### Method 2: Manual configuration

#### Step 1: Install the GEE Python API

```bash
pip install earthengine-api
```

#### Step 2: Start the authentication process

```python
import ee

# Start authentication (opens the browser)
ee.Authenticate()

# Initialize GEE
ee.Initialize()
```

#### Step 3: Test the connection

```python
# Test basic functionality
point = ee.Geometry.Point([116.4074, 39.9042])  # Beijing coordinates
collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(point).limit(1)
image = collection.first()
print(image.getInfo())
```

## Detailed Configuration Steps

### 1. Register a GEE account

1. Visit [Google Earth Engine](https://earthengine.google.com/)
2. Click "Sign up for Earth Engine"
3. Sign in with your Google account
4. Select "Non-commercial use"
5. Fill in the application form
6. Wait for approval (usually 1–2 business days)

### 2. Authentication configuration

#### Browser authentication flow

1. **Run the authentication command**:

   ```python
   import ee
   ee.Authenticate()
   ```

2. **The browser will open automatically**, showing the authentication page

3. **Select your Google account** (make sure it is the account registered with GEE)

4. **Authorize application access**:

   - Click "Allow"
   - Copy the generated authentication token

5. **Paste the token** into the command line

6. **Complete authentication**

#### Authentication file location

After authentication, the credentials file will be created at:

- **Windows**: `C:\Users\<username>\.config\earthengine\credentials`
- **Linux/Mac**: `~/.config/earthengine/credentials`

### 3. Initialize GEE

```python
import ee

try:
    ee.Initialize()
    print("GEE initialized successfully!")
except Exception as e:
    print(f"Initialization failed: {e}")
```

### 4. Test data access

```python
# Test Landsat data access
collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
print(f"Landsat image count: {collection.size().getInfo()}")

# Test data for a specific area
point = ee.Geometry.Point([116.4074, 39.9042])  # Beijing
image = collection.filterBounds(point).first()
print(f"Image ID: {image.getInfo()['id']}")
```

## Troubleshooting

### Issue 1: Authentication failed

**Error message**: `Authentication failed`

**Solution**:

1. Make sure you have registered a GEE account
2. Check your network connection
3. Clear your browser cache
4. Re-run the authentication process

### Issue 2: Quota exceeded

**Error message**: `Quota exceeded`

**Solution**:

1. Non-commercial accounts have usage limits
2. Wait for quota reset (usually 24 hours)
3. Optimize queries to reduce data volume
4. Consider upgrading to a commercial account

### Issue 3: Network connection problem

**Error message**: `Connection timeout`

**Solution**:

1. Check your network connection
2. Use a VPN (if required in your region)
3. Check your firewall settings
4. Try a different network environment

### Issue 4: Insufficient permissions

**Error message**: `Permission denied`

**Solution**:

1. Make sure your account has been approved by GEE
2. Check your account status
3. Contact the GEE support team

## Usage Limits

### Non-commercial account limits

1. **Data limit**: Monthly data download limit
2. **Compute limit**: Computation quota limit
3. **Storage limit**: Storage space limit
4. **API call limit**: API call rate limit

### Optimization recommendations

1. **Cache results**: Avoid querying the same data repeatedly
2. **Batch processing**: Combine multiple query requests
3. **Data compression**: Use appropriate data formats
4. **Error handling**: Implement a retry mechanism

## Verify Configuration

Run the following code to verify your configuration:

```python
import ee

def verify_gee_setup():
    """Verify GEE configuration"""
    try:
        # Initialize
        ee.Initialize()
        print("✅ GEE initialized successfully")

        # Test data access
        point = ee.Geometry.Point([116.4074, 39.9042])
        collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        image = collection.filterBounds(point).first()

        if image:
            info = image.getInfo()
            print(f"✅ Data access successful")
            print(f"   Image ID: {info.get('id')}")
            print(f"   Acquisition date: {info.get('properties', {}).get('DATE_ACQUIRED')}")
            return True
        else:
            print("❌ Unable to fetch data")
            return False

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

# Run verification
if verify_gee_setup():
    print("\n🎉 GEE configuration verified successfully! You can now start using the data center site selection system.")
else:
    print("\n❌ GEE configuration verification failed. Please check your configuration.")
```

## Start the System

After configuration is complete, start the data center site selection system:

```bash
# Start the backend service
python backend/main.py

# Start the frontend service (new terminal)
cd frontend
npm start
```

Visit `http://localhost:3000` to start using the system.

## Technical Support

If you encounter any issues:

1. Check the official GEE documentation
2. Check the GEE status page
3. Contact the GEE support team
4. Check the project GitHub Issues

## Changelog

- **v1.0**: Initial version, supports non-commercial GEE account authentication
- **v1.1**: Added automatic configuration script
- **v1.2**: Improved error handling and user prompts
