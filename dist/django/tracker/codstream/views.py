from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
import json
import requests
import datetime
import pandas as pd
import time
import mariadb
import datetime
import pytz

from .getdata import pars, pars_stats

from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import *

from .models import *
from .forms import RegUser

class api(APIView):
    def get(self, request, mode, view, many, user, order):
        error = ''
        modes = ['wz', 'mp', 'cw']
        views = ['table', 'raw', 'stats']
        orders_wz = ['id', 'timestamp', 'kills', 'wallBangs', 'totalXp', 'headshots', 'assists', 'scorePerMinute', 'deaths', 'distanceTraveled',
        'kdRatio', 'objectiveShieldDamage', 'timePlayed', 'executions', 'nearmisses', 'percentTimeMoving', 'longestStreak',
        'damageDone', 'damageTaken', 'playerCount', 'teamCount', 'challengeXp', 'teamSurvivalTime', 'gulagDeaths', 'gulagKills',
        'teamPlacement', 'objectiveTrophyDefense', 'objectiveMedalScoreSsKillTomaStrike', 'objectiveMedalScoreKillSsHoverJet',
        'objectiveMedalModeXAssaultScore', 'objectiveMedalModeDomSecureAssistScore', 'objectivePlunderCashBloodMoney',
        'objectiveTeamWiped', 'objectiveLastStandKill', 'objectiveBrC130BoxOpen', 'objectiveBrMissionPickupTablet',
        'objectiveReviver', 'objectiveBrKioskBuy', 'objectiveBrCacheOpen', 'objectiveMunitionsBoxTeammateUsed',
        'objectiveDestroyedEquipment', 'objectiveBrDownEnemyCircle1', 'objectiveBrDownEnemyCircle2', 'objectiveBrDownEnemyCircle3',
        'objectiveBrDownEnemyCircle4', 'objectiveBrDownEnemyCircle5', 'objectiveMedalScoreSsKillPrecisionAirstrike',
        'objectiveAssistDecoy', 'objectiveBrDownEnemyCircle6', 'objectiveMedalScoreKillSsRadarDrone', 'objectiveDestroyedVehicleHeavy',
        'objectiveDestroyedVehicleLight', 'objectiveDestroyedVehicleMedium']
        orders_mp = ['id', 'timestamp', 'kills', 'wallBangs', 'totalXp', 'headshots', 'assists', 'scorePerMinute', 'deaths', 'distanceTraveled',
        'kdRatio', 'timePlayed', 'executions', 'nearmisses', 'percentTimeMoving', 'longestStreak', 'damageDone', 'damageTaken',
        'averageSpeedDuringMatch', 'accuracy', 'shotsLanded', 'shotsMissed', 'suicides', 'shotsFired',
        'objectiveMedalScoreSsKillPrecisionAirstrike', 'objectiveMedalScoreSsKillChopperSupport', 'objectiveMedalScoreSsKillHoverJet',
        'objectiveMedalScoreSsKillTomaStrike', 'objectiveMedalModeHpSecureScore', 'objectiveCaptureKill', 'objectiveMedalScoreKillSsPacSentry',
        'objectiveUavAssist', 'objectiveKcFriendlyPickup', 'objectiveMedalModeDomSecureNeutralScore', 'objectiveKillDenied',
        'objectiveMunitionsBoxTeammateUsed', 'objectiveMedalModeDomSecureAssistScore', 'objectiveMedalModeXDefendScore',
        'objectiveObjProgDefend', 'objectiveMegaBank', 'objectiveTagCollected', 'objectiveGrindFriendlyPickup', 'objectiveTagScore',
        'objectiveMedalModeKcOwnTagsScore', 'objectiveDestroyedEquipment', 'objectiveKothInObj', 'objectiveMedalModeDomSecureScore',
        'objectiveMedalModeXAssaultScore', 'objectiveShieldAssist', 'objectiveHack', 'objectiveMedalScoreKillSsUav',
        'objectiveMedalScoreKillSsHoverJet', 'objectiveShieldDamage', 'objectiveKillConfirmed', 'objectiveExecution',
        'objectiveMedalModeDomSecureBScore', 'objectiveMedalScoreKillSsFuelAirstrike', 'objectiveMedalScoreKillSsRadarDrone',
        'objectiveMedalScoreKillSsScramblerDrone', 'objectiveScrapAssist']
        orders_cw = ['id', 'timestamp', 'kills', 'xpAtEnd', 'ekiadRatio', 'accuracy', 'shotsLanded', 'highestMultikill', 'ekia', 'headshots', 'assists',
        'scorePerMinute', 'deaths', 'damageDealt', 'kdRatio', 'shotsMissed', 'multikills', 'highestStreak', 'hits', 'timePlayed', 'suicides',
        'timePlayedAlive', 'objectives', 'shots', 'shotsFired']
        if mode not in modes:
            error = 'modes available: ' + str(modes)
        if view not in views:
            error = 'views available: ' + str(views)
        if mode == 'wz' and str(order).strip('-') not in orders_wz:
            error = 'for mode [' + mode + '] orders available: ' + str(orders_wz)
        if mode == 'mp' and str(order).strip('-') not in orders_mp:
            error = 'for mode [' + mode + '] orders available: ' + str(orders_mp)
        if mode == 'cw' and str(order).strip('-') not in orders_cw:
            error = 'for mode [' + mode + '] orders available: ' + str(orders_cw)
        if many == 'all':
            many = 10000
        else:
            try:
                many = int(many)
            except:
                error = 'need a number(int) how many need rows or use /all/'
        if error != '':
            debug = {
                'error': error,
                'mode': mode,
                'view': view,
                'many': many,
                'user': user
            }
            return JsonResponse(debug)
        if user == 'all':
            table = eval(mode).objects.order_by(order)[:+many]
        else:
            table = eval(mode).objects.filter(user=user).order_by(order)[:+many]
        serializer = globals()[mode+'Serializer'](table, many=True)
        if view == 'stats':
            table = users.objects.order_by(order).filter(user=user)
            data = [m.stats(mode) for m in table]
            response = {'data': data}
        if view == 'table':
            data = [m.dict_json() for m in table]
            response = {'data': data}
        if view == 'raw':
            response = {'data': serializer.data}
        return JsonResponse(response)

