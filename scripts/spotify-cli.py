#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [ "spotipy", "python-dotenv" ]
# ///

"""
Spotify Fetcher MCP - CLI Tool
Fetch track information from Spotify playlists and albums.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

# Configure logging
log_file = Path(__file__).resolve().parent / "duh-spotify-cli.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file),
    ],
)
logger = logging.getLogger(__name__)


class SpotifyFetcher:
    """CLI tool for fetching Spotify playlist and album tracks"""

    def __init__(
        self, client_id: Optional[str] = None, client_secret: Optional[str] = None
    ):
        """Initialize SpotifyFetcher with credentials"""
        load_dotenv(Path(__file__).parent / ".env_spotify")

        self.client_id = client_id or os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SPOTIFY_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Spotify credentials not found. "
                "Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables "
                "or use --client-id and --client-secret arguments."
            )

        self._setup_spotify_client()

    def _setup_spotify_client(self):
        """Set up Spotify client with credentials"""
        client_credentials_manager = SpotifyClientCredentials(
            client_id=self.client_id, client_secret=self.client_secret
        )
        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    def _extract_id(self, url: str, resource_type: str) -> str:
        """Extract resource ID from URL"""
        if f"{resource_type}/" in url:
            return url.split(f"{resource_type}/")[1].split("?")[0]
        return url

    def get_playlist_tracks(
        self,
        playlist_url: str,
        output_format: str = "text",
        limit: Optional[int] = None,
    ) -> dict:
        """
        Fetch playlist tracks from Spotify

        Args:
            playlist_url: Spotify playlist URL or URI
            output_format: Output format ('text', 'json', 'csv')
            limit: Maximum number of tracks to fetch (None for all)

        Returns:
            Dictionary with track information
        """
        try:
            playlist_id = self._extract_id(playlist_url, "playlist")

            # Fetch playlist info
            playlist = self.sp.playlist(playlist_id)
            playlist_name = playlist.get("name", "Unknown Playlist")

            # Filter out None artist names for playlist owner
            owner_names = [
                owner.get("display_name", "Unknown")
                for owner in [playlist.get("owner", {})]
                if owner
            ]
            playlist_owner = ", ".join(owner_names) if owner_names else "Unknown Owner"

            # Fetch tracks
            results = self.sp.playlist_tracks(playlist_id)
            tracks = []
            total_fetched = 0

            while results and (limit is None or total_fetched < limit):
                for item in results["items"]:
                    if limit is not None and total_fetched >= limit:
                        break

                    track = item["track"]
                    if track:
                        # Filter out None artist names
                        artist_names = [
                            artist["name"]
                            for artist in track["artists"]
                            if artist.get("name")
                        ]
                        artists = (
                            ", ".join(artist_names)
                            if artist_names
                            else "Unknown Artist"
                        )

                        tracks.append(
                            {
                                "title": track["name"],
                                "artists": artists,
                                "album": track["album"]["name"],
                                "duration_ms": track["duration_ms"],
                                "track_number": track["track_number"],
                                "url": track["external_urls"]["spotify"],
                                "uri": track["uri"],
                            }
                        )
                        total_fetched += 1

                if limit is not None and total_fetched >= limit:
                    break

                if results["next"]:
                    results = self.sp.next(results)
                else:
                    break

            # Prepare output
            result_data = {
                "success": True,
                "playlist_name": playlist_name,
                "playlist_owner": playlist_owner,
                "playlist_url": playlist["external_urls"]["spotify"],
                "total_tracks": playlist["tracks"]["total"],
                "fetched_tracks": len(tracks),
                "tracks": tracks,
            }

            return self._format_output(result_data, output_format, "playlist")

        except Exception as e:
            logger.exception(f"Error fetching playlist: {str(e)}")
            return {
                "success": False,
                "message": f"Error fetching playlist: {str(e)}",
                "output": f"Error: {str(e)}",
            }

    def get_album_tracks(
        self, album_url: str, output_format: str = "text", limit: Optional[int] = None
    ) -> dict:
        """
        Fetch album tracks from Spotify

        Args:
            album_url: Spotify album URL or URI
            output_format: Output format ('text', 'json', 'csv')
            limit: Maximum number of tracks to fetch (None for all)

        Returns:
            Dictionary with track information
        """
        try:
            album_id = self._extract_id(album_url, "album")

            # Fetch album info
            album = self.sp.album(album_id)

            # Filter out None artist names for album artists
            album_artist_names = [
                artist["name"] for artist in album["artists"] if artist.get("name")
            ]
            album_artists = (
                ", ".join(album_artist_names)
                if album_artist_names
                else "Unknown Artist"
            )

            # Fetch tracks
            results = album["tracks"]
            tracks = []
            total_fetched = 0

            while results and (limit is None or total_fetched < limit):
                for track in results["items"]:
                    if limit is not None and total_fetched >= limit:
                        break

                    # Filter out None artist names
                    artist_names = [
                        artist["name"]
                        for artist in track["artists"]
                        if artist.get("name")
                    ]
                    artists = (
                        ", ".join(artist_names) if artist_names else "Unknown Artist"
                    )

                    tracks.append(
                        {
                            "title": track["name"],
                            "artists": artists,
                            "duration_ms": track["duration_ms"],
                            "track_number": track["track_number"],
                            "url": track["external_urls"]["spotify"],
                            "uri": track["uri"],
                        }
                    )
                    total_fetched += 1

                if limit is not None and total_fetched >= limit:
                    break

                if results["next"]:
                    results = self.sp.next(results)
                else:
                    break

            # Prepare output
            result_data = {
                "success": True,
                "album_name": album["name"],
                "album_artists": album_artists,
                "album_url": album["external_urls"]["spotify"],
                "release_date": album.get("release_date", "Unknown"),
                "total_tracks": album["tracks"]["total"],
                "fetched_tracks": len(tracks),
                "tracks": tracks,
            }

            return self._format_output(result_data, output_format, "album")

        except Exception as e:
            logger.exception(f"Error fetching album: {str(e)}")
            return {
                "success": False,
                "message": f"Error fetching album: {str(e)}",
                "output": f"Error: {str(e)}",
            }

    def _format_output(self, data: dict, format_type: str, resource_type: str) -> dict:
        """Format output based on requested format"""
        if format_type == "json":
            output = json.dumps(data, indent=2, ensure_ascii=False)
        elif format_type == "csv":
            output = self._to_csv(data, resource_type)
        else:  # text format
            output = self._to_text(data, resource_type)

        data["output"] = output
        return data

    def _to_text(self, data: dict, resource_type: str) -> str:
        """Convert data to human-readable text format"""
        if not data["success"]:
            return data["message"]

        if resource_type == "playlist":
            text = f"🎵 Playlist: {data['playlist_name']}\n"
            text += f"👤 Owner: {data['playlist_owner']}\n"
            text += f"🔗 URL: {data['playlist_url']}\n"
            text += f"📊 Total tracks: {data['total_tracks']} (showing {data['fetched_tracks']})\n"
        else:  # album
            text = f"💿 Album: {data['album_name']}\n"
            text += f"👤 Artist(s): {data['album_artists']}\n"
            text += f"📅 Release Date: {data['release_date']}\n"
            text += f"🔗 URL: {data['album_url']}\n"
            text += f"📊 Total tracks: {data['total_tracks']} (showing {data['fetched_tracks']})\n"

        text += "\n" + "=" * 50 + "\n\n"

        for i, track in enumerate(data["tracks"], 1):
            # Format duration (ms to mm:ss)
            minutes = track["duration_ms"] // 60000
            seconds = (track["duration_ms"] % 60000) // 1000
            duration = f"{minutes}:{seconds:02d}"

            text += f"{i:3d}. {track['title']}\n"
            text += f"     Artist(s): {track['artists']}\n"
            if resource_type == "playlist":
                text += f"     Album: {track['album']}\n"
            text += f"     Track #{track['track_number']} | Duration: {duration}\n"
            text += f"     URL: {track['url']}\n"
            text += f"     URI: {track['uri']}\n\n"

        return text

    def _to_csv(self, data: dict, resource_type: str) -> str:
        """Convert data to CSV format"""
        if not data["success"]:
            return data["message"]

        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        if resource_type == "playlist":
            writer.writerow(
                [
                    "Track Number",
                    "Title",
                    "Artists",
                    "Album",
                    "Duration (ms)",
                    "Track #",
                    "URL",
                    "URI",
                ]
            )
        else:
            writer.writerow(
                [
                    "Track Number",
                    "Title",
                    "Artists",
                    "Duration (ms)",
                    "Track #",
                    "URL",
                    "URI",
                ]
            )

        # Write data rows
        for i, track in enumerate(data["tracks"], 1):
            row = [i, track["title"], track["artists"]]
            if resource_type == "playlist":
                row.append(track["album"])
            row.extend(
                [
                    track["duration_ms"],
                    track["track_number"],
                    track["url"],
                    track["uri"],
                ]
            )
            writer.writerow(row)

        return output.getvalue()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Fetch track information from Spotify playlists and albums",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
  %(prog)s album https://open.spotify.com/album/1ATL5GLyefJaxhQzSPVrLX --format json
  %(prog)s playlist https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M --limit 10 --output-file tracks.txt
  %(prog)s album https://open.spotify.com/album/1ATL5GLyefJaxhQzSPVrLX --client-id YOUR_ID --client-secret YOUR_SECRET
        """,
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Playlist command
    playlist_parser = subparsers.add_parser("playlist", help="Fetch playlist tracks")
    playlist_parser.add_argument("url", help="Spotify playlist URL or ID")

    # Album command
    album_parser = subparsers.add_parser("album", help="Fetch album tracks")
    album_parser.add_argument("url", help="Spotify album URL or ID")

    # Common arguments
    for subparser in [playlist_parser, album_parser]:
        subparser.add_argument(
            "--format",
            "-f",
            choices=["text", "json", "csv"],
            default="text",
            help="Output format (default: text)",
        )
        subparser.add_argument(
            "--limit", "-l", type=int, help="Limit number of tracks to fetch"
        )
        subparser.add_argument(
            "--output-file",
            "-o",
            type=str,
            help="Output file path (prints to stdout if not specified)",
        )
        subparser.add_argument(
            "--client-id",
            type=str,
            help="Spotify Client ID (overrides environment variable)",
        )
        subparser.add_argument(
            "--client-secret",
            type=str,
            help="Spotify Client Secret (overrides environment variable)",
        )
        subparser.add_argument(
            "--verbose", "-v", action="store_true", help="Enable verbose logging"
        )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Check if command is provided
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        # Initialize fetcher
        fetcher = SpotifyFetcher(
            client_id=args.client_id, client_secret=args.client_secret
        )

        # Execute command
        if args.command == "playlist":
            result = fetcher.get_playlist_tracks(
                playlist_url=args.url, output_format=args.format, limit=args.limit
            )
        else:  # album
            result = fetcher.get_album_tracks(
                album_url=args.url, output_format=args.format, limit=args.limit
            )

        # Output result
        output = result.get("output", "")

        if args.output_file:
            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Output written to {args.output_file}")
        else:
            print(output)

        # Exit with appropriate code
        sys.exit(0 if result.get("success", False) else 1)

    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        logger.exception("Unexpected error occurred")
        sys.exit(1)


if __name__ == "__main__":
    main()
