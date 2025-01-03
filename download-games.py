import csv
import requests
import json
# Copied from https://github.com/scummvm/scummvm-web/blob/master/include/DataUtils.php

SHEET_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQamumX0p-DYQa5Umi3RxX-pHM6RZhAj1qvUP0jTmaqutN9FwzyriRSXlO9rq6kR60pGIuPvCDzZL3s/pub?output=tsv';
SHEET_IDS = {
    'platforms': '1061029686',
    'compatibility': '1989596967',
    'games': '1775285192',
    'engines': '0',
    'companies': '226191984',
    'versions': '1225902887',
    'game_demos': '1303420306',
    'series': '1095671818',
    'screenshots': '168506355',
    'scummvm_downloads': '1057392663',
    'game_downloads': '810295288',
    'director_demos': '1256563740',
}
SHEET_DATA = {}
def get_data(sheet):
    if sheet in SHEET_DATA:
        return SHEET_DATA[sheet]
    with requests.Session() as s:
        csv_url = f'{SHEET_URL}&gid={SHEET_IDS[sheet]}'
        download = s.get(csv_url)

        decoded_content = download.content.decode('utf-8')

        reader = csv.DictReader(decoded_content.splitlines(), delimiter='\t')
        
        SHEET_DATA[sheet] = reader
        return reader;

GAMES = {}
PLATFORMS = {}
DOWNLOADS = []
for game in get_data('games'):
    GAMES[game['id']] = game;


for platform in get_data('platforms'):
    PLATFORMS[platform['id']] = platform;


for game_demo in get_data('game_demos'):
    if(game_demo['id'] in GAMES):
        download = game_demo
        download['name'] = GAMES[game_demo['id']]['name']
        if(download['category'] == ""):
            download['category'] = PLATFORMS[game_demo['platform']]['name'] + " Demo"
        DOWNLOADS.append(download)

for director_demo in get_data('director_demos'):
    if(director_demo['id'] in GAMES):
        download = {}
        download['id'] = director_demo['id']
        download['platform'] = director_demo['platform']
        download['language'] = director_demo['lang']
        download['name'] = director_demo['title']
        download['url'] = director_demo['url']
        download['category'] = PLATFORMS[director_demo['platform']]['name'] + " Demo"
        DOWNLOADS.append(download)

for game in get_data('game_downloads'):
    if game['game_id'] in GAMES and game['category'] == "games" and "version" in game['name'].lower():
        download = {}
        download['id'] = game['game_id']
        download['platform'] = ""
        download['language'] = ""
        download['name'] = GAMES[game['game_id']]['name']
        download['url'] = "/frs/extras/"+ game['url']
        download['category'] = game['name']
        DOWNLOADS.append(download)

print(json.dumps(DOWNLOADS, indent=4))

f = open("file_list.txt", "w")
for demo in DOWNLOADS:
    f.write("https://downloads.scummvm.org"+demo['url'] + "\n")
f.close()
#wget --content-disposition --trust-server-names -N -c -x -nH -i file_list.txt