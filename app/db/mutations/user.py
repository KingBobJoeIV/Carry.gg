from app.db import db
from app.db.mutations.util import commit
from app.db.schemas import User
from app.models.user import UserIn

# pylint: disable=E1101


def _create(col, batch, return_json):
    js = col.as_json
    db.session.add(col)
    if not batch:
        commit()
    return col if not return_json else js


def create_user(user_model: UserIn, batch=False, return_json=False):
    u = user_model
    col = User(name=u.name, user=u.user, password_hash=u.password_hash)
    return _create(col, batch, return_json)
