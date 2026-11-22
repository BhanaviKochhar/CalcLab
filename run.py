"""Development / production entry point (``python run.py`` or ``gunicorn run:app``)."""
import os

from calclab.api import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=True)
