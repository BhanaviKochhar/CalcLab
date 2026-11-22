"""Flask application factory and REST API for CalcLab."""
from flask import Flask, jsonify, request

from . import __version__
from .engine import evaluate
from .errors import CalcError
from .utils import format_number


def create_app():
    app = Flask(__name__, static_folder="../static", static_url_path="")

    @app.get("/")
    def index():
        return app.send_static_file("index.html")

    @app.get("/api/health")
    def health():
        return jsonify(status="ok", version=__version__)

    @app.post("/api/evaluate")
    def api_evaluate():
        data = request.get_json(silent=True) or {}
        expression = data.get("expression", "")
        try:
            value = evaluate(expression)
        except CalcError as exc:
            return jsonify(ok=False, error=str(exc)), 400
        return jsonify(ok=True, expression=expression, result=value, display=format_number(value))

    return app
