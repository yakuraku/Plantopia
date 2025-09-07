<template>
  <!-- 
    Plant Detail Modal Component
    Full-screen modal displaying comprehensive plant information
    Includes plant image, care requirements, benefits, and sustainability data
  -->
  <div v-if="plant" class="plant-detail-overlay" @click="$emit('close')">
    <!-- Modal Container - prevents close on modal content click -->
    <div class="plant-detail-modal" @click.stop>
      <!-- Back/Close Button -->
      <button @click="$emit('close')" class="back-button">
        <ArrowLeftIcon class="w-5 h-5" />
        Back
      </button>

      <!-- Main Content Container with Top Image Layout -->
      <div class="plant-detail-container">
        <!-- Top Section - Plant Image -->
        <div class="plant-detail-image">
          <img 
            v-if="(plant.imageData || plant.imagePath) && !imageError" 
            :src="getImageSource()"
            :alt="plant.name"
            class="plant-image"
            @error="handleImageError"
          />
          <!-- Fallback placeholder if no image or image fails to load -->
          <div v-if="(!plant.imageData && !plant.imagePath) || imageError" class="image-placeholder">
            <div class="placeholder-icon">Plant</div>
            <span class="placeholder-text">{{ plant.category || 'Plant' }}</span>
          </div>
        </div>

        <!-- Bottom Section - Plant Information -->
        <div class="plant-detail-info">
          <!-- Plant Header -->
          <div class="plant-header">
            <h2 class="plant-detail-title">{{ plant.name }}</h2>
            <p class="plant-detail-scientific">{{ plant.scientificName }}</p>
            <div class="recommendation-score" v-if="plant.score">
              <span class="score-label">Recommendation Score:</span>
              <span class="score-value">{{ plant.score.toFixed(1) }}/100</span>
            </div>
          </div>

          <!-- Information Grid -->
          <div class="info-grid">
            <!-- Description Section -->
            <div class="info-card">
              <h3 class="card-title">Description:</h3>
              <div class="card-content plant-description" v-html="renderedDescription"></div>
              <div class="recommendation-reasons" v-if="plant.whyRecommended?.length">
                <p v-for="reason in plant.whyRecommended" :key="reason" class="reason-item">
                  - {{ reason }}
                </p>
              </div>
            </div>

            <!-- Sowing Information Card -->
            <div class="info-card" v-if="plant.sowingInfo">
              <h3 class="card-title">Sowing Information:</h3>
              <div class="card-content">
                <div class="info-item">
                  <span class="info-icon">Climate:</span>
                  <span>{{ plant.sowingInfo.climateZone }}</span>
                </div>
                <div class="info-item">
                  <span class="info-icon">Months:</span>
                  <span>{{ plant.sowingInfo.months.join(', ') }}</span>
                </div>
                <div class="info-item">
                  <span class="info-icon">Season:</span>
                  <span>{{ plant.sowingInfo.seasonLabel }}</span>
                </div>
                <div class="info-item" v-if="plant.timeToMaturity">
                  <span class="info-icon">Time:</span>
                  <span>{{ plant.timeToMaturity }} days</span>
                </div>
              </div>
            </div>

            <!-- Growing Requirements Card -->
            <div class="info-card">
              <h3 class="card-title">Growing Requirements:</h3>
              <div class="card-content">
                <div class="info-item">
                  <span class="info-icon">Sun:</span>
                  <span>{{ formatSunlight(plant.sunlight) }}</span>
                </div>
                <div class="info-item">
                  <span class="info-icon">Water:</span>
                  <span>{{ plant.water }}</span>
                </div>
                <div class="info-item">
                  <span class="info-icon">Effort:</span>
                  <span>{{ plant.effort }} Maintenance</span>
                </div>
              </div>
            </div>

            <!-- Sustainability Impact Card -->
            <div class="info-card">
              <h3 class="card-title">Sustainability Impact:</h3>
              <div class="card-content">
                <div class="info-item">
                  <span class="info-icon">Cooling:</span>
                  <span>{{ plant.coolingEffect }}</span>
                </div>
                <div class="info-item">
                  <span class="info-icon">Carbon:</span>
                  <span>{{ plant.carbonReduction }}</span>
                </div>
                <div class="info-item">
                  <span class="info-icon">Drought:</span>
                  <span>{{ plant.droughtTolerance }}</span>
                </div>
              </div>
            </div>

            <!-- Plant Benefits Card -->
            <div class="info-card">
              <h3 class="card-title">Benefits:</h3>
              <div class="card-content benefits-grid">
                <!-- Positive Benefits (Green checkmarks) -->
                <div
                  v-if="plant.benefits.petSafe"
                  class="benefit-item benefit-positive"
                >
                  <span class="benefit-icon">+</span>
                  <span>Pet Safe</span>
                </div>
                <div
                  v-if="plant.benefits.fragrant"
                  class="benefit-item benefit-positive"
                >
                  <span class="benefit-icon">+</span>
                  <span>Attracts Birds</span>
                </div>
                <div
                  v-if="plant.benefits.airPurifying"
                  class="benefit-item benefit-positive"
                >
                  <span class="benefit-icon">+</span>
                  <span>Air Purifying</span>
                </div>
                <div v-if="plant.benefits.edible" class="benefit-item benefit-positive">
                  <span class="benefit-icon">+</span>
                  <span>Edible</span>
                </div>
                <div
                  v-if="plant.benefits.droughtResistant"
                  class="benefit-item benefit-positive"
                >
                  <span class="benefit-icon">+</span>
                  <span>Drought Resistant</span>
                </div>
                <div
                  v-if="plant.benefits.containerFriendly"
                  class="benefit-item benefit-positive"
                >
                  <span class="benefit-icon">+</span>
                  <span>Container Friendly</span>
                </div>
                <div
                  v-if="plant.benefits.indoorSuitable"
                  class="benefit-item benefit-positive"
                >
                  <span class="benefit-icon">+</span>
                  <span>Indoor Suitable</span>
                </div>
                
                <!-- Negative Benefits (Red X marks) -->
                <div
                  v-if="!plant.benefits.edible"
                  class="benefit-item benefit-negative"
                >
                  <span class="benefit-icon">-</span>
                  <span>Not Edible</span>
                </div>
                
                <!-- Warning Benefits (Yellow triangle) -->
                <div
                  v-if="!plant.benefits.petSafe"
                  class="benefit-item benefit-warning"
                >
                  <ExclamationTriangleIcon class="w-4 h-4" />
                  <span>Not Pet Safe</span>
                </div>
              </div>
            </div>

            <!-- Care Tips Card -->
            <div class="info-card">
              <h3 class="card-title">Care Tips:</h3>
              <div class="card-content">
                <ul class="care-tips-list">
                  <li>Plant in sunny spot with well-drained soil</li>
                  <li>Water deeply once per week in summer</li>
                  <li>Prune lightly after flowering</li>
                </ul>
                <!-- Link to Guidance Video -->
                <a href="#" class="guidance-video-link"> Guidance video </a>
              </div>
            </div>
          </div>

          <!-- View History Section -->
          <ViewHistory 
            ref="viewHistoryRef"
            @select-plant="handleHistoryPlantSelect"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ArrowLeftIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import type { Plant } from '@/services/api'
