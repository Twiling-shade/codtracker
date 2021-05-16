from django.db import models
# import pytz

def sep(number): 
    return ("{:,}".format(number))

class database(models.Model):
    error = models.TextField(null=True)
    time_error = models.DateTimeField(max_length=25, null=True)
    dumped_json = models.JSONField(null=True)

class users(models.Model):
    user = models.CharField(max_length=100)
    username = models.CharField(max_length=100, null=True)
    uno = models.CharField(max_length=100, null=True)
    clantag = models.CharField(max_length=100, null=True)

    mp = models.BooleanField(null=True)
    wz = models.BooleanField(null=True)
    cw = models.BooleanField(null=True)

    time_check_mp = models.DateTimeField(max_length=25, null=True)
    time_check_wz = models.DateTimeField(max_length=25, null=True)
    time_check_cw = models.DateTimeField(max_length=25, null=True)

    records_mp = models.IntegerField(null=True)
    records_wz = models.IntegerField(null=True)
    records_cw = models.IntegerField(null=True)

    time_records_mp = models.DateTimeField(max_length=25, null=True)
    time_records_wz = models.DateTimeField(max_length=25, null=True)
    time_records_cw = models.DateTimeField(max_length=25, null=True)

    source_records_mp = models.CharField(max_length=60, null=True)
    source_records_wz = models.CharField(max_length=60, null=True)
    source_records_cw = models.CharField(max_length=60, null=True)

    status = models.BooleanField(null=True)

    summary_stats_mp = models.JSONField(null=True)
    summary_stats_wz = models.JSONField(null=True)
    summary_stats_cw = models.JSONField(null=True)

    all_summary_stats_mp = models.JSONField(null=True)
    all_summary_stats_wz = models.JSONField(null=True)
    all_summary_stats_cw = models.JSONField(null=True)

    additional_all_stats_mp = models.JSONField(null=True)

    time_all_summary_stats_mp = models.DateTimeField(max_length=25, null=True)
    time_all_summary_stats_wz = models.DateTimeField(max_length=25, null=True)
    time_all_summary_stats_cw = models.DateTimeField(max_length=25, null=True)

    def stats(self, mode):
        self.mode = mode
        if mode == 'mp':
            result = self.additional_all_stats_mp
        else:
            result = ''
        return {
            'summary_stats': eval('self.summary_stats_'+mode),
            'all_summary_stats': eval('self.all_summary_stats_'+mode),
            'additional_all_stats': result,
            'time_all_summary_stats': eval('self.time_all_summary_stats_'+mode),
        }

    def dict_json(self):
        return {
            'User': self.user,
            'User_': '/tracker/api/raw/users/{}?format=json'.format(str(self.user).replace('#', '%23')),
            'User_mw': '/tracker/api/raw/mult/{}?format=json'.format(str(self.user).replace('#', '%23')),
            'User_wz': '/tracker/api/raw/warzone/{}?format=json'.format(str(self.user).replace('#', '%23')),
            'User_cw': '/tracker/api/raw/cold_war/{}?format=json'.format(str(self.user).replace('#', '%23')),
            'Player': self.username,
            'Multiplayer': self.mp,
            'Warzone': self.wz,
            'Cold_war': self.cw,
            'Check_time_multiplayer': str(self.time_check_mp).replace('TZ', ' ').replace('+00:00', ''),
            'Check_time_warzone': str(self.time_check_wz).replace('TZ', ' ').replace('+00:00', ''),
            'Check_time_cold_war': str(self.time_check_cw).replace('TZ', ' ').replace('+00:00', ''),
            'Records_multiplayer': self.records_mp,
            'Records_warzone': self.records_wz,
            'Records_cold_war': self.records_cw,
            'Records_time_multiplayer': str(self.time_records_mp).replace('TZ', ' ').replace('+00:00', ''),
            'Records_time_warzone': str(self.time_records_wz).replace('TZ', ' ').replace('+00:00', ''),
            'Records_time_cold_war': str(self.time_records_cw).replace('TZ', ' ').replace('+00:00', ''),
        }


