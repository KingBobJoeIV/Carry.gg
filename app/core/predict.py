from . import constants
from . import get_account_info
from . import calculate_weights
from . import get_match_info
import time, datetime
from . import compare_teams
from .watcher import lol_watcher
from app.db import db
from app.db.schemas import PredictInfo, AccountInfo, GameInfo, Game
from app.internal.roleidentification import pull_data, get_roles


def get_key(dict, val):
    for key, value in dict.items():
        if val == value:
            return key


# predict live game given username
def predict(ign):
    # this is for most recent
    # # get matches of current user
    # curr_user_matches = get_match_info.get_matches(current_puuid,0)
    #
    # # get user's most recent game id
    # most_recent_game = curr_user_matches[0]
    #
    # # get info of most recent game
    # curr_match = lol_watcher.match.by_id(constants.REGION, most_recent_game)
    # participants = curr_match["metadata"]["participants"]

    # this is for live game
    current_id = get_account_info.get_info_by_ign(ign)["id"]
    curr_match = get_match_info.get_live_match(current_id)
    # get ids of each participant in live game
    participants = curr_match["participants"]
    participant_id_mapping = {}
    # todo have redundant api calls
    # key: id, value = puuid
    for p in participants:
        p = p["summonerId"]
        participant_id_mapping[p] = get_account_info.get_puuid_from_id(p)
    team1 = []
    team2 = []
    team1_members = []
    team2_members = []
    team1_roles = {}
    team2_roles = {}
    team1_ranks = []
    team2_ranks = []
    counter = 0
    # todo dont need to do this if i do by champ
    # map id to champ id
    for p in curr_match["participants"]:
        if counter < 5:
            team1_roles[p["summonerId"]] = p["championId"]
        else:
            team2_roles[p["summonerId"]] = p["championId"]
        counter += 1
    # get champion role info
    champion_roles = pull_data()
    # add data for Bel'Veth and Nilah todo this won't be an issue if i do by champ
    # Bel'Veth:
    champion_roles[200] = {'TOP': 0.027, 'JUNGLE': 0.957, 'MIDDLE': 0.01, 'BOTTOM': 0.02, 'UTILITY': 0.04}
    # Nilah:
    champion_roles[895] = {'TOP': 0.029, 'JUNGLE': 0.07, 'MIDDLE': 0.026, 'BOTTOM': 0.934, 'UTILITY': 0.03}
    # map champ id to role
    team1_role_res = get_roles(champion_roles, list(team1_roles.values()))
    team2_role_res = get_roles(champion_roles, list(team2_roles.values()))
    counter = 0
    # start time
    print("Start:", datetime.datetime.fromtimestamp(time.time()))
    for participant in participant_id_mapping.values():
        # todo dont have to deal with this if i use champ ids
        if counter < 5:
            current_participant_champ = team1_roles[get_key(participant_id_mapping, participant)]
            role = get_key(team1_role_res, current_participant_champ)
        else:
            current_participant_champ = team2_roles[get_key(participant_id_mapping, participant)]
            role = get_key(team2_role_res, current_participant_champ)
        # fetch and update/add curr_account to accountinfo table
        get_account_info.store_account_in_db(participant)
        curr_acc_info = AccountInfo.query.filter_by(puuid=participant).first()
        # get matches, calculate weights, get current champion mastery, and assign each participant to a team
        # fetch 20 most recent matches from riot api
        participant_recent_matches = get_match_info.get_matches(participant)
        # updates db with any new matches
        get_match_info.update_matches(participant_recent_matches)
        # todo use matches by current champ(later)
        # fetch all matches that the user has played by current role and use for calculations
        participant_stored_matches = Game.query.filter_by(puuid=participant, individualPosition=role)
        current_participant_weights = calculate_weights.calculate_weights(participant_stored_matches)
        # this is done in memory, don't store current champ mastery, return 0 if first time
        try:
            current_participant_mastery = get_account_info.get_mastery_for_champ(curr_acc_info.id, current_participant_champ)
        except:
            current_participant_mastery = 0
        # first 5 members in t1, last 5 in t2
        if counter < 5:
            team1.append(calculate_weights.normalize_stats(
                calculate_weights.bin_stats([current_participant_mastery] + current_participant_weights)))
            team1_members.append(curr_acc_info.name)
            team1_ranks.append(calculate_weights.normalize_rank(curr_acc_info.rank, curr_acc_info.tier, curr_acc_info.leaguePoints))
        else:
            team2.append(calculate_weights.normalize_stats(
                calculate_weights.bin_stats([current_participant_mastery] + current_participant_weights)))
            team2_members.append(curr_acc_info.name)
            team2_ranks.append(calculate_weights.normalize_rank(curr_acc_info.rank, curr_acc_info.tier, curr_acc_info.leaguePoints))
        counter += 1
        # fetch time of one participant
        print(curr_acc_info.name + "'s games fetched at: " + str(datetime.datetime.fromtimestamp(time.time())))
    # print(type(curr_match["gameId"]))
    scores = compare_teams.compare_teams(str(curr_match["gameId"]), team1, team2, team1_ranks, team2_ranks)
    print("gameId:", scores[0])
    print("Team 1:", team1_members)
    print("Team 1 Score:", scores[1])
    print("VS")
    print("Team 2:", team2_members)
    print("Team 2 Score:", scores[2])
    print("Team 1 Win Percentage:", scores[3])
    print("Team 2 Win Percentage:", scores[4])
    try:
        if scores[1] > scores[2]:
            compare_teams.store_prediction_in_db(scores[0], str(list(participant_id_mapping.keys())), "Team 1", "Pending", scores[3])
        else:
            compare_teams.store_prediction_in_db(scores[0], str(list(participant_id_mapping.keys())), "Team 2", "Pending", scores[4])
    except:
        # todo don't go through entire process, check at beginning
        print("prediction already in db!")
    return scores
