from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.auth import router as auth_router
from app.api.routers.health import router as health_router
from app.api.routers.users import router as users_router

app = FastAPI(
    title="E-commerce Core API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS: временно максимально открыто — потом сузим
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)


@app.get("/")
def root():
    return {"name": "E-commerce Core API", "docs": "/docs"}
