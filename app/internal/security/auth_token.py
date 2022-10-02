"""Decorators that ensure authentication is provided
"""
from app.db.queries.user import get_user_by_id, get_user_by_username
from app.exceptions import AppException
from app.internal.constants import REFRESH_TOKEN_SALT
from flask import request
from werkzeug.datastructures import Headers

from .danger import ACCESS_TOKEN, REFRESH_TOKEN, create_token
from .danger import check_password_hash as check
from .danger import decode_token as decode
from .danger import generate_password_hash


def regenerate_access_token(refresh: dict) -> dict:
    user_id = refresh.get("user_id")
    integrity = refresh.get("integrity")
    data = get_user_by_id(user_id)
    is_admin = data.is_admin
    username = data.user
    current = get_integrity(data.id_, data.password_hash)
    if check(integrity, current):
        return (
            issue_access_token(user_id, username, is_admin),
            issue_refresh_token(user_id, data.password_hash),
        )
    return None, None


def issue_access_token(user_id: str, username: str, is_admin: bool):
    return {
        "token_type": ACCESS_TOKEN,
        "user_id": user_id,
        "user": username,
        "is_admin": is_admin,
    }


def issue_refresh_token(user_id, password_hash):
    return {
        "token_type": REFRESH_TOKEN,
        "user_id": user_id,
        "integrity": generate_password_hash(get_integrity(user_id, password_hash)),
    }


def get_integrity(user_id: str, password_hash: str):
    return f"{user_id}{REFRESH_TOKEN_SALT}{password_hash}"


def get_token(strict=True):
    headers = request.headers
    received_access_token = get_bearer_token(headers)

    if not received_access_token:
        if strict:
            raise AppException("No authentication provided")
        return None
    try:
        access = decode(received_access_token)
    except Exception:
        if strict:
            raise AppException("invalid token")
        return None

    if access is None:
        if strict:
            raise AppException("refresh")
        return None

    return access


def get_bearer_token(headers: Headers) -> str:
    auth = headers.get("Authorization", "")
    # count= 1 as in the rare case that the bearer token itself has the word Bearer in it we want it intact
    return auth.replace("Bearer", "", 1).strip()


def authenticate(user: str, password: str):
    user_data = get_user_by_username(user)
    pw_hash = user_data.password_hash
    if not check(pw_hash, password):
        raise AppException("Incorrect Password", code=401)
    username = user_data.user
    is_admin = user_data.is_admin
    access_token = create_token(issue_access_token(user_data.id_, username, is_admin))
    refresh_token = create_token(issue_refresh_token(username, pw_hash))
    return access_token, refresh_token, user_data