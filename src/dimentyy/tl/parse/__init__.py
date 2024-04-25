"""Better parsing modes for telethon.TelegramClient"""

from html.parser import HTMLParser
from typing import TypeAlias, Any

from telethon.tl.types import (TypeMessageEntity, MessageEntityBold,
                               MessageEntityItalic, MessageEntityUnderline,
                               MessageEntityCode, MessageEntityTextUrl,
                               MessageEntityMentionName, MessageEntityPre,
                               MessageEntitySpoiler, MessageEntityBlockquote,
                               MessageEntityStrike, MessageEntityCustomEmoji)

plain_entities = {MessageEntityBold, MessageEntityItalic, MessageEntityCode,
                  MessageEntityUnderline, MessageEntityStrike,
                  MessageEntitySpoiler, MessageEntityBlockquote}

Entities: TypeAlias = list[TypeMessageEntity]
Bundle: TypeAlias = tuple[str, Entities]


class _HTMLParser(HTMLParser):
    entity_tags = {
        # tag: cls
        "b": MessageEntityBold,
        "i": MessageEntityItalic,
        "u": MessageEntityUnderline,
        "s": MessageEntityStrike,
        "a": MessageEntityTextUrl,
        "link": MessageEntityTextUrl,
        "code": MessageEntityCode,
        "pre": MessageEntityPre,
        "mention": MessageEntityMentionName,
        "spoiler": MessageEntitySpoiler,
        "quote": MessageEntityBlockquote,
        "custom_emoji": MessageEntityCustomEmoji
    }

    entity_tag_attr_args = {
        # tag: {tag-attr: (arg-name, type, default)}
        "a": {"href": ("url", str, None)},
        "link": {"url": ("url", str, None)},
        "pre": {"language": ("language", str, '')},
        "mention": {"user_id": ("user_id", int, None)},
        "custom_emoji": {"document_id": ("document_id", int, None)},
    }

    def __init__(self):
        super().__init__()

        self.container = ParsingContainer()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Any]]):
        if tag not in self.entity_tags:
            return

        entity = self.entity_tags[tag]

        if entity in plain_entities:
            self.container.open_entity(entity)
            return

        attrs = dict(attrs)

        # unreadable dictionary comprehension :D
        self.container.open_entity(entity, **{
            arg_name:
                (None if attrs[attr] is None else arg_type(attrs[attr]))

                if attr in attrs

                else default

            for attr, (arg_name, arg_type, default) in self.entity_tag_attr_args[tag].items()
        })

    def handle_endtag(self, tag: str):
        self.container.close_entity(self.entity_tags[tag])

    def handle_data(self, data: str):  #
        self.container.feed_text(data)

    @classmethod
    def immediate(cls, data: str) -> Bundle:
        """
        Just a shorthand:
         - Initialize self;
         - Feed data;
         - Return bundle.
        """

        self = cls()
        self.feed(data)
        return self.container.bundle


# pylint: disable=missing-class-docstring
# this is an internal class, and it speaks for itself
class ParsingContainer:
    def __init__(self):
        self.raw_text: str = ""
        self.entities: Entities = []

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
    def bundle(self) -> Bundle:
        return self.raw_text, self.entities


class BetterParsing:
    """Use any of its inner classes!"""

    class HTML:
        """
        **Don't forget to initialize this class!**

        This class should primarily be used
        only by telethon.TelegramClient as it
        automatically parses and unparses messages
        making it easier to work with messages.

        **Setup**:

        >>> client = TelegramClient(...)
        >>> client.parse_mode = BetterParsing.HTML()
        """

        def parse(self, text: str) -> Bundle:
            """
            **This method is called by** ``telethon.TelegramClient``.
            """

            return _HTMLParser.immediate(text)

        def unparse(self, raw_text: str, entities: Entities):
            """
            **This method is called by** ``telethon.TelegramClient``.

            Unparsing occurs when you want to concatenate two messages
            """
            raise NotImplementedError


__all__ = [
    'BetterParsing'
]
