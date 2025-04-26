from pydantic import BaseModel, field_validator


class Decklist(BaseModel):
    main: list[str]
    side: list[str]
    extra: list[str]

    @field_validator("main", mode="after")
    @classmethod
    def validate_main(cls, value: list[str]) -> list[str]:
        if not 40 <= len(value) <= 60:
            raise ValueError("Main deck needs to be between 40 and 60 cards")
        return value

    @field_validator("side", "extra", mode="after")
    @classmethod
    def validate_side_and_extra(cls, value: list[str]) -> list[str]:
        if not 0 <= len(value) <= 15:
            raise ValueError("Side and extra decks need to be between 0 and 15 cards")
        return value
