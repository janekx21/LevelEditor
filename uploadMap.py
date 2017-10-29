import sys
if len(sys.argv) <= 1:
	print("Not a path")
	print(sys.argv)
	sys.exit()

import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials


scope = ['https://spreadsheets.google.com/feeds']

credentials = ServiceAccountCredentials.from_json_keyfile_name('OnlineLevelEditor-ce46bdb7fe28.json', scope)

gc = gspread.authorize(credentials)

wks = gc.open("Maps").sheet1

st = ""
with open(sys.argv[1],"r") as f:
	st = f.read() 
print(st)
js = json.loads(st)

lis = [js["name"],"Sterne","non","non","non","non","non",st]

wks.append_row(lis)
