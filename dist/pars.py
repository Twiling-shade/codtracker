import json
import mariadb
import requests, pickle
import datetime, time
import re


base, mw, cw, mp, wz = 'cod_', 'mw', 'cw', 'mp', 'wz'
name_change = {'xpAtEnd': 'totalXp', 'damageDealt': 'damageDone', 'highestStreak': 'longestStreak'}
columns = {
    'meta': ['utcStartSeconds', 'duration', 'matchID', 'map', 'mode', 'result', 'team1Score', 'team2Score', 'playerCount', 'teamCount', 'weaponStats'],
    'round': ['scorePerMinute', 'kdRatio', 'averageSpeedDuringMatch', 'percentTimeMoving', 'ekiadRatio'],
    'time': ['timePlayed', 'timePlayedAlive'],
}

s = requests.Session()
s.headers.update({'user-agent': 'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0'})
s.cookies.update(pickle.load(open('cookie', 'rb'))) #log-in cookie from your browser

conn = mariadb.connect(user='user',password='password',host='localhost',port=3306,database='database')
cur = conn.cursor()

for modes in ['mw_mp', 'mw_wz', 'cw_mp']:
    cur.execute('SHOW columns FROM ' + base + 'tv_matches_' + modes)
    columns[modes] = [i[0] for i in cur.fetchall()]


