import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import os

def get_track(sp, albumId):
    res = sp.album_tracks(albumId)
    trackNames = []
    trackIds = []
    for item in res['items']:
        trackNames.append(item['name'])
        trackIds.append(item['id'])
    return trackNames, trackIds

def get_feature(sp, trackIds):
    sp.audio_features(trackIds)

if __name__ == '__main__':
    if os.path.exists('client.txt'):
        with open('client.txt', 'r') as f:
            clientId = f.readline()
            clientSec = f.readline()
    else:
        clientId = input('Client id: ')
        clientSec = input('Client secret: ')

    authMang = SpotifyClientCredentials(clientId, clientSec)
    sp = spotipy.Spotify(auth_manager=authMang)

    albumId = input('Album id: ')
    trackNames, trackIds = get_track(sp, albumId)

    res = sp.audio_features(trackIds)
    df = pd.DataFrame.from_dict(res)

    df.insert(0, 'trackname', trackNames)
    df.to_csv('album_%s.csv' % albumId)
