from . import constants
from .watcher import lol_watcher
from app.db import db
from app.db.schemas import PredictInfo


def store_prediction_in_db(match_id, duration, start, ids, prediction, actual, chance):
    row = PredictInfo(match_id, duration, start, ids, prediction, actual, chance)
    db.session.add(row)
    db.session.commit()
    print("stored prediction:", match_id)
    return row.as_json


def update_prediction_db(match_id, actual, duration):
    row = PredictInfo.query.filter_by(match_id=str(match_id)).first()
    if row:
        row.actualWinner = actual
        row.gameDuration = duration
        db.session.commit()
        return row.as_json


def check_if_in_game(id):
    return lol_watcher.spectator.by_summoner(constants.MY_REGION, id)


# todo where this gets called
def get_predictions_by_id(id):
    return PredictInfo.query.filter(PredictInfo.ids.contains(id)).all()
