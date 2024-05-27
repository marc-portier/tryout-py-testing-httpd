import pytest
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, HTTPServer
from typing import Dict
import re
from threading import Thread


TEST_PATH: Path = Path(__file__).parent
HTTPD_ROOT: Path = TEST_PATH / "httpd-root"
HTTPD_HOST: str = 'localhost'  # can be '' - maybe also try '0.0.0.0' to bind all
HTTPD_PORT: int = 8000
HTTPD_EXTENSION_MAP: Dict[str, str] = {
    '.txt': 'text/plain',
    '.jsonld': 'application/ld+json',
    '.ttl': 'text/turtle',
}


class TestRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server, *args, **kwargs) -> None:
        super().__init__(request, client_address, server, directory=str(HTTPD_ROOT.absolute()))


TestRequestHandler.extensions_map = {**SimpleHTTPRequestHandler.extensions_map, **HTTPD_EXTENSION_MAP}


@pytest.fixture(scope="session")
def httpd_server():
    with HTTPServer((HTTPD_HOST, HTTPD_PORT), TestRequestHandler) as httpd:
        def httpd_serve():
            httpd.serve_forever()

        t = Thread(target=httpd_serve)
        t.daemon = True
        t.start()

        yield httpd
        httpd.shutdown()


@pytest.fixture(scope="session")
def httpd_server_base(httpd_server: HTTPServer) -> str:
    return f"http://{httpd_server.server_name}:{httpd_server.server_port}/"


@pytest.fixture(scope="session")
def all_extensions_testset():
    return {mime: f"{re.sub(r'[^0-9a-zA-Z]+','-', mime)}{ext}" for ext, mime in HTTPD_EXTENSION_MAP.items()}
