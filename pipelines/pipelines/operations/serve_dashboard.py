import json
import logging
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from pipelines.operations.upload_sample import get_dl_service

logger = logging.getLogger(__name__)

DASHBOARD_DIR = Path(__file__).resolve().parents[3] / "dashboard"
DASHBOARD_JSON_PATH = "dashboard/daily_sales_summary_json"


def load_daily_sales_summary() -> list[dict]:
    dl_service = get_dl_service()
    gold_client = dl_service.get_file_system_client("gold")
    paths = gold_client.get_paths(path=DASHBOARD_JSON_PATH)
    json_paths = sorted(
        path.name for path in paths if not path.is_directory and "/part-" in path.name
    )

    rows: list[dict] = []
    for path in json_paths:
        file_client = gold_client.get_file_client(path)
        content = file_client.download_file().readall().decode("utf-8")
        rows.extend(json.loads(line) for line in content.splitlines() if line.strip())

    return rows


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)

    def do_GET(self) -> None:
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/api/daily-sales-summary":
            self.handle_daily_sales_summary()
            return

        if parsed_path.path == "/":
            self.path = "/index.html"

        super().do_GET()

    def handle_daily_sales_summary(self) -> None:
        try:
            rows = load_daily_sales_summary()
            payload = json.dumps({"rows": rows}, default=str).encode("utf-8")
            self.send_response(HTTPStatus.OK)
        except Exception as exc:
            logger.exception("Failed to load daily sales summary")
            payload = json.dumps({"error": str(exc)}).encode("utf-8")
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)

        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def serve_dashboard(host: str = "127.0.0.1", port: int = 8765) -> None:
    server = ThreadingHTTPServer((host, port), DashboardHandler)
    logger.info("Serving dashboard at http://%s:%s", host, port)
    server.serve_forever()
