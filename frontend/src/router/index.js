import { createRouter, createWebHistory } from 'vue-router'

import MapView from '../components/MapView.vue'

const routes = [
  {
    path: '/',
    name: 'MapView',
    component: MapView
  },
  {
    path: '/amap-enhanced',
    name: 'AmapEnhanced',
    component: () => import('../components/AmapEnhancedView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router