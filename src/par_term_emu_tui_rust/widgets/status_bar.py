from typing import TYPE_CHECKING, Literal

from textual.widgets import Static

if TYPE_CHECKING:
    from textual.content import Content

# Adapted from Toad project by Will McGugan


class StatusBar(Static):
    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        width: 1fr;
        background: $success 10%;
        color: $text-success;
        text-align: center;
        visibility: hidden;
        text-wrap: nowrap;
        text-overflow: ellipsis;

        &.-default {
            background: $primary 10%;
            color: $text-primary;
        }

        &.-success {
            background: $success 10%;
            color: $text-success;
        }

        &.-warning {
            background: $warning 10%;
            color: $text-warning;
        }

        &.-error {
            background: $error 10%;
            color: $text-error;
        }
    }
    """

    def update_content(
        self,
        content: str | Content,
        *,
        style: Literal["default", "success", "warning", "error"] = "default",
    ) -> None:
        """Show Status Bar Info

        Args:
            content: Content to show.
            style: A semantic style.
        """

        self.update(content)
        self.update_style(style)

    def update_style(
        self,
        style: Literal["default", "success", "warning", "error"] = "default",
    ) -> None:
        """Change status bar style.

        Args:
            style: A semantic style.
        """

        self.remove_class("-default", "-success", "-warning", "-error", update=False)
        self.add_class(f"-{style}")
