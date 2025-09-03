<template>
  <!--
    Location Input Component
    Provides location search with autocomplete suggestions
    Includes search icon and dropdown for Melbourne suburb suggestions
  -->
  <div class="form-group">
    <!-- Location Input Label -->
    <label for="location">Location</label>

    <!-- Location Input Container with Search Icon -->
    <div class="location-input-wrapper">
      <!-- Magnifying Glass Search Icon -->
      <MagnifyingGlassIcon class="search-icon" />

      <!-- Location Text Input Field -->
      <input
        type="text"
        id="location"
        v-model="location"
        placeholder="Enter suburb name"
        class="location-input"
        @input="onLocationInput"
      />

      <!-- Autocomplete Suggestions Dropdown -->
      <div
        v-if="showDropdown && filteredSuggestions.length > 0"
        class="location-dropdown"
      >
        <!-- Individual Suggestion Options -->
        <div
          v-for="(suggestion, index) in filteredSuggestions"
          :key="index"
          class="location-option"
          @click="selectLocation(suggestion)"
        >
          {{ suggestion }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { MagnifyingGlassIcon } from '@heroicons/vue/24/outline'

// Component events - emits location changes to parent component
const emit = defineEmits(['update:location'])

// Reactive state for location input and dropdown visibility
const location = ref('')
const showDropdown = ref(false)

// Predefined location suggestions for Melbourne area - suburb names only
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

// Computed property that filters suggestions based on user input
const filteredSuggestions = computed(() => {
  // Return empty array if no input
  if (!location.value) return []

  // Filter suggestions that contain the user's input (case insensitive)
  return locationSuggestions.filter((suggestion) =>
    suggestion.toLowerCase().includes(location.value.toLowerCase()),
  )
})

// Handle input changes - show dropdown and emit location to parent
const onLocationInput = () => {
  // Show dropdown if there's input and matching suggestions
  showDropdown.value = location.value.length > 0 && filteredSuggestions.value.length > 0
  // Emit current location value to parent component
  emit('update:location', location.value)
}

// Handle suggestion selection from dropdown
const selectLocation = (suggestion: string) => {
  // Set selected suggestion as input value
  location.value = suggestion
  // Hide dropdown after selection
  showDropdown.value = false
  // Emit selected location to parent component
  emit('update:location', location.value)
}

// Handle clicks outside component to close dropdown
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  // Close dropdown if click is outside the location input wrapper
  if (!target.closest('.location-input-wrapper')) {
    showDropdown.value = false
  }
}

// Add click outside listener when component mounts
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

// Remove click outside listener when component unmounts
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  font-weight: 600;
  color: white;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
}

.location-input-wrapper {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  color: #1c3d21;
  z-index: 2;
}

.location-input {
  width: 100%;
  padding: 1rem 1rem 1rem 2.5rem;
  border: none;
  border-radius: 1.5rem;
  font-size: 0.875rem;
  background: #ebf2e5;
  transition: all 0.2s ease;
  color: #1c3d21;
  font-weight: 500;
}

.location-input:focus {
  outline: none;
  background: #ebf2e5;
}

.location-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 2px solid #a7f3d0;
  border-radius: 1rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  z-index: 50;
  margin-top: 0.25rem;
  max-height: 200px;
  overflow-y: auto;
}

.location-option {
  padding: 0.75rem;
  cursor: pointer;
  transition: background-color 0.2s;
  color: #064e3b;
}

.location-option:hover {
  background-color: #d1fae5;
}
</style>
