from fastapi import FastAPI
from app.routes.auth_routes import auth_router
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.core import handlers as ha

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.DATABASE_URL
)

app.include_router(auth_router)

app.add_exception_handler(
    ha.InvalidRegistrationResponseError,
    ha.invalid_registration_response_handler
)

app.add_exception_handler(
    ha.InternalServerError,
    ha.internal_server_error_handler
)

app.add_exception_handler(
    ha.PasskeyUserVerificationFailedError,
    ha.passkey_user_verification_failed_handler
)

app.add_exception_handler(
    ha.ActiveUserEmailAlreadyExistsError,
    ha.active_user_email_already_exists_handler
)

app.add_exception_handler(
    ha.ChallengeNotFoundError,
    ha.challenge_not_found_handler
)

app.add_exception_handler(
    ha.CredentialNotFoundError,
    ha.credential_not_found_handler
)

app.add_exception_handler(
    ha.UserNotFoundError,
    ha.user_not_found_handler
)
