import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', () => {
  const isLoggedIn = ref(false)
  const username = ref('')

  // Check if user is logged in from localStorage on store initialization
  const checkAuthStatus = () => {
    const savedLoginStatus = localStorage.getItem('plantopia_logged_in')
    const savedUsername = localStorage.getItem('plantopia_username')
    
    if (savedLoginStatus === 'true' && savedUsername) {
      isLoggedIn.value = true
      username.value = savedUsername
    }
  }

  // Login function
  const login = (user: string) => {
    isLoggedIn.value = true
    username.value = user
    localStorage.setItem('plantopia_logged_in', 'true')
    localStorage.setItem('plantopia_username', user)
  }

  // Logout function
  const logout = () => {
    isLoggedIn.value = false
    username.value = ''
    localStorage.removeItem('plantopia_logged_in')
    localStorage.removeItem('plantopia_username')
  }

  // Initialize auth status
  checkAuthStatus()

  return {
    isLoggedIn: computed(() => isLoggedIn.value),
    username: computed(() => username.value),
    login,
    logout,
    checkAuthStatus
  }
})
