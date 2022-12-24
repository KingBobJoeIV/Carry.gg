from .watcher import lol_watcher
from . import constants, get_match_info
import numpy as np
from app.internal.caching.response_caching import cache


# todo this is unused
@cache(lambda x, y: x + y, json_cache=True)
def mby_id(region, match):
    print(region, match)
    a = lol_watcher.match.by_id(region, match)
    return a


def calculate_weights(matches, puuid):
    datas = []
    count = 0
    for match in matches:
        datas.append(np.array(get_match_info.get_stats_from_match(match, puuid)))
        count += 1
    data = sum(datas)
    if not datas:
        return [0, 1, 0, 0, 0]
    return [x / count for x in data]


# todo account for all stats
def normalize_stats(data):
    data[0] = min(data[0] / constants.MASTERY_BINS, 1)
    data[1] = min(data[1] / constants.KILL_BINS, 1)
    data[2] = min(data[2] / constants.DEATH_BINS, 1)
    data[3] = min(data[3] / constants.ASSIST_BINS, 1)
    data[4] = min(data[4] / constants.CS_BINS, 1)
    data[5] = int(data[5])  # convert boolean value of winner
    # data[6] = min(data[6] / constants.GOLD_BINS, 1)
    # data[7] = min(data[7] / constants.VISION_BINS, 1)
    # data[8] = min(data[8] / constants.TIME_DEAD_BINS, 1)
    # data[9] = min(data[9] / constants.TOTAL_DMG_BINS, 1)
    # data[10] = min(data[10] / constants.TOTAL_DMG_TAKEN_BINS, 1)
    return data


# todo account for all stats
def bin_stats(data):
    # mastery (7 bins)
    mastery_bins = np.array([100, 1000, 10000, 50000, 100000, 250000])
    data[0] = np.digitize(data[0], mastery_bins)
    # kills (11 bins)
    kill_bins = np.array([3, 6, 9, 12, 15, 18, 21, 24, 27, 30])
    data[1] = np.digitize(data[1], kill_bins)
    # deaths (11 bins)
    death_bins = np.array([2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
    data[2] = np.digitize(data[2], death_bins)
    # assists (11 bins)
    assist_bins = np.array([4, 8, 12, 16, 20, 24, 28, 32, 36, 40])
    data[3] = np.digitize(data[3], assist_bins)
    # cs/min (13 bins)
    cs_bins = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    data[4] = np.digitize(data[4], cs_bins)
    # no bin for win(bool)
    # data[6] = ...
    # vision/min (9 bins)
    # data[7] = np.array([.25, .5, .75, 1, 1.25, 1.5, 1.75, 2])
    # data[8] = ...
    # data[9] = ...
    # data[10] = ...
    return data


def normalize_rank(rank, tier, lp):
    res = 13
    if rank == "IRON":
        res = .5
    elif rank == "BRONZE":
        res = 1
    # todo not sure
    elif rank == "SILVER" or rank == "UNRANKED":
        res = 2
    elif rank == "GOLD":
        res = 4
    elif rank == "PLATINUM":
        if tier == "IV" or tier == "III":
            res = 6
        else:
            res = 8
    elif rank == "DIAMOND":
        if tier == "IV" or tier == "III":
            res = 9
        else:
            res = 12
    else:
        res += (lp // 200)
    return min(res / constants.RANK_BINS, 1)


def create_blob_entry(champ_role, data, team_data):
    # key = champ_role, val = [participant data, count]
    return {champ_role: [transform_data(data, team_data), 1]}


def merge_blobs(blobs):
    res = {}
    for blob in blobs:
        for k in blob.keys():
            if k not in res:
                res[k] = blob[k]
            else:
                res[k] = [[(res[k][0][i] + blob[k][0][i])/(res[k][1]+1) for i in range(len(blob[k][0]))], res[k][1]+1]
    return res


def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


# todo
# towers,inhibs,first_inhib,dragons,barons,first_baron,kda,first_tower,heralds,first_drag,first_herald,fb,neutralMinionsKilled
# damageDealtToBuildings(maybe cut out)
# damageDealtToTurrets(maybe cut out)
# visionScore
# totalUnitsHealed
# totalMinionsKilled
# timeccingothers
# totaltimeccdealt
def transform_data(data, team_data):
    towers = team_data["objectives"]["tower"]["kills"]
    inhibs = team_data["objectives"]["inhibitor"]["kills"]
    first_inhib = int(team_data["objectives"]["inhibitor"]["first"])
    dragons = team_data["objectives"]["dragon"]["kills"]
    barons = team_data["objectives"]["baron"]["kills"]
    kda = data["challenges"]["kda"]
    first_tower = int(team_data["objectives"]["tower"]["first"])
    heralds = team_data["objectives"]["riftHerald"]["kills"]
    first_drag = int(team_data["objectives"]["dragon"]["first"])
    first_herald = int(team_data["objectives"]["riftHerald"]["first"])
    fb = int(team_data["objectives"]["champion"]["first"])
    neutralMinionsKilled = data["neutralMinionsKilled"]
    return [towers, inhibs, first_inhib, dragons, barons, kda, first_tower, heralds, first_drag, first_herald, fb,
            neutralMinionsKilled]
