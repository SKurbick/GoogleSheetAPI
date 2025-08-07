import json
from pprint import pprint
from typing import List, Tuple

import asyncpg
from asyncpg import Pool, UniqueViolationError
from app.models import  StockData


class StockDataRepository:
    def __init__(self, pool: Pool):
        self.pool = pool

    async def get_all_product_current_balances(self) -> List[StockData]:
        select_query = """
        SELECT * FROM current_balances;
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetch(select_query)
        pprint(result)
        return [StockData(**res) for res in result]