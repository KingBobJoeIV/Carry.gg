import math
from . import constants
from .watcher import lol_watcher
from app.db import db
from app.db.schemas import PredictInfo
import numpy as np


# todo do matrix multiplication(dot product), x0-xn dot w0-wn, pass in vector(list) instead
# todo team1,team2 are now lists of np arrays <- need to dot by weights
# todo tweak weights for accuracy
# todo mastery weight will be different based on champion mastery curve data when i change later
def calculate_weights(mastery, kills, deaths, assists, cs, wins, rank):
    # weights = np.array([.5, -.7, .5, .2,log?])
    w = [1, .2, .4, .1, .3, .8]
    # multiply result by rank modifier
    return rank * ((w[0] * mastery) + (w[1] * kills) + (w[2] * (1 - deaths)) + (w[3] * assists) + (w[4] * cs) + (w[5] * wins))


# todo make this more functional
# todo fix!!!!!!!!!!!
def compare_teams(gameId, team1, team2, t1_ranks, t2_ranks):
    t1_score = 0
    t2_score = 0
    for player, rank in zip(team1, t1_ranks):
        t1_score += calculate_weights(player[0], player[1], player[2], player[3], player[4], player[5], rank)
    for player, rank in zip(team2, t2_ranks):
        t2_score += calculate_weights(player[0], player[1], player[2], player[3], player[4], player[5], rank)
    t1_percent = t1_score / (t1_score + t2_score)
    t2_percent = t2_score / (t1_score + t2_score)
    return gameId, t1_score, t2_score, t1_percent, t2_percent


def store_prediction_in_db(match_id, ids, prediction, actual, chance):
    row = PredictInfo(match_id, ids, prediction, actual, chance)
    db.session.add(row)
    db.session.commit()
    return row.as_json


def update_prediction_db(match_id, actual):
    row = PredictInfo.query.filter_by(match_id=str(match_id)).first()
    if row:
        row.actualWinner = actual
        db.session.commit()
        return row.as_json


def check_if_in_game(id):
    return lol_watcher.spectator.by_summoner(constants.MY_REGION, id)


# todo where this gets called
def get_predictions_by_id(id):
    return PredictInfo.query.filter(PredictInfo.ids.contains(id)).all()
