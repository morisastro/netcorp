# Changelog

## [0.2.0] - 2026-09-29

### Dodane
- Realne przypisywanie klientów do serwerów (ServiceInstance)
  - VPS/WWW/dedyk zużywają realne CPU/RAM/dysk na konkretnym serwerze
  - Oversubscription: 1.5× CPU, 1.2× RAM (VPS/WWW)
  - Dedyk = jeden klient na serwer
  - Brak serwera = klient nie kupuje + spadek reputacji
  - Obciążenie serwerów pokazywane w UI na żywo
- Tickety supportu (auto-rozwiązywane przez pracowników)
  - Typy: support, failure, network, sla
  - Priorytet 1-3 (DDoS/zasilanie = wysoki)
  - Generowane automatycznie przy awariach
  - Pracownicy rozwiązują wg roli (support/sysadmin/neteng)
  - Pojemność = poziom × 10 ticketów/dzień
  - Nierozwiązane tickety = spadek reputacji
- Rozbudowany system modowania (10 kategorii):
  - balance (16 stałych), start (cash, reputation), server_models, tlds,
    products (gotowe plany), failure_types (wagi), marketing, employee,
    names (imiona, nazwy serwerów)
- Mod aplikowany przy nowej grze (apply_mods w Game.new_game)
- Sekcja "Zainstalowane mody" w Ustawieniach z listą i statusem
- Przykładowy mod demonstrujący wszystkie opcje
- Przyciski otwierania folderów w Ustawieniach (zapisy, mody, folder gry)
- Sprzedaż/usuwanie serwerów (zwrot 30% kosztu, malejący z wiekiem)
- System samouczka (8 kroków, auto-pokaz przy nowej grze)
