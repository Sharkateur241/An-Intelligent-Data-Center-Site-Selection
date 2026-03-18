#!/usr/bin/env python3
"""
GEE Authentication Configuration Script - Required Setup
The system must use GEE data, please complete GEE authentication first
"""

import os
import sys
import ee

def setup_gee_auth():
    """Setup GEE authentication"""
    print("=" * 60)
    print("Google Earth Engine Authentication Configuration - Required Step")
    print("=" * 60)
    print()
    print("⚠️  Important: This system must use GEE data!")
    print("Please complete the following steps first:")
    print()
    print("1. Visit https://earthengine.google.com/")
    print("2. Register a Google account and apply for GEE access")
    print("3. Create a Google Cloud project")
    print("4. Enable the Earth Engine API")
    print("5. Complete GEE authentication")
    print()
    
    # Check if already authenticated
    try:
        ee.Initialize(project='data-center-location-analysis')
        print("✅ GEE is authenticated, system can run normally!")
        return True
    except Exception as e:
        print("❌ GEE is not authenticated, please complete authentication first")
        print(f"Error message: {e}")
        print()
        
        # Attempt authentication
        try:
            print("Attempting GEE authentication...")
            ee.Authenticate()
            ee.Initialize(project='data-center-location-analysis')
            print("✅ GEE authentication successful!")
            return True
        except Exception as auth_error:
            print(f"❌ GEE authentication failed: {auth_error}")
            print()
            print("Please manually complete the following steps:")
            print("1. Visit in your browser: https://code.earthengine.google.com/")
            print("2. Sign in with your Google account")
            print("3. Accept the GEE Terms of Service")
            print("4. Re-run this script")
            return False

if __name__ == "__main__":
    success = setup_gee_auth()
    if not success:
        print("\n❌ System cannot start, please complete GEE authentication first!")
        sys.exit(1)
    else:
        print("\n✅ System is ready, you can start!")