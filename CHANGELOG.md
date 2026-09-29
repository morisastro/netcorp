# Changelog

## [0.2.9] - 2026-09-29

### Naprawione
- Krytyczny bug: serwer zostawał "down" po naprawie awarii
  - Akcja naprawy (restart/wymiana/failover) oznaczała awarię jako "resolved"
    ale nie zmieniała statusu serwera z "down" na "ok"
  - Naprawa: przy akcji naprawy serwer wraca do "ok"
- DDoS nie ustawia już serwera na "down" (atak na sieć, nie sprzęt)
  - Serwery nadal działają wewnętrznie, ale generują tickety sieciowe
