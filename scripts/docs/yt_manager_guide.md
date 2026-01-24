# YouTube Manager (`yt_manager.py`) Detailed Guide

`duh-ytdl` is a comprehensive YouTube CLI for downloading media, synchronizing local libraries with remote playlists, and maintaining metadata integrity.

---

## Global Options

These flags apply regardless of the subcommand used.

- `-c, --cookies FILE`: Path to a Netscape formatted cookies file. Required for age-restricted videos or Premium-only bitrates. Default: `~/.config/scripts/cookies.txt`.
- `-v, --verbose`: Enables verbose output, showing raw `yt-dlp` commands and internal debugging logs.
- `-h, --help`: Display help information for the tool or a specific subcommand.

---

## Subcommands

### 1. `download`

Used for one-off downloads of videos or playlists.

**Usage:** `duh-ytdl download <URL_OR_QUERY> <OUTPUT_PATH>`

- `URL_OR_QUERY`: A direct YouTube URL (video or playlist) or a search query (downloads the first result).
- `OUTPUT_PATH`: Directory or filename for the download.
- `-t, --type [mp3|mp4]`: Output format. `mp3` includes high-quality audio extraction and metadata tagging. `mp4` merges best video and audio. (Default: `mp3`)
- `-p, --parallel N`: Number of concurrent downloads. (Default: `1`)
- `-f, --force`: Re-download the file even if it already exists in the output directory.

---

### 2. `sync`

Synchronizes a local directory with a YouTube playlist. Only downloads missing tracks.

**Usage:** `duh-ytdl sync <PLAYLIST_OR_NAME> [DIRECTORY]`

- `PLAYLIST_OR_NAME`: A YouTube playlist URL or the name of a saved playlist (see `add`).
- `DIRECTORY`: Target directory. Optional if using a saved playlist name.
- `-t, --type [mp3|mp4]`: Target file format for the sync.
- `-p, --parallel N`: Number of concurrent downloads for missing tracks.
- `-f, --force`: Force re-download of all tracks in the playlist.
- `--prune`: **Destructive.** Deletes local files in the target directory that are no longer present in the YouTube playlist.
- `--dry-run`: Shows which tracks are missing and which files would be pruned without executing any changes.
- `--all`: Synchronizes every playlist currently in the saved registry.
- `--to-file FILE`: Instead of downloading, saves a list of missing tracks to a JSON file.

---

### 3. `batch`

Downloads a list of tracks defined in a JSON file. Useful for restoring libraries or migrating metadata.

**Usage:** `duh-ytdl batch <JSON_FILE> <DIRECTORY>`

- `JSON_FILE`: Path to a JSON file containing an array of track objects (must include `url`).
- `DIRECTORY`: Output directory for the downloads.
- `-t, --type [mp3|mp4]`, `-p, --parallel N`, `-f, --force`: Same as `download`.

---

### 4. `m3u`

Generates an M3U playlist file for local media players, preserving the exact order of the YouTube source.

**Usage:** `duh-ytdl m3u <PLAYLIST_OR_NAME> [DIRECTORY]`

- `PLAYLIST_OR_NAME`: A YouTube playlist URL or saved name.
- `DIRECTORY`: Directory containing the local MP3 files.
- `-o, --output FILE`: Custom path for the resulting `.m3u` file. Default is `<directory_name>.m3u`.

---

### 5. `view`

Inspects metadata for a track or playlist without downloading.

**Usage:** `duh-ytdl view <URL_OR_QUERY>`

- `URL_OR_QUERY`: URL or search term.
- `--to-file FILE`: Saves the metadata output to a JSON file instead of printing to the console.

---

### 6. `add`

Saves a playlist configuration to the local registry for simplified `sync` operations.

**Usage:** `duh-ytdl add <NAME> <URL> <DIRECTORY>`

- `NAME`: A short alias for the playlist (e.g., `work-lofi`).
- `URL`: The full YouTube playlist URL.
- `DIRECTORY`: The default local directory where this playlist should be synced.

---

### 7. `remove`

Deletes a playlist from the local registry.

**Usage:** `duh-ytdl remove <NAME>`

---

### 8. `list`

Displays all saved playlists in the registry, including their URLs and target directories.

**Usage:** `duh-ytdl list`

---

## Feature Deep Dive: Metadata & Tagging

When downloading in `mp3` mode, `yt_manager.py` performs the following automated steps:

1.  **Normalization**: Standardizes URLs and filenames.
2.  **ID3v2.3 Tagging**:
    - **Artist**: Sets the `TPE1` tag from the YouTube channel name.
    - **Title**: Sets the `TIT2` tag from the video title.
    - **Comment**: Stores the source YouTube URL in the `COMM` tag (this is critical for subsequent `sync` operations to identify the file).
3.  **Thumbnails**: Embeds the video's high-resolution thumbnail as album art.
