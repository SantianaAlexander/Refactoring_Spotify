from flask import Blueprint, redirect, request, url_for, session, render_template
from services.spotify_oauth import sp_oauth, get_spotify_object
from services.spotify_client import get_spotify_client

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

home_bp = Blueprint('home', __name__)

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

@home_bp.route('/')
def home():
    sp = get_spotify_client()
    user_info = None
    playlists = []
    profile_pic_url = None
    selected_playlist = session.get('selected_playlist')

    if isinstance(sp, spotipy.Spotify) and session.get("token_info"):
        try:
            user_info = sp.current_user()
            playlists = sp.current_user_playlists()["items"]
            if user_info.get("images"):
                profile_pic_url = user_info["images"][0]["url"]
        except Exception:
            pass

    playlist_data = None
    if selected_playlist:
        playlist_data = sp.playlist(selected_playlist)

    return render_template('home.html', user_info=user_info, playlists=playlists, profile_pic_url=profile_pic_url, selected_playlist=playlist_data)

@home_bp.route('/search', methods=['POST'])
def search_playlist():
    query = request.form.get('query')
    if not query:
        return redirect(url_for('home.home'))

    sp = get_spotify_client()
    results = sp.search(q=query, type='playlist', limit=5)

    search_results = results['playlists']['items'] if 'playlists' in results else []
    
    return render_template('home.html', search_results=search_results, user_info=session.get('user_info'), profile_pic_url=session.get('profile_pic_url'))


@home_bp.route('/select_playlist/<playlist_id>')
def select_playlist(playlist_id):
    session['selected_playlist'] = playlist_id  # Salva nella sessione
    return redirect(url_for('home.home'))

#@home_bp.route('/playlist/<playlist_id>')
#def visualizza_playlist(playlist_id):
    #sp = get_spotify_client()
    #token_info = session.get('token_info', None)
    #sp = spotipy.Spotify(auth=token_info['access_token'])
    #user_info = sp.current_user()
    #brani_playlist = sp.playlist_items(playlist_id)
    #brano_singolo = brani_playlist['items']
    #return render_template('playlist.html', brani = brano_singolo, user_info = user_info)