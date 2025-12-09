import argparse
import yt_dlp

parser = argparse.ArgumentParser(
    description="An automated script to donwload and use yt-dlp with a single enter."
)
parser.add_argument("-p", "--playlist", action="store_true", help="Playlist URL")
parser.add_argument("urls", type=str, nargs="+", help="Video URLS")
args = parser.parse_args()

URLS = args.urls
IS_PLAYLIST = args.playlist

ydl_opts = {
    "format": "mp3/bestaudio/best",
    "postprocessors": [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }
    ],
}

if IS_PLAYLIST:
    ydl_opts.update({"noplaylist": "false", "outtmpl": "%(title)s.%(ext)s"})
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(URLS, download=False)
        video_title = info_dict.get("title", "<No title found>")
        uploader = info_dict.get("uploader", "<No uploader found>")

        _err = ydl.download(URLS)
        print(f'Downloaded "{video_title}" by {uploader}')
else:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in URLS:
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get("title", "<No title found>")
            uploader = info_dict.get("uploader", "<No uploader found>")

            _err = ydl.download(url)
            print(f'Downloaded "{video_title}" by {uploader}')
