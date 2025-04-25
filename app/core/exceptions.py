class UserCancelled(Exception):
    """Raised when a user cancels a session."""

    pass


class UserRetry(Exception):
    """Raised when a user chooses to retry a session."""

    pass