class mp(models.Model):
    user = models.CharField(max_length=100)
    username = models.CharField(max_length=100, null=True)
    uno = models.CharField(max_length=100, null=True)
    clantag = models.CharField(max_length=100, null=True)
    matchID = models.CharField(max_length=100)
    timestamp = models.DateTimeField(max_length=25)
    map = models.CharField(max_length=100, null=True)
    mode = models.CharField(max_length=100, null=True)
    duration = models.TimeField(max_length=6, null=True)
    kills = models.IntegerField(null=True)
    medalXp = models.IntegerField(null=True)
    matchXp = models.IntegerField(null=True)
    scoreXp = models.IntegerField(null=True)
    wallBangs = models.IntegerField(null=True)
    score = models.IntegerField(null=True)
    totalXp = models.IntegerField(null=True)
    headshots = models.IntegerField(null=True)
    assists = models.IntegerField(null=True)
    rank = models.IntegerField(null=True)
    scorePerMinute = models.IntegerField(null=True)
    deaths = models.IntegerField(null=True)
    distanceTraveled = models.IntegerField(null=True)
    kdRatio = models.FloatField(max_length=25, null=True)
    timePlayed = models.TimeField(max_length=6, null=True)
    executions = models.IntegerField(null=True)
    nearmisses = models.IntegerField(null=True)
    percentTimeMoving = models.FloatField(null=True)
    miscXp = models.IntegerField(null=True)
    longestStreak = models.IntegerField(null=True)
    damageDone = models.BigIntegerField(null=True)
    damageTaken = models.BigIntegerField(null=True)
    loadout = models.JSONField(null=True)

    weaponStats = models.JSONField(null=True)
    result = models.CharField(max_length=40, null=True)
    team1Score = models.IntegerField(null=True)
    team2Score = models.IntegerField(null=True)
    averageSpeedDuringMatch = models.IntegerField(null=True)
    accuracy = models.IntegerField(null=True)
    shotsLanded = models.IntegerField(null=True)
    shotsMissed = models.IntegerField(null=True)
    suicides = models.IntegerField(null=True)
    seasonRank = models.IntegerField(null=True)
    shotsFired = models.IntegerField(null=True)

    objectiveMedalScoreKillSsScramblerDrone = models.IntegerField(null=True)
    objectiveMedalScoreKillSsFuelAirstrike = models.IntegerField(null=True)
    objectiveMedalScoreKillSsRadarDrone = models.IntegerField(null=True)
    objectiveScrapAssist = models.IntegerField(null=True)
    objectiveMedalScoreSsKillPrecisionAirstrike = models.IntegerField(null=True)
    objectiveMedalScoreSsKillChopperSupport = models.IntegerField(null=True)
    objectiveMedalScoreSsKillHoverJet = models.IntegerField(null=True)
    objectiveMedalScoreSsKillTomaStrike = models.IntegerField(null=True)
    objectiveMedalModeHpSecureScore = models.IntegerField(null=True)
    objectiveCaptureKill = models.IntegerField(null=True)
    objectiveMedalScoreKillSsPacSentry = models.IntegerField(null=True)
    objectiveUavAssist = models.IntegerField(null=True)
    objectiveKcFriendlyPickup = models.IntegerField(null=True)
    objectiveMedalModeDomSecureNeutralScore = models.IntegerField(null=True)
    objectiveKillDenied = models.IntegerField(null=True)
    objectiveMunitionsBoxTeammateUsed = models.IntegerField(null=True)
    objectiveMedalModeDomSecureAssistScore = models.IntegerField(null=True)
    objectiveMedalModeXDefendScore = models.IntegerField(null=True)
    objectiveObjProgDefend = models.IntegerField(null=True)
    objectiveMegaBank = models.IntegerField(null=True)
    objectiveTagCollected = models.IntegerField(null=True)
    objectiveGrindFriendlyPickup = models.IntegerField(null=True)
    objectiveTagScore = models.IntegerField(null=True)
    objectiveMedalModeKcOwnTagsScore = models.IntegerField(null=True)
    objectiveDestroyedEquipment = models.IntegerField(null=True)
    objectiveKothInObj = models.IntegerField(null=True)
    objectiveMedalModeDomSecureScore = models.IntegerField(null=True)
    objectiveMedalModeXAssaultScore = models.IntegerField(null=True)
    objectiveShieldAssist = models.IntegerField(null=True)
    objectiveHack = models.IntegerField(null=True)
    objectiveMedalScoreKillSsUav = models.IntegerField(null=True)
    objectiveMedalScoreKillSsHoverJet = models.IntegerField(null=True)
    objectiveShieldDamage = models.IntegerField(null=True)
    objectiveKillConfirmed = models.IntegerField(null=True)
    objectiveExecution = models.IntegerField(null=True)
    objectiveMedalModeDomSecureBScore = models.IntegerField(null=True)


    def dict_json(self):
        if self.accuracy == None or self.accuracy == 0:
            self.accuracy = ''
        else:
            self.accuracy = str(self.accuracy) + '%'
        return {
            'Played': str(self.timestamp).replace('TZ', ' ').replace('+00:00', ''),
            'Player': self.username,
            'Kills': self.kills,
            'Deaths': self.deaths,
            'K/D': self.kdRatio,
            'DamageDone': self.damageDone,
            'LongesStreak': self.longestStreak,
            'Headshots': self.headshots,
            'Accuracy': self.accuracy,
            'TotalXp': sep(self.totalXp),
        }


