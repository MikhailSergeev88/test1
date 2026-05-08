# Network Technologies AI Assistant

Production-ready Telegram AI assistant for corporate knowledge base with RAG (Retrieval Augmented Generation).

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Google API Setup](#google-api-setup)
8. [Database Setup](#database-setup)
9. [Running the Application](#running-the-application)
10. [Docker Deployment](#docker-deployment)
11. [Admin Commands](#admin-commands)
12. [Troubleshooting](#troubleshooting)
13. [API Reference](#api-reference)

---

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Telegram Bot   │────▶│   Bot Handler    │────▶│  Auth Service   │
│   (aiogram)     │     │    (aiogram)     │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │
                                ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Qwen LLM      │◀────│   RAG Pipeline   │◀────│ Vector Database │
│    (API)        │     │  (LangChain)     │     │  (pgvector)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                ▲
                                │
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Google Drive   │────▶│ Document Sync    │────▶│  PostgreSQL     │
│     (API)       │     │   Service        │     │  (Documents)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Component Interaction

1. **User** sends message to Telegram Bot
2. **Bot Handler** receives and validates the message
3. **Auth Service** checks user permissions
4. **RAG Pipeline**:
   - Converts query to embeddings
   - Searches vector database
   - Retrieves relevant document chunks
   - Reranks results
5. **LLM Provider** generates response based on retrieved context
6. **Bot** sends formatted response with citations

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Language** | Python 3.12+ |
| **Telegram Bot** | aiogram 3.x |
| **LLM** | Qwen API |
| **RAG Framework** | LangChain |
| **Vector Database** | PostgreSQL + pgvector |
| **ORM** | SQLAlchemy 2.x |
| **Migrations** | Alembic |
| **Task Scheduler** | APScheduler |
| **Speech-to-Text** | OpenAI Whisper |
| **OCR** | Tesseract / PaddleOCR |
| **Containerization** | Docker, docker-compose |
| **Validation** | Pydantic v2 |

---

## Project Structure

```
network-tech-bot/
├── app/
│   ├── bot/
│   │   ├── handlers/          # Message handlers
│   │   ├── middleware/        # Authentication, rate limiting
│   │   └── keyboards/         # Inline keyboards
│   ├── rag/                   # RAG pipeline components
│   ├── llm/                   # LLM provider abstraction
│   ├── database/
│   │   ├── models/            # SQLAlchemy models
│   │   ├── repositories/      # Data access layer
│   │   └── migrations/        # Alembic migrations
│   ├── auth/                  # Authorization logic
│   ├── admin/                 # Admin panel handlers
│   ├── services/              # Business logic services
│   ├── utils/                 # Utility functions
│   ├── config/                # Configuration management
│   └── logging/               # Logging configuration
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/
│   ├── unit/
│   └── integration/
├── .env.example
├── alembic.ini
└── README.md
```

---

## Prerequisites

- **Python**: 3.12 or higher
- **PostgreSQL**: 15+ with pgvector extension
- **Docker**: 24+ (optional, for containerized deployment)
- **Tesseract OCR**: For image processing
- **Git**: For version control

### System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv postgresql postgresql-contrib tesseract-ocr libtesseract-dev

# macOS
brew install python@3.12 postgresql tesseract
```

---

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd network-tech-bot
```

### 2. Create Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements/prod.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file with your credentials (see [Configuration](#configuration)).

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash

# Qwen LLM
QWEN_API_KEY=your_qwen_api_key
QWEN_MODEL_NAME=qwen-max
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/network_tech_db
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Google Drive API
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_DRIVE_FOLDER_ID=your_folder_id
GOOGLE_CREDENTIALS_PATH=./credentials/google_credentials.json

# Admin Configuration
ADMIN_IDS=123456789,987654321

# Security
SECRET_KEY=your_secret_key_for_sessions
RATE_LIMIT_PER_MINUTE=10

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/bot.log

# Application
APP_ENV=production
DEBUG=false
```

---

## Google API Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable required APIs:
   - Google Drive API
   - Google Docs API

### 2. Create OAuth Credentials

1. Navigate to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. Select **Web application**
4. Add authorized redirect URIs
5. Download credentials JSON

### 3. Set Up Service Account (Optional)

For server-to-server authentication:

1. Go to **IAM & Admin** > **Service Accounts**
2. Create new service account
3. Grant **Drive API** permissions
4. Download JSON key file
5. Save to `./credentials/google_credentials.json`

### 4. Share Google Drive Folder

1. Create folder in Google Drive with company documents
2. Share folder with service account email
3. Copy folder ID to `GOOGLE_DRIVE_FOLDER_ID`

---

## Database Setup

### 1. Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

### 2. Create Database and User

```bash
sudo -u postgres psql

CREATE DATABASE network_tech_db;
CREATE USER network_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE network_tech_db TO network_user;
\q
```

### 3. Enable pgvector Extension

```bash
# Connect to database
psql -U network_user -d network_tech_db

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify installation
SELECT * FROM pg_extension WHERE extname = 'vector';
\q
```

### 4. Run Migrations

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Run migrations
alembic upgrade head
```

---

## Running the Application

### Development Mode

```bash
# Set environment
export APP_ENV=development
export DEBUG=true

# Run bot
python -m app.main
```

### Production Mode

```bash
# Using gunicorn with uvicorn workers
gunicorn app.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:8000
```

### With Task Scheduler

```bash
# Start scheduler for background tasks
python -m app.services.scheduler
```

---

## Docker Deployment

### 1. Build Docker Image

```bash
docker-compose build
```

### 2. Start Services

```bash
docker-compose up -d
```

### 3. View Logs

```bash
docker-compose logs -f bot
docker-compose logs -f db
```

### 4. Stop Services

```bash
docker-compose down
```

### 5. Production Deployment

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d
```

---

## Admin Commands

| Command | Description |
|---------|-------------|
| `/admin` | Show admin panel |
| `/users` | List all users |
| `/approve <user_id>` | Approve user access |
| `/reject <user_id>` | Reject access request |
| `/ban <user_id>` | Ban user |
| `/unban <user_id>` | Unban user |
| `/documents` | List indexed documents |
| `/reindex` | Reindex all documents |
| `/stats` | Show usage statistics |
| `/logs` | View recent logs |

### Admin Panel Features

- User management (approve/reject/ban)
- Document management (add/remove/reindex)
- Statistics dashboard
- Error logs viewer
- System health check

---

## Troubleshooting

### Common Issues

#### 1. Bot Not Responding

**Check:**
- Bot token is correct in `.env`
- Bot is running (`docker-compose ps`)
- Network connectivity

**Solution:**
```bash
docker-compose restart bot
docker-compose logs bot
```

#### 2. Database Connection Error

**Check:**
- PostgreSQL is running
- Database credentials in `.env`
- pgvector extension installed

**Solution:**
```bash
docker-compose restart db
docker-compose exec db psql -U network_user -d network_tech_db -c "SELECT 1"
```

#### 3. Google Drive Sync Fails

**Check:**
- Google credentials are valid
- Service account has access to folder
- Folder ID is correct

**Solution:**
```bash
python -m app.services.document_sync --test
```

#### 4. LLM API Errors

**Check:**
- Qwen API key is valid
- API quota not exceeded
- Network connectivity to API

**Solution:**
```bash
curl -H "Authorization: Bearer $QWEN_API_KEY" https://dashscope.aliyuncs.com/compatible-mode/v1/models
```

#### 5. OCR Not Working

**Check:**
- Tesseract installed
- Tesseract in PATH
- Language data installed

**Solution:**
```bash
tesseract --version
sudo apt-get install tesseract-ocr-rus
```

### Log Files

```bash
# Application logs
tail -f logs/bot.log

# Docker logs
docker-compose logs -f

# Database logs
docker-compose exec db tail -f /var/log/postgresql/postgresql.log
```

---

## API Reference

### Internal API Endpoints

#### Health Check

```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "llm": "available",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### Metrics

```http
GET /metrics
```

Response:
```json
{
  "total_users": 50,
  "active_users": 25,
  "total_queries": 1000,
  "avg_response_time_ms": 250
}
```

---

## Security Best Practices

1. **Never commit `.env` file** - Contains sensitive credentials
2. **Use strong passwords** - For database and API keys
3. **Enable SSL** - For production database connections
4. **Regular updates** - Keep dependencies updated
5. **Rate limiting** - Prevent abuse
6. **Input validation** - All user inputs validated
7. **Audit logging** - Track all admin actions

---

## Performance Optimization

### Database

- Connection pooling configured
- Indexes on frequently queried columns
- pgvector HNSW index for fast similarity search

### Caching

- Embeddings cached for repeated queries
- Document chunks cached in memory
- Redis for session storage (optional)

### Async Operations

- All I/O operations are async
- Background task processing
- Non-blocking document indexing

---

## Future Enhancements

- [ ] Web admin panel
- [ ] Slack integration
- [ ] WhatsApp integration
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Custom LLM fine-tuning
- [ ] Multi-tenant support

---

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Email: support@network-tech.com
- Documentation: [Internal Wiki]

---

## License

Proprietary - Network Technologies © 2024