import { addToViewHistory } from '@/services/viewHistory'
import ViewHistory from './ViewHistory.vue'
import { renderMarkdown } from '@/services/markdownService'

// Component props - receives plant data or null when modal is closed
const props = defineProps<{
  plant: Plant | null
}>()

// Component events - emits close event when modal is dismissed
const emit = defineEmits<{
  close: []
  'select-plant': [plant: Plant]
}>()

// State for handling image loading errors
const imageError = ref(false)

// Markdown rendering computed property
const renderedDescription = computed(() => {
  if (!props.plant || !props.plant.description) {
    return 'No description available.'
  }
  return renderMarkdown(props.plant.description)
})

// Reference to ViewHistory component
const viewHistoryRef = ref<InstanceType<typeof ViewHistory> | null>(null)

// Watch for plant changes and add to view history
watch(() => props.plant, (newPlant) => {
  if (newPlant) {
    addToViewHistory(newPlant)
    // Refresh history display after a short delay to ensure the new item is saved
    setTimeout(() => {
      viewHistoryRef.value?.refreshHistory()
    }, 100)
  }
}, { immediate: true })

// Handle plant selection from history
const handleHistoryPlantSelect = (plant: Plant) => {
  emit('select-plant', plant)
}

// Function to get image source (Base64 or URL)
const getImageSource = (): string => {
  if (!props.plant) return ''
  
  // Priority 1: Use Base64 data if available
  if (props.plant.imageData) {
    // Check if it's already a data URL
    if (props.plant.imageData.startsWith('data:')) {
      return props.plant.imageData
    }
    
    // If it's just the base64 string, add the data URL prefix
    return `data:image/jpeg;base64,${props.plant.imageData}`
  }
  
  // Priority 2: Fall back to URL construction if no Base64 data
  if (props.plant.imagePath) {
    return getImageUrl(props.plant.imagePath)
  }
  
  return ''
}

// Function to construct full image URL (fallback method)
const getImageUrl = (imagePath: string): string => {
  // If the path is already a full URL, use it as is
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }
  
  // If it's a relative path, construct URL with backend base
  const primaryUrl = process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000'
  const fallbackUrl = process.env.NODE_ENV === 'production' ? '/api' : 'http://127.0.0.1:8000'
  
  // Try primary URL first, fallback URL if needed
  const fullUrl = `${primaryUrl}/static/${imagePath}`
  return fullUrl
}

// Handle image loading errors
const handleImageError = (event: Event) => {
  imageError.value = true
  
  // Hide the broken image and show placeholder
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}

// Helper function to format sunlight requirements for display
const formatSunlight = (sunlight: string): string => {
  switch (sunlight) {
    case 'full':
      return 'Full Sun'
    case 'partial':
      return 'Partial Sun'
    case 'shade':
      return 'Shade'
    default:
      return sunlight // Return original value if not recognized
  }
}
</script>

