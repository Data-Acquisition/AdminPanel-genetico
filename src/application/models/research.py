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
    diff_p = db.Column(db.Float)
    mix_p = db.Column(db.Float)
    den_p = db.Column(db.Float)
    prol = db.Column(db.Float)
    path = db.Column(db.Unicode(128))

    def __unicode__(self):
        return self.name