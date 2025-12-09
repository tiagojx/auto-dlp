#!/usr/bin/env python3

import os
import subprocess
import argparse

from __init__ import (
    VENV_FOLDER,
    PYTHON_VERSION,
    PYTHON_BIN_NAME,
    PLATFORM,
    DW_SCRIPT,
    YDL_SCRIPT,
    REQUIREMENTS_OK_FILE,
)
from utils import (exec_cmd, get_user_choice, color_print)


def define_args():
    parser = argparse.ArgumentParser(
        description="An automated script to donwload and use yt-dlp with one Enter!"
    )
    parser.add_argument("-p", "--playlist", action="store_true", help="Playlist URL")
    parser.add_argument("urls", type=str, nargs="*", default=[], help="Video URLS")
    args = parser.parse_args()
    return (args.urls, args.playlist)


def create_venv(timeout=20):
    if not os.path.exists(VENV_FOLDER):
        print("Creating virtual environment...")
        while True:
            if PLATFORM == "win":
                try:
                    cmd = subprocess.Popen(
                        ["python", "-m", "venv", VENV_FOLDER],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    stdout, stderr = cmd.communicate(timeout=timeout)
                    if cmd.returncode != 0:
                        print(stderr)
                        raise subprocess.CalledProcessError(
                            cmd.returncode, cmd.args, output=stdout, stderr=stderr
                        )
                    print(stdout)

                except subprocess.TimeoutError:
                    print("The command timed out.")
                    break
                except subprocess.CalledProcessError as err:
                    print(f"Error ocurred: {err.stderr}")
                    break
                except Exception as err:
                    print(f"An unexpected error ocurred: {str(err)}")
                    break
                except FileNotFoundError:
                    print("'python.exe' was not found.")
                    ok = get_user_choice(
                        f"Do you want to install Python {PYTHON_VERSION} now? (y/n)"
                    )
                    if not ok:
                        break
                finally:
                    break
            else:
                print("Can't detect the current OS.")
                break


def download_packages(timeout=20) -> int:
    python_bin = ""
    if PLATFORM == "win":
        python_bin = f"{VENV_FOLDER}\\Scripts\\python.exe"
    elif PLATFORM == "unix":
        python_bin = f"{VENV_FOLDER}/bin/python3"

    err, _status = exec_cmd([python_bin, DW_SCRIPT], timeout=timeout)
    if err != 0:
        return 1
    else:
        return 0


def get_url_input() -> str:
    return input("Enter the video/playlist URL:\n")


def url_filter(url: str) -> str:
    filterd_url = str(url).split("&")
    filterd_url = str(filterd_url[0]).removeprefix("['")
    return filterd_url


def main():
    create_venv()
    URLS, IS_PLAYLIST = define_args()
    try:
        if not os.path.isfile(REQUIREMENTS_OK_FILE):
            err = download_packages(timeout=120)
            if err != 0:
                raise Exception
        pass
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
                filtered_url = url_filter(url) if not IS_PLAYLIST else url
                cmd.append(filtered_url)
                err, _status = exec_cmd(
                    cmd,
                    timeout=500,
                    verbose=False,
                )
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
