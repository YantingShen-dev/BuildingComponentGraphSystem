"""Compatibility entry point; install the toolkit from the repository root first."""

from bcgs.server import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, threaded=False)
