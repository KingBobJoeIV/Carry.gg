from flask import Blueprint, render_template, request,current_app,stream_with_context
from app.decorators.api_response import api
from app.core.predict import predict, get_account_info
from app.core.update import update, update_account_table
from app.core.get_account_info import get_all_mastery, get_rank_info, determine_level_image
from app.core.get_match_info import check_if_in_game, calculate_game_time
from app.imageinfo import imageinfo
from app.db import db
from app.db.schemas import PredictInfo, AccountInfo, GameInfo
from threading import Thread
from time import sleep
import json
router = Blueprint("predict", __name__, url_prefix="/predict")



@router.get("/<ign>")
@api.none
def predict_route(ign):
    return predict(ign)


@router.get("/update/<ign>")
@api.none
def update_route(ign):
    return update(ign)


@router.get("/account-info/<ign>")
@api.none
def get_acc_info(ign):
    return get_account_info.store_account_in_db(get_account_info.get_info_by_ign(ign)["puuid"])

# todo problem with name changes don't use!
# @router.get("update-all")
# @api.none
# def update_all_accounts():
#     return update_account_table()


@router.get("/home")
def home_page():
    return render_template("home.html")


def profile_page(ign):
    # todo change location
    mapping = get_account_info.map_id_to_champ()
    update_info = update(ign)
    if update_info == "toolow":
        return render_template("unranked.html", ign=ign)
    elif update_info == "notfound":
        return render_template("pageNotFound.html", ign=ign)
    hide = False
    yield "<!DOCTYPE html>"
    if request.args.get("_in_game"):
        t=Thread(target=predict,args=(ign,current_app._get_current_object()))
        t.start()
        while t.is_alive():
            yield b" "
            sleep(1)
        hide = True
        # todo this
        # # declare cache somewhere? idk
        # # need to use lru
        # # need to check top element on 1 second intervals
        # if ign not in cache:
        #     predict(ign)
        #     cache[live_match_id] = currentTime + 2 min
        #     hide = True
        # else:
        #     # popup saying request already in progress/complete

    prof = get_account_info.get_info_by_ign(ign)
    # past/live predictions
    predictions = PredictInfo.query.filter(PredictInfo.ids.contains(prof["id"])).all()
    pred = []
    for p in predictions:
        game = GameInfo.query.filter_by(matchId="NA1_" + p.match_id).first()
        if not game:
            game_info = ["In Progress", ""]
        else:
            game_info = calculate_game_time(game.gameStartTimestamp, game.gameDuration)
        players = p.ids.strip('][').split(',')
        count = 0
        team1 = []
        team2 = []
        for player in players:
            player = player.replace("'", "").replace(" ", "")
            if count < 5:
                team1.append(AccountInfo.query.filter_by(id=player).first().name)
            else:
                team2.append(AccountInfo.query.filter_by(id=player).first().name)
            count += 1
            color = "#c04840cc"
            if p.actualWinner == "Pending":
                color = "#7d7d7dcc"
            elif p.predictedWinner == p.actualWinner:
                color = "#079a3bcc"
        pred.append([game_info, team1, team2, p.predictedWinner, p.actualWinner,
                     str(round(p.predictedChance * 100, 2)) + "%", color])

    if not check_if_in_game(prof["id"]):
        hide = True
    mastery = get_all_mastery(prof["id"])[0]
    # todo change location
    imageinfo.skin_info()
    skin = imageinfo.randomize_skins_by_champ(mapping[mastery["championId"]])

    league = get_rank_info(prof["id"])
    if not league:
        league = {"tier": "UNRANKED", "rank": "", "leaguePoints": 0, "wins": 0, "losses": 0}
    elif league[0]["queueType"] == "RANKED_FLEX_SR":
        league = league[1]
    else:
        league = league[0]

    # determine which border image to use
    level = prof["summonerLevel"]
    img_level = determine_level_image(level)
    yield render_template("profile.html", ign=prof["name"], icon=prof["profileIconId"], img_level=img_level,
                           level=level, championName=mapping[mastery["championId"]], skin=skin,
                           championPoints=mastery["championPoints"], championLevel=mastery["championLevel"],
                           tier=league["tier"], rank=league["rank"], leaguePoints=league["leaguePoints"],
                           wins=league["wins"], losses=league["losses"], hide=hide, pred=pred)


@router.get("/profile/<ign>")
def prof__page(ign):
    return stream_with_context(profile_page(ign))