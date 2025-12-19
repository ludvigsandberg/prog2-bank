from textual.app import ComposeResult
from textual.widgets import Button, Input
from textual.containers import Center, Container, Horizontal
from textual.screen import Screen
from typing import Any


class SimulateInterestScreen(Screen[Any]):
    def __init__(self):
        super().__init__()

    def compose(self) -> ComposeResult:
        with Center():
            content = Container(classes="content")
            content.border_title = "Simulera ränteutbetalning"

            with content:
                num_years = Input(
                    placeholder="År...",
                    id="simulate-interest-years-input",
                    classes="margin-bottom",
                )
                num_years.border_title = "Antal år"
                yield num_years

                with Horizontal():
                    yield Button(
                        "Avbryt",
                        id="simulate-interest-cancel-button",
                        variant="default",
                        flat=True,
                    )
                    yield Button(
                        "Simulera ränteutbetalning",
                        id="simulate-interest-create-button",
                        classes="margin-left",
                        variant="primary",
                        flat=True,
                    )

    @staticmethod
    def validate_year_input(input: str) -> int | None:
        try:
            num_years = int(input)
            if num_years <= 0:
                return None
            return num_years
        except ValueError:
            return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "simulate-interest-cancel-button":
                self.app.pop_screen()

            case "simulate-interest-create-button":
                num_years = SimulateInterestScreen.validate_year_input(
                    self.query_one("#simulate-interest-years-input").value
                )

                if not num_years:
                    self.notify(
                        "Ange ett positivt heltal",
                        severity="warning",
                    )
                    return

                for _ in range(num_years):
                    self.app.bank.apply_yearly_update()

                self.notify(
                    f"Simulering genomförd för {num_years} år",
                    severity="information",
                )

                self.app.pop_screen()
