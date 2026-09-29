# NetCorp Tycoon

Desktopowa gra management/tycoon o budowaniu własnej firmy hostingowej / cloud providera — od garażowego home labu do międzynarodowego operatora infrastruktury.

> **Status:** Wczesna wersja (v0.2.5) — aktywnie rozwijana.

---

## 🎮 Jak zagrać (bez instalacji czegokolwiek)

### Windows (najprościej)

1. Wejdź na https://github.com/morisastro/netcorp/releases
2. Pobierz plik **`netcorp-tycoon-vX.X.X-win.zip`** (ok. 50 MB)
3. Rozpakuj ZIP gdziekolwiek (np. na Pulpicie)
4. Kliknij dwukrotnie **`netcorp-tycoon.exe`**
5. Gra się otworzy. To wszystko.

Nie potrzebujesz Pythona, żadnych bibliotek, ani instalatora. Po prostu rozpakuj i graj.

### Linux

1. Pobierz `netcorp-tycoon-vX.X.X-linux.zip` z [releases](https://github.com/morisastro/netcorp/releases)
2. Rozpakuj: `unzip netcorp-tycoon-vX.X.X-linux.zip`
3. Uruchom: `./netcorp-tycoon/netcorp-tycoon`
4. Jeśli nie działa, nadaj uprawnienia: `chmod +x netcorp-tycoon/netcorp-tycoon`

### macOS

1. Pobierz `netcorp-tycoon-vX.X.X-mac.zip` z [releases](https://github.com/morisastro/netcorp/releases)
2. Rozpakuj (kliknij dwukrotnie lub `unzip`)
3. Uruchom `netcorp-tycoon` z terminalala lub Finder

> ⚠️ macOS może zapytać czy ufasz aplikacji (bo nie ma podpisu Apple). Kliknij Prawy klik → Otwórz → Otwórz.

---

## 🎯 O grze

**Cel:** Zbudować firmę hostingową od garażu do globalnego providera.

**Jak grasz:**
- Gra działa w **turach dziennych** — podejmujesz decyzje, klikasz „Następny dzień", system symuluje 24h
- **Bankructwo** (gotówka poniżej $0) = koniec gry
- W jednej partii możesz grać dowolnie długo (sandbox, open-ended)

**Co robisz:**
- 🖥️ **Kupujesz serwery** (5 modeli × 3 tier jakości — od taniego/awaryjnego do premium)
- 📦 **Tworzysz produkty** (Hosting WWW, VPS, serwery dedykowane, domeny) z własnymi cenami
- 👥 **Zarządzasz klientami** — przychodzą z marketingu i reputacji, odchodzą po 1-7 dniach
- ⚠️ **Reagujesz na awarie** (dysk, CPU, przegrzanie, zasilanie, sieć, DDoS) — wybierasz akcję
- 👤 **Zatrudniasz pracowników** (Support, Sysadmin, Network engineer, Sales, Marketing)
- 📢 **Inwestujesz w marketing** ($ → nowi klienci)
- 🌐 **Budujesz stronę firmy** (drag & drop bloków → bonus do konwersji)
- 💰 **Zarządzasz finansami** (przychody, koszty, pożyczki z odsetkami)
- 🧩 **Instalujesz mody** (zmieniają balans, dodają serwery, produkty, domeny)

**Tryby gry:**
- **Sandbox** — $5,000 startu, normalna awaryjność
- **Kariera** — $3,000 startu, wyższa awaryjność (×1.2)
- **Hardcore** — $1,500 startu, wysoka awaryjność (×1.8)

---

## 📁 Gdzie są moje zapisy?

Zapisy gry są w:
- **Windows:** `C:\Users\<TwojaNazwa>\.netcorp-tycoon\saves\`
- **Linux/macOS:** `~/.netcorp-tycoon/saves/`

Każda partia = osobny plik `.json`. Autosave po każdym dniu. Możesz też zapisać ręcznie pod własną nazwą (nadpisując istniejące zapisy).

Otwórz folder zapisów z poziomu gry: **Ustawienia → 📂 Otwórz folder zapisów**

---

## 🧩 Mody

Gra obsługuje mody — pliki `.json` które zmieniają dane gry bez zmieniania kodu.

**Jak zainstalować mod:**
1. Znajdź mod (plik `.json`)
2. Skopiuj do folderu `mods/` obok pliku gry (`netcorp-tycoon.exe`)
3. Uruchom grę — mod załaduje się automatycznie przy nowej grze

**Co modyfikują mody:** 18 kategorii — balans, ceny serwerów, domeny, produkty, imiona, awaryjność, marketing, pożyczki, segmenty klientów, ustawienia startowe, mnożniki, bloki strony, kroki samouczka, wydarzenia, kamienie milowe.

Szczegóły w [`mods/README.md`](mods/README.md).

Otwórz folder modów: **Ustawienia → 🧩 Otwórz folder modów**

---

## 🔄 Aktualizacje

Gra sprawdza automatycznie przy starcie czy jest nowsza wersja na GitHub. Jeśli tak — pokaże banner z linkiem do pobrania.

Możesz sprawdzić ręcznie: **Ustawienia → Sprawdź aktualizacje teraz**

Najnowsze wersje: https://github.com/morisastro/netcorp/releases

---

## 📜 Licencja

Gra jest **darmowa** i licencjonowana na **CC BY-ND 4.0** (Creative Commons Attribution-NoDerivatives 4.0 International).

- ✅ Możesz **kopiować, dystrybuować i używać** gry, nawet komercyjnie, **z atrybucją** (oznaczeniem autora)
- ❌ **Nie wolno** redystrybuować **zmodyfikowanej** wersji kodu źródłowego ani binariów
- ✅ **Mody są dozwolone** — dodatkowe pakiety ładowane przez oficjalny system modów (nie są derivative work)

Pełny tekst: [`LICENSE`](LICENSE)

---

## 🛠️ Dla programistów (opcjonalne)

### Uruchomienie z kodu źródłowego

Jeśli chcesz uruchomić grę z kodu (np. do modowania lub rozwoju), potrzebujesz Pythona 3.11+.

1. Pobierz Python: https://www.python.org/downloads/ (podczas instalacji zaznacz „Add Python to PATH")
2. Otwórz terminal/wiersz poleceń w folderze gry
3. Utwórz wirtualne środowisko:
   ```
   python -m venv .venv
   ```
4. Aktywuj je:
   - **Windows:** `.venv\Scripts\activate`
   - **Linux/macOS:** `source .venv/bin/activate`
5. Zainstaluj zależności:
   ```
   pip install -r requirements.txt
   ```
6. Uruchom grę:
   ```
   python main.py
   ```

### Stack technologiczny

- **Język:** Python 3.11+
- **UI:** PySide6 (Qt for Python)
- **Stan:** plik JSON (bez bazy danych, bez serwera)
- **Bundling:** PyInstaller (`.exe`, Linux binary, macOS `.app`)
- **CI:** GitHub Actions (automatyczny build na tag → release)

### Struktura projektu

```
netcorp-tycoon/
├── main.py                  # punkt wejścia (uruchom grę)
├── app/                     # powłoka aplikacji, ustawienia, update checker
├── core/                    # logika gry (testowalna bez UI)
├── data/                    # dane statyczne (katalogi, balans)
├── persistence/             # zapis/wczytywanie stanu
├── ui/                      # ekrany PySide6
├── mods/                    # mody (pliki JSON)
├── assets/                  # ikona aplikacji
└── tests/                   # testy logiki
```

### Build release

```
python build_release.py
```
Tworzy ZIP w `release/` gotowy do dystrybucji.

### Nowa wersja

```
python new_version.py auto
```
Automatycznie podbija wersję (+0.0.1), tworzy tag i pcha do GitHub → CI buduje 3 platformy i tworzy release.

---

## ❓ Pomoc

- **Gra się nie otwiera?** Sprawdź czy rozpakowałeś cały ZIP (nie tylko .exe)
- **Brak dźwięku?** Gra obecnie nie ma dźwięków (planowane w przyszłości)
- **Błąd/propozycja?** https://github.com/morisastro/netcorp/issues

---

## 📊 Status projektu

- Wersja: v0.2.5
- 10 ekranów: Przegląd, Infrastruktura, Produkty, Klienci, Awarie, Pracownicy, Marketing, Strona firmy, Finanse, Ustawienia
- Realne przypisywanie klientów do serwerów (CPU/RAM/dysk)
- Tickety supportu auto-rozwiązywane przez pracowników
- Bankructwo = game over
- System pożyczek (w zamian za klientów)
- 18 kategorii modowania
- Samouczek (8 kroków)
- Zapis/wczytywanie (multi-slot, autosave, nadpisywanie)
- Tryby gry: Sandbox, Kariera, Hardcore
- Nickname gracza / nazwa firmy (podstawa pod multiplayer)

**Roadmapa:** wykresy finansów, dźwięki, lokalizacja EN, multiplayer (ranking online, marketplace), więcej produktów (Minecraft, storage, backup).