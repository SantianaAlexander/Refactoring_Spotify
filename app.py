from flask import Flask
from blueprints.auth import auth_bp
from blueprints.home import home_bp
from blueprints.about_us import aboutus_bp
from blueprints.playlist import playlist_bp

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

app = Flask(__name__)
app.secret_key = "chiavesessione"

app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(aboutus_bp)
app.register_blueprint(playlist_bp)

if __name__ == "__main__":
    app.run(debug = True, port=5001)


   """ tracks = [
    {
        'track': {
            'name': 'Song 1',
            'album': {'name': 'Album 1', 'images': [{'url': 'image_url_1'}]},
            'artists': [{'name': 'Artist 1'}, {'name': 'Artist 2'}],
            'genre': 'Pop'
        }
    },
    {
        'track': {
            'name': 'Song 2',
            'album': {'name': 'Album 2', 'images': [{'url': 'image_url_2'}]},
            'artists': [{'name': 'Artist 2'}, {'name': 'Artist 3'}],
            'genre': 'Rock'
        }
    },

]


data = []
for brano in tracks:
    track_info = brano['track']
    for artist in track_info['artists']:
        data.append({
            'track_name': track_info['name'],
            'album_name': track_info['album']['name'],
            'album_image': track_info['album']['images'][0]['url'] if track_info['album']['images'] else None,
            'artist_name': artist['name'],
            'genre': track_info['genre']
        })

df = pd.DataFrame(data)
