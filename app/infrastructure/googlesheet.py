import asyncio
import time
from datetime import datetime

import pandas

import gspread
import requests
from gspread import Client, service_account
import pandas as pd


def column_index_to_letter(index):
    letter = ''
    while index > 0:
        index -= 1
        letter = chr((index % 26) + 65) + letter
        index //= 26
    return letter

def retry_on_quota_exceeded(max_retries=10, delay=60):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except gspread.exceptions.APIError as e:
                    print(f"Error: {e} | time sleep 60 sec [сработал декоратор]")
                    time.sleep(delay)
                    retries += 1
            print("Не удалось выполнить операцию после нескольких попыток.")
            raise Exception("Не удалось выполнить операцию после нескольких попыток.")

        return wrapper

    return decorator


def retry_on_quota_exceeded_async(max_retries=10, delay=60):
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except gspread.exceptions.APIError as e:
                    print(f"Error: {e} | Async sleep {delay} sec [сработал декоратор]")
                    await asyncio.sleep(delay)
                    retries += 1
            print("Не удалось выполнить операцию после нескольких попыток.")
            raise Exception("Не удалось выполнить операцию после нескольких попыток.")

        return async_wrapper

    return decorator


class PCGoogleSheet:
    def __init__(self, spreadsheet: str, sheet: str, creds_json='creds.json'):
        self.creds_json = creds_json
        self.spreadsheet = spreadsheet
        self.client = self.client_init_json()
        self.sheet = self.connect_to_sheet(sheet)

    def client_init_json(self) -> Client:
        """Создание клиента для работы с Google Sheets."""
        return service_account(filename=self.creds_json)

    def connect_to_sheet(self, sheet: str):
        """Попытка подключения к Google Sheets с повторными попытками в случае ошибки."""
        for _ in range(10):
            try:
                spreadsheet = self.client.open(self.spreadsheet)
                return spreadsheet.worksheet(sheet)
            except (gspread.exceptions.APIError, requests.exceptions.ConnectionError) as e:
                print(f"Error: {e} | Время: {datetime.now()} | Time sleep: 60 sec")
                time.sleep(60)
        print("Не удалось подключиться к Google Sheets после 10 попыток.")
        raise Exception("Не удалось подключиться к Google Sheets после 10 попыток.")


    # @retry_on_quota_exceeded_async()
    # async def update_revenue_rows(self, data_json, table_id="Артикул"):
    #     data = self.sheet.get_all_records(expected_headers=[])
    #     df = pd.DataFrame(data)
    #
    #     # Преобразуем данные из словаря в DataFrame
    #     json_df = pd.DataFrame.from_dict(data_json, orient='index')
    #
    #     # Преобразуем все значения в json_df в типы данных, которые могут быть сериализованы в JSON
    #     json_df = json_df.astype(object).where(pd.notnull(json_df), None)
    #
    #     # Обновите данные в основном DataFrame на основе "Артикул"
    #     for index, row in json_df.iterrows():
    #         matching_rows = df[df[table_id] == index].index
    #         for idx in matching_rows:
    #             for column in row.index:
    #                 # if column in df.columns and (pd.isna(df.at[idx, column]) or df.at[idx, column] == ""):
    #                 if column in df.columns:
    #                     df.at[idx, column] = row[column]
    #
    #     # Обновите Google Таблицу только для измененных строк
    #     updates = []
    #     headers = df.columns.tolist()
    #     for index, row in json_df.iterrows():
    #         matching_rows = df[df[table_id] == index].index
    #         for idx in matching_rows:
    #             row_number = idx + 2  # +2 потому что индексация в Google Таблицах начинается с 1, а первая строка - заголовки
    #             for column in row.index:
    #                 if column in headers:
    #                     # +1 потому что индексация в Google Таблицах начинается с 1 строки
    #                     column_index = headers.index(column) + 1
    #                     column_letter = column_index_to_letter(column_index)
    #                     updates.append({'range': f'{column_letter}{row_number}', 'values': [[row[column]]]})
    #     self.sheet.batch_update(updates)
    #     print(f"Актуализированы данные по '{table_id}'")

    @retry_on_quota_exceeded_async()
    async def update_revenue_rows(self, data_json, table_id="Артикул"):
        # Получаем текущие данные из таблицы
        data = self.sheet.get_all_records(expected_headers=[])
        df = pd.DataFrame(data)

        # Преобразуем входные данные
        json_df = pd.DataFrame.from_dict(data_json, orient='index')
        json_df = json_df.astype(object).where(pd.notnull(json_df), None)

        # 1. Добавляем новые артикулы, которых нет в таблице
        existing_articles = set(df[table_id].unique())
        new_articles = [art for art in json_df.index if art not in existing_articles]

        if new_articles:
            # Подготавливаем данные для новых строк
            headers = df.columns.tolist()
            new_rows = []

            for article in new_articles:
                new_row = {col: "" for col in headers}  # Пустая строка
                new_row[table_id] = article  # Устанавливаем артикул

                # Заполняем доступные данные из json_df
                for col in json_df.columns:
                    if col in headers:
                        new_row[col] = json_df.at[article, col]

                new_rows.append([new_row[col] for col in headers])

            # Вставляем новые строки
            self.sheet.append_rows(new_rows)

        # 2. Оригинальный код для обновления существующих данных
        updates = []
        headers = df.columns.tolist()

        for index, row in json_df.iterrows():
            matching_rows = df[df[table_id] == index].index
            for idx in matching_rows:
                row_number = idx + 2
                for column in row.index:
                    if column in headers:
                        column_index = headers.index(column) + 1
                        column_letter = column_index_to_letter(column_index)
                        updates.append({'range': f'{column_letter}{row_number}', 'values': [[row[column]]]})

        if updates:
            self.sheet.batch_update(updates)