def pars(target : str, base : str, group : str, game : str, mode : str, view : str, time_now: datetime.datetime):
    game_mode = game + '_' + mode
    path = base + group + '_'
    path_matches = path + view + '_' + game_mode
    path_usermatches = path + 'usermatches_' + re.sub(r'[^\w]', '', target).lower() + '_' + game_mode
    pars_info = ', '.join([target, path_matches])


    def rep(message=None, url=None, res=None):
        cur.execute('INSERT INTO {}database (error, time_error, dumped_json) VALUES (?, ?, ?)'.format(path),
            (pars_info, time_now, json.dumps({'url': url, 'message': message, 'res': res})))
        conn.commit()


    def to_time(value): return datetime.datetime.utcfromtimestamp(value).strftime('%H:%M:%S')


    def fill_list():
        return [{
            'match': insert_match(data['matches'][i]),
            'utcStartSeconds': data['matches'][i]['utcStartSeconds'],
            'matchID':  data['matches'][i]['matchID']
            }
            for i in range(20) if data['matches'][i]['utcStartSeconds'] > LastGame]


    def insert_match(match : list):
        name, value = [], []
        if view == 'matches': name.append('user'), value.append(target)
        for meta_name, meta_value in match.items():
            if meta_name in columns['meta']:
                name.append(meta_name)
                if meta_name == 'utcStartSeconds':
                    value.append(meta_value), name.append('timestamp')
                    value.append(datetime.datetime.fromtimestamp(meta_value))
                elif meta_name == 'duration': value.append(to_time(meta_value/1000))
                elif meta_name == 'weaponStats': value.append(json.dumps(meta_value))
                else: value.append(meta_value)
            elif meta_name == 'player' and game == mw:
                for player_name, player_value in meta_value.items():
                    if player_name in ['username', 'uno', 'clantag', 'loadout']:
                        name.append(player_name)
                        if player_name == 'loadout': value.append(json.dumps(player_value))
                        else: value.append(player_value)
        for stats_name, stats_value in match['playerStats'].items():
            if stats_name in name_change: name.append(name_change[stats_name]), value.append(stats_value)
            elif stats_name in columns['round']: name.append(stats_name), value.append(round(stats_value, 2))
            elif stats_name in columns['time']: name.append(stats_name), value.append(to_time(stats_value))
            elif stats_name == 'accuracy': name.append(stats_name), value.append(round(stats_value * 100, 2))
            elif stats_name == 'teamSurvivalTime': name.append(stats_name), value.append(to_time(stats_value/1000))
            elif stats_name not in columns[game_mode]: rep(stats_name+' '+game_mode+'_'+target)
            else: name.append(stats_name), value.append(stats_value)
        name_str, value_str = ', '.join(name), ', '.join(['%r' % str(i) for i in value])
        return {
            'matches': 'INSERT INTO {} ({}) VALUES ({})'.format(path_matches, name_str, value_str),
            'usermatches': 'INSERT INTO {} ({}) VALUES ({})'.format(path_usermatches, name_str, value_str)
        }


    def get_data(temp_time : int = 0):
        user = target.replace('#', '%23')
        url = 'https://www.callofduty.com/api/papi-client/'
        if view == 'matches':
            url += 'crm/cod/v2/title/{}/platform/battle/gamer/{}/matches/{}/start/0/end/{}000/details?limit=20'.format(game, user, mode, str(temp_time))
        if view == 'fullmatches': url += 'crm/cod/v2/title/{}/platform/battle/fullMatch/{}/{}/it'.format(game, mode, target)
        if view == 'stats': url += 'stats/cod/v1/title/{}/platform/battle/gamer/{}/profile/type/{}'.format(game, user, mode)
        try: res : json = s.get(url).json()
        except:
            rep(message='from try get', url=url)
            time.sleep(1000)
            return
        if res['status'] == 'success':
            time.sleep(20)
            return res['data']
        else:
            rep('no success', url, res)
            if res['data']['message'] == 'Could not load data from datastore; full exception logged as error.': return
            else: exit()


    data = get_data()
    if not data: return

    if view == 'matches':
        cur.execute('SELECT utcStartSeconds FROM {} ORDER BY id DESC LIMIT 1'.format(path_usermatches))
        LastGame : int = cur.fetchall()[0][0]
        insert_list = fill_list()
        if insert_list:
            if len(insert_list) == 20:
                while True:
                    data = get_data(data['matches'][-1]['utcStartSeconds'])
                    insert_list += fill_list()
                    if len(fill_list()) < 20: break
            insert_list.sort(key=lambda x: x['utcStartSeconds'])
            for i in insert_list: cur.execute(i['match']['matches']), cur.execute(i['match']['usermatches'])
            if game == mw:
                cur.execute('SELECT json_id FROM {}list_id WHERE game_mode = (?)'.format(path), (game_mode,))
                list_id : list = json.loads(cur.fetchall()[0][0])
                for i in insert_list:
                    if i['matchID'] not in list_id:
                        pars(i['matchID'], base, group, game, mode, 'fullmatches', time_now)
                        list_id.append(i['matchID'])
                cur.execute('UPDATE {}list_id SET json_id = (?) WHERE game_mode = (?)'.format(path), (json.dumps(list_id), game_mode))
            cur.execute('UPDATE {0}users SET summary_stats_{1} = (?), records_{1} = (?), time_records_{1} = (?) WHERE user = (?)'.format(path, game_mode),
                (json.dumps(data['summary']['all']), len(insert_list), time_now, target))
        cur.execute('UPDATE {0}users SET time_check_{1} = (?) WHERE user = (?)'.format(path, game_mode), (time_now, target))

    if view == 'fullmatches':
        for i in range(len(data['allPlayers'])): cur.execute(insert_match(data['allPlayers'][i])['matches'])

    if view == 'stats':
        all_summary, weekly_summary = json.dumps(data['lifetime']['all']['properties']), json.dumps(data['weekly']['all']['properties'])
        item, scorestreak = json.dumps(data['lifetime']['itemData']), json.dumps(data['lifetime']['scorestreakData'])
        column_name = 'additional_all' if game == mw else 'attachment'
        column_value = json.dumps(data['lifetime']['accoladeData']['properties']) if game == mw else json.dumps(data['lifetime']['attachmentData'])
        cur.execute('UPDATE {0}users SET {1}{7} = (?), {2}{7} = (?), {3}{7} = (?), {4}{7} = (?), {5}{7} = (?), {6}{7} = (?) WHERE user = (?)'.format(
            path, 'all_summary', 'weekly_summary', 'item', 'scorestreak', column_name, 'time_all_summary', '_stats_' + game_mode),
                    (all_summary, weekly_summary, item, scorestreak, column_value, time_now, target))

    conn.commit()


for group in ['group1', 'group2', 'group3']:
    cur.execute('SELECT user, {0}_{2}, {0}_{3}, {1}_{2}, {4}{0}_{2}, {4}{0}_{3}, {4}{1}_{2} FROM {5}users'.format(
        mw, cw, mp, wz, 'time_all_summary_stats_', base + group + '_'))
    users = cur.fetchall()
    for n in range(len(users)):
        time_now = datetime.datetime.utcnow()
        if users[n][1]:
            if time_now > users[n][4]+datetime.timedelta(days=7): pars(users[n][0], base, group, mw, mp, 'stats', time_now)
            pars(users[n][0], base, group, mw, mp, 'matches', time_now)
        if users[n][2]:
            if time_now > users[n][5]+datetime.timedelta(days=7): pars(users[n][0], base, group, mw, wz, 'stats', time_now)
            pars(users[n][0], base, group, mw, wz, 'matches', time_now)
        if users[n][3]:
            if time_now > users[n][6]+datetime.timedelta(days=7): pars(users[n][0], base, group, cw, mp, 'stats', time_now)
            pars(users[n][0], base, group, cw, mp, 'matches', time_now)
