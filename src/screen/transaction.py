from enum import Enum, auto
from textual.app import ComposeResult
from textual.widgets import Button, Input, Select, Label, Checkbox
from textual.containers import Center, Container, Horizontal
from textual.screen import Screen
from typing import Any

from bank import Account, AccountType


class TransactionType(Enum):
    DEPOSIT = auto()
    WITHDRAW = auto()
    TRANSFER = auto()


class TransactionScreen(Screen[Any]):
    def __init__(
        self,
        type: TransactionType,
        deposit_to: Account = None,
        withdraw_from: Account = None,
        transfer_from: Account = None,
        transfer_to: Account = None,
    ):
        super().__init__()
        self.type = type

        self.deposit_to = deposit_to

        self.withdraw_from = withdraw_from

        self.transfer_from = transfer_from
        self.transfer_to = transfer_to

    def compose(self) -> ComposeResult:
        with Center():
            content = Container(classes="content")

            match self.type:
                case TransactionType.DEPOSIT:
                    content.border_title = "Sätt in"
                case TransactionType.WITHDRAW:
                    content.border_title = "Ta ut"
                case TransactionType.TRANSFER:
                    content.border_title = "Överför"

            with content:
                match self.type:
                    case TransactionType.DEPOSIT:
                        self.to_select = Select(
                            [
                                (
                                    f"{account.name} - {account.type.value} ({account.balance:.2f} kr)",
                                    account,
                                )
                                for account in self.app.bank.accounts.values()
                            ],
                            prompt="Välj...",
                            id="transaction-deposit-select",
                            compact=True,
                        )
                        self.to_select.border_title = "Konto"
                        yield self.to_select

                    case TransactionType.WITHDRAW:
                        self.from_select = Select(
                            [
                                (
                                    f"{account.name} - {account.type.value} ({account.balance:.2f} kr)",
                                    account,
                                )
                                for account in self.app.bank.accounts.values()
                            ],
                            prompt="Välj...",
                            id="transaction-withdraw-select",
                            compact=True,
                        )
                        self.from_select.border_title = "Konto"
                        yield self.from_select

                    case TransactionType.TRANSFER:
                        self.from_select = Select(
                            [
                                (
                                    f"{account.name} - {account.type.value} ({account.balance:.2f} kr)",
                                    account,
                                )
                                for account in self.app.bank.accounts.values()
                            ],
                            prompt="Välj...",
                            id="transaction-transfer-from-select",
                            compact=True,
                        )
                        self.from_select.border_title = "Från"
                        yield self.from_select

                        self.to_select = Select(
                            [
                                (
                                    f"{account.name} - {account.type.value} ({account.balance:.2f} kr)",
                                    account,
                                )
                                for account in self.app.bank.accounts.values()
                            ],
                            prompt="Välj...",
                            id="transaction-transfer-to-select",
                            compact=True,
                        )
                        self.to_select.border_title = "Till"
                        yield self.to_select

                with Container(classes="margin-top-bottom"):
                    self.amount = Input(placeholder="Belopp (kr)...")
                    self.amount.border_title = "Belopp kr"
                    yield self.amount

                    match self.type:
                        case TransactionType.WITHDRAW:
                            yield Checkbox(
                                "Ta ut hela tillgängliga saldot",
                                id="transaction-withdraw-checkbox",
                            )

                        case TransactionType.TRANSFER:
                            yield Checkbox(
                                "Överför hela tillgängliga saldot",
                                id="transaction-transfer-checkbox",
                            )

                with Horizontal():
                    yield Button(
                        "Avbryt",
                        id="transaction-cancel-button",
                        variant="error",
                        flat=True,
                    )
                    yield Button(
                        "Bekräfta",
                        id="transaction-confirm-button",
                        classes="margin-left",
                        variant="primary",
                        flat=True,
                    )

    def on_mount(self):
        match self.type:
            case TransactionType.DEPOSIT:
                if self.deposit_to:
                    self.to_select.value = self.deposit_to
                    self.to_select.disabled = True

            case TransactionType.WITHDRAW:
                if self.withdraw_from:
                    self.from_select.value = self.withdraw_from
                    self.from_select.disabled = True

            case TransactionType.TRANSFER:
                if self.transfer_from:
                    self.from_select.value = self.transfer_from
                    self.from_select.disabled = True

                if self.transfer_to:
                    self.to_select.value = self.transfer_to
                    self.to_select.disabled = True

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        self.amount.disabled = event.value

    @staticmethod
    def validate_amount_input(input: str) -> float | None:
        try:
            amount = float(input)
            if amount <= 0:
                return None
            return amount
        except ValueError:
            return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "transaction-cancel-button":
                self.app.pop_screen()

            case "transaction-confirm-button":
                amount = TransactionScreen.validate_amount_input(self.amount.value)

                match self.type:
                    case TransactionType.DEPOSIT:
                        account = self.query_one(
                            "#transaction-deposit-select", Select
                        ).value

                        if account == Select.BLANK:
                            self.notify("Välj konto", severity="warning")
                            return

                        if not amount:
                            self.notify("Ange ett giltigt belopp", severity="warning")
                            return

                        account.deposit(amount)

                        self.notify(
                            f'{amount:.2f} kr har satts in på "{account.name}"',
                            severity="information",
                        )
                        self.app.pop_screen()

                    case TransactionType.WITHDRAW:
                        account = self.query_one(
                            "#transaction-withdraw-select", Select
                        ).value

                        if account == Select.BLANK:
                            self.notify("Välj konto", severity="warning")
                            return

                        if account.type == AccountType.CHECKING:
                            self.notify(
                                "Uttag från ditt användarkonto är inte tillåtet. Överför istället",
                                severity="warning",
                            )
                            return

                        # hitta användarkonto
                        checking_account = next(
                            (
                                account
                                for account in self.app.bank.accounts.values()
                                if account.type == AccountType.CHECKING
                            ),
                            None,
                        )

                        if not checking_account:
                            self.notify(
                                "Inget användarkonto hittades. Uttaget avbröts",
                                severity="error",
                            )
                            return

                        # kolla om hela saldot ska tas ut
                        if self.query_one(
                            "#transaction-withdraw-checkbox", Checkbox
                        ).value:
                            amount = account.balance
                        elif not amount:
                            self.notify("Ange ett giltigt belopp", severity="warning")
                            return

                        if amount == 0.0:
                            self.notify("Inget att ta ut", severity="warning")
                            return

                        if not account.withdraw(amount):
                            self.notify("Otillräckligt saldo", severity="warning")
                            return

                        checking_account.deposit(amount)

                        self.notify(
                            f'{amount:.2f} kr har tagits ut från "{account.name}" och satts in på "{checking_account.name}"',
                            severity="information",
                        )
                        self.app.pop_screen()

                    case TransactionType.TRANSFER:
                        account_from = self.query_one(
                            "#transaction-transfer-from-select", Select
                        ).value

                        if account_from == Select.BLANK:
                            self.notify("Välj konto", severity="warning")
                            return

                        account_to = self.query_one(
                            "#transaction-transfer-to-select", Select
                        ).value

                        if account_to == Select.BLANK:
                            self.notify("Välj konto", severity="warning")
                            return

                        if account_from == account_to:
                            self.notify("Du kan inte överföra pengar till samma konto")
                            return

                        # kolla om hela saldot ska överföras
                        if self.query_one(
                            "#transaction-transfer-checkbox", Checkbox
                        ).value:
                            amount = account_from.balance
                        elif not amount:
                            self.notify("Ange ett giltigt belopp", severity="warning")
                            return

                        if amount == 0.0:
                            self.notify("Inget att överföra", severity="warning")
                            return

                        if not account_from.withdraw(amount):
                            self.notify("Otillräckligt saldo", severity="warning")
                            return

                        account_to.deposit(amount)

                        self.notify(
                            f'{amount:.2f} kr har överförts från "{account_from.name}" till "{account_to.name}"',
                            severity="information",
                        )
                        self.app.pop_screen()
