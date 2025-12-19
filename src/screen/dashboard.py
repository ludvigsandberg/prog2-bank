from textual.app import ComposeResult
from textual.widgets import Button, Static
from textual.containers import Center, Container
from textual.screen import Screen
from typing import Any

from screen.overview import OverviewScreen
from screen.transaction import TransactionScreen, TransactionType


class DashboardScreen(Screen[Any]):
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        with Center():
            content = Container(classes="content")
            content.border_title = "DecemberBanken"

            with content:
                yield Button(
                    "Översikt",
                    id="dashboard-overview",
                    classes="dashboard-button",
                    flat=True,
                    variant="default",
                )

                yield Button(
                    "Sätt in",
                    id="dashboard-deposit",
                    classes="dashboard-button",
                    flat=True,
                    variant="primary",
                )

                yield Button(
                    "Ta ut",
                    id="dashboard-withdraw",
                    classes="dashboard-button",
                    flat=True,
                    variant="error",
                )

                yield Button(
                    "Överför",
                    id="dashboard-transfer",
                    classes="dashboard-button",
                    flat=True,
                    variant="default",
                )

                quit = Button(
                    "Logga ut",
                    id="dashboard-logout",
                    classes="dashboard-button",
                    flat=True,
                    variant="default",
                )
                quit.styles.margin = (1, 0, 0, 0)
                yield quit

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "dashboard-overview":
                self.app.push_screen(OverviewScreen())

            case "dashboard-logout":
                self.app.exit()

            case "dashboard-deposit":
                self.app.push_screen(TransactionScreen(TransactionType.DEPOSIT))

            case "dashboard-withdraw":
                self.app.push_screen(TransactionScreen(TransactionType.WITHDRAW))

            case "dashboard-transfer":
                self.app.push_screen(TransactionScreen(TransactionType.TRANSFER))
