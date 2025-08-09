# FastAPI Boilerplate

A FastAPI boilerplate with PostgreSQL, Alembic, JWT authentication, and MVC architecture.

## Features

- FastAPI with PostgreSQL database
- Alembic for database migrations
- JWT authentication
- MVC architecture
- Testing setup with pytest
- Environment configuration with .env
- Docker and Docker Compose support
- Database management UI with Adminer
- MongoDB for document storage

## Setup

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd backend
```

2. Create a `.env` file in the root directory with the following variables:
```bash
# Postgres
POSTGRES_SERVER=db
POSTGRES_USER=fastapi_user
POSTGRES_PASSWORD=fastapi_password
POSTGRES_DB=fastapi_db

# Redis (optional overrides)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# MongoDB (optional overrides)
MONGO_HOST=mongo
MONGO_PORT=27017
MONGO_DB=fastapi_mongo

# JWT
SECRET_KEY=your-super-secret-key-change-in-production-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
PROJECT_NAME=FastAPI Boilerplate
VERSION=1.0.0
API_V1_STR=/api/v1
```

3. Build and run with Docker Compose:
```bash
docker-compose up --build
```

The application will be available at:
- FastAPI app: http://localhost:8000
- API documentation: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Redis ping: http://localhost:8000/redis/ping
- Mongo ping: http://localhost:8000/mongo/ping
- Database admin (Adminer): http://localhost:8080

### Option 2: Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database locally and create a `.env` file:
```bash
# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=fastapi_db

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

4. Initialize the database:
```bash
alembic upgrade head
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
app/
├── api/           # API routes
├── core/          # Core functionality (config, security)
├── db/            # Database models and session
├── models/        # Pydantic models
├── schemas/       # SQLAlchemy models
├── services/      # Business logic
└── tests/         # Test files
```

## Docker Commands

### Using Makefile (Recommended)
```bash
# Show available commands
make help

# Development setup (build and start)
make dev

# Start services
make up

# Stop services
make down

# View logs
make logs

# Run tests
make test

# Access application shell
make shell

# Create new migration
make migration name="your_migration_name"

# Run migrations
make migrate

# Clean up everything
make clean
```

### Manual Docker Commands
```bash
# Build and start services
docker-compose up --build

# Start services in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (database data)
docker-compose down -v
```

### Production Build
```bash
# Build production image
docker build -t fastapi-app .

# Run production container (with external services)
docker run -p 8000:8000 \
  -e POSTGRES_SERVER=your-db-host \
  -e POSTGRES_USER=your-db-user \
  -e POSTGRES_PASSWORD=your-db-password \
  -e POSTGRES_DB=your-db-name \
  -e REDIS_HOST=your-redis-host -e REDIS_PORT=6379 -e REDIS_DB=0 \
  -e MONGO_HOST=your-mongo-host -e MONGO_PORT=27017 -e MONGO_DB=fastapi_mongo \
  -e SECRET_KEY=your-production-secret \
  fastapi-app
```

## Testing

Run tests with:
```bash
# Local testing
pytest

# Docker testing
docker-compose exec web pytest
``` 