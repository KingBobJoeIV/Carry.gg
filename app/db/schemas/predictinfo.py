from app.db import db
from sqlalchemy.dialects.postgresql import TEXT


class PredictInfo(db.Model):
    # todo make this int
    match_id: str = db.Column(db.TEXT, primary_key=True)
    ids: str = db.Column(db.TEXT)
    predictedWinner: str = db.Column(db.TEXT)
    actualWinner: str = db.Column(db.TEXT)
    predictedChance: float = db.Column(db.Float)

    def __init__(self, match_id, ids, predict, actual, chance):
        self.match_id = match_id
        self.ids = ids
        self.predictedWinner = predict
        self.actualWinner = actual
        self.predictedChance = chance

    @property
    def as_json(self):
        return {
            "match_id": self.match_id,
            "ids": self.ids,
            "predictedWinner": self.predictedWinner,
            "actualWinner": self.actualWinner,
            "predictedChance": self.predictedChance
        }
