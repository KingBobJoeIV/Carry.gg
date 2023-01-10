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
