from enum import Enum


# olika kontotyper behöver olika fält, programflöde bestäms av kontots "type"
class AccountType(Enum):
    CHECKING = "Användarkonto"
    SAVINGS = "Sparkonto"
    ISK = "Investeringssparkonto"
    AF = "Aktie- och fondkonto"


class Account:
    """
    här valde jag "data driven" över den klassiska
    "object oriented programming" genom att spara extra fält i en dict
    i ett riktigt program skulle någon form av databas passa bättre

    populärt i modern arkitektur (composition over inheritence)
    """

    fields: dict

    def __init__(self, name: str, type: AccountType, fields: dict = None):
        self.name = name
        self.type = type
        self.balance = 0.0
        self.fields = fields or {}

    # statiska fabriksmetoder
    # t.ex. Account.new_savings("Mitt sparkonto", 0.02)

    @staticmethod
    def new_checking(name: str):
        """Skapa ett användarkonto. Användarkonton har vanligtvis ingen ränta."""
        return Account(name, AccountType.CHECKING)

    @staticmethod
    def new_savings(name: str, interest: float):
        """Skapa ett sparkonto med fast årlig ränta."""
        return Account(name, AccountType.SAVINGS, {"interest": interest})

    @staticmethod
    def new_isk(name: str, return_rate: float, standardized_tax: float):
        """Skapa ett investeringssparkonto.

        Args:
            return_rate (float): Förenklad årlig avkastning. I verkligheten beror den på marknaden och värdeförändringar på aktier och fonder.
            standardized_tax (float): Årlig schablonskatt.
        """
        return Account(
            name,
            AccountType.ISK,
            {
                "return_rate": return_rate,
                "standardized_tax": standardized_tax,
                # startkapital och summan av årets transaktioner, används vid beräkning av schablonskatt
                "starting_balance": 0.0,
                "yearly_transactions": 0.0,
            },
        )

    @staticmethod
    def new_af(name: str, return_rate: float, tax_rate: float):
        """Skapa ett aktie- och fondkonto.

        Args:
            return_rate (float): Förenklad årlig avkastning. I verkligheten beror den på marknaden och värdeförändringar på aktier och fonder.
            tax_rate (float): Vinstskatt (runt 30%).
        """
        return Account(
            name,
            AccountType.AF,
            {
                "return_rate": return_rate,
                "capital_gains_tax": tax_rate,
                # håll koll på vinsten
                "capital_gains": 0.0,
            },
        )

    def withdraw(self, amount: float) -> bool:
        if amount > self.balance:
            return False

        match self.type:
            case AccountType.CHECKING:
                self.balance -= amount

            case AccountType.SAVINGS:
                self.balance -= amount

            case AccountType.ISK:
                self.fields["yearly_transactions"] -= amount
                self.balance -= amount

            case AccountType.AF:
                # beräkna andel av uttaget som är vinst
                capital_ratio = self.fields["capital_gains"] / self.balance
                capital_gains_withdrawn = amount * capital_ratio
                tax = capital_gains_withdrawn * self.fields["capital_gains_tax"]

                # dra saldo och skatt
                self.balance -= amount + tax
                self.fields["capital_gains"] -= capital_gains_withdrawn
        return True

    def deposit(self, amount):
        if self.type == AccountType.ISK:
            self.fields["yearly_transactions"] += amount

        self.balance += amount

    def apply_yearly_update(self):
        match self.type:
            case AccountType.SAVINGS:
                self.balance *= 1.0 + self.fields["interest"]

            case AccountType.ISK:
                self.balance *= 1.0 + self.fields["return_rate"]

                # schablonskatt

                capital_base = (
                    self.fields["starting_balance"] + self.balance
                ) / 2.0 + self.fields["yearly_transactions"]

                tax = capital_base * self.fields["standardized_tax"]

                self.balance -= tax

                # återställ inför nästa år
                self.fields["starting_balance"] = self.balance
                self.fields["yearly_transactions"] = 0.0

            case AccountType.AF:
                gains = self.balance * self.fields["return_rate"]
                self.balance += gains
                self.fields["capital_gains"] += gains


class Bank:
    def __init__(self):
        # key=kontonummer
        self.accounts: dict[int, Account] = {}
        self.account_number: int = 1

    def register_account(self, account: Account):
        account_number = self.account_number

        # öka kontonummer så att nästa konto får ett unikt nummer
        self.account_number += 1

        account.number = account_number
        self.accounts[account_number] = account

    def delete_account(self, account_number: int) -> bool:
        account = self.accounts.get(account_number)

        # kontot kan inte raderas om det finns pengar på det
        if account is None or account.balance > 0:
            return False

        del self.accounts[account_number]
        return True

    def apply_yearly_update(self):
        for account in self.accounts.values():
            account.apply_yearly_update()
