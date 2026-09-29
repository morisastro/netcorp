# Changelog

## [0.2.2] - 2026-09-29

### Dodane
- Bankructwo = game over
  - Gdy gotówka spadnie poniżej $0 → flaga bankrupt
  - Przycisk "Następny dzień" zablokowany przy bankructwie
  - Dialog Game Over z podsumowaniem
  - Topbar pokazuje "⛔ BANKRUT" na czerwono gdy ujemna gotówka
- System pożyczki w Finansach
  - Weź pożyczkę w zamian za część klientów ($0.50 per utracony klient)
  - Minimum 5 klientów
  - Odsetki 0.1% dziennie (rosnący dług)
  - Spłata długu w dowolnej kwocie
  - Ekran Finanse pokazuje: gotówkę, przychody, koszty (z odsetkami), dług
