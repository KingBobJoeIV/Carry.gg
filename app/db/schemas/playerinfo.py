from app.db import db


class PlayerInfo(db.Model):
    accountId: str = db.Column(db.TEXT, nullable=False, primary_key=True)
    profileIconId: int = db.Column(db.Integer)
    revisionDate: int = db.Column(db.BIGINT)
    name: str = db.Column(db.TEXT, unique=True, nullable=True)
    id: str = db.Column(db.TEXT, nullable=False, primary_key=True)
    puuid: str = db.Column(db.TEXT, nullable=False, primary_key=True)
    summonerLevel: int = db.Column(db.Integer)
    championId: int = db.Column(db.Integer)
    championPoints: int = db.Column(db.Integer)
    championLevel: int = db.Column(db.Integer)
    tier: str = db.Column(db.TEXT)
    rank: str = db.Column(db.TEXT)
    leaguePoints: int = db.Column(db.Integer)
    wins: int = db.Column(db.Integer)
    losses: int = db.Column(db.Integer)
    blob: str = db.Column(db.JSON)
    matchlist: str = db.Column(db.JSON)

    def __init__(self, summoner, mastery, league, predict, matches):
        self.accountId = summoner["accountId"]
        self.profileIconId = summoner["profileIconId"]
        # replacing with last time update was called (in get_account_info)
        self.revisionDate = summoner["revisionDate"]
        self.name = summoner["name"]
        self.id = summoner["id"]
        self.puuid = summoner["puuid"]
        self.summonerLevel = summoner["summonerLevel"]
        self.championId = mastery["championId"]
        self.championPoints = mastery["championPoints"]
        self.championLevel = mastery["championLevel"]
        if league:
            self.tier = league["tier"]
            self.rank = league["rank"]
            self.leaguePoints = league["leaguePoints"]
            self.wins = league["wins"]
            self.losses = league["losses"]
        else:
            self.tier = "UNRANKED"
            self.rank = ""
            self.leaguePoints = 0
            self.wins = 0
            self.losses = 0
        self.blob = predict
        self.matchlist = matches

    @property
    def as_json(self):
        return {
            "accountId": self.accountId,
            "profileIconId": self.profileIconId,
            "revisionDate": self.revisionDate,
            "name": self.name,
            "id": self.id,
            "puuid": self.puuid,
            "summonerLevel": self.summonerLevel,
            "championId": self.championId,
            "championPoints": self.championPoints,
            "championLevel": self.championLevel,
            "tier": self.tier,
            "rank": self.rank,
            "leaguePoints": self.leaguePoints,
            "wins": self.wins,
            "losses": self.losses,
            "blob": self.blob,
            "matchlist": self.matchlist
        }
