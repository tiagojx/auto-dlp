#!/usr/bin/env python3

import os
import subprocess
import argparse
import yt_dlp

VENV_FOLDER = ".venv"
PYTHON_VERSION = 3.11
PYTHON_BIN_NAME = "python" if os.name == "nt" else "python3"
PLATFORM = "win" if os.name == "nt" else "unix"
DW_SCRIPT = "download_packages.py"
YDL_SCRIPT = "ydl.py"
REQUIREMENTS_OK_FILE = "requirements_ok.txt"


arg_parser = argparse.ArgumentParser(
    description="An automated script to donwload and use yt-dlp with one Enter!"
)
arg_parser.add_argument("-p", "--playlist", action="store_true", help="Playlist URL")
arg_parser.add_argument("urls", type=str, nargs="*", default=[], help="Video URLS")
arg_parser.add_argument("--log", type=bool, default=False, help="Video URLS")
ARGS = arg_parser.parse_args()


def color_print(text, color="reset"):
    colors = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
        "reset": 0,
    }
    if color not in colors:
        print("Invalid color.")

    print(f"\033[{colors[color]}m{text}\033[0m")


def exec_cmd(cmd, timeout=20, verbose=True) -> tuple[int, str]:
    try:
        cmd = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = cmd.communicate(timeout=timeout)
        if cmd.returncode != 0:
            if verbose:
                print(stderr)
            raise subprocess.CalledProcessError(
                cmd.returncode, cmd.args, output=stdout, stderr=stderr
            )
        if verbose:
            print(stdout)

    except subprocess.TimeoutExpired:
        color_print("The command timed out.", color="magenta")
        return 1, "unavailable"
    except subprocess.CalledProcessError as err:
        color_print(f"Error ocurred: {err.stderr}")
        return 1, "unavailable"
    except Exception as err:
        color_print(f"An unexpected error ocurred: {str(err)}", color="red")
        return 1, "unavailable"
    else:
        return 0, "OK"


def get_user_choice(prompt, cmd) -> bool:
    ok = input(prompt)[0]
    ok.lower()
    while True:
        if ok == "y":
            exec_cmd(cmd)
            return True
        elif ok == "n":
            return False


def download_packages(timeout=20, log=False) -> int:
    try:
        color_print("Upgrading pip...", color="cyan")
        err, _status = exec_cmd(f"{PYTHON_BIN_NAME} -m pip install --upgrade pip")
        if err != 0:
            raise Exception
    except Exception:
        color_print("\nCould not upgrade pip. -- Skipping...", color="yellow")
    else:
        color_print("Pip was sucessfully upgraded!\n", color="green")
    finally:
        package_status = dict()
        try:
            color_print("Installing necessary packages...", color="cyan")
            err, status = exec_cmd(f"{PYTHON_BIN_NAME} -m pip install yt-dlp --no-deps")
            package_status.update({"yt-dlp": status})
            if err != 0:
                raise Exception
        except Exception:
            color_print("Could not install yt-dlp.", color="red")
            return 1
        else:
            color_print("yt-dlp was sucessfully installed!\n", color="green")
            try:
                err, status = exec_cmd(
                    "winget install ffmpeg --no-upgrade", timeout=240
                )
                package_status.update({"ffmpeg": status})
                if err != 0:
                    raise Exception
            except Exception:
                color_print(
                    "Could not install ffmpeg. You can still use yt-dlp to download video/music, but you will unable to change media format.\n",
                    color="yellow",
                )
            else:
                color_print("ffmpeg was sucessfully installed!", color="green")
        finally:
            if log:
                with open(REQUIREMENTS_OK_FILE, "w") as f:
                    for key, value in package_status.items():
                        content = f"Requires '{key}'... {value}"
                        f.write(f"{content}\n")
                f.close()
            print("All done!\n")
            return 0


def get_url_input() -> str:
    return input("Enter the video/playlist URL:\n")


def url_filter(url: str) -> str:
    filterd_url = str(url).split("&")
    filterd_url = str(filterd_url[0]).removeprefix("['")
    return filterd_url


def ydl(is_playlist: bool, urls: list) -> int:
    ydl_opts = {
        "format": "mp3/bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }
        ],
    }

    if is_playlist:
        try:
            ydl_opts.update({"noplaylist": "false", "outtmpl": "%(title)s.%(ext)s"})
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(urls, download=False)
                video_title = info_dict.get("title", "<No title found>")
                uploader = info_dict.get("uploader", "<No uploader found>")

                _err = ydl.download(url)
                color_print(
                    f'\nDownloaded "{video_title}" by "{uploader}"', color="greem"
                )
        except Exception:
            return 1
        else:
            return 0
    else:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for url in urls:
                    info_dict = ydl.extract_info(url, download=False)
                    video_title = info_dict.get("title", "<No title found>")
                    uploader = info_dict.get("uploader", "<No uploader found>")

                    _err = ydl.download(url)
                    color_print(
                        f'\nDownloaded "{video_title}" by "{uploader}"', color="green"
                    )
        except Exception:
            return 1
        else:
            return 0


def main():
    URLS, IS_PLAYLIST = ARGS.urls, ARGS.playlist
    try:
        if not os.path.isfile(REQUIREMENTS_OK_FILE):
            log = True if ARGS.log else False
            err = download_packages(timeout=120, log=log)
            if err != 0:
                raise Exception
    except Exception:
        print("Could not install packages.")
    else:
        try:
            cmd = [PYTHON_BIN_NAME, YDL_SCRIPT]

            if not URLS:
                URLS = [get_url_input()]

            if IS_PLAYLIST or "list" in str(URLS):
                color_print("Donwloading playlist...", color="cyan")
                IS_PLAYLIST = True
            else:
                color_print("Donwloading video...", color="cyan")

            for url in URLS:
                filtered_url = [url_filter(url) if not IS_PLAYLIST else url]
                cmd.append(filtered_url)
                err = ydl(IS_PLAYLIST, filtered_url)
                if err != 0:
                    raise Exception
        except KeyboardInterrupt:
            print("Exiting...")
        except Exception as e:
            print(f"Could not execute the main script. {str(e)}")
        else:
            print("Program has finished.")


if __name__ == "__main__":
    main()
