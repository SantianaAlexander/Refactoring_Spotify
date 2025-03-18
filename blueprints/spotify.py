from flask import Blueprint, redirect, request, url_for, session
from services.spotify_oauth import sp_oauth

spotify_bp = Blueprint('spotify', __name__)

@spotify_bp.route('/sp_login')
def spotify_login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@spotify_bp.route('/callback')
def spotify_callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code) 
    session['token_info'] = token_info
    return redirect(url_for('home.home'))

@spotify_bp.route('/sp_logout')
def spotify_logout():
    session.clear()
    return redirect(url_for('home.home'))