import os
import spotipy
import numpy as np
import pandas as pd

from math import trunc

def get_playlists(spotify):
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