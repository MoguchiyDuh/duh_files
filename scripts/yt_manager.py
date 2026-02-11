#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["mutagen", "colorama", "argcomplete"]
# ///

"""YouTube playlist manager: download, sync, and create M3U playlists."""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import argcomplete
from colorama import Fore, Style, init as colorama_init
from mutagen.id3 import COMM, ID3, TIT2, TPE1
from mutagen.mp3 import MP3

if TYPE_CHECKING:
    from argparse import Namespace

colorama_init(autoreset=True)

FileType = Literal["mp3", "mp4"]

# ============================================================================
# Logging
# ============================================================================

def setup_logger(verbose: bool = False) -> logging.Logger:
    """Configure logger. Only outputs with verbose flag."""
    logger = logging.getLogger("duh-ytdl")
    logger.handlers.clear()
    logger.propagate = False

    if verbose:
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter(f"{Fore.CYAN}[%(levelname)s]{Style.RESET_ALL} %(message)s")
        )
        logger.addHandler(handler)
    else:
        logger.setLevel(logging.WARNING)

    return logger


log = setup_logger()


# ============================================================================
# Config
# ============================================================================

PLAYLISTS_FILE = Path(__file__).resolve().parent / "playlists.json"


@dataclass
class Config:
    """Shared configuration for operations."""
    cookies: Path | None = None
    verbose: bool = False
    file_type: FileType = "mp3"
    parallel: int = 1
    force: bool = False
    segment: str | None = None

    @classmethod
    def from_args(cls, args: Namespace) -> Config:
        return cls(
            cookies=args.cookies,
            verbose=args.verbose,
            file_type=getattr(args, "type", "mp3"),
            parallel=getattr(args, "parallel", 1),
            force=getattr(args, "force", False),
            segment=getattr(args, "segment", None),
        )


# ============================================================================
# Saved Playlists
# ============================================================================

@dataclass
class SavedPlaylist:
    """A saved playlist configuration."""
    name: str
    url: str
    directory: Path

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "directory": str(self.directory),
        }

    @classmethod
    def from_dict(cls, name: str, data: dict) -> SavedPlaylist:
        return cls(
            name=name,
            url=data["url"],
            directory=Path(data["directory"]).expanduser(),
        )


def load_playlists() -> dict[str, SavedPlaylist]:
    """Load saved playlists from config file."""
    if not PLAYLISTS_FILE.exists():
        return {}

    with open(PLAYLISTS_FILE) as f:
        data = json.load(f)

    return {name: SavedPlaylist.from_dict(name, pl) for name, pl in data.items()}


