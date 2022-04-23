from flask import Flask, request, redirect, url_for, render_template, session
import os
import spotipy
import json
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv


# flask app setup
load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

@app.route('/', methods=["GET","POST"])
def index():
    if request.method == "POST":
        result = sp.search(request.form["song_name"])
        return render_template("index_song.html", tracks=result["tracks"])
    return render_template("index.html")

@app.route('/features/<track_id>')
def feature(track_id):
    return json.dumps(sp.audio_features(track_id))
    
if __name__ == "__main__":
    app.run()