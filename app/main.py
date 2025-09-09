from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.health import router as health_router

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


@app.get("/")
def root():
    return {"name": "E-commerce Core API", "docs": "/docs"}
