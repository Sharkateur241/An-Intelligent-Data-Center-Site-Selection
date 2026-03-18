# Google Earth Engine Authentication Setup Guide

## 📋 Overview

This project uses Google Earth Engine (GEE) to retrieve satellite imagery and geographic data. To use this feature, you need to set up GEE authentication.

## 🔑 Getting GEE Authentication

### Method 1: Using a Personal Google Account (Recommended for Development)

1. **Visit the GEE website**
   - Open https://earthengine.google.com/
   - Sign in with your Google account

2. **Register for a GEE account**
   - Click "Sign up for Earth Engine"
   - Fill out the registration form
   - Wait for approval (usually takes 1-2 days)

3. **Get your Project ID**
   - Create a new project in the GEE console
   - Record the project ID (e.g.: `your-project-name`)

### Method 2: Using a Service Account (Recommended for Production)

1. **Create a Google Cloud Project**
   - Visit https://console.cloud.google.com/
   - Create a new project or select an existing one

2. **Enable the Earth Engine API**
   - In Google Cloud Console
   - Go to "APIs & Services" > "Library"
   - Search for "Earth Engine API" and enable it

3. **Create a Service Account**
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Fill in the service account details

4. **Generate a Key File**
   - In the service account list, click the service account you just created
   - Go to the "Keys" tab
   - Click "Add Key" > "Create new key"
   - Select "JSON" format
   - Download the key file

5. **Add the Key File to the Project**
   - Rename the downloaded JSON file to `gee_service_account_key.json`
   - Place the file in the project root directory

## ⚙️ Project Configuration

### 1. Copy the environment configuration file

```bash
cp env.example .env
```

### 2. Edit the .env file

```env
# GEE Configuration
GEE_PROJECT_ID=your_gee_project_id
GEE_SERVICE_ACCOUNT_KEY_PATH=./gee_service_account_key.json
```

### 3. Set environment variables (optional)

```bash
# Windows
set GEE_PROJECT_ID=your_gee_project_id
set GOOGLE_APPLICATION_CREDENTIALS=./gee_service_account_key.json

# Linux/Mac
export GEE_PROJECT_ID=your_gee_project_id
export GOOGLE_APPLICATION_CREDENTIALS=./gee_service_account_key.json
```

## 🧪 Testing the GEE Connection

Run the following command to test the GEE connection:

```bash
python setup_gee_auth.py
```

If you see the "GEE authentication successful" message, the configuration is correct.

## ❗ Important Notes

1. **Do not commit the key file to Git**
   - Make sure `gee_service_account_key.json` is listed in `.gitignore`
   - Use `env.example` as a template

2. **Permission Management**
   - The service account requires Earth Engine user permissions
   - Contact the GEE team to add service account permissions

3. **Quota Limits**
   - GEE has usage quota limits
   - Exceeding the limit may cause requests to fail

## 🔧 Troubleshooting

### Common Errors

1. **Authentication Failed**

```
   Error: The caller does not have permission
```

- Check if the service account has GEE permissions
- Confirm the project ID is correct

2. **API Not Enabled**

```
   Error: Earth Engine API has not been used
```

- Enable the Earth Engine API in Google Cloud Console

3. **Quota Exceeded**

```
   Error: Quota exceeded
```

- Wait for quota reset or apply for a quota increase

### Getting Help

- [GEE Official Documentation](https://developers.google.com/earth-engine)
- [GEE Community Forum](https://groups.google.com/forum/#!forum/google-earth-engine-developers)
- [Project Issues](https://github.com/your-repo/issues)

## 📝 Changelog

- 2025-10-12: Initial version
- Added both personal account and service account authentication methods
- Provided detailed configuration steps and troubleshooting guide
