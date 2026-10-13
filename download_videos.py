#!/usr/bin/env python3
"""Download YouTube videos (or just their audio) for tango performance prep.

Examples:
    # Download a video in the best available quality (MP4)
    python download_videos.py https://www.youtube.com/watch?v=VIDEO_ID

    # Download only the music as MP3 (e.g. the tango you will perform to)
    python download_videos.py --audio-only https://www.youtube.com/watch?v=VIDEO_ID

    # Keep only a section, e.g. a 3-minute performance starting at 1:15
    python download_videos.py --start 1:15 --end 4:15 https://www.youtube.com/watch?v=VIDEO_ID

    # Download every URL listed in a text file (one per line, '#' for comments)
    python download_videos.py --batch-file videos.txt

Requires yt-dlp (pip install -r requirements.txt) and ffmpeg on your PATH.
"""

import argparse
import sys
from pathlib import Path

try:
    import yt_dlp
    from yt_dlp.utils import download_range_func
except ImportError:
    sys.exit("yt-dlp is not installed. Run: pip install -r requirements.txt")


def parse_timestamp(value):
    """Convert 'SS', 'MM:SS' or 'HH:MM:SS' into seconds."""
    try:
        parts = [float(p) for p in value.split(":")]
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid timestamp: {value!r}")
    if not 1 <= len(parts) <= 3 or any(p < 0 for p in parts):
        raise argparse.ArgumentTypeError(f"invalid timestamp: {value!r}")
    seconds = 0.0
    for part in parts:
        seconds = seconds * 60 + part
    return seconds


def read_batch_file(path):
    """Return the URLs in a text file, skipping blank lines and comments."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


def build_options(args):
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    options = {
        "outtmpl": str(output_dir / "%(title)s [%(id)s].%(ext)s"),
        "noplaylist": not args.playlist,
        "restrictfilenames": False,
        "windowsfilenames": True,
        "ignoreerrors": True,
    }

    if args.audio_only:
        options["format"] = "bestaudio/best"
        options["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": args.audio_format,
            "preferredquality": "0",
        }]
    else:
        height = f"[height<={args.max_height}]" if args.max_height else ""
        options["format"] = (
            f"bestvideo{height}[ext=mp4]+bestaudio[ext=m4a]/"
            f"bestvideo{height}+bestaudio/best{height}"
        )
        options["merge_output_format"] = "mp4"

    if args.start is not None or args.end is not None:
        start = args.start or 0
        end = args.end if args.end is not None else float("inf")
        if end <= start:
            sys.exit("--end must be later than --start")
        options["download_ranges"] = download_range_func(None, [(start, end)])
        # Re-encode at the cut points so the clip starts exactly on time.
        options["force_keyframes_at_cuts"] = True

    return options


def main():
    parser = argparse.ArgumentParser(
        description="Download YouTube videos or audio for tango practice and performances.",
    )
    parser.add_argument("urls", nargs="*", help="YouTube video or playlist URLs")
    parser.add_argument("-b", "--batch-file", help="text file with one URL per line")
    parser.add_argument("-o", "--output-dir", default="downloads",
                        help="where to save files (default: ./downloads)")
    parser.add_argument("-a", "--audio-only", action="store_true",
                        help="download only the music")
    parser.add_argument("--audio-format", default="mp3", choices=["mp3", "m4a", "wav", "flac"],
                        help="audio format with --audio-only (default: mp3)")
    parser.add_argument("--max-height", type=int, metavar="PIXELS",
                        help="cap video resolution, e.g. 720 or 1080")
    parser.add_argument("--start", type=parse_timestamp, metavar="TIME",
                        help="clip start, e.g. 1:15 or 75")
    parser.add_argument("--end", type=parse_timestamp, metavar="TIME",
                        help="clip end, e.g. 4:15 or 255")
    parser.add_argument("--playlist", action="store_true",
                        help="download the whole playlist when a URL contains one")
    args = parser.parse_args()

    urls = list(args.urls)
    if args.batch_file:
        urls.extend(read_batch_file(args.batch_file))
    if not urls:
        parser.error("give at least one URL or --batch-file")

    with yt_dlp.YoutubeDL(build_options(args)) as ydl:
        failed = ydl.download(urls)

    if failed:
        sys.exit("Some downloads failed; see the messages above.")
    print(f"Done. Files saved in {Path(args.output_dir).expanduser().resolve()}")


if __name__ == "__main__":
    main()
