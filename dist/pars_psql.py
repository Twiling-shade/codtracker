import json
import psycopg2
import requests, pickle
import datetime, time
import re


base, mw, cw, mp, wz = 'cod_', 'mw', 'cw', 'mp', 'wz'
modes = ['mw_mp', 'mw_wz', 'cw_mp']
name_change = {'xpAtEnd': 'totalXp', 'damageDealt': 'damageDone', 'highestStreak': 'longestStreak'}
columns = {
    'meta': ['utcStartSeconds', 'duration', 'matchID', 'map', 'mode', 'result', 'team1Score', 'team2Score', 'playerCount', 'teamCount', 'weaponStats'],
    'round': ['scorePerMinute', 'kdRatio', 'averageSpeedDuringMatch', 'percentTimeMoving', 'ekiadRatio'],
    'time': ['timePlayed', 'timePlayedAlive'],
    'loadout': ['primaryWeapon', 'secondaryWeapon', 'tactical', 'lethal'],
    'loadout_extra': ['perks', 'extraPerks', 'killstreaks'],
}
insert_matches = {}
groups = ['group1', 'group2']

s = requests.Session()
s.headers.update({'user-agent': 'Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0'})
s.cookies.update(pickle.load(open('cookie', 'rb'))) #log-in cookie from your browser

conn = psycopg2.connect(
    host='localhost',
    database='database',
    user='user',
    password='password')

cur = conn.cursor()

for game_modes in modes:
    cur.execute('SELECT * FROM ' + base + 'group1_matches_' + game_modes + ' LIMIT 0')
    columns[game_modes] = [desc[0] for desc in cur.description]


def pars(target : str, base : str, group : str, game : str, mode : str, view : str, time_now: datetime.datetime):
    game_mode = game + '_' + mode
    path = base + group + '_'
    path_matches = path + view + '_' + game_mode
    path_usermatches = path + 'usermatches_' + re.sub(r'[^\w]', '', target).lower() + '_' + game_mode
    pars_info = ', '.join([target, path_matches])


    def rep(message=None, url=None, res=None):
        cur.execute('INSERT INTO {}logs (error, time_error, dumped_json) VALUES (%s, %s, %s)'.format(base),
            (pars_info, time_now, json.dumps({'url': url, 'message': message, 'res': res})))
        conn.commit()


    def to_time(value): return datetime.datetime.utcfromtimestamp(value).strftime('%H:%M:%S')


    def fill_list() -> list:
        return [{
            'match': insert_match(match),
            'utcStartSeconds': match['utcStartSeconds'],
            'matchID':  match['matchID']
            }
            for match in data['matches'] if match['utcStartSeconds'] > LastGame]


    def insert_match(match : list) -> dict:
        name, value = [], []
        if view == 'matches': name.append('battle_tag'), value.append(target)
        name.append('utc_timestamp')
        value.append(datetime.datetime.utcfromtimestamp(match['utcStartSeconds']))
        for meta_name, meta_value in match.items():
            if meta_name in columns['meta']:
                if meta_name == 'duration': meta_value = to_time(meta_value/1000)
                if meta_name == 'weaponStats': meta_value = json.dumps(meta_value)
                name.append(meta_name), value.append(meta_value)
            if meta_name == 'player' and game == mw:
                for player_name, player_value in meta_value.items():
                    if player_name in ['username', 'uno', 'clantag', 'team', 'loadout']:
                        if player_name == 'clantag' and "'" in player_value:
                            player_value = re.sub("'", "''", player_value)
                        if player_name == 'loadout':
                            for loadout in player_value:
                                for weapon_name, weapon_info in loadout.items():
                                    if weapon_name in columns['loadout']:
                                        if weapon_info['label']: weapon_info['label'] = re.sub("'", "''", weapon_info['label'])
                                    if weapon_name in columns['loadout_extra']:
                                        for extra in weapon_info:
                                            if extra['label']: extra['label'] = re.sub("'", "''", extra['label'])
                            player_value = json.dumps(player_value)
                        name.append(player_name), value.append(player_value)
        for stats_name, stats_value in match['playerStats'].items():
            if stats_name in name_change: stats_name = name_change[stats_name]
            if stats_name in columns['round']: stats_value = round(stats_value, 2)
            elif stats_name == 'accuracy': stats_value = round(stats_value * 100, 2)
            elif isinstance(stats_value, float): stats_value = int(stats_value)
            if stats_name in columns['time']: stats_value = to_time(stats_value)
            if stats_name == 'teamSurvivalTime': stats_value = to_time(stats_value/1000)
            if stats_name not in columns[game_mode]:
                rep(stats_name+' '+game_mode+'_'+target)
                continue
            value.append(stats_value), name.append(stats_name)
        name_str, value_str = ', '.join(['"{}"'.format(i) for i in name]), ', '.join(["'{}'".format(i) for i in value])
        return {
            'matches': 'INSERT INTO {} ({}) VALUES ({})'.format(path_matches, name_str, value_str),
            'usermatches': 'INSERT INTO {} ({}) VALUES ({})'.format(path_usermatches, name_str, value_str)
        }


    def get_data(temp_time : int = 0):
        battle_tag = target.replace('#', '%23')
        url = 'https://www.callofduty.com/api/papi-client/'
        if view == 'matches': url += 'crm/cod/v2/title/{}/platform/battle/gamer/{}/matches/{}/start/0/end/{}000/details?limit=20'.format(
            game, battle_tag, mode, str(temp_time))
        if view == 'fullmatches': url += 'crm/cod/v2/title/{}/platform/battle/fullMatch/{}/{}/it'.format(game, mode, target)
        if view == 'stats': url += 'stats/cod/v1/title/{}/platform/battle/gamer/{}/profile/type/{}'.format(game, battle_tag, mode)

        try: res : json = s.get(url).json()
        except:
            rep(message='from try get', url=url)
            time.sleep(1000)
            return
        if res['status'] == 'success':
            time.sleep(2)
            return res['data']
        else:
            rep('no success', url, res)
            if res['data']['message'] == 'Could not load data from datastore; full exception logged as error.': return
            else: exit()

    data = get_data()
    if not data: return

    if view == 'matches':
        cur.execute('SELECT "utcStartSeconds" FROM {} ORDER BY id DESC LIMIT 1'.format(path_usermatches))
        LastGame = cur.fetchone()
        LastGame : int = 0 if LastGame == None else LastGame[0]
        insert_list = fill_list()

        if insert_list:
            if len(insert_list) == 20 and LastGame:
                while True:
                    data = get_data(data['matches'][-1]['utcStartSeconds'])
                    temp_list = fill_list()
                    insert_list += temp_list
                    if len(temp_list) < 20: break

            insert_list.sort(key=lambda x: x['utcStartSeconds'])
            insert_matches[group][game_mode] += insert_list

            for i in insert_list:
                cur.execute(i['match']['usermatches'])

            user_columns = 'UPDATE {0}users SET summary_stats_{1} = (%s), records_{1} = (%s), time_records_{1} = (%s) WHERE battle_tag = (%s)'.format(
                base, game_mode)
            cur.execute(user_columns, (json.dumps(data['summary']['all']), len(insert_list), time_now, target))
        cur.execute('UPDATE {0}users SET time_check_{1} = (%s) WHERE battle_tag = (%s)'.format(base, game_mode), (time_now, target))

    if view == 'fullmatches':
        for match in data['allPlayers']:
            cur.execute(insert_match(match)['matches'])

    if view == 'stats':
        all_summary, weekly_summary = json.dumps(data['lifetime']['all']['properties']), json.dumps(data['weekly']['all']['properties'])
        item, scorestreak = json.dumps(data['lifetime']['itemData']), json.dumps(data['lifetime']['scorestreakData'])
        column_name = 'additional_all' if game == mw else 'attachment'
        column_value = json.dumps(data['lifetime']['accoladeData']['properties']) if game == mw else json.dumps(data['lifetime']['attachmentData'])
        cur.execute('UPDATE {0}users SET {1}{7} = (%s), {2}{7} = (%s), {3}{7} = (%s), {4}{7} = (%s), {5}{7} = (%s), {6}{7} = (%s) WHERE battle_tag = (%s)'.format(
            base, 'all_summary', 'weekly_summary', 'item', 'scorestreak', column_name, 'time_all_summary', '_stats_' + game_mode),
                    (all_summary, weekly_summary, item, scorestreak, column_value, time_now, target))

    conn.commit()

