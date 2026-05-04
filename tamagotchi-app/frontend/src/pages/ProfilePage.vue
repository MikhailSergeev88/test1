<template>
  <div class="profile-page">
    <header class="header">
      <router-link to="/" class="back-btn">← Назад</router-link>
      <h1>Профиль</h1>
      <div class="placeholder"></div>
    </header>

    <div class="profile-content">
      <!-- Pet Info Card -->
      <div class="pet-info-card">
        <div class="pet-avatar-large">
          <PetAvatar :stage="currentStage" :isSleeping="isSleeping" :mood="overallMood" />
        </div>
        
        <div class="pet-details">
          <h2>{{ pet.name }}</h2>
          <p class="stage-name">{{ stages[currentStage]?.name || currentStage }}</p>
          
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">Уровень</span>
              <span class="info-value">{{ pet.level }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Опыт</span>
              <span class="info-value">{{ pet.experience }}/{{ pet.level * 100 }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Возраст</span>
              <span class="info-value">{{ formatAge(pet.age) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Настроение</span>
              <span class="info-value mood">{{ getMoodEmoji() }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Overview -->
      <div class="stats-overview">
        <h3>📊 Состояние питомца</h3>
        <div class="stats-grid">
          <div class="stat-card" :style="{ borderColor: '#ff6b6b' }">
            <span class="stat-icon">❤️</span>
            <span class="stat-number" :style="{ color: '#ff6b6b' }">{{ Math.round(pet.health) }}%</span>
            <span class="stat-label">Здоровье</span>
          </div>
          <div class="stat-card" :style="{ borderColor: '#feca57' }">
            <span class="stat-icon">🍖</span>
            <span class="stat-number" :style="{ color: '#feca57' }">{{ Math.round(pet.hunger) }}%</span>
            <span class="stat-label">Сытость</span>
          </div>
          <div class="stat-card" :style="{ borderColor: '#ff9ff3' }">
            <span class="stat-icon">😊</span>
            <span class="stat-number" :style="{ color: '#ff9ff3' }">{{ Math.round(pet.happiness) }}%</span>
            <span class="stat-label">Счастье</span>
          </div>
          <div class="stat-card" :style="{ borderColor: '#54a0ff' }">
            <span class="stat-icon">⚡</span>
            <span class="stat-number" :style="{ color: '#54a0ff' }">{{ Math.round(pet.energy) }}%</span>
            <span class="stat-label">Энергия</span>
          </div>
          <div class="stat-card" :style="{ borderColor: '#48dbfb' }">
            <span class="stat-icon">🧼</span>
            <span class="stat-number" :style="{ color: '#48dbfb' }">{{ Math.round(pet.hygiene) }}%</span>
            <span class="stat-label">Гигиена</span>
          </div>
        </div>
      </div>

      <!-- Game Settings -->
      <div class="settings-section">
        <h3>⚙️ Настройки игры</h3>
        <div class="settings-list">
          <button @click="requestNotificationPermission" class="setting-btn">
            <span class="setting-icon">🔔</span>
            <span class="setting-text">Включить уведомления</span>
          </button>
          <button @click="confirmReset" class="setting-btn danger">
            <span class="setting-icon">🔄</span>
            <span class="setting-text">Начать заново</span>
          </button>
        </div>
      </div>

      <!-- Created Date -->
      <div class="created-date">
        <p>Питомец создан: {{ formatDate(pet.createdAt) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { usePetStore } from '../store/pet'
import PetAvatar from '../components/PetAvatar.vue'

const petStore = usePetStore()

const { 
  pet, 
  isSleeping, 
  currentStage, 
  overallMood, 
  stages,
  resetGame 
} = petStore

function formatAge(hours) {
  if (hours < 1) return 'Только что'
  if (hours < 24) return `${Math.floor(hours)} ч.`
  const days = hours / 24
  if (days < 30) return `${Math.floor(days)} дн.`
  const months = days / 30
  return `${Math.floor(months)} мес.`
}

function formatDate(dateString) {
  if (!dateString) return 'Неизвестно'
  return new Date(dateString).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getMoodEmoji() {
  switch(overallMood.value) {
    case 'excellent': return '🌟'
    case 'good': return '😊'
    case 'okay': return '😐'
    case 'bad': return '😟'
    case 'critical': return '🚨'
    default: return '❓'
  }
}

function requestNotificationPermission() {
  if ('Notification' in window) {
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        new Notification('Уведомления включены!', {
          body: 'Вы будете получать уведомления о состоянии питомца',
          icon: '/vite.svg'
        })
      }
    })
  } else {
    alert('Ваш браузер не поддерживает уведомления')
  }
}

function confirmReset() {
  if (confirm('Вы уверены? Весь прогресс будет потерян!')) {
    resetGame()
    alert('Игра началась заново!')
  }
}
</script>

<style scoped>
.profile-page {
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

.profile-content {
  max-width: 600px;
  margin: 0 auto;
}

.pet-info-card {
  background: white;
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.pet-avatar-large {
  margin-bottom: 20px;
  transform: scale(1.2);
}

.pet-details h2 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 1.8rem;
}

.stage-name {
  color: #667eea;
  font-weight: 600;
  margin-bottom: 20px;
  font-size: 1.1rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  width: 100%;
}

.info-item {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-label {
  font-size: 0.85rem;
  color: #666;
}

.info-value {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
}

.info-value.mood {
  font-size: 1.5rem;
}

.stats-overview {
  background: white;
  border-radius: 20px;
  padding: 25px;
  margin-bottom: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stats-overview h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 1.3rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 15px;
}

.stat-card {
  background: #f8f9fa;
  border-radius: 15px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  border-left: 4px solid;
}

.stat-icon {
  font-size: 1.8rem;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: bold;
}

.stat-label {
  font-size: 0.8rem;
  color: #666;
  text-align: center;
}

.settings-section {
  background: white;
  border-radius: 20px;
  padding: 25px;
  margin-bottom: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.settings-section h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 1.3rem;
}

.settings-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.setting-btn {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 20px;
  background: #f8f9fa;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  width: 100%;
  text-align: left;
}

.setting-btn:hover {
  background: #e9ecef;
  transform: translateX(5px);
}

.setting-btn.danger {
  color: #d63031;
}

.setting-btn.danger:hover {
  background: #ffeaea;
}

.setting-icon {
  font-size: 1.5rem;
}

.setting-text {
  flex: 1;
  font-weight: 500;
}

.created-date {
  text-align: center;
  color: #666;
  font-size: 0.9rem;
  padding: 15px;
}
</style>
