from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.auth_routes import router as auth_router
from app.api.v1.infra_routes import router as infra_router
from app.api.v1.internal_routes import router as internal_router
from app.api.v1.main_routes import router as main_router
from app.api.v1.websocket_routes import router as websocket_router
from app.log_setup import get_app_logger
import uvicorn

app = FastAPI(title="${PROJECT_NAME} API", logger=get_app_logger())

# CORS: do not combine allow_credentials=True with allow_origins=["*"].
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)
app.include_router(auth_router)
app.include_router(infra_router)
app.include_router(internal_router)
app.include_router(websocket_router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        reload=True,
        port=8000,
        log_level="info",
    )
