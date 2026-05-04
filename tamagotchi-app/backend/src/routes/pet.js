import express from 'express'
import Pet from '../models/Pet.js'

const router = express.Router()

// Get or create pet for user
router.get('/pet/:telegramId', async (req, res) => {
  try {
    const { telegramId } = req.params
    const pet = await Pet.findOrCreate(telegramId)
    
    // Update stats based on time passed
    updatePetStats(pet)
    
    res.json({ success: true, pet })
  } catch (error) {
    console.error('Error getting pet:', error)
    res.status(500).json({ success: false, error: error.message })
  }
})

// Feed pet
router.post('/pet/:telegramId/feed', async (req, res) => {
  try {
    const { telegramId } = req.params
    const pet = await Pet.findOne({ telegramId })
    
    if (!pet) {
      return res.status(404).json({ success: false, error: 'Pet not found' })
    }
    
    if (pet.isSleeping) {
      return res.status(400).json({ success: false, error: 'Pet is sleeping' })
    }
    
    pet.hunger = Math.min(100, pet.hunger + 20)
    pet.experience += 10
    pet.updateStage()
    await pet.save()
    
    res.json({ success: true, pet })
  } catch (error) {
    console.error('Error feeding pet:', error)
    res.status(500).json({ success: false, error: error.message })
  }
})

// Play with pet
router.post('/pet/:telegramId/play', async (req, res) => {
  try {
    const { telegramId } = req.params
    const pet = await Pet.findOne({ telegramId })
    
    if (!pet) {
      return res.status(404).json({ success: false, error: 'Pet not found' })
    }
    
    if (pet.isSleeping) {
      return res.status(400).json({ success: false, error: 'Pet is sleeping' })
    }
    
    if (pet.energy < 20) {
      return res.status(400).json({ success: false, error: 'Not enough energy' })
    }
    
    pet.happiness = Math.min(100, pet.happiness + 15)
    pet.energy = Math.max(0, pet.energy - 10)
    pet.experience += 10
    pet.updateStage()
    await pet.save()
    
    res.json({ success: true, pet })
  } catch (error) {
    console.error('Error playing with pet:', error)
    res.status(500).json({ success: false, error: error.message })
  }
})

// Toggle sleep
router.post('/pet/:telegramId/sleep', async (req, res) => {
  try {
    const { telegramId } = req.params
    const pet = await Pet.findOne({ telegramId })
    
    if (!pet) {
      return res.status(404).json({ success: false, error: 'Pet not found' })
    }
    
    pet.isSleeping = !pet.isSleeping
    
    if (!pet.isSleeping) {
      // Waking up - restore some energy
      pet.energy = Math.min(100, pet.energy + 50)
    }
    
    await pet.save()
    
    res.json({ success: true, pet })
  } catch (error) {
    console.error('Error toggling sleep:', error)
    res.status(500).json({ success: false, error: error.message })
  }
})

// Heal pet
router.post('/pet/:telegramId/heal', async (req, res) => {
  try {
    const { telegramId } = req.params
    const pet = await Pet.findOne({ telegramId })
    
    if (!pet) {
      return res.status(404).json({ success: false, error: 'Pet not found' })
    }
    
    if (pet.isSleeping) {
      return res.status(400).json({ success: false, error: 'Pet is sleeping' })
    }
    
    pet.health = Math.min(100, pet.health + 25)
    pet.experience += 10
    pet.updateStage()
    await pet.save()
    
    res.json({ success: true, pet })
  } catch (error) {
    console.error('Error healing pet:', error)
    res.status(500).json({ success: false, error: error.message })
  }
})

// Clean pet
router.post('/pet/:telegramId/clean', async (req, res) => {
  try {
    const { telegramId } = req.params
    const pet = await Pet.findOne({ telegramId })
    
    if (!pet) {
      return res.status(404).json({ success: false, error: 'Pet not found' })
    }
    
    if (pet.isSleeping) {
      return res.status(400).json({ success: false, error: 'Pet is sleeping' })
    }
    
    pet.hygiene = Math.min(100, pet.hygiene + 30)
    pet.happiness = Math.min(100, pet.happiness + 5)
    pet.experience += 10
    pet.updateStage()
    await pet.save()
    
    res.json({ success: true, pet })
  } catch (error) {
    console.error('Error cleaning pet:', error)
    res.status(500).json({ success: false, error: error.message })
  }
})

// Helper function to update pet stats based on time
function updatePetStats(pet) {
  if (!pet.lastUpdate) return
  
  const now = new Date()
  const last = new Date(pet.lastUpdate)
  const hoursPassed = (now - last) / (1000 * 60 * 60)
  
  // Decay stats over time
  pet.hunger = Math.max(0, pet.hunger - hoursPassed * 5)
  pet.happiness = Math.max(0, pet.happiness - hoursPassed * 3)
  pet.energy = Math.max(0, pet.energy - hoursPassed * 2)
  pet.hygiene = Math.max(0, pet.hygiene - hoursPassed * 4)
  
  // Health decays if other stats are low
  if (pet.hunger < 20 || pet.happiness < 20 || pet.hygiene < 20) {
    pet.health = Math.max(0, pet.health - hoursPassed * 2)
  }
  
  // Age increases
  pet.age += hoursPassed
  
  pet.updateStage()
  pet.lastUpdate = now
  
  return pet.save()
}

export default router
