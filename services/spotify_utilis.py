#IMPORT
from flask import session
from .spotify_oauth import get_spotify_object
from services.models import db, Playlist

#FUNZIONE CHE PRENDE LE TRACCE
def get_playlist_tracks(playlist_id):
    # RECUPERO PLAYLIST DAL DATABASE
    playlist = Playlist.query.filter_by(id=playlist_id).first()

    if not playlist:
        print(f"Playlist con ID {playlist_id} non trovata.")
        return None

    token_info = session.get("token_info")
    if not token_info:
        print("Token non trovato nella sessione.")
        return None

    sp = get_spotify_object(token_info)

    # RECUPERO TRACCE TRAMITE ID
    try:
        results = sp.playlist_tracks(playlist.spotify_id)["items"]
    except Exception as e:
        print(f"Errore nel recupero delle tracce: {e}")
        return None

    tracks = []
    for item in results:
        track = item["track"]
        tracks.append({
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "popularity": track.get("popularity", 0),
            "genre": "Sconosciuto" 
        })

    return tracks