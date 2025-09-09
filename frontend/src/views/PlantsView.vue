画<template>
  <!--
    Plants Page
    Display all available plants in the system
  -->
  <div class="plants-page">
    <!-- Bootstrap Container -->
    <div class="container-fluid bg-transparent">
      <!-- Top Section -->
      <div class="top-section">
        <div class="container-xl">
          <div class="page-header">
            <h1 class="page-title">All Plants</h1>
            <p class="page-subtitle">Discover our complete collection of plants</p>
          </div>
        </div>
      </div>

      <!-- Content section -->
      <div class="content-section">
        <div class="container-xl">
          <div class="content-panel">
            <!-- Search and Filter Bar -->
            <div class="search-filter-bar">
              <div class="search-input-group">
                <input
                  type="text"
                  class="form-control search-input"
                  placeholder="Search plants by name..."
                  v-model="searchQuery"
                  @input="handleSearch"
                >
              </div>
              <div class="filter-buttons">
                <button
                  class="btn filter-btn"
                  :class="{ 'active': selectedCategory === 'all' }"
                  @click="setCategory('all')"
                >
                  All
                </button>
                <button
                  class="btn filter-btn"
                  :class="{ 'active': selectedCategory === 'vegetable' }"
                  @click="setCategory('vegetable')"
                >
                  Vegetables
                </button>
                <button
                  class="btn filter-btn"
                  :class="{ 'active': selectedCategory === 'herb' }"
                  @click="setCategory('herb')"
                >
                  Herbs
                </button>
                <button
                  class="btn filter-btn"
                  :class="{ 'active': selectedCategory === 'flower' }"
                  @click="setCategory('flower')"
                >
                  Flowers
                </button>
              </div>
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="loading-state text-center py-5">
              <div class="loading-spinner mx-auto mb-3"></div>
              <p class="mb-0">Loading plants...</p>
            </div>

            <!-- Error State -->
            <div v-else-if="error" class="error-state">
              <div class="alert alert-danger d-flex align-items-center" role="alert">
                <div class="flex-grow-1">{{ error }}</div>
                <button @click="loadPlants" class="btn btn-outline-danger btn-sm ms-3">Retry</button>
              </div>
            </div>

            <!-- Plants Grid -->
            <div v-else-if="filteredPlants.length > 0" class="plants-results">
              <div class="plants-count">
                <p class="mb-3">
                  Showing {{ ((currentPage - 1) * plantsPerPage) + 1 }}-{{ Math.min(currentPage * plantsPerPage, totalPlants) }}
                  of {{ totalPlants }} plants
                  <span v-if="totalPages > 1">(Page {{ currentPage }} of {{ totalPages }})</span>
                </p>
              </div>
              <div class="plants-grid">
                <div
                  v-for="plant in paginatedPlants"
                  :key="plant.id"
                  class="plant-card"
                  @click="selectPlant(plant)"
                >
                  <div class="plant-image">
                    <!-- Show Google Drive image if available -->
                    <img
                      v-if="plant.has_image && !hasImageError(plant.id)"
                      :src="getPlantImageSrc(plant)"
                      :alt="plant.name"
                      @error="(event) => handleImageError(event, plant.id)"
                    >
                    <!-- Show placeholder if no image available or image failed to load -->
                    <div v-else class="image-placeholder">
                      <div class="placeholder-icon">Plant</div>
                      <span class="placeholder-text">{{ plant.category || 'Plant' }}</span>
                    </div>
                  </div>
                  <div class="plant-info">
                    <h3 class="plant-name">{{ plant.name }}</h3>
                    <p class="plant-scientific">{{ plant.scientific_name }}</p>
                    <div class="plant-tags">
                      <span
                        v-for="tag in plant.tags?.slice(0, 3)"
                        :key="tag"
                        class="plant-tag"
                      >
                        {{ tag }}
                      </span>
                    </div>
                    <div class="plant-care">
                      <div class="care-item">
                        <span class="care-label">Sun:</span>
                        <span class="care-value">{{ plant.care_requirements?.sunlight || 'N/A' }}</span>
                      </div>
                      <div class="care-item">
                        <span class="care-label">Water:</span>
                        <span class="care-value">{{ plant.care_requirements?.watering || 'N/A' }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Pagination Controls -->
              <div v-if="totalPages > 1" class="pagination-controls">
                <nav aria-label="Plants pagination">
                  <ul class="pagination">
                    <!-- Previous button -->
                    <li class="page-item" :class="{ disabled: !canGoPrevious }">
                      <button
                        class="page-link"
                        @click="goToPreviousPage"
                        :disabled="!canGoPrevious"
                        aria-label="Previous page"
                      >
                        &lsaquo; Previous
                      </button>
                    </li>

                    <!-- Page numbers -->
                    <li
                      v-for="pageNumber in pageNumbers"
                      :key="pageNumber"
                      class="page-item"
                      :class="{ active: pageNumber === currentPage }"
                    >
                      <button
                        class="page-link"
                        @click="goToPage(pageNumber)"
                        :aria-label="`Go to page ${pageNumber}`"
                        :aria-current="pageNumber === currentPage ? 'page' : undefined"
                      >
                        {{ pageNumber }}
                      </button>
                    </li>

                    <!-- Next button -->
                    <li class="page-item" :class="{ disabled: !canGoNext }">
                      <button
                        class="page-link"
                        @click="goToNextPage"
                        :disabled="!canGoNext"
                        aria-label="Next page"
                      >
                        Next &rsaquo;
                      </button>
                    </li>
                  </ul>
                </nav>
              </div>
            </div>

            <!-- No Results State -->
            <div v-else class="no-results-state">
              <div class="alert alert-info text-center" role="alert">
                <p class="mb-0">
                  {{ searchQuery ? 'No plants found matching your search.' : 'No plants available at the moment.' }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Plant Detail Modal -->
    <div v-if="selectedPlant" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">{{ selectedPlant.name }}</h2>
          <button class="modal-close" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
          <div class="plant-detail-image">
            <!-- Show Google Drive image if available -->
            <img
              v-if="selectedPlant.has_image && !hasImageError(selectedPlant.id)"
              :src="getPlantImageSrc(selectedPlant)"
              :alt="selectedPlant.name"
              @error="(event) => handleImageError(event, selectedPlant.id)"
            >
            <!-- Show placeholder if no image available or image failed to load -->
            <div v-else class="image-placeholder">
              <div class="placeholder-icon">Plant</div>
              <span class="placeholder-text">{{ selectedPlant.category || 'Plant' }}</span>
            </div>
          </div>
          <div class="plant-detail-info">
            <p class="scientific-name">{{ selectedPlant.scientific_name }}</p>
            <div class="description">
              <h4>Description</h4>
              <div class="plant-description" v-html="renderedDescription"></div>
            </div>
            <div class="plant-type" v-if="selectedPlant.plant_type">
              <h4>Plant Type</h4>
              <p>{{ selectedPlant.plant_type }}</p>
            </div>
            <div class="growing-details" v-if="selectedPlant.days_to_maturity || selectedPlant.plant_spacing || selectedPlant.position">
              <h4>Growing Details</h4>
              <div class="care-grid">
                <div class="care-detail" v-if="selectedPlant.days_to_maturity">
                  <strong>Days to Maturity:</strong> {{ selectedPlant.days_to_maturity }}
                </div>
                <div class="care-detail" v-if="selectedPlant.plant_spacing">
                  <strong>Plant Spacing:</strong> {{ selectedPlant.plant_spacing }}
                </div>
                <div class="care-detail" v-if="selectedPlant.sowing_depth">
                  <strong>Sowing Depth:</strong> {{ selectedPlant.sowing_depth }}
                </div>
                <div class="care-detail" v-if="selectedPlant.position">
                  <strong>Position:</strong> {{ selectedPlant.position }}
                </div>
                <div class="care-detail" v-if="selectedPlant.season">
                  <strong>Season:</strong> {{ selectedPlant.season }}
                </div>
                <div class="care-detail" v-if="selectedPlant.germination_period">
                  <strong>Germination:</strong> {{ selectedPlant.germination_period }}
                </div>
                <div class="care-detail" v-if="selectedPlant.sowing_method">
                  <strong>Sowing Method:</strong> {{ selectedPlant.sowing_method }}
                </div>
                <div class="care-detail" v-if="selectedPlant.hardiness_life_cycle">
                  <strong>Hardiness:</strong> {{ selectedPlant.hardiness_life_cycle }}
                </div>
              </div>
            </div>
            <div class="care-requirements" v-if="selectedPlant.care_requirements">
              <h4>Care Requirements</h4>
              <div class="care-grid">
                <div class="care-detail" v-if="selectedPlant.care_requirements.sunlight">
                  <strong>Sunlight:</strong> {{ selectedPlant.care_requirements.sunlight }}
                </div>
                <div class="care-detail" v-if="selectedPlant.care_requirements.watering">
                  <strong>Watering:</strong> {{ selectedPlant.care_requirements.watering }}
                </div>
                <div class="care-detail" v-if="selectedPlant.care_requirements.soil">
                  <strong>Soil:</strong> {{ selectedPlant.care_requirements.soil }}
                </div>
                <div class="care-detail" v-if="selectedPlant.care_requirements.temperature">
                  <strong>Temperature:</strong> {{ selectedPlant.care_requirements.temperature }}
                </div>
              </div>
            </div>
            <div class="additional-info" v-if="selectedPlant.additional_information">
              <h4>Additional Information</h4>
              <p>{{ selectedPlant.additional_information }}</p>
            </div>
            <div class="characteristics" v-if="selectedPlant.characteristics">
              <h4>Characteristics</h4>
              <p>{{ selectedPlant.characteristics }}</p>
            </div>
            <div class="plant-features" v-if="hasPlantFeatures(selectedPlant)">
              <h4>Plant Features</h4>
              <div class="features-grid">
                <div class="feature-item" v-if="selectedPlant.edible">
                  <strong>Edible:</strong> <span class="feature-yes">Yes</span>
                </div>
                <div class="feature-item" v-if="selectedPlant.fragrant">
                  <strong>Fragrant:</strong> <span class="feature-yes">Yes</span>
                </div>
                <div class="feature-item" v-if="selectedPlant.container_ok">
                  <strong>Container Suitable:</strong> <span class="feature-yes">Yes</span>
                </div>
                <div class="feature-item" v-if="selectedPlant.indoor_ok">
                  <strong>Indoor Suitable:</strong> <span class="feature-yes">Yes</span>
                </div>
                <div class="feature-item" v-if="selectedPlant.habit">
                  <strong>Growth Habit:</strong> {{ selectedPlant.habit }}
                </div>
                <div class="feature-item" v-if="selectedPlant.flower_colors && selectedPlant.flower_colors.length">
                  <strong>Flower Colors:</strong> {{ selectedPlant.flower_colors.join(', ') }}
                </div>
                <div class="feature-item" v-if="selectedPlant.maintainability_score !== undefined">
                  <strong>Maintenance Level:</strong> {{ getMaintenanceLevel(selectedPlant.maintainability_score) }}
                </div>
              </div>
            </div>
            <div class="climate-sowing" v-if="selectedPlant.climate_specific_sowing && hasClimateData(selectedPlant.climate_specific_sowing)">
              <h4>Sowing Times by Climate</h4>
              <div class="climate-grid">
                <div class="climate-item" v-for="(months, climate) in selectedPlant.climate_specific_sowing" :key="climate" v-if="months">
                  <strong>{{ capitalizeFirst(climate) }}:</strong> {{ months }}
                </div>
              </div>
            </div>
            <div class="plant-tags-detail" v-if="selectedPlant.tags && selectedPlant.tags.length">
              <h4>Tags</h4>
              <div class="tags-list">
                <span
                  v-for="tag in selectedPlant.tags"
                  :key="tag"
                  class="tag-item"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { plantApiService, type Plant } from '@/services/api'
import { getPlantImageUrl, handleImageError as handleImageErrorHelper } from '@/utils/imageHelper'
import { renderMarkdown } from '@/services/markdownService'

// Reactive state
const plants = ref<Plant[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const searchQuery = ref('')
const selectedCategory = ref<'all' | 'vegetable' | 'herb' | 'flower'>('all')
const selectedPlant = ref<Plant | null>(null)
const imageErrors = ref<Set<string>>(new Set())

// Pagination state
const currentPage = ref(1)
const plantsPerPage = 12

// API integration for loading plants

// Computed properties
const filteredPlants = computed(() => {
  let filtered = plants.value

  // Filter by category
  if (selectedCategory.value !== 'all') {
    filtered = filtered.filter(plant => plant.category === selectedCategory.value)
  }

  // Filter by search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(plant =>
      plant.name.toLowerCase().includes(query) ||
      plant.scientific_name.toLowerCase().includes(query) ||
      plant.tags?.some(tag => tag.toLowerCase().includes(query))
    )
  }

  return filtered
})

// Pagination computed properties
const totalPlants = computed(() => filteredPlants.value.length)
const totalPages = computed(() => Math.ceil(totalPlants.value / plantsPerPage))

// Markdown rendering computed property
const renderedDescription = computed(() => {
  if (!selectedPlant.value || !selectedPlant.value.description) {
    return 'No description available.'
  }
  return renderMarkdown(selectedPlant.value.description)
})

const paginatedPlants = computed(() => {
  const start = (currentPage.value - 1) * plantsPerPage
  const end = start + plantsPerPage
  return filteredPlants.value.slice(start, end)
})

// Pagination navigation helpers
const canGoPrevious = computed(() => currentPage.value > 1)
const canGoNext = computed(() => currentPage.value < totalPages.value)

const pageNumbers = computed(() => {
  const pages = []
  const maxVisiblePages = 5
  let startPage = Math.max(1, currentPage.value - Math.floor(maxVisiblePages / 2))
  let endPage = Math.min(totalPages.value, startPage + maxVisiblePages - 1)

  // Adjust start page if we're near the end
  if (endPage - startPage + 1 < maxVisiblePages) {
    startPage = Math.max(1, endPage - maxVisiblePages + 1)
  }

  for (let i = startPage; i <= endPage; i++) {
    pages.push(i)
  }

  return pages
})

// Methods
const loadPlants = async () => {
  loading.value = true
  error.value = null

  try {
    console.log('[PLANTS VIEW] Starting to load plants from API...')

    // First check if API is available
    try {
      await plantApiService.healthCheck()
      console.log('[PLANTS VIEW] Health check passed')
    } catch (healthErr) {
      console.error('[PLANTS VIEW] Health check failed:', healthErr)
      throw new Error('API server is not available. Please check your internet connection.')
    }

    // Get all plants from API
    const apiResponse = await plantApiService.getAllPlants()
    console.log('[PLANTS VIEW] API Response received:', apiResponse)

    // Transform API response to frontend format
    console.log('[PLANTS VIEW] Raw API response structure:', {
      total_count: apiResponse.total_count,
      plants_count: apiResponse.plants?.length || 0,
      first_plant: apiResponse.plants?.[0] || null
    })

    const transformedPlants = plantApiService.transformAllPlantsToPlants(apiResponse)
    console.log('[PLANTS VIEW] Plants transformed:', transformedPlants.length, 'plants')
    console.log('[PLANTS VIEW] First transformed plant:', transformedPlants[0] || null)
    console.log('[PLANTS VIEW] First plant has_image:', transformedPlants[0]?.has_image)
    console.log('[PLANTS VIEW] First plant image_url:', transformedPlants[0]?.image_url)
    console.log('[PLANTS VIEW] First plant category:', transformedPlants[0]?.category)

    plants.value = transformedPlants
    console.log('[PLANTS VIEW] Plants loaded successfully!')
  } catch (err) {
    console.error('[PLANTS VIEW] Error loading plants:', err)
    error.value = err instanceof Error ? err.message : 'Failed to load plants'
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  // Reset to first page when searching
  currentPage.value = 1
}

const setCategory = (category: 'all' | 'vegetable' | 'herb' | 'flower') => {
  selectedCategory.value = category
  // Reset to first page when changing category
  currentPage.value = 1
  // Keep user at top when switching via navigation
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Pagination methods
const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    // Scroll to top of plant results
    scrollToResults()
  }
}

const goToPreviousPage = () => {
  if (canGoPrevious.value) {
    goToPage(currentPage.value - 1)
  }
}

const goToNextPage = () => {
  if (canGoNext.value) {
    goToPage(currentPage.value + 1)
  }
}

const scrollToResults = () => {
  const resultsElement = document.querySelector('.plants-results')
  if (resultsElement) {
    resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const selectPlant = (plant: Plant) => {
  selectedPlant.value = plant
}

const closeModal = () => {
  selectedPlant.value = null
}

// Function to get image source (Base64 or URL) - following RecommendationsView pattern
const getPlantImageSrc = (plant: Plant): string => {
  // Priority 1: Use Google Drive URL from API if available
  if (plant.image_url && plant.image_url.includes('drive.google.com')) {
    return plant.image_url
  }

  // Priority 2: Legacy Base64 support (for backwards compatibility)
  if (plant.image_base64) {
    // Check if it's already a data URL
    if (plant.image_base64.startsWith('data:')) {
      return plant.image_base64
    }
    // If it's just the base64 string, add the data URL prefix
    return `data:image/jpeg;base64,${plant.image_base64}`
  }

  // Priority 3: Legacy image URL support
  if (plant.image_url) {
    return plant.image_url
  }

  // Priority 4: Generate Google Drive URL from category (fallback)
  if (plant.category && plant.has_image !== false) {
    return getPlantImageUrl(plant.category)
  }

  // Final fallback to placeholder
  return '/placeholder-plant.svg'
}

// Handle image loading errors - using Google Drive helper
const handleImageError = (event: Event, plantId: string) => {
  const img = event.target as HTMLImageElement
  console.warn('[PLANTS VIEW] Failed to load plant image:', img.src)

  // Track this plant as having image error
  imageErrors.value.add(plantId)

  // Try to find the plant and get its category for fallback
  const plant = plants.value.find(p => p.id === plantId)
  const category = plant?.category

  // Use the helper function to handle the error with category context
  handleImageErrorHelper(event, category)

  // Hide the broken image
  img.style.display = 'none'
}

// Check if plant has image error
const hasImageError = (plantId: string): boolean => {
  return imageErrors.value.has(plantId)
}

// Check if plant has any features to display
const hasPlantFeatures = (plant: Plant): boolean => {
  return !!(plant.edible || plant.fragrant || plant.container_ok || plant.indoor_ok ||
           plant.habit || (plant.flower_colors && plant.flower_colors.length) ||
           plant.maintainability_score !== undefined)
}

// Check if climate data has any non-empty values
const hasClimateData = (climateData: any): boolean => {
  if (!climateData) return false
  return Object.values(climateData).some(value => value && value !== '')
}

// Get maintenance level from score
const getMaintenanceLevel = (score: number): string => {
  if (score >= 0.8) return 'Low'
  if (score >= 0.5) return 'Medium'
  return 'High'
}

// Capitalize first letter
const capitalizeFirst = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

// Lifecycle
onMounted(() => {
  // if navigated with ?category=vegetables|herbs|flowers, map to internal keys
  const route = useRoute()
  const q = String(route.query.category || '').toLowerCase()
  if (q === 'vegetables') selectedCategory.value = 'vegetable'
  else if (q === 'herbs') selectedCategory.value = 'herb'
  else if (q === 'flowers') selectedCategory.value = 'flower'

  loadPlants()
})
</script>

<style scoped>
/* Background and Page Setup - Same as RecommendationsView */
.plants-page {
  min-height: 100vh;
  position: relative;
  background: transparent !important;
}

/* Ensure Bootstrap containers don't have white backgrounds */
.container-fluid,
.container-xl,
.row,
.col-xl-3,
.col-xl-9,
.col-lg-4,
.col-lg-8,
.col-md-12,
.col-12 {
  background: transparent !important;
}

/* Remove default horizontal padding so full-width backgrounds can bleed to edges */
.plants-page .container-fluid {
  padding-left: 0;
  padding-right: 0;
}

/* Background image - Same as RecommendationsView */
.plants-page::after {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('@/assets/photo/plant-1.jpg') no-repeat center center;
  background-size: cover;
  background-attachment: fixed;
  z-index: -2;
  pointer-events: none;
}

/* Top Section */
.top-section {
  background: transparent;
  border-bottom: 0;
  padding: 2rem 0;
  margin-top: 20px;
  position: relative;
  z-index: 1;
  backdrop-filter: none;
  width: 100%;
  isolation: isolate;
}

.page-header {
  text-align: center;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.page-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  margin-bottom: 0;
}

/* Content Section */
.content-section {
  padding-top: 1rem;
}

.content-panel {
  padding: 1.5rem 0;
  background: transparent;
  min-height: calc(100vh - 200px);
}

/* Search and Filter Bar */
.search-filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  gap: 1rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.search-input-group {
  flex: 1;
  max-width: 400px;
}

.search-input {
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  transition: all 0.2s ease;
}

.search-input:focus {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
  outline: none;
}

.filter-buttons {
  display: flex;
  gap: 0.5rem;
}

.filter-btn {
  padding: 0.5rem 1rem;
  border: 2px solid #e5e7eb;
  background: white;
  color: #374151;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.filter-btn:hover {
  border-color: #10b981;
  color: #10b981;
}

.filter-btn.active {
  background: #10b981;
  border-color: #10b981;
  color: white;
}

/* Loading Spinner */
.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e6edd8;
  border-top: 4px solid #0d9488;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Plants Results */
.plants-results {
  padding: 1rem 0;
}

.plants-count {
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  font-weight: 500;
}

.plants-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
  max-width: 100%;
}

/* Ensure optimal grid layout for different screen sizes */
@media (min-width: 1200px) {
  .plants-grid {
    grid-template-columns: repeat(4, 1fr); /* 4 columns on large screens */
  }
}

@media (min-width: 992px) and (max-width: 1199px) {
  .plants-grid {
    grid-template-columns: repeat(3, 1fr); /* 3 columns on medium screens */
  }
}

@media (min-width: 768px) and (max-width: 991px) {
  .plants-grid {
    grid-template-columns: repeat(2, 1fr); /* 2 columns on small screens */
  }
}

@media (max-width: 767px) {
  .plants-grid {
    grid-template-columns: 1fr; /* 1 column on mobile */
  }
}

/* Plant Card */
.plant-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.plant-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
}

.plant-image {
  height: 200px;
  overflow: hidden;
  position: relative;
}

.plant-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

/* Image placeholder styles - following RecommendationsView pattern */
.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
  color: #64748b;
  text-align: center;
  padding: 1rem;
}

