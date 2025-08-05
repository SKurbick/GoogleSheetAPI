# todo подключение пользователя
# todo метод отправки данных

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import (google_sheet_router)
from contextlib import asynccontextmanager
import uvicorn
from app.config import settings



# Создаем экземпляр FastAPI с использованием lifespan
app = FastAPI(title="1CRoutingAPI")
app.include_router(google_sheet_router, prefix="/api")

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
