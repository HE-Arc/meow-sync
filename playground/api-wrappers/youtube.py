import os
import base64
import requests
from flask import Flask, json, redirect, request, session, url_for
from dotenv import load_dotenv
from YoutubeApi import *


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
            <th>Id in playlist</th>
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
            <td>{song.id_in_playlist}</td>
        </tr>
        """

    output += "</table>"

    return output


@app.route("/youtube/playlist/add-songs", methods=["GET"])
def youtube_playlist_form_add_songs():
    return """
        <h2>Add Songs</h2>
        <form method="POST" action="/youtube/playlist/add-songs">
            <label>Playlist ID:</label><br>
            <input type="text" name="playlist_id" required><br><br>

            <label>Song IDs (comma separated):</label><br>
            <input type="text" name="song_ids" required><br><br>

            <button type="submit">Submit</button>
        </form>
    """

@app.route("/youtube/playlist/add-songs", methods=["POST"])
def youtube_submit_playlist_form_add_songs():
    playlist_id = request.form.get("playlist_id", "").strip()
    song_ids_raw = request.form.get("song_ids", "").strip()

    # --- Simple validation ---
    if not playlist_id:
        return "Error: playlist_id is required", 400

    if not song_ids_raw:
        return "Error: song_ids is required", 400

    # --- Parse comma-separated IDs ---
    song_ids = [
        song_id.strip()
        for song_id in song_ids_raw.split(",")
        if song_id.strip()
    ]

    if not song_ids:
        return "Error: No valid song IDs provided", 400
    
    access_token = session.get("access_token")
    if not access_token:
        return redirect("/youtube")

    youtube_api = YoutubeApi(access_token=access_token)
    response = youtube_api.add_to_playlist(playlist_id, song_ids)

    if not response.success:
        return f"Error adding songs to playlist: {response.status_code} | {response.message} | {response.data} | {response.success}"

    # --- Manually build HTML list ---
    ul_items = ""
    for song in song_ids:
        ul_items += f"<li>{song}</li>"

    # --- Build full HTML response ---
    html_response = f"""
        <h2>Playlist Submitted</h2>
        <p><strong>Playlist ID:</strong> {playlist_id}</p>

        <h3>Song IDs:</h3>
        <ul>
            {ul_items}
        </ul>
    """

    return html_response
    

@app.route("/youtube/playlist/remove-songs", methods=["GET"])
def youtube_playlist_form_remove_songs():
    return """
        <h2>Remove Songs</h2>
        <form method="POST" action="/youtube/playlist/remove-songs">
            <label>Song IDs (comma separated):</label><br>
            <input type="text" name="song_ids" required><br><br>

            <button type="submit">Submit</button>
        </form>
    """

@app.route("/youtube/playlist/remove-songs", methods=["POST"])
def youtube_submit_playlist_form_remove_songs():
    song_ids_raw = request.form.get("song_ids", "").strip()

    # --- Simple validation ---
    if not song_ids_raw:
        return "Error: song_ids is required", 400

    # --- Parse comma-separated IDs ---
    song_ids = [
        song_id.strip()
        for song_id in song_ids_raw.split(",")
        if song_id.strip()
    ]

    if not song_ids:
        return "Error: No valid song IDs provided", 400
    
    access_token = session.get("access_token")
    if not access_token:
        return redirect("/spotify")

    spotify_api = YoutubeApi(access_token=access_token)
    spotify_api.remove_from_playlist(None, song_ids)
    
    # --- Manually build HTML list ---
    ul_items = ""
    for song in song_ids:
        ul_items += f"<li>{song}</li>"

    # --- Build full HTML response ---
    html_response = f"""
        <h3>Song IDs:</h3>
        <ul>
            {ul_items}
        </ul>
    """

    return html_response


@app.route("/youtube/playlist/create", methods=["GET"])
def youtube_playlist_create():
    return """
        <h2>Create Playlist</h2>
        <form method="POST" action="/youtube/playlist/create">
            <label>Playlist Name:</label><br>
            <input type="text" name="playlist_name" required><br><br>

            <label>Playlist Descriptions:</label><br>
            <input type="text" name="playlist_description"><br><br>

            <button type="submit">Submit</button>
        </form>
    """

@app.route("/youtube/playlist/create", methods=["POST"])
def submit_youtube_playlist_create():
    playlist_name = request.form.get("playlist_name", "").strip()
    playlist_description = request.form.get("playlist_description", "").strip()

    # --- Simple validation ---
    if not playlist_name:
        return "Error: playlist_name is required", 400

    if not playlist_description:
        return "Error: playlist_description is required", 400

    access_token = session.get("access_token")
    if not access_token:
        return redirect("/youtube")

    youtube_api = YoutubeApi(access_token=access_token)
    response = youtube_api.create_playlist(ApiPlaylist(
        title=playlist_name,
        description=playlist_description,
        author="",
        image_url=None,
        playlist_id=None,
        songs=None
        ))

    return f"""
        <h2>status: {response.status_code}</h2>
        <h2>success: {response.success}</h2>
        <h2>message: {response.message}</h2>
        <hr>
        <h2>id: {response.data.id}</h2>
        <h2>author: {response.data.author}</h2>
        
    """


if __name__ == "__main__":
    app.run(debug=True, port=8000)