.placeholder-icon {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #10b981;
}

.placeholder-text {
  font-size: 0.875rem;
  color: #64748b;
  text-transform: capitalize;
}

.plant-card:hover .plant-image img {
  transform: scale(1.05);
}

.plant-info {
  padding: 1.25rem;
}

.plant-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.plant-scientific {
  font-style: italic;
  color: #6b7280;
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
}

.plant-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
}

.plant-tag {
  background: #ecfdf5;
  color: #065f46;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
}

.plant-care {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.care-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.875rem;
}

.care-label {
  font-weight: 500;
  color: #4b5563;
}

.care-value {
  color: #6b7280;
}

/* Plant Features Styles */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

.feature-item {
  padding: 0.5rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.feature-item:last-child {
  border-bottom: none;
}

.feature-item strong {
  color: #374151;
  font-weight: 600;
}

.feature-yes {
  color: #10b981;
  font-weight: 600;
}

/* Climate Sowing Styles */
.climate-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 0.75rem;
}

.climate-item {
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 8px;
  border-left: 3px solid #10b981;
}

.climate-item strong {
  color: #374151;
  font-weight: 600;
}

/* Pagination Styles */
.pagination-controls {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
  padding: 1rem 0;
}

.pagination {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 0.25rem;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.page-item {
  margin: 0;
}

.page-link {
  display: block;
  padding: 0.5rem 0.75rem;
  margin: 0;
  color: #374151;
  background: transparent;
  border: 2px solid transparent;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
  min-width: 44px;
  text-align: center;
}

.page-link:hover:not(:disabled) {
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
  border-color: #10b981;
}

.page-link:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
}

