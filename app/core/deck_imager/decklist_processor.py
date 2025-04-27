from app.core.deck_imager.models import Decklist
from app.core.deck_imager.config import DecklistProcessorSetting


class DecklistProcessor:
    def __init__(self, settings: DecklistProcessorSetting):
        """Initialize with deck file processor settings"""
        self.settings = settings

    def create_decklist(self, deck_ydk_content: str) -> Decklist:
        """Parse the deck content and return a Decklist model instance with URL mappings for card ids"""
        sections = self._parse_deck_string(deck_ydk_content)
        deck_urls = {
            key: self._map_card_ids_to_urls(value) for key, value in sections.items()
        }
        return Decklist(**deck_urls)

    def _parse_deck_string(self, content: str) -> dict[str, list[str]]:
        """Parse the deck string into main, side, and extra sections with validations"""
        sections: dict[str, list[str]] = {"main": [], "side": [], "extra": []}
        current_section = None
        lines = content.splitlines()

        if not self._validate_line_count(len(lines)):
            raise ValueError("The deck file must have between 40 and 100 lines")

        for line in lines:
            line = line.strip()

            if not line:
                continue

            if line.startswith("#") or line.startswith("!"):
                marker = line[1:].strip().lower()
                if marker in sections:
                    current_section = marker
                else:
                    current_section = None
            elif current_section is not None:
                if not self._validate_card_id(line):
                    raise ValueError(f"Invalid card id: '{line}'")
                sections[current_section].append(line)

        return sections

    def _map_card_ids_to_urls(self, card_ids: list[str]) -> list[str]:
        """Convert card ids to urls"""
        return [
            f"{self.settings.CARD_IMAGE_BASE_URL}{card_id}{self.settings.CARD_IMAGE_FORMAT}"
            for card_id in card_ids
        ]

    def _validate_line_count(self, count: int) -> bool:
        # Invalidate if the ydk has unexpected number of lines
        return 40 <= count <= 100

    def _validate_card_id(self, card_id: str) -> bool:
        # Invalidate if id has gte 10 characters
        if len(card_id) >= 10:
            return False

        # Invalidate if id cannot be parsed to int
        try:
            int(card_id)
        except ValueError:
            return False

        return True
