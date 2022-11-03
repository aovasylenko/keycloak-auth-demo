import base64
import io
import json
from pprint import pprint as pp
import webbrowser
import time

#import jwt
import qrcode
import requests

REALM = "app"
CLIENT_ID = "app1-device"
WELLKNOWN_CONFIGURATION = f"http://localhost:8080/realms/{REALM}/.well-known/openid-configuration"


def get_qrcode(url: str) -> str:
    qr = qrcode.QRCode()
    qr.add_data(url)
    f = io.StringIO()
    qr.print_ascii(out=f)
    f.seek(0)
    return f.read()


def main():
    # 1. getting well-known configuration
    resp = requests.get(WELLKNOWN_CONFIGURATION)
    resp.raise_for_status()
    config = resp.json()

    # 2. initiating flow
    resp = requests.post(config["device_authorization_endpoint"], data={
        "client_id": CLIENT_ID
    })
    if resp.status_code == 401:
        print(resp.text)
        return
        
    resp.raise_for_status()
    resp = resp.json()
    
    device_code = resp["device_code"]
    user_code = resp["user_code"]
    verification_uri_complete = resp["verification_uri_complete"]

    print(get_qrcode(verification_uri_complete))

    print(f"Received usercode:\n\n{user_code}\n\nopening browser for authorization at:\n{verification_uri_complete}")
    print(f"\nStart pooling token endpoint using {device_code} device code...")

    # 3. opening the browser
    webbrowser.open(verification_uri_complete)

    while True:
        resp = requests.post(config["token_endpoint"], data={
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": CLIENT_ID,
            "device_code": device_code
        })
        if resp.status_code == 400 and resp.json()["error"] in ["slow_down", "authorization_pending"]:
            print(resp.json()["error_description"])
            time.sleep(1)
            continue

        if resp.status_code == 200:
            access_token = resp.json()['access_token']
            print(f"\nRECEIVED TOKEN:\n{access_token}")
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
        else:
            print(f"\nERROR: {resp.status_code}")
            pp(resp.json())
        break


if __name__ == "__main__":
    main()
