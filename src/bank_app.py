from textual.app import App
from bank import Account, Bank
from screen.greeting import GreetingScreen
from theme import theme


class BankApp(App[None]):
    CSS_PATH = "style.tcss"

    def __init__(self):
        super().__init__()

        self.bank = Bank()

        # Skapa exempelkonton

        checking = Account.new_checking("Användarkonto")
        checking.balance = 6000
        self.bank.register_account(checking)

        savings = Account.new_savings("Sparkonto", 0.02)
        savings.balance = 80000
        self.bank.register_account(savings)

        isk = Account.new_isk("Mina aktier", 0.06, 0.0125)
        isk.balance = 130000
        self.bank.register_account(isk)

        af = Account.new_af("Nordea Stratega 50", 0.05, 0.3)
        af.balance = 40614.4
        self.bank.register_account(af)

    def on_mount(self):
        self.register_theme(theme)
        self.theme = "custom"

        self.push_screen(GreetingScreen())
