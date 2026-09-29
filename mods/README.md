# Mody NetCorp Tycoon

Ten folder zawiera mody do gry. Mody to pliki `.json` nadpisujące dane gry (balans, katalog serwerów, domeny, imiona).

## Jak stworzyć mod

Utwórz plik `.json` w tym folderze. Przykład:

```json
{
  "name": "Mój mod",
  "version": "1.0",
  "author": "Twój nick",
  "enabled": true,
  "description": "Co robi ten mod",
  "balance": {
    "MARKETING_COST_PER_NEW_CUSTOMER": 10.0,
    "FAILURE_BASE_DAILY": 0.01
  }
}
```

## Co można modyfikować

### `balance` — stałe balansu (z `data/balance.py`)
| Klucz | Opis | Domyślnie |
|-------|------|-----------|
| `FAILURE_BASE_DAILY` | Bazowa szansa awarii/serwer/dzień | 0.02 |
| `MARKETING_COST_PER_NEW_CUSTOMER` | $ za 1 klienta z marketingu | 15.0 |
| `MARKETING_BASELINE_NEW_CUSTOMERS` | Bazowy przyrost/dzień | 3 |
| `EMPLOYEE_SALARY_PER_LEVEL` | Pensja = poziom × to | 50.0 |
| `LICENSE_DAILY` | Koszt licencji/dzień | 5.0 |
| `POWER_PRICE_PER_KWH` | Cena prądu/kWh | 0.15 |
| `CHURN_BASE_MONTHLY` | Bazowy churn/mies | 0.05 |

### `server_models` — dodatkowe modele serwerów
```json
"server_models": [
  {
    "id": "custom_server",
    "name": "Mój serwer",
    "cpu_cores": 64,
    "ram_gb": 128,
    "disk_gb": 8000,
    "disk_type": "nvme",
    "prices": {"budget": 5000, "standard": 8000, "premium": 12000},
    "tdp_w": 800
  }
]
```

### `tlds` — dodatkowe domeny
```json
"tlds": [
  {"id": "xyz", "name": ".xyz", "register": 5.0, "renew": 5.0, "popularity": 0.2}
]
```

### `names` — imiona pracowników i nazwy serwerów
```json
"names": {
  "first_names": ["Jan", "Maria"],
  "server_names": ["MÓJ-SERWER"]
}
```

## Włączanie/wyłączanie

Ustaw `"enabled": false` w pliku modu aby go wyłączyć bez usuwania.

## Licencja

Mody to osobne pakiety (nie derivative work gry) — zgodne z licencją CC BY-ND 4.0. Autor modu zachowuje pełne prawa do swojej pracy.