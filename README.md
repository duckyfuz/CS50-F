# BAD MUSIC BOT
#### Video Demo:  https://www.youtube.com/watch?v=1_MG21vB3es
#### Github Repo: https://github.com/duckyfuz/CS50-F
### Description:
This bot utilises the spotify api along with the spotipy library to read the user's liked songs and give suggestions accordingly.

This project was creaated to add addional functions to spotify throught the web api. While the project is not entirely complete, one is currently able to view a list of their playlists, the individual songs in the playlists, as well as averaged data on the songs in their playlists - such as danceability, loundness, etc.

Throughout the process of creating this web app, I have learn more about the authentication process Spotify uses as well as OAuth 2.0. I have learnt how to upload projects to github, as well as to update and maintain repositories. I did research on how to use Pandas and Numpy to be able to more efficiently organize and manipulate data from the spotiy api. 

The frontend of the project is not very well done. I am much more interested in the backend of web apps, and hence put more of a piority in making functions for the web app. 

Currently some of the other functions that are WIP include: 
1. A song reccomender
2. Playlist sorter

The html pages use jinja syntax to grab data from the dataframes and lists. 

Here is a list of the files and folders included with the project:
1. static/
2. templates/
3. app.py
4. helpers.py
5. requirements.txt

The folder static contains images that are used in the web app.

The folder templates contain html documents, including an layout.html which every other html file makes use of. It contains the header of the webpage, and it returns a different one based on whether the user is logged in or not. 

The python file app.py uses flask to combine python and html. There are various functions inside to take data from spotipy and pass it over to the html files. Similarly, the file hempers.py is an extention of app.py - by moving complicated functions over to a differnent file, app.py becomes much more readable. 

The file requirements.txt contains a list of all the libraries needed to run the program. Note that the version of the spotipy library used is yet to be released - I had to manally download it from the repo on github. This is because the latest unreleased version has added functionality for easier authentication. 

##### Spotify API: https://developer.spotify.com/documentation/web-api/
##### Spotipy Library: https://spotipy.readthedocs.io/en/master/