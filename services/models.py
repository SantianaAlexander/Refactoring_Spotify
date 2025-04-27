#IMPORT
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

#TABELLA USER
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

#TABELLA PLAYLIST
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    spotify_id = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(300)) 
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))

     
    __table_args__ = (db.UniqueConstraint('spotify_id', 'user_id', name='unique_playlist_per_user'),)

# TABELLA USERPLAYLIST
class UserPlaylist(db.Model):
    __tablename__ = "user_playlist"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False) 
    description = db.Column(db.String(500), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('user_playlists', lazy=True))

    tracks = db.relationship(
        'UserPlaylistTrack', 
        backref='user_playlist', 
        cascade='all, delete-orphan', 
        lazy='dynamic'
    )

# TABELLA USERPLAYLISTTRACK
class UserPlaylistTrack(db.Model):
    __tablename__ = "user_playlist_track"
    id = db.Column(db.Integer, primary_key=True)
    user_playlist_id = db.Column(db.Integer, db.ForeignKey('user_playlist.id'), nullable=False)
    track_id = db.Column(db.String(100), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_playlist_id', 'track_id', name='unique_track_per_playlist'),)