def save_playlists(playlists: dict[str, SavedPlaylist]) -> None:
    """Save playlists to config file."""
    data = {name: pl.to_dict() for name, pl in playlists.items()}

    with open(PLAYLISTS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_playlist(name: str) -> SavedPlaylist | None:
    """Get a saved playlist by name."""
    playlists = load_playlists()
    return playlists.get(name)


def resolve_playlist(name_or_url: str) -> tuple[str, Path | None]:
    """Resolve playlist name to URL and directory. Returns (url, directory)."""
    if is_url(name_or_url):
        return name_or_url, None

    playlist = get_playlist(name_or_url)
    if playlist:
        return playlist.url, playlist.directory

    # Not a URL and not a saved playlist
    raise ValueError(f"Unknown playlist: {name_or_url}")


# ============================================================================
# URL Utilities
# ============================================================================

def normalize_url(url: str) -> str:
    """Normalize YouTube URL to standard watch format."""
    if "youtube.com" not in url and "youtu.be" not in url:
        return url

    video_id: str | None = None

    if "watch?v=" in url:
        video_id = url.split("watch?v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
    elif "/watch/" in url:
        video_id = url.split("/watch/")[1].split("?")[0]

    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    return url


def is_playlist_url(url: str) -> bool:
    """Check if URL is a YouTube playlist."""
    return "list=" in url or "/playlist" in url


def is_url(s: str) -> bool:
    """Check if string is a URL."""
    return s.startswith(("http://", "https://"))


def detect_input_type(input_str: str) -> Literal["url", "playlist", "search"]:
    """Detect input type: single url, playlist, or search query."""
    if is_url(input_str):
        return "playlist" if is_playlist_url(input_str) else "url"
    return "search"


# ============================================================================
# Filesystem Utilities
# ============================================================================

INVALID_CHARS = "/\\:*?\"<>|"


def sanitize_filename(name: str) -> str:
    """Remove invalid filesystem characters."""
    for char in INVALID_CHARS:
        name = name.replace(char, "-")
    return name.strip(". ")


def make_filename(artist: str, title: str, ext: str) -> str:
    """Create sanitized filename from metadata."""
    return sanitize_filename(f"{artist} - {title}.{ext}")


# ============================================================================
# yt-dlp Wrapper
# ============================================================================

class YtdlpError(Exception):
    """yt-dlp command failed."""
    pass


def run_ytdlp(args: list[str], capture: bool = True, verbose: bool = False) -> str:
    """Execute yt-dlp command."""
    cmd = ["yt-dlp", *args]
    log.debug(f"Running: {' '.join(cmd)}")

    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        else:
            if verbose:
                subprocess.run(cmd, check=True)
            else:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return ""
    except subprocess.CalledProcessError as e:
        raise YtdlpError(f"yt-dlp failed: {e.stderr or e}") from e


def build_download_args(
    url: str,
    output: Path,
    file_type: FileType,
    cookies: Path | None = None,
    segment: str | None = None,
) -> list[str]:
    """Build yt-dlp arguments for downloading."""
    args = ["--no-playlist", "-o", str(output)]

    if segment:
        args.extend(["--download-sections", f"*{segment}"])

    if file_type == "mp3":
        args.extend([
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--embed-thumbnail",
            "--convert-thumbnails", "jpg",
        ])
    else:  # mp4
        args.extend([
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
        ])

    if cookies and cookies.exists():
        args.extend(["--cookies", str(cookies)])
        log.debug(f"Using cookies: {cookies}")

    args.append(url)
    return args


# ============================================================================
# Track Data
# ============================================================================

@dataclass
class Track:
    """Track metadata."""
    artist: str
    title: str
    url: str
    id: int = 0  # Position in playlist

    def to_dict(self) -> dict:
        return {"id": self.id, "artist": self.artist, "title": self.title, "url": self.url}

    @classmethod
    def from_dict(cls, data: dict) -> Track:
        return cls(
            artist=data.get("artist", "Unknown"),
            title=data.get("title", "Unknown"),
            url=data["url"],
            id=data.get("id", 0),
        )

    def filename(self, ext: str) -> str:
        return make_filename(self.artist, self.title, ext)


def search_youtube(query: str, cookies: Path | None = None) -> str:
    """Search YouTube, return first result URL."""
    log.debug(f"Searching: {query}")
    args = [f"ytsearch1:{query}", "--get-id"]
    if cookies and cookies.exists():
        args.extend(["--cookies", str(cookies)])

    video_id = run_ytdlp(args)
    return f"https://www.youtube.com/watch?v={video_id}"


@dataclass
class TrackDetails:
    """Extended track metadata for display."""
    artist: str
    title: str
    url: str
    upload_date: str | None = None
    duration: int = 0
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    categories: list[str] = field(default_factory=list)
    description: str = ""

    def to_track(self) -> Track:
        return Track(artist=self.artist, title=self.title, url=self.url)

    def to_dict(self) -> dict:
        return {
            "artist": self.artist,
            "title": self.title,
            "url": self.url,
            "upload_date": self.upload_date,
            "duration": self.duration,
            "view_count": self.view_count,
            "like_count": self.like_count,
            "comment_count": self.comment_count,
            "categories": self.categories,
            "description": self.description,
        }

    @property
    def duration_str(self) -> str:
        """Format duration as MM:SS or HH:MM:SS."""
        if not self.duration:
            return "0:00"
        m, s = divmod(self.duration, 60)
        h, m = divmod(m, 60)
        return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"

    @property
    def date_str(self) -> str:
        """Format upload date as YYYY-MM-DD."""
        if not self.upload_date or len(self.upload_date) != 8:
            return "Unknown"
        return f"{self.upload_date[:4]}-{self.upload_date[4:6]}-{self.upload_date[6:]}"


def get_track_info(url: str, cookies: Path | None = None) -> Track:
    """Fetch single track metadata (minimal)."""
    details = get_track_details(url, cookies)
    return details.to_track()


def get_track_details(url: str, cookies: Path | None = None) -> TrackDetails:
    """Fetch detailed track metadata."""
    args = ["--dump-json"]
    if cookies and cookies.exists():
        args.extend(["--cookies", str(cookies)])
    args.append(url)

    log.debug(f"Fetching info: {url}")
    data = json.loads(run_ytdlp(args))

    return TrackDetails(
        artist=data.get("channel", "Unknown"),
        title=data.get("title", "Unknown"),
        url=normalize_url(url),
        upload_date=data.get("upload_date"),
        duration=data.get("duration", 0),
        view_count=data.get("view_count", 0),
        like_count=data.get("like_count", 0),
        comment_count=data.get("comment_count", 0),
        categories=data.get("categories", []),
        description=data.get("description", "")[:500],  # Truncate
    )


def get_playlist_info(url: str, cookies: Path | None = None) -> tuple[str, list[Track]]:
    """Fetch playlist metadata. Returns (playlist_title, tracks)."""
    args = ["--flat-playlist", "--dump-json"]
    if cookies and cookies.exists():
        args.extend(["--cookies", str(cookies)])
    args.append(url)

    log.debug(f"Fetching playlist: {url}")
    output = run_ytdlp(args)

    tracks: list[Track] = []
    playlist_title = "Unknown Playlist"

    for i, line in enumerate(output.splitlines(), 1):
        if not line.strip():
            continue
        data = json.loads(line)

        # First entry might have playlist info
        if i == 1 and "playlist_title" in data:
            playlist_title = data["playlist_title"]

        video_id = data.get("id")
        if not video_id:
            continue

        tracks.append(Track(
            artist=data.get("channel", "Unknown"),
            title=data.get("title", "Unknown"),
            url=f"https://www.youtube.com/watch?v={video_id}",
            id=i,
        ))

    return playlist_title, tracks


# ============================================================================
# ID3 Metadata
# ============================================================================

def get_mp3_url(filepath: Path) -> str | None:
    """Extract YouTube URL from MP3 comment field."""
    try:
        audio = MP3(filepath, ID3=ID3)
        for comment in audio.tags.getall("COMM"):
            text = str(comment.text[0]) if comment.text else ""
            if "youtube.com" in text or "youtu.be" in text:
                return normalize_url(text)
    except Exception:
        pass
    return None


def set_mp3_metadata(filepath: Path, artist: str, title: str, url: str) -> None:
    """Set ID3 tags on MP3 file."""
    log.debug(f"Setting metadata: {filepath}")
    audio = MP3(filepath, ID3=ID3)

    try:
        audio.add_tags()
    except Exception:
        pass  # Tags already exist

    audio.tags["TPE1"] = TPE1(encoding=3, text=artist)
    audio.tags["TIT2"] = TIT2(encoding=3, text=title)
    audio.tags["COMM"] = COMM(encoding=3, lang="eng", desc="", text=url)
    audio.save(v2_version=3)


# ============================================================================
# Download
# ============================================================================

@dataclass
class DownloadResult:
    """Result of a download operation."""
    track: Track
    success: bool
    path: Path | None = None
    error: str | None = None
    skipped: bool = False


def download_track(track: Track, output_dir: Path, cfg: Config, filename: str | None = None) -> DownloadResult:
    """Download single track to directory."""
    if not filename:
        filename = track.filename(cfg.file_type)
    
    output_path = output_dir / filename

    # Skip if exists and not forcing
    if output_path.exists() and not cfg.force:
        log.debug(f"Skipping (exists): {output_path}")
        return DownloadResult(track, success=True, path=output_path, skipped=True)

    # Download to temp, then move (atomic)
    temp_dir = Path(tempfile.mkdtemp(prefix="duh-ytdl-"))
    temp_output = temp_dir / filename

    try:
        args = build_download_args(track.url, temp_output, cfg.file_type, cfg.cookies, cfg.segment)
        run_ytdlp(args, capture=False, verbose=cfg.verbose)

        # Find downloaded file (extension might differ before conversion)
        downloaded = list(temp_dir.glob(f"*.{cfg.file_type}"))
        if not downloaded:
            raise YtdlpError(f"No {cfg.file_type} file found after download")

        shutil.move(str(downloaded[0]), str(output_path))

        # Set metadata for mp3
        if cfg.file_type == "mp3":
            set_mp3_metadata(output_path, track.artist, track.title, track.url)

        log.debug(f"Downloaded: {output_path}")
        return DownloadResult(track, success=True, path=output_path)

    except Exception as e:
        return DownloadResult(track, success=False, error=str(e))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def download_tracks(
    tracks: list[Track],
    output_dir: Path,
    cfg: Config,
    callback: callable | None = None,
) -> list[DownloadResult]:
    """Download multiple tracks, optionally in parallel."""
    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[DownloadResult] = []

    if cfg.parallel <= 1:
        # Sequential download
        for track in tracks:
            result = download_track(track, output_dir, cfg)
            results.append(result)
            if callback:
                callback(result)
    else:
        # Parallel download
        print_lock = threading.Lock()

        def download_with_lock(track: Track) -> DownloadResult:
            return download_track(track, output_dir, cfg)

        with ThreadPoolExecutor(max_workers=min(cfg.parallel, 10)) as executor:
            futures = {executor.submit(download_with_lock, t): t for t in tracks}

            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                if callback:
                    with print_lock:
                        callback(result)

    return results


# ============================================================================
# Output Helpers
# ============================================================================

def print_success(msg: str) -> None:
    print(f"{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")


def print_error(msg: str) -> None:
    print(f"{Fore.RED}✗ {msg}{Style.RESET_ALL}")


def print_warning(msg: str) -> None:
    print(f"{Fore.YELLOW}! {msg}{Style.RESET_ALL}")


def print_track(track: Track, status: str = "") -> None:
    prefix = f"[{track.id}] " if track.id else ""
    suffix = f" - {status}" if status else ""
    print(f"  {prefix}{track.artist} - {track.title}{suffix}")


def print_result(result: DownloadResult, total: int = 0) -> None:
    """Print download result with status."""
    track = result.track
    prefix = f"[{track.id}/{total}] " if total else (f"[{track.id}] " if track.id else "")

    if result.skipped:
        print(f"  {prefix}{track.artist} - {track.title} - {Fore.YELLOW}skipped{Style.RESET_ALL}")
    elif result.success:
        print(f"  {prefix}{track.artist} - {track.title} - {Fore.GREEN}done{Style.RESET_ALL}")
    else:
        print(f"  {prefix}{track.artist} - {track.title} - {Fore.RED}failed: {result.error}{Style.RESET_ALL}")


# ============================================================================
# Local File Scanning
# ============================================================================

def scan_local_files(directory: Path, file_type: FileType) -> dict[str, Path]:
    """Scan directory for files and extract URLs. Returns url -> path mapping."""
    url_to_file: dict[str, Path] = {}

    if not directory.exists():
        return url_to_file

    for filepath in directory.glob(f"*.{file_type}"):
        if file_type == "mp3":
            url = get_mp3_url(filepath)
            if url:
                url_to_file[url] = filepath

    return url_to_file


# ============================================================================
# Commands
# ============================================================================

def cmd_download(args: Namespace) -> int:
    """Download single track or playlist."""
    global log
    log = setup_logger(args.verbose)
    cfg = Config.from_args(args)

    input_type = detect_input_type(args.url)
    output: Path = args.output.expanduser().resolve()

    # Handle search query
    if input_type == "search":
        print(f"Searching: {args.url}")
        url = search_youtube(args.url, cfg.cookies)
        print(f"Found: {url}")
        input_type = "url"
    else:
        url = args.url

    if input_type == "playlist":
        # Playlist download
        print("Fetching playlist...")
        title, tracks = get_playlist_info(url, cfg.cookies)
        print(f"Playlist: {title} ({len(tracks)} tracks)")

        if cfg.parallel > 1:
            print(f"Downloading with {min(cfg.parallel, 10)} workers...")

        total = len(tracks)
        results = download_tracks(
            tracks, output, cfg,
            callback=lambda r: print_result(r, total)
        )

        # Summary
        success = sum(1 for r in results if r.success and not r.skipped)
        skipped = sum(1 for r in results if r.skipped)
        failed = sum(1 for r in results if not r.success)

        print(f"\nDownloaded: {success}, Skipped: {skipped}, Failed: {failed}")
        print_success(f"Output: {output}")
    else:
        # Single track
        track = get_track_info(url, cfg.cookies)
        print(f"Track: {track.artist} - {track.title}")

        if output.is_dir():
            result = download_track(track, output, cfg)
        elif output.suffix:
            output.parent.mkdir(parents=True, exist_ok=True)
            result = download_track(track, output.parent, cfg, filename=output.name)
        else:
            output.mkdir(parents=True, exist_ok=True)
            result = download_track(track, output, cfg)

        if result.success:
            actual_filename = result.path.name if result.path else track.filename(cfg.file_type)
            print_success(f"Downloaded: {actual_filename}")
        else:
            print_error(f"Failed: {result.error}")
            return 1

    return 0


def sync_single_playlist(
    url: str,
    directory: Path,
    cfg: Config,
    dry_run: bool,
    prune: bool,
    name: str | None = None,
    to_file: Path | None = None,
) -> int:
    """Sync a single playlist. Returns exit code."""
    if name:
        print(f"\n{Fore.CYAN}=== {name} ==={Style.RESET_ALL}")

    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

    # Fetch playlist
    print("Fetching playlist...")
    title, tracks = get_playlist_info(url, cfg.cookies)
    playlist_urls = {t.url for t in tracks}
    print(f"Playlist: {title} ({len(tracks)} tracks)")

    # Scan local files
    print(f"Scanning {directory}...")
    local_urls = scan_local_files(directory, cfg.file_type)
    print(f"Local files with URLs: {len(local_urls)}")

    # Find missing (in playlist but not local)
    missing_urls = playlist_urls - set(local_urls.keys())
    missing_tracks = [t for t in tracks if t.url in missing_urls]

    # Find orphaned (local but not in playlist)
    orphaned_urls = set(local_urls.keys()) - playlist_urls
    orphaned_files = [(local_urls[url], url) for url in orphaned_urls]

    # Report
    if not missing_tracks and not orphaned_files:
        print_success("Already in sync!")
        return 0

    if missing_tracks:
        print(f"\n{Fore.YELLOW}Missing {len(missing_tracks)} tracks:{Style.RESET_ALL}")
        for t in missing_tracks[:10]:
            print_track(t)
        if len(missing_tracks) > 10:
            print(f"  ... and {len(missing_tracks) - 10} more")

    if orphaned_files:
        print(f"\n{Fore.YELLOW}Orphaned {len(orphaned_files)} files:{Style.RESET_ALL}")
        for filepath, _ in orphaned_files[:10]:
            print(f"  {filepath.name}")
        if len(orphaned_files) > 10:
            print(f"  ... and {len(orphaned_files) - 10} more")

    if dry_run:
        print(f"\n{Fore.CYAN}Dry run - no changes made{Style.RESET_ALL}")
        return 0

    # Save to file if requested (and exit)
    if to_file:
        data = [t.to_dict() for t in missing_tracks]
        with open(to_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print_success(f"Saved {len(missing_tracks)} missing tracks to {to_file}")
        return 0

    # Download missing
    if missing_tracks:
        print(f"\nDownloading {len(missing_tracks)} missing tracks...")
        if cfg.parallel > 1:
            print(f"Using {min(cfg.parallel, 10)} workers...")

        total = len(missing_tracks)
        results = download_tracks(
            missing_tracks, directory, cfg,
            callback=lambda r: print_result(r, total)
        )

        success = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)
        print(f"Downloaded: {success}, Failed: {failed}")

    # Prune orphaned
    if prune and orphaned_files:
        print(f"\nDeleting {len(orphaned_files)} orphaned files...")
        deleted = 0
        for filepath, _ in orphaned_files:
            try:
                filepath.unlink()
                print(f"  Deleted: {filepath.name}")
                deleted += 1
            except Exception as e:
                print_error(f"Failed to delete {filepath.name}: {e}")
        print(f"Deleted: {deleted}/{len(orphaned_files)}")

    print_success("Sync complete!")
    return 0


def cmd_sync(args: Namespace) -> int:
    """Sync playlist with local directory."""
    global log
    log = setup_logger(args.verbose)
    cfg = Config.from_args(args)

    dry_run = args.dry_run
    prune = args.prune
    to_file = getattr(args, "to_file", None)

    # Handle --all flag
    if getattr(args, "all", False):
        playlists = load_playlists()
        if not playlists:
            print_error("No saved playlists. Use 'add' command first.")
            return 1

        if to_file:
            print_error("--to-file not supported with --all")
            return 1

        print(f"Syncing {len(playlists)} playlists...")
        for name, pl in playlists.items():
            sync_single_playlist(pl.url, pl.directory, cfg, dry_run, prune, name, None)

        print_success(f"\nAll {len(playlists)} playlists synced!")
        return 0

    # Resolve playlist name or URL
    try:
        url, saved_dir = resolve_playlist(args.playlist)
    except ValueError as e:
        print_error(str(e))
        return 1

    # Use provided directory or saved directory
    if args.directory:
        directory = args.directory.expanduser().resolve()
    elif saved_dir:
        directory = saved_dir
    else:
        print_error("Directory required when using URL directly")
        return 1

    return sync_single_playlist(url, directory, cfg, dry_run, prune, None, to_file)


def cmd_batch(args: Namespace) -> int:
    """Batch download from JSON file."""
    global log
    log = setup_logger(args.verbose)
    cfg = Config.from_args(args)

    json_file: Path = args.json_file.expanduser().resolve()
    directory: Path = args.directory.expanduser().resolve()

    if not json_file.exists():
        print_error(f"JSON file not found: {json_file}")
        return 1

    # Load tracks
    with open(json_file) as f:
        data = json.load(f)

    tracks = [Track.from_dict(d) for d in data]
    # Assign IDs if missing
    for i, t in enumerate(tracks, 1):
        if not t.id:
            t.id = i

    print(f"Loaded {len(tracks)} tracks from {json_file.name}")

    if cfg.parallel > 1:
        print(f"Downloading with {min(cfg.parallel, 10)} workers...")

    total = len(tracks)
    results = download_tracks(
        tracks, directory, cfg,
        callback=lambda r: print_result(r, total)
    )

    # Summary
    success = sum(1 for r in results if r.success and not r.skipped)
    skipped = sum(1 for r in results if r.skipped)
    failed = sum(1 for r in results if not r.success)

    print(f"\nDownloaded: {success}, Skipped: {skipped}, Failed: {failed}")
    print_success(f"Output: {directory}")
    return 0


def cmd_m3u(args: Namespace) -> int:
    """Generate M3U playlist ordered by YouTube playlist."""
    global log
    log = setup_logger(args.verbose)

    # Resolve playlist name or URL
    try:
        url, saved_dir = resolve_playlist(args.playlist)
    except ValueError as e:
        print_error(str(e))
        return 1

    # Use provided directory or saved directory
    if args.directory:
        directory = args.directory.expanduser().resolve()
    elif saved_dir:
        directory = saved_dir
    else:
        print_error("Directory required when using URL directly")
        return 1

    output: Path = args.output or directory.with_suffix(".m3u")

    if not directory.exists():
        print_error(f"Directory not found: {directory}")
        return 1

    # Fetch playlist for ordering
    print("Fetching playlist...")
    title, tracks = get_playlist_info(url, args.cookies)
    playlist_urls = [t.url for t in tracks]
    print(f"Playlist: {title} ({len(tracks)} tracks)")

    # Scan local files
    print(f"Scanning {directory}...")
    local_urls = scan_local_files(directory, "mp3")
    print(f"Local files with URLs: {len(local_urls)}")

    # Build M3U in playlist order
    print(f"Creating M3U: {output}")
    matched = 0
    missing = 0

    with open(output, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        for url in playlist_urls:
            if url in local_urls:
                filepath = local_urls[url]
                if args.abs:
                    path_str = str(filepath.absolute())
                else:
                    try:
                        # Make relative to the M3U file's directory
                        path_str = str(filepath.relative_to(output.parent))
                    except ValueError:
                        path_str = str(filepath.absolute())
                f.write(f"{path_str}\n")
                matched += 1
            else:
                missing += 1

    print(f"Matched: {matched}/{len(playlist_urls)}")
    if missing:
        print_warning(f"Missing: {missing} tracks (not in local directory)")

    print_success(f"Saved: {output}")
    return 0


def cmd_view(args: Namespace) -> int:
    """View playlist or track info."""
    global log
    log = setup_logger(args.verbose)

    # Check if it's a saved playlist name first
    saved = get_playlist(args.url)
    if saved:
        url = saved.url
        input_type = "playlist"
    else:
        input_type = detect_input_type(args.url)

        # Handle search query
        if input_type == "search":
            print(f"Searching: {args.url}")
            url = search_youtube(args.url, args.cookies)
            print(f"Found: {url}")
            input_type = "url"
        else:
            url = args.url

    if input_type == "playlist":
        title, tracks = get_playlist_info(url, args.cookies)

        if args.to_file:
            # Save to JSON
            data = [t.to_dict() for t in tracks]
            with open(args.to_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print_success(f"Saved {len(tracks)} tracks to {args.to_file}")
        else:
            # Print to console
            print(f"\n{Fore.CYAN}{title}{Style.RESET_ALL}")
            print(f"Tracks: {len(tracks)}\n")

            for track in tracks:
                print(f"  [{track.id:3}] {track.artist} - {track.title}")

    else:
        details = get_track_details(url, args.cookies)

        if args.to_file:
            with open(args.to_file, "w", encoding="utf-8") as f:
                json.dump([details.to_dict()], f, indent=2, ensure_ascii=False)
            print_success(f"Saved to {args.to_file}")
        else:
            print(f"\n{Fore.CYAN}{details.title}{Style.RESET_ALL}")
            print(f"  Channel:   {details.artist}")
            print(f"  Date:      {details.date_str}")
            print(f"  Duration:  {details.duration_str}")
            print(f"  Views:     {details.view_count:,}")
            print(f"  Likes:     {details.like_count:,}")
            print(f"  Comments:  {details.comment_count:,}")
            if details.categories:
                print(f"  Category:  {', '.join(details.categories)}")
            print(f"  URL:       {details.url}")
            if details.description:
                print(f"\n  {Fore.CYAN}Description:{Style.RESET_ALL}")
                # Wrap description lines
                for line in details.description.split("\n")[:5]:
                    if line.strip():
                        print(f"    {line[:80]}")

    return 0


# ============================================================================
# Playlist Management Commands
# ============================================================================

def cmd_add(args: Namespace) -> int:
    """Add a playlist to saved playlists."""
    playlists = load_playlists()

    name = args.name
    url = args.url
    directory = args.directory.expanduser().resolve()

    if name in playlists:
        print_warning(f"Playlist '{name}' already exists, updating...")

    playlists[name] = SavedPlaylist(name=name, url=url, directory=directory)
    save_playlists(playlists)

    print_success(f"Added playlist '{name}'")
    print(f"  URL: {url}")
    print(f"  Directory: {directory}")
    return 0


def cmd_remove(args: Namespace) -> int:
    """Remove a playlist from saved playlists."""
    playlists = load_playlists()

    name = args.name
    if name not in playlists:
        print_error(f"Playlist '{name}' not found")
        return 1

    del playlists[name]
    save_playlists(playlists)

    print_success(f"Removed playlist '{name}'")
    return 0


def cmd_list(args: Namespace) -> int:
    """List all saved playlists."""
    playlists = load_playlists()

    if not playlists:
        print("No saved playlists.")
        print(f"Use 'duh-ytdl add <name> <url> <directory>' to add one.")
        return 0

    print(f"\n{Fore.CYAN}Saved Playlists{Style.RESET_ALL} ({len(playlists)})\n")

    for name, pl in sorted(playlists.items()):
        print(f"  {Fore.GREEN}{name}{Style.RESET_ALL}")
        print(f"    URL: {pl.url}")
        print(f"    Dir: {pl.directory}")
        print()

    return 0


# ============================================================================
# CLI
# ============================================================================

def add_common_flags(parser: argparse.ArgumentParser) -> None:
    """Add flags common to download/sync/batch."""
    parser.add_argument(
        "-t", "--type",
        choices=["mp3", "mp4"],
        default="mp3",
        help="output format (default: mp3)",
    )
    parser.add_argument(
        "-p", "--parallel",
        type=int,
        default=1,
        metavar="N",
        help="parallel downloads (default: 1)",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="re-download even if file exists",
    )


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="duh-ytdl",
        description="YouTube playlist manager: download, sync, and create M3U playlists",
    )

    parser.add_argument(
        "-c", "--cookies",
        type=Path,
        metavar="FILE",
        help="cookies file for authentication",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="show yt-dlp output",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # download
    p_download = subparsers.add_parser("download", help="download single track or playlist")
    p_download.add_argument("url", help="YouTube URL or search query")
    p_download.add_argument("output", type=Path, nargs="?", default=Path("."), help="output directory or file (default: .)")
    p_download.add_argument("--segment", help="download specific segment (e.g. '00:01:00-00:02:00')")
    add_common_flags(p_download)
    p_download.set_defaults(func=cmd_download)

    # sync
    p_sync = subparsers.add_parser("sync", help="sync playlist with local directory")
    p_sync.add_argument("playlist", help="playlist name or YouTube URL")
    p_sync.add_argument("directory", type=Path, nargs="?", help="local directory (optional if using saved playlist)")
    add_common_flags(p_sync)
    p_sync.add_argument("--prune", action="store_true", help="delete files not in playlist")
    p_sync.add_argument("--dry-run", action="store_true", help="show what would be done")
    p_sync.add_argument("--all", action="store_true", help="sync all saved playlists")
    p_sync.add_argument("--to-file", type=Path, metavar="FILE", help="save missing tracks to JSON")
    p_sync.set_defaults(func=cmd_sync)

    # batch
    p_batch = subparsers.add_parser("batch", help="download from JSON file")
    p_batch.add_argument("json_file", type=Path, help="JSON file with track list")
    p_batch.add_argument("directory", type=Path, help="output directory")
    add_common_flags(p_batch)
    p_batch.set_defaults(func=cmd_batch)

    # m3u
    p_m3u = subparsers.add_parser("m3u", help="generate M3U playlist")
    p_m3u.add_argument("playlist", help="playlist name or YouTube URL")
    p_m3u.add_argument("directory", type=Path, nargs="?", help="directory with MP3 files (optional if using saved playlist)")
    p_m3u.add_argument("-o", "--output", type=Path, metavar="FILE", help="output M3U file")
    p_m3u.add_argument("--abs", action="store_true", help="use absolute paths in M3U (default: relative)")
    p_m3u.set_defaults(func=cmd_m3u)

    # view
    p_view = subparsers.add_parser("view", help="view playlist or track info")
    p_view.add_argument("url", help="playlist name, YouTube URL, or search query")
    p_view.add_argument("--to-file", type=Path, metavar="FILE", help="save output as JSON")
    p_view.set_defaults(func=cmd_view)

    # --- Playlist management ---
    # add
    p_add = subparsers.add_parser("add", help="save a playlist for quick access")
    p_add.add_argument("name", help="short name for the playlist")
    p_add.add_argument("url", help="YouTube playlist URL")
    p_add.add_argument("directory", type=Path, help="local directory for downloads")
    p_add.set_defaults(func=cmd_add)

    # remove
    p_remove = subparsers.add_parser("remove", help="remove a saved playlist")
    p_remove.add_argument("name", help="playlist name to remove")
    p_remove.set_defaults(func=cmd_remove)

    # list
    p_list = subparsers.add_parser("list", help="list saved playlists")
    p_list.set_defaults(func=cmd_list)

    return parser


def main() -> int:
    parser = build_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    # Default cookies location
    if not args.cookies:
        default_cookies = Path.home() / ".config/scripts/cookies.txt"
        if default_cookies.exists():
            args.cookies = default_cookies

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nInterrupted")
        return 130
    except YtdlpError as e:
        print_error(str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
