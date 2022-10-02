from app.internal.helpers.guard import guard
from app.internal.helpers import sanitize
from ..schemas.user import User


message = "User does not exist"


def get_user_by_username(idx: str) -> User:
    if sanitize(idx) != idx or not idx:
        return guard(None, message)
    return guard(User.query.filter_by(user=idx).first(), message)


def get_user_by_id(idx: str) -> User:
    return guard(User.query.filter_by(id_=idx).first(), message)
