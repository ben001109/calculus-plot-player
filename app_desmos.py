import os
import sys
import threading
import webbrowser

from backend import app


def _base_dir():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def _open_browser():
    html_path = os.path.join(_base_dir(), "index.html")
    webbrowser.open("file://" + html_path)


def main():
    threading.Timer(1.0, _open_browser).start()
    app.run()


if __name__ == "__main__":
    main()
