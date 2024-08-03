import numpy as np
import requests
from flask import Blueprint, render_template, request, current_app, stream_with_context, redirect, url_for
from app.decorators.api_response import api
from app.core.predict import predict, get_account_info, make_path
from app.core.update import update
from app.core.get_account_info import get_all_mastery, get_rank_info, determine_level_image, get_info_by_ign
from app.core.get_match_info import check_if_in_game, calculate_game_time, get_live_match, get_match_by_id,\
    format_expected, process_actual
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

@router.get("/")
def redirect_to_home():
    return redirect(url_for("predict.home_page"))


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
    update_msg, account, me = update(ign)
    print("updated!")
    if update_msg == "toolow":
        return render_template("unranked.html", ign=ign)
    elif update_msg == "notfound":
        return render_template("pageNotFound.html")
    elif update_msg == "servererror":
        return render_template("500.html")
    hide = False
    pending = ""
    # past/live predictions
    predictions = PredictInfo.query.filter(PredictInfo.ids.contains(me["id"])).all()
    pred = []
    # todo game
    for p in predictions:
        live = False
        game_info = p.gameDuration
        if game_info == 0:
            game_info = ["In Progress", ""]
            live = True
        else:
            game_info = []
            temp = calculate_game_time(p.gameStartTimestamp, p.gameDuration)
            game_info.append(temp[0])
            game_info.append(temp[1])
            game_info.append(p.match_id)
            print(game_info)
        players = p.ids.strip('][').split(',')
        count = 0
        team1 = []
        team2 = []
        for player in players:
            player = player.replace("'", "").replace(" ", "")
            print(player)
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
        if live:
            pred.append((float("-inf"), [game_info, team1, team2, p.predictedWinner, p.actualWinner,
                                  str(round(p.predictedChance * 100, 2)) + "%", color, live]))
        else:
            pred.append((-int(p.gameStartTimestamp), [game_info, team1, team2, p.predictedWinner, p.actualWinner,
                                        str(round(p.predictedChance * 100, 2)) + "%", color, live]))
    pred.sort(key=lambda x: x[0])
    for i in range(len(pred)):
        pred[i] = pred[i][1]
    # not in game
    if not check_if_in_game(account["puuid"]):
        hide = True
        print("not ingame")
    # in game
    else:
        live_id = get_live_match(account["puuid"])["gameId"]
        in_db = PredictInfo.query.filter(PredictInfo.match_id == str(live_id)).first()
        # check if prediction is pending(calculation)
        file = make_path(live_id)
        if file.is_file():
            print("calculating")
            pending = "calculating"
        # check if prediction is pending(ingame)
        elif in_db is not None and in_db.actualWinner == "Pending":
            print("waiting")
            pending = "waiting"
        else:
            pending = "predict"
            print("prediction not started")
    mastery = get_all_mastery(account["puuid"])[0]
    skin = imageinfo.randomize_skins_by_champ(app.core.constants.CHAMPION_MAPPING[mastery["championId"]])
    league = get_rank_info(me["id"])
    if not league:
        league = {"tier": "UNRANKED", "rank": "", "leaguePoints": 0, "wins": 0, "losses": 0}

    # determine which border image to use
    level = me["summonerLevel"]
    img_level = determine_level_image(level)
    print("hide", hide, "pending", pending)
    return render_template("profile.html", ign=ign, icon=me["profileIconId"], img_level=img_level,
                           level=level, championName=app.core.constants.CHAMPION_MAPPING[mastery["championId"]], skin=skin,
                           championPoints=mastery["championPoints"], championLevel=mastery["championLevel"],
                           tier=league["tier"], rank=league["rank"], leaguePoints=league["leaguePoints"],
                           wins=league["wins"], losses=league["losses"], hide=hide, pred=pred, pending=pending)


@router.get("/profile/<ign>")
def prof_page(ign):
    return stream_with_context(profile_page(ign))


@router.get("/profile/<ign>/live")
def live_game(ign):
    # give it time to create temp file
    sleep(2)
    try:
        puuid = get_info_by_ign(ign)["puuid"]
    except:
        return render_template("pageNotFound.html")
    # not ingame
    if not check_if_in_game(puuid):
        return render_template("notInGame.html", ign=ign)
    # in game
    else:
        match = get_live_match(puuid)
        gameid = match["gameId"]
        print(match)
        in_db = PredictInfo.query.filter(PredictInfo.match_id == str(gameid)).first()
        # check if prediction is pending(calculation)
        file = make_path(gameid)
        if file.is_file():
            print("calculating")
            return render_template("calculatingGame.html")
        # check if prediction is pending(ingame)
        elif in_db is not None and in_db.actualWinner == "Pending":
            print("waiting")
            pending = "waiting"
            team_1 = match["participants"][:4]
            team_2 = match["participants"][5:]
            snapshot = format_expected(PredictInfo.query.filter(PredictInfo.match_id == str(gameid)).first().currentStats)
            snapshot = [format_expected(x) for x in snapshot]
            return render_template("liveGame.html", team_1=team_1, team_2=team_2, gameid=gameid, status=pending, ign=ign,
                                   snapshot=snapshot)
        else:
            print("new predict just started calculating")
            predict_live(match)
            return render_template("calculatingGame.html")


@router.get("/game/<gameid>")
def past_game(gameid):
    try:
        # todo needs to be a prediction in db (add custom template for prediction not done on past game)
        match = get_match_by_id("NA1_" + gameid)
        data = match["info"]
        if data["queueId"] != 420:
            raise Exception
        team_1 = data["participants"][:5]
        team_2 = data["participants"][5:]
        expected = format_expected(PredictInfo.query.filter(PredictInfo.match_id == str(gameid)).first().currentStats)
        expected = [format_expected(x) for x in expected]
        actual = process_actual(match)
        diff = [np.array(actual[i]-np.array(expected[i][0])) for i in range(10)]
        return render_template("pastGame.html", team_1=team_1, team_2=team_2, gameid=gameid, expected=expected,
                               duration=data["gameDuration"]/60, actual=actual, diff=diff)
    except:
        return render_template("pageNotFound.html")


@router.get("/about")
def about():
    return render_template("about.html")

# todo
# @router.get("/")
# def redirect_to_home():
#     return stream_with_context(home_page)


def check_pending():
    if app.core.constants.home is None:
        app.core.constants.home = True
        skin_info()
        get_account_info.map_id_to_champ()


def predict_live(match):
    t = Thread(target=predict, args=(match, current_app._get_current_object()))
    t.start()
