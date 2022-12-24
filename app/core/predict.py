import concurrent.futures
import pickle
from multiprocessing import Process, Queue
import numpy as np
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
    X = [None for _ in range(10)]
    role_mat_map = {"TOP": 0, "JUNGLE": 1, "MIDDLE": 2, "BOTTOM": 3, "UTILITY": 4}
    # print(participant_id_mapping.values())
    # figure out last revisionDate for all players
    times = [None for _ in range(10)]
    count = 0
    print("All players' info fetching started at:" + str(datetime.datetime.fromtimestamp(time.time())))
    # todo prob redundant fix later
    # create rows for participants
    for participant in participant_id_mapping.values():
        info = PlayerInfo.query.filter_by(puuid=participant).first()
        if not info:
            curr = get_account_info.get_info(participant)
            curr["revisionDate"] = constants.SZN_START
            mastery = get_account_info.get_all_mastery(curr["id"])[0]
            league = get_account_info.get_rank_info(curr["id"])
            if not league:
                league = []
            row = PlayerInfo(curr, mastery, league, {}, {})
            db.session.add(row)
            times[count] = constants.SZN_START
        else:
            times[count] = info.revisionDate
        count += 1
    db.session.commit()
    # get all matches
    print(times)
    all_matches = get_match_info.get_matches_for_pred(list(participant_id_mapping.values()), times)
    # divide matches evenly for 5 threads
    splits = get_match_info.split_into_threads(all_matches[0], all_matches[1], constants.NUM_THREADS)
    to_store = []
    # execute n threads
    q = Queue()
    p = [Process(target=get_match_info.process_by_thread, args=(split, q)) for split in splits]
    for t in p:
        t.start()
    for t in p:
        to_store.append(q.get())
    for t in p:
        t.join()
    # put results of threads into 1 dict
    final = get_match_info.join_threads(to_store)
    # store results in db
    print("All players' info updated in db at:" + str(datetime.datetime.fromtimestamp(time.time())))
    for k in final.keys():
        get_match_info.store_blobs_in_db(final[k][0], final[k][1], k)
    for participant in participant_id_mapping.values():
        if counter < 5:
            current_participant_champ = team1_roles[get_key(participant_id_mapping, participant)]
            role = get_key(team1_role_res, current_participant_champ)
        else:
            current_participant_champ = team2_roles[get_key(participant_id_mapping, participant)]
            role = get_key(team2_role_res, current_participant_champ)
        # fetch all matches that the user has played by current champ in current role and use for calculations
        curr_player_info = PlayerInfo.query.filter_by(puuid=participant).first()
        champ_role = str(current_participant_champ) + ", " + role
        # get data for the current champ_role from db; if never played set all vals to 0
        if counter < 5:
            try:
                data = curr_player_info.blob[champ_role]
                X[role_mat_map[role]] = data[0]
            except:
                # todo make constant (12) change everywhere
                X[role_mat_map[role]] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        else:
            try:
                data = curr_player_info.blob[champ_role]
                X[role_mat_map[role] + 5] = data[0]
            except:
                X[role_mat_map[role] + 5] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        counter += 1
        # fetch time of one participant
        print(curr_player_info.name + "'s games fetched at: " + str(datetime.datetime.fromtimestamp(time.time())))
    # make the prediction
    # todo make constant
    X = np.array(sum(X, [])).reshape(1, -1)
    with open('app/core/model.pkl', 'rb') as f:
        model = pickle.load(f)
    res = model.predict_proba(X)[0]
    print(res)
    print("gameId:", curr_match["gameId"])
    print("Team 1 Win Percentage:", res[0])
    print("Team 2 Win Percentage:", res[1])
    if res[1] < .5:
        compare_teams.store_prediction_in_db(str(curr_match["gameId"]), 0, curr_match["gameStartTime"],
                                             str(list(participant_id_mapping.keys())), "Team 1", "Pending", str(res[0]))
    else:
        compare_teams.store_prediction_in_db(str(curr_match["gameId"]), 0, curr_match["gameStartTime"],
                                             str(list(participant_id_mapping.keys())), "Team 2", "Pending", str(res[1]))
    # remove finished prediction from files
    remove_live(curr_match["gameId"])
    return res
