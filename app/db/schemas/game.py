from app.db import db
from sqlalchemy.dialects.postgresql import TEXT


class Game(db.Model):
    # metadata
    match_id: str = db.Column(db.TEXT, primary_key=True)
    puuid: str = db.Column(db.TEXT, primary_key=True)
    # info
    # gameCreation: str = db.Column(db.TEXT, nullable=False)
    gameDuration: int = db.Column(db.Integer)
    # gameEndTimestamp: str = db.Column(db.TEXT, nullable=False)
    # gameId: str = db.Column(db.TEXT, nullable=False)
    # gameMode: str = db.Column(db.TEXT, nullable=False)
    # gameName: str = db.Column(db.TEXT, nullable=False)
    gameStartTimestamp: str = db.Column(db.TEXT, nullable=False)
    # gameType: str = db.Column(db.TEXT, nullable=False)
    gameVersion: str = db.Column(db.TEXT, nullable=False)
    # mapId: int = db.Column(db.Integer)
    # participant
    assists: int = db.Column(db.Integer)
    baronKills: int = db.Column(db.Integer)
    basicPings: int = db.Column(db.Integer)
    # bountyLevel: int = db.Column(db.Integer)
    # IGNORING CHALLENGES
    # champExperience: int = db.Column(db.Integer)
    champLevel: int = db.Column(db.Integer)
    championId: int = db.Column(db.Integer)
    championName: str = db.Column(db.TEXT, nullable=False)
    # championTransform: int = db.Column(db.Integer)
    # consumablesPurchased: int = db.Column(db.Integer)
    damageDealtToBuildings: int = db.Column(db.Integer)
    damageDealtToObjectives: int = db.Column(db.Integer)
    damageDealtToTurrets: int = db.Column(db.Integer)
    damageSelfMitigated: int = db.Column(db.Integer)
    deaths: int = db.Column(db.Integer)
    detectorWardsPlaced: int = db.Column(db.Integer)
    # doubleKills: int = db.Column(db.Integer)
    dragonKills: int = db.Column(db.Integer)
    # eligibleForProgression: bool = db.Column(db.Boolean)
    firstBloodAssist: bool = db.Column(db.Boolean)
    firstBloodKill: bool = db.Column(db.Boolean)
    firstTowerAssist: bool = db.Column(db.Boolean)
    firstTowerKill: bool = db.Column(db.Boolean)
    gameEndedInEarlySurrender: bool = db.Column(db.Boolean)
    gameEndedInSurrender: bool = db.Column(db.Boolean)
    goldEarned: int = db.Column(db.Integer)
    # goldSpent: int = db.Column(db.Integer)
    individualPosition: str = db.Column(db.TEXT, nullable=False)
    # inhibitorKills: int = db.Column(db.Integer)
    inhibitorTakedowns: int = db.Column(db.Integer)
    inhibitorsLost: int = db.Column(db.Integer)
    item0: int = db.Column(db.Integer)
    item1: int = db.Column(db.Integer)
    item2: int = db.Column(db.Integer)
    item3: int = db.Column(db.Integer)
    item4: int = db.Column(db.Integer)
    item5: int = db.Column(db.Integer)
    item6: int = db.Column(db.Integer)
    # itemsPurchased: int = db.Column(db.Integer)
    killingSprees: int = db.Column(db.Integer)
    kills: int = db.Column(db.Integer)
    # lane: str = db.Column(db.TEXT, nullable=False)
    # largestCriticalStrike: int = db.Column(db.Integer)
    largestKillingSpree: int = db.Column(db.Integer)
    # largestMultiKill: int = db.Column(db.Integer)
    longestTimeSpentLiving: int = db.Column(db.Integer)
    # magicDamageDealt: int = db.Column(db.Integer)
    magicDamageDealtToChampions: int = db.Column(db.Integer)
    magicDamageTaken: int = db.Column(db.Integer)
    neutralMinionsKilled: int = db.Column(db.Integer)
    # nexusKills: int = db.Column(db.Integer)
    # nexusLost: int = db.Column(db.Integer)
    # nexusTakedowns: int = db.Column(db.Integer)
    objectivesStolen: int = db.Column(db.Integer)
    objectivesStolenAssists: int = db.Column(db.Integer)
    # participantId: int = db.Column(db.Integer)
    # pentaKills: int = db.Column(db.Integer)
    #perks
    # "perks": {
    #     "statPerks": {
    #         "defense": 5003,
    #         "flex": 5008,
    #         "offense": 5008
    #     },
    #     "styles": [
    #         {
    #             "description": "primaryStyle",
    #             "selections": [
    #                 {
    #                     "perk": 8010,
    #                     "var1": 329,
    #                     "var2": 0,
    #                     "var3": 0
    #                 },
    #                 {
    #                     "perk": 9111,
    #                     "var1": 21,
    #                     "var2": 140,
    #                     "var3": 0
    #                 },
    #                 {
    #                     "perk": 9105,
    #                     "var1": 18,
    #                     "var2": 30,
    #                     "var3": 0
    #                 },
    #                 {
    #                     "perk": 8299,
    #                     "var1": 340,
    #                     "var2": 0,
    #                     "var3": 0
    #                 }
    #             ],
    #             "style": 8000
    #         },
    #         {
    #             "description": "subStyle",
    #             "selections": [
    #                 {
    #                     "perk": 8429,
    #                     "var1": 57,
    #                     "var2": 11,
    #                     "var3": 13
    #                 },
    #                 {
    #                     "perk": 8451,
    #                     "var1": 202,
    #                     "var2": 0,
    #                     "var3": 0
    #                 }
    #             ],
    #             "style": 8400
    #         }
    #     ]
    # },
    # physicalDamageDealt: int = db.Column(db.Integer)
    physicalDamageDealtToChampions: int = db.Column(db.Integer)
    physicalDamageTaken: int = db.Column(db.Integer)
    # profileIcon: int = db.Column(db.Integer)
    # "puuid": "eIxZK0TNizjQxijtGBA0tQzemMytPFLpHIKhOxUB4dl9iDJP-q9Lr4yCddFO00BYf8wMLrwxLmaLpA",
    # quadraKills: int = db.Column(db.Integer)
    role: str = db.Column(db.TEXT, nullable=False)
    sightWardsBoughtInGame: int = db.Column(db.Integer)
    # spell1Casts: int = db.Column(db.Integer)
    # spell2Casts: int = db.Column(db.Integer)
    # spell3Casts: int = db.Column(db.Integer)
    # pell4Casts: int = db.Column(db.Integer)
    # summoner1Casts: int = db.Column(db.Integer)
    summoner1Id: int = db.Column(db.Integer)
    # summoner2Casts: int = db.Column(db.Integer)
    summoner2Id: int = db.Column(db.Integer)
    # summonerId: str = db.Column(db.TEXT, nullable=False)
    # summonerLevel: int = db.Column(db.Integer)
    # summonerName: str = db.Column(db.TEXT, nullable=False)
    teamEarlySurrendered: bool = db.Column(db.Boolean)
    teamId: int = db.Column(db.Integer)
    # teamPosition: str = db.Column(db.TEXT, nullable=False)
    timeCCingOthers: int = db.Column(db.Integer)
    timePlayed: int = db.Column(db.Integer)
    # totalDamageDealt: int = db.Column(db.Integer)
    totalDamageDealtToChampions: int = db.Column(db.Integer)
    totalDamageShieldedOnTeammates: int = db.Column(db.Integer)
    totalDamageTaken: int = db.Column(db.Integer)
    totalHeal: int = db.Column(db.Integer)
    totalHealsOnTeammates: int = db.Column(db.Integer)
    totalMinionsKilled: int = db.Column(db.Integer)
    totalTimeCCDealt: int = db.Column(db.Integer)
    totalTimeSpentDead: int = db.Column(db.Integer)
    totalUnitsHealed: int = db.Column(db.Integer)
    # tripleKills: int = db.Column(db.Integer)
    # trueDamageDealt: int = db.Column(db.Integer)
    trueDamageDealtToChampions: int = db.Column(db.Integer)
    trueDamageTaken: int = db.Column(db.Integer)
    turretKills: int = db.Column(db.Integer)
    turretTakedowns: int = db.Column(db.Integer)
    turretsLost: int = db.Column(db.Integer)
    # unrealKills: int = db.Column(db.Integer)
    visionScore: int = db.Column(db.Integer)
    visionWardsBoughtInGame: int = db.Column(db.Integer)
    wardsKilled: int = db.Column(db.Integer)
    wardsPlaced: int = db.Column(db.Integer)
    win: bool = db.Column(db.Boolean)

    def __init__(self, match, start, duration, version, participant):
        self.match_id = match
        self.puuid = participant["puuid"]
        self.gameStartTimestamp = start
        self.gameDuration = duration
        self.gameVersion = version
        self.assists = participant["assists"]
        self.baronKills = participant["baronKills"]
        self.basicPings = participant.get("basicPings", 0)
        self.champLevel = participant["champLevel"]
        self.championId = participant["championId"]
        self.championName = participant["championName"]
        self.consumablesPurchased = participant["consumablesPurchased"]
        self.damageDealtToBuildings = participant["damageDealtToBuildings"]
        self.damageDealtToObjectives = participant["damageDealtToObjectives"]
        self.damageDealtToTurrets = participant["damageDealtToTurrets"]
        self.damageSelfMitigated = participant["damageSelfMitigated"]
        self.deaths = participant["deaths"]
        self.detectorWardsPlaced = participant["detectorWardsPlaced"]
        self.dragonKills = participant["dragonKills"]
        self.firstBloodAssist = participant["firstBloodAssist"]
        self.firstBloodKill = participant["firstBloodKill"]
        self.firstTowerAssist = participant["firstTowerAssist"]
        self.firstTowerKill = participant["firstTowerKill"]
        self.gameEndedInEarlySurrender = participant["gameEndedInEarlySurrender"]
        self.gameEndedInSurrender = participant["gameEndedInSurrender"]
        self.goldEarned = participant["goldEarned"]
        self.individualPosition = participant["individualPosition"]
        self.inhibitorTakedowns = participant["inhibitorTakedowns"]
        self.inhibitorsLost = participant["inhibitorsLost"]
        self.item0 = participant["item0"]
        self.item1 = participant["item1"]
        self.item2 = participant["item2"]
        self.item3 = participant["item3"]
        self.item4 = participant["item4"]
        self.item5 = participant["item5"]
        self.item6 = participant["item6"]
        self.killingSprees = participant["killingSprees"]
        self.kills = participant["kills"]
        self.largestKillingSpree = participant["largestKillingSpree"]
        self.longestTimeSpentLiving = participant["longestTimeSpentLiving"]
        self.magicDamageDealtToChampions = participant["magicDamageDealtToChampions"]
        self.magicDamageTaken = participant["magicDamageTaken"]
        self.neutralMinionsKilled = participant["neutralMinionsKilled"]
        self.objectivesStolen = participant["objectivesStolen"]
        self.objectivesStolenAssists = participant["objectivesStolenAssists"]
        self.physicalDamageDealtToChampions = participant["physicalDamageDealtToChampions"]
        self.physicalDamageTaken = participant["physicalDamageTaken"]
        self.role = participant["role"]
        self.sightWardsBoughtInGame = participant["sightWardsBoughtInGame"]
        self.summoner1Id = participant["summoner1Id"]
        self.summoner2Id = participant["summoner2Id"]
        self.teamEarlySurrendered = participant["teamEarlySurrendered"]
        self.teamId = participant["teamId"]
        self.timeCCingOthers = participant["timeCCingOthers"]
        self.timePlayed = participant["timePlayed"]
        self.totalDamageDealtToChampions = participant["totalDamageDealtToChampions"]
        self.totalDamageShieldedOnTeammates = participant["totalDamageShieldedOnTeammates"]
        self.totalDamageTaken = participant["totalDamageTaken"]
        self.totalHeal = participant["totalHeal"]
        self.totalHealsOnTeammates = participant["totalHealsOnTeammates"]
        self.totalMinionsKilled = participant["totalMinionsKilled"]
        self.totalTimeCCDealt = participant["totalTimeCCDealt"]
        self.totalTimeSpentDead = participant["totalTimeSpentDead"]
        self.totalUnitsHealed = participant["totalUnitsHealed"]
        self.trueDamageDealtToChampions = participant["trueDamageDealtToChampions"]
        self.trueDamageTaken = participant["trueDamageTaken"]
        self.turretKills = participant["turretKills"]
        self.turretTakedowns = participant["turretTakedowns"]
        self.turretsLost = participant["turretsLost"]
        self.visionScore = participant["visionScore"]
        self.visionWardsBoughtInGame = participant["visionWardsBoughtInGame"]
        self.wardsKilled = participant["wardsKilled"]
        self.wardsPlaced = participant["wardsPlaced"]
        self.win = participant["win"]
