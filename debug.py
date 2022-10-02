from set_env import setup_env

setup_env()
# pylint: disable=unused-wildcard-import
from app.main import *
from app.db import db
from app.db.schemas import *
from app.models.user import *

app.app_context().push()