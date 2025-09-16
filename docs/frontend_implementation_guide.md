# Frontend Implementation Guide - Climate Action Quantification

## Overview

This guide provides frontend developers with everything needed to implement the Climate Action Quantification feature in the Plantopia Vue.js application. The feature adds environmental impact metrics to plant recommendations, helping users understand the real-world climate benefits of their gardening choices.

## Quick Start

### 1. API Endpoints Available

The backend provides these new endpoints for quantification:

```typescript
// Base URL: http://localhost:8000/api/v1 (development) or /api/v1 (production)

POST /quantify-plant              // Quantify a specific plant
POST /batch-quantify             // Quantify multiple plants
POST /recommendations-with-impact // Enhanced recommendations with climate data
GET  /quantification-info        // Framework documentation
```

### 2. Key Components to Create

1. **ImpactCard.vue** - Display quantified impact metrics
2. **EnhancedPlantCard.vue** - Plant card with impact preview
3. **QuantificationService.ts** - API integration service
4. **ImpactMetrics types** - TypeScript interfaces

## TypeScript Interfaces

### Core Data Types

```typescript
// File: src/types/quantification.ts

export interface QuantifiedImpact {
  temperature_reduction_c: number
  air_quality_points: number
  co2_absorption_kg_year: number
  water_processed_l_week: number
  pollinator_support: 'Minimal' | 'Low' | 'Medium' | 'High'
  edible_yield?: string  // e.g., "80g/week after day 45"
  maintenance_time: string  // e.g., "8mins/week"
  water_requirement: string  // e.g., "4.5L/week"
  risk_badge: 'low' | 'medium' | 'high'
  confidence_level: string  // e.g., "High (87%)"
  why_this_plant: string
  community_impact_potential?: string
}

export interface SuitabilityScore {
  total_score: number  // 0-100
  breakdown: {
    [key: string]: number  // Individual factor scores
  }
}

export interface PlantQuantificationResponse {
  plant_name: string
  scientific_name?: string
  plant_category: string
  quantified_impact: QuantifiedImpact
  suitability_score: SuitabilityScore
  suburb: string
  climate_zone: string
  plant_count: number
}

export interface PlantQuantificationRequest {
  plant_name: string
  suburb: string
  plant_count: number
  user_preferences: {
    site: {
      location_type: string
      area_m2: number
      sun_exposure: string
      wind_exposure: string
      containers: boolean
      container_sizes?: string[]
    }
    preferences: {
      goal: string
      maintainability: string
      watering: string
      time_to_results: string
      season_intent: string
    }
  }
}
```

### Enhanced Plant Interface

```typescript
// File: src/types/plant.ts (extend existing Plant interface)

export interface Plant {
  // ... existing fields
  quantified_impact?: QuantifiedImpact  // Optional quantified impact data
  suitability_score?: number           // Optional suitability score
}
```

## API Service Integration

### Quantification Service

