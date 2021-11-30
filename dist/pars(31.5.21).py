import json
import mariadb
import requests
import datetime, time, pytz

conn = mariadb.connect(
    user="xxxxx",
    password="xxxxxxxxxx",
    host="localhost",
    port=3306,
    database="xxxxxxxxxxx")
cur = conn.cursor()

rapidapi_header = {'x-rapidapi-key': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'x-rapidapi-host': 'call-of-duty-modern-warfare.p.rapidapi.com'}
session = requests.Session()
mp = 'mp'
wz = 'wz'
cw = 'cw'
mw = 'mw'
cw = 'cw'

def create_session():
    global session
    session.get('https://profile.callofduty.com/cod/login')
    session.post('https://profile.callofduty.com/do_login?new_SiteId=cod',params={'username': 'your-email', 'password': 'your-password', 'remember_me': 'true', '_csrf': session.cookies['XSRF-TOKEN']})

create_session()

def pars(user, base, game, mode, view):
    exec = base + mode if game == mw else base + game
    cur.execute('SHOW columns FROM ' + exec)
    columns = [i[0] for i in cur.fetchall()]
    def insert(i):
        name = ['user']
        value = [user]
        d = data['data']['matches'][i]
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
            if stats in ['scorePerMinute', 'kdRatio', 'averageSpeedDuringMatch', 'percentTimeMoving']:
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
            elif stats not in columns:
                cur.execute('INSERT INTO {}database (error, time_error) VALUES (?, ?)'.format(base),
                ('[' + stats + '] Column not found for mode [' + mode + '] user [' + user + ']', datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
            else:
                name.append(stats)
                value.append(d['playerStats'][stats])
        cur.execute('INSERT INTO {} ({}) VALUES ({})'.format(exec, ', '.join(name), ', '.join(["'%s'" % i for i in value])))
    def get_data(user, game, mode, view, source):
        user_url = str(user).replace('#', '%23')
        url = ''
        if source == 'RapidApi':
            url_mode = 'warzone' if mode == wz else 'multiplayer'
            url_view = '-matches' if view == 'matches' else ''
            data = requests.get('https://call-of-duty-modern-warfare.p.rapidapi.com/{}{}/{}/battle'.format(url_mode, url_view, user_url), headers=rapidapi_header).json()
            try:
                if view == 'matches':
                    last_id = [data['matches'][i]['matchID'] for i in range(20)]
                    return {'last_id': last_id, 'data': data}
                if view == 'stats':
                    if mode == mp:
                        return {'all_time_stats': json.dumps(data['lifetime']['all']['properties']), 'additional_stats': json.dumps(data['lifetime']['accoladeData']['properties'])}
                    if mode == wz:
                        return {'all_time_stats': json.dumps(data['br_all'])}
            except KeyError:
                cur.execute('INSERT INTO {}database (error, time_error, dumped_json) VALUES (?, ?, ?)'.format(base),
                (', '.join([mode, user, source]), datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), json.dumps(data)))
                get_data(user, game, mode, view, 'CodApi')
        if source == 'CodApi':
            if view == 'matches':
                url = 'https://my.callofduty.com/api/papi-client/crm/cod/v2/title/{}/platform/battle/gamer/{}/matches/{}/start/0/end/0/details'.format(game, user_url, mode)
            if view == 'stats':
                url = 'https://my.callofduty.com/api/papi-client/stats/cod/v1/title/{}/platform/battle/gamer/{}/profile/type/{}'.format(game, user_url, mode)
            res = session.get(url).json()
            data = res['data']
            try:
                if view == 'matches':
                    last_id = [data['matches'][i]['matchID'] for i in range(20)]
                    return {'last_id': last_id, 'data': data}
                if view == 'stats':
                    if mode == mp and game == mw:
                        return {'all_time_stats': json.dumps(data['lifetime']['all']['properties']), 'additional_stats': json.dumps(data['lifetime']['accoladeData']['properties'])}
                    if mode == wz and game == mw:
                        return {'all_time_stats': json.dumps(data['br_all'])}
                    if mode == mp and game == cw:
                        return {'all_time_stats': json.dumps(data['lifetime']['all']['properties'])}
            except KeyError:
                cur.execute('INSERT INTO {}database (error, time_error, dumped_json) VALUES (?, ?, ?)'.format(base),
                (', '.join([mode, user, source]), datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), json.dumps(data)))
                return False
    source = 'CodApi' if game == cw else 'RapidApi'
    data = get_data(user, game, mode, view, source)
    if data:
        mode = game if game == cw else mode
        if view == 'matches':
            cur.execute('SELECT matchID FROM {} WHERE user = "{}" ORDER BY timestamp DESC LIMIT 20'.format(exec, user))
            id_list = [i[0] for i in cur.fetchall()]
            count = 0
            for i in range(19, -1, -1):
                if data['last_id'][i] not in id_list:
                    count += 1
                    insert(i)
            if count > 0:
                cur.execute('UPDATE {0}users SET summary_stats_{1} = (?), records_{1} = (?), time_records_{1} = (?), source_records_{1} = (?) WHERE user = (?)'.format(base, mode),
                (json.dumps(data['data']['summary']['all']), count, datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), source, user))
            cur.execute('UPDATE {0}users SET time_check_{1} = (?) WHERE user = (?)'.format(base, mode), (datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), user))
        if view == 'stats':
            if game == mw and mode == mp:
                cur.execute("UPDATE {0}users SET all_summary_stats_{1} = (?), additional_all_stats_{1} = (?), time_all_summary_stats_{1} = (?) WHERE user = (?)".format(base, mode),
                (data['all_time_stats'], data['additional_stats'], datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), user))
            else:
                cur.execute("UPDATE {0}users SET all_summary_stats_{1} = (?), time_all_summary_stats_{1} = (?) WHERE user = (?)".format(base, mode),
                (data['all_time_stats'], datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), user))
    conn.commit()
    time.sleep(60)


def start_loop(duration):
    while(True):
        for base in ['codstream_', 'cod_']:
            cur.execute('SELECT user, {0}, {1}, {2}, {3}{0}, {3}{1}, {3}{2} FROM {4}users'.format(mp, wz, cw, 'time_all_summary_stats_', base))
            users = cur.fetchall()
            for n in range(len(users)):
                try:
                    cur.execute('UPDATE {}users SET status = (?) WHERE user = (?)'.format(base), (1, users[n][0]))
                    if users[n][1]:
                        if datetime.datetime.now() > users[n][4]+datetime.timedelta(days=7):
                            pars(users[n][0], base, mw, mp, 'stats')
                        pars(users[n][0], base, mw, mp, 'matches')
                    if users[n][2]:
                        if datetime.datetime.now() > users[n][5]+datetime.timedelta(days=7):
                            pars(users[n][0], base, mw, wz, 'stats')
                        pars(users[n][0], base, mw, wz, 'matches')
                    if users[n][3]:
                        if datetime.datetime.now() > users[n][6]+datetime.timedelta(days=7):
                            pars(users[n][0], base, cw, mp, 'stats')
                        pars(users[n][0], base, cw, mp, 'matches')
                    time.sleep(duration)
                    cur.execute('UPDATE {}users SET status = (?) WHERE user = (?)'.format(base), (0, users[n][0]))
                except Exception as e:
                    cur.execute('INSERT INTO {}database (error, time_error) VALUES (?, ?)'.format(base),
                    (str(e), datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
                    conn.commit()
                    time.sleep(duration)
                    continue

start_loop(1000)