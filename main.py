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


def get_payment(invoice_date: datetime.date, payment_currencies):
    """
    Pobiera dane płatności od użytkownika.

    :param invoice_date: data faktury.
    :param payment_currencies: możliwe waluty.
    :return: słownik z datą, kwotą i walutą.
    """
    print("Wprowadź dane płatności: ")
    while True:
        payment_date = get_date()
        if payment_date < invoice_date:
            print("Data nie może być wcześniejsza niż data faktury")
        else:
            break
    payment_value, payment_currency = get_amount(payment_currencies)
    payment_data = {'date': payment_date,
                    'value': payment_value,
                    'currency': payment_currency}
    return payment_data


def another_payment() -> bool:
    """Pobiera informację od użytkownika, czy chce wprowadzić
        kolejną płatność"""
    while True:
        user_input = input("Czy chcesz wprowadzić kolejną płatność? (T/N): ").upper()
        if user_input == 'T':
            return True
        elif user_input == 'N':
            return False
        else:
            print("Nieprawidłowa wartość, wybierz T lub N")


def main():
    currencies = ('PLN', 'EUR', 'USD', 'GBP')

    print("Wprowadź dane faktury: ")
    invoice_date = get_date()
    invoice_value, invoice_currency = get_amount(currencies)
    print(f"Faktura: {invoice_date}, {invoice_value} {invoice_currency}")

    payment_num = 0

    if invoice_currency == 'PLN':
        # Jeśli faktura została wystawiona w PLN, to płatność może być w dowolnej walucie.
        payment_currencies = currencies
        while True:
            payment_num += 1
            payment_data = get_payment(invoice_date, payment_currencies)

            print(f"Płatność nr{payment_num}: {payment_data['date']}, {payment_data['value']} "
                  f"{payment_data['currency']}")

            if not another_payment():
                break
    else:
        # Jeśli faktura została wystawiona w walucie obcej, to płatność może być
        # w tej samej walucie lub w PLN.
        payment_currencies = ('PLN', invoice_currency)

        while True:
            payment_num += 1
            payment_data = get_payment(invoice_date, payment_currencies)

            print(f"Płatność nr{payment_num}: {payment_data['date']}, {payment_data['value']} "
                  f"{payment_data['currency']}")

            if not another_payment():
                break


if __name__ == "__main__":
    main()
