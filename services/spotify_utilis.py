from flask import session
from .spotify_oauth import get_spotify_object
from services.models import db, Playlist

def get_playlist_tracks(playlist_id):
    # Recupera la playlist dal database
    playlist = Playlist.query.filter_by(id=playlist_id).first()

    if not playlist:
        print(f"Playlist con ID {playlist_id} non trovata.")
        return None

    # Recupera il token Spotify dalla sessione
    token_info = session.get("token_info")
    if not token_info:
        print("Token non trovato nella sessione.")
        return None

    # Ottieni l'oggetto Spotify tramite il token
    sp = get_spotify_object(token_info)

    # Recupera le tracce della playlist utilizzando l'ID di Spotify
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
            "genre": "Sconosciuto"  # Puoi migliorarlo se recuperi un genere dalla traccia
        })

    return tracks