```typescript
// File: src/services/quantificationService.ts

import type {
  PlantQuantificationRequest,
  PlantQuantificationResponse,
  QuantifiedImpact
} from '@/types/quantification'

class QuantificationApiService {
  private baseUrl: string

  constructor() {
    this.baseUrl = process.env.NODE_ENV === 'production'
      ? '/api/v1'
      : 'http://localhost:8000/api/v1'
  }

  /**
   * Quantify climate impact for a single plant
   */
  async quantifyPlant(request: PlantQuantificationRequest): Promise<PlantQuantificationResponse> {
    const response = await fetch(`${this.baseUrl}/quantify-plant`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    })

    if (!response.ok) {
      throw new Error(`Quantification failed: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Quantify multiple plants in batch
   */
  async batchQuantifyPlants(requests: PlantQuantificationRequest[]): Promise<PlantQuantificationResponse[]> {
    if (requests.length > 20) {
      throw new Error('Maximum 20 plants can be quantified in batch')
    }

    const response = await fetch(`${this.baseUrl}/batch-quantify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requests)
    })

    if (!response.ok) {
      throw new Error(`Batch quantification failed: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Get enhanced recommendations with quantified impact
   */
  async getRecommendationsWithImpact(request: any): Promise<any> {
    const response = await fetch(`${this.baseUrl}/recommendations-with-impact`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    })

    if (!response.ok) {
      throw new Error(`Enhanced recommendations failed: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * Get quantification framework information
   */
  async getQuantificationInfo(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/quantification-info`)

    if (!response.ok) {
      throw new Error(`Failed to fetch quantification info: ${response.statusText}`)
    }

    return response.json()
  }
}

export const quantificationService = new QuantificationApiService()
```

## Vue Components

### 1. ImpactCard Component

```vue
<!-- File: src/components/ImpactCard.vue -->
<template>
  <div class="impact-card">
    <div class="impact-header">
      <h4 class="impact-title">Climate Impact</h4>
      <div class="suitability-score" v-if="suitabilityScore">
        {{ Math.round(suitabilityScore) }}/100
      </div>
    </div>

    <div class="impact-metrics">
      <!-- Cooling Effect -->
      <div class="metric-item cooling">
        <div class="metric-icon">🌡️</div>
        <div class="metric-content">
          <div class="metric-value">~{{ impact.temperature_reduction_c }}°C</div>
          <div class="metric-label">Cooling nearby</div>
        </div>
      </div>

      <!-- Air Quality -->
      <div class="metric-item air-quality">
        <div class="metric-icon">💨</div>
        <div class="metric-content">
          <div class="metric-value">+{{ impact.air_quality_points }}</div>
          <div class="metric-label">AQ points</div>
        </div>
      </div>

      <!-- CO2 Absorption -->
      <div class="metric-item co2">
        <div class="metric-icon">🌱</div>
        <div class="metric-content">
          <div class="metric-value">{{ impact.co2_absorption_kg_year }}kg/yr</div>
          <div class="metric-label">CO₂ absorbed</div>
        </div>
      </div>

      <!-- Water Processing -->
      <div class="metric-item water">
        <div class="metric-icon">💧</div>
        <div class="metric-content">
          <div class="metric-value">{{ impact.water_processed_l_week }}L/wk</div>
          <div class="metric-label">Water cycled</div>
        </div>
      </div>

      <!-- Pollinator Support -->
      <div class="metric-item pollinator">
        <div class="metric-icon">🦋</div>
        <div class="metric-content">
          <div class="metric-value">{{ impact.pollinator_support }}</div>
          <div class="metric-label">Pollinator support</div>
        </div>
      </div>

      <!-- Edible Yield (if applicable) -->
      <div class="metric-item edible" v-if="impact.edible_yield">
        <div class="metric-icon">🍃</div>
        <div class="metric-content">
          <div class="metric-value">{{ formatEdibleYield(impact.edible_yield) }}</div>
          <div class="metric-label">Edible yield</div>
        </div>
      </div>
    </div>

    <div class="impact-footer">
      <!-- Requirements -->
      <div class="requirements">
        <div class="req-item">
          <span class="req-label">Maintenance:</span>
          <span class="req-value">{{ impact.maintenance_time }}</span>
        </div>
        <div class="req-item">
          <span class="req-label">Water:</span>
          <span class="req-value">{{ impact.water_requirement }}</span>
        </div>
      </div>

      <!-- Risk & Confidence -->
      <div class="badges">
        <div class="risk-badge" :class="`risk-${impact.risk_badge}`">
          Risk: {{ impact.risk_badge }}
        </div>
        <div class="confidence-badge">
          {{ impact.confidence_level }}
        </div>
      </div>

      <!-- Why This Plant -->
      <div class="why-plant">
        <strong>{{ impact.why_this_plant }}</strong>
      </div>

      <!-- Community Impact (if available) -->
      <div class="community-impact" v-if="impact.community_impact_potential">
        <p class="community-text">{{ impact.community_impact_potential }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { QuantifiedImpact } from '@/types/quantification'

defineProps<{
  impact: QuantifiedImpact
  suitabilityScore?: number
}>()

function formatEdibleYield(yield: string): string {
  // Extract just the amount for display
  // "80g/week after day 45" -> "80g/week"
  return yield.split(' after ')[0]
}
</script>

<style scoped>
.impact-card {
  background: linear-gradient(135deg, #ecfdf5, #f0fdf4);
  border: 2px solid #86efac;
  border-radius: 1rem;
  padding: 1.5rem;
  margin-top: 1rem;
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.1);
}

.impact-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #86efac;
}

.impact-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #065f46;
  margin: 0;
}

