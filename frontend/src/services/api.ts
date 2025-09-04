// API service for Plantopia Recommendation Engine
// Handles all communication with the backend recommendation API

// Base configuration
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api' // Vercel serverless functions - no trailing slash to avoid double slash
  : 'http://localhost:8000' // Development

// API Response interfaces matching the backend structure
export interface ApiPlantRecommendation {
  plant_name: string
  scientific_name: string
  plant_category: string
  score: number
  why: string[]
  fit: {
    sun_need: string
    time_to_maturity_days: number
    maintainability: string
    container_ok: boolean
    indoor_ok: boolean
  }
  sowing: {
    climate_zone: string
    months: string[]
    method: string
    season_label: string
  }
  media: {
    image_path: string
    image_base64?: string  // Base64 encoded image data
  }
}

export interface ApiRecommendationResponse {
  recommendations: ApiPlantRecommendation[]
  notes: string[]
  suburb: string
  climate_zone: string
  month_now: string
}

// All Plants API Response interface
export interface ApiAllPlantsResponse {
  plants: ApiPlantData[]
  total_count: number
  categories: {
    vegetable: number
    herb: number
    flower: number
  }
}

// Individual plant data from /plants endpoint
export interface ApiPlantData {
  plant_name: string
  scientific_name: string
  plant_category: 'vegetable' | 'herb' | 'flower'
  plant_type: string
  description: string
  additional_information?: string
  days_to_maturity: number
  plant_spacing: string
  sowing_depth: string
  position: string
  sun_need: string
  season: string
  germination_period: string
  sowing_method: string
  hardiness_life_cycle: string
  characteristics: string
  climate_specific_sowing: {
    [key: string]: string  // e.g., "temperate": "Mar-May, Sep-Nov"
  }
  container_ok: boolean
  indoor_ok: boolean
  edible: boolean
  fragrant: boolean
  flower_colors: string[]
  habit: string
  maintainability_score: number
  media: {
    image_path: string
    image_base64?: string
    has_image: boolean
  }
}

// Request interfaces matching the correct API requirements
export interface ApiSite {
  location_type: 'indoors' | 'balcony' | 'courtyard' | 'backyard' | 'community_garden'
  area_m2: number
  sun_exposure: 'full_sun' | 'part_sun' | 'bright_shade' | 'low_light'
  wind_exposure: 'sheltered' | 'moderate' | 'windy'
  containers: boolean
  container_sizes?: string[]
}

export interface ApiPreferences {
  goal: 'edible' | 'ornamental' | 'mixed'
  edible_types?: string[]
  ornamental_types?: string[]
  colors?: string[]
  fragrant?: boolean
  maintainability: 'low' | 'medium' | 'high'
  watering?: 'low' | 'medium' | 'high'
  time_to_results: 'quick' | 'standard' | 'patient'
  season_intent?: 'start_now' | 'happy_to_wait'
  pollen_sensitive?: boolean
  pets_or_toddlers?: boolean
}

export interface ApiPractical {
  budget: 'low' | 'medium' | 'high'
  has_basic_tools: boolean
  organic_only: boolean
}

export interface ApiUserEnvironment {
  climate_zone?: string
  month_now?: string
  uv_index?: number
  temperature_c?: number
  humidity_pct?: number
  wind_speed_kph?: number
}

export interface ApiRecommendationRequest {
  suburb: string
  n: number
  climate_zone?: string | null
  user_preferences: {
    user_id: string
    site: ApiSite
    preferences: ApiPreferences
    practical: ApiPractical
    environment: ApiUserEnvironment
  }
}

