from flask import Blueprint, redirect, request, url_for, session, render_template
from services.spotify_oauth import sp_oauth, get_spotify_object
import spotipy

home_bp = Blueprint('home', __name__)


@home_bp.route('/home')
def home():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect(url_for('login'))
    sp = spotipy.Spotify(auth=token_info['access_token']) 
    user_info = sp.current_user()
    print(user_info)
    playlists = sp.current_user_playlists() 
    playlists_info = playlists['items'] 
    return render_template('home.html', user_info=user_info, playlists=playlists_info)

@home_bp.route('/playlist/<playlist_id>')
def visualizza_playlist(playlist_id):
    token_info = session.get('token_info', None)
    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_info = sp.current_user()
    brani_playlist = sp.playlist_items(playlist_id)
    brano_singolo = brani_playlist['items']
    return render_template('playlist.html', brani = brano_singolo, user_info = user_info)