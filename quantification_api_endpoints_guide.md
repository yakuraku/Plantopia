# 🔧 Quantification API Endpoints Guide

## **Issue: "Method Not Allowed" Error** ❌

The frontend is getting `{"detail":"Method Not Allowed"}` because they're likely using the wrong endpoint URL or HTTP method.

## **Correct API Endpoints** ✅

Based on the code analysis, here are the **actual quantification API endpoints**:

### **1. Single Plant Quantification**
- **URL**: `POST /api/v1/quantify-plant` ⚠️ **NOT** `/api/v1/quantification`
- **Method**: `POST` (required)
- **Purpose**: Get detailed climate impact quantification for a specific plant

### **2. Batch Plant Quantification**
- **URL**: `POST /api/v1/batch-quantify`
- **Method**: `POST` (required)
- **Purpose**: Quantify multiple plants in a single request

### **3. Recommendations with Impact**
- **URL**: `POST /api/v1/recommendations-with-impact`
- **Method**: `POST` (required)
- **Purpose**: Get recommendations enhanced with quantification data

## **Complete API Configuration**

Based on the `.env` file and FastAPI configuration:

```javascript
// Frontend API Configuration
const API_BASE_URL = "http://localhost:8000";  // Local development
// OR for production: use your deployed API URL

const API_ENDPOINTS = {
  quantifyPlant: "/api/v1/quantify-plant",              // ← CORRECT ENDPOINT
  batchQuantify: "/api/v1/batch-quantify",
  recommendationsWithImpact: "/api/v1/recommendations-with-impact",
  recommendations: "/api/v1/recommendations",
  plants: "/api/v1/plants"
};
```

## **Frontend Implementation Examples**

### **1. Single Plant Quantification**

```javascript
// ✅ CORRECT Implementation
async function quantifyPlant(plantName, userPreferences, suburb = "Richmond") {
  const response = await fetch(`${API_BASE_URL}/api/v1/quantify-plant`, {
    method: 'POST',  // Must be POST
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      plant_name: plantName,
      suburb: suburb,
      plant_count: 1,
      user_preferences: {
        user_id: "user123",
        site: {
          location_type: "balcony",
          area_m2: 4.0,
          sun_exposure: "part_sun",
          wind_exposure: "moderate",
          containers: true,
          container_sizes: ["small", "medium"]
        },
        preferences: {
          goal: "mixed",
          edible_types: ["herbs", "leafy"],
          ornamental_types: ["flowers"],
          colors: ["purple", "white"],
          fragrant: true,
          maintainability: "low",
          watering: "medium",
          time_to_results: "quick",
          season_intent: "start_now",
          pollen_sensitive: false
        },
        practical: {
          budget: "medium",
          has_basic_tools: true,
          organic_only: false
        }
      }
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API Error: ${response.status} - ${error}`);
  }

  return await response.json();
}

// Usage Example
try {
  const result = await quantifyPlant("Basil", userPreferences);
  console.log("Quantification Result:", result);
} catch (error) {
  console.error("Quantification failed:", error.message);
}
```

### **2. Recommendations with Impact**

```javascript
// ✅ Get recommendations with quantified impact
async function getRecommendationsWithImpact(userPreferences, suburb = "Richmond") {
  const response = await fetch(`${API_BASE_URL}/api/v1/recommendations-with-impact`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      suburb: suburb,
      n: 6,  // Number of recommendations (1-9)
      user_preferences: userPreferences
    })
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`API Error: ${response.status} - ${error}`);
  }

  return await response.json();
}
```

## **Common Frontend Errors and Fixes**

### **❌ Wrong Endpoint (causes "Method Not Allowed")**
```javascript
// WRONG - This will return 405 Method Not Allowed
fetch('/api/v1/quantification', { method: 'POST' })

// CORRECT
fetch('/api/v1/quantify-plant', { method: 'POST' })
```

### **❌ Wrong HTTP Method**
```javascript
// WRONG - GET not allowed
fetch('/api/v1/quantify-plant', { method: 'GET' })

