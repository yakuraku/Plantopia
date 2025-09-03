<template>
  <!--
    Search Form Container
    Redesigned layout with main search fields and sidebar filters
  -->
  <div class="search-form-container">
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <!-- Page Title -->
        <h1 class="h3 mb-4 text-center fw-bold" style="color: white; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);">Plant Recommendations</h1>

        <!-- Location Input -->
        <div class="mb-3">
          <LocationInput @update:location="updateLocation" />
        </div>

        <!-- Required Fields Row with Search Button -->
        <div class="row g-3 align-items-end five-grid">
          <div class="col-lg-2 col-md-6">
            <DropdownSelect
              id="location-type"
              label="Location Type *"
              placeholder="Select Location"
              :options="locationTypes"
              v-model="formData.locationType"
            />
          </div>

          <div class="col-lg-2 col-md-6">
            <DropdownSelect
              id="sunlight"
              label="Sun Exposure *"
              placeholder="Select Sunlight"
              :options="sunlightOptions"
              v-model="formData.sunlight"
            />
          </div>

          <div class="col-lg-2 col-md-6">
            <DropdownSelect
              id="goal"
              label="Primary Goal *"
              placeholder="Select Goal"
              :options="goalOptions"
              v-model="formData.goal"
            />
          </div>

          <div class="col-lg-2 col-md-6">
            <DropdownSelect
              id="time-to-results"
              label="Time to Results *"
              placeholder="Select Timeline"
              :options="timeToResultsOptions"
              v-model="formData.timeToResults"
            />
          </div>

          <!-- Search Button -->
          <div class="col-lg-2 col-md-12">
            <button class="btn btn-success btn-equal w-100 d-flex align-items-center justify-content-center" @click="handleFindPlants" style="position: relative; z-index: 3;">
              <ArrowRightIcon class="me-2" style="width: 1rem; height: 1rem;" />
              Search
            </button>
          </div>
        </div>

        <!-- Conditional Plant Type Selectors -->
        <div v-if="showEdibleTypes || showOrnamentalTypes" class="row g-3 mt-2">
          <!-- Edible Types -->
          <div v-if="showEdibleTypes" class="col-lg-6 col-md-12">
            <label class="form-label text-white fw-bold mb-2">Edible Types</label>
            <div class="chip-container">
              <div
                v-for="type in edibleTypes"
                :key="`edible-${type}`"
                class="chip"
                :class="{ 'chip-selected': formData.edibleTypes.includes(type) }"
                @click="toggleEdibleType(type)"
              >
                {{ type }}
              </div>
            </div>
          </div>

          <!-- Ornamental Types -->
          <div v-if="showOrnamentalTypes" class="col-lg-6 col-md-12">
            <label class="form-label text-white fw-bold mb-2">Ornamental Types</label>
            <div class="chip-container">
              <div
                v-for="type in ornamentalTypes"
                :key="`ornamental-${type}`"
                class="chip"
                :class="{ 'chip-selected': formData.ornamentalTypes.includes(type) }"
                @click="toggleOrnamentalType(type)"
              >
                {{ type }}
              </div>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="alert alert-danger d-flex align-items-center mt-3" role="alert">
          <ExclamationTriangleIcon class="me-2" style="width: 1.25rem; height: 1.25rem;" />
          {{ error }}
        </div>
      </div>
    </div>

    <!-- Expose filter data for parent component to use in sidebar -->
    <template v-if="$slots.sidebar">
      <slot name="sidebar" :filters="filterData" :updateFilters="updateFilters" />
    </template>

    <!-- Slot for Search Results -->
    <slot />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArrowRightIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import LocationInput from './LocationInput.vue'
import DropdownSelect from './DropdownSelect.vue'

// Extended search parameters interface to match API requirements
interface SearchParams {
  location: string
  locationType: string
  areaM2: number
  sunlight: string
  windExposure: string
  containers: boolean
  containerSizes: string[]
  goal: string
  edibleTypes: string[]
  ornamentalTypes: string[]
  maintainability: string
  watering: string
  timeToResults: string
  seasonIntent: string
  colors: string[]
  fragrant: boolean
  pollenSensitive: boolean
  petsOrToddlers: boolean
  budget: string
  hasBasicTools: boolean
  organicOnly: boolean
}

