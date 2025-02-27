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

@home_bp.route('/', methods=['GET', 'POST'])
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
    search_results = []
    query = ""

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            try:
                
                if not isinstance(sp, spotipy.Spotify):
                    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                        client_id="af4cae999c184ad7b760fb8c51b60d60", 
                        client_secret="9d1c008a6aaa4a969b178224406d5a73"  
                    ))
                
                results = sp.search(q=query, type="playlist", limit=10)
                search_results = [
                    {
                        "id": playlist["id"],
                        "name": playlist.get("name", "Senza Nome"),
                        "owner": playlist["owner"].get("display_name", "Sconosciuto"),
                        "image": playlist["images"][0]["url"] if playlist.get("images") else None,
                        "track_count": playlist["tracks"]["total"]
                    }
                    for playlist in results.get("playlists", {}).get("items", [])
                    if playlist
                ]
            except Exception as e:
                print("Errore nella ricerca:", e)

    return render_template('home.html', user_info=user_info, playlists=playlists, profile_pic_url=profile_pic_url, query = query, search_results = search_results)


@home_bp.route('/playlist/<playlist_id>')
def visualizza_playlist(playlist_id):
    sp = get_spotify_client()
    if not isinstance(sp, spotipy.Spotify):
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id="af4cae999c184ad7b760fb8c51b60d60", 
            client_secret="9d1c008a6aaa4a969b178224406d5a73"  
    ))

    playlist_data, tracks = None, []
    try:
        playlist_data = sp.playlist(playlist_id)
        tracks_data = playlist_data["tracks"]["items"]

        tracks = [
            {
                "name": track["track"].get("name", "Senza Nome"),
                "artist": track["track"]["artists"][0].get("name", "Sconosciuto"),
                "album": track["track"]["album"].get("name", "Senza Nome"),
                "cover": track["track"]["album"].get("images", [{}])[0].get("url", None)
            }
            for track in tracks_data if track.get("track")
        ]
    except Exception as e:
        print("Errore nel recupero della playlist:", e)

    return render_template("playlist.html", playlist=playlist_data, tracks=tracks)

@home_bp.route("/public_playlist/<playlist_id>")
def public_playlist_details(playlist_id):
    sp = get_spotify_client()
    tracks = sp.playlist_tracks(playlist_id)["items"]
    profile_pic_url = None
    user_info = sp.current_user()
    if user_info.get("images"):
        profile_pic_url = user_info["images"][0]["url"]
    return render_template("public_playlist_details.html", tracks=tracks, profile_pic_url=profile_pic_url)