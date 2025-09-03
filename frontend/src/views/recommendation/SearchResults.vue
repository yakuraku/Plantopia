<template>
  <!-- 
    Search Results Section
    Displays filtered plant recommendations with sidebar filters
    Layout includes FilterSidebar and plant grid with responsive design
  -->
  <div class="results-section-inline">
    <div class="results-layout">
      <!-- Filter Sidebar Component - handles plant filtering options -->
      <FilterSidebar @filters-changed="handleFiltersChanged" />

      <!-- Main Results Content Area -->
      <div class="results-content">
        <!-- Results Header with location-specific messaging -->
        <div class="results-header">
          <h2>Recommended for {{ location || 'Melbourne' }}</h2>
          <p>These climate-smart plants are perfect for your local conditions</p>
        </div>

        <!-- Plant Cards Grid - displays filtered plant recommendations -->
        <div class="plant-grid">
          <PlantCard
            v-for="plant in filteredPlants"
            :key="plant.id"
            :plant="plant"
            @select="$emit('plant-selected', $event)"
          />
        </div>

        <!-- No Results Message - shown when no plants match current filters -->
        <div v-if="filteredPlants.length === 0" class="no-results">
          <p>
            No plants match your current filters. Try adjusting your preferences or filters.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import FilterSidebar from './FilterSidebar.vue'
import PlantCard from './PlantCard.vue'

import type { Plant } from '@/services/api'

// Component props for search results
interface Props {
  location: string
  locationType: string
  sunlight: string
  maintainability: string
  plants: Plant[]
}

// Component props and events definition
const props = defineProps<Props>()
const emit = defineEmits<{
  'plant-selected': [plant: Plant]
}>()

// Active filter state - tracks which benefit filters are currently applied
const activeFilters = ref<string[]>([])

// Computed property that filters plants based on search criteria and active filters
const filteredPlants = computed(() => {
  let filtered = props.plants

  // Filter by location type - indoor locations prefer shade/partial sun plants
  if (props.locationType === 'Indoor') {
    filtered = filtered.filter(
      (plant) => plant.sunlight === 'shade' || plant.sunlight === 'partial',
    )
  }

  // Filter by sunlight requirements - map UI labels to plant data values
  if (props.sunlight) {
    const sunlightMap: { [key: string]: string } = {
      'Full Sun': 'full',
      'Partial Sun': 'partial',
      Shade: 'shade',
    }
    filtered = filtered.filter((plant) => plant.sunlight === sunlightMap[props.sunlight])
  }

  // Filter by maintainability - map UI labels to plant data values
  if (props.maintainability) {
    const maintainabilityMap: { [key: string]: string } = {
      'Low Maintenance': 'low',
      'Medium Maintenance': 'medium',
      'High Maintenance': 'high',
    }
    filtered = filtered.filter((plant) => plant.effort === maintainabilityMap[props.maintainability])
  }

  // Apply benefit filters from sidebar - plant must match ALL selected benefits
  if (activeFilters.value.length > 0) {
    filtered = filtered.filter((plant) => {
      return activeFilters.value.every((filter) => {
        switch (filter) {
          case 'Edible': return plant.benefits.edible
          case 'Fragrant': return plant.benefits.fragrant
          case 'Pet Safe': return plant.benefits.petSafe
          case 'Air Purifying': return plant.benefits.airPurifying
          case 'Drought Resistant': return plant.benefits.droughtResistant
          case 'Container Friendly': return plant.benefits.containerFriendly
          case 'Indoor Suitable': return plant.benefits.indoorSuitable
          default: return false
        }
      })
    })
  }

  return filtered
})

// Handle filter changes from FilterSidebar component
const handleFiltersChanged = (filters: string[]) => {
  activeFilters.value = filters
}
</script>

<style scoped>
.results-section-inline {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid rgba(28, 61, 33, 0.1);
}

.results-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 2rem;
}

.results-content {
  min-height: 400px;
}

.results-header {
  margin-bottom: 2rem;
}

.results-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1c3d21;
  margin-bottom: 0.5rem;
}

.results-header p {
  color: #1c3d21;
  font-weight: 500;
}

.plant-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.no-results {
  text-align: center;
  padding: 3rem;
  color: #1c3d21;
  font-weight: 500;
}

@media (max-width: 768px) {
  .results-layout {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .plant-grid {
    grid-template-columns: 1fr;
  }
}
</style>