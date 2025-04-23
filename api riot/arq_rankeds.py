import requests
import json
import time
import pandas as pd
import numpy as np
#import seaborn
import datetime
import csv
# descobri que a data inicial do timestamp é 1/1/1970 e que na api da riot essa é a data inicial contada em segundos. mas
# nos dados da api o tempo é contado em milisegundos.

with open("C:\\Users\\matht\\Downloads\\dragontail-15.2.1\\15.2.1\\data\\pt_BR\\item.json", 'r', encoding="utf8") as file:
    itens = json.load(file)

API_KEY = 'RGAPI-be4e145c-4a42-4ef4-8a78-e3cfc534eb29'

def enforce_rate_limit():
    global initial_time1
    global initial_time2
    global n_calls
    duration_execution1 = time.time() - initial_time1
    duration_execution2 = time.time() - initial_time2
    n_calls += 1
    if n_calls%100 == 99:
        if duration_execution2 < 120:
            time.sleep(121 - duration_execution2)
        initial_time2 = time.time()
    if n_calls%20 == 19:
        if duration_execution1 < 1:
            time.sleep(1.1 - duration_execution1)
        initial_time1 = time.time()

def puuid_api(SUMMONER_NAME, TAG_NAME):
    PUUID_URL = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{SUMMONER_NAME}/{TAG_NAME}?api_key={API_KEY}"
    enforce_rate_limit()
    result = requests.get(PUUID_URL)
    if result.status_code == 200:
        return result.json()['puuid']
    elif result.status_code == 429:
        time.sleep(1)
        puuid_api(SUMMONER_NAME, TAG_NAME)
    else:
        print('VERIFIQUE O API KEY')

def list_matchid_api(puuid, starttime=1736218800, endtime=1736218800 + 60*60*24*30):
    LIST_MATCHID_URL = (
        f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue=420&count=100&startTime={starttime}&endTime"
        f"={endtime}&api_key={API_KEY}")
    enforce_rate_limit()
    result = requests.get(LIST_MATCHID_URL)
    if result.status_code == 200:
        if result.json() == None:
            print(puuid)
        return result.json()
    elif result.status_code == 429:
        time.sleep(1)
        list_matchid_api(puuid, starttime, endtime)
    else:
        print('VERIFIQUE O API KEY')

def stats_game_api(match_id):
    MATCHID_URL = f"https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={API_KEY}"
    enforce_rate_limit()
    result = requests.get(MATCHID_URL)
    if result.status_code == 200:
        return result.json()
    elif result.status_code == 429:
        time.sleep(1)
        stats_game_api(match_id)
    else:
        print('VERIFIQUE O API KEY')

def get_list_matchid(intervals, puuid):
    starttime = 1736218800
    endtime = starttime + 60*60*24*intervals
    finallistmatchid = []
    while True:
        listmatchid = list_matchid_api(puuid, starttime, endtime)
        try:
            len(listmatchid)
        except:
            print(puuid)
        if len(listmatchid) == 0:
            break
        if len(listmatchid) < 100:
            finallistmatchid += listmatchid
            starttime = endtime
            endtime = starttime + 60*60*24*intervals
        else:
            intervals = intervals//2 if intervals > 2 else 1
            endtime = starttime + 60*60*24*intervals
    resultado = []
    matchid_games_saved = pd.read_csv('data_rankeds.csv', index_col=0)['matchid'].values.tolist()
    for i in range(len(finallistmatchid)):
        if finallistmatchid[i] not in matchid_games_saved:
            resultado.append(finallistmatchid[i])
    return resultado

# recebe uma lista de matchid e salva no arquivo api_result.csv
# se o arquivo não existir, ele cria o arquivo e salva os matchid
def save_api_result(listmatchid):
    matchid_in_arq = []
    try:
        with open('api_result.csv', 'r', encoding="utf-8") as myfile:
            reader = csv.reader(myfile)
            for row in reader:
                matchid_in_arq.append(row[0])
    except FileNotFoundError:
        pass
    api_result = [[match_id, stats_game_api(match_id)] for match_id in listmatchid if match_id not in matchid_in_arq]
    # w substitui o arquivo, a cada vez que o programa roda. para não perder os dados, use o a
    with open('api_result.csv', 'a', newline='\n', encoding="utf-8") as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for line in api_result:
            if line[1] != "":
                wr.writerow(line)

def load_stats_game(match_id):
    try:
        with open('api_result.csv', 'r', encoding="utf-8") as myfile:
            reader = csv.reader(myfile)
            for row in reader:
                if row[0] == match_id:
                    return eval(row[1])
    except FileNotFoundError:
        save_api_result([match_id])
        return load_stats_game(match_id)

