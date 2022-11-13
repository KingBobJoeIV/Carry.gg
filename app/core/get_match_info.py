from .watcher import lol_watcher
from . import constants
from app.db import db
from app.db.schemas import BetterGame
import time
from humanfriendly import format_timespan
from sqlalchemy import or_


# get all ranked matches # todo of season
def get_all_matches(puuid):
    start = 0
    total = []
    while True:
        r = get_matches(puuid, start)
        if not r:
            break
        total.extend(r)
        start += 100
    total = list(set(total))
    print(len(total), "matches fetched")
    return total


# returns 100 ranked matches
def get_matches(puuid, start=0):
    return lol_watcher.match.matchlist_by_puuid(constants.REGION, puuid, start=start, count=100, queue=420)


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
    # get general game info
    id = match["metadata"]["matchId"]
    duration = match["info"]["gameDuration"]
    start = match["info"]["gameStartTimestamp"]
    version = match["info"]["gameVersion"]
    # get individual participant info
    puuids = match["metadata"]["participants"]
    participants = match["info"]["participants"]
    champ_roles = []
    for p in participants:
        champ_roles = p["championId"] + ", " + p["teamPosition"]
    row = BetterGame(id, start, duration, version, puuids, champ_roles, participants)
    db.session.add(row)
    db.session.commit()


def get_stored_by_champ_role(participant, champ_role):
    return BetterGame.query.filter_by(BetterGame.puuid == participant,
                                      or_(BetterGame.participantOneChamp == champ_role,
                                       BetterGame.participantTwoChamp == champ_role,
                                       BetterGame.participantThreeChamp == champ_role,
                                       BetterGame.participantFourChamp == champ_role,
                                       BetterGame.participantFiveChamp == champ_role,
                                       BetterGame.participantSixChamp == champ_role,
                                       BetterGame.participantSevenChamp == champ_role,
                                       BetterGame.participantEightChamp == champ_role,
                                       BetterGame.participantNineChamp == champ_role,
                                       BetterGame.participantTenChamp == champ_role))


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
