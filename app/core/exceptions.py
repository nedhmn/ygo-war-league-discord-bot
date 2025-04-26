from discord import app_commands


class SessionExpired(app_commands.AppCommandError):
    """Raised when a session has expired."""

    pass


class UnathorizedGuild(app_commands.AppCommandError):
    """Raised when a command is used in an unauthorized guild."""

    pass


class UserCancelled(app_commands.AppCommandError):
    """Raised when a user cancels a session."""

    pass


class UserRetry(app_commands.AppCommandError):
    """Raised when a user chooses to retry a session."""

    pass
