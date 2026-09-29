# Mody NetCorp Tycoon

Ten folder zawiera mody do gry. Mody to pliki `.json` nadpisujące dane gry.

## Jak stworzyć mod

Utwórz plik `.json` w tym folderze. Przykład — patrz `przyklad-wiecej-klientow.json`.

## Wszystkie opcje modowania

### `balance` — stałe balansu (z `data/balance.py`)
| Klucz | Opis | Domyślnie |
|-------|------|-----------|
| `FAILURE_BASE_DAILY` | Bazowa szansa awarii/serwer/dzień | 0.02 |
| `FAILURE_MOD_OVERLOAD_CPU` | Mnożnik gdy CPU > 80% | 3.0 |
| `FAILURE_MOD_AGE` | Mnożnik gdy serwer stary | 1.5 |
| `MARKETING_COST_PER_NEW_CUSTOMER` | $ za 1 klienta z marketingu | 15.0 |
| `MARKETING_BASELINE_NEW_CUSTOMERS` | Bazowy przyrost/dzień | 3 |
| `EMPLOYEE_SALARY_PER_LEVEL` | Pensja = poziom × to | 50.0 |
| `EMPLOYEE_CAPACITY_PER_LEVEL` | Pojemność tickotów = poziom × to | 10 |
| `LICENSE_DAILY` | Koszt licencji/dzień | 5.0 |
| `POWER_PRICE_PER_KWH` | Cena prądu/kWh | 0.15 |
| `NETWORK_PRICE_PER_MBPS_DAILY` | Cena łącza/Mbps/dzień | 0.05 |
| `CHURN_BASE_MONTHLY` | Bazowy churn/mies | 0.05 |
| `SLA_PENALTY_PER_HOUR_HOBBYIST` | Kara SLA/h hobbyist | 5.0 |
| `SLA_PENALTY_PER_HOUR_SMALL_BIZ` | Kara SLA/h small biz | 20.0 |
| `TIER_MTBF.budget` | MTBF budget tier (godziny) | 4000 |
| `TIER_MTBF.standard` | MTBF standard tier | 10000 |
| `TIER_MTBF.premium` | MTBF premium tier | 25000 |

### `start` — start gry
```json
"start": { "cash": 20000, "reputation": 70 }
```

### `server_models` — dodatkowe modele serwerów
```json
"server_models": [
  {
    "id": "turbo_x1",
    "name": "Turbo X1",
    "cpu_cores": 24,
    "ram_gb": 48,
    "disk_gb": 2000,
    "disk_type": "nvme",
    "prices": {"budget": 3000, "standard": 5000, "premium": 8000},
    "tdp_w": 350
  }
]
```

### `tlds` — dodatkowe domeny
```json
"tlds": [
  {"id": "xyz", "name": ".xyz", "register": 5.0, "renew": 5.0, "popularity": 0.2}
]
```

### `products` — gotowe plany produktów dodawane do nowej gry
```json
"products": [
  {
    "id": "mod_vps_pro",
    "product_type": "vps",
    "name": "VPS Pro",
    "cpu_cores": 8, "ram_gb": 16, "disk_gb": 200,
    "bandwidth_mbps": 1000, "price_monthly": 49.99, "sla_target": 99.99
  }
]
```

### `failure_types` — wagi typów awarii
```json
"failure_types": { "disk": 0.10, "ddos": 0.30 }
```
(Domyślne: `{"disk": 0.25, "cpu_overload": 0.20, "overheat": 0.15, "power": 0.15, "network": 0.15, "ddos": 0.10}`)

### `marketing` — ustawienia marketingu
```json
"marketing": { "cost_per_customer": 8.0, "baseline_new": 4 }
```

### `employee` — ustawienia pracowników
```json
"employee": { "salary_per_level": 40, "capacity_per_level": 15 }
```

### `names` — imiona i nazwy serwerów
```json
"names": {
  "first_names": ["Jan", "Maria"],
  "last_names": ["Kowalski", "Nowak"],
  "server_names": ["MÓJ-SERWER"]
}
```

## Włączanie/wyłączanie

Ustaw `"enabled": false` w pliku modu aby go wyłączyć bez usuwania.

## Licencja

Mody to osobne pakiety (nie derivative work gry) — zgodne z licencją CC BY-ND 4.0. Autor modu zachowuje pełne prawa do swojej pracy.