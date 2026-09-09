from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.routers import users, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables
    create_db_and_tables()
    yield


app = FastAPI(
    title="Task Management API",
    version="1.0.0",
    description="A FastAPI Task Management service with SQLModel, Auth dependencies, and Background Tasks.",
    lifespan=lifespan,
)

# Register Routers
app.include_router(users.router)
app.include_router(tasks.router)


@app.get("/")
def root():
    return {"message": "Welcome to the Task Management API. Visit /docs for interactive API documentation."}