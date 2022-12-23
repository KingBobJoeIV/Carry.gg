from app.db import db


class BetterGame(db.Model):
    # metadata
    match_id: str = db.Column(db.TEXT, primary_key=True)
    gameDuration: int = db.Column(db.Integer)
    gameStartTimestamp: str = db.Column(db.TEXT, nullable=False)
    gameVersion: str = db.Column(db.TEXT, nullable=False)
    win: str = db.Column(db.TEXT, nullable=False)
    # puuids
    participantOne: str = db.Column(db.TEXT, nullable=False)
    participantTwo: str = db.Column(db.TEXT, nullable=False)
    participantThree: str = db.Column(db.TEXT, nullable=False)
    participantFour: str = db.Column(db.TEXT, nullable=False)
    participantFive: str = db.Column(db.TEXT, nullable=False)
    participantSix: str = db.Column(db.TEXT, nullable=False)
    participantSeven: str = db.Column(db.TEXT, nullable=False)
    participantEight: str = db.Column(db.TEXT, nullable=False)
    participantNine: str = db.Column(db.TEXT, nullable=False)
    participantTen: str = db.Column(db.TEXT, nullable=False)
    # champs + role (id, role)
    participantOneChamp: str = db.Column(db.TEXT, nullable=False)
    participantTwoChamp: str = db.Column(db.TEXT, nullable=False)
    participantThreeChamp: str = db.Column(db.TEXT, nullable=False)
    participantFourChamp: str = db.Column(db.TEXT, nullable=False)
    participantFiveChamp: str = db.Column(db.TEXT, nullable=False)
    participantSixChamp: str = db.Column(db.TEXT, nullable=False)
    participantSevenChamp: str = db.Column(db.TEXT, nullable=False)
    participantEightChamp: str = db.Column(db.TEXT, nullable=False)
    participantNineChamp: str = db.Column(db.TEXT, nullable=False)
    participantTenChamp: str = db.Column(db.TEXT, nullable=False)
    # json dumps
    participantOneDump: str = db.Column(db.JSON, nullable=False)
    participantTwoDump: str = db.Column(db.JSON, nullable=False)
    participantThreeDump: str = db.Column(db.JSON, nullable=False)
    participantFourDump: str = db.Column(db.JSON, nullable=False)
    participantFiveDump: str = db.Column(db.JSON, nullable=False)
    participantSixDump: str = db.Column(db.JSON, nullable=False)
    participantSevenDump: str = db.Column(db.JSON, nullable=False)
    participantEightDump: str = db.Column(db.JSON, nullable=False)
    participantNineDump: str = db.Column(db.JSON, nullable=False)
    participantTenDump: str = db.Column(db.JSON, nullable=False)

    def __init__(self, match, start, duration, version, participants, participantChamps, participantDumps):
        # metadata
        self.match_id = match
        self.gameStartTimestamp = start
        self.gameDuration = duration
        self.gameVersion = version
        if participantDumps[0]["win"]:
            self.win = "Team 1"
        else:
            self.win = "Team 2"
        # puuids
        self.participantOne = participants[0]
        self.participantTwo = participants[1]
        self.participantThree = participants[2]
        self.participantFour = participants[3]
        self.participantFive = participants[4]
        self.participantSix = participants[5]
        self.participantSeven = participants[6]
        self.participantEight = participants[7]
        self.participantNine = participants[8]
        self.participantTen = participants[9]
        # champs + role
        self.participantOneChamp = participantChamps[0]
        self.participantTwoChamp = participantChamps[1]
        self.participantThreeChamp = participantChamps[2]
        self.participantFourChamp = participantChamps[3]
        self.participantFiveChamp = participantChamps[4]
        self.participantSixChamp = participantChamps[5]
        self.participantSevenChamp = participantChamps[6]
        self.participantEightChamp = participantChamps[7]
        self.participantNineChamp = participantChamps[8]
        self.participantTenChamp = participantChamps[9]
        # json dumps
        self.participantOneDump = participantDumps[0]
        self.participantTwoDump = participantDumps[1]
        self.participantThreeDump = participantDumps[2]
        self.participantFourDump = participantDumps[3]
        self.participantFiveDump = participantDumps[4]
        self.participantSixDump = participantDumps[5]
        self.participantSevenDump = participantDumps[6]
        self.participantEightDump = participantDumps[7]
        self.participantNineDump = participantDumps[8]
        self.participantTenDump = participantDumps[9]
