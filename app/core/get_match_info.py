import datetime
import time

from humanfriendly import format_timespan
from sqlalchemy import or_
from sqlalchemy.orm.attributes import flag_modified
from app.db import db
from app.db.schemas import BetterGame, PlayerInfo
from . import constants, calculate_weights, get_account_info
# from calculate_weights import create_blob_entry, update_blob_entry
# from get_account_info import get_all_mastery, get_rank_info, get_info
from .watcher import lol_watcher


# get all ranked matches from current season
def get_all_matches(puuid):
    start = 0
    total = []
    while True:
        r = get_matches(puuid, constants.SZN_START, start, 100)
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


def store_match_in_db(match):
    # get individual participant info
    matchid = match
    print("trying to store:", matchid, "started at:", str(datetime.datetime.fromtimestamp(time.time())))
    match = get_match_by_id(matchid)
    puuids = match["metadata"]["participants"]
    participants = match["info"]["participants"]
    # account_fields = ["accountId", "profileIconId", "revisionDate", "name", "id",
    #                   "puuid", "summonerLevel", "championId", "championPoints",
    #                   "championLevel", "tier", "rank", "leaguePoints", "wins", "losses", "blob", "matchlist"]
    count = 0
    for puuid in puuids:
        curr = get_account_info.get_info(puuid)
        info = PlayerInfo.query.filter_by(puuid=puuid).first()
        if count < 5:
            team = match["info"]["teams"][0]
        else:
            team = match["info"]["teams"][1]
        # new player in db
        if not info:
            champ_role = str(participants[count]["championId"]) + ", " + participants[count]["teamPosition"]
            mastery = get_account_info.get_all_mastery(curr["id"])[0]
            league = get_account_info.get_rank_info(curr["id"])
            if not league:
                league = []
            blob = calculate_weights.create_blob_entry(champ_role, participants[count], team)
            row = PlayerInfo(curr, mastery, league, blob, {matchid: True})
            db.session.add(row)
        else:
            # add match if not already in player's matchlist
            if matchid not in info.matchlist:
                champ_role = str(participants[count]["championId"]) + ", " + participants[count]["teamPosition"]
                blob = calculate_weights.create_blob_entry(champ_role, participants[count], team)
                temp = info.matchlist
                if champ_role in info.blob:
                    temp_blob = calculate_weights.update_blob_entry(champ_role, blob, info.blob)
                else:
                    temp_blob = info.blob
                    temp_blob[champ_role] = blob[champ_role]
                temp[matchid] = True
                print("Adding match to: ", curr["name"])
                setattr(info, "blob", temp_blob)
                setattr(info, "matchlist", temp)
                flag_modified(info, "blob")
                flag_modified(info, "matchlist")
                db.session.commit()
        count += 1
    db.session.commit()
    print("stored:", matchid, "at:", str(datetime.datetime.fromtimestamp(time.time())))


def get_stored_by_champ_role(participant, champ_role):
    role = champ_role.split(",")[1]
    print("Role:", role)
    if role == " TOP":
        return BetterGame.query.filter(or_(BetterGame.participantOne == participant, BetterGame.participantOneChamp == champ_role),
                                       or_(BetterGame.participantSix == participant, BetterGame.participantSixChamp == champ_role)).all()
    elif role == " JUNGLE":
        return BetterGame.query.filter(or_(BetterGame.participantTwo == participant, BetterGame.participantTwoChamp == champ_role),
                                       or_(BetterGame.participantSeven == participant, BetterGame.participantSevenChamp == champ_role)).all()
    elif role == " MID":
        return BetterGame.query.filter(or_(BetterGame.participantThree == participant, BetterGame.participantThreeChamp == champ_role),
                                       or_(BetterGame.participantEight == participant, BetterGame.participantEightChamp == champ_role)).all()
    elif role == " BOTTOM":
        return BetterGame.query.filter(or_(BetterGame.participantFour == participant, BetterGame.participantFourChamp == champ_role),
                                       or_(BetterGame.participantNine == participant, BetterGame.participantNineChamp == champ_role)).all()
    elif role == " UTILITY":
        return BetterGame.query.filter(or_(BetterGame.participantFive == participant, BetterGame.participantFiveChamp == champ_role),
                                       or_(BetterGame.participantTen == participant, BetterGame.participantTenChamp == champ_role)).all()


def update_matches(matchlist):
    for match in matchlist:
        info = BetterGame.query.filter_by(match_id=str(match)).first()
        # if match is not in db
        if not info:
            store_match_in_db(get_match_by_id(match))


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
