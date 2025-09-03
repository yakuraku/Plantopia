/**
 * Google Drive Image Helper for Plantopia
 * Handles image URLs from public Google Drive folders
 */

const DRIVE_BASE_URL = 'https://drive.google.com/uc?export=view&id=';

// Public Google Drive folder IDs
const DRIVE_FOLDERS = {
  flower: '1ZcE9R3FMvZa5TRp8HfAHo-K7dAD5IfmL',
  herb: '1aVMw8n51wCndrlUb8xG5cRjsMvBnON7n',
  vegetable: '1rmv-7k70qL_fR1efsKa_t28I22pLKzf_'
};

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
 * Get Google Drive image URL for a plant image
 * @param {string} category - Plant category (flower, herb, vegetable)
 * @param {string} imageName - Image filename (optional, for future file-specific URLs)
 * @returns {string} Google Drive image URL
 */
export const getPlantImageUrl = (category, imageName = null) => {
  // Handle undefined/null category
  if (!category) {
    console.warn('No category provided for plant image');
    return '/placeholder-plant.svg'; // Fallback to existing placeholder
  }
  
  // Normalize category name
  const normalizedCategory = CATEGORY_MAPPING[category.toLowerCase()] || category.toLowerCase();
  const folderId = DRIVE_FOLDERS[normalizedCategory];
  
  if (!folderId) {
    console.warn(`No Google Drive folder found for category: ${category}`);
    return '/placeholder-plant.svg'; // Fallback to existing placeholder
  }
  
  // For now, return folder URL (will show folder contents)
  // Later can be enhanced to return specific file URLs when we have file ID mappings
  if (imageName) {
    console.log(`Requested specific image: ${imageName} from category: ${category}`);
    // TODO: Implement specific file ID mapping when needed
    // For now, still return folder URL
  }
  
  return `${DRIVE_BASE_URL}${folderId}`;
};

/**
 * Get thumbnail URL for Google Drive folder/file
 * @param {string} category - Plant category
 * @param {string} size - Thumbnail size (s150, s220, s320, etc.)
 * @returns {string} Google Drive thumbnail URL
 */
export const getPlantImageThumbnail = (category, size = 's220') => {
  const normalizedCategory = CATEGORY_MAPPING[category?.toLowerCase()] || category?.toLowerCase();
  const folderId = DRIVE_FOLDERS[normalizedCategory];
  
  if (!folderId) {
    return '/placeholder-plant.svg';
  }
  
  // Google Drive thumbnail URL format
  return `https://drive.google.com/thumbnail?id=${folderId}&sz=${size}`;
};

/**
 * Get all available plant categories
 * @returns {string[]} Array of category names
 */
export const getPlantCategories = () => {
  return Object.keys(DRIVE_FOLDERS);
};

/**
 * Validate if a category exists
 * @param {string} category - Category to validate
 * @returns {boolean} True if category exists
 */
export const isValidCategory = (category) => {
  if (!category) return false;
  const normalizedCategory = CATEGORY_MAPPING[category.toLowerCase()] || category.toLowerCase();
  return DRIVE_FOLDERS.hasOwnProperty(normalizedCategory);
};

/**
 * Handle image loading errors with fallback
 * @param {Event} event - Image error event
 * @param {string} category - Plant category for alternative URL
 */
export const handleImageError = (event, category = null) => {
  const img = event.target;
  
  // Prevent infinite loop
  if (img.src.includes('placeholder-plant.svg')) {
    return;
  }
  
  console.warn('Failed to load image:', img.src);
  
  // Try alternative Google Drive URL format first
  if (category && !img.dataset.retried) {
    img.dataset.retried = 'true';
    const thumbnailUrl = getPlantImageThumbnail(category);
    if (thumbnailUrl !== img.src) {
      img.src = thumbnailUrl;
      return;
    }
  }
  
  // Final fallback to placeholder
  img.src = '/placeholder-plant.svg';
  img.alt = 'Plant image unavailable';
};

/**
 * Preload images for better performance
 * @param {string[]} categories - Categories to preload
 * @returns {Promise[]} Array of image load promises
 */
export const preloadPlantImages = (categories = []) => {
  return categories.map(category => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => resolve({ category, status: 'loaded' });
      img.onerror = () => resolve({ category, status: 'error' });
      img.src = getPlantImageUrl(category);
    });
  });
};

// Default export for convenience
export default {
  getPlantImageUrl,
  getPlantImageThumbnail,
  getPlantCategories,
  isValidCategory,
  handleImageError,
  preloadPlantImages
};