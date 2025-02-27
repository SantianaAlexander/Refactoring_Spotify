from flask import Blueprint, redirect, request, url_for, session
from flask import Blueprint, redirect, request, url_for, session, render_template
from services.spotify_oauth import sp_oauth, get_spotify_object
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

playlist_bp = Blueprint('playlist', __name__)

def get_spotify_client():
    token_info = session.get("token_info")
    if token_info:
        return spotipy.Spotify(auth=token_info.get("access_token"))
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id="af4cae999c184ad7b760fb8c51b60d60",  
        client_secret="9d1c008a6aaa4a969b178224406d5a73" 
    ))

@playlist_bp.route('/playlist')
def playlist():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('auth.login')) 

    sp = get_spotify_client() 
    playlists = sp.current_user_playlists()
    playlists_info = playlists['items']  

    profile_pic_url = None
    user_info = sp.current_user()
    if user_info.get("images"):
        profile_pic_url = user_info["images"][0]["url"]

    return render_template('playlist.html', playlists=playlists_info, profile_pic_url=profile_pic_url)

@playlist_bp.route('/playlist_details/<playlist_id>')
def playlist_details(playlist_id):
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('auth.login'))  

    sp = get_spotify_client() 
    results = sp.playlist_tracks(playlist_id)  
    tracks = results['items'] 
    profile_pic_url = None
    user_info = sp.current_user()
    if user_info.get("images"):
        profile_pic_url = user_info["images"][0]["url"]

    return render_template('playlist_details.html', tracks=tracks, playlist=playlist, profile_pic_url=profile_pic_url)
