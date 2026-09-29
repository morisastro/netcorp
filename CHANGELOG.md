# Changelog

## [0.3.0] - 2026-09-29

### Naprawione
- Reputacja spadała do 0 i nigdy nie wracała
  - Kara za otwarte tickety: -0.2/ticket → max -2/dzień (lżejsza)
  - Nagroda za rozwiązane tickety: +0.1 → +0.5/dzień (silniejsza)
  - Kara za awarie: -0.5 → -0.3 per awaria (lżejsza)
- Tickety sieciowe (network/DDoS) kumulowały się gdy brak network engineera
  - Support może przejąć połowę pracy neteng/sysadmin gdy brak specjalisty

### Zmienione
- Playtest 50 dni: gra stabilna (cash rośnie, reputacja stabilna, tickety nadążane)
