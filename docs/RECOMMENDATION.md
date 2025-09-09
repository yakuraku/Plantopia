# Plant Recommendation System Documentation

## Architecture

```
RecommendationsView.vue (Main Container)
├── SearchForm.vue (Search Interface)
│   ├── LocationInput.vue (Location Selection)
│   └── DropdownSelect.vue (Selection Options)
├── SearchResults.vue (Results Display)
│   ├── FilterSidebar.vue (Benefit Filters)
│   └── PlantCard.vue (Individual Plant Cards)
└── PlantDetailModal.vue (Detailed Plant Information)
```

## Components

### 1. RecommendationsView.vue

**Purpose**: Main container component that orchestrates the entire recommendation flow.

**Key Features**:

- Manages application state (search parameters, results visibility, selected plant)
- Contains mock plant data for demonstration
- Handles communication between child components
- Provides background styling with plant imagery

**Data Flow**: Receives search parameters from SearchForm, passes them to SearchResults, and manages modal state for PlantDetailModal.

### 2. SearchForm.vue

**Purpose**: Primary interface for user input collection and search initiation.

**Key Features**:

- Responsive grid layout for form elements
- Location validation for Melbourne postcodes
- Error handling and user feedback
- Slot-based architecture for displaying search results inline

**Validation Rules**:

- Location is required
- Must contain valid Melbourne postcode (3000, 3001, 3002, 3121, 3065, 3182)
- Supports both postcode and suburb name formats

### 3. LocationInput.vue

**Purpose**: Specialized input component for location selection with autocomplete functionality.

**Key Features**:

- Real-time search suggestions
- Click-outside behavior for dropdown closure
- Predefined Melbourne suburb suggestions
- Search icon integration

**Supported Locations**:

- Melbourne, 3000 VIC
- Richmond, 3121 VIC
- Fitzroy, 3065 VIC
- St Kilda, 3182 VIC

### 4. DropdownSelect.vue

**Purpose**: Reusable dropdown component for garden type, sunlight, and watering effort selection.

**Key Features**:

- v-model binding support
- Customizable options and labels
- Click-outside behavior
- Hover and selection states

**Usage Examples**:

- Garden Type: Indoor, Balcony, Outdoor garden
- Sunlight: Full Sun, Partial Sun, Shade
- Watering Effort: Low, Medium, High

### 5. SearchResults.vue

**Purpose**: Manages the display of filtered plant recommendations and coordinate between filter sidebar and plant grid.

**Key Features**:

- Two-column layout (filters + results)
- Advanced filtering logic
- Dynamic plant filtering based on:
  - Garden type compatibility
  - Sunlight requirements
  - Watering effort preferences
  - Plant benefit characteristics
- Responsive design for mobile devices

**Filtering Logic**:

- Indoor gardens automatically filter for shade/partial sun plants
- Multiple filters work with AND logic (plant must match ALL selected filters)
- Real-time updates as filters change

### 6. FilterSidebar.vue

**Purpose**: Provides additional filtering options based on plant benefits and characteristics.

**Available Filters**:

- Edible: Plants that produce edible parts
- Fragrant: Plants with pleasant scents
- Pet Safe: Plants that are non-toxic to pets
- Air Purifying: Plants that improve indoor air quality
- Drought Resistant: Plants that tolerate water scarcity

**Features**:

- Toggle-based filter selection
- Dynamic status notifications
- Sticky positioning for easy access while scrolling

### 7. PlantCard.vue

**Purpose**: Individual plant display component showing key information and care requirements.

**Displayed Information**:

- Plant name and description
- Care requirement icons (sun, water, effort level)
- Recommendation reasoning
- Quick access to detailed information

**Interactive Features**:

- Hover effects for enhanced user experience
- Click-to-view details functionality
- Icon-based care requirement display

### 8. PlantDetailModal.vue

**Purpose**: Comprehensive plant information display in a modal overlay.

**Detailed Sections**:

- **Basic Information**: Name, scientific name, description
- **Growing Requirements**: Sunlight, water, and maintenance needs
- **Sustainability Impact**: Cooling effect, carbon reduction, drought tolerance
- **Benefits**: Comprehensive list of plant characteristics
- **Care Tips**: Practical growing advice
- **Additional Resources**: Links to guidance videos

## Data Models

### Plant Interface

```typescript
interface Plant {
  id: string
  name: string
  scientificName: string
  description: string
  sunlight: 'full' | 'partial' | 'shade'
  water: 'low' | 'medium' | 'high'
  effort: 'low' | 'medium' | 'high'
  whyRecommended: string
  benefits: {
    edible: boolean
    fragrant: boolean
    petSafe: boolean
    airPurifying: boolean
    droughtResistant: boolean
  }
  coolingEffect: string
  carbonReduction: string
  droughtTolerance: string
}
```

### SearchParams Interface

```typescript
interface SearchParams {
  location: string
  gardenType: string
  sunlight: string
  wateringEffort: string
}
```

## Usage Instructions

### For Developers

1. **Component Integration**: Import required components from `@/views/recommendation/`
2. **Styling Customization**: Modify CSS custom properties for theme changes
3. **Data Integration**: Replace `mockPlants` array with API calls
4. **Feature Extension**: Add new filter options to `FilterSidebar.vue`

### For Users

1. **Search Process**: Enter location → Select preferences → Click "Find my plant"
2. **Filtering**: Use sidebar filters to refine results
3. **Plant Details**: Click "Learn More" on any plant card for comprehensive information
4. **Mobile Support**: All features available on mobile devices
