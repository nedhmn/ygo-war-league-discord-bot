import io
from dataclasses import dataclass


@dataclass
class ConfirmationDetails:
    url: str
    image_bytes: io.BytesIO
