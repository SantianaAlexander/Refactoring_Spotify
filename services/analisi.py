import pandas as pd
import plotly.express as px
from services.spotify_utilis import get_playlist_tracks
from services.spotify_client import get_spotify_client

def analyze_and_visualize(playlist_id):
    # Ottieni le tracce dalla playlist usando l'ID della playlist
    sp = get_spotify_client()
    results = sp.playlist_tracks(playlist_id)
    tracks = results["items"]

    # Crea una lista di dati per le tracce
    data = []
    for track_item in tracks:
        track = track_item["track"]
        data.append({
            "track_name": track["name"],
            "artist": track["artists"][0]["name"],  # Prendi il primo artista
            "album": track["album"]["name"],
            "popularity": track.get("popularity", 0),  # Popolarità delle tracce
            "duration_ms": track["duration_ms"]  # Durata in millisecondi
        })

    # Crea un DataFrame da pandas per l'elaborazione dei dati
    df = pd.DataFrame(data)

    # Calcola la durata media in secondi
    avg_duration_sec = df["duration_ms"].mean() / 1000  # Converti in secondi

    # Crea il grafico della distribuzione della popolarità
    fig_popularity = px.histogram(
        df, x="popularity", nbins=20,
        title="Distribuzione della Popolarità delle Tracce",
        labels={"popularity": "Popolarità", "count": "Numero di Brani"}
    )

    # Calcola la presenza degli artisti
    artist_counts = df["artist"].value_counts().reset_index()
    artist_counts.columns = ["artist", "count"]

    # Crea il grafico a barre degli artisti più presenti
    fig_artists_presence = px.bar(
        artist_counts.head(10), x="artist", y="count",
        title="Top 10 Artisti più Presenti nella Playlist"
    )

    # Restituisci i risultati
    return {
        "avg_duration": f"Durata media: {avg_duration_sec:.2f} secondi",
        "fig_popularity": fig_popularity.to_html(full_html=False),
        "fig_artists_presence": fig_artists_presence.to_html(full_html=False)
    }