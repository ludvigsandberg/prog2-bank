from textual.app import ComposeResult
from textual.widgets import Button, ListView, ListItem, Label
from textual.containers import Center, Container, Horizontal
from textual.screen import Screen
from typing import Any

from bank import Account
from screen.account_dashboard import AccountDashboardScreen
from screen.create_account import CreateAccountScreen
from screen.simulate_interest import SimulateInterestScreen


class AccountListItem(ListItem):
    def __init__(self, account: Account):
        super().__init__(classes="overview-account-list-item")
        self.border_subtitle = account.type.value
        self.account = account

    def compose(self):
        yield Label(self.account.name)
        yield Label(f"{self.account.balance:.2f} kr")

    def on_click(self):
        self.app.push_screen(AccountDashboardScreen(self.account))


class OverviewScreen(Screen[Any]):
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        with Center():
            content = Container(classes="content")
            content.border_title = "Översikt"

            with content:
                self.total_label = Label(
                    f"Totala tillgångar {sum(account.balance for account in self.app.bank.accounts.values()):.2f} kr",
                    classes="margin-bottom",
                )
                yield self.total_label

                self.list = ListView(
                    *(
                        AccountListItem(account)
                        for account in self.app.bank.accounts.values()
                    )
                )
                yield self.list

                yield Button(
                    "+ Nytt konto",
                    id="overview-new-account-list-item",
                    classes="margin-bottom",
                    flat=True,
                    variant="default",
                )

                with Horizontal():
                    yield Button(
                        "Tillbaka",
                        id="overview-back-button",
                        flat=True,
                        variant="default",
                    )
                    yield Button(
                        "Simulera ränteutbetalning",
                        id="overview-simulate-interest-button",
                        classes="margin-left",
                        flat=True,
                        variant="primary",
                    )

    def on_screen_resume(self) -> None:
        # uppdatera lista med konton
        self.list.clear()
        for account in self.app.bank.accounts.values():
            self.list.append(AccountListItem(account))

        # uppdatera "totala tillgångar" label
        total = sum(account.balance for account in self.app.bank.accounts.values())
        self.total_label.update(f"Totala tillgångar {total:.2f} kr")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "overview-back-button":
                self.app.pop_screen()

            case "overview-new-account-list-item":
                self.app.push_screen(CreateAccountScreen())

            case "overview-simulate-interest-button":
                self.app.push_screen(SimulateInterestScreen())
