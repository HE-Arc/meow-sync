import os
import base64
import requests
from flask import Flask, json, redirect, request, session, url_for
from dotenv import load_dotenv
from YoutubeApi import YoutubeApi


load_dotenv()

YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("YOUTUBE_REDIRECT_URI")


app = Flask(__name__)
app.secret_key = "super_secret_key_change_this"

YOUTUBE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
YOUTUBE_TOKEN_URL = "https://oauth2.googleapis.com/token"
YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"


@app.route("/youtube/playlists")
def playlists_youtube():
    access_token = session.get("access_token")
    if not access_token:
        return redirect("/")
    youtube_api = YoutubeApi(access_token=access_token)
    response = youtube_api.get_all_playlists()


    playlist_list = response.data

    output = """
    <h1>Your Playlists</h1>
    <table border="1" cellpadding="8" cellspacing="0">
        <tr>
            <th>Image</th>
            <th>ID</th>
            <th>Title</th>
            <th>Author</th>
            <th>Description</th>
        </tr>
    """

    for playlist in playlist_list:
        playlist_url = f"/youtube/playlists/{playlist.id}"
        output += f"""
        <tr>
            <td>
                <img src="{playlist.image_url}" height="50px" width="50px">
            </td>
            <td>{playlist.id}</td>
            <td>
                <a href="{playlist_url}">{playlist.title}</a>
            </td>
            <td>{playlist.author}</td>
            <td>{playlist.description}</td>
        </tr>
        """

    output += "</table>"

    return output

@app.route("/youtube")
def login():
    scope = " https://www.googleapis.com/auth/youtube"

    auth_params = {
        "response_type": "code",
        "client_id": YOUTUBE_CLIENT_ID,
        "scope": scope,
        "redirect_uri": REDIRECT_URI,
    }

    url = requests.Request("GET", YOUTUBE_AUTH_URL, params=auth_params).prepare().url
    return redirect(url)


@app.route("/youtube/callback")
def callback():
    code = request.args.get("code")
    id_client = YOUTUBE_CLIENT_ID
    secret_client = YOUTUBE_CLIENT_SECRET
    grant_type = "authorization_code"
    redirect_uri = REDIRECT_URI

    response = requests.post(YOUTUBE_TOKEN_URL, data={
        "client_id": id_client,
        "client_secret": secret_client,
        "grant_type": grant_type,
        "code": code,
        "redirect_uri": redirect_uri
    })
    token_info = response.json()

    session["access_token"] = token_info["access_token"]

    return redirect(url_for("playlists_youtube"))


@app.route("/youtube/playlists/<playlist_id>")
def youtube_playlist(playlist_id):
    access_token = session.get("access_token")

    if not access_token:
        return redirect("/youtube")

    youtube_api = YoutubeApi(access_token=access_token)
    playlist_res = youtube_api.get_playlist(playlist_id=playlist_id)
    
    playlist = playlist_res.data
    
    output = f"""
    <h1>{playlist.title} | count: {len(playlist.songs)} | id: {playlist.id}</h1>
    <table border="1" cellpadding="8" cellspacing="0">
        <tr>
            <th>Image</th>
            <th>ID</th>
            <th>Title</th>
            <th>Duration (minutes)</th>
            <th>Artist</th>
            <th>Release Date</th>
        </tr>
    """

    for song in playlist.songs:
        output += f"""
        <tr>
            <td>
                <img src="{song.image_url}" height="50px" width="50px">
            </td>
            <td>{song.id}</td>
            <td>{song.title}</td>
            <td>{song.get_formatted_duration()}</td>
            <td>{song.artist}</td>
            <td>{song.release_date}</td>
        </tr>
        """

    output += "</table>"

    return output


if __name__ == "__main__":
    app.run(debug=True, port=8000)
