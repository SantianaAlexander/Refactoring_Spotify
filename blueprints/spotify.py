#IMPORT
from flask import Blueprint, redirect, request, url_for, session
from flask_login import login_required, current_user
from services.spotify_oauth import sp_oauth

spotify_bp = Blueprint('spotify', __name__)

#ENDPOINT LOGIN SPOTIFY
@spotify_bp.route('/sp_login')
def spotify_login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

#CALLBACK
@spotify_bp.route('/callback')
def spotify_callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code) 
    session['token_info'] = token_info
    return redirect(url_for('home.home'))

#ENDPOINT LOGOUT SPOTIFY
@spotify_bp.route('/sp_logout')
def spotify_logout():
    session.pop('token_info', None)
    return redirect(url_for('home.home', username = current_user.username))