from discord import app_commands


class UserCancelled(app_commands.AppCommandError):
    """Raised when a user cancels a session."""

    pass


class UserRetry(app_commands.AppCommandError):
    """Raised when a user chooses to retry a session."""

    pass


class InvalidDecklist(app_commands.AppCommandError):
    """Proxy HAT format Decklist checker for when card requests fail"""

    pass


class CardImageError(app_commands.AppCommandError):
    pass
