# Yummizi Admin CLI — setup

## 1. Point the client at your Cognito user pool

Nothing is hardcoded — everything comes from environment variables, so
the same code works against dev/staging/prod:

```bash
export YUMMIZI_USER_POOL_ID="us-east-1_xxxxxxx"
export YUMMIZI_APP_CLIENT_ID="xxxxxxxxxxxxxxxxxxxxxxxxxx"
export YUMMIZI_REGION="us-east-1"
export YUMMIZI_API_URL="https://abc123.execute-api.us-east-1.amazonaws.com"
# Only set this if the app client has a secret (confidential client):
export YUMMIZI_APP_CLIENT_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

### Required app client configuration

This CLI uses the `USER_PASSWORD_AUTH` flow (`initiate_auth` with plain username/password), not SRP — far less boto3 ceremony for a terminal tool. On the app client used by this CLI:

- `ExplicitAuthFlows` must include `ALLOW_USER_PASSWORD_AUTH` (and `ALLOW_REFRESH_TOKEN_AUTH` if you want silent refresh).
- If you're reusing an app client meant for a browser/mobile client, it likely has no secret — that's fine, `YUMMIZI_APP_CLIENT_SECRET` is optional and the `SECRET_HASH` is only computed when it's set.
- Self-sign-up must be enabled on the pool if you want `sign_up` to work (admins created purely via `AdminCreateUser` elsewhere can skip it and just sign in).

### Which token goes to the API

`cli.py` sends `tokens.access_token` as the bearer token to API Gateway. This is correct **only if your HTTP API's JWT authorizer validates the access token** (the typical setup — it checks `client_id` against your app client). If your authorizer instead validates the **ID token** (checking `aud`), swap `tokens.access_token` for `tokens.id_token` in `cli.py`. They are not interchangeable — using the wrong one fails authorization with a 401, not a helpful error.

## 2. Install and run

```bash
pip install -r requirements.txt
python main.py
```

Only `boto3` is a third-party dependency — the HTTP calls use the standard library's `urllib`.

## 3. How response-shape handling works

`models.py` parses every API response into a frozen dataclass instead of passing raw `dict`s around:

- **Restaurant feed:** `restaurants/feed` returns a list of `FeedItem` objects with restaurant identity, branding, section, dishes, location, and contact information. `get_all_restaurants()` currently fetches this feed in one request; add pagination if its size grows.
- **Tracking requests:** `tracking/{restaurantId}/{from}/{to}/requests` returns a `restaurantRequests` list of `ActiveRequests`. The CLI displays request state, user, queue timestamp, and arrival time.
- **Required fields raise clearly.** Missing fields and invalid response shapes raise `ModelParseError` instead of failing later during display.
