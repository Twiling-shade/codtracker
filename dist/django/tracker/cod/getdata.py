import json
import mariadb
import time
import requests
import datetime
import pytz

rapidapi_header = {'x-rapidapi-key': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'x-rapidapi-host': 'call-of-duty-modern-warfare.p.rapidapi.com'}
mp = 'mp'
wz = 'wz'
cw = 'cw'

conn = mariadb.connect(
    user="xxxxx",
    password="xxxxxxxxxx",
    host="localhost",
    port=3306,
    database="xxxxxxxxxxx")
cur = conn.cursor()

def get_CodApi_data(url):
    session = requests.Session()
    session.get('https://profile.callofduty.com/cod/login')
    session.post('https://profile.callofduty.com/do_login?new_SiteId=cod',
    params={'username': 'your-email', 'password': 'your-password', 'remember_me': 'true', '_csrf': session.cookies['XSRF-TOKEN']})
    data = session.get(url).json()
    return data['data']

def pars(user, base, mode):
    cur.execute('SHOW columns FROM '+ base + mode)
    columns = [i[0] for i in cur.fetchall()]
    def insert(i):
        name = []
        value = []
        name.append('user')
        value.append(user)
        d = data['matches'][i]
        for meta in d:
            if meta in ['matchID', 'map', 'mode', 'result', 'team1Score', 'team2Score', 'playerCount', 'teamCount']:
                name.append(meta)
                value.append(d[meta])
            elif meta == 'player' and mode != cw:
                for player in d[meta]:
                    if player in ['username', 'uno', 'clantag']:
                        name.append(player)
                        value.append(d[meta][player])
                    elif player == 'loadout':
                        name.append(player)
                        value.append(json.dumps(d[meta][player]))
            elif meta == 'utcStartSeconds':
                name.append('timestamp')
                value.append(datetime.datetime.fromtimestamp(d['utcStartSeconds'], pytz.timezone('Europe/Moscow')).strftime('%Y-%m-%d %H:%M:%S'))
            elif meta == 'duration':
                name.append(meta)
                value.append(datetime.datetime.utcfromtimestamp(d[meta]/1000.0).strftime('%H:%M:%S'))
            elif meta == 'weaponStats':
                name.append(meta)
                value.append(json.dumps(d[meta]))
        for stats in d['playerStats']:
            if stats not in columns:
                cur.execute('INSERT INTO {}database (error, time_error) VALUES (?, ?)'.format(base),
                ('[' + stats + '] Column not found for mode [' + mode + '] user [' + user + ']', datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
            elif stats in ['scorePerMinute', 'kdRatio', 'averageSpeedDuringMatch', 'percentTimeMoving']:
                name.append(stats)
                value.append(round(d['playerStats'][stats], 2))
            elif stats == 'accuracy':
                name.append(stats)
                value.append(round(d['playerStats'][stats] * 100, 2))
            elif stats == 'teamSurvivalTime':
                name.append(stats)
                value.append(datetime.datetime.utcfromtimestamp(d['playerStats'][stats]/1000.0).strftime('%H:%M:%S'))
            elif stats == 'timePlayed' or stats == 'timePlayedAlive':
                name.append(stats)
                value.append(datetime.datetime.utcfromtimestamp(d['playerStats'][stats]).strftime('%H:%M:%S'))
            else:
                name.append(stats)
                value.append(d['playerStats'][stats])
        cur.execute('INSERT INTO {} ({}) VALUES ({})'.format(base + mode, ', '.join(name), ', '.join(["'%s'" % i for i in value])))
    user_url = str(user).replace('#', '%23')
    cur.execute('SELECT matchID FROM {} WHERE user = "{}" ORDER BY timestamp DESC LIMIT 20'.format(base + mode, user))
    id_list = [i[0] for i in cur.fetchall()]
    if mode == mp:
        data = requests.get('https://call-of-duty-modern-warfare.p.rapidapi.com/multiplayer-matches/' + user_url + '/battle', headers=rapidapi_header).json()
        source = 'RapidApi'
    if mode == wz:
        data = requests.get('https://call-of-duty-modern-warfare.p.rapidapi.com/warzone-matches/' + user_url + '/battle', headers=rapidapi_header).json()
        source = 'RapidApi'
    if mode == cw:
        data = get_CodApi_data('https://my.callofduty.com/api/papi-client/crm/cod/v2/title/cw/platform/battle/gamer/' + user_url + '/matches/mp/start/0/end/0/details')
        source = 'CodApi'
    try:
        last_id = [data['matches'][i]['matchID'] for i in range(20)]
    except KeyError:
        cur.execute('INSERT INTO {}database (error, time_error, dumped_json) VALUES (?, ?, ?)'.format(base),
        (', '.join([mode, user, source]), datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), json.dumps(data)))
        data = get_CodApi_data('https://my.callofduty.com/api/papi-client/crm/cod/v2/title/mw/platform/battle/gamer/' + user_url + '/matches/' + mode +'/start/0/end/0/details')
        source = 'CodApi'
        last_id = [data['matches'][i]['matchID'] for i in range(20)]
        if mode == cw:
            last_id = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    count = 0
    for i in range(19, -1, -1):
        if last_id[i] not in id_list and last_id[i] != 0:
            count += 1
            insert(i)
    if count > 0:
        cur.execute('UPDATE {0}users SET summary_stats_{1} = (?), records_{1} = (?), time_records_{1} = (?), source_records_{1} = (?) WHERE user = (?)'.format(base, mode),
        (json.dumps(data['summary']['all']), count, datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), source, user))
    cur.execute('UPDATE {0}users SET time_check_{1} = (?) WHERE user = (?)'.format(base, mode), (datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), user))
    conn.commit()

def pars_stats(user, base, mode):
    user_url = str(user).replace("#", "%23")
    if mode == mp:
        data = requests.get('https://call-of-duty-modern-warfare.p.rapidapi.com/multiplayer/' + user_url + '/battle', headers=rapidapi_header).json()
        cur.execute("UPDATE {0}users SET all_summary_stats_{1} = (?), additional_all_stats_{1} = (?), time_all_summary_stats_{1} = (?) WHERE user = (?)".format(base, mode),
        (json.dumps(data['lifetime']['all']['properties']), json.dumps(data['lifetime']['accoladeData']['properties']), datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), user))
    if mode == wz:
        data = requests.get('https://call-of-duty-modern-warfare.p.rapidapi.com/warzone/' + user_url + '/battle', headers=rapidapi_header).json()
        cur.execute("UPDATE {0}users SET all_summary_stats_{1} = (?), time_all_summary_stats_{1} = (?) WHERE user = (?)".format(base, mode),
        (json.dumps(data['br_all']), datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), user))
    if mode == cw:
        data = get_CodApi_data('https://my.callofduty.com/api/papi-client/stats/cod/v1/title/cw/platform/battle/gamer/' + user_url + '/profile/type/mp')
        cur.execute("UPDATE {0}users SET all_summary_stats_{1} = (?), time_all_summary_stats_{1} = (?) WHERE user = (?)".format(base, mode),
        (json.dumps(data['lifetime']['all']['properties']), datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), user))
    conn.commit()
