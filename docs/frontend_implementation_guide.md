# Frontend Implementation Guide - Plantopia API

This comprehensive guide provides documentation for all API endpoints available in the Plantopia backend, including plant data, companion planting, markdown content, recommendations, and more.

## Table of Contents

1. [Base Configuration](#base-configuration)
2. [Plants API](#plants-api)
3. [Companion Planting API](#companion-planting-api)
4. [Recommendations API](#recommendations-api)
5. [Markdown Content API](#markdown-content-api)
6. [Climate & Environmental Data API](#climate--environmental-data-api)
7. [Error Handling](#error-handling)
8. [Frontend Implementation Examples](#frontend-implementation-examples)

---

## Base Configuration

**API Base URL:** `http://localhost:8000/api/v1` (adjust for production)
**Content Type:** `application/json`
**Authentication:** None required (currently)

---

## Plants API

The Plants API provides access to the complete database of 2,117+ plants (flowers, herbs, and vegetables) with detailed information about growing requirements, characteristics, and companion planting data.

### Get All Plants

**Endpoint:** `GET /plants`

**Description:** Retrieve all plants from the database with complete information including companion planting data.

**Response:**
```json
{
  "plants": [
    {
      "id": 1,
      "plant_name": "Basil",
      "scientific_name": "Ocimum basilicum",
      "plant_category": "herb",
      "water_requirements": "Regular watering",
      "sunlight_requirements": "Full sun",
      "soil_type": "Well-drained, fertile soil",
      "growth_time": "60-90 days",
      "maintenance_level": "Easy",
      "description": "Popular culinary herb...",
      "sun_need": "full_sun",
      "indoor_ok": true,
      "container_ok": true,
      "edible": true,
      "time_to_maturity_days": 75,
      "beneficial_companions": "Tomatoes, Peppers, Oregano",
      "harmful_companions": "Rue, Sage",
      "neutral_companions": "Lettuce, Spinach, Beans",
      "media": {
        "image_url": "https://storage.googleapis.com/.../basil_1.jpg",
        "image_path": "herb_plant_images/Basil_Ocimum basilicum/...",
        "image_base64": "base64encodedstring...",
        "has_image": true
      },
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-09-04T14:20:00"
    }
  ],
  "total_count": 2117
}
```

**Frontend Usage:**
```javascript
// Fetch all plants
const fetchAllPlants = async () => {
  try {
    const response = await fetch('/api/v1/plants');
    const data = await response.json();
    return data.plants;
  } catch (error) {
    console.error('Error fetching plants:', error);
    throw error;
  }
};
```

### Get Paginated Plants

**Endpoint:** `GET /plants/paginated`

**Query Parameters:**
- `page` (integer, default: 1): Page number (1-based)
- `limit` (integer, default: 12, max: 100): Items per page
- `category` (string, optional): Filter by category (`flower`, `herb`, `vegetable`)
- `search` (string, optional): Search by plant name, scientific name, or description

**Description:** Get paginated plants with optional filtering and search. Recommended for better performance with large datasets.

**Response:**
```json
{
  "plants": [
    {
      "id": 1,
      "plant_name": "Basil",
      "scientific_name": "Ocimum basilicum",
      "plant_category": "herb",
      "beneficial_companions": "Tomatoes, Peppers, Oregano",
      "harmful_companions": "Rue, Sage",
      "neutral_companions": "Lettuce, Spinach, Beans",
      "media": {
        "image_url": "https://storage.googleapis.com/.../basil_1.jpg",
        "has_image": true
      }
    }
  ],
  "page": 1,
  "limit": 12,
  "total": 2117,
  "total_pages": 177,
  "has_next": true,
  "has_previous": false
}
```

**Frontend Usage:**
```javascript
// Fetch paginated plants with filters
const fetchPaginatedPlants = async (page = 1, category = null, searchTerm = null) => {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: '12'
    });

    if (category) params.append('category', category);
    if (searchTerm) params.append('search', searchTerm);

    const response = await fetch(`/api/v1/plants/paginated?${params}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching paginated plants:', error);
    throw error;
  }
};

// Usage examples
const herbsPage1 = await fetchPaginatedPlants(1, 'herb');
const searchResults = await fetchPaginatedPlants(1, null, 'tomato');
const flowersPage2 = await fetchPaginatedPlants(2, 'flower');
```

### Get Plant Image URLs

**Endpoint:** `GET /plants/{plant_id}/image-url`

**Description:** Get the primary Google Cloud Storage image URL for a specific plant.

**Response:**
```json
{
  "image_url": "https://storage.googleapis.com/plantopia-images/herb_plant_images/Basil_Ocimum basilicum/Basil_Ocimum basilicum_1.jpg"
}
```

**Frontend Usage:**
```javascript
const getPlantImage = async (plantId) => {
  const response = await fetch(`/api/v1/plants/${plantId}/image-url`);
  const data = await response.json();
  return data.image_url;
};
```

### Get All Plant Images

**Endpoint:** `GET /plants/{plant_id}/all-images`

**Description:** Get all available GCS image URLs for a plant (typically 2-4 images per plant).

**Response:**
```json
{
  "image_urls": [
    "https://storage.googleapis.com/.../Basil_1.jpg",
    "https://storage.googleapis.com/.../Basil_2.jpg",
    "https://storage.googleapis.com/.../Basil_3.jpg"
  ]
}
```

**Frontend Usage:**
```javascript
const getAllPlantImages = async (plantId) => {
  const response = await fetch(`/api/v1/plants/${plantId}/all-images`);
  const data = await response.json();
  return data.image_urls;
};
```

---

## Companion Planting API

The Companion Planting API provides detailed information about which plants grow well together, which plants should be avoided, and neutral companions. This data is sourced from the three CSV files with companion data.

### Get Companion Data for a Plant

**Endpoint:** `GET /plants/{plant_id}/companions`

**Description:** Get detailed companion planting information for a specific plant. Returns lists of beneficial, harmful, and neutral companion plants.

**Response:**
```json
{
  "plant_id": 123,
  "plant_name": "Tomatoes",
  "scientific_name": "Solanum lycopersicum",
  "plant_category": "vegetable",
  "companion_planting": {
    "beneficial_companions": [
      "Basil",
      "Carrots",
      "Onions",
      "Parsley",
      "Marigold",
      "Nasturtium"
    ],
    "harmful_companions": [
      "Cabbage",
      "Fennel",
      "Corn",
      "Kohlrabi"
    ],
    "neutral_companions": [
      "Lettuce",
      "Spinach",
      "Radish",
      "Beans"
    ]
  }
}
```

**Companion Data Explanation:**
- **Beneficial Companions**: Plants that grow well together and provide mutual benefits (pest control, nutrient sharing, improved growth)
- **Harmful Companions**: Plants that should NOT be planted together (compete for nutrients, attract same pests, inhibit growth)
- **Neutral Companions**: Compatible plants that can coexist without significant positive or negative effects

**Frontend Usage:**
```javascript
// Fetch companion planting data
const getCompanionPlanting = async (plantId) => {
  try {
    const response = await fetch(`/api/v1/plants/${plantId}/companions`);
    if (!response.ok) {
      throw new Error('Failed to fetch companion data');
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching companion planting data:', error);
    throw error;
  }
};

// Usage example
const tomatoCompanions = await getCompanionPlanting(123);
console.log('Plant with tomatoes:', tomatoCompanions.companion_planting.beneficial_companions);
console.log('Avoid planting with tomatoes:', tomatoCompanions.companion_planting.harmful_companions);
```

### React Component Example - Companion Planting Display

```jsx
import React, { useState, useEffect } from 'react';

const CompanionPlantingCard = ({ plantId }) => {
  const [companionData, setCompanionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCompanions = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/v1/plants/${plantId}/companions`);
        if (!response.ok) throw new Error('Plant not found');
        const data = await response.json();
        setCompanionData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (plantId) fetchCompanions();
  }, [plantId]);

  if (loading) return <div className="loading">Loading companion data...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!companionData) return null;

  const { plant_name, companion_planting } = companionData;

  return (
    <div className="companion-planting-card">
      <h2>Companion Planting Guide for {plant_name}</h2>

      {/* Beneficial Companions */}
      <div className="companion-section beneficial">
        <h3>✅ Good Companions</h3>
        <p className="description">Plant these together for mutual benefits</p>
        <ul className="companion-list">
          {companion_planting.beneficial_companions.length > 0 ? (
            companion_planting.beneficial_companions.map((plant, index) => (
              <li key={index} className="companion-item good">
                🌱 {plant}
              </li>
            ))
          ) : (
            <li className="no-data">No beneficial companions listed</li>
          )}
        </ul>
      </div>

      {/* Harmful Companions */}
      <div className="companion-section harmful">
        <h3>❌ Avoid These Plants</h3>
        <p className="description">Keep these plants away from each other</p>
        <ul className="companion-list">
          {companion_planting.harmful_companions.length > 0 ? (
            companion_planting.harmful_companions.map((plant, index) => (
              <li key={index} className="companion-item bad">
                🚫 {plant}
              </li>
            ))
          ) : (
            <li className="no-data">No harmful companions listed</li>
          )}
        </ul>
      </div>

      {/* Neutral Companions */}
      <div className="companion-section neutral">
        <h3>➖ Neutral Companions</h3>
        <p className="description">Can be planted together without issues</p>
        <ul className="companion-list">
          {companion_planting.neutral_companions.length > 0 ? (
            companion_planting.neutral_companions.map((plant, index) => (
              <li key={index} className="companion-item neutral">
                ⚪ {plant}
              </li>
            ))
          ) : (
            <li className="no-data">No neutral companions listed</li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default CompanionPlantingCard;
```

### Vue.js Component Example - Companion Planting

```vue
<template>
  <div class="companion-planting-widget">
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="companionData" class="companion-content">
      <h3>Companion Planting: {{ companionData.plant_name }}</h3>

      <!-- Beneficial -->
      <div class="companion-group">
        <h4 class="beneficial-header">✅ Plant With:</h4>
        <div class="plant-tags">
          <span
            v-for="plant in companionData.companion_planting.beneficial_companions"
            :key="plant"
            class="tag beneficial"
          >
            {{ plant }}
          </span>
          <span v-if="companionData.companion_planting.beneficial_companions.length === 0" class="no-data">
            None listed
          </span>
        </div>
      </div>

      <!-- Harmful -->
      <div class="companion-group">
        <h4 class="harmful-header">❌ Keep Away From:</h4>
        <div class="plant-tags">
          <span
            v-for="plant in companionData.companion_planting.harmful_companions"
            :key="plant"
            class="tag harmful"
          >
            {{ plant }}
          </span>
          <span v-if="companionData.companion_planting.harmful_companions.length === 0" class="no-data">
            None listed
          </span>
        </div>
      </div>

      <!-- Neutral -->
      <div class="companion-group">
        <h4 class="neutral-header">➖ Neutral:</h4>
        <div class="plant-tags">
          <span
            v-for="plant in companionData.companion_planting.neutral_companions"
            :key="plant"
            class="tag neutral"
          >
            {{ plant }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CompanionPlantingWidget',
  props: {
    plantId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      companionData: null,
      loading: false,
      error: null
    };
  },
  watch: {
    plantId: {
      immediate: true,
      handler(newPlantId) {
        if (newPlantId) {
          this.fetchCompanionData(newPlantId);
        }
      }
    }
  },
  methods: {
    async fetchCompanionData(plantId) {
      this.loading = true;
      this.error = null;

      try {
        const response = await fetch(`/api/v1/plants/${plantId}/companions`);
        if (!response.ok) {
          throw new Error('Failed to fetch companion data');
        }
        this.companionData = await response.json();
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.companion-planting-widget {
  padding: 1rem;
  border-radius: 8px;
  background: #f9f9f9;
}

.companion-group {
  margin: 1rem 0;
}

.plant-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.tag {
  padding: 0.25rem 0.75rem;
  border-radius: 16px;
  font-size: 0.875rem;
  font-weight: 500;
}

.tag.beneficial {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.tag.harmful {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.tag.neutral {
  background-color: #e2e3e5;
  color: #383d41;
  border: 1px solid #d6d8db;
}

.no-data {
  color: #6c757d;
  font-style: italic;
}
</style>
```

### Companion Data in Main Plant Responses

**Important:** The companion data fields are now automatically included in all plant API responses:

- `GET /plants` - Includes companion data for all plants
- `GET /plants/paginated` - Includes companion data in paginated results
- `GET /plants/{plant_id}/image-url` - Basic endpoint, use `/companions` for detailed companion data

**Plant Object Structure with Companion Data:**
```typescript
interface Plant {
  id: number;
  plant_name: string;
  scientific_name: string;
  plant_category: 'flower' | 'herb' | 'vegetable';
  // ... other plant fields ...

  // Companion planting data (comma-separated strings in raw format)
  beneficial_companions: string;  // "Basil, Carrots, Onions, Marigold"
  harmful_companions: string;     // "Cabbage, Fennel"
  neutral_companions: string;     // "Lettuce, Spinach, Radish"
}
```

**Parsing Companion Data from Plant Response:**
```javascript
// Helper function to parse companion strings
const parseCompanions = (companionStr) => {
  if (!companionStr || companionStr.trim() === '') return [];
  return companionStr.split(',').map(c => c.trim()).filter(c => c);
};

// Usage with plant data
const plant = await fetchPlantById(123);
const beneficialCompanions = parseCompanions(plant.beneficial_companions);
const harmfulCompanions = parseCompanions(plant.harmful_companions);
const neutralCompanions = parseCompanions(plant.neutral_companions);

console.log('Beneficial:', beneficialCompanions);  // ['Basil', 'Carrots', 'Onions']
console.log('Harmful:', harmfulCompanions);        // ['Cabbage', 'Fennel']
console.log('Neutral:', neutralCompanions);        // ['Lettuce', 'Spinach']
```

---

## Recommendations API

### Get Personalized Plant Recommendations

**Endpoint:** `POST /recommendations`

**Description:** Get personalized plant recommendations based on user preferences and location.

**Request Body:**
```json
{
  "suburb": "Richmond",
  "n": 5,
  "user_preferences": {
    "sun_exposure": "full_sun",
    "maintenance_level": "easy",
    "plant_goals": ["edible", "flowers"],
    "time_to_results": "quick"
  }
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "plant_name": "Basil",
      "score": 0.92,
      "category": "herb",
      "why": "Perfect match for full sun, easy maintenance, edible herb with quick maturity",
      "media": {
        "image_url": "https://storage.googleapis.com/..."
      },
      "beneficial_companions": "Tomatoes, Peppers, Oregano",
      "harmful_companions": "Rue, Sage"
    }
  ]
}
```

---

## Markdown Content API

The Markdown Content API provides access to 465+ educational articles organized into 10 categories covering various gardening topics.

### Available Categories

| Category | Endpoint Slug | File Count | Description |
|----------|---------------|------------|-------------|
| Beneficial Insects | `beneficial-insects` | 6 | Attracting helpful garden insects |
| Companion Planting | `companion-planting` | 4 | Plant pairing strategies |
| Composting | `composting` | 8 | Composting techniques and tips |
| Craft | `craft` | 8 | DIY garden projects and crafts |
| Fertiliser Soil | `fertiliser-soil` | 22 | Soil management and fertilization |
| Flowers | `flowers` | 36 | Flower growing guides |
| Grow Guide | `grow-guide` | 255 | Comprehensive growing instructions |
| Herbs | `herbs` | 12 | Herb cultivation guides |
| Informational | `informational` | 69 | General gardening information |
| Pests Diseases | `pests-diseases` | 45 | Pest and disease management |

### Get All Categories

**Endpoint:** `GET /markdown/categories`

**Response:**
```json
{
  "categories": [
    {
      "name": "Companion Planting",
      "slug": "companion-planting",
      "file_count": 4
    }
  ],
  "total_categories": 10
}
```

### Get Category Content

**Endpoint:** `GET /markdown/category/{category_slug}`

**Response:**
```json
{
  "category": "Companion Planting",
  "files": [
    {
      "filename": "Companion Planting Guide.md",
      "title": "Companion Planting Guide",
      "content": "# Companion Planting Guide\n\n...",
      "file_size": 4532,
      "file_path": "Companion Planting/Companion Planting Guide.md"
    }
  ]
}
```

---

## Climate & Environmental Data API

### Get Climate Data for Suburb

**Endpoint:** `GET /climate/{suburb_name}`

**Description:** Get current climate data including temperature, UV index, air quality for a specific suburb.

**Response:**
```json
{
  "suburb": "Richmond",
  "temperature_current": 24.5,
  "uv_index": 7.2,
  "air_quality_index": 42,
  "rainfall": 0.0
}
```

---

## Error Handling

### Common Error Responses

**404 - Not Found:**
```json
{
  "detail": "Plant not found"
}
```

**400 - Bad Request:**
```json
{
  "detail": "Invalid category. Must be one of: flower, herb, vegetable"
}
```

**500 - Server Error:**
```json
{
  "detail": "Error loading plants: [error details]"
}
```

### Frontend Error Handling Example

```javascript
const apiRequest = async (url, options = {}) => {
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

// Usage
try {
  const companions = await apiRequest('/api/v1/plants/123/companions');
  console.log(companions);
} catch (error) {
  // Handle error in UI
  showErrorMessage(error.message);
}
```

---

## Frontend Implementation Examples

### Complete Plant Detail Component with Companion Planting

```jsx
import React, { useState, useEffect } from 'react';

const PlantDetailPage = ({ plantId }) => {
  const [plant, setPlant] = useState(null);
  const [companions, setCompanions] = useState(null);
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPlantData = async () => {
      try {
        setLoading(true);

        // Fetch plant details, companions, and images in parallel
        const [plantRes, companionsRes, imagesRes] = await Promise.all([
          fetch(`/api/v1/plants/paginated?page=1&limit=1`), // Or specific plant endpoint
          fetch(`/api/v1/plants/${plantId}/companions`),
          fetch(`/api/v1/plants/${plantId}/all-images`)
        ]);

        const plantData = await plantRes.json();
        const companionsData = await companionsRes.json();
        const imagesData = await imagesRes.json();

        setPlant(plantData.plants[0]);
        setCompanions(companionsData);
        setImages(imagesData.image_urls);
      } catch (error) {
        console.error('Error loading plant data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPlantData();
  }, [plantId]);

  if (loading) return <div>Loading...</div>;
  if (!plant) return <div>Plant not found</div>;

  return (
    <div className="plant-detail-page">
      {/* Image Gallery */}
      <div className="image-gallery">
        {images.map((url, index) => (
          <img key={index} src={url} alt={`${plant.plant_name} ${index + 1}`} />
        ))}
      </div>

      {/* Plant Info */}
      <div className="plant-info">
        <h1>{plant.plant_name}</h1>
        <p className="scientific-name">{plant.scientific_name}</p>
        <span className="category-badge">{plant.plant_category}</span>

        <div className="growing-info">
          <p><strong>Sun:</strong> {plant.sunlight_requirements}</p>
          <p><strong>Water:</strong> {plant.water_requirements}</p>
          <p><strong>Maintenance:</strong> {plant.maintenance_level}</p>
          <p><strong>Days to Maturity:</strong> {plant.time_to_maturity_days}</p>
        </div>

        <p className="description">{plant.description}</p>
      </div>

      {/* Companion Planting Section */}
      {companions && (
        <div className="companion-planting-section">
          <h2>Companion Planting Guide</h2>

          <div className="companions-grid">
            <div className="companion-box good">
              <h3>✅ Plant Together</h3>
              <ul>
                {companions.companion_planting.beneficial_companions.map((comp, i) => (
                  <li key={i}>{comp}</li>
                ))}
              </ul>
            </div>

            <div className="companion-box bad">
              <h3>❌ Keep Apart</h3>
              <ul>
                {companions.companion_planting.harmful_companions.map((comp, i) => (
                  <li key={i}>{comp}</li>
                ))}
              </ul>
            </div>

            <div className="companion-box neutral">
              <h3>➖ Neutral</h3>
              <ul>
                {companions.companion_planting.neutral_companions.map((comp, i) => (
                  <li key={i}>{comp}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlantDetailPage;
```

### Garden Planner with Companion Validation

```javascript
class GardenPlanner {
  constructor() {
    this.selectedPlants = [];
    this.companionDataCache = new Map();
  }

  async addPlant(plantId) {
    // Get plant companion data
    const companions = await this.getCompanionData(plantId);

    // Check compatibility with existing plants
    const conflicts = this.checkCompatibility(companions);

    if (conflicts.length > 0) {
      return {
        success: false,
        message: `Warning: ${companions.plant_name} conflicts with: ${conflicts.join(', ')}`,
        conflicts: conflicts
      };
    }

    this.selectedPlants.push(plantId);
    return {
      success: true,
      message: `${companions.plant_name} added to garden plan`
    };
  }

  async getCompanionData(plantId) {
    if (this.companionDataCache.has(plantId)) {
      return this.companionDataCache.get(plantId);
    }

    const response = await fetch(`/api/v1/plants/${plantId}/companions`);
    const data = await response.json();
    this.companionDataCache.set(plantId, data);
    return data;
  }

  checkCompatibility(newPlantCompanions) {
    const conflicts = [];
    const newPlantName = newPlantCompanions.plant_name;
    const harmfulToNew = newPlantCompanions.companion_planting.harmful_companions;

    for (const existingPlantId of this.selectedPlants) {
      const existingCompanions = this.companionDataCache.get(existingPlantId);

      if (!existingCompanions) continue;

      const existingPlantName = existingCompanions.plant_name;

      // Check if new plant is harmful to existing plant
      if (existingCompanions.companion_planting.harmful_companions.includes(newPlantName)) {
        conflicts.push(existingPlantName);
      }

      // Check if existing plant is harmful to new plant
      if (harmfulToNew.includes(existingPlantName)) {
        conflicts.push(existingPlantName);
      }
    }

    return [...new Set(conflicts)]; // Remove duplicates
  }

  getSuggestions(plantId) {
    const companions = this.companionDataCache.get(plantId);
    if (!companions) return [];

    return companions.companion_planting.beneficial_companions;
  }
}

// Usage
const planner = new GardenPlanner();

const result1 = await planner.addPlant(123); // Tomatoes
console.log(result1); // { success: true, message: "Tomatoes added..." }

const result2 = await planner.addPlant(456); // Basil (good companion)
console.log(result2); // { success: true, message: "Basil added..." }

const result3 = await planner.addPlant(789); // Cabbage (bad companion)
console.log(result3); // { success: false, conflicts: ['Tomatoes'], ... }

// Get suggestions for companion plants
const suggestions = planner.getSuggestions(123);
console.log('Good companions for tomatoes:', suggestions);
```

---

## Performance & Best Practices

### 1. Use Pagination for Plant Lists

```javascript
// ✅ Good - Use paginated endpoint
const plants = await fetch('/api/v1/plants/paginated?page=1&limit=20');

// ❌ Avoid - Fetching all 2117 plants at once
const allPlants = await fetch('/api/v1/plants');
```

### 2. Cache Companion Data

```javascript
const companionCache = new Map();

const getCachedCompanions = async (plantId) => {
  if (companionCache.has(plantId)) {
    return companionCache.get(plantId);
  }

  const data = await fetch(`/api/v1/plants/${plantId}/companions`).then(r => r.json());
  companionCache.set(plantId, data);
  return data;
};
```

### 3. Batch Requests When Possible

```javascript
// Fetch multiple resources in parallel
const fetchPlantDetails = async (plantId) => {
  const [plant, companions, images] = await Promise.all([
    fetch(`/api/v1/plants/${plantId}`).then(r => r.json()),
    fetch(`/api/v1/plants/${plantId}/companions`).then(r => r.json()),
    fetch(`/api/v1/plants/${plantId}/all-images`).then(r => r.json())
  ]);

  return { plant, companions, images };
};
```

---

## Integration Checklist

### Companion Planting Features
- [ ] Display companion data on plant detail pages
- [ ] Create companion planting visualization/widget
- [ ] Implement garden planner with compatibility checking
- [ ] Add companion plant suggestions based on selected plants
- [ ] Show warnings for incompatible plant combinations
- [ ] Create companion planting educational content section
- [ ] Add search/filter by companion compatibility

### General Integration
- [ ] Set up API base URL configuration
- [ ] Implement error handling and loading states
- [ ] Add pagination for plant lists
- [ ] Set up image lazy loading
- [ ] Implement caching for frequently accessed data
- [ ] Test all API endpoints
- [ ] Add accessibility features
- [ ] Responsive design for all screen sizes

---

## Support & Documentation

- **Backend API Code:** `/app/api/endpoints/plants.py`
- **Database Models:** `/app/models/database.py`
- **Plant Service:** `/app/services/plant_service.py`
- **CSV Data:** `/data/csv/` (flower_plants_data.csv, herbs_plants_data.csv, vegetable_plants_data.csv)

For questions about the API or issues with companion data, contact the backend development team.

---

**Last Updated:** December 2024
**API Version:** v1
**Total Plants:** 2,117+ (flowers, herbs, vegetables)
**Total Markdown Files:** 465+ across 10 categories
**New Features:** Companion Planting Data (beneficial_companions, harmful_companions, neutral_companions)
