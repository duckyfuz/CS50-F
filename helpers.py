import os
import spotipy
import numpy as np
import pandas as pd

from math import trunc

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

    track_columns = ['name', 'popularity', 'preview_url', 'track_id']
    tracks_df = pd.DataFrame(np.column_stack([indiv, popularity, preview_url, track_id]), 
                                              columns=track_columns)

    return tracks_df

def get_song(spotify, song_id):

    song_id = list(filter(lambda item: item is not None, song_id))
    song = spotify.audio_features(song_id)

    features = [[] for _ in range(10)]
    for each in song:
        features[0].append(each['acousticness'])
        features[1].append(each['danceability'])
        features[2].append(each['duration_ms'])
        features[3].append(each['energy'])
        features[4].append(each['instrumentalness'])
        features[5].append(each['liveness'])
        features[6].append(each['loudness'])
        features[7].append(each['speechiness'])
        features[8].append(each['tempo'])
        features[9].append(each['valence'])

    averages = [[] for _ in range(10)]
    for x in range(10):
        averages[x] = round(sum(features[x]) / len(features[x]), 2)

    return averages
