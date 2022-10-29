import os
import spotipy
import numpy as np
import pandas as pd

from math import trunc
from flask import Flask, session, request, redirect, render_template

def cache_auth_spoti(id):

    if id == 1:

        cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
        if not auth_manager.validate_token(cache_handler.get_cached_token()):
            return redirect('/')
        return spotipy.Spotify(auth_manager=auth_manager)

    elif id == 0:

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
        return spotipy.Spotify(auth_manager=auth_manager)

    else:
        return 400

def get_playlists(spotify):
    # Could be done better with the use of if smth['next'] to repeat instead
    playlist_name = []
    playlist_url = []
    playlist_size = []
    playlist_id = []
    playlist_image = []
    playlist_columns = ['name', 'url', 'size', 'id', 'image']

    # This function retrives the name of all the playlists, storing them in a dictionary named playlists 
    total = spotify.current_user_playlists(limit=1)['total']
    reps = trunc(total / 50)
    remainder = total - reps * 50
    print(reps)
    for y in range(reps):
        playlists_raw = spotify.current_user_playlists(limit=50, offset=y*50) #check if this works properly later

        for x in range(50):
            playlist_name.append(playlists_raw['items'][x]['name'])
            playlist_url.append(playlists_raw['items'][x]['external_urls']['spotify'])
            playlist_size.append(playlists_raw['items'][x]['tracks']['total'])
            playlist_id.append(playlists_raw['items'][x]['id'])
            playlist_image.append(playlists_raw['items'][x]['images'][0]['url'])


    playlists_raw = spotify.current_user_playlists(limit=50, offset=(reps)*50) #check if this works properly later

    for x in range(remainder):
        playlist_name.append(playlists_raw['items'][x]['name'])
        playlist_url.append(playlists_raw['items'][x]['external_urls']['spotify'])
        playlist_size.append(playlists_raw['items'][x]['tracks']['total'])
        playlist_id.append(playlists_raw['items'][x]['id'])
        playlist_image.append(playlists_raw['items'][x]['images'][0]['url'])
    
    playlist_df = pd.DataFrame(np.column_stack([playlist_name, playlist_url, playlist_size, playlist_id, playlist_image]), 
                                                columns=playlist_columns)

    return playlist_df

def get_tracks(spotify, playlist_id):

    playlist = spotify.playlist_tracks(playlist_id, fields=None, market=None)
    tracks = playlist['items']
    # Repeats till every track is added to the list - there is a limit of 100 imposed for the function playlist_tracks
    while playlist['next']: 
        playlist = spotify.next(playlist)
        tracks.extend(playlist['items'])

    indiv = [] # tracks[x]['track']['name']
    popularity = [] # tracks[x]['track']['popularity']
    preview_url = [] # tracks[x]['track']['preview_url']
    track_id = [] # tracks[x]['track']['id']


    for track in tracks:
        indiv.append(track['track']['name'])
        popularity.append(track['track']['popularity'])
        preview_url.append(track['track']['preview_url']) # tracks[x]['track']['preview_url']
        track_id.append(track['track']['id']) # tracks[x]['track']['id']

    track_columns = ['name', 'poplarity', 'preview_url', 'track_id']
    tracks_df = pd.DataFrame(np.column_stack([indiv, popularity, preview_url, track_id]), columns=track_columns)

    return tracks_df