.page-item.active .page-link {
  color: white;
  background: #10b981;
  border-color: #10b981;
  font-weight: 600;
}

.page-item.disabled .page-link {
  color: #9ca3af;
  cursor: not-allowed;
  opacity: 0.5;
}

.page-item.disabled .page-link:hover {
  color: #9ca3af;
  background: transparent;
  border-color: transparent;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: color 0.2s ease;
}

.modal-close:hover {
  color: #1f2937;
}

.modal-body {
  padding: 1.5rem;
}

.plant-detail-image {
  width: 100%;
  height: 250px;
  overflow: hidden;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.plant-detail-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.plant-detail-image .image-placeholder {
  height: 100%;
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
}

.plant-detail-image .placeholder-icon {
  font-size: 2rem;
}

.plant-detail-image .placeholder-text {
  font-size: 1rem;
}

.scientific-name {
  font-style: italic;
  color: #6b7280;
  font-size: 1rem;
  margin-bottom: 1.5rem;
}

.description,
.plant-type,
.growing-details,
.care-requirements,
.additional-info,
.characteristics,
.plant-features,
.climate-sowing,
.plant-tags-detail {
  margin-bottom: 1.5rem;
}

.description h4,
.plant-type h4,
.growing-details h4,
.care-requirements h4,
.additional-info h4,
.characteristics h4,
.plant-features h4,
.climate-sowing h4,
.plant-tags-detail h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.75rem;
}

