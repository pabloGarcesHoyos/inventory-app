class DuplicateEmailException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class InactiveUserException(Exception):
    pass


class InvalidCredentialsException(Exception):
    pass


class InvalidRoleException(Exception):
    pass


class ForbiddenOperationException(Exception):
    pass
