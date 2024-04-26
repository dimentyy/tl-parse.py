"""Better parsing modes for telethon.TelegramClient"""
from telethon.tl.types import TypeMessageEntity

from .new_html import HTMLParser, OnUnknownTag


class HTML:
    """
    **Don't forget to initialize this class!**

    This class should primarily be used
    only by telethon.TelegramClient as it
    automatically parses and unparses messages
    making it easier to work with messages.

    **Setup**:

    >>> client = TelegramClient(...)
    >>> client.parse_mode = HTML()
    """

    def __init__(self, on_unknown_tag: OnUnknownTag = "ignore"):
        self.on_unknown_tag = on_unknown_tag

    def parse(self, text: str) -> tuple[str, list[TypeMessageEntity]]:
        """
        **This method is called by** ``telethon.TelegramClient``.
        """

        return HTMLParser.immediate(text, self.on_unknown_tag)

    def unparse(self, raw_text: str, entities: list[TypeMessageEntity]):
        """
        **This method is called by** ``telethon.TelegramClient``.

        Unparsing occurs when you want to concatenate two messages
        """
        raise NotImplementedError


__all__ = [
    'HTML'
]
