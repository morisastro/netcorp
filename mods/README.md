# Mody NetCorp Tycoon

Ten folder zawiera mody do gry. Mody to pliki `.json` nadpisujące dane gry.

## Jak stworzyć mod

Utwórz plik `.json` w tym folderze. Przykład — patrz `przyklad-wiecej-klientow.json`.

## Wszystkie 18 kategorii modowania

### 1. `balance` — stałe balansu (z `data/balance.py`)
16 stałych: FAILURE_BASE_DAILY, MARKETING_COST_PER_NEW_CUSTOMER, EMPLOYEE_SALARY_PER_LEVEL, POWER_PRICE_PER_KWH, CHURN_BASE_MONTHLY, SLA_PENALTY_PER_HOUR_*, itp.

### 2. `start` — start gry
```json
"start": { "cash": 20000, "reputation": 70 }
```

### 3. `server_models` — dodatkowe modele serwerów
```json
"server_models": [{ "id": "turbo_x1", "name": "Turbo X1", "cpu_cores": 24, ... }]
```

### 4. `tlds` — dodatkowe domeny
```json
"tlds": [{ "id": "xyz", "name": ".xyz", "register": 5.0, ... }]
```

### 5. `products` — gotowe plany dodawane do nowej gry
```json
"products": [{ "id": "mod_vps", "product_type": "vps", "name": "VPS Pro", ... }]
```

### 6. `failure_types` — wagi typów awarii
```json
"failure_types": { "disk": 0.10, "ddos": 0.30 }
```

### 7. `names` — imiona i nazwy serwerów
```json
"names": { "first_names": [...], "last_names": [...], "server_names": [...] }
```

### 8. `marketing` — ustawienia marketingu
```json
"marketing": { "cost_per_customer": 8.0, "baseline_new": 4 }
```

### 9. `employee` — ustawienia pracowników
```json
"employee": { "salary_per_level": 40, "capacity_per_level": 15 }
```

### 10. `loan` — parametry pożyczki (NOWE)
```json
"loan": { "interest_rate": 0.002, "rate_per_customer": 0.8, "min_customers": 3 }
```

### 11. `sla_penalties` — kary za naruszenia SLA (NOWE)
```json
"sla_penalties": {
  "SLA_PENALTY_PER_HOUR_HOBBYIST": 10.0,
  "SLA_PENALTY_PER_HOUR_SMALL_BIZ": 50.0,
  "SLA_PENALTY_PER_HOUR_ENTERPRISE": 200.0
}
```

### 12. `segments` — własne segmenty klientów (NOWE)
```json
"segments": [
  {"id": "budget", "name": "Budżetowy", "churn": 0.08, "sla": 99.0},
  {"id": "pro", "name": "Pro", "churn": 0.03, "sla": 99.9}
]
```

### 13. `game_settings` — ustawienia startowe gry (NOWE)
```json
"game_settings": {
  "start_region_name": "Mój garaż",
  "start_slots": 5,
  "start_power_kw": 3.0,
  "start_cooling": 0.8
}
```

### 14. `modifiers` — globalne modyfikatory (mnożniki) (NOWE)
```json
"modifiers": { "income_mult": 1.5, "expense_mult": 0.8, "churn_mult": 0.7 }
```

### 15. `website_blocks` — dodatkowe bloki strony (NOWE)
```json
"website_blocks": [
  {"type": "testimonials", "name": "Referencje", "bonus": 0.12}
]
```

### 16. `tutorial_steps` — własne kroki samouczka (NOWE)
```json
"tutorial_steps": [
  {"title": "Witaj!", "body": "To krok samouczka z modu."}
]
```

### 17. `events` — własne wydarzenia (NOWE)
```json
"events": [
  {"type": "boom", "name": "Boom rynkowy", "effect": "+20% klientów na 5 dni"}
]
```

### 18. `milestones` — własne kamienie milowe (NOWE)
```json
"milestones": [
  {"id": "mega_dc", "customers": 5000, "name": "Mega DC (mod)"}
]
```

## Włączanie/wyłączanie

Ustaw `"enabled": false` w pliku modu aby go wyłączyć bez usuwania.

## Licencja

Mody to osobne pakiety (nie derivative work gry) — zgodne z licencją CC BY-ND 4.0. Autor modu zachowuje pełne prawa do swojej pracy.