import datetime
from . import constants, get_match_info
from .watcher import lol_watcher
from app.db import db
from app.db.schemas import PlayerInfo
from sqlalchemy.orm.attributes import flag_modified
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
    print("storing:", curr["name"], "started at", str(datetime.datetime.fromtimestamp(time.time())))
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
        db.session.commit()
        print("new row created for:", curr["name"], "finished at:", str(datetime.datetime.fromtimestamp(time.time())))
    # if it has been at least 2 minutes since last update, update info
    elif curr["revisionDate"] - info.revisionDate > 120000:
        mastery = get_all_mastery(curr["id"])[0]
        league = get_rank_info(curr["id"])
        if league:
            setattr(info, "tier", league["tier"])
            setattr(info, "rank", league["rank"])
            setattr(info, "leaguePoints", league["leaguePoints"])
            setattr(info, "wins", league["wins"])
            setattr(info, "losses", league["losses"])
            flag_modified(info, "tier")
            flag_modified(info, "rank")
            flag_modified(info, "leaguePoints")
            flag_modified(info, "wins")
            flag_modified(info, "losses")
        setattr(info, "championId", mastery["championId"])
        setattr(info, "championPoints", mastery["championPoints"])
        setattr(info, "championLevel", mastery["championLevel"])
        setattr(info, "revisionDate", curr["revisionDate"])
        flag_modified(info, "championId")
        flag_modified(info, "championPoints")
        flag_modified(info, "championLevel")
        flag_modified(info, "revisionDate")
        db.session.commit()
        print("Updated:", curr["name"], "finished at:", str(datetime.datetime.fromtimestamp(time.time())))
    else:
        print("too soon to update", curr["name"])
    return (info or row).as_json


def get_current_champ_info(puuid, champ_role):
    try:
        return str(PlayerInfo.query.filter_by(puuid=puuid).first().blob[champ_role])
    except:
        # todo use constant(12)
        return "[[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0]"


def determine_level_image(level):
    if 30 <= level < 50:
        return 30
    elif level >= 500:
        return 500
    return (level // 25) * 25
