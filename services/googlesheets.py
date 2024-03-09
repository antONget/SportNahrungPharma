import gspread
import logging


gp = gspread.service_account(filename='services/test.json')

#Open Google spreadsheet
gsheet = gp.open('SportNahrungPharma')



# select worksheet
start_sheet = gsheet.worksheet("/start")
order_sheet = gsheet.worksheet("Заявка на консультацию")


# добавить значения
def append_user(telegram_id, username, date_user):
    logging.info(f'append_user')
    start_sheet.append_row([telegram_id, username, date_user])


def append_client(id_telegram, user_name, name, phone, info):
    logging.info(f'append_user')
    order_sheet.append_row([id_telegram, user_name, name, phone, info])
