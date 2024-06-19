from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from pytz import timezone 
from datetime import datetime


db = SQLAlchemy()

#Usermixin it will take some of the default features
class User(UserMixin,db.Model):
    UserID = db.Column(db.Integer, primary_key=True, autoincrement = True)
    Name = db.Column(db.String(100), nullable=False)
    Username = db.Column(db.String(50), unique=True, nullable=False)
    HashedPassword = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default = False, nullable = False)
    def get_id(self):
        return str(self.UserID)
    def __str__(self):
        return self.Name


class Venue(db.Model):
    VenueID = db.Column(db.Integer, primary_key=True, autoincrement = True)
    VenueName = db.Column(db.String(100), nullable=False)
    VenueAddress = db.Column(db.String(500), nullable=False)
    VenueImageURL = db.Column(db.String(200))
    FirstSlot = db.Column(db.Time, nullable = False)
    LastSlot = db.Column(db.Time, nullable = False)
    # many to one relationship
    Sports = db.relationship('Sport', secondary='venue_sport', backref= db.backref('venues', lazy='dynamic'))
    VenueBlog = db.Column(db.String(2000))
    def __str__(self):
        return self.VenueName


class Sport(db.Model):
    SportID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    SportName = db.Column(db.String(100), nullable=False, unique=True)
    SportImageURL= db.Column(db.String(200))
    def __str__(self):
        return self.SportName

venue_sport = db.Table("venue_sport",
db.Column("venue_id",db.Integer,db.ForeignKey("venue.VenueID")),
db.Column("sport_id",db.Integer,db.ForeignKey("sport.SportID"))
)  

class BookingLog(db.Model):
    BookingID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, db.ForeignKey('user.UserID'), nullable=False)
    VenueID = db.Column(db.Integer, db.ForeignKey('venue.VenueID'), nullable=False)
    SportID = db.Column(db.Integer, db.ForeignKey('sport.SportID'), nullable=False)
    Slot = db.Column(db.String(10),nullable=False)
    Duration = db.Column(db.String(5),nullable=False)
    Date = db.Column(db.String(20), nullable=False)
    BookingTime = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone("Asia/Kolkata")).replace(microsecond=0))
    # To keep a track of when booking took place

    User = db.relationship('User', backref='bookings', lazy=True)
    Venue = db.relationship('Venue', backref='bookings', lazy=True)
    Sport = db.relationship('Sport', backref='bookings', lazy=True)
    __table_args__ = (
        UniqueConstraint("UserID",'VenueID', 'SportID', 'Slot', 'Duration', 'Date'),
    )


# NOT USED to its full potential but may use when members increase
class Member(db.Model):
    MemberId= db.Column(db.Integer, primary_key=True, autoincrement=True)
    Instno = db.Column(db.Integer, nullable = False, unique= True)
    Name = db.Column(db.String(100), nullable=False)
    Batch = db.Column(db.Integer, nullable = False)
    MemImageURL = db.Column(db.String(200), nullable = False)
    