class wz(models.Model):
    user = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=100, null=True)
    uno = models.CharField(max_length=100, null=True)
    clantag = models.CharField(max_length=100, null=True)
    matchID = models.CharField(max_length=100, null=True)
    timestamp = models.DateTimeField(max_length=25, null=True)
    map = models.CharField(max_length=100, null=True)
    mode = models.CharField(max_length=100, null=True)
    duration = models.TimeField(max_length=6, null=True)
    kills = models.IntegerField(null=True)
    medalXp = models.IntegerField(null=True)
    matchXp = models.IntegerField(null=True)
    scoreXp = models.IntegerField(null=True)
    wallBangs = models.IntegerField(null=True)
    score = models.IntegerField(null=True)
    totalXp = models.IntegerField(null=True)
    headshots = models.IntegerField(null=True)
    assists = models.IntegerField(null=True)
    rank = models.IntegerField(null=True)
    scorePerMinute = models.IntegerField(null=True)
    deaths = models.IntegerField(null=True)
    distanceTraveled = models.IntegerField(null=True)
    kdRatio = models.FloatField(max_length=25, null=True)
    objectiveShieldDamage = models.IntegerField(null=True)
    timePlayed = models.TimeField(max_length=6, null=True)
    executions = models.IntegerField(null=True)
    nearmisses = models.IntegerField(null=True)
    percentTimeMoving = models.FloatField(null=True)
    miscXp = models.IntegerField(null=True)
    longestStreak = models.IntegerField(null=True)
    damageDone = models.BigIntegerField(null=True)
    damageTaken = models.BigIntegerField(null=True)
    loadout = models.JSONField(null=True)

    playerCount = models.IntegerField(null=True)
    teamCount = models.IntegerField(null=True)
    challengeXp = models.IntegerField(null=True)
    teamSurvivalTime = models.TimeField(max_length=6, null=True)
    bonusXp = models.IntegerField(null=True)
    gulagDeaths = models.IntegerField(null=True)
    gulagKills = models.IntegerField(null=True)
    teamPlacement = models.IntegerField(null=True)

    objectiveManualFlareMissileRedirect = models.IntegerField(null=True)
    objectiveDestroyedVehicleLight = models.IntegerField(null=True)
    objectiveDestroyedVehicleMedium = models.IntegerField(null=True)
    objectiveDestroyedVehicleHeavy = models.IntegerField(null=True)
    objectiveAssistDecoy = models.IntegerField(null=True)
    objectiveMedalScoreKillSsRadarDrone = models.IntegerField(null=True)
    objectiveMedalScoreSsKillPrecisionAirstrike = models.IntegerField(null=True)
    objectiveTrophyDefense = models.IntegerField(null=True)
    objectiveMedalScoreSsKillTomaStrike = models.IntegerField(null=True)
    objectiveMedalScoreKillSsHoverJet = models.IntegerField(null=True)
    objectiveMedalModeXAssaultScore = models.IntegerField(null=True)
    objectiveMedalModeDomSecureAssistScore = models.IntegerField(null=True)
    objectivePlunderCashBloodMoney = models.IntegerField(null=True)
    objectiveTeamWiped = models.IntegerField(null=True)
    objectiveLastStandKill = models.IntegerField(null=True)
    objectiveBrC130BoxOpen = models.IntegerField(null=True)
    objectiveBrMissionPickupTablet = models.IntegerField(null=True)
    objectiveReviver = models.IntegerField(null=True)
    objectiveBrKioskBuy = models.IntegerField(null=True)
    objectiveBrCacheOpen = models.IntegerField(null=True)
    objectiveMunitionsBoxTeammateUsed = models.IntegerField(null=True)
    objectiveDestroyedEquipment = models.IntegerField(null=True)
    objectiveBrDownEnemyCircle1 = models.IntegerField(null=True)
    objectiveBrDownEnemyCircle2 = models.IntegerField(null=True)
    objectiveBrDownEnemyCircle3 = models.IntegerField(null=True)
    objectiveBrDownEnemyCircle4 = models.IntegerField(null=True)
    objectiveBrDownEnemyCircle5 = models.IntegerField(null=True)
    objectiveBrDownEnemyCircle6 = models.IntegerField(null=True)

    def dict_json(self):
        return {
            'Played': str(self.timestamp).replace('TZ', ' ').replace('+00:00', ''),
            'Player': self.username,
            'Kills': self.kills,
            'Deaths': self.deaths,
            'K/D': self.kdRatio,
            'DamageDone': self.damageDone,
            'LongesStreak': self.longestStreak,
            'Headshots': self.headshots,
            'DistanceTraveled': self.distanceTraveled,
            'TotalXp': sep(self.totalXp),
        }


