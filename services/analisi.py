from flask import Flask, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import plotly.express as px
import pandas as pd
from collections import Counter
from services.spotify_utilis import get_playlist_tracks
from services.spotify_client import get_spotify_client
 
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

def genera_grafici(tracks):
    """Genera i grafici per i top 5 artisti e album presenti nella playlist."""
    artisti = [artist for track in tracks for artist in track['artists'].split(', ')]
    album = [track['album'] for track in tracks]

    top_artisti = Counter(artisti).most_common(5)
    top_album = Counter(album).most_common(5)

    df_artisti = pd.DataFrame(top_artisti, columns=['Artista', 'Conteggio'])
    df_album = pd.DataFrame(top_album, columns=['Album', 'Conteggio'])

    fig_artisti = px.bar(df_artisti, x='Artista', y='Conteggio', title='Top 5 Artisti nella Playlist', color='Artista')
    fig_album = px.pie(df_album, names='Album', values='Conteggio', title='Top 5 Album nella Playlist')

    return fig_artisti.to_html(full_html=False), fig_album.to_html(full_html=False)

if __name__ == "__main__":
    app.run(debug=True)
