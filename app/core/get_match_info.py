import datetime
import math
import time

from humanfriendly import format_timespan
from sqlalchemy import or_
from sqlalchemy.orm.attributes import flag_modified
from app.db import db
from app.db.schemas import PlayerInfo
from . import constants, calculate_weights, get_account_info
# from calculate_weights import create_blob_entry, update_blob_entry
# from get_account_info import get_all_mastery, get_rank_info, get_info
from .watcher import lol_watcher


# todo can be more efficient with shared matches(save matches with val len > 1)
# todo maybe thread this? lol
# gets all matches that need to be processed and # of matches
def get_matches_for_pred(puuids, times):
    res = {}
    total = 0
    for i in range(len(puuids)):
        if times[i] is not None:
            temp = get_all_matches(puuids[i], times[i])
        else:
            temp = get_all_matches(puuids[i])
        total += len(temp)
        for t in temp:
            if t not in res:
                res[t] = []
            res[t].append(puuids[i])
    return res, total


# get all ranked matches from current season
def get_all_matches(puuid, beg=constants.SZN_START):
    start = 0
    total = []
    while True:
        r = get_matches(puuid, beg, start, 100)
        if not r:
            break
        total.extend(r)
        start += 100
    total = list(set(total))
    print(len(total), "matches fetched")
    return total


# returns 100 ranked matches
def get_matches(puuid, startTime, start=0, count=100):
    return lol_watcher.match.matchlist_by_puuid(constants.REGION, puuid, start_time=startTime, start=start, count=count, queue=420)


def get_match_by_id(matchid):
    return lol_watcher.match.by_id(constants.REGION, matchid)


def get_live_match(id):
    return lol_watcher.spectator.by_summoner(constants.MY_REGION, id)


# returns match info for one match
def get_stats_from_match(match, puuid):
    def stat_by_time(stat, time=match.gameDuration):
        return stat / time
    participant = get_participant(puuid, match)
    # kills, deaths, assists, cs/min, win
    return [participant.kills, participant.deaths, participant.assists,
            stat_by_time(participant.neutralMinionsKilled + participant.totalMinionsKilled), participant.win]
    # todo choose which cols are relevant and return values(APPLY FUNCTIONS eg. by min)
    # order: kills, deaths, assists, cs/min, win, gold/min, vision/min, %of game spent dead, dmg/min, damage taken/min
    # return [match.kills, match.deaths, match.assists, stat_by_time(match.neutralMinionsKilled + match.totalMinionsKilled),
    #         match.win, stat_by_time(match.goldEarned), stat_by_time(match.visionScore), stat_by_time(match.totalTimeSpentDead),
    #         stat_by_time(match.totalDamageDealtToChampions), stat_by_time(match.totalDamageTaken)]


# returns the participant info in a given match object
def get_participant(id, match):
    for p in match["info"]["participants"]:
        if p["summonerId"] == id:
            return p


# given blobs for a player, store in db
def store_blobs_in_db(matchlist, blobs, puuid):
    print("trying to store:", puuid, "started at:", str(datetime.datetime.fromtimestamp(time.time())))
    to_store = calculate_weights.merge_blobs(blobs)
    info = PlayerInfo.query.filter_by(puuid=puuid).first()
    if not info:
        curr = get_account_info.get_info(puuid)
        mastery = get_account_info.get_all_mastery(curr["id"])[0]
        league = get_account_info.get_rank_info(curr["id"])
        if not league:
            league = []
        row = PlayerInfo(curr, mastery, league, to_store, {matchlist[i]: True for i in range(len(matchlist))})
        curr["revisionDate"] = math.floor(time.time() * 1000)
        db.session.add(row)
        print("new row created for:", curr["name"])
    else:
        to_store = calculate_weights.merge_blobs([to_store, info.blob])
        setattr(info, "revisionDate", math.floor(time.time() * 1000))
        setattr(info, "blob", to_store)
        setattr(info, "matchlist", calculate_weights.merge_dicts(info.matchlist, {matchlist[i]: True for i in range(len(matchlist))}))
        flag_modified(info, "revisionDate")
        flag_modified(info, "blob")
        flag_modified(info, "matchlist")
    db.session.commit()
    print("stored:", puuid, "at:", str(datetime.datetime.fromtimestamp(time.time())))


