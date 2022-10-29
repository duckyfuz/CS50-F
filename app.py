import os
import spotipy
import numpy as np
import pandas as pd


from flask import Flask, session, request, redirect, render_template
from flask_session import Session
from math import trunc
from helpers import get_playlists, get_tracks, cache_auth_spoti


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)


@app.route('/')
def index():

    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-library-modify user-read-currently-playing playlist-read-private playlist-modify-private',
                                            cache_handler=cache_handler,
                                            show_dialog=True)

    if request.args.get("code"):
        # Step 2. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 1. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return render_template("login.html", logged=False, auth_url = auth_url)

    # Step 3. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    return render_template("index.html", logged=True, spotify=spotify)



@app.route('/logout')
def logout():
    session.pop("token_info", None)
    return redirect('/')


@app.route('/playlists')
def playlists():

    spotify = cache_auth_spoti(1)

    playlist_df = get_playlists(spotify)
    playlist_list = playlist_df.values.tolist()

    return render_template("playlists.html", logged=True, playlist_list = playlist_list)


@app.route('/modify', methods=['GET', 'POST'])
def modify():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        spotify = cache_auth_spoti(1)

        playlist_id = request.form.get("playlist_id")

        tracks = get_tracks(spotify, playlist_id)
        

        return render_template("modify.html", playlist=tracks)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return redirect("/playlists")


@app.route('/currently_playing')
def currently_playing():

    spotify = cache_auth_spoti(1)

    track = spotify.current_user_playing_track()
    if not track is None:
        return track
    return "No track currently playing."


@app.route('/current_user')
def current_user():

    spotify = cache_auth_spoti(1)

    return spotify.current_user()


'''
Following lines allow application to be run more conveniently with
`python app.py` (Make sure you're using python3)
(Also includes directive to leverage pythons threading capacity.)
'''
if __name__ == '__main__':
    app.run(debug=True, 
            threaded=True, 
            port=int(os.environ.get("PORT",
                                    os.environ.get("SPOTIPY_REDIRECT_URI", 8080).split(":")[-1])))


"""
Prerequisites
    pip3 install spotipy Flask Flask-Session
    // from your [app settings](https://developer.spotify.com/dashboard/applications)
    export SPOTIPY_CLIENT_ID=client_id_here
    export SPOTIPY_CLIENT_SECRET=client_secret_here
    export SPOTIPY_REDIRECT_URI='http://127.0.0.1:8080' // must contain a port
    // SPOTIPY_REDIRECT_URI must be added to your [app settings](https://developer.spotify.com/dashboard/applications)
    OPTIONAL
    // in development environment for debug output
    export FLASK_ENV=development
    // so that you can invoke the app outside of the file's directory include
    export FLASK_APP=/path/to/spotipy/examples/app.py
 
    // on Windows, use `SET` instead of `export`
Run app.py
    python3 app.py OR python3 -m flask run
    NOTE: If receiving "port already in use" error, try other ports: 5000, 8090, 8888, etc...
        (will need to be updated in your Spotify app and SPOTIPY_REDIRECT_URI variable)
"""