// Frontend Plant interface (transformed from API response)
export interface Plant {
  id: string
  name: string
  scientific_name: string
  description: string
  category: 'vegetable' | 'herb' | 'flower'
  plant_type?: string
  additional_information?: string
  days_to_maturity: number
  plant_spacing?: string
  sowing_depth?: string
  position?: string
  season?: string
  germination_period?: string
  sowing_method?: string
  hardiness_life_cycle?: string
  characteristics?: string
  climate_specific_sowing?: { [key: string]: string }
  image_url?: string
  image_base64?: string
  has_image?: boolean
  tags?: string[]
  care_requirements?: {
    sunlight?: string
    watering?: string
    soil?: string
    temperature?: string
  }
  // Additional plant properties from API
  container_ok?: boolean
  indoor_ok?: boolean
  edible?: boolean
  fragrant?: boolean
  flower_colors?: string[]
  habit?: string
  maintainability_score?: number
  // Legacy fields for backwards compatibility with recommendation system
  scientificName?: string
  score?: number
  sunlight?: 'full' | 'partial' | 'shade'
  water?: 'low' | 'medium' | 'high'
  effort?: 'low' | 'medium' | 'high'
  whyRecommended?: string[]
  benefits?: {
    edible: boolean
    fragrant: boolean
    petSafe: boolean
    airPurifying: boolean
    droughtResistant: boolean
    containerFriendly: boolean
    indoorSuitable: boolean
  }
  coolingEffect?: string
  carbonReduction?: string
  droughtTolerance?: string
  timeToMaturity?: number
  sowingInfo?: {
    climateZone: string
    months: string[]
    method: string
    seasonLabel: string
  }
  imagePath?: string
  imageData?: string
}

