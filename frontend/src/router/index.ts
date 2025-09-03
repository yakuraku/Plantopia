import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RecommendationsView from '../views/RecommendationsView.vue'
import PlantsView from '../views/PlantsView.vue'
import GuidesView from '../views/GuidesView.vue'
import DashboardView from '../views/DashboardView.vue'
import MyImpactView from '../views/MyImpactView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/recommendations',
      name: 'recommendations',
      component: RecommendationsView,
    },
    {
      path: '/plants',
      name: 'plants',
      component: PlantsView,
    },
    {
      path: '/guides',
      name: 'guides',
      component: GuidesView,
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
    },
    {
      path: '/my-impact',
      name: 'my-impact',
      component: MyImpactView,
    },

  ],
})

export default router
