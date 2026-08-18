class DomainError(ValueError):
    """A rejected domain operation with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


class AuthorizationError(DomainError):
    pass

