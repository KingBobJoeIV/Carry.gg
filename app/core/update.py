from . import constants
from . import get_account_info, get_match_info, compare_teams
from app.db import db
from app.db.schemas import AccountInfo, PredictInfo, GameInfo
from . import compare_teams
import time


def update(ign):
    try:
        account = get_account_info.get_info_by_ign(ign)
    except Exception as e:
        print(e)
        return "notfound"
    # too low level players have no profile
    if account["summonerLevel"] < 30:
        return "toolow"
    # update in account table
    get_account_info.store_account_in_db(account["puuid"])
    # select * from predict_info where match_id = live_game_id and puuid contains ‘id’
    # find any pending past prediction games and update status
    pending = PredictInfo.query.filter(PredictInfo.ids.contains(account["id"])).filter_by(actualWinner="Pending").all()
    for prediction in pending:
        try:
            # get match from riot and store it
            match = get_match_info.get_match_by_id("NA1_" + prediction.match_id)
            # if already stored
            if not GameInfo.query.filter_by(matchId="NA1_" + prediction.match_id).first():
                get_match_info.store_match_in_db(match)
            # remove it from cache if still in it
            if int(prediction.match_id) in constants.pending:
                constants.pending.remove(int(prediction.match_id))
            # if team 1 won
            if match["info"]["teams"][0]["win"]:
                compare_teams.update_prediction_db(prediction.match_id, "Team 1")
            else:
                compare_teams.update_prediction_db(prediction.match_id, "Team 2")
        except:
            # remove it from cache
            try:
                constants.pending.remove(int(prediction.match_id))
            except Exception as e:
                print("e", e)
                continue
            continue
    return "ok"


# todo problem with name changes DON'T USE!
# for internal use only
# this also updates the predict table
def update_account_table():
    rows = db.session.query(AccountInfo)
    for row in rows:
        update(row.name)
    print("all accounts updated!")
