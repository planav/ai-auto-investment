# AutoInvest - Setup Guide

## Prerequisites

Before starting the application, you need to set up the following:

### 1. PostgreSQL Database

Install PostgreSQL and create a database:

```bash
# macOS (using Homebrew)
brew install postgresql
brew services start postgresql

# Create database
createdb autoinvest_db

# Create user (optional)
createuser -P autoinvest_user
# Enter password: autoinvest_pass
```

### 2. Python Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
cd backend
cp .env.example .env
```

Edit the `.env` file with your database credentials:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://autoinvest_user:autoinvest_pass@localhost:5432/autoinvest_db
DATABASE_URL_SYNC=postgresql://autoinvest_user:autoinvest_pass@localhost:5432/autoinvest_db

# Security (generate a secure secret key)
SECRET_KEY=your-super-secret-key-change-this-in-production

# External APIs (optional - for production features)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
NEWS_API_KEY=your_news_api_key
OPENAI_API_KEY=your_openai_key

# Application Settings
APP_NAME=AutoInvest
DEBUG=true
ENVIRONMENT=development

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 4. Database Migrations

Run the database migrations:

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### 5. Node.js Environment (Frontend)

```bash
cd frontend/web

# Install dependencies
npm install
```

## Starting the Application

### Option 1: Start Both Services (Recommended)

Open two terminal windows:

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend/web
npm run dev
```

### Option 2: Using Docker (Future Enhancement)

Create a `docker-compose.yml` file for easier deployment.

## Accessing the Application

Once both services are running:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Default Test User

You can register a new user through the frontend, or use the API directly.

## Troubleshooting

### Database Connection Issues

1. Ensure PostgreSQL is running:
   ```bash
   brew services list | grep postgresql
   ```

2. Check database exists:
   ```bash
   psql -l | grep autoinvest
   ```

### Port Already in Use

If port 8000 or 5173 is in use:

- Backend: Change port with `--port 8001`
- Frontend: Vite will automatically find an available port

### Missing Dependencies

If you get import errors:
```bash
cd backend
pip install -r requirements.txt

cd frontend/web
npm install
```

## Production Deployment Notes

For production deployment:

1. Use a strong `SECRET_KEY`
2. Set `DEBUG=false` and `ENVIRONMENT=production`
3. Use a production PostgreSQL database
4. Set up Redis for caching
5. Configure external API keys (Alpha Vantage, News API, OpenAI)
6. Use HTTPS
7. Set up proper CORS origins

## API Keys (Optional Features)

The application works without these, but for full functionality:

- **Alpha Vantage**: https://www.alphavantage.co/support/#api-key
- **News API**: https://newsapi.org/register
- **OpenAI**: https://platform.openai.com/api-keys
