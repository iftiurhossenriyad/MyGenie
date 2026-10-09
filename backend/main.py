from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import (
    auth,
    workspaces,
    tasks,
    notes,
    appointments,
    business,
    products,
    orders,
    bookings,
    conversations,
)

app = FastAPI(
    title="MyGenie API",
    description="An Intelligent AI-Powered Personal and Business Assistant",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(workspaces.router)
app.include_router(tasks.router)
app.include_router(notes.router)
app.include_router(appointments.router)
app.include_router(business.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(bookings.router)
app.include_router(conversations.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to MyGenie API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}