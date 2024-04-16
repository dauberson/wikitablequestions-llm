import os

import uvicorn
from fastapi import FastAPI
from loguru import logger

from wikitablequestions_llm_service.services.health_service import health_router

APP_NAME = os.environ.get("APPLICATION_NAME")

prefix: str = f"/service/{APP_NAME}"

app = FastAPI(
    docs_url=prefix + "/docs",
    redoc_url=prefix,
    openapi_url=prefix + "/openapi.json",
)

# app.include_router(prefix=prefix, router=wikitablequestions_llm_router)
app.include_router(prefix=prefix, router=health_router)

if __name__ == "__main__":
    logger.info(f"Starting {APP_NAME} app...")
    logger.info(f"Root path: {prefix}")
    uvicorn.run(
        app=app,
        host="0.0.0.0",
        port=8000,
        access_log=True,
        log_config=None,
        workers=1,
    )
