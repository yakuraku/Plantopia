# 🐛 Debug Guide - Plant Recommendation API

This guide explains how to use the console debugging features that have been added to help you monitor API requests and responses.

## 📊 What You'll See in Console

When you perform a plant search, you'll see detailed logging in the browser console organized into several groups:

### 1. **[SEARCH] Plant Search Debug**
- Shows the initial search parameters from the form
- Tracks each step of the search process
- Reports success/failure status

### 2. **[BUILD REQUEST] Form Data to API Request**
- Shows how form data is transformed into API request format
- Displays field mappings (e.g., "Full Sun" → "full_sun")
- Shows the final API request object that will be sent

### 3. **[PLANT API] Request Debug**
- Shows the exact HTTP request being made
- Includes URL, method, headers, and request body
- Displays the raw request object

### 4. **[PLANT API] Response Debug**
- Shows HTTP response status and headers
- Displays the complete response data from backend
- Shows number of recommendations received
- Shows detected suburb and climate zone

### 5. **[TRANSFORM] API Response to Plants**
- Shows how backend response is transformed to frontend format
- Details each plant transformation step by step
- Shows the final transformed plants array

## 🔍 How to Use

1. **Open Browser Developer Tools**
   - Chrome/Edge: Press `F12` or `Ctrl+Shift+I`
   - Firefox: Press `F12` or `Ctrl+Shift+I`
   - Safari: Press `Cmd+Opt+I`

2. **Go to Console Tab**
   - Click on the "Console" tab in developer tools

3. **Perform a Plant Search**
   - Fill out the plant recommendation form
   - Click "Search"
   - Watch the console for detailed logging

## 📋 Example Console Output

```
[SEARCH] Plant Search Debug
  [SEARCH] Initiated with parameters: {location: "Richmond, 3121 VIC", locationType: "Backyard", ...}
  [SEARCH] Step 1: Health check...
  [SEARCH] Health check passed: {message: "Plant Recommendation API is running"}

[BUILD REQUEST] Form Data to API Request
  [BUILD REQUEST] Input Form Data: {location: "Richmond, 3121 VIC", ...}
  [BUILD REQUEST] Extracted suburb: Richmond from location: Richmond, 3121 VIC
  [BUILD REQUEST] Field Mappings:
    - Location Type: Backyard -> backyard
    - Area Size: Medium (2-10m2) -> 6.0
    - Sunlight: Full Sun -> full_sun
    ...

[PLANT API] Request Debug
  [REQUEST] URL: http://localhost:8000/recommendations
  [REQUEST] Method: POST
  [REQUEST] Body: {"suburb":"Richmond","n":5,"user_preferences":{...}}

[PLANT API] Response Debug
  [RESPONSE] Status: 200
  [RESPONSE] Data: {recommendations: [...], suburb: "Richmond", climate_zone: "temperate"}
  [RESPONSE] Number of recommendations: 5
  [RESPONSE] Suburb detected: Richmond

[TRANSFORM] API Response to Plants
  [TRANSFORM] Plant 1: Tomato
  [TRANSFORM] Plant 2: Basil
  ...
  [TRANSFORM] All plants completed successfully!
```

## ❌ Error Debugging

If something goes wrong, you'll see error groups like:

```
[SEARCH] Error
  [SEARCH] Error occurred: Error: API request failed: 500 Internal Server Error
  [SEARCH] Error message: API request failed: 500 Internal Server Error
  [SEARCH] Error stack: Error: API request failed...

[PLANT API] Error Debug
  [ERROR] Details: Error: API request failed: 500 Internal Server Error
  [ERROR] Message: API request failed: 500 Internal Server Error
```

## 🎯 Common Issues to Look For

1. **Health Check Fails**: Backend server is not running
2. **Request Body Issues**: Form data not mapping correctly
3. **Response Errors**: Backend returning error status codes
4. **Transformation Errors**: Issues converting API response to frontend format

## 🧹 Disabling Debug Logging

To disable debug logging in production, you can:

1. **Comment out console statements** in:
   - `/frontend/src/services/api.ts`
   - `/frontend/src/views/RecommendationsView.vue`

2. **Or use environment variables** to conditionally enable logging:
   ```javascript
   if (import.meta.env.DEV) {
     console.log('[DEBUG]', ...);
   }
   ```

## 📝 Tips

- Use the browser's console filter to show only specific log types
- Collapse/expand console groups to focus on specific areas
- Copy console output to share with team members for debugging
- Check Network tab in developer tools for additional HTTP request details
