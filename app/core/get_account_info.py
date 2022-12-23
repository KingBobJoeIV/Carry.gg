from . import constants, get_match_info
from .watcher import lol_watcher
from app.db import db
from app.db.schemas import PlayerInfo
# from get_match_info import store_match_in_db, get_all_matches
import json
from pathlib import Path
from app.internal.caching.response_caching import cache
import time
import math


# todo needs to be updated every patch
# @cache
def map_id_to_champ():
    p=Path("./app/ddragon_12_23_1_champ_data.json").resolve()
    print(p)
    f = open(p)
    data = json.load(f)
    for key in data["data"].keys():
        constants.CHAMPION_MAPPING[int(data["data"][key]["key"])] = data["data"][key]["id"]


def get_champ_from_id(championId):
    return constants.CHAMPION_MAPPING[championId]


def get_info(puuid):
    return lol_watcher.summoner.by_puuid(constants.MY_REGION, puuid)


def get_info_by_ign(ign):
    return lol_watcher.summoner.by_name(constants.MY_REGION, ign)


def get_puuid_from_id(id):
    return lol_watcher.summoner.by_id(constants.MY_REGION, id)["puuid"]


def get_rank_info(summonerId):
    leagues = lol_watcher.league.by_summoner(constants.MY_REGION, summonerId)
    for league in leagues:
        if league["queueType"] == "RANKED_SOLO_5x5":
            return league


def get_mastery_for_champ(summonerId, championId):
    return lol_watcher.champion_mastery.by_summoner_by_champion(constants.MY_REGION, summonerId, championId)["championPoints"]


def get_all_mastery(summonerId):
    return lol_watcher.champion_mastery.by_summoner(constants.MY_REGION, summonerId)


def store_player_in_db(puuid):
    curr = get_info(puuid)
    print("main player storing:", curr["name"])
    # replace revisionDate with current time
    curr["revisionDate"] = math.floor(time.time() * 1000)
    # check to see if account is already stored in db
    info = PlayerInfo.query.filter_by(puuid=puuid).first()
    # create a new row for the account
    if not info:
        mastery = get_all_mastery(curr["id"])[0]
        league = get_rank_info(curr["id"])
        if not league:
            league = []
        row = PlayerInfo(curr, mastery, league, {}, {})
        db.session.add(row)
    # if it has been at least 2 minutes since last update, update info
    elif curr["revisionDate"] - info.revisionDate > 120000:
        # all matches the player has played
        all_matches = set(get_match_info.get_all_matches(puuid))
        # matches that are stored
        temp = info.matchlist
        stored = set()
        for t in temp.keys():
            stored.add(t)
        print("all:", len(all_matches), all_matches)
        print("stored:", len(stored), stored)
        # set difference, store new matches
        for match in all_matches - stored:
            print("looping through match:", match)
            get_match_info.store_match_in_db(match)
        print("Updated:", curr["name"])
    db.session.commit()
    return (info or row).as_json


def determine_level_image(level):
    if 30 <= level < 50:
        return 30
    elif level >= 500:
        return 500
    return (level // 25) * 25