def chart(request, duration):
    def sort(dict):
        games = []
        for i in general_list_dates[mode]['dates']:
           if i in dict:
              games.append(dates_count[i])
           else:
              games.append(0)
        return games
    general_list_dates = {
        'wz': {
            'players': {}
        },
        'mp': {
            'players': {}
        },
        'cw': {
            'players': {}
        }
    }
    for mode in ['wz', 'mp', 'cw']:
        username = 'username'
        if mode == 'cw':
            username = 'user'
        if duration == 'week':
            raw_data = eval(mode).objects.filter(timestamp__range=(datetime.datetime.now(tz=timezone.utc) - datetime.timedelta(days=6), datetime.datetime.now(tz=timezone.utc))).values_list('timestamp', username)
            general_list_dates[mode]['dates'] = sorted(set([i[0].strftime('%Y-%m-%d') + '\n' + pd.to_datetime(i[0]).day_name() for i in raw_data]))
            for user in set([i[1] for i in raw_data]):
                user_dates = [c[0].strftime('%Y-%m-%d') + '\n' + pd.to_datetime(c[0]).day_name() if c[1] == user else 0 for c in raw_data]
                dates_count = {i:user_dates.count(i) for i in user_dates}
                general_list_dates[mode]['players'][str(user).split("#", 1)[0]] = sort(dates_count)
        if duration == 'lifetime':
            raw_data = eval(mode).objects.values_list('timestamp', username)
            general_list_dates[mode]['dates'] = sorted(set([i[0].strftime('%Y-%m-%d') for i in raw_data]))
            for user in set([i[1] for i in raw_data]):
                user_dates = [c[0].strftime('%Y-%m-%d') if c[1] == user else 0 for c in raw_data]
                dates_count = {i:user_dates.count(i) for i in user_dates}
                general_list_dates[mode]['players'][str(user).split("#", 1)[0]] = sort(dates_count)
    return JsonResponse(general_list_dates)

def tracker(request):
    info = ''
    Username = ''
    if request.method == 'POST':
        form = RegUser(request.POST)
        if form.is_valid():
            userlist = [i['user'] for i in users.objects.values('user')]
            usern = form.cleaned_data['user']
            mp = form.cleaned_data['mp']
            wz = form.cleaned_data['wz']
            cw = form.cleaned_data['cw']
            base = 'codstream_'
            mp = 'mp'
            wz = 'wz'
            cw = 'cw'
            if usern not in userlist:
                try:
                    conn = mariadb.connect(
                        user="xxxxx",
                        password="xxxxxxxxxx",
                        host="localhost",
                        port=3306,
                        database="xxxxxxxxxxx")
                    cur = conn.cursor()
                    url = 'https://call-of-duty-modern-warfare.p.rapidapi.com/multiplayer-matches/' + str(usern).replace("#", "%23") +'/battle'
                    data = requests.get(url, headers={'x-rapidapi-key': "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", 'x-rapidapi-host': "call-of-duty-modern-warfare.p.rapidapi.com"}).json()
                    Username = data['matches'][0]['player']['username']
                    Uno = data['matches'][0]['player']['uno']
                    try:
                        Clantag = data['matches'][0]['player']['clantag']
                    except:
                        Clantag = None
                    form.save()
                    users.objects.filter(user=usern).update(username=Username)
                    users.objects.filter(user=usern).update(uno=Uno)
                    users.objects.filter(user=usern).update(clantag=Clantag)
                    time.sleep(1)
                    pars(usern, base, mp)
                    time.sleep(1)
                    pars_stats(usern, base, mp)
                    time.sleep(1)
                    pars(usern, base, wz)
                    time.sleep(1)
                    pars_stats(usern, base, wz)
                    if cw == 1:
                        pars(usern, base, cw)
                        time.sleep(1)
                        pars_stats(usern, base, cw)
                    conn.close()
                    info = Username + ' successfully registered.'
                except KeyError:
                    info = usern + ' Not found'
            elif usern in userlist:
                users.objects.filter(user=usern).update(mp=mp)
                users.objects.filter(user=usern).update(wz=wz)
                users.objects.filter(user=usern).update(cw=cw)
                info = 'Games for user ' + usern + ' has been updated.'
        else:
            info = 'Form not valid'

    form = RegUser()
    context = {
        'title': 'Tracker',
        'users': users.objects.all(),
        'form': form,
        'info': info,
    }
    return render(request, "Tracker.html", context=context)

def index(request):
    context = {
        'title': 'Main page',
    }
    return render(request, "index.html", context=context)