from fastapi import Request
from fastapi.security import OpenIdConnect
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt, ExpiredSignatureError, JWTError
import requests
from starlette.exceptions import HTTPException


class OIDCToken(OpenIdConnect):
    def __init__(self, *, openIdConnectUrl: str, audience: str, **kwargs):
        super().__init__(openIdConnectUrl=openIdConnectUrl, **kwargs)
        resp = requests.get(openIdConnectUrl)
        resp.raise_for_status()
        self._wellknown = resp.json()
        jwks_uri = self._wellknown["jwks_uri"]

        resp = requests.get(jwks_uri)
        resp.raise_for_status()
        self._certs = resp.json()
        self._audience = audience


    @property
    def wellknown(self) -> dict:
        return self._wellknown


    async def __call__(self, request: Request) -> dict:
        scheme, token = get_authorization_scheme_param(await super().__call__(request))
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=401, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"}
                )
        try:
            token = jwt.decode(token, self._certs, audience=self._audience)
        except (ExpiredSignatureError, JWTError) as e:
            raise HTTPException(status_code=401, detail=f"Error validating token: {e}")
        return token