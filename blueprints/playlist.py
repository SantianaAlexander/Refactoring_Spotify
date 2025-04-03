from flask import Blueprint, redirect, request, url_for, session, flash, jsonify
from flask import Blueprint, redirect, request, url_for, session, render_template
from flask_login import login_required, current_user
from services.spotify_oauth import sp_oauth, get_spotify_object
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from services.models import db, Playlist
from services.analisi import analyze_and_visualize, get_tracks_from_playlist, genera_grafici

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

@playlist_bp.route("/public_playlist/<playlist_id>")
def public_playlist_details(playlist_id):
    sp = get_spotify_client()
    tracks = sp.playlist_tracks(playlist_id)["items"]
    profile_pic_url = None
    user_info = sp.current_user()
    if user_info.get("images"):
        profile_pic_url = user_info["images"][0]["url"]
    
    # Genera i grafici
    grafici = genera_grafici(tracks)

    return render_template(
        "public_playlist_details.html",
        tracks=tracks,
        profile_pic_url=profile_pic_url,
        playlist_id=playlist_id,
        grafici=grafici
    )

@playlist_bp.route("/saved_playlists")
@login_required
def saved_playlists():
    saved_playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    
    sp = get_spotify_client()
    playlists_info = []

    for playlist in saved_playlists:
        details = sp.playlist(playlist.spotify_id)
        tracks = sp.playlist_tracks(playlist.spotify_id)['items']
        analysis = analyze_and_visualize(playlist.spotify_id)
        playlists_info.append({
            "id": playlist.spotify_id,
            "name": details["name"],
            "image": details["images"][0]["url"] if details["images"] else "/static/images/default_cover.png",
            "analysis": analysis,
        })
    
    print(f"Playlists Info: {playlists_info}")

    return render_template("saved_playlists.html", playlists=playlists_info)

@playlist_bp.route("/add_playlist/<playlist_id>", methods=["POST"])
@login_required
def add_playlist(playlist_id):

    sp = get_spotify_client()  
    playlist_details = sp.playlist(playlist_id)


    name = playlist_details.get("name")
    image_url = playlist_details.get("images", [{}])[0].get("url") if playlist_details.get("images") else None


    existing_playlist = Playlist.query.filter_by(user_id=current_user.id, spotify_id=playlist_id).first()
    
    if existing_playlist:
        flash("Questa playlist è già salvata!", "info")
    else:

        new_playlist = Playlist(
            user_id=current_user.id,
            spotify_id=playlist_id,
            name=name,
            image_url=image_url
        )
        db.session.add(new_playlist)
        db.session.commit()
        flash("Playlist aggiunta con successo!", "success")
    
    return redirect(url_for("playlist.saved_playlists"))

@playlist_bp.route("/delete_playlist/<playlist_id>", methods=["POST"])
@login_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.filter_by(user_id=current_user.id, spotify_id=playlist_id).first()
    
    if playlist:
        db.session.delete(playlist)
        db.session.commit()
        flash("Playlist rimossa con successo!", "success")
    else:
        flash("Playlist non trovata.", "danger")
    
    return redirect(url_for('playlist.saved_playlists'))