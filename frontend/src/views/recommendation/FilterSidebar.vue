<template>
  <!--
    Filter Sidebar Component
    Contains all optional search parameters as filters
  -->
  <div class="filter-sidebar" :class="{ 'expanded': isFilterExpanded }">
    <!-- Filter Header -->
    <div class="filter-header">
      <button
        class="main-filter-header"
        @click="toggleMainFilter"
        :class="{ 'expanded': isFilterExpanded }"
      >
        <div class="filter-circle-container">
          <div class="filter-circle">
            <img src="/whiteicon.jpg" alt="Filter Icon" class="filter-icon" />
            <span class="filter-text">Filter</span>
          </div>
        </div>
      </button>
    </div>

    <!-- All Filters Section -->
    <div class="filter-section" v-show="isFilterExpanded">

      <!-- Area M2 Collapsible -->
      <div class="collapsible-filter">
        <button
          class="collapsible-header"
          @click="toggleFilter('areaM2')"
          :class="{ 'expanded': expandedFilters.areaM2 }"
        >
          <span>Area Size (m²)</span>
          <ChevronDownIcon class="collapsible-icon" />
        </button>
        <div class="collapsible-content" v-show="expandedFilters.areaM2">
          <div class="collapsible-options">
            <label class="option-label">
              <input
                type="number"
                min="0.1"
                step="0.1"
                v-model="localFilters.areaM2"
                class="option-input"
                placeholder="2.0"
              >
              <span class="option-text">Square meters</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Wind Exposure Collapsible -->
      <div class="collapsible-filter">
        <button
          class="collapsible-header"
          @click="toggleFilter('windExposure')"
          :class="{ 'expanded': expandedFilters.windExposure }"
        >
          <span>Wind Exposure</span>
          <ChevronDownIcon class="collapsible-icon" />
        </button>
        <div class="collapsible-content" v-show="expandedFilters.windExposure">
          <div class="collapsible-options">
            <label v-for="option in windExposureOptions" :key="option" class="option-label">
              <input
                type="radio"
                :id="'windExposure-' + option"
                name="windExposure"
                :value="option"
                :checked="localFilters.windExposure === option"
                @click="handleRadioToggle('windExposure', option)"
                class="option-radio"
              >
              <span class="option-text">{{ option }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Using Containers Collapsible -->
      <div class="collapsible-filter">
        <button
          class="collapsible-header"
          @click="toggleFilter('containers')"
          :class="{ 'expanded': expandedFilters.containers }"
        >
          <span>Using Containers</span>
          <ChevronDownIcon class="collapsible-icon" />
        </button>
        <div class="collapsible-content" v-show="expandedFilters.containers">
          <div class="collapsible-options">
            <label class="option-label">
              <input
                type="checkbox"
                v-model="localFilters.containers"
                class="option-checkbox"
              >
              <span class="option-text">Yes</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Container Sizes Collapsible -->
      <div class="collapsible-filter" v-show="localFilters.containers">
        <button
          class="collapsible-header"
          @click="toggleFilter('containerSizes')"
          :class="{ 'expanded': expandedFilters.containerSizes }"
        >
          <span>Container Sizes</span>
          <ChevronDownIcon class="collapsible-icon" />
        </button>
        <div class="collapsible-content" v-show="expandedFilters.containerSizes">
          <div class="collapsible-options">
            <label v-for="size in containerSizes" :key="size" class="option-label">
              <input
                type="checkbox"
                :id="'containerSizes-' + size"
                :name="'containerSizes-' + size"
                :value="size"
                v-model="localFilters.containerSizes"
                class="option-checkbox"
              >
              <span class="option-text">{{ size }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Maintenance Level Collapsible -->
      <div class="collapsible-filter">
        <button
          class="collapsible-header"
          @click="toggleFilter('maintainability')"
          :class="{ 'expanded': expandedFilters.maintainability }"
        >
          <span>Maintenance Level</span>
          <ChevronDownIcon class="collapsible-icon" />
        </button>
        <div class="collapsible-content" v-show="expandedFilters.maintainability">
          <div class="collapsible-options">
            <label v-for="option in maintainabilityOptions" :key="option" class="option-label">
              <input
                type="radio"
                :id="'maintainability-' + option"
                name="maintainability"
                :value="option"
                :checked="localFilters.maintainability === option"
                @click="handleRadioToggle('maintainability', option)"
                class="option-radio"
              >
              <span class="option-text">{{ option }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Watering Frequency Collapsible -->
      <div class="collapsible-filter">
        <button
          class="collapsible-header"
          @click="toggleFilter('watering')"
          :class="{ 'expanded': expandedFilters.watering }"
        >
          <span>Watering Frequency</span>
          <ChevronDownIcon class="collapsible-icon" />
        </button>
        <div class="collapsible-content" v-show="expandedFilters.watering">
          <div class="collapsible-options">
            <label v-for="option in wateringOptions" :key="option" class="option-label">
              <input
                type="radio"
                :id="'watering-' + option"
                name="watering"
                :value="option"
                :checked="localFilters.watering === option"
                @click="handleRadioToggle('watering', option)"
                class="option-radio"
              >
              <span class="option-text">{{ option }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Season Intent Collapsible -->
      <div class="collapsible-filter">
        <button
          class="collapsible-header"
          @click="toggleFilter('seasonIntent')"
          :class="{ 'expanded': expandedFilters.seasonIntent }"
        >
          <span>When to Start</span>
          <ChevronDownIcon class="collapsible-icon" />
        </button>
        <div class="collapsible-content" v-show="expandedFilters.seasonIntent">
          <div class="collapsible-options">
            <label v-for="option in seasonIntentOptions" :key="option" class="option-label">
              <input
                type="radio"
                :id="'seasonIntent-' + option"
                name="seasonIntent"
                :value="option"
                :checked="localFilters.seasonIntent === option"
                @click="handleRadioToggle('seasonIntent', option)"
                class="option-radio"
              >
              <span class="option-text">{{ option }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Colors Collapsible -->
      <div class="collapsible-filter">
        <button
          class="collapsible-header"
          @click="toggleFilter('colors')"
          :class="{ 'expanded': expandedFilters.colors }"
        >
          <span>Preferred Colors</span>
          <ChevronDownIcon class="collapsible-icon" />
        </button>
        <div class="collapsible-content" v-show="expandedFilters.colors">
          <div class="collapsible-options">
            <label v-for="color in colorOptions" :key="color" class="option-label">
              <input
                type="radio"
                name="preferred-color"
                :id="'colors-' + color"
                :value="color"
                v-model="preferredColor"
                class="option-radio"
              >
              <span class="option-text">{{ color }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Fragrant Plants Collapsible -->
      <div class="collapsible-filter">
        <button
          class="collapsible-header"
          @click="toggleFilter('fragrant')"
          :class="{ 'expanded': expandedFilters.fragrant }"
        >
          <span>Fragrant Plants</span>
          <ChevronDownIcon class="collapsible-icon" />
        </button>
        <div class="collapsible-content" v-show="expandedFilters.fragrant">
          <div class="collapsible-options">
            <label class="option-label">
              <input
                type="checkbox"
                v-model="localFilters.fragrant"
                class="option-checkbox"
              >
              <span class="option-text">Prefer fragrant plants</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Pollen Sensitivity Collapsible -->
      <div class="collapsible-filter">
        <button
          class="collapsible-header"
          @click="toggleFilter('pollenSensitive')"
          :class="{ 'expanded': expandedFilters.pollenSensitive }"
        >
          <span>Pollen Sensitivity</span>
          <ChevronDownIcon class="collapsible-icon" />
        </button>
        <div class="collapsible-content" v-show="expandedFilters.pollenSensitive">
          <div class="collapsible-options">
            <label class="option-label">
              <input
                type="checkbox"
                v-model="localFilters.pollenSensitive"
                class="option-checkbox"
              >
              <span class="option-text">I am sensitive to pollen</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Pets or Toddlers Collapsible -->
      <div class="collapsible-filter">
        <button
          class="collapsible-header"
          @click="toggleFilter('petsOrToddlers')"
          :class="{ 'expanded': expandedFilters.petsOrToddlers }"
        >
          <span>Safety Concerns</span>
          <ChevronDownIcon class="collapsible-icon" />
        </button>
        <div class="collapsible-content" v-show="expandedFilters.petsOrToddlers">
          <div class="collapsible-options">
            <label class="option-label">
              <input
                type="checkbox"
                v-model="localFilters.petsOrToddlers"
                class="option-checkbox"
              >
              <span class="option-text">I have pets or toddlers</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Budget Collapsible -->
      <div class="collapsible-filter">
        <button
          class="collapsible-header"
          @click="toggleFilter('budget')"
          :class="{ 'expanded': expandedFilters.budget }"
        >
          <span>Budget</span>
          <ChevronDownIcon class="collapsible-icon" />
        </button>
        <div class="collapsible-content" v-show="expandedFilters.budget">
          <div class="collapsible-options">
            <label v-for="option in budgetOptions" :key="option" class="option-label">
              <input
                type="radio"
                :id="'budget-' + option"
                name="budget"
                :value="option"
                :checked="localFilters.budget === option"
                @click="handleRadioToggle('budget', option)"
                class="option-radio"
              >
              <span class="option-text">{{ option }}</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Basic Gardening Tools Collapsible -->
      <div class="collapsible-filter">
        <button
          class="collapsible-header"
          @click="toggleFilter('hasBasicTools')"
          :class="{ 'expanded': expandedFilters.hasBasicTools }"
        >
          <span>Basic Gardening Tools</span>
          <ChevronDownIcon class="collapsible-icon" />
        </button>
        <div class="collapsible-content" v-show="expandedFilters.hasBasicTools">
          <div class="collapsible-options">
            <label class="option-label">
              <input
                type="checkbox"
                v-model="localFilters.hasBasicTools"
                class="option-checkbox"
              >
              <span class="option-text">Yes</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Organic Methods Only Collapsible -->
      <div class="collapsible-filter">
        <button
          class="collapsible-header"
          @click="toggleFilter('organicOnly')"
          :class="{ 'expanded': expandedFilters.organicOnly }"
        >
          <span>Organic Methods Only</span>
          <ChevronDownIcon class="collapsible-icon" />
        </button>
        <div class="collapsible-content" v-show="expandedFilters.organicOnly">
          <div class="collapsible-options">
            <label class="option-label">
              <input
                type="checkbox"
                v-model="localFilters.organicOnly"
                class="option-checkbox"
              >
              <span class="option-text">Yes</span>
            </label>
          </div>
        </div>
      </div>



      <!-- Clear Filters Button -->
      <button class="clear-filters-button" @click="clearAllFilters">
        Clear All Filters
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ChevronDownIcon } from '@heroicons/vue/24/outline'

// Props interface
interface FilterData {
  areaM2: number
  windExposure: string
  containers: boolean
  containerSizes: string[]
  maintainability: string
  watering: string
  seasonIntent: string
  colors: string[]
  fragrant: boolean
  pollenSensitive: boolean
  petsOrToddlers: boolean
  budget: string
  hasBasicTools: boolean
  organicOnly: boolean
}

// Props from parent
const props = defineProps<{
  filters: FilterData
}>()

// Component events
const emit = defineEmits<{
  'update-filters': [filters: FilterData]
}>()

// Local filter state
const localFilters = ref<FilterData>({ ...props.filters })
// Single-value proxy for preferred color to simplify binding
const preferredColor = ref<string>('')

// Main filter collapse state
const isFilterExpanded = ref(false)

// Collapsible filter state
const expandedFilters = ref({
  areaM2: false,
  windExposure: false,
  containers: false,
  containerSizes: false,
  maintainability: false,
  watering: false,
  seasonIntent: false,
  colors: false,
  fragrant: false,
  pollenSensitive: false,
  petsOrToddlers: false,
  budget: false,
  hasBasicTools: false,
  organicOnly: false
})

// Toggle main filter
const toggleMainFilter = () => {
  isFilterExpanded.value = !isFilterExpanded.value
}

// Toggle specific filter
const toggleFilter = (filterName: keyof typeof expandedFilters.value) => {
  expandedFilters.value[filterName] = !expandedFilters.value[filterName]
}

// Watch for changes and emit to parent
watch(localFilters, (newFilters) => {
  // sync from single-value proxy to array form
  newFilters.colors = preferredColor.value ? [preferredColor.value] : []
  emit('update-filters', { ...newFilters })
}, { deep: true })

// keep proxy in sync if parent provides initial colors
if (localFilters.value.colors && localFilters.value.colors.length > 0) {
  preferredColor.value = localFilters.value.colors[0]
}

// Dropdown options
const windExposureOptions = ['Sheltered', 'Moderate', 'Windy']
const maintainabilityOptions = ['Low', 'Medium', 'High']
const wateringOptions = ['Low', 'Medium', 'High']
const seasonIntentOptions = ['Start Now']
const budgetOptions = ['Low', 'Medium', 'High']
const containerSizes = ['Small (<=15cm)', 'Medium (16-25cm)', 'Large (26-40cm)', 'Very Large (>40cm)']
const colorOptions = ['White', 'Yellow', 'Orange', 'Pink', 'Red', 'Purple', 'Blue']

// Handle radio button toggle (allow deselection)
const handleRadioToggle = (fieldName: keyof FilterData, value: string) => {
  if (localFilters.value[fieldName] === value) {
    // If clicking the same option, deselect it
    (localFilters.value[fieldName] as string) = ''
  } else {
    // Otherwise select the new option
    (localFilters.value[fieldName] as string) = value
  }
}

// no handler needed; v-model preferredColor handles it

// Clear all filters
const clearAllFilters = () => {
  localFilters.value = {
    areaM2: 2.0,
    windExposure: '',
    containers: false,
    containerSizes: [],
    maintainability: '',
    watering: '',
    seasonIntent: '',
    colors: [],
    fragrant: false,
    pollenSensitive: false,
    petsOrToddlers: false,
    budget: '',
    hasBasicTools: false,
    organicOnly: false,
  }
}
</script>

<style scoped>
.filter-sidebar {
  background: transparent;
  backdrop-filter: none;
  padding: 1rem; /* small horizontal padding so content does not touch edges */
  margin-top: 0; /* flush align with top section */
  height: fit-content;
  border-top: 0 !important; /* remove top border */
  border: none; /* ensure no borders remain */
  position: relative;
  z-index: 2;
  transition: background-color 0.3s ease, backdrop-filter 0.3s ease;
  width: 320px; /* keep same width collapsed/expanded to avoid horizontal shift */
  box-sizing: border-box;
}

/* Keep the collapsed button at exactly the same horizontal position as expanded */
/* Shift only the collapsed header slightly to the right */
.filter-sidebar:not(.expanded) .main-filter-header {
  padding-left: 5rem;
}

/* Keep the same left offset when expanded so it doesn't jump */
.filter-sidebar.expanded .main-filter-header {
  padding-left: 5rem;
}

.filter-sidebar.expanded {
  background: transparent !important;
  backdrop-filter: none !important;
}

.filter-header {
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 0;
  padding-left: 0;
}

.main-filter-header,
.main-filter-header.expanded {
  width: 100%;
  padding: 1rem 1rem 1rem 0;
  background: transparent;
  color: #333;
  border: none;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.2s ease;
  margin-bottom: -2rem;
  margin-top: 2rem;
}

.main-filter-header:hover .filter-circle {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.filter-circle-container,
.filter-circle-container.expanded {
  display: flex;
  align-items: center;
  justify-content: center;
}

.filter-circle {
  width: 6rem;
  height: 3rem;
  border: 2px solid #333;
  border-radius: 0.5rem;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  background: #ebf2e5; /* match search bar background */
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  gap: 0.4rem;
  margin-left: 0;
  margin-right: 0;
}

.filter-icon {
  width: 1.8rem;
  height: 1.8rem;
  object-fit: contain;
  background: transparent;
  /* Try to remove dark background, keep only green plant parts */
  filter: contrast(1.2) saturate(1.5);
  /* If icon has fixed background color, try this */
  /* mix-blend-mode: multiply; */
}

.filter-text {
  font-size: 0.75rem;
  font-weight: 600;
  color: #22c55e;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.clear-filters-button {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.5rem 0.75rem;
  border-radius: 0.25rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
  font-size: 0.8rem;
  margin-top: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.clear-filters-button:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

.filter-section {
  margin-bottom: 1.5rem;
  border-bottom: 0;
  padding-bottom: 1rem;
  padding-left: 5rem; /* align expanded items with Filter header left edge */
}

.filter-section:last-of-type {
  border-bottom: none;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1c3d21;
  margin-bottom: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  cursor: pointer;
  background: transparent; /* unify background with parent */
  padding: 0.5rem 0;
  border-radius: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.checkbox-field {
  display: flex;
  align-items: center;
  padding: 0.5rem 0;
  margin-bottom: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-weight: 500;
  color: #1c3d21;
  font-size: 0.875rem;
}

.checkbox-input {
  width: 1rem;
  height: 1rem;
  accent-color: #0d9488;
  cursor: pointer;
}

.checkbox-text {
  font-size: 0.875rem;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem 0;
  background: transparent; /* remove inner tint */
  border-radius: 0;
  border: 0;
  margin-bottom: 0.75rem;
}

.group-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1c3d21;
  margin-bottom: 0.5rem;
  border-bottom: 0;
  padding-bottom: 0.25rem;
}

/* Collapsible Filter Styles */
.collapsible-filter {
  margin-bottom: 1rem;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 0.25rem;
  overflow: hidden;
}

.collapsible-header {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 1rem; /* base padding */
  background: #ebf2e5; /* match filter background */
  color: #1c3d21; /* match search text color */
  border: none;
  text-align: left;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: background-color 0.2s ease, color 0.2s ease;
}

/* Ensure the visible blue buttons align with the Filter header's left edge */
.filter-sidebar.expanded .collapsible-header {
  padding-left: 1rem; /* inner padding for button itself */
}

.collapsible-header:hover {
  background: #e2efda;
}

.collapsible-header.expanded {
  background: #e2efda;
}

.collapsible-icon {
  width: 1rem;
  height: 1rem;
  transition: transform 0.2s ease;
}

.collapsible-header.expanded .collapsible-icon {
  transform: rotate(180deg);
}

.collapsible-content {
  overflow: hidden;
  transition: all 0.3s ease;
}

.collapsible-options {
  padding: 0.75rem 1rem;
  background: #ffffff;
}

.option-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.25rem 0;
  font-size: 0.875rem;
  color: #1c3d21; /* match search text color */
}

.option-radio {
  width: 1rem;
  height: 1rem;
  accent-color: #4a90a4;
  cursor: pointer;
}

.option-checkbox {
  width: 1rem;
  height: 1rem;
  accent-color: #4a90a4;
  cursor: pointer;
}

.option-text {
  font-size: 0.875rem;
}

.option-input {
  width: 100px;
  padding: 0.25rem 0.5rem;
  border: 1px solid #ccc;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  margin-right: 0.5rem;
}



@media (max-width: 1024px) {
  .filter-sidebar {
    position: static;
    order: -1;
    max-height: none;
    margin-bottom: 2rem;
  }

  .filter-section {
    margin-bottom: 0.75rem;
  }
}

@media (max-width: 768px) {
  .filter-sidebar {
    padding: 1rem;
  }

  .checkbox-group {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.25rem;
  }

  .group-title {
    grid-column: 1 / -1;
  }
}
</style>
