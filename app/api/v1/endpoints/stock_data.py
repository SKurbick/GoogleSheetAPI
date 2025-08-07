
from typing import List
from fastapi import APIRouter, Depends, status, Body, HTTPException, Query

from app.models import StockData, GoogleSheetParams
from app.service import StockDataService
from app.dependencies import get_stock_data_service
router = APIRouter(prefix="/googlesheet", tags=["Склад и остатки"])





@router.post("/update_stock_data")
async def update_stock_data(
        data: GoogleSheetParams,
        service: StockDataService = Depends(get_stock_data_service)
):
    await service.update_stock_data(data)
    return {"status":200, "message": "Успешно"}