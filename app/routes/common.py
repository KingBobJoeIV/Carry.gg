from flask import Blueprint
from app.internal.helpers import send_static_file

router = Blueprint("common", __name__)


@router.get("/favicon.ico")
def favicon():
    return send_static_file("favicon.ico")


@router.get("/robots.txt")
def robots():
    return send_static_file("robots.txt")