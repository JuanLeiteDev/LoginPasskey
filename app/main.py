from fastapi import FastAPI
from app.routes.auth_routes import auth_router
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.core import handlers as ha

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
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

app.add_exception_handler(
    ha.InvalidAuthenticationResponseError,
    ha.invalid_authentication_response_handler
)

app.add_exception_handler(
    ha.InvalidCredentialJSONError,
    ha.invalid_credential_json_handler
)

app.add_exception_handler(
    ha.CredentialUserMismatchError,
    ha.credential_user_mismatch_handler
)

app.add_exception_handler(
    ha.InactiveUserError,
    ha.inactive_user_handler
)

app.add_exception_handler(
    ha.RegistrationSessionNotFoundError,
    ha.registration_session_not_found_handler
)
