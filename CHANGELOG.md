# Changelog

## [0.2.8] - 2026-09-29

### Naprawione
- Krytyczny bug: wszystkie klienty trafiały do pierwszego produktu (www)
  - `rng.random()` zwracało [0,1) ale suma wag > 1 → zawsze trafiał pierwszy produkt
  - Naprawa: `r = rng.random() * total_w` (normalizacja do [0, suma_wag))
- Przychód dzienny: /20 → /10 (podwojenie zysku per klient)
- Domeny: $0.60/dzień → $1.20/dzień (podwojenie)

### Zmienione
- Ekonomia: lżejsza gra na start
  - Pensje: $50/level → $30/level
  - Licencje: $5/dzień → $2/dzień
  - Marketing cost: $15/klient → $10/klient
- Playtest potwierdził: gra stabilna finansowo po 30 dniach
