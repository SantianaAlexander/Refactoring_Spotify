from flask import session
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from services.spotify_oauth import sp_oauth

def get_spotify_client():
    if "token_info" in session:
        token_info = session["token_info"]
        sp = spotipy.Spotify(auth=token_info["access_token"])
        return sp
    else:
        client_credentials_manager = SpotifyClientCredentials(
            client_id='af4cae999c184ad7b760fb8c51b60d60',
            client_secret='9d1c008a6aaa4a969b178224406d5a73'
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        return sp