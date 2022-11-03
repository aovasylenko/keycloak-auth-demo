#from authlib.integrations.requests_client import OAuth2Session

from fastapi import Depends, FastAPI, Security, Request
from fastapi.security import OpenIdConnect
from pydantic import BaseModel
import uvicorn

app = FastAPI()

oid = OpenIdConnect(openIdConnectUrl="http://localhost:8080/realms/app/.well-known/openid-configuration")

class User(BaseModel):
    username: str


def get_current_user(oauth_header: str = Security(oid)):
    user = User(username=oauth_header)
    return user


@app.get("/")
async def base(request: Request, current_user: User = Depends(get_current_user)):
    # token = request.headers['authorization'].replace("Bearer ", "")


    print(current_user)

    # oauth = OAuth2Session(client_id="Test Client ID", client_secret="some-secret-string")
    # result = oauth.introspect_token(
    #     url="https://keycloak.sso.gwdg.de/auth/realms/MeDIC/protocol/openid-connect/token/introspect", token=token)
    # content = json.loads(result.content.decode())
    # if not content['active']:
    #     raise HTTPException(status_code=401, detail="Token expired or invalid")
    # else:
    #     return content


if __name__ == "__main__":
    uvicorn.run("app:app", port=5000, reload=True)
