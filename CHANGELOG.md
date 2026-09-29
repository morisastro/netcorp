# Changelog

## [0.2.7] - 2026-09-29

### Naprawione
- Krytyczny bug: domeny nie rosły (count zawsze 0)
  - churn_services() nadpisywał count domen wartością z services (domeny nie są services)
  - Dodany osobny churn dla domen (z arrival_days i avg_stay_days)

### Dodane
- Komunikat "⚠️ SERWERY NIEWYSTARCZAJĄCE" w raporcie dziennym
  - Pokazuje liczbę klientów którzy nie kupili (brak miejsca na serwerach)
  - Sugeruje kupno serwerów / rozbudowę serwerowni
- Debug mode w Ustawieniach
  - Checkbox (zapisywany w settings.json)
  - Loguje detale symulacji do konsoli (cash, services, customers, unplaced, failures, tickets)
- Sekcja "🐞 Zgłaszanie błędów" w Ustawieniach
  - Link do GitHub Issues (https://github.com/morisastro/netcorp/issues)
- Skalowanie UI pod rozdzielczość monitora (screen_info.py)
  - Wykrywanie rozmiaru ekranu, dostosowanie okna i liczby kolumn kart
- Churn klientów wydłużony: 1-7 dni → 5-15 dni
- Oversubscription serwerów zwiększony: 1.5× → 3× CPU, 1.2× → 2× RAM
- Max 20 klientów z marketingu dziennie (żeby nie zalewać gracza)
