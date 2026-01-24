# Spotify CLI (`spotify-cli.py`) Guide

`duh-spotify-cli` is a command-line interface for the Spotify API, designed to fetch and format metadata from playlists and albums for archival or integration purposes.

---

## Configuration

The tool requires Spotify Developer credentials to authenticate. You can provide these via:

1.  **Environment Variables**: `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`.
2.  **Arguments**: `--client-id` and `--client-secret` flags.
3.  **Dotenv File**: A `.env_spotify` file in the script's directory.

---

## Global Options

- `--format, -f [text|json|csv]`: Specifies the output format. (Default: `text`)
- `--output-file, -o FILE`: Writes the output to a specified file instead of standard output.
- `--limit, -l N`: Restricts the number of tracks fetched. Useful for testing or previewing.
- `--verbose, -v`: Enables debug-level logging.
- `--client-id`: Overrides the Spotify Client ID.
- `--client-secret`: Overrides the Spotify Client Secret.

---

## Commands

### 1. `playlist`

Fetches track information from a public Spotify playlist.

**Usage:** `duh-spotify-cli playlist <URL> [OPTIONS]`

**Example:**

```bash
duh-spotify-cli playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M --format json --output-file playlist_data.json
```

**Output Data:**

- Playlist Name
- Owner
- Total Track Count
- Track List (Title, Artist, Album, Duration, URI)

---

### 2. `album`

Fetches track information from a Spotify album.

**Usage:** `duh-spotify-cli album <URL> [OPTIONS]`

**Example:**

```bash
duh-spotify-cli album https://open.spotify.com/album/1ATL5GLyefJaxhQzSPVrLX --format csv
```

**Output Data:**

- Album Name
- Artist(s)
- Release Date
- Track List (Title, Artist, Duration, URI)

