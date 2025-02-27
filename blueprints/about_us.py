from flask import Blueprint, redirect, request, url_for, session, render_template
from services.spotify_oauth import sp_oauth, get_spotify_object
from services.spotify_client import get_spotify_client

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

aboutus_bp = Blueprint('aboutus', __name__)

def get_spotify_client():
    token_info = session.get("token_info")
    if token_info:
        return spotipy.Spotify(auth=token_info.get("access_token"))
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id="af4cae999c184ad7b760fb8c51b60d60",
        client_secret="9d1c008a6aaa4a969b178224406d5a73"
    ))

def get_user_playlists(user_id):
    token_info = session.get('token_info')
    if not token_info:
        return None
    sp = spotipy.Spotify(auth=token_info['access_token'])
    playlists = sp.user_playlists(user_id)
    return playlists['items']

@aboutus_bp.route('/about')
def about_us():
    sp = get_spotify_client()
    user_info = None
    playlists = []
    profile_pic_url = None

    if isinstance(sp, spotipy.Spotify) and session.get("token_info"):
        try:
            user_info = sp.current_user()
            playlists = sp.current_user_playlists()["items"]
            if user_info.get("images"):
                profile_pic_url = user_info["images"][0]["url"]
        except Exception:
            pass

    return render_template('about_us.html', user_info=user_info, playlists=playlists, profile_pic_url=profile_pic_url)