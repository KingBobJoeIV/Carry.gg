from secrets import token_urlsafe
from time import time

from sqlalchemy.dialects.postgresql import TEXT

from ..base import db


class User(db.Model):
    # pylint: disable=E1101
    id_: str = db.Column(TEXT, unique=True, nullable=False, primary_key=True)
    user: str = db.Column(db.String(50), unique=True, nullable=False)
    name: str = db.Column(db.String(100), nullable=False)
    password_hash: str = db.Column(TEXT, nullable=False)
    created_at: int = db.Column(db.Integer)
    is_admin: bool = db.Column(db.Boolean, default=False)
    # pylint: enable=E1101

    def __init__(
        self,
        user: str = None,
        name: str = None,
        password_hash: str = None,
    ):
        self.id_ = token_urlsafe(20)
        self.user = user.lower()
        self.name = name
        self.password_hash = password_hash
        self.created_at = time()

    @property
    def as_json(self):
        return {
            "id_": self.id_,
            "name": self.name,
            "user": self.user,
            "created_at": self.created_at,
            "is_admin": self.is_admin,
            "_secure_": {},
        }
