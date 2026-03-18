Google Earth Engine Real Data Configuration Complete Guide
🎯 Goal
Configure GEE to use real satellite data, replacing simulated data.
📋 Current Issues

Missing Google Cloud Project: GEE requires a linked Google Cloud project
API not enabled: Earth Engine API needs to be enabled
Permission configuration: Project permissions need to be correctly configured

🚀 Solution Steps
Step 1: Create a Google Cloud Project

Visit Google Cloud Console

Open: https://console.cloud.google.com/
Sign in with your Google account

Create a new project

Click the project selector
Click "New Project"
Project name: data-center-location-analysis
Click "Create"

Record the Project ID

Project ID format: data-center-location-analysis-xxxxx
Note this project ID, you will need it later

Step 2: Enable the Earth Engine API

Go to the API Library

In Google Cloud Console
Navigate to "APIs & Services" > "Library"

Search and enable the API

Search for "Earth Engine API"
Click "Enable"

Wait for activation to complete

This usually takes a few minutes

Step 3: Configure Earth Engine

Visit Earth Engine

Open: https://earthengine.google.com/
Sign in with the same Google account

Link the project

In the Earth Engine interface
Select the Google Cloud project you created
Confirm the link

Step 4: Update Code Configuration
Modify backend/services/satellite_service.py:
pythondef **init**(self):
"""Initialize GEE service"""
try: # Initialize GEE with your project ID
project_id = "your-project-id-here" # Replace with your project ID
ee.Initialize(project=project_id)
print("Google Earth Engine initialized successfully")
self.use_real_data = True
except Exception as e:
print(f"GEE initialization failed: {e}")
print("Please check project configuration")
self.use_real_data = False
Step 5: Test Real Data
Run the test script to verify configuration:
pythonimport ee

# Use your project ID

project_id = "your-project-id-here"
ee.Initialize(project=project_id)

# Test data access

point = ee.Geometry.Point([116.4074, 39.9042]) # Beijing
collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
image = collection.filterBounds(point).first()
print("Real data test successful!")
print("Image ID:", image.getInfo()['id'])
🔧 Quick Configuration Script
Create an automatic configuration script:
python# configure_gee.py
import ee
import os

def configure_gee():
"""Configure GEE to use real data"""

    # Get project ID
    project_id = input("Please enter your Google Cloud project ID: ")

    try:
        # Initialize GEE
        ee.Initialize(project=project_id)
        print("✅ GEE initialized successfully!")

        # Test data access
        point = ee.Geometry.Point([116.4074, 39.9042])
        collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        image = collection.filterBounds(point).first()

        if image:
            info = image.getInfo()
            print("✅ Real data access successful!")
            print(f"   Image ID: {info.get('id')}")
            print(f"   Acquisition date: {info.get('properties', {}).get('DATE_ACQUIRED')}")

            # Save project ID to config file
            with open('.gee_project_id', 'w') as f:
                f.write(project_id)
            print("✅ Project ID saved to config file")

            return True
        else:
            print("❌ Unable to retrieve data")
            return False

    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

if **name** == "**main**":
configure_gee()
📝 Detailed Operation Steps

1. Create Google Cloud Project
   Visit: https://console.cloud.google.com/
   Steps:

Click the project selector at the top
Click "New Project"
Enter project name: data-center-location-analysis
Click "Create"
Wait for project creation to complete
Record the project ID (format: data-center-location-analysis-xxxxx)

2. Enable Earth Engine API
   Visit: https://console.cloud.google.com/apis/library
   Steps:

Search for "Earth Engine API"
Click to enter the API page
Click the "Enable" button
Wait for activation to complete (usually 2-3 minutes)

3. Link Earth Engine Project
   Visit: https://earthengine.google.com/
   Steps:

Sign in with the same Google account
Select the Google Cloud project you created in the project selector
Confirm the link

4. Update the Code
   Modify the project ID in backend/services/satellite_service.py:
   python# Change this line
   ee.Initialize()

# To this

ee.Initialize(project="your-actual-project-id")
🧪 Test Verification
Create test script test_gee.py:
pythonimport ee

def test_gee_connection():
"""Test GEE connection"""
try: # Use your project ID
project_id = "your-project-id-here"
ee.Initialize(project=project_id)

        print("✅ GEE initialized successfully")

        # Test Beijing area data
        beijing = ee.Geometry.Point([116.4074, 39.9042])
        collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        image = collection.filterBounds(beijing).first()

        if image:
            info = image.getInfo()
            print("✅ Data access successful")
            print(f"Image ID: {info.get('id')}")
            print(f"Acquisition date: {info.get('properties', {}).get('DATE_ACQUIRED')}")
            print(f"Cloud cover: {info.get('properties', {}).get('CLOUD_COVER')}%")
            return True
        else:
            print("❌ Unable to retrieve image data")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if **name** == "**main**":
test_gee_connection()
