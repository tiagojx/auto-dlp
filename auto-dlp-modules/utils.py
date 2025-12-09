import subprocess


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
