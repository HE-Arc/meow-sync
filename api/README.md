# Meow-sync API
This is the backend for Meow-Sync, a playlist synchronization tool. It is built in django with Django-rest-framework.

## Development
Copy the env examples:
```bash
$ cp .env.example .env
```
To run the backend in development mode, you'll first need to have a Spotify and Youtube OAuth app. For both, the redirect URI is `http://127.0.0.1:5173/login_callback`.

For YouTube, follow [these](https://developers.google.com/youtube/v3/guides/auth/server-side-web-apps#creatingcred) steps from the official documentation to create an app and fill the `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET` in the `.env`.

For Spotify, you'll need a Premium account (Thanks spotify). Then follow the "Create an app" section from [here](https://developer.spotify.com/documentation/web-api/tutorials/getting-started#create-an-app) and fill the `SPOTIFIY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` in the `.env`. You will need to enable **both** `Web API` and `Web Playback SDK`.

For both of these apps, you'll need to whitelist users(other than you) so that they can login.

We are using [uv](https://github.com/astral-sh/uv) to manage python dependencies, you can install them and run the project with:
```bash
$ uv sync
$ uv run manage.py migrate
$ uv run manage.py runserver
```