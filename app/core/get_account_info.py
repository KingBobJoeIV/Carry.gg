from . import constants
from .watcher import lol_watcher
from app.db import db
from app.db.schemas import AccountInfo
import json
from pathlib import Path
from app.internal.caching.response_caching import cache
import time
import math


# todo needs to be updated every patch
# @cache
def map_id_to_champ():
    p=Path("./app/ddragon_12_20_1_champ_data.json").resolve()
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
    return lol_watcher.league.by_summoner(constants.MY_REGION, summonerId)


def get_mastery_for_champ(summonerId, championId):
    return lol_watcher.champion_mastery.by_summoner_by_champion(constants.MY_REGION, summonerId, championId)["championPoints"]


def get_all_mastery(summonerId):
    return lol_watcher.champion_mastery.by_summoner(constants.MY_REGION, summonerId)


def store_account_in_db(puuid):
    account_fields = ["accountId", "profileIconId", "revisionDate", "name", "id",
                      "puuid", "summonerLevel", "championId", "championPoints",
                      "championLevel", "tier", "rank", "leaguePoints", "wins", "losses"]
    curr = get_info(puuid)
    # replace revisionDate with current time
    curr["revisionDate"] = math.floor(time.time() * 1000)
    info = AccountInfo.query.filter_by(puuid=puuid).first()
    # print(curr["revisionDate"], info.revisionDate)
    # print(curr["revisionDate"] - info.revisionDate)
    if not info:
        mastery = get_all_mastery(curr["id"])[0]
        league = get_rank_info(curr["id"])
        if not league:
            league = []
        elif league[0]["queueType"] == "RANKED_FLEX_SR":
            league = league[1]
        else:
            league = league[0]
        row = AccountInfo(curr, mastery, league)
        db.session.add(row)
    # if it has been at least 2 minutes since last update, update info
    elif curr["revisionDate"] - info.revisionDate > 120000:
        mastery = get_all_mastery(curr["id"])[0]
        league = get_rank_info(curr["id"])
        if not league:
            league = []
        elif league[0]["queueType"] == "RANKED_FLEX_SR":
            league = league[1]
        else:
            league = league[0]
        row = AccountInfo(curr, mastery, league)
        print("Updating:", curr["name"])
        for field in account_fields:
            setattr(info, field, getattr(row, field))
    db.session.commit()
    return (info or row).as_json


def determine_level_image(level):
    if 30 <= level < 50:
        return 30
    elif level >= 500:
        return 500
    return (level // 25) * 25