<style scoped>
.plant-detail-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  backdrop-filter: blur(8px);
}

.plant-detail-modal {
  background: white;
  border-radius: 1.5rem;
  padding: 2rem;
  max-width: 1200px;
  width: 95%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: white;
  border: 2px solid #a7f3d0;
  border-radius: 0.75rem;
  color: #047857;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 2rem;
}

.back-button:hover {
  background: #f0fdf4;
  border-color: #059669;
}

.plant-detail-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.plant-detail-image {
  width: fit-content;
  max-width: 100%;
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #a7f3d0;
  margin: 0 auto 1rem auto;
  padding: 0.5rem;
  overflow: hidden;
  overflow: hidden;
}

.plant-detail-image .plant-image {
  max-width: 100%;
  max-height: 250px;
  height: auto;
  object-fit: contain;
  object-position: center;
  border-radius: 0.875rem;
  display: block;
}

.plant-detail-image .image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: #059669;
  text-align: center;
}

.plant-detail-image .placeholder-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.7;
}

.plant-detail-image .placeholder-text {
  font-size: 1.125rem;
  font-weight: 600;
  text-transform: capitalize;
  opacity: 0.8;
}

.plant-detail-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.plant-header {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #a7f3d0;
}

.recommendation-score {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.score-label {
  font-weight: 600;
  color: #047857;
}

.score-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #059669;
  background: #f0fdf4;
  padding: 0.25rem 0.75rem;
  border-radius: 0.5rem;
  border: 2px solid #a7f3d0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.info-card {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 1rem;
  padding: 1.5rem;
  transition: all 0.2s;
}

.info-card:hover {
  border-color: #a7f3d0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #047857;
  margin: 0 0 1rem 0;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 0.5rem;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  background: white;
  border-radius: 0.5rem;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #e2e8f0;
  flex-wrap: nowrap;
}

.info-item:last-child {
  border-bottom: none;
}

.info-icon {
  font-size: 0.875rem;
  font-weight: 600;
  color: #047857;
  min-width: 4rem;
  flex-shrink: 0;
}

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.5rem;
}

.plant-basic-info {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.plant-detail-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #047857;
  margin: 0;
}

.plant-detail-scientific {
  font-size: 1rem;
  color: #059669;
  font-style: italic;
  margin: 0;
}

.plant-section h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #047857;
  margin-bottom: 0.5rem;
}

.plant-section p {
  color: #059669;
  line-height: 1.6;
  margin: 0;
}

.requirement-list,
.impact-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.requirement-item,
.impact-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #047857;
  font-weight: 500;
}

.requirement-icon,
.impact-icon {
  font-size: 1rem;
}

.recommendation-reasons {
  margin-top: 0.5rem;
}

.reason-item {
  color: #059669;
  line-height: 1.5;
  margin: 0.25rem 0;
  font-size: 0.875rem;
}

.sowing-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.sowing-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #047857;
  font-weight: 500;
}

.sowing-icon {
  font-size: 1rem;
}

.benefits-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.benefit-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.benefit-positive {
  background: linear-gradient(135deg, #f0fdf4, #dcfce7);
  color: #047857;
}

.benefit-negative {
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
  color: #991b1b;
}

.benefit-warning {
  background: linear-gradient(135deg, #fef3c7, #fde68a);
  color: #92400e;
}

.benefit-icon {
  font-size: 1rem;
}

.care-tips-section h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #047857;
  margin-bottom: 0.5rem;
}

.care-tips-list {
  list-style: none;
  padding: 0;
  margin: 0 0 1rem 0;
}

.care-tips-list li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #a7f3d0;
  color: #059669;
  font-weight: 500;
}

.care-tips-list li:last-child {
  border-bottom: none;
}

.guidance-video-link {
  display: inline-block;
  color: #047857;
  text-decoration: underline;
  font-weight: 600;
  transition: color 0.2s;
}

.guidance-video-link:hover {
  color: #065f46;
}

.w-5 {
  width: 1.25rem;
}
.h-5 {
  height: 1.25rem;
}
.w-4 {
  width: 1rem;
}
.h-4 {
  height: 1rem;
}

@media (max-width: 768px) {
  .plant-detail-modal {
    width: 98%;
    padding: 1rem;
    max-height: 95vh;
  }
  
  .plant-detail-image {
    width: fit-content;
    max-width: 95%;
    padding: 0.25rem;
  }
  
  .plant-detail-image .plant-image {
    max-height: 200px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .info-card {
    padding: 1rem;
  }
  
  .benefits-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .plant-detail-modal {
    padding: 0.75rem;
  }
  
  .plant-detail-image {
    width: fit-content;
    max-width: 98%;
    padding: 0.25rem;
  }
  
  .plant-detail-image .plant-image {
    max-height: 150px;
  }
  
  .plant-detail-title {
    font-size: 1.25rem;
  }
}
</style>