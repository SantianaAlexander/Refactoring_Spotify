#IMPORT
from flask import Flask
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from services.spotify_client import get_spotify_client
import pandas as pd
import plotly.express as px
import plotly.io as pio
from collections import Counter
 
app = Flask(__name__)
 
client_credentials_manager = SpotifyClientCredentials(client_id='YOUR_SPOTIFY_CLIENT_ID', client_secret='YOUR_SPOTIFY_CLIENT_SECRET')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# FUNZIONE PER ANALIZZARE UNA PLAYLIST E GENERARE GRAFICI SULLA POPOLARITÀ, PRESENZA ARTISTI E DISTRIBUZIONE ARTISTICA
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

# FUNZIONE PER ESTRARRE I DATI DEI BRANI DA UNA PLAYLIST
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

# FUNZIONE PER ANALIZZARE I BRANI DI UNA PLAYLIST (ANNO DI USCITA, DURATA, POPOLARITÀ, GENERI) E GENERARE GRAFICI APPROFONDITI 
def analyze_playlist_tracks(playlist_id):
    sp = get_spotify_client()
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']

    track_data = []

    for item in tracks:
        track = item.get("track")
        if not track:
            continue

        track_name = track.get("name")
        duration_ms = track.get("duration_ms")
        popularity = track.get("popularity", 0)

        album = track.get("album", {})
        release_date = album.get("release_date", "")
        release_year = release_date.split("-")[0] if release_date else None

        artists = track.get("artists", [])
        main_artist = artists[0] if artists else {}
        artist_name = main_artist.get("name")
        artist_id = main_artist.get("id")

        genres = []
        if artist_id:
            artist_info = sp.artist(artist_id)
            genres = artist_info.get("genres", [])

        track_data.append({
            "track_name": track_name,
            "artist_name": artist_name,
            "duration_ms": duration_ms,
            "popularity": popularity,
            "release_year": int(release_year) if release_year and release_year.isdigit() else None,
            "genres": genres
        })

    df = pd.DataFrame(track_data)

    fig_years = px.histogram(df.dropna(subset=['release_year']), x="release_year", nbins=20, title="Distribuzione dei brani per anno")

    fig_duration = px.histogram(df, x="duration_ms", nbins=20, title="Distribuzione della durata dei brani (ms)")

    fig_popularity = px.histogram(df, x="popularity", nbins=20, title="Distribuzione della popolarità")

    all_genres = [genre for track in track_data for genre in track["genres"]]
    genre_counts = dict(Counter(all_genres))

    genre_counts_df = pd.DataFrame(list(genre_counts.items()), columns=["Genre", "Count"])

    fig_genres = px.bar(genre_counts_df, x="Genre", y="Count",
                        labels={"Genre": "Genere", "Count": "Conteggio"},
                        title="Distribuzione dei generi musicali")

    pop_year = df.dropna(subset=['release_year'])
    fig_trend = px.line(pop_year.sort_values('release_year'), x="release_year", y="popularity",
                        title="Evoluzione della popolarità nel tempo")

    return { 
        "fig_years": pio.to_html(fig_years, full_html=False),
        "fig_duration": pio.to_html(fig_duration, full_html=False),
        "fig_popularity": pio.to_html(fig_popularity, full_html=False),
        "fig_genres": pio.to_html(fig_genres, full_html=False),
        "fig_trend": pio.to_html(fig_trend, full_html=False)
    } 


if __name__ == "__main__":
    app.run(debug=True)
              