from . import constants
from . import get_account_info
from . import calculate_weights
from . import get_match_info
import time, datetime
from . import compare_teams
from .watcher import lol_watcher
from app.db import db
from app.db.schemas import PredictInfo, PlayerInfo
from app.internal.roleidentification import pull_data, get_roles
from pathlib import Path
import os
from sklearn.linear_model import LogisticRegression
# from cachetools import cached, TTLCache
# from app.internal.caching.response_caching import cache


#cache = TTLCache(maxsize=100, ttl=86400)


def get_key(dict, val):
    for key, value in dict.items():
        if val == value:
            return key


def add_to_live(match):
    curr = Path.cwd()
    f_name = "app/pending/" + str(match) + ".txt"
    file = make_path(match)
    print(file)
    if file.is_file():
        return False
    in_db = PredictInfo.query.filter(PredictInfo.match_id == str(match)).first()
    if in_db is not None and in_db.actualWinner == "Pending":
        return False
    f = open(f_name, "w")
    f.close()
    return True


def make_path(match):
    curr = Path.cwd()
    f_path = "app/pending/" + str(match) + ".txt"
    return curr / f_path


def remove_live(match):
    os.remove(make_path(match))


# predict live game given username
def predict(ign, app):
    app.app_context().push()
    # this is for live game
    current_id = get_account_info.get_info_by_ign(ign)["id"]
    curr_match = get_match_info.get_live_match(current_id)
    # check if prediction is already pending
    if not add_to_live(curr_match["gameId"]):
        return
    # check if prediction is already in db
    in_db = PredictInfo.query.filter(PredictInfo.match_id == str(curr_match["gameId"])).first()
    if in_db is not None:
        return
    # get ids of each participant in live game
    participants = curr_match["participants"]
    participant_id_mapping = {}
    # todo have redundant api calls
    # key: id, value = puuid
    for p in participants:
        p = p["summonerId"]
        participant_id_mapping[p] = get_account_info.get_puuid_from_id(p)
    team1_members = []
    team2_members = []
    team1_roles = {}
    team2_roles = {}
    counter = 0
    # todo dont need to do this if i do by champ? maybe still have to
    # map id to champ id
    for p in curr_match["participants"]:
        if counter < 5:
            team1_roles[p["summonerId"]] = p["championId"]
        else:
            team2_roles[p["summonerId"]] = p["championId"]
        counter += 1
    # get champion role info
    champion_roles = pull_data()
    # map champ id to role
    team1_role_res = get_roles(champion_roles, list(team1_roles.values()))
    team2_role_res = get_roles(champion_roles, list(team2_roles.values()))
    counter = 0
    # start time
    print("Start:", datetime.datetime.fromtimestamp(time.time()))
    # vector containing prediction data p1, p2, ..., p10
    X = []
    print(participant_id_mapping.values())
    exit()
    for participant in participant_id_mapping.values():
        if counter < 5:
            current_participant_champ = team1_roles[get_key(participant_id_mapping, participant)]
            role = get_key(team1_role_res, current_participant_champ)
        else:
            current_participant_champ = team2_roles[get_key(participant_id_mapping, participant)]
            role = get_key(team2_role_res, current_participant_champ)
        # fetch and update/add curr_account to accountinfo table
        get_account_info.store_player_in_db(participant)
        curr_player_info = PlayerInfo.query.filter_by(puuid=participant).first()
        # fetch all matches that the user has played by current champ in current role and use for calculations
        champ_role = str(current_participant_champ) + ", " + role
        data = None
        # get data for the current champ_role from db; if never played set all vals to 0
        data = curr_player_info.blob[champ_role]
        if data is not None:
            X.extend(data[0])
        else:
            X.extend([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        counter += 1
        # fetch time of one participant
        print(curr_player_info.name + "'s games fetched at: " + str(datetime.datetime.fromtimestamp(time.time())))
    # make the prediction
    res = constants.model.predict(X)
    print("gameId:", curr_match["gameId"])
    print("Team 1:", team1_members)
    print("VS")
    print("Team 2:", team2_members)
    print("Team 1 Win Percentage:", 1-res)
    print("Team 2 Win Percentage:", res)
    if res < .5:
        compare_teams.store_prediction_in_db(curr_match["gameId"], 0, curr_match["gameStartTime"],
                                             str(list(participant_id_mapping.keys())), "Team 1", "Pending", 1-res)
    else:
        compare_teams.store_prediction_in_db(curr_match["gameId"], 0, curr_match["gameStartTime"],
                                             str(list(participant_id_mapping.keys())), "Team 2", "Pending", res)
    # remove finished prediction from files
    remove_live(curr_match["gameId"])
    return res