for group in groups: insert_matches[group] = {i: [] for i in modes}

time_now = datetime.datetime.utcnow()
week = datetime.timedelta(days=7)

cur.execute('SELECT battle_tag, "group", {0}_{2}, {0}_{3}, {1}_{2}, {4}{0}_{2}, {4}{0}_{3}, {4}{1}_{2} FROM {5}users'.format(
    mw, cw, mp, wz, 'time_all_summary_stats_', base))
users = cur.fetchall()

for user in users:
    if user[2]:
        if time_now > user[5].replace(tzinfo=None) + week:
            pars(user[0], base, user[1], mw, mp, 'stats', time_now)
        pars(user[0], base, user[1], mw, mp, 'matches', time_now)
    if user[3]:
        if time_now > user[6].replace(tzinfo=None) + week:
            pars(user[0], base, user[1], mw, wz, 'stats', time_now)
        pars(user[0], base, user[1], mw, wz, 'matches', time_now)
    if user[4]:
        if time_now > user[7].replace(tzinfo=None) + week:
            pars(user[0], base, user[1], cw, mp, 'stats', time_now)
        pars(user[0], base, user[1], cw, mp, 'matches', time_now)


for group in groups:

    for game_modes in modes:
        game = game_modes.split('_')[0]
        mode = game_modes.split('_')[1]
        if game == 'mw':
            cur.execute('SELECT json_id FROM {}list_id WHERE game_mode = (%s)'.format('cod_' + group + '_'), (game_modes,))
            list_id : list = cur.fetchone()[0]

        insert_matches[group][game_modes].sort(key=lambda x: x['utcStartSeconds'])
        new_fullmatch_id = []

        for match in insert_matches[group][game_modes]:
            cur.execute(match['match']['matches'])
            if game == 'mw' and match['matchID'] not in list_id + new_fullmatch_id:
                new_fullmatch_id.append(match['matchID'])
                pars(match['matchID'], base, group, game, mode, 'fullmatches', time_now)

        cur.execute('UPDATE {}list_id SET json_id = (%s) WHERE game_mode = (%s)'.format('cod_' + group + '_'),
        (json.dumps(list_id + new_fullmatch_id), game_modes))

    conn.commit()
