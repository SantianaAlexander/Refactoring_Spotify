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
import io
import base64
 
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
    # Estrazione delle informazioni
    anni_release = []
    durate = []
    popolarita = []
    generi = []
    popolarita_per_anno = {}

    for track in tracks:
        # Anno di rilascio dalla data di rilascio del brano
        data_release = track['track']['album']['release_date']  # Qui accediamo solo alla data del brano
        if len(data_release) == 4:  # Se è solo l'anno (es: "1981")
            anno = int(data_release)
        else:  # Se è formato completo (es: "1981-12")
            anno = int(data_release.split('-')[0])
        anni_release.append(anno)
        
        # Durata del brano in secondi (convertito da millisecondi)
        durata = track['track']['duration_ms'] / 1000  # durata in secondi
        durate.append(durata)
        
        # Popolarità
        popolarita.append(track['track']['popularity'])
        
        # Generi
        if 'genres' in track['track']:
            for genre in track['track']['genres']:
                generi.append(genre)
        
        # Popolarità per anno (per grafico evoluzione della popolarità)
        if anno not in popolarita_per_anno:
            popolarita_per_anno[anno] = []
        popolarita_per_anno[anno].append(track['track']['popularity'])

    # Funzione per convertire i grafici in base64
    def fig_to_base64(fig):
        img_stream = io.BytesIO()
        fig.savefig(img_stream, format='png')
        img_stream.seek(0)
        return base64.b64encode(img_stream.read()).decode('utf-8')

    # Grafico per distribuzione temporale (brani per anno)
    fig_anni, ax_anni = plt.subplots()
    anni_count = Counter(anni_release)
    ax_anni.bar(anni_count.keys(), anni_count.values())
    ax_anni.set_title("Distribuzione Temporale dei Brani")
    ax_anni.set_xlabel("Anno di Pubblicazione")
    ax_anni.set_ylabel("Numero di Brani")
    grafico_anni = fig_to_base64(fig_anni)

    # Grafico per distribuzione della durata dei brani
    fig_durata, ax_durata = plt.subplots()
    ax_durata.hist(durate, bins=20, color='skyblue', edgecolor='black')
    ax_durata.set_title("Distribuzione della Durata dei Brani")
    ax_durata.set_xlabel("Durata (secondi)")
    ax_durata.set_ylabel("Numero di Brani")
    grafico_durata = fig_to_base64(fig_durata)

    # Grafico per distribuzione della popolarità
    fig_popolarita, ax_popolarita = plt.subplots()
    ax_popolarita.hist(popolarita, bins=20, color='green', edgecolor='black')
    ax_popolarita.set_title("Distribuzione della Popolarità dei Brani")
    ax_popolarita.set_xlabel("Popolarità")
    ax_popolarita.set_ylabel("Numero di Brani")
    grafico_popolarita = fig_to_base64(fig_popolarita)

    # Grafico per distribuzione dei generi
    fig_generi, ax_generi = plt.subplots()
    generi_count = Counter(generi)
    ax_generi.bar(generi_count.keys(), generi_count.values())
    ax_generi.set_title("Distribuzione dei Generi Musicali")
    ax_generi.set_xlabel("Generi")
    ax_generi.set_ylabel("Numero di Brani")
    grafico_generi = fig_to_base64(fig_generi)

    # Grafico per evoluzione della popolarità nel tempo
    fig_evoluzione, ax_evoluzione = plt.subplots()
    anni_ordinati = sorted(popolarita_per_anno.keys())
    popolarita_media_per_anno = [np.mean(popolarita_per_anno[anno]) for anno in anni_ordinati]
    ax_evoluzione.plot(anni_ordinati, popolarita_media_per_anno, marker='o')
    ax_evoluzione.set_title("Evoluzione della Popolarità nel Tempo")
    ax_evoluzione.set_xlabel("Anno di Pubblicazione")
    ax_evoluzione.set_ylabel("Popolarità Media")
    grafico_evoluzione = fig_to_base64(fig_evoluzione)

    # Ritorna i grafici come immagini base64
    return {
        "grafico_anni": grafico_anni,
        "grafico_durata": grafico_durata,
        "grafico_popolarita": grafico_popolarita,
        "grafico_generi": grafico_generi,
        "grafico_evoluzione": grafico_evoluzione
    }

@app.route('/grafici_playlist')
def grafici_playlist():
    """Endpoint per ottenere i grafici della playlist."""
    playlist_id = request.args.get('playlist_id')
    if not playlist_id:
        return jsonify({'error': 'Playlist ID mancante'}), 400
    
    tracks = get_tracks_from_playlist(playlist_id)  # Recupera i brani della playlist
    if not tracks:
        return jsonify({'error': 'Nessun brano trovato'}), 404
    
    fig_artisti, fig_album = genera_grafici(tracks)
    return jsonify({'grafico_artisti': fig_artisti, 'grafico_album': fig_album})

if __name__ == "__main__":
    app.run(debug=True)
