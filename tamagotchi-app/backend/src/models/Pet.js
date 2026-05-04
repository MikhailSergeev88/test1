import mongoose from 'mongoose'

const petSchema = new mongoose.Schema({
  telegramId: {
    type: String,
    required: true,
    index: true
  },
  name: {
    type: String,
    default: 'Питомец'
  },
  age: {
    type: Number,
    default: 0
  },
  level: {
    type: Number,
    default: 0
  },
  experience: {
    type: Number,
    default: 0
  },
  stage: {
    type: String,
    enum: ['egg', 'baby', 'teen', 'adult', 'senior'],
    default: 'egg'
  },
  health: {
    type: Number,
    default: 100,
    min: 0,
    max: 100
  },
  hunger: {
    type: Number,
    default: 100,
    min: 0,
    max: 100
  },
  happiness: {
    type: Number,
    default: 100,
    min: 0,
    max: 100
  },
  energy: {
    type: Number,
    default: 100,
    min: 0,
    max: 100
  },
  hygiene: {
    type: Number,
    default: 100,
    min: 0,
    max: 100
  },
  isSleeping: {
    type: Boolean,
    default: false
  },
  achievements: [{
    id: String,
    name: String,
    description: String,
    unlockedAt: Date
  }],
  createdAt: {
    type: Date,
    default: Date.now
  },
  lastUpdate: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
})

// Index for efficient queries
petSchema.index({ telegramId: 1, lastUpdate: -1 })

// Method to calculate current stage based on level
petSchema.methods.updateStage = function() {
  if (this.level >= 20) this.stage = 'senior'
  else if (this.level >= 10) this.stage = 'adult'
  else if (this.level >= 5) this.stage = 'teen'
  else if (this.level >= 1) this.stage = 'baby'
  else this.stage = 'egg'
  return this.stage
}

// Method to calculate overall mood
petSchema.methods.getMood = function() {
  const avg = (this.health + this.hunger + this.happiness + this.energy) / 4
  if (avg >= 80) return 'excellent'
  if (avg >= 60) return 'good'
  if (avg >= 40) return 'okay'
  if (avg >= 20) return 'bad'
  return 'critical'
}

// Static method to find or create pet
petSchema.statics.findOrCreate = async function(telegramId, name) {
  let pet = await this.findOne({ telegramId })
  
  if (!pet) {
    pet = await this.create({
      telegramId,
      name: name || 'Питомец'
    })
  }
  
  return pet
}

export default mongoose.model('Pet', petSchema)
