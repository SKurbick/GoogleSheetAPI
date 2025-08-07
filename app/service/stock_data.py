import datetime
from pprint import pprint
from typing import List

from app.infrastructure.googlesheet import PCGoogleSheet
from app.models import GoogleSheetParams, StockData
from app.database.repositories import StockDataRepository
from app.models import GoogleSheetParams
from config import settings

class StockDataService:
    def __init__(
            self,
            stock_data_repository: StockDataRepository,
            # gs_connect: PCGoogleSheet
    ):
        self.gs_connect = PCGoogleSheet
        self.stock_data_repository = stock_data_repository

    async def update_stock_data(self, gs_params: GoogleSheetParams):
        stock_data = await self.stock_data_repository.get_all_product_current_balances()
        update_data = {}

        for item in stock_data:
            if item.warehouse_id == 1:
                lvc = item.product_id
                if lvc not in update_data:
                    update_data[lvc] = {}

                update_data[lvc]["Название"] = item.name
                update_data[lvc]["Свободный остаток"] = item.available_quantity
                update_data[lvc]["Физ. остаток"] = item.physical_quantity
                update_data[lvc]["Резерв (ФБС)"] = item.reserved_quantity
                update_data[lvc]["Время последней актуализации"] = str(datetime.datetime.now()).split('.')[0]


        pprint(update_data)
        await self.gs_connect(
            sheet = gs_params.sheet, spreadsheet = gs_params.spreadsheet, creds_json = settings.CREDS
        ).update_revenue_rows(data_json=update_data, table_id=gs_params.table_id_header)