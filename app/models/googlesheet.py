from pydantic import BaseModel


class GoogleSheetParams(BaseModel):
    sheet: str
    spreadsheet: str
    table_id_header: str