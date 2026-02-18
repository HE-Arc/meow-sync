import os
import base64
import requests
from flask import Flask, redirect, request, session, url_for
from dotenv import load_dotenv

from SpotifyApi import *


load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:8000/spotify/callback"

app = Flask(__name__)
app.secret_key = "super_secret_key_change_this"

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1"


@app.route("/")
def login():
    scope = "playlist-read-private"

    auth_params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "scope": scope,
        "redirect_uri": REDIRECT_URI,
    }

    url = requests.Request("GET", AUTH_URL, params=auth_params).prepare().url
    return redirect(url)


@app.route("/spotify/callback")
def callback():
    code = request.args.get("code")

    auth_header = base64.b64encode(
        f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
    ).decode()

    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    token_headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = requests.post(TOKEN_URL, data=token_data, headers=token_headers)
    token_info = response.json()

    session["access_token"] = token_info["access_token"]

    return redirect(url_for("playlists"))


@app.route("/playlists")
def playlists():
    access_token = session.get("access_token")

    if not access_token:
        return redirect("/")

    spotify_api = SpotifyApi(access_token=access_token)

    playlist_list = spotify_api.get_all_playlists().data

    output = "<h1>Your Playlists</h1><ul>"

    for playlist in playlist_list:
        playlist_url = f"/playlists/{playlist.id}"
        output += f"<li> <img src=\"{playlist.image_url}\" height=\"50px\" width=\"50px\"> {playlist.id} <br> <a href=\"{playlist_url}\"> {playlist.title} </a> | {playlist.author} <br> {playlist.description}</li>"

    output += "</ul>"

    return output

@app.route("/playlists/<playlist_id>")
def playlist(playlist_id):
    access_token = session.get("access_token")

    if not access_token:
        return redirect("/")

    spotify_api = SpotifyApi(access_token=access_token)
    playlist_res = spotify_api.get_playlist(playlist_id=playlist_id)
    
    playlist = playlist_res.data

    output = f"<h1>{"playlist.title"}</h1><ul>"

    for song in playlist.songs:
        output += f"<li> <img src=\"{song.image_url}\" height=\"50px\" width=\"50px\"> {song.id} <br>  {song.title} ({song.duration_ms / 1000 / 60}) | {song.artist} <br> {song.release_date}</li>"

    output += "</ul>"

    return output
    

if __name__ == "__main__":
    app.run(debug=True, port=8000)
