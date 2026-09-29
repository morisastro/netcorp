# Changelog

Wszystkie istotne zmiany projektu NetCorp Tycoon będą dokumentowane w tym pliku.

Format oparty na [Keep a Changelog](https://keepachangelog.com/pl/), wersjonowanie [Semantic Versioning](https://semver.org/lang/pl/).

## [0.1.1] - 2026-09-29

### Dodane
- Link do GitHub (repo, releases, zgłoś problem) w Ustawieniach
- Sprawdzanie aktualizacji z linkami do pobrania per platforma (Win/Linux/Mac)
- System wersjonowania (`new_version.py`) — automatyczny bump + tag + CI

### Zmienione
- CI buduje teraz tylko 3 pliki ZIP (1 na platformę) z poprawną nazwą (bez podwójnego `v`)
- Powiadomienie o aktualizacji pokazuje rozmiar pliku i bezpośredni link do Windows builda
- Release zawiera changelog z tego pliku zamiast auto-generowanych commitów

## [0.1.0] - 2026-09-29

### Dodane
- Pierwsza grywalna wersja gry
- Menu startowe z wyborem trybów: Sandbox, Kariera, Hardcore
- 10 ekranów: Przegląd, Infrastruktura, Produkty, Klienci, Awarie, Pracownicy, Marketing, Strona firmy, Finanse, Ustawienia
- Tury dzienne (1 klik = 1 dzień symulacji) z raportem dziennym
- Infrastruktura: katalog serwerów (5 modeli × 3 tier jakości), sloty w serwerowni (SVG), zasoby DC (prąd, sieć, chłodzenie)
- Produkty: WWW, VPS, serwer dedykowany, domena — własne plany z ręcznymi cenami
- Klienci: agregaty per produkt, churn, czas pobytu 1-7 dni, SLA kary
- Awarie: 6 typów (dysk, CPU, przegrzanie, zasilanie, sieć, DDoS), RNG z modyfikatorami stanu, wybór akcji
- Pracownicy: 5 ról (Support, Sysadmin, NetEng, Sales, Marketing), indywidualni z poziomem i pensją
- Marketing: budżet dzienny, ROI, przyrost klientów
- Strona firmy: drag & drop builder sekcji z podglądem HTML na żywo
- Domeny per TLD (.com/.net/.org/.pl/.io/.eu/.dev/.app)
- Finanse: prosta gotówka, koszty stałe, przychody z subskrypcji
- Reputacja, kamienie milowe (50/500/2000 klientów)
- Save/load: multi-slot JSON, autosave dzienny, manualny zapis
- Update checker: sprawdza GitHub releases przy starcie
- Ikona aplikacji (PNG → ICO, 16-256px)
- Licencja CC BY-ND 4.0 (gra darmowa, mody dozwolone)
- Dark pro-operator UI z animacjami hover i emoji ikonami
- Build .exe przez PyInstaller + CI (GitHub Actions)
- Testy logiki core (11/11 pass)