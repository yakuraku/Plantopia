<template>
  <div class="view-history" v-if="historyPlants.length > 0">
    <h3 class="history-title">View History</h3>
    <div class="history-grid">
      <div 
        v-for="plant in historyPlants" 
        :key="plant.id"
        class="history-item"
        @click="$emit('select-plant', plant)"
      >
        <div class="history-image">
          <img 
            v-if="getImageSource(plant)" 
            :src="getImageSource(plant)" 
            :alt="plant.name" 
            @error="handleImageError"
          />
          <!-- Fallback placeholder if no image or image fails to load -->
          <div v-else class="image-placeholder">
            <div class="placeholder-icon">Plant</div>
          </div>
        </div>
        <div class="history-name">{{ plant.name }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Plant } from '@/services/api'
import { getViewHistory } from '@/services/viewHistory'

// Props and emits
defineEmits<{
  'select-plant': [plant: Plant]
}>()

// Reactive state
const historyPlants = ref<Plant[]>([])

// Load history on component mount
onMounted(() => {
  loadHistory()
})

// Load view history from localStorage
const loadHistory = () => {
  historyPlants.value = getViewHistory()
}

// Function to get image source (Base64 or URL) - same logic as PlantDetailModal
const getImageSource = (plant: Plant): string => {
  if (!plant) return ''
  
  // Priority 1: Use Base64 data if available
  if (plant.imageData) {
    // Check if it's already a data URL
    if (plant.imageData.startsWith('data:')) {
      return plant.imageData
    }
    
    // If it's just the base64 string, add the data URL prefix
    return `data:image/jpeg;base64,${plant.imageData}`
  }
  
  // Priority 2: Fall back to URL construction if no Base64 data
  if (plant.imagePath) {
    return getImageUrl(plant.imagePath)
  }
  
  return ''
}

// Function to construct full image URL (fallback method)
const getImageUrl = (imagePath: string): string => {
  // If the path is already a full URL, use it as is
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }
  
  // Otherwise, construct URL relative to API base
  const primaryUrl = process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000'
  return `${primaryUrl}${imagePath.startsWith('/') ? '' : '/'}${imagePath}`
}

// Handle image loading errors
const handleImageError = (event: Event) => {
  console.warn('Failed to load plant image in history:', event)
}

// Expose method to refresh history (called when new plant is viewed)
defineExpose({
  refreshHistory: loadHistory
})
</script>

<style scoped>
.view-history {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(8px);
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-top: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.history-title {
  color: #0d9488;
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
  text-align: center;
}

.history-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
  justify-items: center;
}

.history-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  padding: 0.75rem;
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(13, 148, 136, 0.2);
}

.history-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(13, 148, 136, 0.15);
  background: rgba(255, 255, 255, 0.9);
}

.history-image {
  width: 80px;
  height: 80px;
  border-radius: 0.5rem;
  overflow: hidden;
  margin-bottom: 0.5rem;
  border: 2px solid rgba(13, 148, 136, 0.1);
}

.history-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  color: #6b7280;
}

.placeholder-icon {
  font-size: 0.75rem;
  font-weight: 600;
  text-align: center;
  color: #059669;
}

.history-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  text-align: center;
  line-height: 1.2;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* Responsive adjustments */
@media (max-width: 767.98px) {
  .history-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 0.75rem;
  }
  
  .history-image {
    width: 60px;
    height: 60px;
  }
  
  .history-name {
    font-size: 0.75rem;
    max-width: 80px;
  }
  
  .view-history {
    padding: 1rem;
  }
}

@media (max-width: 575.98px) {
  .history-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}
</style>
