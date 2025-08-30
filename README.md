# LinkedInAPI Project

A FastAPI-based LinkedIn API integration project with MongoDB, Redis, JWT authentication, and comprehensive LinkedIn posting capabilities.

## Features

- FastAPI with MongoDB database
- Redis for caching and session management
- LinkedIn API integration for posting and authentication
- JWT authentication
- MongoDB for flexible document storage
- MVC architecture
- Testing setup with pytest
- Environment configuration with .env
- Docker and Docker Compose support
- Database management UI with MongoDB Express

## Setup

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd fast-api-boilerplate
```

2. Create a `.env` file in the root directory with the following variables:
```bash
# Database Configuration
MONGODB_URL=mongodb://mongodb:27017/
MONGODB_DB_NAME=fastapi_db

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LinkedIn Configuration
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/v1/linkedin/callback
LINKEDIN_ACCESS_TOKEN_URL=https://www.linkedin.com/oauth/v2/accessToken
LINKEDIN_AUTH_URL=https://www.linkedin.com/oauth/v2/authorization
LINKEDIN_REST_URL=https://api.linkedin.com/v2
LINKEDIN_SCOPE=openid profile email w_member_social

# Application Configuration
PROJECT_NAME=LinkedInAPI Project
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
- MongoDB Express (Database admin): http://localhost:8081

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

3. Set up MongoDB and Redis locally and create a `.env` file with the configuration shown above, but update these values:
```bash
MONGODB_URL=mongodb://localhost:27017/
REDIS_HOST=localhost
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
app/
├── api/                # API routes
│   └── v1/
│       └── endpoints/  # API endpoint modules
├── core/              # Core functionality (config, security, logging, redis)
├── db/                # Database configuration
├── models/            # MongoDB models
├── schemas/           # Pydantic schemas
├── services/          # Business logic
└── tests/             # Test files
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

# Initialize MongoDB collections
make init-db

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

## API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## LinkedIn Integration

The project provides endpoints for:
1. LinkedIn OAuth authentication
2. Posting content to LinkedIn
3. Managing LinkedIn tokens and user sessions

To use the LinkedIn integration:
1. Set up a LinkedIn Developer Application at https://www.linkedin.com/developers/
2. Configure the OAuth 2.0 settings in your LinkedIn App
3. Update the `.env` file with your LinkedIn credentials
4. Use the `/api/v1/linkedin/auth` endpoint to start the OAuth flow

## Testing

Run tests with:
```bash
# Local testing
pytest

# Docker testing
docker-compose exec web pytest
```