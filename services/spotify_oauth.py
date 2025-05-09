#IMPORT
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# CREDENZIALI DI AUTENTICAZIONE PER L'API DI SPOTIFY
SPOTIFY_CLIENT_ID = "af4cae999c184ad7b760fb8c51b60d60"
SPOTIFY_CLIENT_SECRET = "9d1c008a6aaa4a969b178224406d5a73"
SPOTIFY_REDIRECT_URI = "https://5004-santianaale-refactoring-frkm85kw10z.ws-eu118.gitpod.io/callback"

# CONFIGURAZIONE DELL'OAUTH PER L'AUTENTICAZIONE CON SPOTIFY
sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-read-private",
    show_dialog=True 
)

def get_spotify_object(token_info):
    return spotipy.Spotify( auth=token_info['access_token'])