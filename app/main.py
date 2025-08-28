from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.endpoints import users, auth, linkedin
from app.core.logging import get_logger
import time
import uuid
from app.core.redis import get_redis, close_redis
from app.db.base import init_mongodb

# Set up logging
logger = get_logger("app.main")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    logger.info(f"Request started: {request.method} {request.url.path}")
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(f"Request completed: {request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.4f}s")
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.exception(f"Request failed: {request.method} {request.url.path} - Error: {str(e)} - Time: {process_time:.4f}s")
        raise

# Startup/Shutdown events
@app.on_event("startup")
async def on_startup():
    # Initialize MongoDB
    try:
        await init_mongodb()
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.exception(f"MongoDB connection failed: {e}")
        raise  # We raise here because the app can't work without MongoDB

    # Initialize Redis
    try:
        redis = await get_redis()
        await redis.ping()
        logger.info("Connected to Redis")
    except Exception as e:
        logger.exception(f"Redis connection failed: {e}")

@app.on_event("shutdown")
async def on_shutdown():
    await close_redis()

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}")
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(linkedin.router, prefix=f"{settings.API_V1_STR}", tags=["linkedin"])

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"message": "Welcome to FastAPI Boilerplate"}

@app.get("/health")
def health_check():
    logger.info("Health check endpoint called")
    return {"status": "healthy"}

@app.get("/redis/ping")
async def redis_ping():
    redis = await get_redis()
    pong = await redis.ping()
    return {"redis": "pong" if pong else "no-reply"} 