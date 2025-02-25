from flask import session
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def get_spotify_client():
    token_info = session.get("token_info")
    if token_info:
        return spotipy.Spotify(auth=token_info.get("access_toke"))
    return spotipy.Spotify(auth=None)