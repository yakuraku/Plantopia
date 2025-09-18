# Urban Heat Island (UHI) API - Frontend Implementation Guide

## Overview
The UHI API provides endpoints to visualize Melbourne's Urban Heat Island effect data from 2018. The data includes heat intensity measurements, vegetation coverage, and geographic boundaries for 323 Melbourne suburbs.

## Base URL
```
Development: http://localhost:8000/api/v1/uhi
Production: https://budgets-accepting-porcelain-austin.trycloudflare.com/api/v1/uhi
```

## Essential Endpoints for Heatmap

### 1. Get Suburb Boundaries (GeoJSON)
**Endpoint:** `GET /boundaries?simplified={boolean}`

Returns URLs to GeoJSON files hosted on Google Cloud Storage for direct fetching.

**Parameters:**
- `simplified` (boolean, default: true):
  - `true`: Returns URL for simplified boundaries (726KB) - recommended for initial load
  - `false`: Returns URL for full detail boundaries (8.8MB) - use for zoomed-in views

**Example Response:**
```json
{
  "url": "https://storage.googleapis.com/plantopia-images-1757656642/data/melbourne_suburbs_simplified.geojson",
  "size": "726KB",
  "description": "Simplified boundaries for fast loading"
}
```

**Frontend Usage:**
```javascript
// Step 1: Get the GeoJSON URL from our API
const response = await fetch('/api/v1/uhi/boundaries?simplified=true');
const { url } = await response.json();

// Step 2: Fetch the actual GeoJSON from Google Cloud Storage
const geoJSONData = await fetch(url).then(r => r.json());

// Step 3: Add to your map (Leaflet example)
L.geoJSON(geoJSONData, {
  style: feature => ({
    fillColor: getColorForHeatCategory(feature.properties.HEAT_CATEGORY),
    fillOpacity: 0.7,
    weight: 1,
    color: 'white'
  })
}).addTo(map);
```

### 2. Get Heat Data
**Endpoint:** `GET /data`

Returns complete heat intensity data for all 323 suburbs.

**Example Response:**
```json
{
  "metadata": {
    "dataset_name": "Melbourne Urban Heat Islands 2018",
    "total_suburbs": 323,
    "coordinate_system": "WGS84"
  },
  "heat_categories": {
    "extreme_heat": {
      "min": 12.0,
      "max": 999,
      "color": "#8B0000",
      "label": "Extreme Heat"
    },
    "high_heat": {
      "min": 8.0,
      "max": 11.9,
      "color": "#FF0000",
      "label": "High Heat"
    }
    // ... more categories
  },
  "suburbs": [
    {
      "id": "melbourne",
      "name": "Melbourne",
      "council": "Melbourne (C)",
      "coordinates": { "lat": -37.81, "lng": 144.96 },
      "heat": {
        "intensity": 7.26,
        "category": "Moderate Heat",
        "rank": 195
      },
      "vegetation": {
        "total": 6.9,
        "trees": 5.9,
        "shrubs": 0.4,
        "grass": 0.6
      }
    }
    // ... more suburbs
  ]
}
```

## Additional Endpoints

### 3. Get Metadata (for Legend)
**Endpoint:** `GET /metadata`

Returns heat categories with colors for map legend.

**Example Response:**
```json
{
  "heat_categories": {
    "extreme_heat": { "color": "#8B0000", "label": "Extreme Heat", "min": 12.0 },
    "high_heat": { "color": "#FF0000", "label": "High Heat", "min": 8.0 },
    "moderate_heat": { "color": "#FF8C00", "label": "Moderate Heat", "min": 4.0 },
    "low_heat": { "color": "#FFD700", "label": "Low Heat", "min": 0.0 },
    "cool": { "color": "#32CD32", "label": "Cool", "max": -0.1 }
  }
}
```

### 4. Get Single Suburb Details
**Endpoint:** `GET /suburb/{suburb_id}`

**Example:** `/suburb/melbourne`

Returns detailed data for a specific suburb (useful for popup/modal on click).

### 5. Search Suburbs
**Endpoint:** `GET /suburbs/search?q={query}&limit={number}`

**Example:** `/suburbs/search?q=melb&limit=5`

Returns suburbs matching the search query.

### 6. Get Hottest/Coolest Suburbs
**Endpoint:** `GET /suburbs/by-heat?category={category}&limit={number}`

**Parameters:**
- `category` (optional): Filter by heat category (e.g., "extreme_heat")
- `limit` (default: 10): Number of results

**Example:** `/suburbs/by-heat?limit=10` returns top 10 hottest suburbs

## Complete Implementation Example (Vue.js + Leaflet)

