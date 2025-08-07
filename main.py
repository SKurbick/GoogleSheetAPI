from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import (google_sheet_router, stock_data_router)
import uvicorn

from app.database.db_connect import init_db, close_db
from config import settings
from contextlib import asynccontextmanager


# Контекстный менеджер для управления жизненным циклом приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация пула соединений при старте приложения
    pool = await init_db()
    app.state.pool = pool
    yield
    # Закрытие пула соединений при завершении работы приложения
    await close_db(pool)


# Создаем экземпляр FastAPI с использованием lifespan
app = FastAPI(lifespan=lifespan, title="GoogleSheetAPI")

app.include_router(google_sheet_router, prefix="/api")
app.include_router(stock_data_router, prefix="/api")

origins = [
    "*",  # временное решение
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Список разрешённых origin
    allow_credentials=True,  # Разрешить передачу cookies и авторизационных данных
    allow_methods=["*"],  # Разрешить все HTTP методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.APP_IP_ADDRESS, port=settings.APP_PORT, reload=True)
