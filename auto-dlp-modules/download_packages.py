#!/usr/bin/env python3

from __init__ import (PYTHON_BIN_NAME, REQUIREMENTS_OK_FILE)
from utils import (exec_cmd, color_print)


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
        err, status = exec_cmd("pip install yt-dlp --no-deps")
        package_status.update({"yt-dlp": status})
        if err != 0:
            raise Exception
    except Exception:
        color_print("Could not install yt-dlp.", color="red")
    else:
        color_print("yt-dlp was sucessfully installed!\n", color="green")
        try:
            err, status = exec_cmd("winget install ffmpeg --no-upgrade", timeout=240)
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
        with open(REQUIREMENTS_OK_FILE, "w") as f:
            for key, value in package_status.items():
                content = f"Requires '{key}'... {value}"
                f.write(f"{content}\n")
        f.close()
        print("All done!\n")
