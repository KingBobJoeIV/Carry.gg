from app.internal.constants import STATIC_DIR
from flask import send_from_directory

ONE_YEAR_IN_SECONDS = 365 * 86400


def send_static_file(file_name: str, max_age=ONE_YEAR_IN_SECONDS):
    return send_from_directory(STATIC_DIR, file_name, max_age=max_age)
