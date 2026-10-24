# What is Yummizi (ymz)?
Yummizi was a foodtech startup project that allowed restaurants to prepare diners' food while they were on their way to the establishment. Although I didn't continue with the project due to validation issues, it taught me a lot about marketing, sales, and full-stack development.

I think that the best way to be grateful for what I have is to share it. Here, I share with you what I learned by building a stable, real-time platform that connects diners with restaurants the Yummizi way.

# Sub-systems of the platform
+ [AWS Lambda with hono](https://github.com/PieroEngineer/ymz-aws-lambda-with-hono) (TS) 
+ [AWS serverless configuration with AWS SAM](https://github.com/PieroEngineer/ymz-iac-with-aws-sam) (yaml) 
+ [Client for process observability](https://github.com/PieroEngineer/ymz-admin-client-with-python) (Python) 
+ [Landing page](https://github.com/PieroEngineer/ymz-landing-page) (HTML + JS + CSS) 
+ [Restaurant Web app](https://github.com/PieroEngineer/ymz-restaurant-client-side) (TS + Vite + React) 
+ [Diner Android app](https://github.com/PieroEngineer/ymz-diner-client-side) (Kotlin) 

# Yummizi sample videos (Spanish)

+ [Diner's side](https://youtu.be/7b_l_gql7mM?si=8SZDDcmm5-jZD5qW) 🍽️
+ [Restaurant's side](https://youtu.be/fAfyB8eCOTE?si=P1Oo85OMT-clABDw) 🏪

# Yummizi Admin CLI

A terminal client for authenticating with Amazon Cognito and making read-only
requests to the Yummizi admin HTTP API. API responses are parsed into typed
dataclasses before the CLI displays them.

## Requirements

- Python 3.10 or newer
- AWS Cognito user pool and app client
- Access to the Yummizi HTTP API

Install the project's dependencies:

```bash
python -m pip install -r requirements.txt
```

## Configuration

Set the following environment variables before starting the CLI:

| Variable | Required | Description |
| --- | --- | --- |
| `YUMMIZI_USER_POOL_ID` | Yes | Cognito user pool ID |
| `YUMMIZI_APP_CLIENT_ID` | Yes | Cognito app client ID |
| `YUMMIZI_REGION` | Yes | AWS region containing the user pool |
| `YUMMIZI_API_URL` | Yes | Base URL of the admin HTTP API |
| `ADMIN_EMAIL` | Yes | Email used to sign in |
| `ADMIN_PWD` | Yes | Password used to sign in |
| `YUMMIZI_APP_CLIENT_SECRET` | No | Optional app-client secret setting |

For the current PowerShell session:

```powershell
$env:YUMMIZI_USER_POOL_ID = "your-user-pool-id"
$env:YUMMIZI_APP_CLIENT_ID = "your-app-client-id"
$env:YUMMIZI_REGION = "your-aws-region"
$env:YUMMIZI_API_URL = "https://your-api.example.com"
$env:ADMIN_EMAIL = "admin@example.com"
$env:ADMIN_PWD = "your-password"
```

Do not commit real credentials, tokens, or client secrets to the repository.
The CLI reads the sign-in credentials from `ADMIN_EMAIL` and `ADMIN_PWD`; it
does not prompt for them.

The sign-in implementation uses PyCognito's SRP authentication. Configure the
Cognito app client to allow the SRP flow. The authenticator also has a refresh
method, but the current CLI does not automatically refresh tokens. The API
client sends the access token as a bearer token, so the API's JWT authorizer
must accept that token type.

## Run

From the repository root:

```bash
python main.py
```

The CLI signs in before displaying its menu. Available service operations
include:

| Operation | API path |
| --- | --- |
| Restaurant feed | `GET restaurants/feed?userId=...` |
| Requests for a restaurant and date range | `GET tracking/{restaurantId}/{from}/{to}/requests` |
| Requests for a date range | `GET tracking/{from}/{to}/requests` |
| Orders for a date range | `GET tracking/{from}/{to}/orders` |
| Orders for a restaurant and date range | `GET tracking/{restaurantId}/{from}/{to}/orders` |

Dates are entered as `YYYY-MM-DD`. The API client uses Python's standard
library for HTTP requests; Cognito authentication is handled by the installed
Python dependencies.

## Current limitations

- The restaurant feed request currently sends the fixed query value
  `userId=someUserId`; update it in `AdminService` for the intended user.
- The menu's restaurant-feed and tracking-request selections currently call
  their handlers with incompatible arguments. Those selections need a small
  CLI wiring fix before they can be used; the corresponding service methods
  are implemented.
- Sign-up and confirmation methods exist in the authenticator, but are not
  exposed in the current CLI flow.
- API results must match the required fields and shapes in `models.py`.
  Invalid responses raise `ModelParseError` rather than being displayed as
  raw dictionaries.

# Author

Made with 💙 by **Piero Olivas Tuesta**
