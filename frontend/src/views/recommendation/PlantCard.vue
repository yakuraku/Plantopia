<template>
  <!-- 
    Single Plant Card Component
    Displays an individual plant with image, details, icons, and action button
    Emits 'select' event when clicked to open plant details modal
  -->
  <div class="plant-card" @click="$emit('select', plant)">
    <!-- Plant Image Section -->
    <div class="plant-card-image">

      
      <img 
        :src="getImageSource()"
        :alt="plant.name"
        class="plant-image"
        @error="handleImageError"
        @load="() => {}"
      />
    </div>

    <!-- Plant Information Section -->
    <div class="plant-card-content">
      <!-- Plant Name with Score -->
      <div class="plant-header">
        <h3 class="plant-card-title">{{ plant.name }}</h3>
        <div class="plant-score" v-if="plant.score">
          {{ plant.score.toFixed(1) }}/100
        </div>
      </div>
      
      <!-- Plant Description -->
      <p class="plant-card-description">{{ plant.description }}</p>

      <!-- Plant Care Requirements -->
      <div class="plant-card-requirements">
        <div class="requirement-item">
          <span class="requirement-label">Sun:</span>
          <span class="requirement-value">{{ getSunIcon(plant.sunlight) }}</span>
        </div>
        <div class="requirement-item">
          <span class="requirement-label">Water:</span>
          <span class="requirement-value">{{ getWaterIcon(plant.water) }}</span>
        </div>
        <div class="requirement-item">
          <span class="requirement-label">Care:</span>
          <span class="requirement-value">{{ getEffortIcon(plant.effort) }}</span>
        </div>
      </div>

      <!-- Why This Plant is Recommended Section -->
      <div class="why-recommended">
        <strong>Why Recommended:</strong> 
        <span v-if="Array.isArray(plant.whyRecommended)">
          {{ plant.whyRecommended.join(' ') }}
        </span>
        <span v-else>
          {{ plant.whyRecommended }}
        </span>
      </div>

      <!-- Action Button to View Plant Details -->
      <button class="learn-more-button" @click.stop="$emit('select', plant)">
        Learn More
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Plant } from '@/services/api'

// Component props - receives plant data
const props = defineProps<{
  plant: Plant
}>()

// Component events - emits when plant is selected
defineEmits<{
  select: [plant: Plant]
}>()

// State for handling image loading errors
const imageError = ref(false)
const currentImageUrl = ref('')
const urlIndex = ref(0)
const allPossibleUrls = ref<string[]>([])

// Function to get image source (Base64, URL, or category placeholder)
const getImageSource = (): string => {
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
  
  // Priority 3: Use category-specific placeholder image
  return getCategoryPlaceholder()
}

// Function to get category-specific placeholder image
const getCategoryPlaceholder = (): string => {
  const category = props.plant.category?.toLowerCase()
  
  switch (category) {
    case 'flower':
      return '/Flower.jpg'
    case 'herb':
      return '/Herb.jpg'
    case 'vegetable':
      return '/Vegetable.jpg'
    default:
      return '/placeholder-plant.svg'
  }
}

// Function to construct full image URL (fallback method)
const getImageUrl = (imagePath: string): string => {
  // If the path is already a full URL, use it as is
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }
  
  // Base URL for your backend
  const baseUrl = process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:8000'
  
  // For separated frontend/backend projects, we need API endpoints
  const possibleUrls = [
    `${baseUrl}/api/plant-image/${encodeURIComponent(imagePath)}`,
    `${baseUrl}/api/plant-image?path=${encodeURIComponent(imagePath)}`,
    `${baseUrl}/api/images/${encodeURIComponent(imagePath)}`,
    `${baseUrl}/image/${encodeURIComponent(imagePath)}`,
    `${baseUrl}/static/${imagePath}`,           
    `${baseUrl}/media/${imagePath}`,            
  ]
  
  // Store all possible URLs for fallback
  allPossibleUrls.value = possibleUrls
  urlIndex.value = 0
  
  currentImageUrl.value = possibleUrls[0]
  return possibleUrls[0]
}

// Handle image loading errors with automatic fallback
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  
  // If we have alternative URLs to try
  if (allPossibleUrls.value.length > 0) {
    // Try the next URL if available
    urlIndex.value++
    if (urlIndex.value < allPossibleUrls.value.length) {
      const nextUrl = allPossibleUrls.value[urlIndex.value]
      currentImageUrl.value = nextUrl
      img.src = nextUrl
      return
    }
  }
  
  // All URLs failed or no URLs to try, fall back to category placeholder
  const placeholderUrl = getCategoryPlaceholder()
  
  // Avoid infinite loop if placeholder image also fails
  if (img.src !== placeholderUrl) {
    img.src = placeholderUrl
  } else {
    // If even the placeholder fails, hide the image
    imageError.value = true
    img.style.display = 'none'
  }
}

