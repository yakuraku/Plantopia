<template>
  <!-- 
    Reusable Dropdown Select Component
    Used for Garden Type, Sunlight, and Watering Effort selection
    Provides custom styled dropdown with click-outside handling
  -->
  <div class="form-group">
    <!-- Dynamic Label Based on Props -->
    <label :for="id">{{ label }}</label>
    
    <!-- Dropdown Container -->
    <div class="dropdown-wrapper">
      <!-- Main Dropdown Button showing selected value or placeholder -->
      <button 
        class="dropdown-button" 
        @click.stop="toggleDropdown" 
        type="button"
      >
        {{ selectedValue || placeholder }}
        <ChevronDownIcon class="dropdown-icon" />
      </button>
      
      <!-- Dropdown Menu with Options -->
      <div 
        v-if="showDropdown" 
        class="dropdown-menu"
        :style="{ 
          display: showDropdown ? 'block' : 'none',
          position: 'absolute',
          zIndex: 9999,
          backgroundColor: 'white'
        }"
      >
        <!-- Individual Option Buttons -->
        <button
          v-for="option in options"
          :key="option"
          class="dropdown-item"
          @click.stop="selectOption(option)"
          type="button"
        >
          {{ option }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ChevronDownIcon } from '@heroicons/vue/24/outline'

// Component props interface for type safety
interface Props {
  id: string          // Unique identifier for the dropdown
  label: string       // Display label for the dropdown
  placeholder: string // Placeholder text when no option is selected
  options: string[]   // Array of selectable options
  modelValue?: string // Current selected value (v-model binding)
}

// Define props with default values
const props = withDefaults(defineProps<Props>(), {
  modelValue: ''  // Default to empty string if no initial value
})

// Component events - emits changes for v-model binding
const emit = defineEmits(['update:modelValue'])

// Reactive state for dropdown visibility and selected value
const showDropdown = ref(false)
const selectedValue = ref(props.modelValue)

// Watch for prop changes to keep selectedValue in sync
watch(() => props.modelValue, (newValue) => {
  selectedValue.value = newValue
}, { immediate: true })

// Toggle dropdown menu visibility
const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

// Handle option selection from dropdown menu
const selectOption = (option: string) => {
  // Update local selected value
  selectedValue.value = option
  // Close dropdown after selection
  showDropdown.value = false
  // Emit change to parent component for v-model binding
  emit('update:modelValue', option)
}

// Handle clicks outside component to close dropdown
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  // Close dropdown if click is outside the dropdown wrapper
  if (!target.closest('.dropdown-wrapper')) {
    showDropdown.value = false
  }
}

// Add click outside listener when component mounts
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

// Remove click outside listener when component unmounts to prevent memory leaks
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

.dropdown-wrapper {
  position: relative;
  z-index: 10;
}

.dropdown-button {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 1.5rem;
  background: #ebf2e5;
  text-align: left;
  font-size: 0.875rem;
  color: #1c3d21;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
  pointer-events: auto;
  position: relative;
  z-index: 1;
}

.dropdown-button:hover {
  background: #ebf2e5;
}

.dropdown-icon {
  width: 1rem;
  height: 1rem;
  color: #1c3d21;
  transition: transform 0.2s;
}

.dropdown-menu {
  position: absolute !important;
  top: 100% !important;
  left: 0 !important;
  right: 0 !important;
  background: white !important;
  border: 2px solid #ebf2e5 !important;
  border-radius: 1rem !important;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1) !important;
  z-index: 9999 !important;
  margin-top: 0.25rem !important;
  max-height: 200px !important;
  overflow-y: auto !important;
  display: block !important;
  visibility: visible !important;
  opacity: 1 !important;
}

.dropdown-item {
  width: 100%;
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.875rem;
  color: #064e3b;
  border: none;
  background: none;
  cursor: pointer;
  transition: background-color 0.2s;
  font-weight: 500;
}

.dropdown-item:hover {
  background-color: #ebf2e5;
}
</style>