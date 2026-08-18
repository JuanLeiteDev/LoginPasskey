from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    InvalidRegistrationResponseError,
    InternalServerError,
    PasskeyUserVerificationFailedError,
    ActiveUserEmailAlreadyExistsError,
    ChallengeNotFoundError,
    CredentialNotFoundError,
    UserNotFoundError
)


async def invalid_registration_response_handler(
    request: Request,
    exc: InvalidRegistrationResponseError
):
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Resposta de registro da passkey inválida."
        }
    )


async def internal_server_error_handler(
    request: Request,
    exc: InternalServerError
):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Ocorreu um erro interno no servidor."
        }
    )


async def passkey_user_verification_failed_handler(
    request: Request,
    exc: PasskeyUserVerificationFailedError
):
    return JSONResponse(
        status_code=401,
        content={
            "detail": "Não foi possível verificar o usuário real durante o registro da passkey."
        }
    )

async def active_user_email_already_exists_handler(
    request: Request,
    exc: ActiveUserEmailAlreadyExistsError
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": "Já existe um utilizador ativo com esse e-mail."
        }
    )

async def challenge_not_found_handler(
    request: Request,
    exc: ChallengeNotFoundError
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Challenge não encontrada ou expirou."
        }
    )

async def credential_not_found_handler(
    request: Request,
    exc: CredentialNotFoundError
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Credencial não encontrada ou expirou."
        }
    )

async def user_not_found_handler(
    request: Request,
    exc: UserNotFoundError
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Usuário não encontrado."
        }
    )