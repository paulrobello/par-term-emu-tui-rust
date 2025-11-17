from typing import TYPE_CHECKING, Literal

from textual.reactive import var
from textual.widgets import Static

if TYPE_CHECKING:
    from textual.content import Content
    from textual.timer import Timer

# Adapted from Toad project by Will McGugan


class FlashLine(Static):
    DEFAULT_CSS = """
    FlashLine {
        height: 1;
        width: 1fr;
        background: $success 10%;
        color: $text-success;
        text-align: center;
        visibility: hidden;
        text-wrap: nowrap;
        text-overflow: ellipsis;
        overlay: screen;
        offset-y: 0;

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

        &.-location-bottom {
            offset-y: 0;
        }

        &.-location-top {
            position: absolute;
        }
    }
    """

    flash_timer: var[Timer | None] = var(None)

    def flash(
        self,
        content: str | Content,
        *,
        duration: float | None = None,
        style: Literal["default", "success", "warning", "error"] = "default",
        location: Literal["bottom", "top"] = "bottom",
    ) -> None:
        """Flash the content for a brief period.

        Args:
            content: Content to show.
            duration: Duration in seconds to show content.
            style: A semantic style.
            location: top or bottom.
        """
        if self.flash_timer is not None:
            self.flash_timer.stop()

        self.visible = False

        def hide() -> None:
            """Hide the content after timer expired."""
            self.visible = False

        self.update(content)
        self.remove_class(
            "-default", "-success", "-warning", "-error", "-location-bottom", "-location-top", update=False
        )
        self.add_class(
            f"-{style}",
            f"-location-{location}",
        )
        self.visible = True

        if duration is None or duration <= 0.0:
            duration = 3.0

        self.flash_timer = self.set_timer(duration, hide)