// Component events - emits search parameters when form is submitted
const emit = defineEmits<{
  'find-plants': [params: SearchParams]
}>()

// Reactive form data containing all search parameters
const formData = ref<SearchParams>({
  location: '',
  locationType: '',
  areaM2: 2.0,
  sunlight: '',
  windExposure: '',
  containers: false,
  containerSizes: [],
  goal: '',
  edibleTypes: [],
  ornamentalTypes: [],
  maintainability: '',
  watering: '',
  timeToResults: '',
  seasonIntent: '',
  colors: [],
  fragrant: false,
  pollenSensitive: false,
  petsOrToddlers: false,
  budget: '',
  hasBasicTools: false,
  organicOnly: false,
})

// Filter data for sidebar (optional fields)
const filterData = ref({
  areaM2: 2.0,
  windExposure: '',
  containers: false,
  containerSizes: [] as string[],
  maintainability: '',
  watering: '',
  seasonIntent: '',
  colors: [] as string[],
  fragrant: false,
  pollenSensitive: false,
  petsOrToddlers: false,
  budget: '',
  hasBasicTools: false,
  organicOnly: false,
})

// Error message state for form validation feedback
const error = ref('')

// Dropdown option arrays for form selects
const locationTypes = ['Indoors', 'Balcony', 'Courtyard', 'Backyard', 'Community Garden']
const sunlightOptions = ['Full Sun (6-8h)', 'Part Sun (3-5h)', 'Bright Shade (1-3h)', 'Low Light (<1h)']
const windExposureOptions = ['Sheltered', 'Moderate', 'Windy']
const goalOptions = ['Edible', 'Ornamental', 'Mixed']
const maintainabilityOptions = ['Low', 'Medium', 'High']
const wateringOptions = ['Low', 'Medium', 'High']
const timeToResultsOptions = ['Quick (<=60d)', 'Standard (60-120d)', 'Patient (>120d)']
const seasonIntentOptions = ['Start Now', 'Happy to Wait']
const budgetOptions = ['Low', 'Medium', 'High']

// Container sizes - shown when containers is true
const containerSizes = ['Small (<=15cm)', 'Medium (16-25cm)', 'Large (26-40cm)', 'Very Large (>40cm)']

// Plant type options - shown conditionally based on goal
const edibleTypes = ['Leafy', 'Fruiting', 'Root', 'Herbs', 'Legumes']
const ornamentalTypes = ['Flowers', 'Foliage', 'Climbers', 'Groundcovers']

// Color options - optional aesthetics
const colorOptions = ['White', 'Yellow', 'Orange', 'Pink', 'Red', 'Purple', 'Blue']

// Predefined location suggestions for user convenience - Melbourne suburbs (names only)
const locationSuggestions = [
  'Melbourne',
  'Richmond',
  'Fitzroy',
  'St Kilda',
  'Carlton',
  'South Yarra',
  'Prahran',
  'Collingwood',
  'Southbank',
  'Docklands',
  'Port Melbourne',
  'Albert Park',
  'Brunswick',
  'Thornbury',
  'Northcote',
  'Hawthorn',
  'Camberwell',
  'Toorak',
  'Armadale',
  'Kensington',
  'Footscray',
  'Yarraville',
  'Williamstown',
  'Brighton',
  'Caulfield'
]

// Computed properties for conditional display
const showEdibleTypes = computed(() => {
  return formData.value.goal === 'Edible' || formData.value.goal === 'Mixed'
})

const showOrnamentalTypes = computed(() => {
  return formData.value.goal === 'Ornamental' || formData.value.goal === 'Mixed'
})

const showContainerSizes = computed(() => {
  return formData.value.containers
})

// Toggle functions for chip selection
const toggleEdibleType = (type: string) => {
  const index = formData.value.edibleTypes.indexOf(type)
  if (index > -1) {
    formData.value.edibleTypes.splice(index, 1)
  } else {
    formData.value.edibleTypes.push(type)
  }
}

