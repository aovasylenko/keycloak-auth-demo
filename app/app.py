from urllib.parse import urlencode

from fastapi import Depends, FastAPI, Security, Request
from fastapi.security import OpenIdConnect
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt, ExpiredSignatureError, JWTError
from pydantic import BaseModel
import requests
import uvicorn
from starlette.exceptions import HTTPException

from utils import OIDCToken


app = FastAPI()
oid = OIDCToken(openIdConnectUrl="http://localhost:8080/realms/app/.well-known/openid-configuration", audience="account")

CLIENT_ID = "app1"
CLIENT_SECRET="CLIENTSECRET"

#
# FastAPI user dependencies and User Model
#

class User(BaseModel):
    user_id: str
    username: str
    is_superadmin: bool


def current_user(token: dict = Security(oid)):
    user = User(
        user_id=token["sub"],
        username=token["preferred_username"],
        is_superadmin="super-admin" in token["realm_access"]["roles"]
    )
    return user


def admin_user(me: User = Depends(current_user)):
    if not me.is_superadmin:
        raise HTTPException(status_code=403, detail="Access denied - super-admin rights are needed") 
    return me

#
# Service endpoints
#

@app.get("/auth", include_in_schema=False)
def auth():
    auth_endpoint = oid.wellknown["authorization_endpoint"]
    query = urlencode({
        "client_id": CLIENT_ID,
        "response_type": "code",
        "scope": "openid",
        "redirect_uri": "http://localhost:5000/callback"
    })
    return f"{auth_endpoint}?{query}"


@app.get("/callback", include_in_schema=False)
def callback(code: str):
    token_endpoint = oid.wellknown["token_endpoint"]
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "redirect_uri": "http://localhost:5000/callback",
        "code": code
    }
    resp = requests.post(token_endpoint, data=data)
    if resp.status_code == 200:
        return {
            "response": resp.json()
        }
    else:
        return {
            "error": resp.text
        }


@app.get("/")
def base(request: Request, me: User = Depends(current_user)):
    """ Returns basic account information. Valid JWT token is required. """
    return {
        "account": {
            "user": me
        }
    }


@app.get("/admin")
def admin(request: Request, me: User = Depends(admin_user)):
    """ Return admin-only account information. Only users with `super-admin` role can access. """
    return {
        "admin": True,
        "account": {
            "user": me
        }
    }


if __name__ == "__main__":
    uvicorn.run("app:app", port=5000, reload=True)
