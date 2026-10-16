"""Klient NBP Web API: pobieranie kursów średnich (tabela A) i zapis warstwy raw.
 
Moduł nie parsuje i nie czyści danych. Jego jedyne zadanie: pobrać odpowiedź
NBP i zapisać ją na dysk bajt w bajt (kopia audytowa). Parsowanie = dzień 3.
"""
 
from __future__ import annotations  # list[Path] w adnotacjach działa też na starszym Pythonie
 
from datetime import date, timedelta  # date = sama data bez godziny; timedelta = różnica dat
from pathlib import Path  # ścieżki niezależne od systemu (Linux / Windows)
from typing import Iterator  # typ zwracany przez generator (funkcję z yield)
 
import requests  # biblioteka HTTP: timeouty, statusy, nagłówki
 
# --- Stałe kontraktu API (jedno miejsce zamiast „magicznych liczb”) ---------
BASE_URL = "https://api.nbp.pl/api/exchangerates/rates/a"  # /a = tabela A (kursy średnie)
MAX_RANGE_DAYS = 93  # dokumentowany limit NBP: jedno zapytanie ≤ 93 dni
REQUEST_TIMEOUT_SECONDS = 30  # po tylu sekundach bez odpowiedzi przerywamy zamiast wisieć

def iter_date_ranges(
    start_date: date,
    end_date: date,
    max_days: int = MAX_RANGE_DAYS,
) -> Iterator[tuple[date, date]]:
    """Dzieli [start_date, end_date] (obie granice włącznie) na ciągłe fragmenty ≤ max_days."""
    if end_date < start_date:  # odwrócony zakres = błąd wywołującego
        raise ValueError("end_date must not be earlier than start_date")
    current_start = start_date
    while current_start <= end_date:
        # max_days - 1, bo liczymy obie granice: 1 sty + 92 dni = 93 dni kalendarzowe
        current_end = min(current_start + timedelta(days=max_days - 1), end_date)
        yield current_start, current_end  # generator: oddaje jeden fragment naraz
        current_start = current_end + timedelta(days=1)  # kolejny fragment: dzień później
