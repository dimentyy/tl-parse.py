from html.parser import HTMLParser as PythonsHTMLParser
from typing import TypeAlias, Literal, Any

from telethon.tl.types import (MessageEntityBold, MessageEntityItalic, MessageEntityCode,
                               MessageEntityStrike, MessageEntityUnderline, MessageEntityBlockquote,
                               MessageEntitySpoiler, MessageEntityTextUrl, MessageEntityPre,
                               MessageEntityMentionName, MessageEntityCustomEmoji,
                               TypeMessageEntity)

from .types import plain_entities
from .container import ParsingContainer

OnUnknownTag: TypeAlias = Literal["ignore", "raise"]


class HTMLParser(PythonsHTMLParser):
    def __init__(self, on_unknown_tag: OnUnknownTag):
        super().__init__()

        self.on_unknown_tag = on_unknown_tag
        self.container = ParsingContainer()

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
        "custom_emoji": MessageEntityCustomEmoji  # needs testing
    }

    entity_tag_attr_args = {
        # tag: {tag-attr: (arg-name, type, default)}
        "a": {"href": ("url", str, None)},
        "link": {"url": ("url", str, None)},
        "pre": {"language": ("language", str, '')},
        "mention": {"user_id": ("user_id", int, None)},
        "custom_emoji": {"document_id": ("document_id", int, None)},
    }

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Any]]):
        if tag not in self.entity_tags:

            # pylint: disable=no-else-return
            if self.on_unknown_tag == "ignore":
                return
            elif self.on_unknown_tag == "raise":
                formatted_tag = f"""<{tag}{''.join([
                    key if value is None else f' {key}="{value}"' for key, value in attrs
                ])}>"""

                raise ValueError(f"Bad HTML-tag: {formatted_tag}")
            else:
                raise ValueError(f"Unknown '{self.on_unknown_tag}' action on unknown tag.")

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
    def immediate(cls, data: str, unknown_tag: OnUnknownTag) -> tuple[str, list[TypeMessageEntity]]:
        """
        Just a shorthand:
         - Initialize self;
         - Feed data;
         - Return text & entities.
        """

        self = cls(unknown_tag)
        self.feed(data)
        return self.container.raw_text, self.container.entities
