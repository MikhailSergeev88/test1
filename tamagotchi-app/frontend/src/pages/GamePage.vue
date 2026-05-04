<template>
  <div class="game-page">
    <!-- Header -->
    <header class="header">
      <div class="header-left">
        <h1>{{ pet.name }}</h1>
        <span class="level-badge">Уровень {{ pet.level }}</span>
      </div>
      <nav class="nav">
        <router-link to="/profile" class="nav-btn">👤</router-link>
        <router-link to="/achievements" class="nav-btn">🏆</router-link>
      </nav>
    </header>

    <!-- Pet Display -->
    <div class="pet-container">
      <div class="pet-display" :class="{ sleeping: isSleeping }">
        <PetAvatar :stage="currentStage" :isSleeping="isSleeping" :mood="overallMood" />
        
        <!-- Animation Effects -->
        <div v-if="isAnimating" class="animation-overlay">
          <span v-if="animationEffect === 'feed'" class="effect">🍖</span>
          <span v-if="animationEffect === 'play'" class="effect">🎾</span>
          <span v-if="animationEffect === 'sleep'" class="effect">💤</span>
          <span v-if="animationEffect === 'heal'" class="effect">💊</span>
          <span v-if="animationEffect === 'clean'" class="effect">✨</span>
          <span v-if="animationEffect === 'levelup'" class="effect levelup">⭐⭐⭐</span>
        </div>
      </div>
      
      <div class="stage-indicator">
        {{ stages[currentStage]?.name || currentStage }}
      </div>
    </div>

    <!-- Stats -->
    <div class="stats-container">
      <StatBar 
        label="Здоровье" 
        :value="pet.health" 
        color="#ff6b6b"
        icon="❤️"
      />
      <StatBar 
        label="Сытость" 
        :value="pet.hunger" 
        color="#feca57"
        icon="🍖"
      />
      <StatBar 
        label="Счастье" 
        :value="pet.happiness" 
        color="#ff9ff3"
        icon="😊"
      />
      <StatBar 
        label="Энергия" 
        :value="pet.energy" 
        color="#54a0ff"
        icon="⚡"
      />
      <StatBar 
        label="Гигиена" 
        :value="pet.hygiene" 
        color="#48dbfb"
        icon="🧼"
      />
    </div>

    <!-- Actions -->
    <div class="actions-container">
      <ActionButton 
        @click="feed" 
        :disabled="isSleeping"
        icon="🍖" 
        label="Кормить"
        :tooltip="isSleeping ? 'Питомец спит!' : ''"
      />
      <ActionButton 
        @click="play" 
        :disabled="isSleeping || pet.energy < 20"
        icon="🎾" 
        label="Играть"
        :tooltip="pet.energy < 20 && !isSleeping ? 'Недостаточно энергии!' : ''"
      />
      <ActionButton 
        @click="sleep" 
        icon="🛏️" 
        :label="isSleeping ? 'Разбудить' : 'Спать'"
        :active="isSleeping"
      />
      <ActionButton 
        @click="heal" 
        :disabled="isSleeping"
        icon="💊" 
        label="Лечить"
        :tooltip="isSleeping ? 'Питомец спит!' : ''"
      />
      <ActionButton 
        @click="clean" 
        :disabled="isSleeping"
        icon="🧼" 
        label="Мыть"
        :tooltip="isSleeping ? 'Питомец спит!' : ''"
      />
    </div>

    <!-- Status Message -->
    <div class="status-message" :class="overallMood">
      <span v-if="overallMood === 'excellent'">🌟 Питомец чувствует себя прекрасно!</span>
      <span v-else-if="overallMood === 'good'">😊 Питомец в хорошем настроении</span>
      <span v-else-if="overallMood === 'okay'">😐 Питомец нормально себя чувствует</span>
      <span v-else-if="overallMood === 'bad'">😟 Питомцу нужна забота</span>
      <span v-else-if="overallMood === 'critical'">🚨 Питомцу срочно нужна помощь!</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { usePetStore } from '../store/pet'
import PetAvatar from '../components/PetAvatar.vue'
import StatBar from '../components/StatBar.vue'
import ActionButton from '../components/ActionButton.vue'

const petStore = usePetStore()

const { 
  pet, 
  isSleeping, 
  isAnimating, 
  animationEffect,
  currentStage,
  overallMood,
  stages
} = petStore

const { feed, play, sleep, heal, clean } = petStore
</script>

<style scoped>
.game-page {
  padding: 20px;
  min-height: 100vh;
  background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
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

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header h1 {
  font-size: 1.5rem;
  color: #333;
  margin: 0;
}

.level-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: bold;
}

.nav {
  display: flex;
  gap: 10px;
}

.nav-btn {
  text-decoration: none;
  font-size: 1.5rem;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.nav-btn:hover {
  background: #e9ecef;
  transform: scale(1.1);
}

.pet-container {
  background: white;
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 20px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  position: relative;
  min-height: 250px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.pet-display {
  position: relative;
  width: 150px;
  height: 150px;
  margin-bottom: 15px;
}

.animation-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  pointer-events: none;
}

.effect {
  font-size: 3rem;
  animation: float 1s ease-out forwards;
}

.effect.levelup {
  font-size: 2rem;
  animation: spin 1s ease-in-out infinite;
}

@keyframes float {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(-50px) scale(1.5);
  }
}

@keyframes spin {
  0%, 100% { transform: rotate(0deg); }
  50% { transform: rotate(180deg); }
}

.stage-indicator {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 8px 20px;
  border-radius: 20px;
  font-weight: bold;
  font-size: 1rem;
}

.stats-container {
  background: white;
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.actions-container {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 10px;
  margin-bottom: 20px;
}

@media (max-width: 480px) {
  .actions-container {
    grid-template-columns: repeat(3, 1fr);
  }
}

.status-message {
  text-align: center;
  padding: 15px;
  border-radius: 15px;
  font-weight: bold;
  animation: pulse 2s ease-in-out infinite;
}

.status-message.excellent {
  background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
  color: white;
}

.status-message.good {
  background: linear-gradient(135deg, #0984e3 0%, #74b9ff 100%);
  color: white;
}

.status-message.okay {
  background: linear-gradient(135deg, #fdcb6e 0%, #ffeaa7 100%);
  color: #333;
}

.status-message.bad {
  background: linear-gradient(135deg, #e17055 0%, #fab1a0 100%);
  color: white;
}

.status-message.critical {
  background: linear-gradient(135deg, #d63031 0%, #ff7675 100%);
  color: white;
  animation: shake 0.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.02); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
</style>
