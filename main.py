from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up SEQ_SONIC application...")

    try:
        # Import the agent router
        from src.Backend.routes.agent import agent_router
        logger.info("Successfully imported agent router")
    except Exception as e:
        logger.error(f"Failed to import agent router: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

    yield
    # Shutdown
    logger.info("Shutting down SEQ_SONIC application...")

app = FastAPI(
    title="SEQ_SONIC - Sequence Analysis and Sonic Agent Platform",
    description="A FastAPI application for sequence analysis and AI agent interactions",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
try:
    from src.Backend.routes.agent import agent_router
    app.include_router(agent_router, tags=["agents"])
    logger.info("Successfully included agent router")
except Exception as e:
    logger.error(f"Failed to include agent router: {e}")
    logger.error(traceback.format_exc())

@app.get("/")
async def root():
    return {
        "message": "Welcome to SEQ_SONIC API",
        "version": "1.0.0",
        "endpoints": {
            "agents": "/agent",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SEQ_SONIC"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)




