from textual.app import ComposeResult
from textual.widgets import Button, Static
from textual.containers import Center
from textual.screen import Screen
from typing import Any

from screen.dashboard import DashboardScreen


class GreetingScreen(Screen[Any]):
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        with Center():
            yield Static("DecemberBanken ❄")
            yield Static("Din bank direkt i kommandotolken", id="greeting-subtitle")
            yield Button("Logga in", id="greeting-next", variant="primary", flat=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.app.push_screen(DashboardScreen())
