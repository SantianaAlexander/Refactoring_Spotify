#IMPORT
from flask import Blueprint, redirect, request, url_for, session, flash, jsonify
from flask import Blueprint, redirect, request, url_for, session, render_template
from flask_login import login_required, current_user
from services.spotify_oauth import sp_oauth, get_spotify_object
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from services.models import db, Playlist, UserPlaylist, UserPlaylistTrack
from services.analisi import analyze_and_visualize, analyze_playlist_tracks

playlist_bp = Blueprint('playlist', __name__)



def get_spotify_client():
    token_info = session.get("token_info")
    if token_info:
        return spotipy.Spotify(auth=token_info.get("access_token"))
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id="af4cae999c184ad7b760fb8c51b60d60",  
        client_secret="9d1c008a6aaa4a969b178224406d5a73" 
    ))

# ROTTA PER MOSTRARE LE PLAYLIST DELL'UTENTE
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

# ROTTA PER VISUALIZZARE I DETTAGLI DI UNA PLAYLIST PUBBLICA
@playlist_bp.route("/public_playlist/<playlist_id>")
@login_required
def public_playlist_details(playlist_id):
    sp = get_spotify_client()

    track_data = []
    usertrack_data = []

    # Prima controlliamo se è una playlist creata dall'utente
    user_playlist = UserPlaylist.query.filter_by(id=playlist_id).first()

    if user_playlist:
        # È una playlist creata sul sito
        tracks = UserPlaylistTrack.query.filter_by(user_playlist_id=user_playlist.id).all()
        
        for track in tracks:
            # Recupera il nome della traccia tramite track_id (che è l'ID Spotify)
            track_info = sp.track(track.track_id)  # Usa il client Spotify per ottenere il nome della traccia
            usertrack_data.append({
                "name": track_info["name"],  # Usa il nome effettivo della traccia
                "artist": ", ".join(artist["name"] for artist in track_info["artists"]),
                "album": track_info["album"]["name"],
                "popularity": track_info.get("popularity", 0),
                "duration_ms": track_info["duration_ms"],
                "release_date": track_info["album"]["release_date"]
            })

        playlist_details = {
            "name": user_playlist.name,
            "description": user_playlist.description,
            "images": [],  # Nessuna immagine
        }
        grafici = None

    else:
        # È una playlist Spotify
        playlist_details = sp.playlist(playlist_id)
        tracks = sp.playlist_tracks(playlist_id)["items"]

        for item in tracks:
            track = item["track"]
            if track: 
                artist_id = track["artists"][0]["id"]
                artist_data = sp.artist(artist_id)
                genres = artist_data.get("genres", [])

                track_data.append({
                    "name": track["name"],
                    "artists": ", ".join(artist["name"] for artist in track["artists"]),
                    "album": track["album"]["name"],
                    "popularity": track.get("popularity", 0),
                    "duration_ms": track["duration_ms"],
                    "release_date": track["album"]["release_date"],
                    "genres": genres
                })

        grafici = analyze_playlist_tracks(playlist_id)

    profile_pic_url = None
    try:
        user_info = sp.current_user()
        if user_info.get("images"):
            profile_pic_url = user_info["images"][0]["url"]
    except:
        pass

    return render_template(
        "public_playlist_details.html",
        playlist=playlist_details,
        tracks=track_data,
        usertracks=usertrack_data,
        profile_pic_url=profile_pic_url,
        grafici=grafici
    )

# ROTTA PER MOSTRARE LE PLAYLIST SALVATE DALL'UTENTE
@playlist_bp.route("/saved_playlists")
@login_required
def saved_playlists():
    # Playlist salvate (dalla tabella Playlist di Spotify)
    saved_playlists = Playlist.query.filter_by(user_id=current_user.id).all()

    # Playlist create (dalla tabella UserPlaylist)
    created_playlists = UserPlaylist.query.filter_by(user_id=current_user.id).all()

    sp = get_spotify_client()
    playlists_info = []

    # Gestione delle playlist salvate da Spotify
    for playlist in saved_playlists:
        details = sp.playlist(playlist.spotify_id)
        tracks = sp.playlist_tracks(playlist.spotify_id)['items']
        analysis = analyze_and_visualize(playlist.spotify_id)
        playlists_info.append({
            "id": playlist.spotify_id,
            "name": details["name"],
            "image": details["images"][0]["url"] if details["images"] else "/static/images/default_cover.png",
            "analysis": analysis,
            "created": False,  # Indica che questa playlist è salvata da Spotify
        })

    # Gestione delle playlist create dall'utente
    for playlist in created_playlists:
        playlists_info.append({
            "id": playlist.id,  # Usa l'ID interno del database per le playlist create
            "name": playlist.name,
            "image": "/static/images/default_cover.png",  # Puoi decidere se aggiungere un'immagine per le playlist create
            "analysis": None,  # Puoi lasciare l'analisi vuota se non hai bisogno di analizzare le playlist create
            "created": True,  # Indica che questa playlist è stata creata dall'utente
        })

    return render_template("saved_playlists.html", playlists=playlists_info)

                           
# ROTTA PER AGGIUNGERE UNA PLAYLIST ALLA LISTA SALVATA DELL'UTENTE
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

# ROTTA PER RIMUOVERE UNA PLAYLIST DALLA LISTA SALVATA DELL'UTENTE
@playlist_bp.route("/delete_playlist/<playlist_id>", methods=["POST"])
@login_required
def delete_playlist(playlist_id):
    # Verifica se la playlist è salvata (da Spotify)
    playlist = Playlist.query.filter_by(user_id=current_user.id, spotify_id=playlist_id).first()
    
    if playlist:
        db.session.delete(playlist)
        db.session.commit()
        flash("Playlist salvata rimossa con successo!", "success")
    
    # Verifica se la playlist è stata creata dall'utente (da UserPlaylist)
    else:
        user_playlist = UserPlaylist.query.filter_by(user_id=current_user.id, id=playlist_id).first()
        
        if user_playlist:
            db.session.delete(user_playlist)
            db.session.commit()
            flash("Playlist creata rimossa con successo!", "success")
        else:
            flash("Playlist non trovata.", "danger")
    
    return redirect(url_for('playlist.saved_playlists'))

@playlist_bp.route("/create_user_playlist", methods=["POST"])
@login_required
def create_user_playlist():
    playlist_name = request.form['playlist_name']
    playlist_description = request.form['playlist_description']
    
    # Crea una nuova playlist per l'utente
    new_playlist = UserPlaylist(
        name=playlist_name,  
        description=playlist_description,
        user_id=current_user.id
    )
    
    # Aggiungi la playlist al database e salva
    db.session.add(new_playlist)
    db.session.commit()  # Salva la playlist prima di aggiungere le tracce

    # Recupera le tracce selezionate dal form
    selected_tracks = request.form.getlist('selected_tracks')  # Recupera tutte le tracce selezionate
    track_names = request.form.getlist('selected_tracks_name')  # Recupera i nomi delle tracce
    
    # Aggiungi le tracce selezionate alla playlist
    for track_id, track_name in zip(selected_tracks, track_names):
        new_track = UserPlaylistTrack(
            user_playlist_id=new_playlist.id,
            track_id=track_id
        )
        db.session.add(new_track)
    
    db.session.commit()  # Salva tutte le tracce nella playlist

    flash("Playlist creata con successo!", "success")
    return redirect(url_for('playlist.saved_playlists'))