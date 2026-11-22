"""Flask application factory and REST API for CalcLab."""
import os

from flask import Flask, jsonify, request

from . import __version__
from .display import format_result
from .engine import evaluate
from .errors import CalcError
from .history import HistoryStore

def create_app(db_path=None):
    app = Flask(__name__, static_folder="../static", static_url_path="")
    history = HistoryStore(db_path or os.environ.get("CALCLAB_DB", "calclab.db"))

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
        angle_mode = data.get("angle_mode", "rad")
        try:
            value = evaluate(expression, angle_mode=angle_mode, variables=history.variables())
        except CalcError as exc:
            return jsonify(ok=False, error=str(exc)), 400
        display = format_result(value)
        entry_id = history.add(expression, display, value)
        return jsonify(
            ok=True,
            id=entry_id,
            expression=expression,
            result=value,
            display=display,
            angle_mode=angle_mode,
        )

    @app.get("/api/history")
    def get_history():
        limit = max(1, min(request.args.get("limit", default=20, type=int), 100))
        items = [
            dict(item, display=format_result(item["value"], group=True))
            for item in history.recent(limit)
        ]
        return jsonify(ok=True, items=items)

    @app.delete("/api/history")
    def clear_history():
        history.clear()
        return jsonify(ok=True)

    return app
