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


def fetch_currency_chunk(code: str, start_date: date, end_date: date) -> bytes:
    """Pobiera jeden fragment (≤ 93 dni) i zwraca SUROWE bajty odpowiedzi."""
    # np. https://api.nbp.pl/api/exchangerates/rates/a/eur/2025-01-01/2025-01-31/
    url = f"{BASE_URL}/{code.lower()}/{start_date.isoformat()}/{end_date.isoformat()}/"
    response = requests.get(
        url,
        params={"format": "json"},  # dopisuje ?format=json — jak w adresie z dokumentacji
        headers={"Accept": "application/json"},  # równoważna prośba o JSON (bez obu → XML)
        timeout=REQUEST_TIMEOUT_SECONDS,  # bez timeoutu requests może czekać bez końca
    )
    response.raise_for_status()  # status 4xx/5xx → wyjątek requests.HTTPError
    return response.content  # bytes, NIE .json(): nic nie przepisujemy przed zapisem


def save_raw_response(
    content: bytes,
    output_dir: Path,
    code: str,
    start_date: date,
    end_date: date,
) -> Path:
    """Zapisuje bajty do pliku CODE_start_end.json i zwraca ścieżkę."""
    output_dir.mkdir(parents=True, exist_ok=True)  # utwórz, jeśli brak; nie krzycz, jeśli jest
    path = output_dir / f"{code.upper()}_{start_date}_{end_date}.json"  # str(date) = 'YYYY-MM-DD'
    path.write_bytes(content)  # zapis binarny: zero dekodowania, zero zmiany końców linii
    return path

def download_currency_history(
    code: str,
    start_date: date,
    end_date: date,
    raw_root: Path = Path("data/raw/nbp"),
) -> list[Path]:
    """Pobiera cały zakres w fragmentach i zapisuje każdy do raw_root/CODE/."""
    saved: list[Path] = []
    for chunk_start, chunk_end in iter_date_ranges(start_date, end_date):
        content = fetch_currency_chunk(code, chunk_start, chunk_end)
        saved.append(
            save_raw_response(content, raw_root / code.upper(), code, chunk_start, chunk_end)
        )
    return saved

def safe_download(
    code: str,
    start_date: date,
    end_date: date,
    raw_root: Path = Path("data/raw/nbp"),
) -> list[Path]:
    """Jak download_currency_history, ale błędy sieci/API dostają kontekst waluty."""
    try:
        return download_currency_history(code, start_date, end_date, raw_root=raw_root)
    except requests.HTTPError as exc:  # serwer odpowiedział statusem błędu (400, 404…)
        raise RuntimeError(f"NBP HTTP error for {code}") from exc  # zachowaj przyczynę
    except requests.RequestException as exc:  # timeout, brak DNS, zerwane połączenie…
        raise RuntimeError(f"Network error for {code}") from exc
