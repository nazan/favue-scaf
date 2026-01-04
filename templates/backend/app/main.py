from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.v1.main_routes import router as main_router
from app.log_setup import get_app_logger
import uvicorn

app = FastAPI(title="${PROJECT_NAME} API", logger=get_app_logger())

# CORS (allow preflight OPTIONS for browser clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust to specific origins in non-dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(main_router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        reload=True,
        port=8000,
        log_level="info"
    )

