from asyncpg import Pool
from fastapi import Depends
from starlette.requests import Request

from app.service.stock_data import StockDataService
from app.database.repositories.stock_data import StockDataRepository


def get_pool(request: Request) -> Pool:
    """Получение пула соединений из состояния приложения."""
    return request.app.state.pool


def get_stock_data_repository(pool: Pool = Depends(get_pool)) -> StockDataRepository:
    return StockDataRepository(pool)


def get_stock_data_service(repository: StockDataRepository = Depends(get_stock_data_repository)) -> StockDataService:
    return StockDataService(repository)
