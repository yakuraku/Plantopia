/**
 * Enhanced Image Helper with Google Drive API integration
 * Handles secure image URLs via backend API calls
 */

// API base URL configuration with fallback
const PRIMARY_API_URL = import.meta.env.MODE === 'production' 
  ? '/api'  // Vercel serverless functions
  : 'http://localhost:8000';  // Local development

const FALLBACK_API_URL = import.meta.env.MODE === 'production'
  ? '/api'  // Same in production
  : 'http://127.0.0.1:8000';  // Fallback for local development

// Current API URL (will switch to fallback if needed)
let currentApiUrl = PRIMARY_API_URL;

// Alternative category mappings (handle different naming conventions)
const CATEGORY_MAPPING = {
  'flowers': 'flower',
  'flower': 'flower',
  'flower_plant_images': 'flower',
  'herbs': 'herb', 
  'herb': 'herb',
  'herb_plant_images': 'herb',
  'vegetables': 'vegetable',
  'vegetable': 'vegetable', 
  'vegetable_plant_images': 'vegetable'
};

/**
 * Get plant image URL from backend API
 * Backend handles Google Drive API calls securely
 * @param {string} category - Plant category (flower, herb, vegetable)
 * @param {string} imageName - Image filename (optional, for matching specific images)
 * @returns {Promise<string>} Google Drive image URL or null
 */
export const getPlantImageUrl = async (category, imageName = null) => {
  // Handle undefined/null category
  if (!category) {
    console.warn('No category provided for plant image');
    return null;
  }
  
  // Normalize category name
  const normalizedCategory = CATEGORY_MAPPING[category.toLowerCase()] || category.toLowerCase();
  
  if (!['flower', 'herb', 'vegetable'].includes(normalizedCategory)) {
    console.warn(`Invalid category: ${category}`);
    return null;
  }
  
  try {
    // Fetch images for category from backend with fallback
    let response;
    try {
      response = await fetch(`${currentApiUrl}/images/${normalizedCategory}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
    } catch (error) {
      console.warn(`[IMAGE HELPER] Primary URL failed, trying fallback...`);
      currentApiUrl = FALLBACK_API_URL;
      response = await fetch(`${currentApiUrl}/images/${normalizedCategory}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    
    if (data.images && data.images.length > 0) {
      // Find matching image by name if provided
      if (imageName) {
        const matchingImage = data.images.find(img => 
          img.name.toLowerCase().includes(imageName?.toLowerCase() || '') ||
          imageName?.toLowerCase().includes(img.name.toLowerCase().split('.')[0] || '')
        );
        
        if (matchingImage) {
          return matchingImage.url;
        }
      }
      
      // Return first image if no specific match or no imageName provided
      return data.images[0].url;
    }
    
    return null;
  } catch (error) {
    console.warn(`Failed to fetch image for ${category}/${imageName}:`, error);
    return null;
  }
};

/**
 * Get all images for a category from backend API
 * @param {string} category - Plant category
 * @returns {Promise<Array>} Array of image objects
 */
export const getCategoryImages = async (category) => {
  if (!category) return [];
  
  const normalizedCategory = CATEGORY_MAPPING[category.toLowerCase()] || category.toLowerCase();
  
  if (!['flower', 'herb', 'vegetable'].includes(normalizedCategory)) {
    console.warn(`Invalid category: ${category}`);
    return [];
  }
  
  try {
    let response;
    try {
      response = await fetch(`${currentApiUrl}/images/${normalizedCategory}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
    } catch (error) {
      console.warn(`[IMAGE HELPER] Primary URL failed, trying fallback...`);
      currentApiUrl = FALLBACK_API_URL;
      response = await fetch(`${currentApiUrl}/images/${normalizedCategory}`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    return data.images || [];
  } catch (error) {
    console.warn(`Failed to fetch images for category ${category}:`, error);
    return [];
  }
};

/**
 * Fallback/placeholder image component
 * @param {string} category - Plant category
 * @returns {string} Text placeholder or SVG path
 */
export const getPlaceholderImage = (category) => {
  const placeholders = {
    flower: 'Flower',
    herb: 'Herb', 
    vegetable: 'Vegetable'
  };
  
  return placeholders[category] || 'Plant';
};

/**
 * Get all available plant categories
 * @returns {string[]} Array of category names
 */
export const getPlantCategories = () => {
  return ['flower', 'herb', 'vegetable'];
};

/**
 * Validate if a category exists
 * @param {string} category - Category to validate
 * @returns {boolean} True if category exists
 */
export const isValidCategory = (category) => {
  if (!category) return false;
  const normalizedCategory = CATEGORY_MAPPING[category.toLowerCase()] || category.toLowerCase();
  return ['flower', 'herb', 'vegetable'].includes(normalizedCategory);
};

/**
 * Handle image loading errors with fallback
 * @param {Event} event - Image error event
 * @param {string} category - Plant category for placeholder
 */
export const handleImageError = (event, category = null) => {
  const img = event.target;
  
  // Prevent infinite loop
  if (img.src.includes('placeholder-plant.svg')) {
    return;
  }
  
  console.warn('Failed to load image:', img.src);
  
  // Final fallback to placeholder
  img.src = '/placeholder-plant.svg';
  img.alt = `Plant image unavailable for ${getPlaceholderImage(category)}`;
};

/**
 * Preload images for better performance
 * @param {string[]} categories - Categories to preload
 * @returns {Promise[]} Array of image load promises
 */
export const preloadPlantImages = (categories = []) => {
  return categories.map(async category => {
    try {
      const imageUrl = await getPlantImageUrl(category);
      if (imageUrl) {
        return new Promise((resolve) => {
          const img = new Image();
          img.onload = () => resolve({ category, status: 'loaded' });
          img.onerror = () => resolve({ category, status: 'error' });
          img.src = imageUrl;
        });
      }
      return { category, status: 'no-image' };
    } catch (error) {
      return { category, status: 'error', error };
    }
  });
};

// Default export for convenience
export default {
  getPlantImageUrl,
  getCategoryImages,
  getPlaceholderImage,
  getPlantCategories,
  isValidCategory,
  handleImageError,
  preloadPlantImages
};