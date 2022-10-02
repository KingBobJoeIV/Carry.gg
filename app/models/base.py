from typing import Optional
from pydantic import BaseModel


class CustomBase(BaseModel):
    @classmethod
    def from_db(cls, db):
        return cls(**db.as_json)
