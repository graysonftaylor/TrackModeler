import spotipy
import json
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

if __name__ == '__main__':
    clientId = input('Client id: ')
    clientSec = input('Client secret: ')
    auth_manager = SpotifyClientCredentials(
        client_id=clientId, client_secret=clientSec)
    sp = spotipy.Spotify(auth_manager=auth_manager)
    id = input('Track id: ')
    with open('result.txt', 'w') as f:
        f.write(str(sp.audio_features(id)[0]))
        # f.write(str(sp.audio_analysis(id)))
