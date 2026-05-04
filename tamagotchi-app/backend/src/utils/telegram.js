import TelegramBot from 'node-telegram-bot-api'
import Pet from '../models/Pet.js'

class TelegramService {
  constructor() {
    this.bot = null
    this.token = process.env.TELEGRAM_BOT_TOKEN
    
    if (this.token && this.token !== 'your_bot_token_here') {
      this.initBot()
    }
  }

  initBot() {
    try {
      this.bot = new TelegramBot(this.token, { polling: true })
      console.log('✅ Telegram bot initialized')
      this.setupHandlers()
    } catch (error) {
      console.error('❌ Failed to initialize Telegram bot:', error.message)
    }
  }

  setupHandlers() {
    // /start command
    this.bot.onText(/\/start/, async (msg) => {
      const chatId = msg.chat.id
      const telegramId = String(msg.from.id)
      
      try {
        let pet = await Pet.findOne({ telegramId })
        
        if (!pet) {
          pet = await Pet.create({
            telegramId,
            name: msg.from.first_name || 'Питомец'
          })
          
          this.bot.sendMessage(chatId, 
            `🎉 Добро пожаловать в Тамагочи!\n\n` +
            `У вас появился новый питомец: ${pet.name}\n` +
            `Стадия: 🥚 Яйцо\n\n` +
            `Заботьтесь о нём через веб-приложение:\n` +
            `${process.env.FRONTEND_URL || 'http://localhost:3000'}\n\n` +
            `Используйте команды:\n` +
            `/profile - посмотреть статус питомца\n` +
            `/help - справка`
          )
        } else {
          this.bot.sendMessage(chatId,
            `👋 С возвращением, ${msg.from.first_name}!\n\n` +
            `Ваш питомец ${pet.name} ждёт вас!\n` +
            `Откройте игру: ${process.env.FRONTEND_URL || 'http://localhost:3000'}`
          )
        }
      } catch (error) {
        console.error('Error in /start handler:', error)
      }
    })

    // /profile command
    this.bot.onText(/\/profile/, async (msg) => {
      const chatId = msg.chat.id
      const telegramId = String(msg.from.id)
      
      try {
        const pet = await Pet.findOne({ telegramId })
        
        if (!pet) {
          return this.bot.sendMessage(chatId, 
            '❌ У вас нет питомца. Используйте /start для создания.'
          )
        }
        
        const moodEmoji = this.getMoodEmoji(pet.getMood())
        
        this.bot.sendMessage(chatId,
          `📊 Профиль питомца\n\n` +
          `🐾 Имя: ${pet.name}\n` +
          `⭐ Уровень: ${pet.level}\n` +
          `🎭 Стадия: ${this.getStageName(pet.stage)}\n` +
          `⏰ Возраст: ${this.formatAge(pet.age)}\n\n` +
          `❤️ Здоровье: ${Math.round(pet.health)}%\n` +
          `🍖 Сытость: ${Math.round(pet.hunger)}%\n` +
          `😊 Счастье: ${Math.round(pet.happiness)}%\n` +
          `⚡ Энергия: ${Math.round(pet.energy)}%\n` +
          `🧼 Гигиена: ${Math.round(pet.hygiene)}%\n\n` +
          `${moodEmoji} Настроение: ${pet.getMood()}`
        )
      } catch (error) {
        console.error('Error in /profile handler:', error)
      }
    })

    // /help command
    this.bot.onText(/\/help/, (msg) => {
      const chatId = msg.chat.id
      
      this.bot.sendMessage(chatId,
        `📖 Справка по командам:\n\n` +
        `/start - Начать игру или войти\n` +
        `/profile - Показать статус питомца\n` +
        `/help - Эта справка\n\n` +
        `🎮 Полная версия игры доступна по адресу:\n` +
        `${process.env.FRONTEND_URL || 'http://localhost:3000'}`
      )
    })
  }

  // Send notification when pet needs attention
  async sendCriticalNotification(telegramId, pet) {
    if (!this.bot) return
    
    try {
      const chatId = telegramId
      const mood = pet.getMood()
      
      if (mood === 'critical' || mood === 'bad') {
        const messages = {
          critical: `🚨 СРОЧНО! Ваш питомец ${pet.name} в критическом состоянии!\n\n` +
                    `❤️ Здоровье: ${Math.round(pet.health)}%\n` +
                    `🍖 Сытость: ${Math.round(pet.hunger)}%\n` +
                    `😊 Счастье: ${Math.round(pet.happiness)}%\n\n` +
                    `Откройте игру и помогите ему!`,
          bad: `😟 Ваш питомец ${pet.name} плохо себя чувствует.\n\n` +
               `Проверьте его состояние в игре!`
        }
        
        await this.bot.sendMessage(chatId, messages[mood])
      }
    } catch (error) {
      console.error('Error sending notification:', error)
    }
  }

  getMoodEmoji(mood) {
    const emojis = {
      excellent: '🌟',
      good: '😊',
      okay: '😐',
      bad: '😟',
      critical: '🚨'
    }
    return emojis[mood] || '❓'
  }

  getStageName(stage) {
    const names = {
      egg: '🥚 Яйцо',
      baby: '👶 Малыш',
      teen: '🧒 Подросток',
      adult: '🧑 Взрослый',
      senior: '👴 Пожилой'
    }
    return names[stage] || stage
  }

  formatAge(hours) {
    if (hours < 1) return 'Только что'
    if (hours < 24) return `${Math.floor(hours)} ч.`
    const days = hours / 24
    if (days < 30) return `${Math.floor(days)} дн.`
    const months = days / 30
    return `${Math.floor(months)} мес.`
  }

  isInitialized() {
    return this.bot !== null
  }
}

export default new TelegramService()
