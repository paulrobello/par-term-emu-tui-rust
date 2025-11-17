from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from textual.message import Message

if TYPE_CHECKING:
    from textual.content import Content


@dataclass
class Flash(Message):
    """Request a message flash.

    Args:
        Message: Content of flash.
        style: Semantic style.
        duration: Duration in seconds or `None` for default.
    """

    content: str | Content
    style: Literal["default", "warning", "success", "error"]
    duration: float | None = None


@dataclass
class DirectoryChanged(Message):
    """Notify that the shell's current directory changed (via OSC 7).

    Args:
        directory: The new current working directory path.
    """

    directory: str


@dataclass
class TitleChanged(Message):
    """Notify that the terminal title changed (via OSC 0, 1, 2).

    Args:
        title: The new terminal title.
    """

    title: str
