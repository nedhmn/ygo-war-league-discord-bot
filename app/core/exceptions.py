from discord import app_commands


class UserCancelled(app_commands.AppCommandError):
    """Raised when a user cancels a session."""

    pass


class UserRetry(app_commands.AppCommandError):
    """Raised when a user chooses to retry a session."""

    pass


class InvalidDecklist(app_commands.AppCommandError):
    """Raised when a deck's ydk contents fails Decklist validation."""

    pass


class CardImageError(app_commands.AppCommandError):
    """Raised when DeckImager cannot successfully request a card image."""

    pass
