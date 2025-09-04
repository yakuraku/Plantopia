<script setup lang="ts">
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { computed } from 'vue'
import { useAuthStore } from './stores/auth'
import {
  HomeIcon,
  MagnifyingGlassIcon,
  BookOpenIcon,
  ChartBarIcon,
  TrophyIcon,
  BeakerIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isDarkNavbar = computed(() => false)
const showNavbar = computed(() => route.name !== 'login')

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div id="app">
    <nav v-if="showNavbar" class="navbar" :class="{ 'navbar-dark': isDarkNavbar }">
      <div class="nav-container">
        <div class="nav-logo">
          <RouterLink to="/" class="nav-brand"> Plantopia </RouterLink>
        </div>
        <ul class="nav-menu">
          <li class="nav-item">
            <RouterLink to="/" class="nav-link">
              <HomeIcon class="nav-icon" />
              Home
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/recommendations" class="nav-link">
              <MagnifyingGlassIcon class="nav-icon" />
              Recommendations
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/plants" class="nav-link">
              <BeakerIcon class="nav-icon" />
              Plants
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/guides" class="nav-link">
              <BookOpenIcon class="nav-icon" />
              Guides
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/dashboard" class="nav-link">
              <ChartBarIcon class="nav-icon" />
              Dashboard
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/my-impact" class="nav-link">
              <TrophyIcon class="nav-icon" />
              My Impact
            </RouterLink>
          </li>
          <li class="nav-item">
            <button @click="handleLogout" class="nav-link logout-button">
              <ArrowRightOnRectangleIcon class="nav-icon" />
              Logout
            </button>
          </li>
        </ul>
      </div>
    </nav>

    <main class="main-content" :class="{ 'no-navbar': !showNavbar }">
      <RouterView />
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: #f9fafb;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}

.navbar {
  background: transparent;
  position: sticky;
  top: 0;
  z-index: 1000;
  padding: 0;
  transition: all 0.3s ease;
}

.navbar-dark {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow:
    0 1px 3px 0 rgba(0, 0, 0, 0.1),
    0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.nav-container {
  max-width: 100%;
  width: 100%;
  margin: 0;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 80px;
  position: relative;
  transform: scale(0.9);
}

.nav-logo {
  position: absolute;
  left: 0rem;
}

.nav-brand {
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  text-decoration: none;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.navbar-dark .nav-brand {
  color: #111827;
}

.nav-brand:hover {
  color: #34d399;
}

.navbar-dark .nav-brand:hover {
  color: #10b981;
}

.nav-icon {
  width: 16px;
  height: 16px;
  stroke-width: 2;
}

.nav-menu {
  display: flex;
  list-style: none;
  gap: clamp(0.1rem, 0.5vw, 0.5rem);
  position: absolute;
  right: 0rem;
  flex-shrink: 0;
  white-space: nowrap;
}

.nav-item {
  position: relative;
}

.nav-link {
  color: white;
  text-decoration: none;
  font-weight: 500;
  font-size: clamp(0.75rem, 2vw, 1rem);
  padding: 0.5rem clamp(0.5rem, 1.5vw, 1rem);
  border-radius: 9999px;
  transition: all 0.2s ease;
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
  flex-shrink: 0;
}

.navbar-dark .nav-link {
  color: #374151;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.navbar-dark .nav-link:hover {
  background: rgba(52, 211, 153, 0.1);
  color: #10b981;
}

.nav-link.router-link-active {
  background: rgba(52, 211, 153, 0.8);
  color: white;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.1);
}

.navbar-dark .nav-link.router-link-active {
  background: rgba(52, 211, 153, 0.9);
  color: white;
  box-shadow: 0 2px 4px 0 rgba(52, 211, 153, 0.2);
}

.main-content {
  min-height: calc(100vh - 80px);
}

.main-content.no-navbar {
  min-height: 100vh;
}

.logout-button {
  background: none !important;
  border: none;
  cursor: pointer;
  font-family: inherit;
  font-size: inherit;
  font-weight: inherit;
}

/* Responsive adjustments for smaller screens */
@media (max-width: 1200px) {
  .nav-link {
    font-size: clamp(0.7rem, 1.8vw, 0.9rem);
    padding: 0.4rem clamp(0.3rem, 1.2vw, 0.8rem);
  }

  .nav-menu {
    gap: clamp(0.1rem, 0.3vw, 0.3rem);
  }
}

@media (max-width: 900px) {
  .nav-link {
    font-size: clamp(0.6rem, 1.5vw, 0.8rem);
    padding: 0.3rem clamp(0.2rem, 1vw, 0.6rem);
  }

  .nav-icon {
    width: 12px;
    height: 12px;
  }
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    height: auto;
    padding: 1rem 2rem;
    justify-content: center;
    align-items: center;
    position: static;
  }

  .nav-logo {
    position: static;
    left: auto;
    margin-bottom: 1rem;
  }

  .nav-menu {
    position: static;
    right: auto;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
  }

  .nav-link {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }

  .nav-icon {
    width: 14px;
    height: 14px;
  }

  .main-content {
    min-height: calc(100vh - 120px);
  }
}

@media (max-width: 480px) {
  .nav-container {
    padding: 0.5rem 1rem;
  }

  .nav-brand {
    font-size: 1.3rem;
  }

  .nav-menu {
    gap: 0.25rem;
  }

  .nav-link {
    padding: 0.3rem 0.6rem;
    font-size: 0.8rem;
  }

  .nav-icon {
    width: 12px;
    height: 12px;
  }
}
</style>