class cw(models.Model):
    user = models.CharField(max_length=100)
    matchID = models.CharField(max_length=100)
    timestamp = models.DateTimeField(max_length=25)
    map = models.CharField(max_length=100, null=True)
    mode = models.CharField(max_length=100, null=True)
    duration = models.TimeField(max_length=6, null=True)
    result = models.CharField(max_length=40, null=True)
    kills = models.IntegerField(null=True)
    xpAtEnd = models.IntegerField(null=True)
    ekiadRatio = models.IntegerField(null=True)
    rankAtEnd = models.IntegerField(null=True)
    accuracy = models.IntegerField(null=True)
    shotsLanded = models.IntegerField(null=True)
    highestMultikill = models.IntegerField(null=True)
    ekia = models.IntegerField(null=True)
    score = models.IntegerField(null=True)
    headshots = models.IntegerField(null=True)
    assists = models.IntegerField(null=True)
    scorePerMinute = models.IntegerField(null=True)
    deaths = models.IntegerField(null=True)
    damageDealt = models.BigIntegerField(null=True)
    kdRatio = models.FloatField(max_length=25, null=True)
    shotsMissed = models.IntegerField(null=True)
    multikills = models.IntegerField(null=True)
    highestStreak = models.IntegerField(null=True)
    hits = models.IntegerField(null=True)
    timePlayed = models.TimeField(max_length=6, null=True)
    suicides = models.IntegerField(null=True)
    timePlayedAlive = models.TimeField(max_length=6, null=True)
    objectives = models.IntegerField(null=True)
    shots = models.IntegerField(null=True)
    shotsFired = models.IntegerField(null=True)
    team1Score = models.IntegerField(null=True)
    team2Score = models.IntegerField(null=True)
    weaponStats = models.JSONField(null=True)
    
    def dict_json(self):
        if self.accuracy == None or self.accuracy == 0:
            self.accuracy = ''
        else:
            self.accuracy = str(self.accuracy) + '%'
        return {
            'Played': str(self.timestamp).replace('TZ', ' ').replace('+00:00', ''),
            'Player': str(self.user).split("#", 1)[0],
            'Kills': self.kills,
            'Deaths': self.deaths,
            'K/D': self.kdRatio,
            'DamageDone': self.damageDealt,
            'LongesStreak': self.highestStreak,
            'Headshots': self.headshots,
            'Accuracy': self.accuracy,
            'TotalXp': sep(self.xpAtEnd),
        }