// API Service class
export class PlantRecommendationService {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  // Health check endpoint
  async healthCheck(): Promise<{ message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/`)
      if (!response.ok) {
        throw new Error(`Health check failed: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Health check failed:', error)
      throw error
    }
  }

  // Get all plants endpoint
  async getAllPlants(): Promise<ApiAllPlantsResponse> {
    try {
      console.group('[PLANTS API] Get All Plants Request')
      console.log('[REQUEST] URL:', `${this.baseUrl}/plants`)
      console.log('[REQUEST] Method:', 'GET')

      const response = await fetch(`${this.baseUrl}/plants`)

      console.log('[RESPONSE] Status:', response.status)
      console.log('[RESPONSE] Status Text:', response.statusText)

      if (!response.ok) {
        console.error('[ERROR] API Request Failed:', response.status, response.statusText)
        console.groupEnd()
        throw new Error(`API request failed: ${response.status} ${response.statusText}`)
      }

      const responseData = await response.json()
      console.log('[RESPONSE] Data:', responseData)
      console.log('[RESPONSE] Total plants:', responseData.total_count || 0)
      console.log('[RESPONSE] Categories:', responseData.categories)
      console.groupEnd()

      return responseData
    } catch (error) {
      console.group('[PLANTS API] Error Debug')
      console.error('[ERROR] Details:', error)
      console.error('[ERROR] Message:', error instanceof Error ? error.message : 'Unknown error')
      console.groupEnd()
      throw error
    }
  }

  // Main recommendation endpoint
  async getRecommendations(request: ApiRecommendationRequest): Promise<ApiRecommendationResponse> {
    try {
      console.group('[PLANT API] Request Debug')
      console.log('[REQUEST] URL:', `${this.baseUrl}/recommendations`)
      console.log('[REQUEST] Method:', 'POST')
      console.log('[REQUEST] Headers:', {
        'Content-Type': 'application/json',
      })
      console.log('[REQUEST] Body:', JSON.stringify(request, null, 2))
      console.log('[REQUEST] Raw Object:', request)
      console.groupEnd()

      const response = await fetch(`${this.baseUrl}/recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      console.group('[PLANT API] Response Debug')
      console.log('[RESPONSE] Status:', response.status)
      console.log('[RESPONSE] Status Text:', response.statusText)
      console.log('[RESPONSE] Headers:', Object.fromEntries(response.headers.entries()))

      const responseData = await response.json()
      console.log('[RESPONSE] Data:', responseData)
      
      if (!response.ok) {
        console.error('[ERROR] API Request Failed:', response.status, response.statusText)
        console.error('[ERROR] Response Body:', JSON.stringify(responseData, null, 2))
        console.groupEnd()
        throw new Error(`API request failed: ${response.status} ${response.statusText}`)
      }

      console.log('[RESPONSE] Number of recommendations:', responseData.recommendations?.length || 0)
      console.log('[RESPONSE] Suburb detected:', responseData.suburb)
      console.log('[RESPONSE] Climate zone:', responseData.climate_zone)
      console.groupEnd()

      return responseData
    } catch (error) {
      console.group('[PLANT API] Error Debug')
      console.error('[ERROR] Details:', error)
      console.error('[ERROR] Message:', error instanceof Error ? error.message : 'Unknown error')
      console.error('[ERROR] Stack:', error instanceof Error ? error.stack : 'No stack trace')
      console.groupEnd()
      throw error
    }
  }

  // Transform All Plants API response to frontend Plant interface
  transformAllPlantsToPlants(apiResponse: ApiAllPlantsResponse): Plant[] {
    console.group('[TRANSFORM] All Plants API Response to Plants')
    console.log('[TRANSFORM] Input API Response:', apiResponse)
    console.log('[TRANSFORM] Number of plants:', apiResponse.total_count)

    const transformedPlants = apiResponse.plants.map((apiPlant, index) => {
      console.log(`[TRANSFORM] Plant ${index + 1}:`, apiPlant.plant_name)

      const transformedPlant: Plant = {
        id: `${apiPlant.plant_name.replace(/\s+/g, '_').toLowerCase()}_${index}`,
        name: apiPlant.plant_name,
        scientific_name: apiPlant.scientific_name,
        description: apiPlant.description?.replace(/\\1/g, `${apiPlant.plant_name} (${apiPlant.scientific_name})`) || '',
        category: apiPlant.plant_category,
        plant_type: apiPlant.plant_type,
        additional_information: apiPlant.additional_information?.replace(/\\1/g, `${apiPlant.plant_name} (${apiPlant.scientific_name})`),
        days_to_maturity: apiPlant.days_to_maturity,
        plant_spacing: apiPlant.plant_spacing,
        sowing_depth: apiPlant.sowing_depth,
        position: apiPlant.position,
        season: apiPlant.season,
        germination_period: apiPlant.germination_period,
        sowing_method: apiPlant.sowing_method,
        hardiness_life_cycle: apiPlant.hardiness_life_cycle,
        characteristics: apiPlant.characteristics,
        climate_specific_sowing: apiPlant.climate_specific_sowing,
        image_url: apiPlant.media.drive_url || (apiPlant.media.has_image ? apiPlant.media.image_path : '/placeholder-plant.svg'),
        image_base64: apiPlant.media.image_base64,
        has_image: apiPlant.media.has_image,
        // Additional plant properties
        container_ok: apiPlant.container_ok,
        indoor_ok: apiPlant.indoor_ok,
        edible: apiPlant.edible,
        fragrant: apiPlant.fragrant,
        flower_colors: apiPlant.flower_colors,
        habit: apiPlant.habit,
        maintainability_score: apiPlant.maintainability_score,
        // Generate tags from characteristics and plant type
        tags: this.generateTagsFromPlantData(apiPlant),
        // Generate care requirements from plant data
        care_requirements: this.generateCareRequirements(apiPlant),
      }

      console.log(`[TRANSFORM] Completed plant ${index + 1} (${apiPlant.plant_name}):`, transformedPlant)
      return transformedPlant
    })

    console.log('[TRANSFORM] All plants completed successfully!')
    console.log('[TRANSFORM] Final array:', transformedPlants)
    console.groupEnd()

    return transformedPlants
  }

  // Transform API response to frontend Plant interface
  transformApiResponseToPlants(apiResponse: ApiRecommendationResponse): Plant[] {
    console.group('[TRANSFORM] API Response to Plants')
    console.log('[TRANSFORM] Input API Response:', apiResponse)
    console.log('[TRANSFORM] Number of recommendations:', apiResponse.recommendations.length)

    const transformedPlants = apiResponse.recommendations.map((apiPlant, index) => {
      console.log(`[TRANSFORM] Plant ${index + 1}:`, apiPlant.plant_name)

      const transformedPlant: Plant = {
        id: `${apiPlant.plant_name.replace(/\s+/g, '_').toLowerCase()}_${index}`,
        name: apiPlant.plant_name,
        scientific_name: apiPlant.scientific_name,
        description: apiPlant.why.join(' '),
        category: apiPlant.plant_category as 'vegetable' | 'herb' | 'flower',
        days_to_maturity: apiPlant.fit.time_to_maturity_days,
        image_url: apiPlant.media.drive_url || (apiPlant.media.has_image ? apiPlant.media.image_path : '/placeholder-plant.svg'),
        image_base64: apiPlant.media.image_base64,
        has_image: apiPlant.media.has_image,
        // Legacy fields for backwards compatibility
        scientificName: apiPlant.scientific_name,
        score: apiPlant.score,
        sunlight: this.mapSunlightRequirement(apiPlant.fit.sun_need),
        water: this.mapWaterRequirement(apiPlant.fit.maintainability),
        effort: this.mapEffortLevel(apiPlant.fit.maintainability),
        whyRecommended: apiPlant.why,
        benefits: {
          edible: apiPlant.plant_category === 'herb' || apiPlant.plant_category === 'vegetable',
          fragrant: apiPlant.plant_category === 'herb',
          petSafe: true, // Default - would need plant database for accurate info
          airPurifying: apiPlant.fit.indoor_ok,
          droughtResistant: apiPlant.fit.maintainability === 'hardy',
          containerFriendly: apiPlant.fit.container_ok,
          indoorSuitable: apiPlant.fit.indoor_ok,
        },
        coolingEffect: this.determineCoolingEffect(apiPlant.plant_category),
        carbonReduction: this.determineCarbonReduction(apiPlant.plant_category),
        droughtTolerance: apiPlant.fit.maintainability === 'hardy' ? 'excellent' : 'moderate',
        timeToMaturity: apiPlant.fit.time_to_maturity_days,
        sowingInfo: {
          climateZone: apiPlant.sowing.climate_zone,
          months: apiPlant.sowing.months,
          method: apiPlant.sowing.method,
          seasonLabel: apiPlant.sowing.season_label,
        },
        imagePath: apiPlant.media.image_path,
        imageData: apiPlant.media.image_base64, // Base64 encoded image
      }

      console.log(`[TRANSFORM] Completed plant ${index + 1} (${apiPlant.plant_name}):`, transformedPlant)
      return transformedPlant
    })

    console.log('[TRANSFORM] All plants completed successfully!')
    console.log('[TRANSFORM] Final array:', transformedPlants)
    console.groupEnd()

    return transformedPlants
  }

  // Helper methods for data transformation
  private mapSunlightRequirement(sunNeed: string): 'full' | 'partial' | 'shade' {
    switch (sunNeed.toLowerCase()) {
      case 'full_sun':
        return 'full'
      case 'part_sun':
      case 'partial_sun':
        return 'partial'
      case 'bright_shade':
      case 'shade':
        return 'shade'
      default:
        return 'partial'
    }
  }

  private mapWaterRequirement(maintainability: string): 'low' | 'medium' | 'high' {
    switch (maintainability.toLowerCase()) {
      case 'hardy':
        return 'low'
      case 'moderate':
        return 'medium'
      case 'high_maintenance':
        return 'high'
      default:
        return 'medium'
    }
  }

  private mapEffortLevel(maintainability: string): 'low' | 'medium' | 'high' {
    switch (maintainability.toLowerCase()) {
      case 'hardy':
        return 'low'
      case 'moderate':
        return 'medium'
      case 'high_maintenance':
        return 'high'
      default:
        return 'medium'
    }
  }

  private determineCoolingEffect(category: string): string {
    switch (category.toLowerCase()) {
      case 'tree':
        return 'high cooling effect'
      case 'shrub':
        return 'moderate cooling effect'
      case 'flower':
      case 'herb':
        return 'low cooling effect'
      default:
        return 'moderate cooling effect'
    }
  }

  private determineCarbonReduction(category: string): string {
    switch (category.toLowerCase()) {
      case 'tree':
        return 'high'
      case 'shrub':
        return 'moderate'
      case 'flower':
      case 'herb':
      case 'vegetable':
        return 'low'
      default:
        return 'moderate'
    }
  }

  // Generate tags from plant data
  private generateTagsFromPlantData(apiPlant: ApiPlantData): string[] {
    const tags: string[] = []

    // Add category as a tag
    tags.push(apiPlant.plant_category)

    // Add plant type if different from category
    if (apiPlant.plant_type && apiPlant.plant_type !== apiPlant.plant_category) {
      tags.push(apiPlant.plant_type)
    }

    // Extract tags from characteristics
    if (apiPlant.characteristics) {
      const characteristics = apiPlant.characteristics.toLowerCase()
      if (characteristics.includes('drought')) tags.push('drought-tolerant')
      if (characteristics.includes('fragrant')) tags.push('fragrant')
      if (characteristics.includes('compact')) tags.push('compact')
      if (characteristics.includes('climbing')) tags.push('climbing')
      if (characteristics.includes('fast')) tags.push('fast-growing')
      if (characteristics.includes('container')) tags.push('container-friendly')
    }

    // Add season-based tags
    if (apiPlant.season) {
      const season = apiPlant.season.toLowerCase()
      if (season.includes('summer')) tags.push('summer')
      if (season.includes('winter')) tags.push('winter')
      if (season.includes('spring')) tags.push('spring')
      if (season.includes('autumn') || season.includes('fall')) tags.push('autumn')
    }

    // Add maturity-based tags
    if (apiPlant.days_to_maturity <= 60) {
      tags.push('quick-growing')
    } else if (apiPlant.days_to_maturity > 120) {
      tags.push('slow-growing')
    }

    return tags.filter((tag, index, self) => self.indexOf(tag) === index) // Remove duplicates
  }

  // Generate care requirements from plant data
  private generateCareRequirements(apiPlant: ApiPlantData): { sunlight?: string; watering?: string; soil?: string; temperature?: string } {
    const requirements: { sunlight?: string; watering?: string; soil?: string; temperature?: string } = {}

    // Extract sunlight requirements from sun_need field first, then fallback to position
    if (apiPlant.sun_need) {
      const sunNeed = apiPlant.sun_need.toLowerCase()
      if (sunNeed === 'full_sun') {
        requirements.sunlight = 'Full sun (6-8h)'
      } else if (sunNeed === 'part_sun') {
        requirements.sunlight = 'Part sun (3-5h)'
      } else if (sunNeed === 'bright_shade') {
        requirements.sunlight = 'Bright shade (1-3h)'
      }
    } else if (apiPlant.position) {
      // Fallback to position field if sun_need is not available
      const position = apiPlant.position.toLowerCase()
      if (position.includes('full sun')) {
        requirements.sunlight = 'Full sun (6-8h)'
      } else if (position.includes('part sun') || position.includes('partial')) {
        requirements.sunlight = 'Part sun (3-5h)'
      } else if (position.includes('shade')) {
        requirements.sunlight = 'Bright shade (1-3h)'
      }
    }

    // Determine watering needs based on category and characteristics
    if (apiPlant.characteristics) {
      const characteristics = apiPlant.characteristics.toLowerCase()
      if (characteristics.includes('drought')) {
        requirements.watering = 'Low'
      } else if (characteristics.includes('moist') || apiPlant.plant_category === 'vegetable') {
        requirements.watering = 'Medium'
      } else {
        requirements.watering = 'Medium'
      }
    } else {
      // Default watering based on category
      switch (apiPlant.plant_category) {
        case 'herb':
          requirements.watering = 'Low'
          break
        case 'vegetable':
          requirements.watering = 'Medium'
          break
        case 'flower':
          requirements.watering = 'Medium'
          break
        default:
          requirements.watering = 'Medium'
      }
    }

    // Set soil requirements (generic for now)
    requirements.soil = 'Well-draining'

    // Set temperature range based on season and category
    if (apiPlant.season) {
      const season = apiPlant.season.toLowerCase()
      if (season.includes('cool') || season.includes('winter')) {
        requirements.temperature = '10-18°C'
      } else if (season.includes('warm') || season.includes('summer')) {
        requirements.temperature = '18-26°C'
      } else {
        requirements.temperature = '15-22°C'
      }
    } else {
      requirements.temperature = '15-22°C'
    }

    return requirements
  }
}

// Create and export a singleton instance
export const plantApiService = new PlantRecommendationService()

// Helper function to build API request from enhanced form data
export function buildApiRequest(formData: {
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
}): ApiRecommendationRequest {
  console.group('[BUILD REQUEST] Form Data to API Request')
  console.log('[BUILD REQUEST] Input Form Data:', formData)

  // Use location directly as suburb name (no extraction needed)
  const suburb = formData.location.trim()
  console.log('[BUILD REQUEST] Using suburb:', suburb)

  // Check for empty required fields
  console.log('[BUILD REQUEST] Field Check:')
  console.log('  - locationType empty?', !formData.locationType)
  console.log('  - sunlight empty?', !formData.sunlight)
  console.log('  - goal empty?', !formData.goal)
  console.log('  - timeToResults empty?', !formData.timeToResults)

  // Map location type
  const locationTypeMap: { [key: string]: ApiSite['location_type'] } = {
    'Indoors': 'indoors',
    'Balcony': 'balcony',
    'Courtyard': 'courtyard',
    'Backyard': 'backyard',
    'Community Garden': 'community_garden',
  }

  // Map container sizes
  const containerSizeMap: { [key: string]: string } = {
    'Small (<=15cm)': 'small',
    'Medium (16-25cm)': 'medium',
    'Large (26-40cm)': 'large',
    'Very Large (>40cm)': 'very_large',
  }

  // Map sunlight to sun exposure
  const sunExposureMap: { [key: string]: ApiSite['sun_exposure'] } = {
    'Full Sun (6-8h)': 'full_sun',
    'Part Sun (3-5h)': 'part_sun',
    'Bright Shade (1-3h)': 'bright_shade',
    'Low Light (<1h)': 'low_light',
  }

  // Map wind exposure
  const windExposureMap: { [key: string]: ApiSite['wind_exposure'] } = {
    'Sheltered': 'sheltered',
    'Moderate': 'moderate',
    'Windy': 'windy',
  }

  // Map goal
  const goalMap: { [key: string]: ApiPreferences['goal'] } = {
    'Edible': 'edible',
    'Ornamental': 'ornamental',
    'Mixed': 'mixed',
  }

  // Map maintainability
  const maintainabilityMap: { [key: string]: ApiPreferences['maintainability'] } = {
    'Low': 'low',
    'Medium': 'medium',
    'High': 'high',
  }

  // Map watering
  const wateringMap: { [key: string]: ApiPreferences['watering'] } = {
    'Low': 'low',
    'Medium': 'medium',
    'High': 'high',
  }

  // Map season intent
  const seasonIntentMap: { [key: string]: ApiPreferences['season_intent'] } = {
    'Start Now': 'start_now',
    'Happy to Wait': 'happy_to_wait',
  }

  // Map time to results
  const timeToResultsMap: { [key: string]: ApiPreferences['time_to_results'] } = {
    'Quick (<=60d)': 'quick',
    'Standard (60-120d)': 'standard',
    'Patient (>120d)': 'patient',
  }

  // Map budget
  const budgetMap: { [key: string]: ApiPractical['budget'] } = {
    'Low': 'low',
    'Medium': 'medium',
    'High': 'high',
  }

    // Convert edible types to lowercase
  const edibleTypesLower = formData.edibleTypes.map(type => type.toLowerCase())

  // Convert ornamental types to lowercase
  const ornamentalTypesLower = formData.ornamentalTypes.map(type => type.toLowerCase())

  // Convert colors to lowercase
  const colorsLower = formData.colors.map(color => color.toLowerCase())

  // Map container sizes to API format
  const containerSizesApi = formData.containers ?
    formData.containerSizes.map(size => containerSizeMap[size] || size.toLowerCase()) :
    undefined

  const apiRequest: ApiRecommendationRequest = {
    suburb,
    n: 5,
    climate_zone: null,
    user_preferences: {
      user_id: 'anon_mvp',
      site: {
        location_type: locationTypeMap[formData.locationType] || 'backyard',
        area_m2: formData.areaM2 || 2.0,
        sun_exposure: sunExposureMap[formData.sunlight] || 'part_sun',
        wind_exposure: windExposureMap[formData.windExposure] || 'moderate',
        containers: formData.containers,
        container_sizes: containerSizesApi,
      },
      preferences: {
        goal: goalMap[formData.goal] || 'mixed',
        edible_types: edibleTypesLower.length > 0 ? edibleTypesLower : ['herbs', 'leafy'],
        ornamental_types: ornamentalTypesLower.length > 0 ? ornamentalTypesLower : ['flowers'],
        colors: colorsLower.length > 0 ? colorsLower : ['purple', 'white'],
        fragrant: formData.fragrant,
        maintainability: maintainabilityMap[formData.maintainability] || 'low',
        watering: wateringMap[formData.watering] || 'medium',
        time_to_results: timeToResultsMap[formData.timeToResults] || 'quick',
        season_intent: seasonIntentMap[formData.seasonIntent] || 'start_now',
        pollen_sensitive: formData.pollenSensitive,
        pets_or_toddlers: formData.petsOrToddlers,
      },
      practical: {
        budget: budgetMap[formData.budget] || 'medium',
        has_basic_tools: formData.hasBasicTools,
        organic_only: formData.organicOnly,
      },
      environment: {
        climate_zone: 'temperate',
        month_now: '',
        uv_index: 0.0,
        temperature_c: 8.0,
        humidity_pct: 75,
        wind_speed_kph: 15,
      },
    },
  }

  console.log('[BUILD REQUEST] Field Mappings:')
  console.log('  - Location Type:', formData.locationType, '->', apiRequest.user_preferences.site.location_type)
  console.log('  - Area M2:', formData.areaM2, '->', apiRequest.user_preferences.site.area_m2)
  console.log('  - Sunlight:', formData.sunlight, '->', apiRequest.user_preferences.site.sun_exposure)
  console.log('  - Wind Exposure:', formData.windExposure, '->', apiRequest.user_preferences.site.wind_exposure)
  console.log('  - Goal:', formData.goal, '->', apiRequest.user_preferences.preferences.goal)
  console.log('  - Maintainability:', formData.maintainability, '->', apiRequest.user_preferences.preferences.maintainability)
  console.log('  - Time to Results:', formData.timeToResults, '->', apiRequest.user_preferences.preferences.time_to_results)
  console.log('  - Budget:', formData.budget, '->', apiRequest.user_preferences.practical.budget)
  console.log('  - Edible Types:', formData.edibleTypes, '->', apiRequest.user_preferences.preferences.edible_types)
  console.log('  - Ornamental Types:', formData.ornamentalTypes, '->', apiRequest.user_preferences.preferences.ornamental_types)

  console.log('[BUILD REQUEST] Final API Request:', apiRequest)
  console.groupEnd()

  return apiRequest
}
