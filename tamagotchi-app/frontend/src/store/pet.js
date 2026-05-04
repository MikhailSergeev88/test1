import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePetStore = defineStore('pet', () => {
  // Состояние питомца
  const pet = ref({
    id: null,
    name: 'Питомец',
    age: 0,
    level: 1,
    experience: 0,
    stage: 'egg', // egg, baby, teen, adult, senior
    health: 100,
    hunger: 100,
    happiness: 100,
    energy: 100,
    hygiene: 100,
    createdAt: null,
    lastUpdate: null
  })

  const achievements = ref([])
  const isSleeping = ref(false)
  const isAnimating = ref(false)
  const animationEffect = ref(null)

  // Стадии роста
  const stages = {
    egg: { minLevel: 0, name: 'Яйцо' },
    baby: { minLevel: 1, name: 'Малыш' },
    teen: { minLevel: 5, name: 'Подросток' },
    adult: { minLevel: 10, name: 'Взрослый' },
    senior: { minLevel: 20, name: 'Пожилой' }
  }

  // Вычисляемые свойства
  const currentStage = computed(() => {
    if (pet.value.level >= 20) return 'senior'
    if (pet.value.level >= 10) return 'adult'
    if (pet.value.level >= 5) return 'teen'
    if (pet.value.level >= 1) return 'baby'
    return 'egg'
  })

  const overallMood = computed(() => {
    const avg = (pet.value.health + pet.value.hunger + pet.value.happiness + pet.value.energy) / 4
    if (avg >= 80) return 'excellent'
    if (avg >= 60) return 'good'
    if (avg >= 40) return 'okay'
    if (avg >= 20) return 'bad'
    return 'critical'
  })

  // Методы
  function loadPet() {
    const saved = localStorage.getItem('tamagotchi_pet')
    if (saved) {
      pet.value = JSON.parse(saved)
    } else {
      createNewPet()
    }
    
    const savedAchievements = localStorage.getItem('tamagotchi_achievements')
    if (savedAchievements) {
      achievements.value = JSON.parse(savedAchievements)
    }
    
    updateStats()
  }

  function createNewPet(name = 'Питомец') {
    pet.value = {
      id: Date.now(),
      name,
      age: 0,
      level: 0,
      experience: 0,
      stage: 'egg',
      health: 100,
      hunger: 100,
      happiness: 100,
      energy: 100,
      hygiene: 100,
      createdAt: new Date().toISOString(),
      lastUpdate: new Date().toISOString()
    }
    savePet()
  }

  function savePet() {
    pet.value.lastUpdate = new Date().toISOString()
    localStorage.setItem('tamagotchi_pet', JSON.stringify(pet.value))
    localStorage.setItem('tamagotchi_achievements', JSON.stringify(achievements.value))
  }

  function updateStats() {
    if (!pet.value.lastUpdate) return
    
    const now = new Date()
    const last = new Date(pet.value.lastUpdate)
    const hoursPassed = (now - last) / (1000 * 60 * 60)
    
    // Снижение показателей со временем
    pet.value.hunger = Math.max(0, pet.value.hunger - hoursPassed * 5)
    pet.value.happiness = Math.max(0, pet.value.happiness - hoursPassed * 3)
    pet.value.energy = Math.max(0, pet.value.energy - hoursPassed * 2)
    pet.value.hygiene = Math.max(0, pet.value.hygiene - hoursPassed * 4)
    
    // Здоровье зависит от других показателей
    if (pet.value.hunger < 20 || pet.value.happiness < 20 || pet.value.hygiene < 20) {
      pet.value.health = Math.max(0, pet.value.health - hoursPassed * 2)
    }
    
    // Возраст
    pet.value.age += hoursPassed
    
    pet.value.stage = currentStage.value
    savePet()
  }

  function startDecayTimer() {
    setInterval(() => {
      updateStats()
    }, 60000) // Обновление каждую минуту
  }

  function addAction(action, value) {
    pet.value[action] = Math.min(100, pet.value[action] + value)
    addExperience(10)
    showAnimation(action)
    checkAchievements()
    savePet()
  }

  function feed() {
    if (isSleeping.value) return
    addAction('hunger', 20)
  }

  function play() {
    if (isSleeping.value) return
    if (pet.value.energy < 20) return
    addAction('happiness', 15)
    pet.value.energy = Math.max(0, pet.value.energy - 10)
    savePet()
  }

  function sleep() {
    isSleeping.value = !isSleeping.value
    if (!isSleeping.value) {
      pet.value.energy = Math.min(100, pet.value.energy + 50)
      savePet()
    }
  }

  function heal() {
    if (isSleeping.value) return
    addAction('health', 25)
  }

  function clean() {
    if (isSleeping.value) return
    addAction('hygiene', 30)
    pet.value.happiness = Math.min(100, pet.value.happiness + 5)
    savePet()
  }

  function addExperience(amount) {
    pet.value.experience += amount
    const expNeeded = pet.value.level * 100
    
    if (pet.value.experience >= expNeeded) {
      pet.value.level++
      pet.value.experience = 0
      showAnimation('levelup')
    }
    
    pet.value.stage = currentStage.value
    savePet()
  }

  function showAnimation(effect) {
    animationEffect.value = effect
    isAnimating.value = true
    setTimeout(() => {
      isAnimating.value = false
      animationEffect.value = null
    }, 1000)
  }

  function checkAchievements() {
    const newAchievements = []
    
    if (pet.value.level >= 1 && !hasAchievement('first_level')) {
      newAchievements.push({ id: 'first_level', name: 'Первый уровень', description: 'Достигните уровня 1', unlockedAt: new Date().toISOString() })
    }
    
    if (pet.value.level >= 5 && !hasAchievement('level_5')) {
      newAchievements.push({ id: 'level_5', name: 'Опытный владелец', description: 'Достигните уровня 5', unlockedAt: new Date().toISOString() })
    }
    
    if (pet.value.level >= 10 && !hasAchievement('level_10')) {
      newAchievements.push({ id: 'level_10', name: 'Мастер заботы', description: 'Достигните уровня 10', unlockedAt: new Date().toISOString() })
    }
    
    if (pet.value.health === 100 && !hasAchievement('perfect_health')) {
      newAchievements.push({ id: 'perfect_health', name: 'Здоровяк', description: 'Поддерживайте здоровье на 100%', unlockedAt: new Date().toISOString() })
    }
    
    if (newAchievements.length > 0) {
      achievements.value.push(...newAchievements)
      savePet()
    }
  }

  function hasAchievement(id) {
    return achievements.value.some(a => a.id === id)
  }

  function resetGame() {
    localStorage.removeItem('tamagotchi_pet')
    localStorage.removeItem('tamagotchi_achievements')
    createNewPet()
    achievements.value = []
  }

  return {
    pet,
    achievements,
    isSleeping,
    isAnimating,
    animationEffect,
    currentStage,
    overallMood,
    stages,
    loadPet,
    createNewPet,
    savePet,
    feed,
    play,
    sleep,
    heal,
    clean,
    addExperience,
    showAnimation,
    checkAchievements,
    hasAchievement,
    resetGame,
    startDecayTimer
  }
})
