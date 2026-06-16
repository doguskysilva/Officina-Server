class DomainError(Exception):
    pass


class InvalidProjectOperation(DomainError):
    pass


class InvalidTaskOperation(DomainError):
    pass
