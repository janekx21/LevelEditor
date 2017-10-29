import gspread
from oauth2client.service_account import ServiceAccountCredentials


scope = ['https://spreadsheets.google.com/feeds']

credentials = ServiceAccountCredentials.from_json_keyfile_name('OnlineLevelEditor-ce46bdb7fe28.json', scope)

gc = gspread.authorize(credentials)

wks = gc.open("Maps").sheet1

blocks= []

str = ""

for x in range(10000):
	str+="x"
wks.update_acell('A1', "Level Name")
wks.update_acell('B1', "Sterne")
wks.update_acell('C1', "non")
wks.update_acell('D1', "non")
wks.update_acell('E1', "non")
wks.update_acell('F1', "non")
wks.update_acell('G1', "non")
wks.update_acell('H1', str)