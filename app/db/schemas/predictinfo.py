from app.db import db
from sqlalchemy.dialects.postgresql import TEXT


class PredictInfo(db.Model):
    # todo make this int
    match_id: str = db.Column(db.TEXT, primary_key=True)
    gameDuration: int = db.Column(db.Integer)
    gameStartTimestamp: str = db.Column(db.TEXT, nullable=False)
    ids: str = db.Column(db.TEXT)
    predictedWinner: str = db.Column(db.TEXT)
    actualWinner: str = db.Column(db.TEXT)
    predictedChance: float = db.Column(db.Float)

    def __init__(self, match_id, duration, start, ids, predict, actual, chance):
        self.match_id = match_id
        self.gameDuration = duration
        self.gameStartTimestamp = start
        self.ids = ids
        self.predictedWinner = predict
        self.actualWinner = actual
        self.predictedChance = chance

    @property
    def as_json(self):
        return {
            "match_id": self.match_id,
            "gameDuration": self.duration,
            "gameStartTimestamp": self.start,
            "ids": self.ids,
            "predictedWinner": self.predictedWinner,
            "actualWinner": self.actualWinner,
            "predictedChance": self.predictedChance
        }