.suitability-score {
  background: #059669;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.impact-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: white;
  border-radius: 0.75rem;
  border: 1px solid #d1fae5;
  transition: transform 0.2s ease;
}

.metric-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.15);
}

.metric-icon {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.metric-value {
  font-weight: 700;
  color: #059669;
  font-size: 0.875rem;
  line-height: 1.2;
}

.metric-label {
  font-size: 0.75rem;
  color: #065f46;
  font-weight: 500;
  line-height: 1.2;
}

.requirements {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.req-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.req-label {
  font-weight: 600;
  color: #065f46;
}

.req-value {
  color: #047857;
  font-weight: 500;
}

.badges {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.risk-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.risk-low {
  background: #dcfce7;
  color: #166534;
}

.risk-medium {
  background: #fef3c7;
  color: #92400e;
}

.risk-high {
  background: #fecaca;
  color: #991b1b;
}

.confidence-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  background: #e5e7eb;
  color: #374151;
}

.why-plant {
  padding: 0.75rem;
  background: rgba(34, 197, 94, 0.1);
  border-radius: 0.75rem;
  border-left: 3px solid #22c55e;
  font-size: 0.875rem;
  color: #065f46;
  line-height: 1.4;
  margin-bottom: 1rem;
}

.community-impact {
  padding: 0.5rem;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 0.5rem;
  border-left: 3px solid #3b82f6;
}

.community-text {
  font-size: 0.75rem;
  color: #1e40af;
  margin: 0;
  font-style: italic;
}

/* Responsive design */
@media (max-width: 768px) {
  .impact-metrics {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }

  .requirements {
    flex-direction: column;
    gap: 0.5rem;
  }

  .badges {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
```

### 2. Enhanced Plant Card Component

```vue
<!-- File: src/components/EnhancedPlantCard.vue -->
<template>
  <div class="enhanced-plant-card" @click="$emit('select', plant)">
    <!-- Plant Image -->
    <div class="plant-card-image">
      <img
        :src="getImageSource()"
        :alt="plant.name"
        class="plant-image"
        @error="handleImageError"
      />
    </div>

    <!-- Plant Information -->
    <div class="plant-card-content">
      <!-- Header -->
      <div class="plant-header">
        <h3 class="plant-title">{{ plant.name }}</h3>
        <div class="plant-score" v-if="plant.score">
          {{ plant.score.toFixed(1) }}/100
        </div>
      </div>

      <!-- Description -->
      <div class="plant-description">
        {{ truncateDescription(plant.description) }}
      </div>

      <!-- Climate Impact Preview -->
      <div class="impact-preview" v-if="plant.quantified_impact">
        <h4 class="impact-preview-title">Climate Impact Preview</h4>

        <div class="impact-highlights">
          <div class="highlight-item">
            <span class="highlight-icon">🌡️</span>
            <span class="highlight-text">{{ plant.quantified_impact.temperature_reduction_c }}°C cooling</span>
          </div>

          <div class="highlight-item">
            <span class="highlight-icon">🌱</span>
            <span class="highlight-text">{{ plant.quantified_impact.co2_absorption_kg_year }}kg CO₂/yr</span>
          </div>

          <div class="highlight-item">
            <span class="highlight-icon">💨</span>
            <span class="highlight-text">+{{ plant.quantified_impact.air_quality_points }} AQ points</span>
          </div>

          <div class="highlight-item" v-if="plant.quantified_impact.pollinator_support !== 'Minimal'">
            <span class="highlight-icon">🦋</span>
            <span class="highlight-text">{{ plant.quantified_impact.pollinator_support }} pollinator support</span>
          </div>
        </div>

        <!-- Quick maintenance info -->
        <div class="maintenance-info">
          <span class="maintenance-label">Care:</span>
          <span class="maintenance-value">{{ plant.quantified_impact.maintenance_time }}</span>
          <span class="maintenance-divider">•</span>
          <span class="water-value">{{ plant.quantified_impact.water_requirement }}</span>
        </div>
      </div>

      <!-- Fallback traditional care info -->
      <div class="traditional-care" v-else>
        <div class="care-item">
          <span class="care-label">Sun:</span>
          <span class="care-value">{{ getSunRequirement(plant) }}</span>
        </div>
        <div class="care-item">
          <span class="care-label">Water:</span>
          <span class="care-value">{{ getWaterRequirement(plant) }}</span>
        </div>
      </div>

      <!-- Why Recommended -->
      <div class="why-recommended">
        {{ getRecommendationReason(plant) }}
      </div>

      <!-- Action Button -->
      <button class="learn-more-button" @click.stop="$emit('select', plant)">
        {{ plant.quantified_impact ? 'View Full Impact' : 'Learn More' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Plant } from '@/types/plant'

const props = defineProps<{
  plant: Plant
}>()

defineEmits<{
  select: [plant: Plant]
}>()

function getImageSource(): string {
  if (props.plant.image_base64) {
    return props.plant.image_base64.startsWith('data:')
      ? props.plant.image_base64
      : `data:image/jpeg;base64,${props.plant.image_base64}`
  }

  return getCategoryPlaceholder()
}

function getCategoryPlaceholder(): string {
  const category = props.plant.category?.toLowerCase()

  switch (category) {
    case 'flower': return '/Flower.jpg'
    case 'herb': return '/Herb.jpg'
    case 'vegetable': return '/Vegetable.jpg'
    default: return '/placeholder-plant.svg'
  }
}

function handleImageError(event: Event) {
  const img = event.target as HTMLImageElement
  const placeholder = getCategoryPlaceholder()

  if (img.src !== placeholder) {
    img.src = placeholder
  }
}

function truncateDescription(description: string | undefined): string {
  if (!description) return 'No description available.'
  return description.length > 100 ? description.substring(0, 97) + '...' : description
}

function getSunRequirement(plant: Plant): string {
  return plant.sunlight || plant.care_requirements?.sunlight || 'Full Sun'
}

function getWaterRequirement(plant: Plant): string {
  return plant.water || plant.care_requirements?.watering || 'Medium'
}

function getRecommendationReason(plant: Plant): string {
  if (plant.quantified_impact?.why_this_plant) {
    return plant.quantified_impact.why_this_plant
  }

  if (Array.isArray(plant.whyRecommended)) {
    return plant.whyRecommended.join(' ')
  }

  return plant.whyRecommended || 'Great choice for your garden!'
}
</script>

<style scoped>
.enhanced-plant-card {
  border: 2px solid #a7f3d0;
  border-radius: 1rem;
  background: white;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(5, 150, 105, 0.08);
}

.enhanced-plant-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 40px rgba(5, 150, 105, 0.15);
  border-color: #059669;
}

.plant-card-image {
  height: 200px;
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
  border-bottom: 2px solid #a7f3d0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.plant-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.enhanced-plant-card:hover .plant-image {
  transform: scale(1.05);
}

.plant-card-content {
  padding: 1.5rem;
}

.plant-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  gap: 0.5rem;
}

.plant-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1c3d21;
  margin: 0;
  flex: 1;
}

.plant-score {
  background: #047857;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  flex-shrink: 0;
}

.plant-description {
  color: #1c3d21;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  line-height: 1.5;
}

/* Impact Preview Styles */
.impact-preview {
  background: linear-gradient(135deg, #ecfdf5, #f0fdf4);
  border: 1px solid #86efac;
  border-radius: 0.75rem;
  padding: 1rem;
  margin-bottom: 1rem;
}

.impact-preview-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #065f46;
  margin: 0 0 0.75rem 0;
  text-align: center;
}

.impact-highlights {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.highlight-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #047857;
}

.highlight-icon {
  font-size: 0.875rem;
}

.highlight-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.maintenance-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  border-top: 1px solid #d1fae5;
  padding-top: 0.5rem;
}

.maintenance-label {
  font-weight: 600;
  color: #065f46;
}

.maintenance-value, .water-value {
  color: #047857;
  font-weight: 500;
}

.maintenance-divider {
  color: #9ca3af;
}

/* Traditional care fallback */
.traditional-care {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  justify-content: space-between;
}

.care-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  flex: 1;
}

