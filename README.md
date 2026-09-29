# NetCorp Tycoon

Desktopowa gra management/tycoon o budowaniu własnej firmy hostingowej / cloud providera — od garażowego home labu do międzynarodowego operatora infrastruktury.

> **Status:** Pre-produkcja — faza specyfikacji. Brak grywalnego kodu na ten moment.

## Licencja

Gra jest darmowa i licencjonowana na **CC BY-ND 4.0** (Creative Commons Attribution-NoDerivatives 4.0 International).

- Możesz **kopiować, dystrybuować i używać** gry, nawet komercyjnie, **z atrybucją** (oznaczeniem autora).
- **Nie wolno** redystrybuować **zmodyfikowanej** wersji kodu źródłowego ani binariów.
- **Mody są dozwolone** — dodatkowe pakiety ładowane w czasie działania przez oficjalny modding API nie są uznawane za dzieła pochodne gry, o ile są dystrybuowane oddzielnie i nie zawierają/zastępują kodu źródłowego ani binariów gry. Autorzy modów zachowują pełne prawa do swoich prac.

Pełny tekst licencji: [LICENSE](LICENSE).

## Stack technologiczny

- **Język:** Python 3.11+
- **UI:** PySide6 (Qt for Python)
- **Stan:** lokalny plik JSON (bez bazy danych, bez serwera)
- **Bundling:** PyInstaller
- **CI:** GitHub Actions (build na tag → release)

## Struktura projektu

```
netcorp-tycoon/
├── main.py                  # entrypoint
├── app/                     # powłoka aplikacji, ustawienia, update checker
├── core/                    # logika gry (agnostyczna względem UI, testowalna)
├── data/                    # dane statyczne (katalogi, balans, generatory)
├── persistence/             # save/load
├── ui/                      # ekrany i widgety PySide6
└── tests/                   # testy pytest dla logiki core
```

Warstwa `core/` jest całkowicie odseparowana od `ui/` — logika gry nie zna Qt i jest testowana jednostkowo niezależnie. UI wywołuje tylko metody na obiekcie `Game` i czyta stan przez `Game.get_state()`.

## Dokumentacja

- [SPEC.md](SPEC.md) — pełna specyfikacja gry (pętla rozgrywki, systemy, ekonomia, progression, pracownicy, awarie, klienci, ekrany UI, model danych, roadmapa).

## Język

Gra jest po polsku (interfejs, komunikaty, raporty, tickety, nazwy ról). Kod i identyfikatory techniczne po angielsku. Angielska lokalizacja jako opcjonalna warstwa w późniejszej fazie.

## Zapisy (save)

Każda partia = osobny plik `.json` w `~/.netcorp-tycoon/saves/` z nazwą zapisu. Multi-slot, autosave na koniec dnia, manualny save pod nazwą. Ekran ładowania listuje zapisy z datą i mini-podglądem KPI.

## Development

(Instrukcje setupu zostaną dodane po postawieniu scaffoldu projektu.)