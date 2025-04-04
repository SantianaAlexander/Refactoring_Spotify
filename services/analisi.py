from flask import Flask, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import plotly.express as px
import pandas as pd
from collections import Counter
from services.spotify_utilis import get_playlist_tracks
from services.spotify_client import get_spotify_client
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.io as pio
from collections import Counter
from datetime import datetime
 
app = Flask(__name__)
 
client_credentials_manager = SpotifyClientCredentials(client_id='YOUR_SPOTIFY_CLIENT_ID', client_secret='YOUR_SPOTIFY_CLIENT_SECRET')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

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

def get_tracks_from_playlist(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = []
    for item in results['items']:
        track = item['track']
        track_info = {
            'name': track['name'],
            'artists': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'image_url': track['album']['images'][0]['url'],
            'spotify_url': track['external_urls']['spotify'],
            'release_date': track['album']['release_date'], 
            'duration_ms': track['duration_ms'],  
            'popularity': track['popularity'],  
            'genres': track['album']['artists'][0].get('genres', []) 
        }
        tracks.append(track_info)
    return tracks

def analyze_and_visualyze_tracks(tracks):
    track_data = []

    # Prepara i dati
    for item in tracks:
        track = item.get("track")  # Prendiamo i dati della traccia
        if track:
            track_data.append({
                "name": track["name"],
                "popularity": track.get("popularity", 0),
                "duration_ms": track["duration_ms"],
                "release_date": track["album"]["release_date"],
                "genres": track.get("genres", []),  # Aggiungiamo i generi
            })
    
    # 📊 Grafico della popolarità delle tracce
    fig_popularity = px.histogram(
        track_data, x="popularity", title="Distribuzione della Popolarità delle Tracce", nbins=20
    )
    fig_popularity_html = pio.to_html(fig_popularity, full_html=False)

    # 📊 Durata delle tracce
    fig_duration = px.histogram(
        track_data, x="duration_ms", title="Distribuzione della Durata delle Tracce", nbins=20
    )
    fig_duration_html = pio.to_html(fig_duration, full_html=False)

    # 📅 Distribuzione temporale delle tracce (per anno)
    release_years = [datetime.strptime(track["release_date"], "%Y-%m-%d").year if "-" in track["release_date"] else int(track["release_date"]) for track in track_data]
    fig_release_years = px.histogram(
        x=release_years, title="Distribuzione dei Brani per Anno di Pubblicazione", nbins=20
    )
    fig_release_years_html = pio.to_html(fig_release_years, full_html=False)

    # 🎶 Distribuzione dei generi musicali (somma delle occorrenze)
    all_genres = [genre for track in track_data for genre in track["genres"]]
    genre_counts = dict(Counter(all_genres))
    fig_genres = px.bar(
        x=list(genre_counts.keys()), 
        y=list(genre_counts.values()), 
        labels={'x': 'Generi', 'y': 'Numero di Tracce'}, 
        title="Distribuzione dei Generi Musicali"
    )
    fig_genres_html = pio.to_html(fig_genres, full_html=False)

    # 📈 Evoluzione della popolarità nel tempo
    popularity_over_time = [
        {"year": datetime.strptime(track["release_date"], "%Y-%m-%d").year if "-" in track["release_date"] else int(track["release_date"]), 
         "popularity": track["popularity"]} for track in track_data
    ]
    popularity_over_time.sort(key=lambda x: x["year"])  # Ordina per anno
    fig_popularity_time = px.line(
        popularity_over_time, x="year", y="popularity", title="Evoluzione della Popolarità nel Tempo"
    )
    fig_popularity_time_html = pio.to_html(fig_popularity_time, full_html=False)

    # Ritorna tutti i grafici come HTML
    return {
        "fig_popularity": fig_popularity_html,
        "fig_duration": fig_duration_html,
        "fig_release_years": fig_release_years_html,
        "fig_genres": fig_genres_html,
        "fig_popularity_time": fig_popularity_time_html
    }

if __name__ == "__main__":
    app.run(debug=True)
