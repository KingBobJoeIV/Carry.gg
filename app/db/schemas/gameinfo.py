# this is unused
from app.db import db
from sqlalchemy.dialects.postgresql import TEXT


class GameInfo(db.Model):
    matchId: str = db.Column(db.TEXT, primary_key=True)
    gameDuration: int = db.Column(db.Integer)
    gameStartTimestamp: str = db.Column(db.TEXT, nullable=False)
    gameVersion: str = db.Column(db.TEXT, nullable=False)
    queueId: int = db.Column(db.Integer)

    def __init__(self, id, duration, start, version, queue):
        self.matchId = id
        self.gameDuration = duration
        self.gameStartTimestamp = start
        self.gameVersion = version
        self.queueId = queue

    @property
    def as_json(self):
        return {
            "matchId": self.matchId,
            "gameDuration": self.gameDuration,
            "gameStartTimestamp": self.gameStartTimestamp,
            "gameVersion": self.gameVersion,
            "queueId": self.queueId
        }