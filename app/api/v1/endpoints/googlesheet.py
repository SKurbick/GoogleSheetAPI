from typing import List
from fastapi import APIRouter, Depends, status, Body, HTTPException, Query


router = APIRouter(prefix="/googlesheet", tags=["Работа с гугл таблицей"])


@router.get("/add_new_price")
async def add_new_price(
):
    print("OK")

