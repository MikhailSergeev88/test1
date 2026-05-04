import express from 'express'
import cors from 'cors'
import dotenv from 'dotenv'
import mongoose from 'mongoose'
import petRoutes from './routes/pet.js'
import telegramService from './utils/telegram.js'

// Load environment variables
dotenv.config()

const app = express()
const PORT = process.env.PORT || 5000

// Middleware
app.use(cors())
app.use(express.json())

// Database connection
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/tamagotchi')
  .then(() => console.log('✅ MongoDB connected'))
  .catch(err => console.error('❌ MongoDB connection error:', err))

// Routes
app.use('/api', petRoutes)

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    telegram: telegramService.isInitialized() ? 'connected' : 'not configured'
  })
})

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Error:', err)
  res.status(500).json({
    success: false,
    error: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
  })
})

// Start periodic check for pets needing attention
setInterval(async () => {
  try {
    const Pet = (await import('./models/Pet.js')).default
    
    // Find pets with critical stats that haven't been notified recently
    const criticalPets = await Pet.find({
      $or: [
        { health: { $lt: 30 } },
        { hunger: { $lt: 20 } },
        { happiness: { $lt: 20 } }
      ]
    }).limit(10)
    
    for (const pet of criticalPets) {
      await telegramService.sendCriticalNotification(pet.telegramId, pet)
    }
  } catch (error) {
    console.error('Error in periodic check:', error)
  }
}, 60 * 60 * 1000) // Check every hour

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`)
  console.log(`📱 Frontend URL: ${process.env.FRONTEND_URL || 'http://localhost:3000'}`)
  console.log(`🤖 Telegram Bot: ${telegramService.isInitialized() ? 'Active' : 'Not configured'}`)
})

export default app
