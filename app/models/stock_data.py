from pydantic import BaseModel


class StockData(BaseModel):
    product_id: str
    warehouse_id: int
    reserved_quantity: int
    physical_quantity: int
    available_quantity: int
