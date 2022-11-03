import base64
from collections import namedtuple
from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
import socket
import sys
import threading
from urllib.parse import parse_qs, urlencode, urlparse
import webbrowser

import requests


REALM = "app"
CLIENT_ID = "app1-public"
WELLKNOWN_CONFIGURATION = f"http://localhost:8080/realms/{REALM}/.well-known/openid-configuration"


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, webserver, *args, **kwargs):
        self._webserver = webserver
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if "/init-auth" in self.path:
            authorization_endpoint = self._webserver.wellknown["authorization_endpoint"]
            query = urlencode({
                "client_id": CLIENT_ID,
                "response_type": "code",
                "redirect_uri": self._webserver.redirect_url,
            })
            redirect_url = f"{authorization_endpoint}?{query}"
            return self.redirect(redirect_url)

        if "/cli-callback" in self.path and "code=" in self.path:
            qs = parse_qs(urlparse(self.path).query)
            code = qs["code"][0]
            token_endpoint = self._webserver.wellknown["token_endpoint"]
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": CLIENT_ID,
                "redirect_uri": self._webserver.redirect_url,
            }
            r = requests.post(token_endpoint, data)

            self._webserver.jwt = r.json()["access_token"]
            self.response(200, f"Token received, please close the browser")
            sys.exit()

        self.response(404, "Not Found")

    def redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.end_headers()

    def response(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(data.encode())


class WebServer:
    def __init__(self):
        # 1. getting well-known configuration
        resp = requests.get(WELLKNOWN_CONFIGURATION)
        resp.raise_for_status()
        self._wellknown = resp.json()
        self.jwt = None

        # 2. getting free port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            self._port = s.getsockname()[1]
    
    @property
    def redirect_url(self):
        return f"http://localhost:{self._port}/cli-callback"

    @property
    def init_auth_url(self):
        return f"http://localhost:{self._port}/init-auth"

    @property
    def wellknown(self):
        return self._wellknown

    def server_thread(self):
        server_address = ("", self._port)
        handler = partial(RequestHandler, self)
        server = HTTPServer(server_address, handler)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        return thread


def main():
    server = WebServer()
    thread = server.server_thread()
    thread.start()
    
    webbrowser.open(server.init_auth_url)
    thread.join(60)

    access_token = server.jwt

    body = access_token.split(".")[1]
    body += "=" * ((4 - len(body) % 4) % 4)
    token = json.loads(base64.b64decode(body))
    print(f"\nLogged in as user-id={token['sub']}\n")

    print("Requesting default endpoint:")
    resp = requests.get("http://localhost:5000/", headers={"Authorization": f"Bearer {access_token}"})
    print(resp.json())

    print("Requesting admin endpoint:")
    resp = requests.get("http://localhost:5000/admin", headers={"Authorization": f"Bearer {access_token}"})
    print(resp.json())    


if __name__ == "__main__":
    main()