```vue
<template>
  <div id="heat-map" style="height: 600px;"></div>
</template>

<script>
import L from 'leaflet';

export default {
  data() {
    return {
      map: null,
      heatData: null,
      boundaries: null
    }
  },
  async mounted() {
    // Initialize map
    this.map = L.map('heat-map').setView([-37.8136, 144.9631], 10);

    // Add base tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(this.map);

    // Load data
    await this.loadHeatMap();
  },
  methods: {
    async loadHeatMap() {
      try {
        // 1. Get heat data
        const heatResponse = await fetch('/api/v1/uhi/data');
        this.heatData = await heatResponse.json();

        // 2. Get boundary URL
        const boundaryResponse = await fetch('/api/v1/uhi/boundaries?simplified=true');
        const { url } = await boundaryResponse.json();

        // 3. Fetch GeoJSON from GCS
        const geoJSON = await fetch(url).then(r => r.json());

        // 4. Create color mapping
        const heatCategories = this.heatData.heat_categories;

        // 5. Add GeoJSON layer with styling
        L.geoJSON(geoJSON, {
          style: (feature) => {
            const category = feature.properties.HEAT_CATEGORY;
            const categoryKey = category.toLowerCase().replace(' ', '_');
            return {
              fillColor: heatCategories[categoryKey]?.color || '#gray',
              fillOpacity: 0.7,
              weight: 1,
              color: 'white',
              dashArray: '0'
            };
          },
          onEachFeature: (feature, layer) => {
            // Add popup on click
            layer.on('click', () => {
              this.showSuburbDetails(feature.properties.SUBURB_NAME);
            });

            // Tooltip on hover
            layer.bindTooltip(
              `${feature.properties.SUBURB_NAME}<br>
               Heat: ${feature.properties.AVG_HEAT.toFixed(1)}°C`,
              { permanent: false, sticky: true }
            );
          }
        }).addTo(this.map);

        // 6. Add legend
        this.addLegend();

      } catch (error) {
        console.error('Error loading heatmap:', error);
      }
    },

    async showSuburbDetails(suburbName) {
      // Fetch detailed suburb data
      const suburbId = suburbName.toLowerCase().replace(/\s+/g, '_');
      const response = await fetch(`/api/v1/uhi/suburb/${suburbId}`);
      const data = await response.json();

      // Show in modal/popup
      console.log('Suburb details:', data);
    },

    addLegend() {
      const legend = L.control({ position: 'bottomright' });

      legend.onAdd = () => {
        const div = L.DomUtil.create('div', 'legend');
        const categories = this.heatData.heat_categories;

        div.innerHTML = '<h4>Heat Intensity</h4>';

        for (const [key, cat] of Object.entries(categories)) {
          div.innerHTML += `
            <div>
              <span style="background: ${cat.color};
                          width: 20px;
                          height: 20px;
                          display: inline-block;"></span>
              ${cat.label}
            </div>
          `;
        }

        return div;
      };

      legend.addTo(this.map);
    }
  }
}
</script>

<style>
.legend {
  background: white;
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
</style>
```

## Performance Tips

1. **Start with simplified boundaries** - Load the 726KB version first for instant map display
2. **Implement zoom-based loading** - Only load full detail when zoom > 12
3. **Cache the data** - Both boundary files and heat data are static (from 2018)
4. **Use CDN URLs directly** - The boundaries are served from Google Cloud Storage for fast global delivery

## Color Scheme Reference
```javascript
const HEAT_COLORS = {
  extreme_heat: '#8B0000',  // Dark red (≥12°C)
  high_heat: '#FF0000',     // Red (8-11.9°C)
  moderate_heat: '#FF8C00', // Orange (4-7.9°C)
  low_heat: '#FFD700',      // Gold (0-3.9°C)
  cool: '#32CD32'           // Green (<0°C)
};
```

## Common Use Cases

### Display Top 5 Hottest Suburbs
```javascript
const response = await fetch('/api/v1/uhi/suburbs/by-heat?limit=5');
const { suburbs } = await response.json();
// Display in a list or table
```

### Search Functionality
```javascript
async function searchSuburb(query) {
  const response = await fetch(`/api/v1/uhi/suburbs/search?q=${query}&limit=10`);
  const { suburbs } = await response.json();
  return suburbs;
}
```

### Switch Between Simplified and Full Detail
```javascript
let currentZoom = map.getZoom();

map.on('zoomend', async () => {
  const newZoom = map.getZoom();

  if (currentZoom < 12 && newZoom >= 12) {
    // User zoomed in - load full detail
    await loadBoundaries(false);
  } else if (currentZoom >= 12 && newZoom < 12) {
    // User zoomed out - load simplified
    await loadBoundaries(true);
  }

  currentZoom = newZoom;
});
```

## Error Handling
All endpoints return standard HTTP status codes:
- `200`: Success
- `404`: Suburb or data not found
- `500`: Server error

Handle errors appropriately:
```javascript
try {
  const response = await fetch('/api/v1/uhi/data');
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  const data = await response.json();
} catch (error) {
  console.error('Failed to load heat data:', error);
  // Show user-friendly error message
}
```

## Questions or Issues?
The data is from 2018 and won't change. All endpoints are cached for 24 hours to improve performance. The backend is optimized for the GCP e2-micro instance by serving large files from Google Cloud Storage instead of memory.