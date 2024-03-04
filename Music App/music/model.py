from db import db
from flask_login import UserMixin


class User(UserMixin,db.Model):
    __tablename__ = 'User'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(2000), unique=True, nullable=False) 
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    playlist = db.relationship('playlist', back_populates='user')
    role = db.Column(db.String(255),default='user')
    
    def get_id(self):
        return str(self.user_id)



class Admin(UserMixin,db.Model):
    __tablename__='Admin'
    admin_id = db.Column(db.Integer, primary_key=True)
    adminname = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    
    def get_id(self):
        return str(self.admin_id)
    
    
class Track:
    def __init__(self, name, image_url, mp3_url):
        self.name = name
        self.image_url = image_url
        self.mp3_url = mp3_url

class playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    songs = db.relationship('song', back_populates='playlist')
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))
    user = db.relationship('User', back_populates='playlist')

class song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    track = db.Column(db.String(255), nullable=False)
    creator = db.Column(db.String(255), nullable=False)
    lyrics = db.Column(db.Text, nullable=True)
    song_url=db.Column(db.Text)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id', ondelete='CASCADE'), nullable=True)
    playlist = db.relationship('playlist', back_populates='songs')
    ratings = db.Column(db.Integer, default =0.0)