import asyncio
import io

import httpx
from PIL import Image

from app.core.deck_imager.config import DeckImagerSetting
from app.core.deck_imager.models import Decklist
from app.core.exceptions import CardImageError


class DeckImager:
    def __init__(self, settings: DeckImagerSetting):
        self.settings = settings

    async def generate_deck_image(self, deck: Decklist) -> io.BytesIO:
        """Generate the deck composite image"""
        composite = await self._create_composite(deck)
        buffer = io.BytesIO()
        composite.save(
            buffer,
            format=self.settings.IMAGE_FORMAT,
            quality=self.settings.IMAGE_QUALITY,
        )

        return buffer

    async def _create_composite(self, deck: Decklist) -> Image.Image:
        """Create composite image combining main, side, and extra deck sections"""
        image_cache = await self._fetch_and_process_unique_images(deck)

        main_images = [image_cache[url] for url in deck.main if url in image_cache]
        side_images = [image_cache[url] for url in deck.side if url in image_cache]
        extra_images = [image_cache[url] for url in deck.extra if url in image_cache]

        main_grid = self._create_main_deck_grid(main_images)
        target_width = main_grid.width
        sections = [main_grid]

        if side_images:
            side_grid = self._create_extra_deck_row(side_images)
            sections.append(self._scale_to_width(side_grid, target_width))

        if extra_images:
            extra_grid = self._create_extra_deck_row(extra_images)
            sections.append(self._scale_to_width(extra_grid, target_width))

        total_height = sum(section.height for section in sections)
        total_height += self.settings.DECK_SPACING * (len(sections) - 1)
        composite = Image.new("RGBA", (target_width, total_height))
        y_offset = 0

        for section in sections:
            composite.paste(section, (0, y_offset), section)
            y_offset += section.height + self.settings.DECK_SPACING

        return composite

    async def _fetch_and_process_unique_images(
        self, deck: Decklist
    ) -> dict[str, Image.Image]:
        """Fetch and process unique images from deck for main, side, and extra"""
        # Get unique urls to not make multiple requests for one card
        unique_urls = list(set(deck.main + deck.side + deck.extra))

        async with httpx.AsyncClient() as client:
            tasks = {
                url: self._fetch_and_process_image(client, url) for url in unique_urls
            }
            images = await asyncio.gather(*tasks.values())

        return dict(zip(unique_urls, images))

    async def _fetch_and_process_image(
        self, client: httpx.AsyncClient, url: str
    ) -> Image.Image:
        """Fetch and process a single image"""
        try:
            # Fetch image
            response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError:
            raise CardImageError

        # Process image
        img = Image.open(io.BytesIO(response.content)).convert("RGBA")
        return img.resize(self.settings.CARD_SIZE, Image.Resampling.LANCZOS)

    def _create_main_deck_grid(self, images: list[Image.Image]) -> Image.Image:
        """Create a grid for main deck images arranged with 10 cards per row"""
        card_w, card_h = self.settings.CARD_SIZE
        cards_per_row = 10

        num_cards = len(images)
        num_rows = (num_cards + cards_per_row - 1) // cards_per_row

        grid_w = cards_per_row * card_w
        grid_h = num_rows * card_h
        grid = Image.new("RGBA", (grid_w, grid_h))

        for i, img in enumerate(images):
            x = (i % cards_per_row) * card_w
            y = (i // cards_per_row) * card_h
            grid.paste(img, (x, y), img)

        return grid

    def _create_extra_deck_row(self, images: list[Image.Image]) -> Image.Image:
        """Create a row grid for extra or side deck images with 15 cards"""
        return self._create_row_grid(images, columns=15)

    def _create_row_grid(self, images: list[Image.Image], columns: int) -> Image.Image:
        """Create a single row grid of images with specified number of columns"""
        card_w, card_h = self.settings.CARD_SIZE

        grid_w = columns * card_w
        grid = Image.new("RGBA", (grid_w, card_h))

        for i, img in enumerate(images[:columns]):
            grid.paste(img, (i * card_w, 0), img)

        return grid

    def _scale_to_width(self, image: Image.Image, target_width: int) -> Image.Image:
        """Scale an image to the target width while preserving aspect ratio"""
        scale_factor = target_width / image.width
        new_height = int(image.height * scale_factor)

        return image.resize((target_width, new_height), Image.Resampling.LANCZOS)
