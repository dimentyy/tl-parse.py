from typing import Any

from telethon.tl.types import TypeMessageEntity


# pylint: disable=missing-class-docstring
# this is an internal class, and it speaks for itself
class ParsingContainer:
    def __init__(self):
        self.raw_text: str = ""
        self.entities: list[TypeMessageEntity] = []

        self.unclosed_entities: dict[type[TypeMessageEntity], int] = {}

        self.unclosed_entity_args: dict[type[TypeMessageEntity], dict[str, Any]] = {}

    def feed_text(self, text: str):
        self.raw_text += text

    def open_entity(self, entity: type[TypeMessageEntity], **args: Any):
        self.unclosed_entities[entity] = self.raw_text_tl_len
        self.unclosed_entity_args[entity] = args

    def close_entity(self, entity: type[TypeMessageEntity], **args: Any):
        args = args | self.unclosed_entity_args.pop(entity, {})

        # If not all arguments were fulfilled
        if None in args.values():
            raise ValueError("Argument has no default value and no value was passed.")

        offset = self.unclosed_entities.pop(entity, 0)

        self.entities.append(entity(
            offset=offset,
            length=self.raw_text_tl_len - offset,
            **args
        ))

    @property
    def raw_text_tl_len(self) -> int:
        """
        Calculate length of the raw text to put in the message entity class.

        Using len() on raw text will result in incorrect formatting offset / length!
        """

        return len(self.raw_text.encode('utf-16-le')) // 2

    @property
    def bundle(self) -> tuple[str, list[TypeMessageEntity]]:
        return self.raw_text, self.entities
