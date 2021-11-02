from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import asyncio
from api.tracker import TrackerService

# Initialize Tracker Service
tracker_service = TrackerService()


# Setup FastAPI app
app = FastAPI(
    title="API Server",
    description="API Server",
    version="v1"
)

# Enable CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # Startup tasks
    # Start the tracker service
    asyncio.create_task(tracker_service.track())


# Routes
@app.get("/")
async def get_index():
    return {
        "message": "Welcome to the API Service"
    }

@app.get("/amazing")
async def get_index():
    return {
        "message": "Welcome to the amazing API Service"
    }