// Helper function to get appropriate sun icon based on sunlight requirement
const getSunIcon = (sunlight: string): string => {
  switch (sunlight) {
    case 'full': return 'Full Sun'     // Full sun
    case 'partial': return 'Partial'   // Partial sun/shade
    case 'shade': return 'Shade'     // Shade
    default: return 'Full Sun'
  }
}

// Helper function to get appropriate water icon based on watering needs
const getWaterIcon = (water: string): string => {
  switch (water) {
    case 'low': return 'Low'           // Low water needs
    case 'medium': return 'Medium'      // Medium water needs
    case 'high': return 'High'      // High water needs
    default: return 'Low'
  }
}

// Helper function to get appropriate effort icon based on maintenance level
const getEffortIcon = (effort: string): string => {
  switch (effort) {
    case 'low': return 'Low'      // Low maintenance
    case 'medium': return 'Medium'   // Medium maintenance
    case 'high': return 'High'     // High maintenance
    default: return 'Low'
  }
}
</script>

<style scoped>
/* Main plant card container styling */
.plant-card {
  border: 2px solid #a7f3d0;      /* Light green border */
  border-radius: 1rem;            /* Rounded corners */
  background: white;              /* White background */
  overflow: hidden;               /* Hide overflow content */
  transition: all 0.3s ease;     /* Smooth hover transition */
  cursor: pointer;                /* Show pointer cursor */
}

/* Hover effect for plant card */
.plant-card:hover {
  transform: translateY(-4px);                        /* Lift card up */
  box-shadow: 0 12px 30px rgba(5, 150, 105, 0.15);  /* Add shadow */
  border-color: #059669;                              /* Darker green border */
}

/* Plant image section styling */
.plant-card-image {
  height: 200px;                                      /* Increased height for better image display */
  background: linear-gradient(135deg, #f0fdf4, #dcfce7); /* Green gradient */
  border-bottom: 2px solid #a7f3d0;                  /* Bottom border */
  display: flex;                                      /* Center content */
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;                                   /* Hide overflow for cropped images */
}

/* Actual plant image styling */
.plant-image {
  width: 100%;
  height: 100%;
  object-fit: cover;                                  /* Cover the entire area while maintaining aspect ratio */
  object-position: center;                            /* Center the image */
  transition: transform 0.3s ease;                   /* Smooth hover effect */
}

.plant-card:hover .plant-image {
  transform: scale(1.05);                             /* Slight zoom on hover */
}

/* Image error handling - hide broken images */
.plant-image[style*="display: none"] {
  display: none !important;
}



/* Plant card content container */
.plant-card-content {
  padding: 1.5rem;              /* Inner spacing */
}

/* Plant header with title and score */
.plant-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
  gap: 0.5rem;
}

/* Plant name styling */
.plant-card-title {
  font-size: 1.125rem;          /* Larger font size */
  font-weight: 600;             /* Semi-bold */
  color: #1c3d21;               /* Dark green color */
  margin: 0;                    /* Remove default margin */
  flex: 1;                      /* Take available space */
}

/* Plant score styling */
.plant-score {
  background: #047857;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

/* Plant description styling */
.plant-card-description {
  color: #1c3d21;               /* Dark green color */
  font-size: 0.875rem;          /* Smaller font size */
  margin-bottom: 1rem;          /* Space below */
  line-height: 1.5;             /* Better line spacing */
}

/* Care requirement icons container */
.plant-card-requirements {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  justify-content: space-between;
}

.requirement-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  flex: 1;
}

.requirement-label {
  font-weight: 600;
  color: #047857;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.requirement-value {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

/* Why recommended section styling */
.why-recommended {
  font-size: 0.875rem;                               /* Smaller font */
  color: #1c3d21;                                     /* Dark green text */
  margin-bottom: 1rem;                                /* Space below */
  padding: 0.75rem;                                   /* Inner padding */
  background: linear-gradient(135deg, #f0fdf4, #dcfce7); /* Light green gradient */
  border-radius: 0.75rem;                             /* Rounded corners */
  border-left: 3px solid #1c3d21;                    /* Left accent border */
  font-weight: 500;                                   /* Medium font weight */
}

/* Learn more button styling */
.learn-more-button {
  width: 100%;                  /* Full width */
  padding: 0.75rem;             /* Inner spacing */
  background: transparent;      /* Transparent background */
  border: 2px solid #1c3d21;   /* Dark green border */
  color: #1c3d21;               /* Dark green text */
  border-radius: 0.75rem;       /* Rounded corners */
  font-weight: 600;             /* Semi-bold text */
  cursor: pointer;              /* Show pointer cursor */
  transition: all 0.2s;        /* Smooth hover transition */
}

/* Button hover effect */
.learn-more-button:hover {
  background: #1c3d21;                              /* Dark green background */
  color: white;                                     /* White text */
  transform: translateY(-1px);                     /* Slight lift */
  box-shadow: 0 4px 12px rgba(28, 61, 33, 0.3);   /* Add shadow */
}
</style>