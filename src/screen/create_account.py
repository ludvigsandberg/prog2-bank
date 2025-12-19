from textual import on
from textual.app import ComposeResult
from textual.widgets import Button, Input, Select
from textual.containers import Center, Container, Horizontal
from textual.screen import Screen
from typing import Any

from bank import Account, AccountType


class CreateAccountScreen(Screen[Any]):
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        with Center():
            content = Container(classes="content")
            content.border_title = "Skapa konto"

            with content:
                name_input = Input(
                    placeholder="Namn...", id="create-account-name-input"
                )
                name_input.border_title = "Kontonamn"
                yield name_input

                type_select = Select(
                    [
                        (AccountType.SAVINGS.value, AccountType.SAVINGS),
                        (AccountType.ISK.value, AccountType.ISK),
                        (AccountType.AF.value, AccountType.AF),
                    ],
                    prompt="Välj...",
                    id="create-account-account-type-select",
                    compact=True,
                )
                type_select.border_title = "Kontotyp"
                yield type_select

                self.container = Container(
                    id="create-account-dynamic-content-container"
                )
                yield self.container

                with Horizontal():
                    yield Button(
                        "Avbryt",
                        id="create-account-cancel-button",
                        variant="default",
                        flat=True,
                    )
                    yield Button(
                        "Skapa",
                        id="create-account-create-button",
                        classes="margin-left",
                        variant="primary",
                        flat=True,
                    )

    @on(Select.Changed)
    def select_changed(self, event: Select.Changed) -> None:
        self.container.remove_children()

        match event.value:
            case AccountType.SAVINGS:
                interest = Input(
                    placeholder="Ränta (%)...",
                    value="2",
                    id="create-account-dynamic-container-savings-interest-input",
                )
                interest.border_title = "Ränta %"

                self.container.mount(interest)
            case AccountType.ISK:
                return_rate = Input(
                    placeholder="Avkastning (%)...",
                    id="create-account-dynamic-container-isk-return-rate-input",
                )
                return_rate.border_title = "Årlig avkastning %"

                tax = Input(
                    placeholder="Schablonskatt (%)...",
                    value="1.25",
                    id="create-account-dynamic-container-isk-tax-input",
                )
                tax.border_title = "Schablonskatt %"

                self.container.mount(return_rate, tax)
            case AccountType.AF:
                return_rate = Input(
                    placeholder="Avkastning (%)...",
                    id="create-account-dynamic-container-af-return-rate-input",
                )
                return_rate.border_title = "Årlig avkastning %"

                tax = Input(
                    placeholder="Vinstskatt (%)...",
                    value="30",
                    id="create-account-dynamic-container-af-tax-input",
                )
                tax.border_title = "Kapitalvinstskatt %"

                self.container.mount(return_rate, tax)

    @staticmethod
    def validate_percentage_input(input: str) -> float | None:
        try:
            percentage = float(input)
            if percentage < 0.0:
                return None
            return percentage
        except ValueError:
            return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "create-account-cancel-button":
                self.app.pop_screen()

            case "create-account-create-button":
                name: str = self.query_one("#create-account-name-input", Input).value

                if not name:
                    self.notify("Ange ett kontonamn", severity="warning")
                    return

                type: AccountType = self.query_one(
                    "#create-account-account-type-select", Select
                ).value

                match type:
                    case Select.BLANK:
                        self.notify("Välj kontotyp", severity="warning")
                        return

                    case AccountType.CHECKING:
                        self.app.bank.register_account(Account.new_checking(name))

                    case AccountType.SAVINGS:
                        interest = CreateAccountScreen.validate_percentage_input(
                            self.query_one(
                                "#create-account-dynamic-container-savings-interest-input",
                                Input,
                            ).value
                        )

                        if not interest:
                            self.notify("Ogiltig ränta", severity="warning")
                            return

                        self.app.bank.register_account(
                            Account.new_savings(name, interest / 100.0)
                        )

                    case AccountType.ISK:
                        return_rate = CreateAccountScreen.validate_percentage_input(
                            self.query_one(
                                "#create-account-dynamic-container-isk-return-rate-input",
                                Input,
                            ).value
                        )

                        if not return_rate:
                            self.notify("Ogiltig avkastning", severity="warning")
                            return

                        tax = CreateAccountScreen.validate_percentage_input(
                            self.query_one(
                                "#create-account-dynamic-container-isk-tax-input",
                                Input,
                            ).value
                        )

                        if not tax:
                            self.notify("Ogiltig schablonskatt", severity="warning")
                            return

                        self.app.bank.register_account(
                            Account.new_isk(name, return_rate / 100.0, tax / 100.0)
                        )

                    case AccountType.AF:
                        return_rate = CreateAccountScreen.validate_percentage_input(
                            self.query_one(
                                "#create-account-dynamic-container-af-return-rate-input",
                                Input,
                            ).value
                        )

                        if not return_rate:
                            self.notify("Ogiltig avkastning", severity="warning")
                            return

                        tax = CreateAccountScreen.validate_percentage_input(
                            self.query_one(
                                "#create-account-dynamic-container-af-tax-input",
                                Input,
                            ).value
                        )

                        if not tax:
                            self.notify("Ogiltig vinstskatt", severity="warning")
                            return

                        self.app.bank.register_account(
                            Account.new_af(name, return_rate / 100.0, tax / 100.0)
                        )

                # återgå till dashboard
                self.app.pop_screen()
