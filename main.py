import datetime
import json
import urllib.request
from urllib.error import HTTPError


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


def find_exchange_rate(currency: str, date: datetime.date) -> tuple[datetime.date, float, str]:
    """
    Pobiera średni kurs podanej waluty z NBP Web API dla podanej daty.

    Jeśli na stronie brakuje danych dla podanej daty, szuka danych
    z dni poprzednich.

    :param currency: kod waluty.
    :param date: data.
    :return: zwraca kurs, datę, dla której znaleziono dane, walutę.
    """
    while True:
        try:
            filename = 'http://api.nbp.pl/api/exchangerates/rates/a/' + currency + '/' + str(date) + '/?format=json'
            with urllib.request.urlopen(filename) as url:
                data = json.load(url)
                break
        except urllib.error.HTTPError as err:
            if err.getcode() == 404:
                date -= datetime.timedelta(days=1)
            elif err.getcode() == 400:
                raise ValueError('Nieprawidłowy link')
            else:
                raise SystemExit(err)
    mid_exchange_rate = data['rates'][0]['mid']
    return date, mid_exchange_rate, currency


def remaining_payment_info(remaining_payment: float, invoice_currency: str) -> bool:
    """
    Wyświetla informacje o stanie płatności.

    :param remaining_payment: stan płatności.
    :param invoice_currency: waluta faktury.
    :return: zwraca True, jeśli faktura została spłacona w całości lub z nadpłatą,
    w pozostałym przypadku zwraca False.
    """
    if remaining_payment < 0:
        print(f"Nadpłata: {abs(remaining_payment):.2f} {invoice_currency}")
        return True
    elif remaining_payment > 0:
        print(f"Brakuje do spłaty: {remaining_payment:.2f} {invoice_currency}")
        return False
    else:
        print("Kwota została w pełni spłacona")
        return True


def calculate_exchange_difference(value: float, exchange_rate_invoice: float, exchange_rate_payment: float) -> float:
    """
    Oblicza różnicę kursową.

    :param value: kwota
    :param exchange_rate_invoice: kurs zastosowany dla faktury.
    :param exchange_rate_payment: kurs zastosowany dla płatności.
    :return: kwota przemnożona przez różnicę zastosowanych kursów.
    """
    return value * (exchange_rate_payment - exchange_rate_invoice)


def main():
    currencies = ('PLN', 'EUR', 'USD', 'GBP')

    print("Wprowadź dane faktury: ")
    invoice_date = get_date()
    invoice_value, invoice_currency = get_amount(currencies)
    print(f"Faktura: {invoice_date}, {invoice_value} {invoice_currency}")

    remaining_payment = invoice_value
    payment_num = 0

    if invoice_currency == 'PLN':
        # Jeśli faktura została wystawiona w PLN, to płatność może być w dowolnej walucie.
        payment_currencies = currencies
        while True:
            payment_num += 1
            payment_data = get_payment(invoice_date, payment_currencies)
            print(f"Płatność nr{payment_num}: {payment_data['date']}, {payment_data['value']} "
                  f"{payment_data['currency']}")

            if payment_data['currency'] == invoice_currency:
                remaining_payment -= payment_data['value']
            else:
                payment_exchange_data = find_exchange_rate(payment_data['currency'], payment_data['date'])
                payment_exchange_rate = payment_exchange_data[1]
                exchanged_value = payment_data['value'] * payment_exchange_rate
                remaining_payment -= exchanged_value
                print(f"Kwota przeliczona: {exchanged_value:.2f} {invoice_currency}")
                print(f"Zastosowano kurs: {payment_exchange_data[0]}, {payment_exchange_data[1]} "
                      f"{payment_exchange_data[2]}")

            if remaining_payment_info(remaining_payment, invoice_currency):
                break

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

            # Różnice kursowe występują, gdy zarówno faktura, jak i płatność
            # jest w walucie obcej.
            if payment_data['currency'] == invoice_currency:
                invoice_exchange_data = find_exchange_rate(invoice_currency, invoice_date)
                print(f"Kurs z faktury: {invoice_exchange_data[0]}, {invoice_exchange_data[1]} {invoice_currency}")
                payment_exchange_data = find_exchange_rate(payment_data['currency'], payment_data['date'])
                print(f"Kurs z płatności: {payment_exchange_data[0]}, {payment_exchange_data[1]} {payment_data['currency']}")
                exchange_difference = calculate_exchange_difference(payment_data['value'], invoice_exchange_data[1], payment_exchange_data[1])
                print(f"Różnice kursowe: {exchange_difference:.2f}")
                remaining_payment -= payment_data['value']
            else:
                payment_exchange_data = find_exchange_rate(invoice_currency, payment_data['date'])
                payment_exchange_rate = payment_exchange_data[1]
                exchanged_value = payment_data['value'] / payment_exchange_rate
                remaining_payment -= exchanged_value
                print(f"Kwota przeliczona: {exchanged_value:.2f} {invoice_currency}")
                print(f"Zastosowano kurs: {payment_exchange_data[0]}, {payment_exchange_data[1]} "
                      f"{payment_exchange_data[2]}")

            if remaining_payment_info(remaining_payment, invoice_currency):
                break

            if not another_payment():
                break


if __name__ == "__main__":
    main()
