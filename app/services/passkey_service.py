from sqlalchemy.orm import Session
from fastapi import Request, Response

from app.core.exceptions import (
    CredentialUserMismatchError,
    InactiveUserError,
    PasskeyUserVerificationFailedError,
    UsernameAlreadyExistsError,
    ChallengeNotFoundError,
    CredentialNotFoundError,
    RegistrationSessionNotFoundError,
    UserNotFoundError
)
from app.repository.passkey_repo import PasskeyRepo
from app.repository.user_repo import UserRepo
from app.schemas.user import UserCreate
from app.core.security import (
    get_authenticator_selection,
    get_generate_registration_options,
    bytes_to_str_base64,
    str_to_bytes_base64,
    get_verify_registration_response,
    get_generate_authentication_options,
    get_verify_authentication_response,
    create_jwt_token,
    set_token,
    set_login_tokens
)

from webauthn.helpers.options_to_json_dict import options_to_json_dict
from webauthn.helpers.structs import (
    RegistrationCredential,
    AuthenticationCredential
)

from app.core.config import token_settings

class PasskeyService():
    def __init__(self, session: Session):
        self.session = session

    def register_options_service(self, user: UserCreate):
        existing_user = UserRepo(self.session).get_user_by_name(user.username)
        if existing_user:
            if existing_user.status:
                raise UsernameAlreadyExistsError()

        else:
            existing_user = UserRepo(self.session).create_user(user)

        self.session.refresh(existing_user)

        auth_selection = get_authenticator_selection()
        options = get_generate_registration_options(existing_user, auth_selection)
        challenge = bytes_to_str_base64(options.challenge)
        options_json = options_to_json_dict(options)
        user_id = bytes_to_str_base64(existing_user.id)

        return options_json, challenge, user_id

    def register_verify_service(self, credential: RegistrationCredential, request: Request):
        challenge = request.session.get("registration_challenge")
        if not challenge:
            raise ChallengeNotFoundError()

        if not credential:
            raise CredentialNotFoundError()
        
        challenge_bytes = str_to_bytes_base64(challenge)
        verification = get_verify_registration_response(credential, challenge_bytes)

        if not verification.user_verified:
            raise PasskeyUserVerificationFailedError()
        
        user_id_str = request.session.get("current_user")
        if not user_id_str:
            raise RegistrationSessionNotFoundError()
         
        user_id = str_to_bytes_base64(user_id_str)

        if not user_id:
            raise RegistrationSessionNotFoundError()

        user = UserRepo(self.session).get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        PasskeyRepo(self.session).save_credentials_passkey(verification, user_id)
        UserRepo(self.session).update_user_status(user)

        request.session.clear()
        return f"Conta criada com succeso!"

    def auth_options_service(self):
        options = get_generate_authentication_options()

        options_json = options_to_json_dict(options)
        challenge = bytes_to_str_base64(options.challenge)
        
        return options_json, challenge

    def auth_verify_service(
        self, 
        credentials: AuthenticationCredential, 
        request: Request, 
        response: Response
    ):
        challenge = request.session.get("authentication_challenge")
        if not challenge:
            raise ChallengeNotFoundError()

        if not credentials:
            raise CredentialNotFoundError()

        challenge_bytes = str_to_bytes_base64(challenge)
        existing_credential = PasskeyRepo(self.session).get_credential_by_id(credentials.raw_id)

        if not existing_credential:
            raise CredentialNotFoundError()

        if not existing_credential.user:
            raise UserNotFoundError()

        user_id = credentials.response.user_handle
        if not user_id == existing_credential.user_id:
            raise CredentialUserMismatchError()

        if not existing_credential.user.status:
            raise InactiveUserError()

        verification = get_verify_authentication_response(
            credentials,  
            challenge_bytes,
            existing_credential
        )

        if not verification.user_verified:
            raise PasskeyUserVerificationFailedError() 

        PasskeyRepo(self.session).update_sign_count(
            verification.new_sign_count, 
            existing_credential
        )

        request.session.clear()
        set_login_tokens(response=response, user_id=user_id)

        return f"Login efetuado com sucesso!"