.care-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
}

.care-detail {
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 6px;
  font-size: 0.875rem;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-item {
  background: #ecfdf5;
  color: #065f46;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Alert Styles */
.error-state .alert {
  background: rgba(254, 242, 242, 0.9) !important;
  border-color: rgba(254, 202, 202, 0.6) !important;
  backdrop-filter: blur(8px);
}

.no-results-state .alert {
  background: rgba(239, 246, 255, 0.9) !important;
  border-color: rgba(191, 219, 254, 0.6) !important;
  backdrop-filter: blur(8px);
}

/* Responsive Pagination */
@media (max-width: 768px) {
  .pagination {
    gap: 0.125rem;
    padding: 0.25rem;
  }

  .page-link {
    padding: 0.375rem 0.5rem;
    font-size: 0.875rem;
    min-width: 36px;
  }
}

@media (max-width: 480px) {
  .pagination-controls {
    margin-top: 1.5rem;
  }

  .page-link {
    padding: 0.25rem 0.375rem;
    font-size: 0.75rem;
    min-width: 32px;
  }
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }

  .search-filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input-group {
    max-width: none;
  }

  .filter-buttons {
    justify-content: center;
  }

  .plants-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
  }

  .modal-content {
    margin: 1rem;
    max-height: calc(100vh - 2rem);
  }

  .care-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 1.75rem;
  }

  .plants-grid {
    grid-template-columns: 1fr;
  }

  .filter-buttons {
    flex-direction: column;
  }

  .modal-header,
  .modal-body {
    padding: 1rem;
  }
}
</style>