.care-label {
  font-weight: 600;
  color: #047857;
  font-size: 0.75rem;
}

.care-value {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.why-recommended {
  font-size: 0.875rem;
  color: #1c3d21;
  margin-bottom: 1rem;
  padding: 0.75rem;
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
  border-radius: 0.75rem;
  border-left: 3px solid #1c3d21;
  font-weight: 500;
}

.learn-more-button {
  width: 100%;
  padding: 0.75rem;
  background: transparent;
  border: 2px solid #1c3d21;
  color: #1c3d21;
  border-radius: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.learn-more-button:hover {
  background: #1c3d21;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(28, 61, 33, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .impact-highlights {
    grid-template-columns: 1fr;
    gap: 0.375rem;
  }

  .maintenance-info {
    flex-direction: column;
    gap: 0.375rem;
  }

  .plant-card-content {
    padding: 1rem;
  }
}
</style>
```

## Integration with Existing Views

### 1. Update RecommendationsView

```typescript
// File: src/views/RecommendationsView.vue
import { quantificationService } from '@/services/quantificationService'

// Add method to get enhanced recommendations
async function getEnhancedRecommendations() {
  try {
    // Build request from existing form data
    const request = buildApiRequest(formData)

    // Use enhanced endpoint
    const response = await quantificationService.getRecommendationsWithImpact(request)

    // Transform and display as usual
    recommendations.value = transformRecommendations(response)

  } catch (error) {
    console.error('Enhanced recommendations failed:', error)
    // Fallback to standard recommendations
    await getStandardRecommendations()
  }
}

// Add toggle for impact view
const showImpactMetrics = ref(false)
```

### 2. Update PlantDetailModal

```vue
<!-- File: src/views/recommendation/PlantDetailModal.vue -->
<template>
  <div class="modal-content">
    <!-- Existing plant details -->

    <!-- Add Impact Section -->
    <div class="impact-section" v-if="plant.quantified_impact">
      <h3>Climate Impact Analysis</h3>
      <ImpactCard
        :impact="plant.quantified_impact"
        :suitability-score="plant.suitability_score"
      />
    </div>

    <!-- Quantify Button (if no impact data) -->
    <div class="quantify-action" v-else>
      <button
        @click="quantifyPlant"
        :disabled="quantifying"
        class="quantify-button"
      >
        {{ quantifying ? 'Calculating Impact...' : 'Analyze Climate Impact' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import ImpactCard from '@/components/ImpactCard.vue'
import { quantificationService } from '@/services/quantificationService'

const quantifying = ref(false)

async function quantifyPlant() {
  quantifying.value = true

  try {
    // Build quantification request
    const request = {
      plant_name: plant.value.name,
      suburb: getCurrentSuburb(), // From your app state
      plant_count: 1,
      user_preferences: getCurrentPreferences() // From your app state
    }

    const response = await quantificationService.quantifyPlant(request)

    // Update plant with quantified impact
    plant.value.quantified_impact = response.quantified_impact
    plant.value.suitability_score = response.suitability_score.total_score

  } catch (error) {
    console.error('Quantification failed:', error)
    // Show error message to user
  } finally {
    quantifying.value = false
  }
}
</script>
```

## User Settings & Preferences

### Toggle Impact Display

```vue
<!-- File: src/components/ImpactToggle.vue -->
<template>
  <div class="impact-toggle">
    <label class="toggle-label">
      <input
        type="checkbox"
        v-model="showImpact"
        @change="updateSettings"
        class="toggle-input"
      />
      <span class="toggle-slider"></span>
      <span class="toggle-text">Show Climate Impact</span>
    </label>

    <div class="impact-info" v-if="showInfo">
      <p class="info-text">
        See real-world environmental benefits: cooling effect, CO₂ absorption,
        air quality improvement, and pollinator support for each plant.
      </p>
    </div>
  </div>
</template>

<script setup>
const showImpact = ref(true)
const showInfo = ref(false)

function updateSettings() {
  // Save to localStorage or user preferences
  localStorage.setItem('showClimateImpact', showImpact.value.toString())

  // Emit to parent component
  emit('impact-visibility-changed', showImpact.value)
}

// Load saved preference
onMounted(() => {
  const saved = localStorage.getItem('showClimateImpact')
  if (saved !== null) {
    showImpact.value = saved === 'true'
  }
})
</script>
```

## Error Handling & Loading States

### Loading Component

```vue
<!-- File: src/components/ImpactLoading.vue -->
<template>
  <div class="impact-loading">
    <div class="loading-spinner"></div>
    <p class="loading-text">Calculating climate impact...</p>
    <div class="loading-metrics">
      <div class="loading-metric">🌡️ Cooling effect</div>
      <div class="loading-metric">🌱 CO₂ absorption</div>
      <div class="loading-metric">💨 Air quality</div>
      <div class="loading-metric">🦋 Pollinator support</div>
    </div>
  </div>
</template>

<style scoped>
.impact-loading {
  padding: 2rem;
  text-align: center;
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
  border-radius: 1rem;
  border: 1px solid #86efac;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #86efac;
  border-top: 4px solid #059669;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: #065f46;
  font-weight: 600;
  margin-bottom: 1rem;
}

.loading-metrics {
  display: flex;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.loading-metric {
  font-size: 0.75rem;
  color: #047857;
  padding: 0.25rem 0.5rem;
  background: white;
  border-radius: 0.5rem;
  border: 1px solid #d1fae5;
}
</style>
```

### Error Handling

```typescript
// File: src/composables/useQuantification.ts
import { ref, computed } from 'vue'
import { quantificationService } from '@/services/quantificationService'

export function useQuantification() {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const quantifiedPlants = ref<Map<string, any>>(new Map())

  async function quantifyPlant(plantName: string, preferences: any) {
    loading.value = true
    error.value = null

    try {
      const request = {
        plant_name: plantName,
        suburb: preferences.suburb,
        plant_count: preferences.plantCount || 1,
        user_preferences: preferences
      }

      const response = await quantificationService.quantifyPlant(request)

      // Cache the result
      quantifiedPlants.value.set(plantName, response)

      return response

    } catch (err: any) {
      error.value = err.message || 'Failed to quantify plant impact'
      console.error('Quantification error:', err)
      return null

    } finally {
      loading.value = false
    }
  }

  function getQuantifiedImpact(plantName: string) {
    return quantifiedPlants.value.get(plantName)
  }

  function clearError() {
    error.value = null
  }

  return {
    loading: readonly(loading),
    error: readonly(error),
    quantifyPlant,
    getQuantifiedImpact,
    clearError
  }
}
```

## Performance Optimization

### Lazy Loading & Caching

```typescript
// File: src/services/quantificationCache.ts
class QuantificationCache {
  private cache = new Map<string, any>()
  private maxAge = 30 * 60 * 1000 // 30 minutes

  private getCacheKey(plantName: string, preferences: any): string {
    return `${plantName}-${JSON.stringify(preferences)}`
  }

  get(plantName: string, preferences: any): any | null {
    const key = this.getCacheKey(plantName, preferences)
    const cached = this.cache.get(key)

    if (!cached) return null

    // Check if expired
    if (Date.now() - cached.timestamp > this.maxAge) {
      this.cache.delete(key)
      return null
    }

    return cached.data
  }

  set(plantName: string, preferences: any, data: any): void {
    const key = this.getCacheKey(plantName, preferences)
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })

    // Cleanup old entries
    if (this.cache.size > 100) {
      const oldest = Array.from(this.cache.entries())[0]
      this.cache.delete(oldest[0])
    }
  }

  clear(): void {
    this.cache.clear()
  }
}

export const quantificationCache = new QuantificationCache()
```

### Intersection Observer for Lazy Quantification

```typescript
// File: src/composables/useLazyQuantification.ts
import { ref, onMounted, onUnmounted } from 'vue'

export function useLazyQuantification() {
  const observer = ref<IntersectionObserver | null>(null)
  const quantificationTargets = ref<Set<HTMLElement>>(new Set())

  onMounted(() => {
    observer.value = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            // Trigger quantification when element becomes visible
            const plantName = entry.target.getAttribute('data-plant-name')
            if (plantName) {
              triggerQuantification(plantName)
            }

            // Stop observing this element
            observer.value?.unobserve(entry.target)
            quantificationTargets.value.delete(entry.target as HTMLElement)
          }
        })
      },
      {
        rootMargin: '100px', // Start quantifying 100px before element is visible
        threshold: 0.1
      }
    )
  })

  onUnmounted(() => {
    observer.value?.disconnect()
  })

  function observeElement(element: HTMLElement) {
    if (observer.value && !quantificationTargets.value.has(element)) {
      observer.value.observe(element)
      quantificationTargets.value.add(element)
    }
  }

  function triggerQuantification(plantName: string) {
    // Emit event or call quantification service
    console.log(`Triggering quantification for ${plantName}`)
  }

  return {
    observeElement
  }
}
```

## Testing Strategy

### Unit Tests

```typescript
// File: src/services/__tests__/quantificationService.test.ts
import { describe, it, expect, vi } from 'vitest'
import { quantificationService } from '../quantificationService'

