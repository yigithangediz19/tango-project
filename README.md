# Tango Project

## Downloading videos for practice

`download_videos.py` downloads YouTube videos (or just the music) using
[yt-dlp](https://github.com/yt-dlp/yt-dlp).

### Setup

1. Install Python 3.9+ and [ffmpeg](https://ffmpeg.org/download.html)
   (needed to merge video/audio and to convert or trim files).
2. Install the Python dependency:

   ```bash
   pip install -r requirements.txt
   ```

### Usage

```bash
# Full video, best quality, saved as MP4 in ./downloads
python download_videos.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Just the music as MP3 (for rehearsing or the performance sound system)
python download_videos.py --audio-only "https://www.youtube.com/watch?v=VIDEO_ID"

# Only a section of the video, e.g. from 1:15 to 4:15
python download_videos.py --start 1:15 --end 4:15 "https://www.youtube.com/watch?v=VIDEO_ID"

# Cap resolution to save space
python download_videos.py --max-height 720 "https://www.youtube.com/watch?v=VIDEO_ID"

# Many videos at once: list URLs in a text file, one per line
python download_videos.py --batch-file videos.txt

# A whole playlist
python download_videos.py --playlist "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

Run `python download_videos.py --help` for all options.

If downloads start failing, YouTube has probably changed something; update
yt-dlp with `pip install -U yt-dlp`.

Only download videos you have the right to use, and check the licensing for
any music you play at a public performance.
