from flask import Blueprint, render_template, request, current_app, stream_with_context
from app.decorators.api_response import api
from app.core.predict import predict, get_account_info, make_path
from app.core.update import update
from app.core.get_account_info import get_all_mastery, get_rank_info, determine_level_image
from app.core.get_match_info import check_if_in_game, calculate_game_time, get_live_match
from app.imageinfo import imageinfo
from app.db import db
from app.db.schemas import PredictInfo, PlayerInfo
from threading import Thread
from time import sleep, time
import json
import app.core.constants
from pathlib import Path
from app.imageinfo.imageinfo import skin_info
router = Blueprint("predict", __name__, url_prefix="/predict")

# not in use
# @router.get("/<ign>")
# @api.none
# def predict_route(ign):
#     return predict(ign)

# not in use
# @router.get("/update/<ign>")
# @api.none
# def update_route(ign):
#     return update(ign)

# not in use
# @router.get("/account-info/<ign>")
# @api.none
# def get_acc_info(ign):
#     return get_account_info.store_account_in_db(get_account_info.get_info_by_ign(ign)["puuid"])

# problem with name changes don't use!
# @router.get("update-all")
# @api.none
# def update_all_accounts():
#     return update_account_table()


@router.get("/home/riot.txt")
def riot_verify():
    return render_template("riot.txt")


@router.get("/home")
def home_page():
    if app.core.constants.home is None:
        app.core.constants.home = True
        skin_info()
        get_account_info.map_id_to_champ()
    return render_template("home.html")


def profile_page(ign):
    # make sure cache exists
    print("loaded!")
    check_pending()
    update_info = update(ign)
    print("updated!")
    if update_info == "toolow":
        return render_template("unranked.html", ign=ign)
    elif update_info == "notfound":
        return render_template("pageNotFound.html", ign=ign)
    elif update_info == "servererror":
        return render_template("500.html")
    hide = False
    pending = ""
    thread = False
    # predict live game on diff thread
    if request.args.get("_in_game"):
        thread = True
        predict_live(ign)
    prof = get_account_info.get_info_by_ign(ign)
    # past/live predictions
    predictions = PredictInfo.query.filter(PredictInfo.ids.contains(prof["id"])).all()
    pred = []
    # todo game
    for p in predictions:
        game_info = p.gameDuration
        if game_info == 0:
            game_info = ["In Progress", ""]
        else:
            game_info = calculate_game_time(p.gameStartTimestamp, p.gameDuration)
        players = p.ids.strip('][').split(',')
        count = 0
        team1 = []
        team2 = []
        for player in players:
            player = player.replace("'", "").replace(" ", "")
            if count < 5:
                team1.append(PlayerInfo.query.filter_by(id=player).first().name)
            else:
                team2.append(PlayerInfo.query.filter_by(id=player).first().name)
            count += 1
            color = "#c04840cc"
            if p.actualWinner == "Pending":
                color = "#7d7d7dcc"
            elif p.predictedWinner == p.actualWinner:
                color = "#07963e99"
        if game_info == 0:
            pred.append((float("-inf"), [game_info, team1, team2, p.predictedWinner, p.actualWinner,
                                  str(round(p.predictedChance * 100, 2)) + "%", color]))
        else:
            pred.append((-int(p.gameStartTimestamp), [game_info, team1, team2, p.predictedWinner, p.actualWinner,
                                        str(round(p.predictedChance * 100, 2)) + "%", color]))
    pred.sort(key=lambda x: x[0])
    for i in range(len(pred)):
        pred[i] = pred[i][1]
    # give enough time for the pending prediction thread to put game in cache
    if thread:
        sleep(2)
    # not in game
    if not check_if_in_game(prof["id"]):
        hide = True
        print("not ingame")
    # in game
    else:
        live_id = get_live_match(prof["id"])["gameId"]
        in_db = PredictInfo.query.filter(PredictInfo.match_id == str(live_id)).first()
        # check if prediction is pending(calculation)
        file = make_path(live_id)
        if file.is_file():
            print("calculating")
            pending = "calculating"
            hide = True
        # check if prediction is pending(ingame)
        elif in_db is not None and in_db.actualWinner == "Pending":
            print("waiting")
            hide = True
            pending = "waiting"
    mastery = get_all_mastery(prof["id"])[0]
    skin = imageinfo.randomize_skins_by_champ(app.core.constants.CHAMPION_MAPPING[mastery["championId"]])
    league = get_rank_info(prof["id"])
    if not league:
        league = {"tier": "UNRANKED", "rank": "", "leaguePoints": 0, "wins": 0, "losses": 0}

    # determine which border image to use
    level = prof["summonerLevel"]
    img_level = determine_level_image(level)
    print("hide", hide, "pending", pending)
    return render_template("profile.html", ign=prof["name"], icon=prof["profileIconId"], img_level=img_level,
                           level=level, championName=app.core.constants.CHAMPION_MAPPING[mastery["championId"]], skin=skin,
                           championPoints=mastery["championPoints"], championLevel=mastery["championLevel"],
                           tier=league["tier"], rank=league["rank"], leaguePoints=league["leaguePoints"],
                           wins=league["wins"], losses=league["losses"], hide=hide, pred=pred, pending=pending)


@router.get("/profile/<ign>")
def prof_page(ign):
    return stream_with_context(profile_page(ign))


@router.get("/profile/<ign>?_in_game=1")
def redirect_to_prof(ign):
    return stream_with_context(profile_page(ign))


def check_pending():
    if app.core.constants.home is None:
        app.core.constants.home = True
        skin_info()
        get_account_info.map_id_to_champ()


def predict_live(ign):
    t = Thread(target=predict, args=(ign, current_app._get_current_object()))
    t.start()
