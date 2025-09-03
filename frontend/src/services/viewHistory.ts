import type { Plant } from './api'

const VIEW_HISTORY_KEY = 'plantopia_view_history'
const MAX_HISTORY_ITEMS = 8

// Complete plant interface for history storage (with timestamp)
interface HistoryPlant extends Plant {
  timestamp: number
}

// Convert full Plant object to HistoryPlant
const plantToHistoryPlant = (plant: Plant): HistoryPlant => ({
  ...plant,
  timestamp: Date.now()
})

// Convert HistoryPlant back to Plant object (remove timestamp)
const historyPlantToPlant = (historyPlant: HistoryPlant): Plant => {
  const { timestamp, ...plant } = historyPlant
  return plant
}

// Get view history from localStorage
export const getViewHistory = (): Plant[] => {
  try {
    const historyJson = localStorage.getItem(VIEW_HISTORY_KEY)
    if (!historyJson) return []
    
    const history: HistoryPlant[] = JSON.parse(historyJson)
    
    // Sort by timestamp (most recent first) and convert back to Plant objects
    return history
      .sort((a, b) => b.timestamp - a.timestamp)
      .map(historyPlantToPlant)
  } catch (error) {
    console.error('Error loading view history:', error)
    return []
  }
}

// Add plant to view history
export const addToViewHistory = (plant: Plant): void => {
  try {
    const currentHistory = getViewHistoryRaw()
    
    // Remove existing entry for this plant (if any)
    const filteredHistory = currentHistory.filter(item => item.id !== plant.id)
    
    // Add new entry at the beginning
    const newHistory = [plantToHistoryPlant(plant), ...filteredHistory]
    
    // Keep only the most recent MAX_HISTORY_ITEMS
    const trimmedHistory = newHistory.slice(0, MAX_HISTORY_ITEMS)
    
    // Save to localStorage
    localStorage.setItem(VIEW_HISTORY_KEY, JSON.stringify(trimmedHistory))
  } catch (error) {
    console.error('Error saving to view history:', error)
  }
}

// Get raw history data (internal use)
const getViewHistoryRaw = (): HistoryPlant[] => {
  try {
    const historyJson = localStorage.getItem(VIEW_HISTORY_KEY)
    if (!historyJson) return []
    
    return JSON.parse(historyJson)
  } catch (error) {
    console.error('Error loading raw view history:', error)
    return []
  }
}

// Clear view history
export const clearViewHistory = (): void => {
  try {
    localStorage.removeItem(VIEW_HISTORY_KEY)
  } catch (error) {
    console.error('Error clearing view history:', error)
  }
}

// Check if plant is in history
export const isInViewHistory = (plantId: string): boolean => {
  const history = getViewHistoryRaw()
  return history.some(item => item.id === plantId)
}
