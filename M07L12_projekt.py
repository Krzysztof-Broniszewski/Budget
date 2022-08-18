# Napisz program, który ułatwi milionom Polaków śledzenie własnych wydatków oraz ich analizę. Program pozwala na łatwe dodawanie nowych wydatków i generowanie raportów. Aplikacja działa także pomiędzy uruchomieniami, przechowując wszystkie dane w pliku. Każdy wydatek ma id, opis oraz wielkość kwoty.

# 1. Program posiada podkomendy add, report, export-python oraz import-csv. 

# 2. Podkomenda add pozwala na dodanie nowego wydatku. Należy wówczas podać jako kolejne argumenty wiersza poleceń wielkość wydatku (jako int) oraz jego opis (w cudzysłowach). Na przykład:
# $ python budget.py add 100 "stówa na zakupy". 
# Jako id wybierz pierwszy wolny id - np. jeśli masz już wydatki z id = 1, 2, 4, 5, wówczas wybierz id = 3.

# 3. Podkomenda report wyświetla wszystkie wydatki w tabeli. W tabeli znajduje się także kolumna "big?", w której znajduje się ptaszek, gdy wydatek jest duży, tzn. co najmniej 1000. Dodatkowo, na samym końcu wyświetlona jest suma wszystkich wydatów.

# 4. Podkomenda export-python wyświetla listę wszystkich wydatków jako obiekt (hint: zaimplementuj poprawnie metodę __repr__ w klasie reprezentującej pojedynczy wydatek).

# 5. Podkomenda import-csv importuję listę wydatków z pliku CSV.

# 6. Program przechowuje pomiędzy uruchomieniami bazę wszystkich wydatków w pliku budget.db. Zapisuj i wczytuj stan używając modułu pickle. Jeżeli plik nie istnieje, to automatycznie stwórz nową, pustą bazę. Zauważ, że nie potrzebujemy podpolecenia init.

# 7. Wielkość wydatku musi być dodatnią liczbą. Gdzie umieścisz kod sprawdzający, czy jest to spełnione? W jaki sposób zgłosisz, że warunek nie jest spełniony?

import csv
from dataclasses import dataclass
import pickle
import sys
from os import path

import click

"""
USAGE:
$ python M07\M07L12_projekt.py report (show list - use it every time after modification)

$ python M07\M07L12_projekt.py init --example ( make a basic list with 3 positions)

$ python M07\M07L12_projekt.py add <amount> <description>
    $ python M07\M07L12_projekt.py add 2000 'Pieniadze za las'

$ python M07\M07L12_projekt.py import-csv <path to csv file>
    $ python M07\M07L12_projekt.py import-csv M07\expenses.csv

$ python M07\M07L12_projekt.py export-python (show a list of class positions as json)
"""

DB_FILENAME = 'budget.db'

@dataclass
class Expend:
    """
    Making a new object from Expend object with values amount and desc
    """
    amount: float
    desc: str
    

    def __repr__(self):
        return f'Expend(amount={self.amount!r}, desc={self.desc!r})'

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("Amount must be a positive number !")

counter = 0
def find_new_id(counter: int) -> int:
    """
    Generate next free id to show on list of positions
    """
    counter += 1
    return counter


def exist_or_no(filename: str) -> bool:
    """
    Checking and return True when file exists in directory
    """
    if path.exists(filename):
        exist = True
    else:
        exist = False
    return exist


def save_db(filename: str, positions: list[Expend], overwrite: bool=True) -> None:
    """
    Saving the amount and description to file
    """
    if overwrite:
        mode = 'wb'
    else:
        mode = 'xb'
    try:
        with open(filename, mode) as stream:
            pickle.dump(positions, stream)
    except FileExistsError:
        print('This base already exists !')


def init_db(example: bool=True) -> None:
    """
    Making the basic 3 positions on list when params is --example or empty list
    """
    if exist_or_no(DB_FILENAME) == False:
        positions: list[Expend]
        if example:
            positions = [
                Expend(amount=1000, desc='Czynsz'),
                Expend(amount=300, desc='Koty'),
                Expend(amount=2100, desc='Pieniądze za las'),
            ]
        else:
            positions = []
        return positions


def read_db_or_init() -> list[Expend]:
    """
    Reading the data base file and creating positions list from object
    """
    try:
        with open(DB_FILENAME, 'rb') as stream:
            positions = pickle.load(stream)
    except FileNotFoundError:
        positions = []
    return positions


def print_positions(positions: list[Expend]) -> None:
    """
    Printing the basic positions table or empty table when file does not exists
    Show summary of expanditions
    """
    print('----------------------------------------------')
    print(f'  ID | EXPANDITION          | AMOUNT  | BIG')
    print('----------------------------------------------')
    index = 1
    total = 0
    for position in positions:
        if float(position.amount) >= 1000:
            big = '(!)'
        else:
            big = ''
        print(f'{index: >4} | {position.desc: <20} | {float(position.amount): >7.2f} | {big: ^4}')
        index += 1
        total += float(position.amount)
    print('----------------------------------------------')
    print(f'       TOTAL                |{float(total): .2f} |')


def add_position(positions: list[Expend], amount: float,  expandition: str) -> list[Expend]:
    """
    Adding posiotion to list when user write amount and description
    """
    positions.append(Expend(
        amount=float(amount),
        desc=expandition.capitalize(),
    ))
    return positions


def import_from_csv(csv_filename: str) -> None:
    """
    Importing all positions of expandition from csv file and adding to file extension .db
    """
    positions = read_db_or_init()
    with open(csv_filename, encoding='utf-8') as stream: 
        reader = csv.DictReader(stream)
        for row in reader:
            add_position(positions, row['amount'], row['description'].capitalize())
        save_db(DB_FILENAME, positions)
        print("New file csv has been added:")


def export() -> None:
    """
    Exporting of list of objects from main class
    """
    positions = read_db_or_init()
    exp = []
    for position in positions:
        exp.append(repr(position))
    print(exp)


@click.group()
def cli():
    pass


@cli.command()
@click.option('--example', is_flag=True)
def init(example: bool) -> None:
    positions = init_db(example)
    save_db(DB_FILENAME, positions)


@cli.command()
def report() -> None:
    positions = read_db_or_init()
    print_positions(positions)


@cli.command()
def export_python() -> None:
    export()
    

@cli.command()
@click.argument('csv_filename')
def import_csv(csv_filename: str) -> None:
    import_from_csv(csv_filename)


@cli.command()
@click.argument('amount')
@click.argument('expandition')
def add(amount: float, expandition: str) -> None:
    positions = read_db_or_init()
    try:
        add_position(positions, amount, expandition)
    except ValueError as e:
        print(f'Błąd: {e.args[0]}')
        sys.exit(1)
    save_db(DB_FILENAME, positions)
    print("New position on list:")


if __name__ == "__main__":
    cli()