const toggleOrnamentalType = (type: string) => {
  const index = formData.value.ornamentalTypes.indexOf(type)
  if (index > -1) {
    formData.value.ornamentalTypes.splice(index, 1)
  } else {
    formData.value.ornamentalTypes.push(type)
  }
}

const toggleContainerSize = (size: string) => {
  const index = formData.value.containerSizes.indexOf(size)
  if (index > -1) {
    formData.value.containerSizes.splice(index, 1)
  } else {
    formData.value.containerSizes.push(size)
  }
}

const toggleColor = (color: string) => {
  const index = formData.value.colors.indexOf(color)
  if (index > -1) {
    formData.value.colors.splice(index, 1)
  } else {
    formData.value.colors.push(color)
  }
}

// Updates location in form data when LocationInput component emits change
const updateLocation = (location: string) => {
  formData.value.location = location
}

// Update filters from sidebar
const updateFilters = (filters: typeof filterData.value) => {
  filterData.value = { ...filters }
  // Sync filter data with form data
  Object.assign(formData.value, filters)
}

// Validates user location input - accepts suburb names only
const validateLocation = (loc: string): boolean => {
  // Check if location matches any predefined suggestions
  const matchesSuggestion = locationSuggestions.some((suggestion) =>
    suggestion.toLowerCase().includes(loc.toLowerCase())
  )

  // Allow if matches suggestions OR is a valid suburb name (letters and spaces only)
  const isValidSuburbName = /^[a-zA-Z\s]+$/.test(loc.trim()) && loc.trim().length >= 2

  return matchesSuggestion || isValidSuburbName
}

// Handles form submission - validates data and emits to parent component
const handleFindPlants = () => {
  // Clear any previous errors
  error.value = ''

  // Validate required fields
  if (!formData.value.location) {
    error.value = 'Please enter a location'
    return
  }

  if (!validateLocation(formData.value.location)) {
    error.value = 'Please enter a valid Melbourne suburb'
    return
  }

  if (!formData.value.locationType) {
    error.value = 'Please select a location type'
    return
  }

  if (!formData.value.sunlight) {
    error.value = 'Please select sun exposure'
    return
  }

  if (!formData.value.goal) {
    error.value = 'Please select your primary goal'
    return
  }



  if (!formData.value.timeToResults) {
    error.value = 'Please select your preferred time to results'
    return
  }

  // Emit validated form data to parent component
  emit('find-plants', formData.value)
}
</script>

<style scoped>
.search-form-container {
  position: relative;
  z-index: 2;
  margin: 0; /* Remove any default margin */
}

.card {
  background: transparent !important;
  backdrop-filter: none;
  border: 0 !important;
  box-shadow: none !important;
  margin: 0; /* Ensure no margin on card */
}

/* Make the second row exactly five equal columns under the location input */
.five-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.75rem;
}

.five-grid > div {
  width: 100% !important;
}

@media (max-width: 1199.98px) {
  .five-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 767.98px) {
  .five-grid {
    grid-template-columns: 1fr;
  }
}

/* Custom button hover effects */
.btn-success:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3);
}

/* Match dropdown height (padding 1rem) and pill radius */
.btn-equal {
  padding: 1rem;
  border-radius: 1.5rem;
  height: auto;
}

/* Ensure consistent spacing */
@media (max-width: 991.98px) {
  .row.g-3 > * {
    margin-bottom: 0.75rem;
  }
}

@media (max-width: 767.98px) {
  .h3 {
    font-size: 1.25rem !important;
  }
}

/* Chip Styles */
.chip-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.chip {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 1.5rem;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.chip:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-1px);
}

.chip-selected {
  background: rgba(52, 211, 153, 0.8) !important;
  border-color: rgba(52, 211, 153, 1) !important;
  color: white;
  box-shadow: 0 4px 12px rgba(52, 211, 153, 0.3);
}

.chip-selected:hover {
  background: rgba(16, 185, 129, 0.9) !important;
  border-color: rgba(16, 185, 129, 1) !important;
}
</style>
