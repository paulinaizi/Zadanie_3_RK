import datetime


def get_amount(available_currencies) -> tuple[float, str]:
    """
    Pobiera kwotę wraz z walutą od użytkownika
    i sprawdza poprawność danych, zwraca te wartości w tupli.

    :param available_currencies: tupla lub lista z dostępnymi walutami.
    :return: kwota i waluta.
    """
    while True:
        try:
            amount = float(input("Wprowadź kwotę: "))
            if amount < 0:
                print("Wprowadzona kwota jest ujemna")
            else:
                break
        except ValueError:
            print("Wartość niepoprawna")

    while True:
        print(f"Dostępne waluty: {available_currencies}")
        currency = input("Wprowadź walutę: ").upper()
        if currency in available_currencies:
            return amount, currency
        else:
            print("Niepoprawna waluta")


def get_date() -> datetime.date:
    """
    Pobiera datę od użytkownika i sprawdza jej poprawność.

    Archiwalne dane dla kursów walut na NBP Web API dostępne są
    od 2 stycznia 2002, funkcja nie przyjmuje dat starszych,
    ani dat z przyszłości.
    """
    min_date = datetime.date(2002, 1, 2)
    max_date = datetime.date.today()
    while True:
        user_date = input("Wprowadź datę RRRR-MM-DD: ")
        try:
            date = datetime.datetime.strptime(user_date, "%Y-%m-%d").date()
        except ValueError:
            print("Niepoprawny format daty")
        else:
            if date < min_date:
                print(f"Program nie obsługuje dat starszych niż {min_date}")
            elif date > max_date:
                print("Data nie może być z przyszłości")
            else:
                return date


def main():
    currencies = ('PLN', 'EUR', 'USD', 'GBP')

    print("Wprowadź dane faktury: ")
    invoice_date = get_date()
    invoice_value, invoice_currency = get_amount(currencies)
    print(f"Faktura: {invoice_date}, {invoice_value} {invoice_currency}")


if __name__ == "__main__":
    main()
