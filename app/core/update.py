from . import constants
from . import get_account_info, get_match_info, compare_teams
from app.db import db
from app.db.schemas import PredictInfo
from app.core.predict import remove_live, make_path


def update(ign):
    try:
        account = get_account_info.get_info_by_ign(ign)
        me = get_account_info.get_summoner_by_riot_acc(account)
    # todo do separate error codes(notfound/servererror)
    # todo also add this when getting matches(500)
    except Exception as e:
        print(e)
        return "notfound", None, None
    # too low level players have no profile
    if me["summonerLevel"] < 30:
        return "toolow", None, None
    # update in account table
    # todo don't update during a prediction

    get_account_info.store_player_in_db(account, me)
    # select * from predict_info where match_id = live_game_id and puuid contains ‘id’
    # find any pending past prediction games and update status
    pending = PredictInfo.query.filter(PredictInfo.ids.contains(me["id"])).filter_by(actualWinner="Pending").all()
    for prediction in pending:
        try:
            # get match from riot
            match = get_match_info.get_match_by_id("NA1_" + prediction.match_id)
            # remove it from files if still in it
            file = make_path(prediction.match_id)
            if file.is_file():
                remove_live(prediction.match_id)
            # if team 1 won
            if match["info"]["teams"][0]["win"]:
                compare_teams.update_prediction_db(prediction.match_id, "Team 1", match["info"]["gameDuration"])
            else:
                compare_teams.update_prediction_db(prediction.match_id, "Team 2", match["info"]["gameDuration"])
        except:
            # remove it from files
            try:
                remove_live(prediction.match_id)
            except Exception as e:
                print("e", e)
                continue
            continue
    return "ok", account, me
