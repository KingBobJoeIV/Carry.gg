from app.db import db
from app.db.errors import check_integrity_error

# pylint: disable=E1101
def commit():
    try:
        db.session.commit()
    except Exception as e:
        check_integrity_error(e)
