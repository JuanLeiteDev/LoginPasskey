class InvalidRegistrationResponseError(Exception):
    pass


class InternalServerError(Exception):
    pass


class PasskeyUserVerificationFailedError(Exception):
    pass


class ActiveUserEmailAlreadyExistsError(Exception):
    pass


class ChallengeNotFoundError(Exception):
    pass


class CredentialNotFoundError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidAuthenticationResponseError(Exception):
    pass


class InvalidCredentialJSONError(Exception):
    pass


class CredentialUserMismatchError(Exception):
    pass


class InactiveUserError(Exception):
    pass


class RegistrationSessionNotFoundError(Exception):
    pass
