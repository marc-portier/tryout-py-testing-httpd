import pytest
import requests
from typing import Dict
from rdflib import Graph


RDF_MIMES = {"text/turtle", "application/ld+json", }
EXPECTED_TTL = """
@prefix hello: <urn:hello:> .

<http://localhost:8000/any> hello:to "World!"@en .
""".strip()


@pytest.mark.usefixtures("httpd_server_base", "all_extensions_testset")
def test_me(httpd_server_base: str, all_extensions_testset: Dict[str, str]):
    assert httpd_server_base 
    assert all_extensions_testset 

    for mime, resource_path in all_extensions_testset.items():
        url = f"{httpd_server_base}{resource_path}"
        req = requests.get(url)
        assert req.ok
        ctype = req.headers.get('content-type')
        assert ctype.startswith(mime)
        clen = int(req.headers.get('content-length'))
        assert clen > 0

        if mime in RDF_MIMES:
            g = Graph().parse(url)
            ttl = g.serialize(format="turtle").strip()
            assert ttl == EXPECTED_TTL