def get_game_stats(match_id, puuid):
    temp = load_stats_game(match_id)
    if temp == None:
        save_api_result([match_id])
        temp = load_stats_game(match_id)
    for i,j in enumerate([p == puuid for p in temp['metadata']['participants']]):
        if j:
            part_position = i
    part1 = temp['info']['participants'][part_position]
    if part_position < 5:
        enemychampionname1 = temp['info']['participants'][5]['championName']
        enemychampionname2 = temp['info']['participants'][6]['championName']
        enemychampionname3 = temp['info']['participants'][7]['championName']
        enemychampionname4 = temp['info']['participants'][8]['championName']
        enemychampionname5 = temp['info']['participants'][9]['championName']
    else:
        enemychampionname1 = temp['info']['participants'][0]['championName']
        enemychampionname2 = temp['info']['participants'][1]['championName']
        enemychampionname3 = temp['info']['participants'][2]['championName']
        enemychampionname4 = temp['info']['participants'][3]['championName']
        enemychampionname5 = temp['info']['participants'][4]['championName']
    duration = temp['info']['gameDuration']/60
    killspermin = part1['kills']/duration
    deathspermin = part1['deaths']/duration
    assistspermin = part1['assists']/duration
    goldpermin = part1['goldEarned']/duration
    damagetochampionpermin = part1['totalDamageDealtToChampions']/duration
    healpermin = part1['totalHeal']/duration
    shieldonteammatespermin = part1['totalDamageShieldedOnTeammates']/duration
    damagetakenpermin = part1['totalDamageTaken']/duration
    wardspermin = part1['wardsPlaced']/duration
    detectorwardspermin = part1['detectorWardsPlaced']/duration
    item0 = itens['data'][str(part1['item0'])]['name'] if part1['item0'] != 0 else 'vazio'
    item1 = itens['data'][str(part1['item1'])]['name'] if part1['item1'] != 0 else 'vazio'
    item2 = itens['data'][str(part1['item2'])]['name'] if part1['item2'] != 0 else 'vazio'
    item3 = itens['data'][str(part1['item3'])]['name'] if part1['item3'] != 0 else 'vazio'
    item4 = itens['data'][str(part1['item4'])]['name'] if part1['item4'] != 0 else 'vazio'
    item5 = itens['data'][str(part1['item5'])]['name'] if part1['item5'] != 0 else 'vazio'
    item6 = itens['data'][str(part1['item6'])]['name'] if part1['item6'] != 0 else 'vazio'
    return [temp['metadata']['matchId'], part1['championName'], enemychampionname1, enemychampionname2, enemychampionname3,
            enemychampionname4, enemychampionname5, duration, killspermin,
            deathspermin, assistspermin, goldpermin, item0, item1, item2, item3, item4, item5,
            item6, damagetochampionpermin, healpermin, shieldonteammatespermin, damagetakenpermin,
            wardspermin, detectorwardspermin, part1['individualPosition'],
            part1['dragonKills'], part1['baronKills'], part1['win']]

def save_games(list_games, file='data_rankeds.csv'):
    db_data_rankeds = pd.read_csv('data_rankeds.csv', index_col=0)
    games_saved = db_data_rankeds.values.tolist()
    matchid_games_saved = db_data_rankeds['matchid'].values.tolist()
    for i in range(len(list_games)):
        if list_games[i][0] not in matchid_games_saved:
            games_saved.append(list_games[i])
    list_columns = ['matchid', 'champion_name', 'enemychampion1', 'enemychampion2', 'enemychampion3', 'enemychampion4', 'enemychampion5',
                    'duration', 'kills', 'deaths', 'assists', 'gold', 'item0', 'item1', 'item2', 'item3',
                    'item4', 'item5', 'item6', 'damage', 'heal', 'shield', 'damage_taken',
                    'wards', 'pinks', 'position', 'dragon', 'baron', 'win']
    all_games = pd.DataFrame(games_saved, columns = list_columns)
    all_games.to_csv(file)

def update_games(list_players):
    initial_time = time.time()
    try:
        pd.read_csv('data_rankeds.csv', index_col=0).values.tolist()
    except FileNotFoundError:
        game = get_game_stats('BR1_3084034795', 'BB9uaojRqbErbU1z5q0UHwbqY97YyIZzOMnGkzZBozIzWwTuRu3l2AEHDzgpVNJN8SWYdSliY7TcOw')
        list_columns = ['matchid', 'champion_name', 'enemychampion1', 'enemychampion2', 'enemychampion3', 'enemychampion4', 'enemychampion5',
                        'duration', 'kills', 'deaths', 'assists', 'gold', 'item0', 'item1', 'item2', 'item3',
                        'item4', 'item5', 'item6', 'damage', 'heal', 'shield', 'damage_taken',
                        'wards', 'pinks', 'position', 'dragon', 'baron', 'win']
        all_games = pd.DataFrame([game], columns = list_columns)
        all_games.to_csv('data_rankeds.csv')
    for player in list_players:
        SUMMONER_NAME = player[0]
        TAG_NAME = player[1]
        puuid = puuid_api(SUMMONER_NAME, TAG_NAME)
        listmatchid = get_list_matchid(60, puuid)
        list_games = [get_game_stats(match, puuid) for match in listmatchid]
        save_api_result(listmatchid)
        save_games(list_games)
    print('Tempo total de execução:', np.round(time.time() - initial_time, 2))


list_players = [['Lóvely', 'Ágata'] , ['Nina', '244'], ['banheta é bom', 'GOZA'], ['Sir Leucopênico', 'HPGAP'],
                ['Changli', 'sona'], ['clancy', 'copy'], ['heavymetalheart', 'mabi'], ['folklore', 'sona']]

initial_time1 = time.time()
initial_time2 = time.time()
n_calls = 0
update_games(list_players)