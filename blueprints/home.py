from flask import Blueprint, redirect, request, url_for, session
from services.spotify_oauth import sp_oauth, get_spotify_object

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
