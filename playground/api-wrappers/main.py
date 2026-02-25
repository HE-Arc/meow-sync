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


@app.route("/spotify")
def spotify_login():
    scope = "playlist-read-private,playlist-modify-public,playlist-modify-private"

    auth_params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "scope": scope,
        "redirect_uri": REDIRECT_URI,
    }

    url = requests.Request("GET", AUTH_URL, params=auth_params).prepare().url
    return redirect(url)


@app.route("/spotify/callback")
def spotify_callback():
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


@app.route("/spotify/playlists")
def spotify_playlists():
    access_token = session.get("access_token")

    if not access_token:
        return redirect("/spotify")

    spotify_api = SpotifyApi(access_token=access_token)

    playlist_list = spotify_api.get_all_playlists().data

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
        playlist_url = f"/spotify/playlists/{playlist.id}"
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

@app.route("/spotify/playlists/<playlist_id>")
def spotify_playlist(playlist_id):
    access_token = session.get("access_token")

    if not access_token:
        return redirect("/spotify")

    spotify_api = SpotifyApi(access_token=access_token)
    playlist_res = spotify_api.get_playlist(playlist_id=playlist_id)
    
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

@app.route("/spotify/playlist/add-songs", methods=["GET"])
def spotify_playlist_form_add_songs():
    return """
        <h2>Create Playlist</h2>
        <form method="POST" action="/spotify/playlist/add-songs">
            <label>Playlist ID:</label><br>
            <input type="text" name="playlist_id" required><br><br>

            <label>Song IDs (comma separated):</label><br>
            <input type="text" name="song_ids" required><br><br>

            <button type="submit">Submit</button>
        </form>
    """

@app.route("/spotify/playlist/add-songs", methods=["POST"])
def spotify_submit_playlist_form_add_songs():
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
        return redirect("/spotify")

    spotify_api = SpotifyApi(access_token=access_token)
    spotify_api.add_to_playlist(playlist_id, song_ids)
    
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
    

@app.route("/spotify/playlist/remove-songs", methods=["GET"])
def spotify_playlist_form_remove_songs():
    return """
        <h2>Create Playlist</h2>
        <form method="POST" action="/spotify/playlist/remove-songs">
            <label>Playlist ID:</label><br>
            <input type="text" name="playlist_id" required><br><br>

            <label>Song IDs (comma separated):</label><br>
            <input type="text" name="song_ids" required><br><br>

            <button type="submit">Submit</button>
        </form>
    """

@app.route("/spotify/playlist/remove-songs", methods=["POST"])
def spotify_submit_playlist_form_remove_songs():
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
        return redirect("/spotify")

    spotify_api = SpotifyApi(access_token=access_token)
    spotify_api.remove_from_playlist(playlist_id, song_ids)
    
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

if __name__ == "__main__":
    app.run(debug=True, port=8000)