// CORRECT - Must use POST
fetch('/api/v1/quantify-plant', { method: 'POST' })
```

### **❌ Missing Content-Type Header**
```javascript
// WRONG - Missing headers
fetch('/api/v1/quantify-plant', {
  method: 'POST',
  body: JSON.stringify(data)
})

// CORRECT - Include Content-Type
fetch('/api/v1/quantify-plant', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
})
```

## **Expected Response Format**

### **Single Plant Quantification Response:**
```json
{
  "plant_name": "Basil",
  "scientific_name": "Ocimum basilicum",
  "plant_category": "herb",
  "quantified_impact": {
    "temperature_reduction_c": 0.8,
    "air_quality_points": 12,
    "co2_absorption_kg_year": 2.4,
    "water_processed_l_week": 15.6,
    "pollinator_support": "High",
    "edible_yield": "50g/week",
    "maintenance_time": "15mins/week",
    "water_requirement": "8L/week",
    "risk_badge": "Low Risk",
    "confidence_level": "High",
    "why_this_plant": "Excellent choice for container growing...",
    "community_impact_potential": "Moderate"
  },
  "suitability_score": {
    "total_score": 8.7,
    "breakdown": {
      "climate_fit": 9.2,
      "maintenance_match": 8.8,
      "space_efficiency": 8.1
    }
  },
  "suburb": "Richmond",
  "climate_zone": "temperate"
}
```

## **Error Handling**

```javascript
async function handleQuantificationAPI(plantName) {
  try {
    const result = await quantifyPlant(plantName, userPreferences);

    // Success - use the result
    displayQuantificationResults(result);

  } catch (error) {
    console.error('Quantification error:', error);

    if (error.message.includes('405')) {
      console.error('❌ Wrong endpoint or method. Use POST /api/v1/quantify-plant');
    } else if (error.message.includes('404')) {
      console.error('❌ Plant not found:', plantName);
    } else if (error.message.includes('422')) {
      console.error('❌ Invalid request data format');
    } else {
      console.error('❌ Server error or network issue');
    }

    // Show user-friendly error message
    showErrorMessage('Unable to get plant quantification. Please try again.');
  }
}
```

## **Testing the API**

### **Using curl (for testing):**
```bash
# Test the quantification endpoint
curl -X POST "http://localhost:8000/api/v1/quantify-plant" \
     -H "Content-Type: application/json" \
     -d '{
       "plant_name": "Basil",
       "suburb": "Richmond",
       "plant_count": 1,
       "user_preferences": {
         "site": {"location_type": "balcony", "area_m2": 2.0},
         "preferences": {"goal": "edible", "maintainability": "low"}
       }
     }'
```

### **Expected Success Response:**
- **Status Code**: `200 OK`
- **Content-Type**: `application/json`
- **Body**: Complete quantification data (see format above)

### **Common Error Responses:**
- **405 Method Not Allowed**: Wrong endpoint URL or HTTP method
- **404 Not Found**: Plant name not found in database
- **422 Unprocessable Entity**: Invalid request data format
- **500 Internal Server Error**: Server/database issue

## **CORS Configuration**

The API is configured with CORS for these origins:
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative dev port)
- `https://plantopia.vercel.app` (Production)

Make sure your frontend is running on one of these ports.

## **Quick Debugging Checklist**

When getting "Method Not Allowed":

1. ✅ **Check endpoint URL**: Use `/api/v1/quantify-plant` (not `/quantification`)
2. ✅ **Check HTTP method**: Use `POST` (not `GET`)
3. ✅ **Check Content-Type**: Include `'Content-Type': 'application/json'`
4. ✅ **Check request body**: Valid JSON with required fields
5. ✅ **Check server status**: Make sure API server is running on port 8000
6. ✅ **Check CORS**: Frontend must be on allowed origin

## **Summary**

**The main issue**: Frontend is likely using `/api/v1/quantification` instead of `/api/v1/quantify-plant`

**Quick fix**: Update frontend to use the correct endpoint:
```javascript
// Change this:
fetch('/api/v1/quantification', { method: 'POST' })

// To this:
fetch('/api/v1/quantify-plant', { method: 'POST' })
```

This should resolve the "Method Not Allowed" error immediately! 🚀