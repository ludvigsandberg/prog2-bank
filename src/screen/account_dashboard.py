from textual.app import ComposeResult
from textual.widgets import Button, Label, DataTable
from textual.containers import Center, Container, Horizontal, Vertical
from textual.screen import Screen
from typing import Any

from bank import Account, AccountType
from screen.transaction import TransactionScreen, TransactionType


class AccountDashboardScreen(Screen[Any]):
    def __init__(self, account: Account):
        super().__init__()
        self.account = account

    def on_screen_resume(self) -> None:
        self.refresh_table()

    def compose(self) -> ComposeResult:
        with Center():
            content = Container(classes="content")
            content.border_title = "Konto"

            with content:
                self.table = DataTable(show_header=False, cursor_type="row")
                self.table.can_focus = False
                self.table.add_columns("", "")

                self.refresh_table()

                yield self.table

                if self.account.type == AccountType.CHECKING:
                    yield Button(
                        "Sätt in",
                        id="account-dashboard-deposit-button",
                        classes="dashboard-button",
                        flat=True,
                        variant="primary",
                    )
                    yield Button(
                        "Överför till",
                        id="account-dashboard-transfer-to-button",
                        classes="dashboard-button",
                        flat=True,
                        variant="default",
                    )
                    yield Button(
                        "Överför från",
                        id="account-dashboard-transfer-from-button",
                        classes="dashboard-button margin-bottom",
                        flat=True,
                        variant="default",
                    )
                    yield Button(
                        "Tillbaka",
                        id="account-dashboard-back-button",
                        classes="dashboard-button",
                        flat=True,
                        variant="default",
                    )
                else:
                    with Horizontal():
                        with Vertical():
                            yield Button(
                                "Sätt in",
                                id="account-dashboard-deposit-button",
                                classes="dashboard-button-slim",
                                flat=True,
                                variant="primary",
                            )

                            yield Button(
                                "Ta ut",
                                id="account-dashboard-withdraw-button",
                                classes="dashboard-button-slim margin-bottom",
                                flat=True,
                                variant="error",
                            )
                            yield Button(
                                "Tillbaka",
                                id="account-dashboard-back-button",
                                classes="dashboard-button-slim",
                                flat=True,
                                variant="default",
                            )
                        with Vertical(classes="margin-left"):
                            yield Button(
                                "Överför till",
                                id="account-dashboard-transfer-to-button",
                                classes="dashboard-button-slim",
                                flat=True,
                                variant="default",
                            )
                            yield Button(
                                "Överför från",
                                id="account-dashboard-transfer-from-button",
                                classes="dashboard-button-slim margin-bottom",
                                flat=True,
                                variant="default",
                            )
                            yield Button(
                                "Ta bort",
                                id="account-dashboard-delete-button",
                                classes="dashboard-button-slim",
                                flat=True,
                                variant="error",
                            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "account-dashboard-back-button":
                self.app.pop_screen()

            case "account-dashboard-delete-button":
                if not self.app.bank.delete_account(self.account.number):
                    self.notify(
                        "Töm kontot innan du stänger det",
                        severity="error",
                    )
                else:
                    self.notify(
                        f"Kontot '{self.account.name}' togs bort",
                        severity="information",
                    )
                    self.app.pop_screen()

            case "account-dashboard-deposit-button":
                self.app.push_screen(
                    TransactionScreen(TransactionType.DEPOSIT, deposit_to=self.account)
                )

            case "account-dashboard-withdraw-button":
                self.app.push_screen(
                    TransactionScreen(
                        TransactionType.WITHDRAW, withdraw_from=self.account
                    )
                )

            case "account-dashboard-transfer-to-button":
                self.app.push_screen(
                    TransactionScreen(
                        TransactionType.TRANSFER, transfer_to=self.account
                    )
                )

            case "account-dashboard-transfer-from-button":
                self.app.push_screen(
                    TransactionScreen(
                        TransactionType.TRANSFER, transfer_from=self.account
                    )
                )

    def refresh_table(self):
        self.table.clear()

        self.table.add_rows(
            [
                ("Kontonamn", self.account.name),
                ("Saldo", f"{self.account.balance:.2f} kr"),
                ("Kontotyp", self.account.type.value),
                ("Kontonummer", f"{self.account.number:010}"),
            ]
        )

        match self.account.type:
            case AccountType.SAVINGS:
                self.table.add_rows(
                    [("Ränta", f"{self.account.fields['interest']:.1%}")]
                )

            case AccountType.ISK:
                self.table.add_rows(
                    [
                        (
                            "Årlig avkastning",
                            f"{self.account.fields['return_rate']:.1%}",
                        ),
                        (
                            "Schablonskatt",
                            f"{self.account.fields['standardized_tax']:.1%}",
                        ),
                    ]
                )

            case AccountType.AF:
                self.table.add_rows(
                    [
                        (
                            "Årlig avkastning",
                            f"{self.account.fields['return_rate']:.1%}",
                        ),
                        (
                            "Kapitalvinstskatt",
                            f"{self.account.fields['capital_gains_tax']:.1%}",
                        ),
                    ]
                )
