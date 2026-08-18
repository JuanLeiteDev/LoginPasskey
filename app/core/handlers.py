from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    ChallengeNotFoundError,
    CredentialNotFoundError,
    CredentialUserMismatchError,
    InactiveUserError,
    InternalServerError,
    InvalidAuthenticationResponseError,
    InvalidCredentialJSONError,
    InvalidRegistrationResponseError,
    PasskeyUserVerificationFailedError,
    RegistrationSessionNotFoundError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)


async def invalid_registration_response_handler(
    request: Request,
    exc: InvalidRegistrationResponseError,
):
    return JSONResponse(
        status_code=400,
        content={"detail": "Resposta de registro da passkey inválida."},
    )


async def invalid_authentication_response_handler(
    request: Request,
    exc: InvalidAuthenticationResponseError,
):
    return JSONResponse(
        status_code=401,
        content={"detail": "Resposta de autenticação da passkey inválida."},
    )


async def invalid_credential_json_handler(
    request: Request,
    exc: InvalidCredentialJSONError,
):
    return JSONResponse(
        status_code=400,
        content={"detail": "Formato da credencial WebAuthn inválido."},
    )


async def internal_server_error_handler(
    request: Request,
    exc: InternalServerError,
):
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocorreu um erro interno no servidor."},
    )


async def passkey_user_verification_failed_handler(
    request: Request,
    exc: PasskeyUserVerificationFailedError,
):
    return JSONResponse(
        status_code=401,
        content={"detail": "Não foi possível confirmar a verificação do utilizador."},
    )


async def username_already_exists_handler(
    request: Request,
    exc: UsernameAlreadyExistsError,
):
    return JSONResponse(
        status_code=409,
        content={"detail": "Já existe um utilizador com esse username."},
    )


async def challenge_not_found_handler(
    request: Request,
    exc: ChallengeNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail": "Challenge não encontrada ou expirou."},
    )


async def credential_not_found_handler(
    request: Request,
    exc: CredentialNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail": "Credencial não encontrada ou expirou."},
    )


async def user_not_found_handler(
    request: Request,
    exc: UserNotFoundError,
):
    return JSONResponse(
        status_code=404,
        content={"detail": "Utilizador não encontrado."},
    )


async def credential_user_mismatch_handler(
    request: Request,
    exc: CredentialUserMismatchError,
):
    return JSONResponse(
        status_code=401,
        content={"detail": "A credencial não pertence ao utilizador informado."},
    )


async def inactive_user_handler(
    request: Request,
    exc: InactiveUserError,
):
    return JSONResponse(
        status_code=403,
        content={"detail": "A conta do utilizador não está ativa."},
    )


async def registration_session_not_found_handler(
    request: Request,
    exc: RegistrationSessionNotFoundError,
):
    return JSONResponse(
        status_code=400,
        content={"detail": "Os dados da sessão de registro não foram encontrados."},
    )
