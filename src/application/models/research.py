from application.models import db
from datetime import datetime


class Research(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.Unicode(64))
    name = db.Column(db.Unicode(64))
    patronymic = db.Column(db.Unicode(64))
    passport = db.Column(db.Integer)
    comment = db.Column(db.Unicode(256))
    date = db.Column(db.DateTime, default=datetime.now)
    PP = db.Column(db.Float)
    DC = db.Column(db.Float)
    DS = db.Column(db.Float)
    DP = db.Column(db.Float)
    path = db.Column(db.Unicode(128))

    def __unicode__(self):
        return self.name