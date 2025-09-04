import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import HomeView from '../views/HomeView.vue'
import RecommendationsView from '../views/RecommendationsView.vue'
import PlantsView from '../views/PlantsView.vue'
import GuidesView from '../views/GuidesView.vue'
import DashboardView from '../views/DashboardView.vue'
import MyImpactView from '../views/MyImpactView.vue'

// Helper function to check authentication
const isAuthenticated = (): boolean => {
  return localStorage.getItem('plantopia_logged_in') === 'true'
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresGuest: true }
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/recommendations',
      name: 'recommendations',
      component: RecommendationsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/plants',
      name: 'plants',
      component: PlantsView,
      meta: { requiresAuth: true }
    },
    {
      path: '/guides',
      name: 'guides',
      component: GuidesView,
      meta: { requiresAuth: true }
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true }
    },
    {
      path: '/my-impact',
      name: 'my-impact',
      component: MyImpactView,
      meta: { requiresAuth: true }
    },
  ],
})

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  const authenticated = isAuthenticated()
  
  // If route requires authentication and user is not authenticated
  if (to.meta.requiresAuth && !authenticated) {
    next('/login')
  }
  // If route requires guest (like login) and user is already authenticated
  else if (to.meta.requiresGuest && authenticated) {
    next('/')
  }
  // Otherwise proceed normally
  else {
    next()
  }
})

export default router
