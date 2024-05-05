"""Better parsing modes for telethon.TelegramClient"""
import html

from telethon import TelegramClient
from telethon.tl.types import TypeMessageEntity

from .new_html import HTMLParser, OnUnknownTag


class HTML:
    """
    This class should primarily be used
    only by telethon.TelegramClient as it
    automatically parses and unparses messages
    making it easier to work with messages.

    **Setup**:

    >>> client = TelegramClient(...)
    >>> parser = HTML.applied_to(client)
    """

    def __init__(self, client: TelegramClient, on_unknown_tag: OnUnknownTag = "ignore"):
        self.client = client
        self.on_unknown_tag = on_unknown_tag

    @classmethod
    def applied_to(cls, client: TelegramClient, on_unknown_tag: OnUnknownTag = "ignore"):
        self = cls(
            client=client,
            on_unknown_tag=on_unknown_tag
        )
        client.parse_mode = self
        return self

    def parse(self, text: str) -> tuple[str, list[TypeMessageEntity]]:
        """
        **This method is called by** ``telethon.TelegramClient``.
        """

        return HTMLParser.immediate(text, self.client, self.on_unknown_tag)

    def unparse(self, raw_text: str, entities: list[TypeMessageEntity]):
        """
        **This method is called by** ``telethon.TelegramClient``.

        Unparsing occurs when you want to concatenate two messages.
        """
        raise NotImplementedError

    @staticmethod
    def mention(user_id: int, content: str, escape: bool = True):
        """:returns: Mention tag as str."""

        return f"<mention user_id={user_id}>{html.escape(content) if escape else content}</mention>"


__all__ = [
    'HTML'
]
