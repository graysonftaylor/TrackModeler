import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

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
    clientId = input('Client id: ')
    clientSec = input('Client secret: ')
    # clientId = ''
    # clientSec = ''

    authMang = SpotifyClientCredentials(clientId, clientSec)
    sp = spotipy.Spotify(auth_manager=authMang)

    trackNames, trackIds = get_track(sp, input('Album id: '))

    res = sp.audio_features(trackIds)
    df = pd.DataFrame.from_dict(res)

    df.insert(0, 'trackname', trackNames)
    df.to_csv('album.csv')
