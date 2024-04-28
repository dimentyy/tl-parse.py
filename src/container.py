from telethon.tl.types import (MessageEntityBold, MessageEntityItalic, MessageEntityCode,
                               MessageEntityStrike, MessageEntityUnderline, MessageEntityBlockquote,
                               MessageEntitySpoiler, TypeMessageEntity)

PlainEntities = {MessageEntitySpoiler, MessageEntityUnderline, MessageEntityBlockquote,
                 MessageEntityCode, MessageEntityStrike, MessageEntityItalic, MessageEntityBold}


# pylint: disable=missing-class-docstring
# this is an internal class, and it speaks for itself
class ParsingContainer:
    def __init__(self):
        self._raw_text: str = ""
        self._entities: list[TypeMessageEntity] = []

        self._unclosed_entities: dict[type[TypeMessageEntity], tuple[int, set]] = {}

        self._unclosed_entity_args: dict[type[TypeMessageEntity], dict[str, str | int]] = {}

    @property
    def raw_text(self):
        return self._raw_text

    @property
    def entities(self):
        return self._entities

    def feed_text(self, text: str):
        self._raw_text += text

    def open_entity(self, entity: type[TypeMessageEntity], **args: str | int):
        self._unclosed_entities[entity] = self.raw_text_tl_len, set()
        self._unclosed_entity_args[entity] = args

    def close_entity(self, entity: type[TypeMessageEntity], **args: str | int):
        args = args | self._unclosed_entity_args.pop(entity, {})

        # If not all arguments were fulfilled
        # TODO: mode to pass this?
        if None in args.values():
            raise ValueError("Argument has no default value and no value was passed.")

        # TODO: mode for handling not opened entities (ignore / raise / full-fill)

        current_offset, breaks = self._unclosed_entities.pop(entity, (0, set()))
        end_offset = self.raw_text_tl_len

        # what?
        for break_offset in sorted(breaks | {end_offset} - {current_offset}):
            self._entities.append(entity(
                offset=current_offset,
                length=break_offset - current_offset,
                **args
            ))

            current_offset = break_offset

        for unclosed_offset, unclosed_breaks in self._unclosed_entities.values():
            if unclosed_offset < end_offset:
                unclosed_breaks.add(end_offset)

    @property
    def raw_text_tl_len(self) -> int:
        """
        Calculate length of the raw text to put in the message entity class.

        Using len() on raw text will result in incorrect formatting offset / length!
        """

        return len(self._raw_text.encode('utf-16-le')) // 2

    @property
    def bundle(self) -> tuple[str, list[TypeMessageEntity]]:
        """:returns: raw_text, entities"""

        return self._raw_text, self._entities


__all__ = [
    'ParsingContainer', 'PlainEntities'
]