describe('QuantificationService', () => {
  it('should quantify a plant successfully', async () => {
    // Mock fetch
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        plant_name: 'Basil',
        quantified_impact: {
          temperature_reduction_c: 0.8,
          air_quality_points: 12,
          co2_absorption_kg_year: 2.5
        }
      })
    })

    const request = {
      plant_name: 'Basil',
      suburb: 'Richmond',
      plant_count: 1,
      user_preferences: {
        site: { location_type: 'balcony', area_m2: 4 },
        preferences: { goal: 'mixed', maintainability: 'low' }
      }
    }

    const result = await quantificationService.quantifyPlant(request)

    expect(result.plant_name).toBe('Basil')
    expect(result.quantified_impact.temperature_reduction_c).toBe(0.8)
  })

  it('should handle API errors gracefully', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      statusText: 'Plant not found'
    })

    const request = {
      plant_name: 'NonexistentPlant',
      suburb: 'Richmond',
      plant_count: 1,
      user_preferences: {}
    }

    await expect(quantificationService.quantifyPlant(request))
      .rejects.toThrow('Quantification failed: Plant not found')
  })
})
```

### Component Tests

```typescript
// File: src/components/__tests__/ImpactCard.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ImpactCard from '../ImpactCard.vue'

describe('ImpactCard', () => {
  const mockImpact = {
    temperature_reduction_c: 1.2,
    air_quality_points: 8,
    co2_absorption_kg_year: 3.4,
    water_processed_l_week: 15.0,
    pollinator_support: 'High',
    maintenance_time: '10mins/week',
    water_requirement: '5.5L/week',
    risk_badge: 'low',
    confidence_level: 'High (89%)',
    why_this_plant: 'Selected for excellent cooling and air purification'
  }

  it('displays impact metrics correctly', () => {
    const wrapper = mount(ImpactCard, {
      props: {
        impact: mockImpact,
        suitabilityScore: 85
      }
    })

    expect(wrapper.text()).toContain('1.2°C')
    expect(wrapper.text()).toContain('+8')
    expect(wrapper.text()).toContain('3.4kg/yr')
    expect(wrapper.text()).toContain('High')
    expect(wrapper.text()).toContain('85/100')
  })

  it('handles missing edible yield gracefully', () => {
    const impactWithoutYield = { ...mockImpact }
    delete impactWithoutYield.edible_yield

    const wrapper = mount(ImpactCard, {
      props: { impact: impactWithoutYield }
    })

    expect(wrapper.find('.metric-item.edible').exists()).toBe(false)
  })
})
```

## Deployment Checklist

### 1. Environment Variables
```bash
# .env.production
VITE_API_BASE_URL=/api/v1
VITE_ENABLE_QUANTIFICATION=true
```

### 2. Build Configuration
```typescript
// vite.config.ts
export default defineConfig({
  // ... existing config
  define: {
    __ENABLE_QUANTIFICATION__: JSON.stringify(process.env.VITE_ENABLE_QUANTIFICATION === 'true')
  }
})
```

### 3. Feature Flag Usage
```vue
<template>
  <div v-if="isQuantificationEnabled">
    <!-- Quantification features -->
  </div>
</template>

<script>
const isQuantificationEnabled = __ENABLE_QUANTIFICATION__
</script>
```

### 4. Progressive Enhancement
- Quantification features should enhance, not replace existing functionality
- Always provide fallbacks for when quantification fails
- Load quantification assets lazily to avoid impacting initial page load
- Cache quantified results to minimize API calls

This implementation guide provides everything needed to integrate the Climate Action Quantification feature seamlessly into the existing Plantopia frontend while maintaining performance and user experience standards.