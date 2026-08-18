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
