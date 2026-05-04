<template>
  <div class="achievements-page">
    <header class="header">
      <router-link to="/" class="back-btn">← Назад</router-link>
      <h1>🏆 Достижения</h1>
      <div class="placeholder"></div>
    </header>

    <div class="achievements-content">
      <!-- Progress Summary -->
      <div class="progress-summary">
        <div class="progress-circle">
          <svg viewBox="0 0 36 36" class="circular-chart">
            <path
              class="circle-bg"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke="#e9ecef"
              stroke-width="3"
            />
            <path
              class="circle"
              :stroke-dasharray="`${progress}, 100`"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke="url(#gradient)"
              stroke-width="3"
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
              </linearGradient>
            </defs>
          </svg>
          <span class="progress-text">{{ achievements.length }}/{{ totalAchievements }}</span>
        </div>
        <p class="progress-label">достижений открыто</p>
      </div>

      <!-- Achievements List -->
      <div class="achievements-list">
        <div 
          v-for="achievement in allAchievements" 
          :key="achievement.id"
          class="achievement-item"
          :class="{ unlocked: isUnlocked(achievement.id) }"
        >
          <div class="achievement-icon">
            {{ achievement.unlocked ? '🏆' : '🔒' }}
          </div>
          <div class="achievement-info">
            <h3 class="achievement-name">{{ achievement.name }}</h3>
            <p class="achievement-description">{{ achievement.description }}</p>
            <p v-if="isUnlocked(achievement.id)" class="achievement-date">
              Получено: {{ getUnlockDate(achievement.id) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="achievements.length === 0" class="empty-state">
        <div class="empty-icon">🎯</div>
        <h3>Пока нет достижений</h3>
        <p>Заботьтесь о питомце и получайте достижения!</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { usePetStore } from '../store/pet'

const petStore = usePetStore()
const { achievements } = petStore

const totalAchievements = 4

const allAchievements = [
  {
    id: 'first_level',
    name: 'Первый уровень',
    description: 'Достигните уровня 1',
    unlocked: false
  },
  {
    id: 'level_5',
    name: 'Опытный владелец',
    description: 'Достигните уровня 5',
    unlocked: false
  },
  {
    id: 'level_10',
    name: 'Мастер заботы',
    description: 'Достигните уровня 10',
    unlocked: false
  },
  {
    id: 'perfect_health',
    name: 'Здоровяк',
    description: 'Поддерживайте здоровье на 100%',
    unlocked: false
  }
]

const progress = computed(() => {
  return Math.round((achievements.value.length / totalAchievements) * 100)
})

function isUnlocked(id) {
  return achievements.value.some(a => a.id === id)
}

function getUnlockDate(id) {
  const achievement = achievements.value.find(a => a.id === id)
  if (!achievement || !achievement.unlockedAt) return ''
  return new Date(achievement.unlockedAt).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}
</script>

<style scoped>
.achievements-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 15px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.back-btn {
  text-decoration: none;
  color: #667eea;
  font-weight: 600;
  padding: 8px 15px;
  background: #f8f9fa;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: #e9ecef;
}

.header h1 {
  margin: 0;
  color: #333;
  font-size: 1.5rem;
}

.placeholder {
  width: 80px;
}

.achievements-content {
  max-width: 600px;
  margin: 0 auto;
}

.progress-summary {
  background: white;
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.progress-circle {
  position: relative;
  width: 150px;
  height: 150px;
  margin: 0 auto 15px;
}

.circular-chart {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.circle {
  transition: stroke-dasharray 1s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 2rem;
  font-weight: bold;
  color: #667eea;
}

.progress-label {
  color: #666;
  font-size: 1rem;
}

.achievements-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.achievement-item {
  background: white;
  border-radius: 15px;
  padding: 20px;
  display: flex;
  gap: 20px;
  align-items: center;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  opacity: 0.6;
  filter: grayscale(1);
  transition: all 0.3s ease;
}

.achievement-item.unlocked {
  opacity: 1;
  filter: grayscale(0);
  background: linear-gradient(135deg, #fff 0%, #f8f9fa 100%);
}

.achievement-icon {
  font-size: 3rem;
  min-width: 60px;
  text-align: center;
}

.achievement-info {
  flex: 1;
}

.achievement-name {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 1.2rem;
}

.achievement-description {
  margin: 0 0 8px 0;
  color: #666;
  font-size: 0.9rem;
}

.achievement-date {
  margin: 0;
  color: #667eea;
  font-size: 0.85rem;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 1.5rem;
}

.empty-state p {
  margin: 0;
  color: #666;
  font-size: 1rem;
}
</style>
