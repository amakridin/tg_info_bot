import gspread

from get_config import get_key_config


class GoogleSheetsApi:
    def __init__(self):
        self.client = gspread.service_account(
            filename=get_key_config("SERVICE_ACCOUNT_CREDENTIALS")
        )

    def get_data_by_sheet_url(self, sheet_url: str, sheet_name: str):
        sheets = self.client.open_by_url(sheet_url)
        return sheets.worksheet(sheet_name).get_all_records()

    def get_file(self, file_id: str):
        self.client.get_file_drive_metadata(file_id)


# while True:
#     get_data_by_sheet_url(
#         "https://docs.google.com/spreadsheets/d/1rf4_S1gfFy5uAZpUgHYQm2Ko-3tzdoRZTIR8E2BFgu8",
#         "Экспозиция",
#     )
#     sleep(20)
