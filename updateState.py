import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials


scope = ['https://spreadsheets.google.com/feeds']

credentials = ServiceAccountCredentials.from_json_keyfile_name('OnlineLevelEditor-ce46bdb7fe28.json', scope)

gc = gspread.authorize(credentials)

wks = gc.open("Maps").sheet1

print(wks.range(1, 1, wks.row_count, 1))