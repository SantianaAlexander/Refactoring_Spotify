import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_CLIENT_ID = "af4cae999c184ad7b760fb8c51b60d60"
SPOTIFY_CLIENT_SECRET = "9d1c008a6aaa4a969b178224406d5a73"
SPOTIFY_REDIRECT_URI = "https://sturdy-space-yodel-g95pvgpr974c9g6w-5002.app.github.dev/callback"

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-library-read",
    show_dialog=True 
)

def get_spotify_object(token_info):
    return spotipy.Spotify( auth=token_info['access_token'])