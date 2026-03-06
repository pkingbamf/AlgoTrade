from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.logging import configure_logging
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    init_db()
    yield


app = FastAPI(title="Quant Hedge Fund in a Box", lifespan=lifespan)
app.include_router(router)
