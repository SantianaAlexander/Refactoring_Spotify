import pandas as pd
import plotly.express as px
from services.spotify_utilis import get_playlist_tracks
from services.spotify_client import get_spotify_client

def analyze_and_visualize(playlist_id):
    sp = get_spotify_client()
    results = sp.playlist_tracks(playlist_id)
    tracks = results["items"]
    data = []
    for track_item in tracks:
        track = track_item["track"]
        data.append({
            "track_name": track["name"],
            "artist": track["artists"][0]["name"],  
            "album": track["album"]["name"],
            "popularity": track.get("popularity", 0), 
            "duration_ms": track["duration_ms"] 
        })

    df = pd.DataFrame(data)

    fig_popularity = px.histogram(
        df, x="popularity", nbins=10,
        title="Distribuzione della Popolarità delle Tracce",
        labels={"popularity": "Popolarità", "count": "Numero di Brani"}
    )

    artist_counts = df["artist"].value_counts().reset_index()
    artist_counts.columns = ["artist", "count"]

    fig_artists_presence = px.bar(
        artist_counts.head(10), x="artist", y="count",
        title="Top 10 Artisti più Presenti nella Playlist"
    )

    artist_counts_filtered = artist_counts[artist_counts["count"] > 1].head(10)
    fig_pie_chart = px.pie(
        artist_counts_filtered, values="count", names="artist",
        title="Distribuzione degli Artisti nella Playlist"
    )


    return {
        "fig_popularity": fig_popularity.to_html(full_html=False),
        "fig_artists_presence": fig_artists_presence.to_html(full_html=False),
        "fig_pie_chart": fig_pie_chart.to_html(full_html=False)
    }
