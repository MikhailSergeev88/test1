import { createRouter, createWebHistory } from 'vue-router'
import GamePage from '../pages/GamePage.vue'
import ProfilePage from '../pages/ProfilePage.vue'
import AchievementsPage from '../pages/AchievementsPage.vue'

const routes = [
  {
    path: '/',
    name: 'Game',
    component: GamePage
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfilePage
  },
  {
    path: '/achievements',
    name: 'Achievements',
    component: AchievementsPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
