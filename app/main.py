from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import Base, engine
from app.routes import auth, interactions, locations, products, stores, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Autenticación"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["Usuarios"])
app.include_router(stores.router, prefix=f"{settings.API_V1_STR}/stores", tags=["Tiendas"])
app.include_router(locations.router, prefix=f"{settings.API_V1_STR}/locations", tags=["Ubicaciones"])
app.include_router(products.router, prefix=f"{settings.API_V1_STR}/products", tags=["Productos y Servicios"])
app.include_router(interactions.router, prefix=f"{settings.API_V1_STR}/interactions", tags=["Interacciones y Stats"])


@app.get("/", tags=["Health"])
def root():
    return {"message": "Mercado Plug API funcionando", "version": settings.VERSION}


@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