# generate matchid, blob for given player
def process_match(match, puuid):
    matchid = match
    # print("trying to process:", matchid, "started at:", str(datetime.datetime.fromtimestamp(time.time())))
    match = get_match_by_id(matchid)
    puuids = match["metadata"]["participants"]
    ind = puuids.index(puuid)
    participants = match["info"]["participants"]
    champ_role = str(participants[ind]["championId"]) + ", " + participants[ind]["teamPosition"]
    if match["info"]["gameDuration"] <= 240:
        print(matchid, "was a remake")
        return {champ_role: [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0]}
    elif "challenges" not in participants[ind]:
        print("no challenges for:", matchid)
        return {champ_role: [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 0]}
    # print("processed:", matchid, "at:", str(datetime.datetime.fromtimestamp(time.time())))
    return calculate_weights.create_blob_entry(champ_role, participants[ind], match["info"]["teams"][ind // 5])


# given all matches for a pred, divide evenly across threads
def split_into_threads(mapping, total, split):
    print(total, "games to split across", split, "threads")
    # split = 5 for now
    count = 0
    # number of matches per thread; last thread takes remainder
    div = total // split
    if div == 0:
        res = {}
        k = list(mapping.keys())[0]
        for puuid in mapping[k]:
            if puuid not in res:
                res[puuid] = []
            res[puuid].append(k)
        return [res]
    res = [{} for _ in range(split)]
    for k in mapping.keys():
        for puuid in mapping[k]:
            # thread that handles this match
            ind = min((count // div), split - 1)
            if puuid not in res[ind]:
                res[ind][puuid] = []
            res[ind][puuid].append(k)
            count += 1
    return res


# call the process_match function on dict
def process_by_thread(matches, q):
    # given: {"id1": [g1, g2], "id2": [g1]}
    res = {}
    for puuid in matches.keys():
        res[puuid] = [[], []]
        for match in matches[puuid]:
            res[puuid][0].append(match)
            res[puuid][1].append(process_match(match, puuid))
    # return: {"id1": [[g1, g2], [blob1, blob2]], "id2": [[g1], [blob1]]}
    q.put(res)


# given res of all threads, reduce into 1 dict
def join_threads(all_res):
    final = {}
    for res in all_res:
        for k in res.keys():
            if k not in final:
                final[k] = res[k]
            else:
                final[k] = [final[k][0] + res[k][0], final[k][1] + res[k][1]]
    return final


def check_if_in_game(id):
    try:
        game = lol_watcher.spectator.by_summoner(constants.MY_REGION, id)
        # need to check if it's ranked
        if game["gameQueueConfigId"] != 420:
            return False
        return True
    except Exception as e:
        print(e)
        return False


def calculate_game_time(start, duration):
    start = int(start)
    start /= 1000
    duration = int(duration)
    current = time.time()
    diff = current - (start + duration)
    res = format_timespan(duration)
    return time_since_game(diff), res.replace(" hours", "h").replace(" minutes", "m").replace("and", "").replace(
        " seconds", "s")


def time_since_game(seconds):
    # months
    if seconds >= 2628288:
        months = seconds // 2628288
        if months == 1:
            return "1 month ago"
        return str(int(months)) + " months ago"
    elif seconds >= 604800:
        weeks = seconds // 604800
        if weeks == 1:
            return "1 week ago"
        return str(int(weeks)) + " weeks ago"
    elif seconds >= 86400:
        days = seconds // 86400
        if days == 1:
            return "1 day ago"
        return str(int(days)) + " days ago"
    elif seconds >= 3600:
        hours = seconds // 3600
        if hours == 1:
            return "1 hour ago"
        return str(int(hours)) + " hours ago"
    else:
        minutes = seconds // 60
        if minutes == 1:
            return "1 minute ago"
        return str(int(minutes)) + " minutes ago"
